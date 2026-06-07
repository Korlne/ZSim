from __future__ import annotations

import ast
import csv
import json
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_ROOT = PROJECT_ROOT / "zsim" / "sim_progress"
BUFF_XLOGIC_ROOT = PRODUCTION_ROOT / "Buff" / "BuffXLogic"
DATA_ROOT = PROJECT_ROOT / "zsim" / "data"
CONFIG_ROOT = PROJECT_ROOT / "zsim"

EVENT_LIST_TRUE_PATTERN = re.compile(
    r"\bevent_list\b\s*(?:=|:)\s*(?:true|1)\b",
    re.IGNORECASE,
)

ALLOWED_PYTHON_FINDINGS: dict[tuple[str, str], set[str]] = {}


@dataclass(frozen=True)
class DeletionReadinessFinding:
    path: str
    line: int
    matched_expression: str
    classification_suggestion: str
    next_action: str

    def message(self) -> str:
        return (
            f"{self.path}:{self.line}: matched expression: {self.matched_expression}; "
            f"classification suggestion: {self.classification_suggestion}; "
            f"next action: {self.next_action}"
        )


class LegacyEventListDeletionReadinessVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source: str) -> None:
        self.path = path
        self.source = source
        self.findings: list[DeletionReadinessFinding] = []
        self._parents: list[ast.AST] = []
        self._class_stack: list[str] = []

    def visit(self, node: ast.AST) -> Any:
        self._parents.append(node)
        try:
            return super().visit(node)
        finally:
            self._parents.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            if alias.name == "find_event_list":
                module = f"{'.' * node.level}{node.module or ''}"
                self._add_finding(
                    line=getattr(alias, "lineno", node.lineno),
                    kind="find_event_list_import",
                    expression=f"from {module} import find_event_list",
                )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if self._is_find_event_list_call(node.func):
            self._add_finding(
                line=node.lineno,
                kind="find_event_list_call",
                expression=self._source_for(node),
            )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if self._is_buff_record_event_list_access(node):
            self._add_finding(
                line=node.lineno,
                kind=self._buff_record_event_list_kind(node),
                expression=self._attribute_context(node),
            )
        self.generic_visit(node)

    def _add_finding(self, *, line: int, kind: str, expression: str) -> None:
        normalized_expression = self._normalize(expression)
        self.findings.append(
            DeletionReadinessFinding(
                path=self._relative_path(),
                line=line,
                matched_expression=normalized_expression,
                classification_suggestion=self._classification_for(kind),
                next_action=self._next_action_for(kind),
            )
        )

    def _relative_path(self) -> str:
        return self.path.relative_to(PROJECT_ROOT).as_posix()

    def _source_for(self, node: ast.AST) -> str:
        segment = ast.get_source_segment(self.source, node)
        if segment is None:
            return f"<{type(node).__name__}>"
        return self._normalize(segment)

    def _attribute_context(self, node: ast.Attribute) -> str:
        direct_parent = self._parents[-2] if len(self._parents) >= 2 else None
        grandparent = self._parents[-3] if len(self._parents) >= 3 else None

        if isinstance(direct_parent, ast.Compare):
            return self._source_for(direct_parent)
        if isinstance(direct_parent, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            return self._source_for(direct_parent)
        if isinstance(direct_parent, ast.Attribute) and direct_parent.value is node:
            if isinstance(grandparent, ast.Call):
                return self._source_for(grandparent)
            return self._source_for(direct_parent)
        return self._source_for(node)

    @staticmethod
    def _normalize(expression: str) -> str:
        return " ".join(expression.strip().split())

    @staticmethod
    def _is_find_event_list_call(func: ast.expr) -> bool:
        if isinstance(func, ast.Name):
            return func.id == "find_event_list"
        if isinstance(func, ast.Attribute):
            return func.attr == "find_event_list"
        return False

    def _is_buff_record_event_list_access(self, node: ast.Attribute) -> bool:
        if node.attr != "event_list":
            return False
        owner = self._dotted_name(node.value)
        if owner in {"record", "BuffRecordBaseClass", "BRBC"}:
            return True
        return owner == "self" and self._class_stack[-1:] == ["BuffRecordBaseClass"]

    def _buff_record_event_list_kind(self, node: ast.Attribute) -> str:
        direct_parent = self._parents[-2] if len(self._parents) >= 2 else None
        grandparent = self._parents[-3] if len(self._parents) >= 3 else None
        if (
            isinstance(direct_parent, ast.Attribute)
            and direct_parent.value is node
            and direct_parent.attr == "append"
            and isinstance(grandparent, ast.Call)
        ):
            return "record_event_list_append"
        return "buff_record_event_list_access"

    def _dotted_name(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            owner = self._dotted_name(node.value)
            if owner is None:
                return node.attr
            return f"{owner}.{node.attr}"
        return None

    @staticmethod
    def _classification_for(kind: str) -> str:
        return {
            "find_event_list_import": "legacy discovery import outside deletion allowlist",
            "find_event_list_call": "legacy discovery call outside compatibility cache",
            "buff_record_event_list_access": "BuffRecordBaseClass.event_list cache access",
            "record_event_list_append": "producer-level planned-event writer through record.event_list",
            "event_list_preparation_request": "BuffXLogic check_preparation event_list=True entry point",
            "config_event_list_preparation_request": "config/data event_list=True entry point",
        }[kind]

    @staticmethod
    def _next_action_for(kind: str) -> str:
        return {
            "find_event_list_import": "delete old discovery or migrate to ScheduleDispatchPort",
            "find_event_list_call": "delete old discovery or migrate to ScheduleDispatchPort",
            "buff_record_event_list_access": "delete BuffRecordBaseClass.event_list or document retained fallback",
            "record_event_list_append": "migrate to ScheduleDispatchPort",
            "event_list_preparation_request": "block deletion until this entry point is removed",
            "config_event_list_preparation_request": "block deletion until this entry point is removed",
        }[kind]


def _relative_path(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def _source_for(source: str, node: ast.AST) -> str:
    segment = ast.get_source_segment(source, node)
    if segment is None:
        return f"<{type(node).__name__}>"
    return " ".join(segment.strip().split())


def _call_name(func: ast.expr) -> str | None:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _may_request_event_list(value: ast.expr) -> bool:
    if isinstance(value, ast.Constant):
        return bool(value.value)
    return True


def _unpacked_event_list_values(value: ast.expr) -> list[ast.expr]:
    if not isinstance(value, ast.Dict):
        return []
    matches: list[ast.expr] = []
    for key, item in zip(value.keys, value.values, strict=True):
        if isinstance(key, ast.Constant) and key.value == "event_list":
            matches.append(item)
    return matches


def _production_python_files() -> list[Path]:
    return sorted(
        path
        for path in PRODUCTION_ROOT.rglob("*.py")
        if "__pycache__" not in path.parts
    )


def _collect_python_findings() -> list[DeletionReadinessFinding]:
    findings: list[DeletionReadinessFinding] = []
    for path in _production_python_files():
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        visitor = LegacyEventListDeletionReadinessVisitor(path, source)
        visitor.visit(tree)
        findings.extend(visitor.findings)
    return findings


def _collect_buff_xlogic_event_list_entry_points() -> list[DeletionReadinessFinding]:
    findings: list[DeletionReadinessFinding] = []
    for path in sorted(BUFF_XLOGIC_ROOT.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if _call_name(node.func) not in {"get_prepared", "check_preparation"}:
                continue
            for keyword in node.keywords:
                if keyword.arg == "event_list" and _may_request_event_list(keyword.value):
                    findings.append(
                        DeletionReadinessFinding(
                            path=_relative_path(path),
                            line=keyword.value.lineno,
                            matched_expression=_source_for(source, node),
                            classification_suggestion=LegacyEventListDeletionReadinessVisitor._classification_for(
                                "event_list_preparation_request"
                            ),
                            next_action=LegacyEventListDeletionReadinessVisitor._next_action_for(
                                "event_list_preparation_request"
                            ),
                        )
                    )
                if keyword.arg is None:
                    for value in _unpacked_event_list_values(keyword.value):
                        if _may_request_event_list(value):
                            findings.append(
                                DeletionReadinessFinding(
                                    path=_relative_path(path),
                                    line=value.lineno,
                                    matched_expression=_source_for(source, node),
                                    classification_suggestion=LegacyEventListDeletionReadinessVisitor._classification_for(
                                        "event_list_preparation_request"
                                    ),
                                    next_action=LegacyEventListDeletionReadinessVisitor._next_action_for(
                                        "event_list_preparation_request"
                                    ),
                                )
                            )
    return findings


def _is_allowed_python_finding(finding: DeletionReadinessFinding) -> bool:
    expression_allowlist = ALLOWED_PYTHON_FINDINGS.get(
        (finding.path, _kind_for_allowed_expression(finding)), set()
    )
    return finding.matched_expression in expression_allowlist


def _kind_for_allowed_expression(finding: DeletionReadinessFinding) -> str:
    if finding.classification_suggestion.startswith("legacy discovery import"):
        return "find_event_list_import"
    if finding.classification_suggestion.startswith("legacy discovery call"):
        return "find_event_list_call"
    if finding.classification_suggestion.startswith("BuffRecordBaseClass.event_list"):
        return "buff_record_event_list_access"
    if finding.classification_suggestion.startswith("producer-level"):
        return "record_event_list_append"
    raise AssertionError(f"Unknown deletion-readiness finding: {finding}")


def _config_paths() -> list[Path]:
    paths = sorted(CONFIG_ROOT.glob("config*.json"))
    paths.extend(
        path
        for path in sorted(DATA_ROOT.rglob("*"))
        if path.suffix.lower() in {".csv", ".json", ".toml"}
    )
    return paths


def _is_truthy_event_list_value(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value == 1
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes"}
    return False


def _line_for_token(text: str, token: str) -> int:
    for line_number, line in enumerate(text.splitlines(), start=1):
        if token in line:
            return line_number
    return 1


def _walk_config_value(
    path: Path,
    text: str,
    value: object,
    location: str = "$",
) -> list[DeletionReadinessFinding]:
    findings: list[DeletionReadinessFinding] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child_location = f"{location}.{key}"
            if str(key) == "event_list" and _is_truthy_event_list_value(item):
                findings.append(_config_finding(path, text, "event_list", child_location))
            findings.extend(_walk_config_value(path, text, item, child_location))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(_walk_config_value(path, text, item, f"{location}[{index}]"))
    elif isinstance(value, str) and EVENT_LIST_TRUE_PATTERN.search(value):
        findings.append(_config_finding(path, text, value, location))
    return findings


def _config_finding(
    path: Path,
    text: str,
    token: str,
    location: str,
) -> DeletionReadinessFinding:
    return DeletionReadinessFinding(
        path=_relative_path(path),
        line=_line_for_token(text, token),
        matched_expression=f"{location}: {token}",
        classification_suggestion=LegacyEventListDeletionReadinessVisitor._classification_for(
            "config_event_list_preparation_request"
        ),
        next_action=LegacyEventListDeletionReadinessVisitor._next_action_for(
            "config_event_list_preparation_request"
        ),
    )


def _collect_csv_event_list_entry_points(path: Path) -> list[DeletionReadinessFinding]:
    findings: list[DeletionReadinessFinding] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row_index, row in enumerate(csv.reader(handle), start=1):
            for column_index, cell in enumerate(row, start=1):
                if EVENT_LIST_TRUE_PATTERN.search(cell):
                    findings.append(
                        DeletionReadinessFinding(
                            path=_relative_path(path),
                            line=row_index,
                            matched_expression=(
                                f"row {row_index}, column {column_index}: {cell}"
                            ),
                            classification_suggestion=LegacyEventListDeletionReadinessVisitor._classification_for(
                                "config_event_list_preparation_request"
                            ),
                            next_action=LegacyEventListDeletionReadinessVisitor._next_action_for(
                                "config_event_list_preparation_request"
                            ),
                        )
                    )
    return findings


def _collect_config_event_list_entry_points() -> list[DeletionReadinessFinding]:
    findings: list[DeletionReadinessFinding] = []
    for path in _config_paths():
        suffix = path.suffix.lower()
        if suffix == ".csv":
            findings.extend(_collect_csv_event_list_entry_points(path))
            continue

        text = path.read_text(encoding="utf-8")
        if suffix == ".json":
            findings.extend(_walk_config_value(path, text, json.loads(text)))
        elif suffix == ".toml":
            findings.extend(_walk_config_value(path, text, tomllib.loads(text)))
    return findings


def _format_findings(findings: list[DeletionReadinessFinding]) -> str:
    return "\n".join(f"- {finding.message()}" for finding in findings)


def test_legacy_event_list_deletion_readiness_python_surface_has_no_blockers() -> None:
    python_findings = [
        finding
        for finding in _collect_python_findings()
        if not _is_allowed_python_finding(finding)
    ]
    preparation_findings = _collect_buff_xlogic_event_list_entry_points()
    blockers = [*python_findings, *preparation_findings]

    assert not blockers, (
        "Legacy event-list deletion readiness found Python production blockers:\n"
        + _format_findings(blockers)
    )


def test_legacy_event_list_deletion_readiness_data_surface_has_no_entry_points() -> None:
    findings = _collect_config_event_list_entry_points()

    assert not findings, (
        "Legacy event-list deletion readiness found config/data entry points:\n"
        + _format_findings(findings)
    )
