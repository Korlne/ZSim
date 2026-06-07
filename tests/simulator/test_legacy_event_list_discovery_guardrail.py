from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_ROOT = PROJECT_ROOT / "zsim" / "sim_progress"


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    kind: str
    matched_expression: str
    classification_suggestion: str
    next_action: str

    def message(self) -> str:
        return (
            f"{self.path}:{self.line}: matched expression: {self.matched_expression}; "
            f"classification suggestion: {self.classification_suggestion}; "
            f"next action: {self.next_action}"
        )


class LegacyEventListDiscoveryVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source: str) -> None:
        self.path = path
        self.source = source
        self.findings: list[Finding] = []
        self._parents: list[ast.AST] = []
        self._class_stack: list[str] = []

    def visit(self, node: ast.AST):
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
                line = getattr(alias, "lineno", node.lineno)
                self._add_finding(
                    line=line,
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
        self.findings.append(
            Finding(
                path=self._relative_path(),
                line=line,
                kind=kind,
                matched_expression=self._normalize(expression),
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
            "find_event_list_import": "deleted legacy discovery import",
            "find_event_list_call": "deleted legacy discovery call",
            "buff_record_event_list_access": "deleted BuffRecordBaseClass.event_list cache access",
            "record_event_list_append": "producer-level planned-event writer through record.event_list",
        }[kind]

    @staticmethod
    def _next_action_for(kind: str) -> str:
        return {
            "find_event_list_import": "delete old discovery or retain as documented fallback",
            "find_event_list_call": "delete old discovery or retain as documented fallback",
            "buff_record_event_list_access": "delete old discovery or retain as documented fallback",
            "record_event_list_append": "migrate to ScheduleDispatchPort or block deletion",
        }[kind]


def _production_python_files() -> list[Path]:
    return sorted(
        path
        for path in PRODUCTION_ROOT.rglob("*.py")
        if "__pycache__" not in path.parts
    )


def _collect_findings() -> list[Finding]:
    findings: list[Finding] = []
    for path in _production_python_files():
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        visitor = LegacyEventListDiscoveryVisitor(path, source)
        visitor.visit(tree)
        findings.extend(visitor.findings)
    return findings


def _assert_no_disallowed(findings: list[Finding]) -> None:
    assert not findings, (
        "Legacy event-list discovery guardrail found disallowed production uses:\n"
        + "\n".join(f"- {finding.message()}" for finding in findings)
    )


def test_find_event_list_legacy_discovery_surface_has_no_new_production_uses() -> None:
    findings = [
        finding
        for finding in _collect_findings()
        if finding.kind in {"find_event_list_import", "find_event_list_call"}
    ]

    _assert_no_disallowed(findings)


def test_buff_record_event_list_cache_has_no_new_production_uses() -> None:
    findings = [
        finding
        for finding in _collect_findings()
        if finding.kind in {"buff_record_event_list_access", "record_event_list_append"}
    ]

    _assert_no_disallowed(findings)


def test_guardrail_failure_message_includes_post_deletion_triage_fields() -> None:
    source = "def publish(record, payload):\n    record.event_list.append(payload)\n"
    path = PRODUCTION_ROOT / "Buff" / "BuffXLogic" / "_synthetic_guardrail_fixture.py"
    tree = ast.parse(source)
    visitor = LegacyEventListDiscoveryVisitor(path, source)
    visitor.visit(tree)

    assert len(visitor.findings) == 1
    message = visitor.findings[0].message()
    assert "zsim/sim_progress/Buff/BuffXLogic/_synthetic_guardrail_fixture.py:2" in message
    assert "matched expression: record.event_list.append(payload)" in message
    assert (
        "classification suggestion: producer-level planned-event writer through record.event_list"
        in message
    )
    assert "next action: migrate to ScheduleDispatchPort or block deletion" in message


def test_deleted_buff_record_event_list_field_is_not_allowlisted() -> None:
    source = (
        "class BuffRecordBaseClass:\n"
        "    def __init__(self):\n"
        "        self.event_list: list | None = None\n"
    )
    path = (
        PRODUCTION_ROOT
        / "Buff"
        / "BuffXLogic"
        / "_synthetic_buff_record_base_class.py"
    )
    tree = ast.parse(source)
    visitor = LegacyEventListDiscoveryVisitor(path, source)
    visitor.visit(tree)

    assert len(visitor.findings) == 1
    assert visitor.findings[0].kind == "buff_record_event_list_access"
    assert (
        visitor.findings[0].classification_suggestion
        == "deleted BuffRecordBaseClass.event_list cache access"
    )
