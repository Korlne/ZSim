from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_ROOT = PROJECT_ROOT / "zsim" / "sim_progress"

RAW_EVENT_APPEND_KINDS = {
    "compatibility_only_queue_append",
    "handler_requeue_append",
    "raw_data_event_list_append",
    "raw_event_list_append",
    "raw_schedule_data_event_list_append",
}

LOCAL_EVENT_GROUP_NAMES = {"adrenaline_events", "local_event_group"}

TEMPORARY_RAW_EVENT_APPEND_ALLOWLIST = {
    (
        "zsim/sim_progress/data_struct/schedule_dispatch.py",
        "compatibility_only_queue_append",
        "self._event_queue.append(event)",
    ): "US-003",
}


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
        self._local_event_group_stack: list[set[str]] = []

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

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._local_event_group_stack.append(self._local_event_groups_in_scope(node))
        self.generic_visit(node)
        self._local_event_group_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._local_event_group_stack.append(self._local_event_groups_in_scope(node))
        self.generic_visit(node)
        self._local_event_group_stack.pop()

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
        raw_append_kind = self._raw_event_append_kind(node)
        if raw_append_kind is not None:
            self._add_finding(
                line=node.lineno,
                kind=raw_append_kind,
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

    def _raw_event_append_kind(self, node: ast.Call) -> str | None:
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "append":
            return None

        target = node.func.value
        if isinstance(target, ast.Name):
            if self._is_local_event_group_name(target.id):
                return "local_event_group_append"
            if target.id == "event_list":
                return "raw_event_list_append"
            return None

        if not isinstance(target, ast.Attribute):
            return None

        if self._is_schedule_dispatch_compatibility_queue(target):
            return "compatibility_only_queue_append"

        if target.attr != "event_list":
            return None

        owner = self._dotted_name(target.value)
        if owner == "data":
            if self._is_scheduled_event_handler_path():
                return "handler_requeue_append"
            return "raw_data_event_list_append"
        if owner and (owner == "schedule_data" or owner.endswith(".schedule_data")):
            return "raw_schedule_data_event_list_append"
        return None

    def _is_scheduled_event_handler_path(self) -> bool:
        return self._relative_path().startswith(
            "zsim/sim_progress/ScheduledEvent/event_handlers/handlers/"
        )

    def _is_local_event_group_name(self, name: str) -> bool:
        return bool(self._local_event_group_stack) and name in self._local_event_group_stack[-1]

    def _local_event_groups_in_scope(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> set[str]:
        names: set[str] = set()
        for statement in node.body:
            names.update(self._local_event_group_assignments(statement))
        return names

    def _local_event_group_assignments(self, node: ast.AST) -> set[str]:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            return set()

        names: set[str] = set()
        if isinstance(node, ast.Assign) and self._is_new_list(node.value):
            for target in node.targets:
                names.update(self._local_event_group_target_names(target))
        elif isinstance(node, ast.AnnAssign) and node.value and self._is_new_list(node.value):
            names.update(self._local_event_group_target_names(node.target))

        for child in ast.iter_child_nodes(node):
            names.update(self._local_event_group_assignments(child))
        return names

    @staticmethod
    def _is_new_list(node: ast.AST) -> bool:
        if isinstance(node, ast.List):
            return True
        return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "list"

    @staticmethod
    def _local_event_group_target_names(target: ast.AST) -> set[str]:
        if isinstance(target, ast.Name) and target.id in LOCAL_EVENT_GROUP_NAMES:
            return {target.id}
        return set()

    def _is_schedule_dispatch_compatibility_queue(self, target: ast.Attribute) -> bool:
        if self._relative_path() != "zsim/sim_progress/data_struct/schedule_dispatch.py":
            return False
        return self._dotted_name(target) in {"_event_queue", "self._event_queue"}

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
            "compatibility_only_queue_append": (
                "compatibility-only queue append inside schedule dispatch adapter"
            ),
            "handler_requeue_append": (
                "handler requeue raw data.event_list.append write"
            ),
            "local_event_group_append": (
                "local event group append; not ScheduleData.event_list"
            ),
            "raw_data_event_list_append": (
                "planned queue raw data.event_list.append write"
            ),
            "raw_event_list_append": "planned queue raw event_list.append write",
            "raw_schedule_data_event_list_append": (
                "planned queue raw schedule_data.event_list.append write"
            ),
            "record_event_list_append": "producer-level planned-event writer through record.event_list",
        }[kind]

    @staticmethod
    def _next_action_for(kind: str) -> str:
        return {
            "find_event_list_import": "delete old discovery or retain as documented fallback",
            "find_event_list_call": "delete old discovery or retain as documented fallback",
            "buff_record_event_list_access": "delete old discovery or retain as documented fallback",
            "compatibility_only_queue_append": (
                "US-003 owns the schedule queue implementation boundary"
            ),
            "handler_requeue_append": (
                "US-004 owns migration to an EventContext requeue API"
            ),
            "local_event_group_append": (
                "keep local event groups distinctly named and outside ScheduleData.event_list"
            ),
            "raw_data_event_list_append": "publish planned payloads through ScheduleDispatchPort",
            "raw_event_list_append": (
                "US-002 owns migration to ScheduleDispatchPort-backed publishing"
            ),
            "raw_schedule_data_event_list_append": (
                "publish planned payloads through ScheduleDispatchPort"
            ),
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


def _raw_append_key(finding: Finding) -> tuple[str, str, str]:
    return (finding.path, finding.kind, finding.matched_expression)


def _active_prd_story_ids() -> set[str]:
    prd_path = PROJECT_ROOT / "scripts" / "ralph" / "prd.json"
    prd = json.loads(prd_path.read_text(encoding="utf-8"))
    return {story["id"] for story in prd["userStories"]}


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


def test_raw_event_list_append_guardrail_has_only_follow_up_owned_findings() -> None:
    findings = [
        finding for finding in _collect_findings() if finding.kind in RAW_EVENT_APPEND_KINDS
    ]
    actual = {_raw_append_key(finding) for finding in findings}
    expected = set(TEMPORARY_RAW_EVENT_APPEND_ALLOWLIST)

    assert actual == expected, (
        "Raw event-list append guardrail found unexpected production queue writes:\n"
        + "\n".join(f"- {finding.message()}" for finding in findings)
    )

    prd_story_ids = _active_prd_story_ids()
    missing_story_ids = sorted(
        {
            owner_story_id
            for owner_story_id in TEMPORARY_RAW_EVENT_APPEND_ALLOWLIST.values()
            if owner_story_id not in prd_story_ids
        }
    )
    assert not missing_story_ids, (
        "Temporary raw append allowlist entries must name follow-up stories "
        f"in scripts/ralph/prd.json; missing: {missing_story_ids}"
    )


def test_raw_event_list_append_guardrail_reports_event_layer_classifications() -> None:
    samples = [
        (
            PRODUCTION_ROOT / "Load" / "LoadDamageEvent.py",
            "def publish(event_list, event):\n    event_list.append(event)\n",
            "planned queue raw event_list.append write",
        ),
        (
            PRODUCTION_ROOT
            / "ScheduledEvent"
            / "event_handlers"
            / "handlers"
            / "preload.py",
            "def requeue(data, event):\n    data.event_list.append(event)\n",
            "handler requeue raw data.event_list.append write",
        ),
        (
            PRODUCTION_ROOT / "data_struct" / "schedule_dispatch.py",
            "class Adapter:\n    def publish(self, event):\n        self._event_queue.append(event)\n",
            "compatibility-only queue append inside schedule dispatch adapter",
        ),
        (
            PRODUCTION_ROOT / "data_struct" / "_synthetic_raw_schedule_data.py",
            "def publish(schedule_data, event):\n    schedule_data.event_list.append(event)\n",
            "planned queue raw schedule_data.event_list.append write",
        ),
        (
            PRODUCTION_ROOT / "Character" / "Yixuan" / "AdrenalineManagerClass.py",
            (
                "def factory(event):\n"
                "    adrenaline_events = []\n"
                "    adrenaline_events.append(event)\n"
            ),
            "local event group append; not ScheduleData.event_list",
        ),
    ]

    messages: list[str] = []
    for path, source, _classification in samples:
        tree = ast.parse(source)
        visitor = LegacyEventListDiscoveryVisitor(path, source)
        visitor.visit(tree)
        messages.extend(finding.message() for finding in visitor.findings)

    for _path, _source, classification in samples:
        assert any(
            f"classification suggestion: {classification}" in message
            for message in messages
        )


def test_local_event_group_classification_uses_name_and_scope_not_path() -> None:
    yixuan_path = PRODUCTION_ROOT / "Character" / "Yixuan" / "AdrenalineManagerClass.py"
    local_source = (
        "def factory(event):\n"
        "    adrenaline_events = []\n"
        "    adrenaline_events.append(event)\n"
    )
    local_visitor = LegacyEventListDiscoveryVisitor(yixuan_path, local_source)
    local_visitor.visit(ast.parse(local_source))

    assert len(local_visitor.findings) == 1
    assert local_visitor.findings[0].kind == "local_event_group_append"
    assert (
        local_visitor.findings[0].classification_suggestion
        == "local event group append; not ScheduleData.event_list"
    )

    raw_source = "def publish(event_list, event):\n    event_list.append(event)\n"
    raw_visitor = LegacyEventListDiscoveryVisitor(yixuan_path, raw_source)
    raw_visitor.visit(ast.parse(raw_source))

    assert len(raw_visitor.findings) == 1
    assert raw_visitor.findings[0].kind == "raw_event_list_append"


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
