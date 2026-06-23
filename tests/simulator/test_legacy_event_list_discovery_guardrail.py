from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_ROOT = PROJECT_ROOT / "zsim" / "sim_progress"
SIMULATOR_CLASS_PATH = PROJECT_ROOT / "zsim" / "simulator" / "simulator_class.py"

RAW_EVENT_APPEND_KINDS = {
    "compatibility_only_queue_append",
    "event_context_requeue_append",
    "handler_requeue_append",
    "ambiguous_local_event_group_append",
    "local_event_group_append",
    "raw_data_event_list_append",
    "raw_event_list_append",
    "raw_schedule_data_event_list_append",
}
OWNER_ONLY_RAW_EVENT_APPEND_KINDS = {
    "compatibility_only_queue_append",
    "local_event_group_append",
}
POST_MIGRATION_BLOCKED_RAW_EVENT_APPEND_KINDS = RAW_EVENT_APPEND_KINDS - OWNER_ONLY_RAW_EVENT_APPEND_KINDS
SCHEDULED_EVENT_RAW_QUEUE_LIFECYCLE_METHODS = {
    "append",
    "clear",
    "extend",
    "insert",
    "pop",
    "remove",
    "reverse",
    "sort",
}
SCHEDULED_EVENT_RAW_QUEUE_LIFECYCLE_KINDS = {
    "scheduled_event_raw_queue_assignment",
    "scheduled_event_raw_queue_mutation",
}

LOCAL_EVENT_GROUP_NAMES = {"adrenaline_events"}
AMBIGUOUS_LOCAL_EVENT_GROUP_NAMES = {"local_event_group"}
MAIN_LOOP_RAW_PLANNED_QUEUE_NAMES = {
    "event_list",
    "event_queue",
    "planned_events",
    "planned_event_queue",
    "planned_queue",
    "scheduled_events",
    "scheduled_event_queue",
}
MAIN_LOOP_PLANNED_PRODUCER_CALLS = {
    "DamageEventJudge",
    "ScE",
    "ScheduledEvent",
    "SkillEventSplit",
}

CURRENT_ROOT_ALLOWED_EVENT_QUEUE_MUTATIONS = {
    (
        "zsim/sim_progress/data_struct/schedule_dispatch.py",
        86,
        "compatibility_only_queue_append",
        "self._event_queue.append(event)",
    ): "US-002",
    (
        "zsim/sim_progress/Character/Yixuan/AdrenalineManagerClass.py",
        17,
        "local_event_group_append",
        "adrenaline_events.append(event(char_instance=char_instance))",
    ): "US-005",
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
        self._function_stack: list[str] = []
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
        self._function_stack.append(node.name)
        self._local_event_group_stack.append(self._local_event_groups_in_scope(node))
        self.generic_visit(node)
        self._local_event_group_stack.pop()
        self._function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function_stack.append(node.name)
        self._local_event_group_stack.append(self._local_event_groups_in_scope(node))
        self.generic_visit(node)
        self._local_event_group_stack.pop()
        self._function_stack.pop()

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
        scheduled_event_lifecycle_kind = self._scheduled_event_raw_queue_call_kind(node)
        if scheduled_event_lifecycle_kind is not None:
            self._add_finding(
                line=node.lineno,
                kind=scheduled_event_lifecycle_kind,
                expression=self._source_for(node),
            )
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self._record_scheduled_event_raw_queue_assignment(node, target)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._record_scheduled_event_raw_queue_assignment(node, node.target)
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self._record_scheduled_event_raw_queue_assignment(node, node.target)
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
            if target.id in AMBIGUOUS_LOCAL_EVENT_GROUP_NAMES:
                return "ambiguous_local_event_group_append"
            if target.id == "event_list":
                return "raw_event_list_append"
            return None

        if not isinstance(target, ast.Attribute):
            return None

        if self._is_schedule_dispatch_compatibility_queue(target):
            return "compatibility_only_queue_append"

        if target.attr != "event_list":
            return None

        if self._is_event_context_requeue_api(target):
            return "event_context_requeue_append"

        owner = self._dotted_name(target.value)
        if owner == "data":
            if self._is_scheduled_event_handler_path():
                return "handler_requeue_append"
            return "raw_data_event_list_append"
        if owner and (owner == "schedule_data" or owner.endswith(".schedule_data")):
            return "raw_schedule_data_event_list_append"
        return None

    def _scheduled_event_raw_queue_call_kind(self, node: ast.Call) -> str | None:
        if not isinstance(node.func, ast.Attribute):
            return None
        if node.func.attr not in SCHEDULED_EVENT_RAW_QUEUE_LIFECYCLE_METHODS:
            return None
        if self._scheduled_event_raw_queue_target(node.func.value):
            return "scheduled_event_raw_queue_mutation"
        return None

    def _record_scheduled_event_raw_queue_assignment(
        self,
        node: ast.Assign | ast.AnnAssign | ast.AugAssign,
        target: ast.expr,
    ) -> None:
        if self._scheduled_event_raw_queue_target(target):
            self._add_finding(
                line=node.lineno,
                kind="scheduled_event_raw_queue_assignment",
                expression=self._source_for(node),
            )

    def _scheduled_event_raw_queue_target(self, target: ast.AST) -> bool:
        if self._relative_path() != "zsim/sim_progress/ScheduledEvent/__init__.py":
            return False
        if self._function_stack[-1:] == ["_replace_planned_events"]:
            return False
        if isinstance(target, ast.Subscript):
            target = target.value
        return self._dotted_name(target) in {
            "self.data.event_list",
            "data.event_list",
            "schedule_data.event_list",
        }

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

    def _is_event_context_requeue_api(self, target: ast.Attribute) -> bool:
        if (
            self._relative_path()
            != "zsim/sim_progress/ScheduledEvent/event_handlers/context.py"
        ):
            return False
        return (
            self._class_stack[-1:] == ["EventContext"]
            and self._function_stack[-1:] == ["requeue_event"]
            and self._dotted_name(target) == "self.data.event_list"
        )

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
            "event_context_requeue_append": (
                "EventContext requeue API append to current ScheduleData.event_list"
            ),
            "handler_requeue_append": (
                "handler requeue raw data.event_list.append write"
            ),
            "ambiguous_local_event_group_append": (
                "ambiguous local event group append; use a domain-specific name"
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
            "scheduled_event_raw_queue_assignment": (
                "ScheduledEvent direct raw planned queue assignment/reorder"
            ),
            "scheduled_event_raw_queue_mutation": (
                "ScheduledEvent direct raw planned queue lifecycle mutation"
            ),
        }[kind]

    @staticmethod
    def _next_action_for(kind: str) -> str:
        return {
            "find_event_list_import": "delete old discovery or retain as documented fallback",
            "find_event_list_call": "delete old discovery or retain as documented fallback",
            "buff_record_event_list_access": "delete old discovery or retain as documented fallback",
            "compatibility_only_queue_append": (
                "US-002 owns the explicit legacy schedule queue compatibility boundary"
            ),
            "event_context_requeue_append": (
                "keep requeue behind EventContext.requeue_event(...)"
            ),
            "handler_requeue_append": (
                "US-003 owns migration to an EventContext requeue API"
            ),
            "ambiguous_local_event_group_append": (
                "rename to a domain-specific local group or publish through ScheduleDispatchPort"
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
            "scheduled_event_raw_queue_assignment": (
                "US-003 owns migration to the planned queue owner replace API"
            ),
            "scheduled_event_raw_queue_mutation": (
                "US-003 owns migration to the planned queue owner lifecycle API"
            ),
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


def _raw_append_key(finding: Finding) -> tuple[str, int, str, str]:
    return (finding.path, finding.line, finding.kind, finding.matched_expression)


def _active_prd_story_ids() -> set[str]:
    prd_path = PROJECT_ROOT / "scripts" / "ralph" / "prd.json"
    prd = json.loads(prd_path.read_text(encoding="utf-8"))
    return {story["id"] for story in prd["userStories"]}


def _find_simulator_main_loop(tree: ast.Module) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "Simulator":
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == "main_loop":
                    return child
    raise AssertionError("Simulator.main_loop was not found")


def _call_name(func: ast.expr) -> str | None:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        owner = _dotted_name(node.value)
        if owner is None:
            return node.attr
        return f"{owner}.{node.attr}"
    return None


def _source_for_main_loop_node(source: str, node: ast.AST) -> str:
    segment = ast.get_source_segment(source, node)
    if segment is None:
        return f"<{type(node).__name__}>"
    return " ".join(segment.strip().split())


def _looks_like_raw_planned_queue_name(name: str) -> bool:
    return (
        name in MAIN_LOOP_RAW_PLANNED_QUEUE_NAMES
        or name.endswith("_event_list")
        or name.endswith("_event_queue")
        or name.endswith("_planned_events")
        or name.endswith("_planned_queue")
    )


def _raw_main_loop_planned_queue_expression(
    source: str,
    node: ast.AST,
    *,
    producer_call: str | None,
) -> str | None:
    if isinstance(node, ast.Attribute):
        dotted = _dotted_name(node)
        if dotted and (dotted == "event_list" or dotted.endswith(".event_list")):
            return _source_for_main_loop_node(source, node)
    if isinstance(node, ast.Name) and _looks_like_raw_planned_queue_name(node.id):
        return _source_for_main_loop_node(source, node)
    if (
        isinstance(node, (ast.List, ast.ListComp, ast.Call))
        and producer_call in MAIN_LOOP_PLANNED_PRODUCER_CALLS
    ):
        if isinstance(node, ast.Call) and _call_name(node.func) == "create_schedule_dispatch_port":
            return None
        if isinstance(node, ast.Call) and _call_name(node.func) not in {"list"}:
            return None
        return _source_for_main_loop_node(source, node)
    return None


def _collect_main_loop_raw_planned_queue_findings_from_source(source: str) -> list[str]:
    tree = ast.parse(source)
    main_loop = _find_simulator_main_loop(tree)
    findings: list[str] = []

    for node in ast.walk(main_loop):
        if not isinstance(node, ast.Call):
            continue

        call_name = _call_name(node.func)
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "append"
            and (
                expression := _raw_main_loop_planned_queue_expression(
                    source,
                    node.func.value,
                    producer_call=call_name,
                )
            )
        ):
            findings.append(f"raw append in Simulator.main_loop: {expression}.append(...)")

        if call_name == "create_schedule_dispatch_port":
            continue

        for index, arg in enumerate(node.args):
            expression = _raw_main_loop_planned_queue_expression(
                source,
                arg,
                producer_call=call_name,
            )
            if expression is not None:
                findings.append(
                    f"{call_name or '<call>'} positional arg {index} uses raw planned queue "
                    f"{expression}"
                )
        for keyword in node.keywords:
            expression = _raw_main_loop_planned_queue_expression(
                source,
                keyword.value,
                producer_call=call_name,
            )
            if expression is not None:
                name = keyword.arg or "**"
                findings.append(
                    f"{call_name or '<call>'} keyword {name} uses raw planned queue "
                    f"{expression}"
                )

    return findings


def _main_loop_damage_judge_uses_schedule_dispatch_port(source: str) -> bool:
    tree = ast.parse(source)
    main_loop = _find_simulator_main_loop(tree)

    for node in ast.walk(main_loop):
        if not isinstance(node, ast.Call) or _call_name(node.func) != "DamageEventJudge":
            continue
        return any(
            isinstance(arg, ast.Call)
            and _call_name(arg.func) == "create_schedule_dispatch_port"
            and any(
                keyword.arg == "schedule_data"
                and _dotted_name(keyword.value) == "self.schedule_data"
                for keyword in arg.keywords
            )
            for arg in node.args
        )
    return False


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


def test_raw_event_list_append_guardrail_has_only_owner_api_or_local_group_findings() -> None:
    findings = [
        finding for finding in _collect_findings() if finding.kind in RAW_EVENT_APPEND_KINDS
    ]
    actual = {_raw_append_key(finding) for finding in findings}
    expected = set(CURRENT_ROOT_ALLOWED_EVENT_QUEUE_MUTATIONS)

    assert actual == expected, (
        "Raw event-list append guardrail found unexpected production queue writes:\n"
        + "\n".join(f"- {finding.message()}" for finding in findings)
    )

    prd_story_ids = _active_prd_story_ids()
    missing_story_ids = sorted(
        {
            owner_story_id
            for owner_story_id in CURRENT_ROOT_ALLOWED_EVENT_QUEUE_MUTATIONS.values()
            if owner_story_id not in prd_story_ids
        }
    )
    assert not missing_story_ids, (
        "Current-root allowed event queue mutation entries must name follow-up stories "
        f"in scripts/ralph/prd.json; missing: {missing_story_ids}"
    )


def test_current_root_raw_planned_queue_allowlist_is_owner_only_after_migration() -> None:
    findings = [
        finding for finding in _collect_findings() if finding.kind in RAW_EVENT_APPEND_KINDS
    ]

    assert {finding.kind for finding in findings} <= OWNER_ONLY_RAW_EVENT_APPEND_KINDS
    assert not any(
        finding.kind in POST_MIGRATION_BLOCKED_RAW_EVENT_APPEND_KINDS for finding in findings
    ), (
        "Current root still contains raw planned-queue producers outside queue-owner/local "
        "event-group boundaries:\n"
        + "\n".join(f"- {finding.message()}" for finding in findings)
    )

    expected_owner_story_by_kind = {
        "compatibility_only_queue_append": "US-002",
        "local_event_group_append": "US-005",
    }
    for key, owner_story_id in CURRENT_ROOT_ALLOWED_EVENT_QUEUE_MUTATIONS.items():
        _path, _line, kind, _matched_expression = key
        assert kind in OWNER_ONLY_RAW_EVENT_APPEND_KINDS
        assert owner_story_id == expected_owner_story_by_kind[kind]


def test_scheduled_event_raw_queue_lifecycle_has_no_current_findings() -> None:
    findings = [
        finding
        for finding in _collect_findings()
        if finding.kind in SCHEDULED_EVENT_RAW_QUEUE_LIFECYCLE_KINDS
    ]

    _assert_no_disallowed(findings)


def test_main_loop_uses_dispatch_port_and_has_no_raw_planned_queue_handoff() -> None:
    source = SIMULATOR_CLASS_PATH.read_text(encoding="utf-8")

    findings = _collect_main_loop_raw_planned_queue_findings_from_source(source)

    assert findings == []
    assert _main_loop_damage_judge_uses_schedule_dispatch_port(source)


def test_main_loop_raw_planned_queue_guardrail_blocks_synthetic_regressions() -> None:
    source = (
        "class Simulator:\n"
        "    def main_loop(self):\n"
        "        event_list = []\n"
        "        DamageEventJudge(self.tick, missions, enemy, self.schedule_data.event_list, chars)\n"
        "        ScheduledEvent(dynamic_buff, schedule_data, self.tick, event_list)\n"
        "        self.schedule_data.event_list.append(payload)\n"
    )

    findings = _collect_main_loop_raw_planned_queue_findings_from_source(source)

    assert any(
        "DamageEventJudge positional arg 3 uses raw planned queue "
        "self.schedule_data.event_list" in finding
        for finding in findings
    )
    assert any(
        "ScheduledEvent positional arg 3 uses raw planned queue event_list" in finding
        for finding in findings
    )
    assert any(
        "raw append in Simulator.main_loop: self.schedule_data.event_list.append(...)"
        in finding
        for finding in findings
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
            PRODUCTION_ROOT
            / "ScheduledEvent"
            / "event_handlers"
            / "context.py",
            (
                "class EventContext:\n"
                "    def requeue_event(self, event):\n"
                "        self.data.event_list.append(event)\n"
            ),
            "EventContext requeue API append to current ScheduleData.event_list",
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
        (
            PRODUCTION_ROOT / "Character" / "Yixuan" / "AdrenalineManagerClass.py",
            (
                "def factory(event):\n"
                "    local_event_group = []\n"
                "    local_event_group.append(event)\n"
            ),
            "ambiguous local event group append; use a domain-specific name",
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


def test_local_event_group_classification_requires_domain_specific_name() -> None:
    yixuan_path = PRODUCTION_ROOT / "Character" / "Yixuan" / "AdrenalineManagerClass.py"
    ambiguous_source = (
        "def factory(event):\n"
        "    local_event_group = []\n"
        "    local_event_group.append(event)\n"
    )
    visitor = LegacyEventListDiscoveryVisitor(yixuan_path, ambiguous_source)
    visitor.visit(ast.parse(ambiguous_source))

    assert len(visitor.findings) == 1
    assert visitor.findings[0].kind == "ambiguous_local_event_group_append"
    assert (
        visitor.findings[0].classification_suggestion
        == "ambiguous local event group append; use a domain-specific name"
    )


def test_raw_planned_queue_writes_are_blocked_outside_owner_api_or_local_groups() -> None:
    samples = [
        (
            PRODUCTION_ROOT / "Load" / "LoadDamageEvent.py",
            "def publish(event_list, event):\n    event_list.append(event)\n",
            "raw_event_list_append",
        ),
        (
            PRODUCTION_ROOT
            / "ScheduledEvent"
            / "event_handlers"
            / "handlers"
            / "preload.py",
            "def requeue(data, event):\n    data.event_list.append(event)\n",
            "handler_requeue_append",
        ),
        (
            PRODUCTION_ROOT / "Buff" / "BuffXLogic" / "_synthetic_queue_write.py",
            "def publish(record, event):\n    record.event_list.append(event)\n",
            "record_event_list_append",
        ),
        (
            PRODUCTION_ROOT / "Character" / "Yixuan" / "_synthetic_raw_queue.py",
            "def publish(event_list, event):\n    event_list.append(event)\n",
            "raw_event_list_append",
        ),
        (
            PRODUCTION_ROOT / "Enemy" / "_synthetic_raw_queue.py",
            "def publish(schedule_data, event):\n    schedule_data.event_list.append(event)\n",
            "raw_schedule_data_event_list_append",
        ),
        (
            PRODUCTION_ROOT / "Update" / "UpdateAnomaly.py",
            "def publish(schedule_data, event):\n    schedule_data.event_list.append(event)\n",
            "raw_schedule_data_event_list_append",
        ),
    ]

    allowed_keys = set(CURRENT_ROOT_ALLOWED_EVENT_QUEUE_MUTATIONS)
    for path, source, expected_kind in samples:
        visitor = LegacyEventListDiscoveryVisitor(path, source)
        visitor.visit(ast.parse(source))

        assert len(visitor.findings) == 1
        finding = visitor.findings[0]
        assert finding.kind == expected_kind
        assert _raw_append_key(finding) not in allowed_keys


def test_scheduled_event_raw_queue_lifecycle_guardrail_blocks_regressions() -> None:
    source = (
        "class ScheduledEvent:\n"
        "    def process_event(self, event):\n"
        "        self.data.event_list.remove(event)\n"
        "        self.data.event_list.insert(0, event)\n"
        "    def solve_buff(self, events):\n"
        "        self.data.event_list = list(events)\n"
    )
    path = PRODUCTION_ROOT / "ScheduledEvent" / "__init__.py"
    visitor = LegacyEventListDiscoveryVisitor(path, source)

    visitor.visit(ast.parse(source))

    assert [finding.kind for finding in visitor.findings] == [
        "scheduled_event_raw_queue_mutation",
        "scheduled_event_raw_queue_mutation",
        "scheduled_event_raw_queue_assignment",
    ]
    assert (
        visitor.findings[0].classification_suggestion
        == "ScheduledEvent direct raw planned queue lifecycle mutation"
    )
    assert (
        visitor.findings[2].next_action
        == "US-003 owns migration to the planned queue owner replace API"
    )


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
