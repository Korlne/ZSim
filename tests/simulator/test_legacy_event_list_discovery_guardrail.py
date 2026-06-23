from __future__ import annotations

import ast
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_ROOT = PROJECT_ROOT / "zsim" / "sim_progress"
SIMULATOR_ROOT = PROJECT_ROOT / "zsim" / "simulator"
PRODUCTION_SCAN_ROOTS = (PRODUCTION_ROOT, SIMULATOR_ROOT)
SIMULATOR_CLASS_PATH = PROJECT_ROOT / "zsim" / "simulator" / "simulator_class.py"
SCHEDULED_EVENT_PATH = PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent" / "__init__.py"
RUNTIME_COMMAND_PATH = (
    PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent" / "runtime_command.py"
)
LOAD_DAMAGE_EVENT_PATH = (
    PROJECT_ROOT / "zsim" / "sim_progress" / "Load" / "LoadDamageEvent.py"
)
LEGACY_EVENT_LIST_ADAPTER_NAME = "LegacyEventListScheduleDispatchAdapter"
DEFAULT_PATH_LEGACY_ADAPTER_PROHIBITED_FILES = (
    SIMULATOR_CLASS_PATH,
    SCHEDULED_EVENT_PATH,
    RUNTIME_COMMAND_PATH,
    LOAD_DAMAGE_EVENT_PATH,
)


@dataclass(frozen=True)
class CompatibilityAllowance:
    owner: str
    story: str
    rationale: str


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
RAW_PLANNED_QUEUE_LIFECYCLE_KINDS = {
    "raw_data_event_list_lifecycle_assignment",
    "raw_data_event_list_lifecycle_mutation",
    "raw_event_list_lifecycle_assignment",
    "raw_event_list_lifecycle_mutation",
    "raw_planned_queue_handoff",
    "raw_schedule_data_event_list_lifecycle_assignment",
    "raw_schedule_data_event_list_lifecycle_mutation",
}
RAW_PLANNED_QUEUE_FALLBACK_KINDS = {
    "raw_planned_queue_fallback_read",
}
PLANNED_QUEUE_OWNER_INTERNAL_KINDS = {
    "planned_queue_owner_internal_mutation",
    "planned_queue_owner_internal_replacement",
}
PLANNED_QUEUE_COMPATIBILITY_VIEW_KINDS = {
    "planned_queue_compatibility_view_read",
}
SCHEDULE_DATA_EVENT_LIST_COMPATIBILITY_KINDS = {
    "schedule_data_event_list_constructor_field",
    "schedule_data_event_list_owner_read",
    "schedule_data_event_list_owner_rebind",
    "schedule_data_event_list_property_getter",
    "schedule_data_event_list_property_setter",
    "schedule_data_event_list_property_install",
}
CURRENT_ROOT_EVENT_QUEUE_GUARDRAIL_KINDS = (
    RAW_EVENT_APPEND_KINDS
    | SCHEDULED_EVENT_RAW_QUEUE_LIFECYCLE_KINDS
    | RAW_PLANNED_QUEUE_LIFECYCLE_KINDS
    | RAW_PLANNED_QUEUE_FALLBACK_KINDS
    | PLANNED_QUEUE_OWNER_INTERNAL_KINDS
)

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
        "zsim/sim_progress/data_struct/planned_queue.py",
        31,
        "planned_queue_owner_internal_mutation",
        "self._events().append(event)",
    ): "US-001",
    (
        "zsim/sim_progress/data_struct/planned_queue.py",
        44,
        "planned_queue_owner_internal_mutation",
        "self._events().remove(event)",
    ): "US-001",
    (
        "zsim/sim_progress/data_struct/planned_queue.py",
        47,
        "planned_queue_owner_internal_replacement",
        "self._set_events(list(events))",
    ): "US-001",
    (
        "zsim/sim_progress/data_struct/planned_queue.py",
        50,
        "planned_queue_owner_internal_mutation",
        "self._events().clear()",
    ): "US-001",
    (
        "zsim/sim_progress/Character/Yixuan/AdrenalineManagerClass.py",
        17,
        "local_event_group_append",
        "adrenaline_events.append(event(char_instance=char_instance))",
    ): "US-005",
}

CURRENT_ROOT_ALLOWED_COMPATIBILITY_VIEW_READS: dict[tuple[str, int, str, str], str] = {}

CURRENT_ROOT_ALLOWED_SCHEDULE_DATA_EVENT_LIST_COMPATIBILITY: dict[
    tuple[str, int, str, str], CompatibilityAllowance
] = {}


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


@dataclass(frozen=True)
class MigrationSurface:
    path: str
    line: int
    function: str
    kind: str
    matched_expression: str


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
        planned_queue_owner_kind = self._planned_queue_owner_internal_call_kind(node)
        if planned_queue_owner_kind is not None:
            self._add_finding(
                line=node.lineno,
                kind=planned_queue_owner_kind,
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
        raw_lifecycle_kind = None
        if raw_append_kind is None and scheduled_event_lifecycle_kind is None:
            raw_lifecycle_kind = self._raw_planned_queue_lifecycle_call_kind(node)
        if raw_lifecycle_kind is not None:
            self._add_finding(
                line=node.lineno,
                kind=raw_lifecycle_kind,
                expression=self._source_for(node),
            )
        raw_handoff_kind = self._raw_planned_queue_handoff_kind(node)
        if raw_handoff_kind is not None:
            self._add_finding(
                line=node.lineno,
                kind=raw_handoff_kind,
                expression=self._source_for(node),
            )
        raw_fallback_kind = self._raw_planned_queue_fallback_call_kind(node)
        if raw_fallback_kind is not None:
            self._add_finding(
                line=node.lineno,
                kind=raw_fallback_kind,
                expression=self._source_for(node),
            )
        self.generic_visit(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        if (
            self._raw_planned_queue_target_kind(node.body) is not None
            and not self._is_allowed_planned_queue_compatibility_owner()
        ):
            self._add_finding(
                line=node.lineno,
                kind="raw_planned_queue_fallback_read",
                expression=self._source_for(node),
            )
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if not self._record_scheduled_event_raw_queue_assignment(node, target):
                self._record_raw_planned_queue_lifecycle_assignment(node, target)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if not self._record_scheduled_event_raw_queue_assignment(node, node.target):
            self._record_raw_planned_queue_lifecycle_assignment(node, node.target)
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        if not self._record_scheduled_event_raw_queue_assignment(node, node.target):
            self._record_raw_planned_queue_lifecycle_assignment(node, node.target)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        compatibility_view_kind = self._planned_queue_compatibility_view_read_kind(node)
        if compatibility_view_kind is not None:
            self._add_finding(
                line=node.lineno,
                kind=compatibility_view_kind,
                expression=self._attribute_context(node),
            )
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

    def _planned_queue_owner_internal_call_kind(self, node: ast.Call) -> str | None:
        if self._relative_path() != "zsim/sim_progress/data_struct/planned_queue.py":
            return None
        if not isinstance(node.func, ast.Attribute):
            return None
        call_target = node.func.value
        if (
            node.func.attr in {"append", "remove", "clear"}
            and isinstance(call_target, ast.Call)
            and self._dotted_name(call_target.func) == "self._events"
        ):
            return "planned_queue_owner_internal_mutation"
        if self._dotted_name(node.func) == "self._set_events":
            return "planned_queue_owner_internal_replacement"
        return None

    def _planned_queue_compatibility_view_read_kind(
        self,
        node: ast.Attribute,
    ) -> str | None:
        if node.attr != "compatibility_view":
            return None
        if not isinstance(node.ctx, ast.Load):
            return None
        return "planned_queue_compatibility_view_read"

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
    ) -> bool:
        if self._scheduled_event_raw_queue_target(target):
            self._add_finding(
                line=node.lineno,
                kind="scheduled_event_raw_queue_assignment",
                expression=self._source_for(node),
            )
            return True
        return False

    def _raw_planned_queue_lifecycle_call_kind(self, node: ast.Call) -> str | None:
        if not isinstance(node.func, ast.Attribute):
            return None
        if node.func.attr not in SCHEDULED_EVENT_RAW_QUEUE_LIFECYCLE_METHODS:
            return None
        target_kind = self._raw_planned_queue_target_kind(node.func.value)
        if target_kind is None:
            return None
        return f"{target_kind}_lifecycle_mutation"

    def _record_raw_planned_queue_lifecycle_assignment(
        self,
        node: ast.Assign | ast.AnnAssign | ast.AugAssign,
        target: ast.expr,
    ) -> None:
        if self._is_schedule_data_event_list_field_declaration(target):
            return
        if self._is_allowed_planned_queue_replacement_owner():
            return
        target_kind = self._raw_planned_queue_target_kind(target)
        if target_kind is None:
            return
        self._add_finding(
            line=node.lineno,
            kind=f"{target_kind}_lifecycle_assignment",
            expression=self._source_for(node),
        )

    def _raw_planned_queue_handoff_kind(self, node: ast.Call) -> str | None:
        call_name = self._call_name(node.func)
        if call_name not in MAIN_LOOP_PLANNED_PRODUCER_CALLS:
            return None
        if any(self._raw_planned_queue_handoff_expression(arg) for arg in node.args):
            return "raw_planned_queue_handoff"
        if any(
            self._raw_planned_queue_handoff_expression(keyword.value)
            for keyword in node.keywords
        ):
            return "raw_planned_queue_handoff"
        return None

    def _raw_planned_queue_handoff_expression(self, node: ast.AST) -> str | None:
        if self._raw_planned_queue_target_kind(node) is not None:
            return self._source_for(node)
        if isinstance(node, ast.Name) and _looks_like_raw_planned_queue_name(node.id):
            return self._source_for(node)
        if (
            isinstance(node, ast.Call)
            and self._call_name(node.func) == "list"
            and node.args
            and self._raw_planned_queue_handoff_expression(node.args[0]) is not None
        ):
            return self._source_for(node)
        return None

    def _raw_planned_queue_fallback_call_kind(self, node: ast.Call) -> str | None:
        call_name = self._call_name(node.func)
        if (
            call_name == "getattr"
            and len(node.args) >= 2
            and _string_literal_value(node.args[1]) == "event_list"
            and self._raw_planned_queue_owner_kind(node.args[0]) is not None
            and not self._is_allowed_planned_queue_compatibility_owner()
        ):
            return "raw_planned_queue_fallback_read"
        if (
            call_name == "setattr"
            and len(node.args) >= 2
            and _string_literal_value(node.args[1]) == "event_list"
            and self._raw_planned_queue_owner_kind(node.args[0]) is not None
            and not self._is_allowed_planned_queue_compatibility_owner()
        ):
            return f"{self._raw_planned_queue_owner_kind(node.args[0])}_lifecycle_assignment"
        return None

    def _raw_planned_queue_owner_kind(self, owner: ast.AST) -> str | None:
        dotted = self._dotted_name(owner)
        if dotted in {"data", "self.data"}:
            return "raw_data_event_list"
        if dotted in {"schedule_data", "self.schedule_data", "_schedule_data", "self._schedule_data"}:
            return "raw_schedule_data_event_list"
        if dotted and dotted.endswith(".schedule_data"):
            return "raw_schedule_data_event_list"
        return None

    def _raw_planned_queue_target_kind(self, target: ast.AST) -> str | None:
        if isinstance(target, ast.Subscript):
            target = target.value
        if isinstance(target, ast.Name):
            if target.id == "event_list":
                return "raw_event_list"
            return None
        dotted = self._dotted_name(target)
        if dotted is None:
            return None
        if dotted == "event_list":
            return "raw_event_list"
        if not dotted.endswith(".event_list"):
            return None
        owner = dotted.removesuffix(".event_list")
        if owner in {"data", "self.data"}:
            return "raw_data_event_list"
        if owner in {"schedule_data", "self.schedule_data", "_schedule_data", "self._schedule_data"}:
            return "raw_schedule_data_event_list"
        if owner.endswith(".schedule_data"):
            return "raw_schedule_data_event_list"
        return None

    def _is_allowed_planned_queue_replacement_owner(self) -> bool:
        relative_path = self._relative_path()
        return (
            relative_path == "zsim/simulator/dataclasses.py"
            and self._class_stack[-1:] == ["ScheduleData"]
            and self._function_stack[-1:] == ["_replace_planned_events"]
        )

    def _is_allowed_planned_queue_compatibility_owner(self) -> bool:
        relative_path = self._relative_path()
        if relative_path == "zsim/sim_progress/data_struct/planned_queue.py":
            return self._function_stack[-1:] == [
                "ensure_event_list_migration_planned_event_queue"
            ]
        return self._is_allowed_planned_queue_replacement_owner()

    def _is_schedule_data_event_list_field_declaration(self, target: ast.expr) -> bool:
        return (
            self._relative_path() == "zsim/simulator/dataclasses.py"
            and self._class_stack[-1:] == ["ScheduleData"]
            and not self._function_stack
            and isinstance(target, ast.Name)
            and target.id == "event_list"
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
    def _call_name(func: ast.expr) -> str | None:
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return func.attr
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
            "planned_queue_owner_internal_mutation": (
                "planned queue owner internal compatibility-view lifecycle mutation"
            ),
            "planned_queue_owner_internal_replacement": (
                "planned queue owner internal compatibility-view replacement"
            ),
            "planned_queue_compatibility_view_read": (
                "PlannedEventQueue raw compatibility view read"
            ),
            "raw_data_event_list_append": (
                "planned queue raw data.event_list.append write"
            ),
            "raw_event_list_append": "planned queue raw event_list.append write",
            "raw_schedule_data_event_list_append": (
                "planned queue raw schedule_data.event_list.append write"
            ),
            "raw_data_event_list_lifecycle_assignment": (
                "planned queue raw data.event_list list replacement"
            ),
            "raw_data_event_list_lifecycle_mutation": (
                "planned queue raw data.event_list lifecycle mutation"
            ),
            "raw_event_list_lifecycle_assignment": (
                "planned queue raw event_list list replacement"
            ),
            "raw_event_list_lifecycle_mutation": (
                "planned queue raw event_list lifecycle mutation"
            ),
            "raw_planned_queue_handoff": (
                "raw planned queue handed to planned-event producer"
            ),
            "raw_planned_queue_fallback_read": (
                "raw planned queue compatibility fallback read outside owner"
            ),
            "raw_schedule_data_event_list_lifecycle_assignment": (
                "planned queue raw schedule_data.event_list list replacement"
            ),
            "raw_schedule_data_event_list_lifecycle_mutation": (
                "planned queue raw schedule_data.event_list lifecycle mutation"
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
            "planned_queue_owner_internal_mutation": (
                "keep raw lifecycle mutation inside PlannedEventQueue owner APIs"
            ),
            "planned_queue_owner_internal_replacement": (
                "keep raw replacement inside PlannedEventQueue owner APIs"
            ),
            "planned_queue_compatibility_view_read": (
                "delete compatibility_view reads or move them to an explicitly private migration helper"
            ),
            "raw_data_event_list_append": "publish planned payloads through ScheduleDispatchPort",
            "raw_event_list_append": (
                "US-002 owns migration to ScheduleDispatchPort-backed publishing"
            ),
            "raw_schedule_data_event_list_append": (
                "publish planned payloads through ScheduleDispatchPort"
            ),
            "raw_data_event_list_lifecycle_assignment": (
                "replace through ScheduleData.planned_event_queue owner APIs"
            ),
            "raw_data_event_list_lifecycle_mutation": (
                "mutate through ScheduleData.planned_event_queue owner APIs"
            ),
            "raw_event_list_lifecycle_assignment": (
                "replace through ScheduleData.planned_event_queue owner APIs"
            ),
            "raw_event_list_lifecycle_mutation": (
                "mutate through ScheduleData.planned_event_queue owner APIs"
            ),
            "raw_planned_queue_handoff": (
                "pass ScheduleDispatchPort/EventInbox owner APIs instead of raw queue"
            ),
            "raw_planned_queue_fallback_read": (
                "install an explicit migration owner before raw fallback reads"
            ),
            "raw_schedule_data_event_list_lifecycle_assignment": (
                "replace through ScheduleData.planned_event_queue owner APIs"
            ),
            "raw_schedule_data_event_list_lifecycle_mutation": (
                "mutate through ScheduleData.planned_event_queue owner APIs"
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
        for root in PRODUCTION_SCAN_ROOTS
        for path in root.rglob("*.py")
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


def _scope_name(class_stack: list[str], function_stack: list[str]) -> str:
    if not function_stack:
        return "<module>"
    if class_stack:
        return f"{'.'.join(class_stack)}.{function_stack[-1]}"
    return function_stack[-1]


class PlannedQueueMigrationSurfaceVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source: str) -> None:
        self.path = path
        self.source = source
        self.surfaces: list[MigrationSurface] = []
        self._class_stack: list[str] = []
        self._function_stack: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function_stack.append(node.name)
        if node.name == "_raw_events_for_migration":
            self._add_surface(
                line=node.lineno,
                kind="private_raw_migration_helper_definition",
                expression=_source_line(self.source, node.lineno),
            )
        self.generic_visit(node)
        self._function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function_stack.append(node.name)
        self.generic_visit(node)
        self._function_stack.pop()

    def visit_Call(self, node: ast.Call) -> None:
        call_name = _call_name(node.func)
        if call_name == "PlannedEventQueue" and self._is_event_list_backed_owner(
            node
        ):
            self._add_surface(
                line=node.lineno,
                kind="event_list_migration_owner_construction",
                expression=_source_for_main_loop_node(self.source, node),
            )
        elif call_name == "ensure_event_list_migration_planned_event_queue":
            self._add_surface(
                line=node.lineno,
                kind="event_list_migration_owner_helper_call",
                expression=_source_for_main_loop_node(self.source, node),
            )
        elif (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "_raw_events_for_migration"
        ):
            self._add_surface(
                line=node.lineno,
                kind="private_raw_migration_helper_call",
                expression=_source_for_main_loop_node(self.source, node),
            )
        self.generic_visit(node)

    def _is_event_list_backed_owner(self, node: ast.Call) -> bool:
        keyword_values = {keyword.arg: keyword.value for keyword in node.keywords}
        return self._lambda_reads_schedule_data_event_list(
            keyword_values.get("get_events")
        ) and self._lambda_sets_schedule_data_event_list(keyword_values.get("set_events"))

    @staticmethod
    def _lambda_reads_schedule_data_event_list(node: ast.AST | None) -> bool:
        return isinstance(node, ast.Lambda) and _dotted_name(node.body) == (
            "schedule_data.event_list"
        )

    @staticmethod
    def _lambda_sets_schedule_data_event_list(node: ast.AST | None) -> bool:
        if not isinstance(node, ast.Lambda):
            return False
        body = node.body
        return (
            isinstance(body, ast.Call)
            and _call_name(body.func) == "setattr"
            and len(body.args) >= 2
            and _dotted_name(body.args[0]) == "schedule_data"
            and _string_literal_value(body.args[1]) == "event_list"
        )

    def _add_surface(self, *, line: int, kind: str, expression: str) -> None:
        self.surfaces.append(
            MigrationSurface(
                path=self.path.relative_to(PROJECT_ROOT).as_posix(),
                line=line,
                function=_scope_name(self._class_stack, self._function_stack),
                kind=kind,
                matched_expression=expression,
            )
        )


def _collect_planned_queue_migration_surfaces() -> list[MigrationSurface]:
    surfaces: list[MigrationSurface] = []
    for path in _production_python_files():
        source = path.read_text(encoding="utf-8")
        visitor = PlannedQueueMigrationSurfaceVisitor(path, source)
        visitor.visit(ast.parse(source, filename=str(path)))
        surfaces.extend(visitor.surfaces)
    return surfaces


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


def _string_literal_value(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _source_for_main_loop_node(source: str, node: ast.AST) -> str:
    segment = ast.get_source_segment(source, node)
    if segment is None:
        return f"<{type(node).__name__}>"
    return " ".join(segment.strip().split())


def _source_line(source: str, line: int) -> str:
    return " ".join(source.splitlines()[line - 1].strip().split())


def _schedule_data_event_list_classification_for(kind: str) -> str:
    return {
        "schedule_data_event_list_constructor_field": (
            "approved ScheduleData.event_list constructor compatibility field"
        ),
        "schedule_data_event_list_owner_read": (
            "approved ScheduleData.event_list owner read for current queue rebinding"
        ),
        "schedule_data_event_list_owner_rebind": (
            "approved ScheduleData.event_list owner rebind through compatibility setter"
        ),
        "schedule_data_event_list_property_getter": (
            "approved ScheduleData.event_list compatibility property getter"
        ),
        "schedule_data_event_list_property_setter": (
            "approved ScheduleData.event_list compatibility property setter"
        ),
        "schedule_data_event_list_property_install": (
            "approved ScheduleData.event_list compatibility property installation"
        ),
    }[kind]


def _schedule_data_event_list_next_action_for(kind: str) -> str:
    return {
        "schedule_data_event_list_constructor_field": (
            "delete when ScheduleData no longer accepts event_list= seeding"
        ),
        "schedule_data_event_list_owner_read": (
            "replace with non-raw owner storage before deleting the compatibility property"
        ),
        "schedule_data_event_list_owner_rebind": (
            "replace with non-raw owner storage before deleting assignment rebinding"
        ),
        "schedule_data_event_list_property_getter": (
            "delete with the ScheduleData.event_list compatibility property"
        ),
        "schedule_data_event_list_property_setter": (
            "delete with the ScheduleData.event_list compatibility property"
        ),
        "schedule_data_event_list_property_install": (
            "delete with the ScheduleData.event_list compatibility property"
        ),
    }[kind]


class ScheduleDataEventListCompatibilityVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source: str) -> None:
        self.path = path
        self.source = source
        self.findings: list[Finding] = []
        self._class_stack: list[str] = []
        self._function_stack: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self._is_schedule_data_path() and not self._class_stack:
            if node.name == "_get_schedule_data_event_list":
                self._add_finding(
                    line=node.lineno,
                    kind="schedule_data_event_list_property_getter",
                    expression=_source_line(self.source, node.lineno),
                )
            elif node.name == "_set_schedule_data_event_list":
                self._add_finding(
                    line=node.lineno,
                    kind="schedule_data_event_list_property_setter",
                    expression=_source_line(self.source, node.lineno),
                )
        self._function_stack.append(node.name)
        self.generic_visit(node)
        self._function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function_stack.append(node.name)
        self.generic_visit(node)
        self._function_stack.pop()

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if (
            self._is_schedule_data_path()
            and self._class_stack[-1:] == ["ScheduleData"]
            and not self._function_stack
            and isinstance(node.target, ast.Name)
            and node.target.id == "event_list"
        ):
            self._add_finding(
                line=node.lineno,
                kind="schedule_data_event_list_constructor_field",
                expression=_source_line(self.source, node.lineno),
            )
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if (
            self._is_schedule_data_path()
            and self._class_stack[-1:] == ["ScheduleData"]
            and self._function_stack[-1:] == ["_replace_planned_events"]
        ):
            for target in node.targets:
                if _dotted_name(target) == "self.event_list":
                    self._add_finding(
                        line=node.lineno,
                        kind="schedule_data_event_list_owner_rebind",
                        expression=_source_line(self.source, node.lineno),
                    )
        self.generic_visit(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        if (
            self._is_schedule_data_path()
            and self._class_stack[-1:] == ["ScheduleData"]
            and self._function_stack[-1:] == ["__post_init__"]
            and _dotted_name(node.body) == "self.event_list"
        ):
            self._add_finding(
                line=node.lineno,
                kind="schedule_data_event_list_owner_read",
                expression=_source_for_main_loop_node(self.source, node),
            )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if (
            self._is_schedule_data_path()
            and _call_name(node.func) == "property"
            and len(node.args) >= 2
            and _dotted_name(node.args[0]) == "_get_schedule_data_event_list"
            and _dotted_name(node.args[1]) == "_set_schedule_data_event_list"
        ):
            self._add_finding(
                line=node.lineno,
                kind="schedule_data_event_list_property_install",
                expression=_source_for_main_loop_node(self.source, node),
            )
        self.generic_visit(node)

    def _is_schedule_data_path(self) -> bool:
        return self.path == SIMULATOR_ROOT / "dataclasses.py"

    def _add_finding(self, *, line: int, kind: str, expression: str) -> None:
        self.findings.append(
            Finding(
                path=self.path.relative_to(PROJECT_ROOT).as_posix(),
                line=line,
                kind=kind,
                matched_expression=expression,
                classification_suggestion=_schedule_data_event_list_classification_for(kind),
                next_action=_schedule_data_event_list_next_action_for(kind),
            )
        )


def _collect_schedule_data_event_list_compatibility_findings_from_source(
    path: Path,
    source: str,
) -> list[Finding]:
    visitor = ScheduleDataEventListCompatibilityVisitor(path, source)
    visitor.visit(ast.parse(source, filename=str(path)))
    return visitor.findings


def _collect_schedule_data_event_list_compatibility_findings() -> list[Finding]:
    path = SIMULATOR_ROOT / "dataclasses.py"
    return _collect_schedule_data_event_list_compatibility_findings_from_source(
        path,
        path.read_text(encoding="utf-8"),
    )


def _event_list_deletion_readiness_counts() -> dict[str, object]:
    compatibility_findings = _collect_schedule_data_event_list_compatibility_findings()
    event_findings = _collect_findings()
    raw_lifecycle_mutation_kinds = (
        SCHEDULED_EVENT_RAW_QUEUE_LIFECYCLE_KINDS
        | (RAW_PLANNED_QUEUE_LIFECYCLE_KINDS - {"raw_planned_queue_handoff"})
    )
    raw_lifecycle_mutations = [
        finding
        for finding in event_findings
        if finding.kind in raw_lifecycle_mutation_kinds
    ]
    raw_producer_handoffs = [
        finding for finding in event_findings if finding.kind == "raw_planned_queue_handoff"
    ]

    return {
        "approved_schedule_data_event_list_compatibility": len(
            compatibility_findings
        ),
        "approved_schedule_data_event_list_compatibility_by_kind": dict(
            Counter(finding.kind for finding in compatibility_findings)
        ),
        "raw_planned_queue_lifecycle_mutation": len(raw_lifecycle_mutations),
        "raw_planned_queue_producer_handoff": len(raw_producer_handoffs),
    }


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


def _collect_legacy_event_list_adapter_dependency_findings_from_source(
    path: Path, source: str
) -> list[str]:
    tree = ast.parse(source)
    relative_path = path.relative_to(PROJECT_ROOT).as_posix()
    findings: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == LEGACY_EVENT_LIST_ADAPTER_NAME:
                    findings.append(
                        f"{relative_path}:{node.lineno}: imports "
                        f"{LEGACY_EVENT_LIST_ADAPTER_NAME}"
                    )
        elif isinstance(node, ast.Call):
            dotted = _dotted_name(node.func)
            if dotted is None:
                continue
            if dotted == LEGACY_EVENT_LIST_ADAPTER_NAME or dotted.endswith(
                f".{LEGACY_EVENT_LIST_ADAPTER_NAME}"
            ):
                expression = _source_for_main_loop_node(source, node)
                findings.append(
                    f"{relative_path}:{node.lineno}: constructs "
                    f"{LEGACY_EVENT_LIST_ADAPTER_NAME}: {expression}"
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
    expected = {
        key
        for key in CURRENT_ROOT_ALLOWED_EVENT_QUEUE_MUTATIONS
        if key[2] in RAW_EVENT_APPEND_KINDS
    }

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
        finding
        for finding in _collect_findings()
        if finding.kind in CURRENT_ROOT_EVENT_QUEUE_GUARDRAIL_KINDS
    ]
    actual = {_raw_append_key(finding) for finding in findings}
    expected = set(CURRENT_ROOT_ALLOWED_EVENT_QUEUE_MUTATIONS)

    assert actual == expected, (
        "Current root still contains raw planned-queue producers outside queue-owner/local "
        "event-group boundaries, or the allowlist has stale entries:\n"
        + "\n".join(f"- {finding.message()}" for finding in findings)
    )
    assert not (
        {finding.kind for finding in findings}
        & (
            POST_MIGRATION_BLOCKED_RAW_EVENT_APPEND_KINDS
            | SCHEDULED_EVENT_RAW_QUEUE_LIFECYCLE_KINDS
            | RAW_PLANNED_QUEUE_LIFECYCLE_KINDS
        )
    ), (
        "Current root still contains raw planned-queue producers outside queue-owner/local "
        "event-group boundaries:\n"
        + "\n".join(f"- {finding.message()}" for finding in findings)
    )

    expected_owner_story_by_kind = {
        "planned_queue_owner_internal_mutation": "US-001",
        "planned_queue_owner_internal_replacement": "US-001",
        "local_event_group_append": "US-005",
    }
    allowed_kinds = OWNER_ONLY_RAW_EVENT_APPEND_KINDS | PLANNED_QUEUE_OWNER_INTERNAL_KINDS
    for key, owner_story_id in CURRENT_ROOT_ALLOWED_EVENT_QUEUE_MUTATIONS.items():
        _path, _line, kind, _matched_expression = key
        assert kind in allowed_kinds
        assert owner_story_id == expected_owner_story_by_kind[kind]


def test_planned_queue_compatibility_view_reads_are_migration_only() -> None:
    findings = [
        finding
        for finding in _collect_findings()
        if finding.kind in PLANNED_QUEUE_COMPATIBILITY_VIEW_KINDS
    ]
    actual = {_raw_append_key(finding) for finding in findings}
    expected = set(CURRENT_ROOT_ALLOWED_COMPATIBILITY_VIEW_READS)

    assert actual == expected, (
        "PlannedEventQueue.compatibility_view production reads must stay inside "
        "approved migration hooks:\n"
        + "\n".join(f"- {finding.message()}" for finding in findings)
    )

    prd_story_ids = _active_prd_story_ids()
    missing_story_ids = sorted(
        {
            owner_story_id
            for owner_story_id in CURRENT_ROOT_ALLOWED_COMPATIBILITY_VIEW_READS.values()
            if owner_story_id not in prd_story_ids
        }
    )
    assert not missing_story_ids, (
        "Current-root approved compatibility_view reads must name follow-up stories "
        f"in scripts/ralph/prd.json; missing: {missing_story_ids}"
    )


def test_production_public_planned_queue_compatibility_surfaces_are_zero() -> None:
    compatibility_view_findings = [
        finding
        for finding in _collect_findings()
        if finding.kind in PLANNED_QUEUE_COMPATIBILITY_VIEW_KINDS
    ]
    schedule_data_event_list_findings = (
        _collect_schedule_data_event_list_compatibility_findings()
    )

    assert CURRENT_ROOT_ALLOWED_COMPATIBILITY_VIEW_READS == {}
    assert CURRENT_ROOT_ALLOWED_SCHEDULE_DATA_EVENT_LIST_COMPATIBILITY == {}
    assert compatibility_view_findings == []
    assert schedule_data_event_list_findings == []


def test_schedule_data_event_list_compatibility_allowance_is_exact_and_owned() -> None:
    findings = _collect_schedule_data_event_list_compatibility_findings()
    actual = {_raw_append_key(finding) for finding in findings}
    expected = set(CURRENT_ROOT_ALLOWED_SCHEDULE_DATA_EVENT_LIST_COMPATIBILITY)

    assert actual == expected, (
        "ScheduleData.event_list compatibility allowance drifted:\n"
        + "\n".join(f"- {finding.message()}" for finding in findings)
    )

    prd_story_ids = _active_prd_story_ids()
    missing_story_ids = sorted(
        {
            allowance.story
            for allowance in CURRENT_ROOT_ALLOWED_SCHEDULE_DATA_EVENT_LIST_COMPATIBILITY.values()
            if allowance.story not in prd_story_ids
        }
    )
    assert not missing_story_ids, (
        "ScheduleData.event_list compatibility allowances must name active PRD "
        f"stories; missing: {missing_story_ids}"
    )
    assert all(
        allowance.owner and allowance.rationale
        for allowance in CURRENT_ROOT_ALLOWED_SCHEDULE_DATA_EVENT_LIST_COMPATIBILITY.values()
    )
    assert {
        allowance.story
        for allowance in CURRENT_ROOT_ALLOWED_SCHEDULE_DATA_EVENT_LIST_COMPATIBILITY.values()
    } == set()


def test_event_list_migration_owner_construction_is_exactly_helper_owned() -> None:
    surfaces = [
        surface
        for surface in _collect_planned_queue_migration_surfaces()
        if surface.kind
        in {
            "event_list_migration_owner_construction",
            "event_list_migration_owner_helper_call",
        }
    ]
    owner_constructions = [
        surface
        for surface in surfaces
        if surface.kind == "event_list_migration_owner_construction"
    ]
    helper_calls = [
        surface
        for surface in surfaces
        if surface.kind == "event_list_migration_owner_helper_call"
    ]

    assert [
        (surface.path, surface.function, surface.kind)
        for surface in owner_constructions
    ] == [
        (
            "zsim/sim_progress/data_struct/planned_queue.py",
            "ensure_event_list_migration_planned_event_queue",
            "event_list_migration_owner_construction",
        )
    ]
    assert helper_calls == []


def test_private_raw_migration_helper_usage_is_exactly_owner_and_runtime_bridge() -> None:
    surfaces = [
        surface
        for surface in _collect_planned_queue_migration_surfaces()
        if surface.kind
        in {
            "private_raw_migration_helper_definition",
            "private_raw_migration_helper_call",
        }
    ]

    assert Counter(
        (surface.path, surface.function, surface.kind) for surface in surfaces
    ) == Counter(
        {
            (
                "zsim/sim_progress/data_struct/planned_queue.py",
                "PlannedEventQueue._raw_events_for_migration",
                "private_raw_migration_helper_definition",
            ): 1,
            (
                "zsim/sim_progress/ScheduledEvent/runtime_command.py",
                "_planned_queue_raw_events_for_migration",
                "private_raw_migration_helper_call",
            ): 1,
        }
    )


def test_event_list_deletion_readiness_counts_categories_separately() -> None:
    counts = _event_list_deletion_readiness_counts()

    assert counts["approved_schedule_data_event_list_compatibility"] == len(
        CURRENT_ROOT_ALLOWED_SCHEDULE_DATA_EVENT_LIST_COMPATIBILITY
    )
    assert counts["approved_schedule_data_event_list_compatibility_by_kind"] == dict(
        Counter(
            key[2]
            for key in CURRENT_ROOT_ALLOWED_SCHEDULE_DATA_EVENT_LIST_COMPATIBILITY
        )
    )
    assert counts["raw_planned_queue_lifecycle_mutation"] == 0
    assert counts["raw_planned_queue_producer_handoff"] == 0


def test_raw_planned_queue_lifecycle_has_no_current_findings_outside_owner_surfaces() -> None:
    findings = [
        finding
        for finding in _collect_findings()
        if finding.kind in SCHEDULED_EVENT_RAW_QUEUE_LIFECYCLE_KINDS
        or finding.kind in RAW_PLANNED_QUEUE_LIFECYCLE_KINDS
    ]

    _assert_no_disallowed(findings)


def test_main_loop_uses_dispatch_port_and_has_no_raw_planned_queue_handoff() -> None:
    source = SIMULATOR_CLASS_PATH.read_text(encoding="utf-8")

    findings = _collect_main_loop_raw_planned_queue_findings_from_source(source)

    assert findings == []
    assert _main_loop_damage_judge_uses_schedule_dispatch_port(source)


def test_default_paths_do_not_depend_on_legacy_event_list_adapter() -> None:
    findings: list[str] = []
    for path in DEFAULT_PATH_LEGACY_ADAPTER_PROHIBITED_FILES:
        findings.extend(
            _collect_legacy_event_list_adapter_dependency_findings_from_source(
                path, path.read_text(encoding="utf-8")
            )
        )

    assert findings == []


def test_legacy_event_list_adapter_dependency_guardrail_blocks_default_path_regressions() -> None:
    samples = [
        (
            SIMULATOR_CLASS_PATH,
            (
                "from zsim.sim_progress.data_struct.schedule_dispatch import "
                "LegacyEventListScheduleDispatchAdapter\n"
                "class Simulator:\n"
                "    def main_loop(self):\n"
                "        return LegacyEventListScheduleDispatchAdapter(\n"
                "            self.schedule_data.event_list\n"
                "        )\n"
            ),
        ),
        (
            SCHEDULED_EVENT_PATH,
            (
                "class ScheduledEvent:\n"
                "    def process_event(self):\n"
                "        return schedule_dispatch.LegacyEventListScheduleDispatchAdapter(\n"
                "            self.data.event_list\n"
                "        )\n"
            ),
        ),
        (
            LOAD_DAMAGE_EVENT_PATH,
            (
                "from zsim.sim_progress.data_struct.schedule_dispatch import "
                "LegacyEventListScheduleDispatchAdapter\n"
                "def _as_schedule_publisher(event_list):\n"
                "    return LegacyEventListScheduleDispatchAdapter(event_list)\n"
            ),
        ),
        (
            RUNTIME_COMMAND_PATH,
            (
                "def schedule_followup(schedule_data):\n"
                "    return LegacyEventListScheduleDispatchAdapter(\n"
                "        schedule_data.event_list\n"
                "    )\n"
            ),
        ),
    ]

    for path, source in samples:
        findings = _collect_legacy_event_list_adapter_dependency_findings_from_source(
            path, source
        )

        assert any(LEGACY_EVENT_LIST_ADAPTER_NAME in finding for finding in findings)


def test_runtime_command_followup_scheduling_uses_owner_view_not_raw_adapter() -> None:
    source = RUNTIME_COMMAND_PATH.read_text(encoding="utf-8")

    assert LEGACY_EVENT_LIST_ADAPTER_NAME not in source
    assert "_planned_queue_raw_events_for_migration" in source
    assert "ensure_planned_event_queue" not in source
    assert "_EVENT_LIST_MIGRATION_OWNER_ATTR" in source
    assert "_planned_queue_owner_for_migration" in source
    assert ")._raw_events_for_migration()" in source
    assert ".compatibility_view" not in source
    assert "getattr(schedule_data, \"event_list\"" not in source
    assert "getattr(schedule_data, 'event_list'" not in source


def test_retained_scheduled_event_processing_uses_owner_queue_not_raw_adapter() -> None:
    source = SCHEDULED_EVENT_PATH.read_text(encoding="utf-8")

    assert LEGACY_EVENT_LIST_ADAPTER_NAME not in source
    assert "return ensure_planned_event_queue(self.data)" in source
    assert "self.data.event_list.append" not in source
    assert "self.data.event_list.remove" not in source


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
        (
            PRODUCTION_ROOT / "Enemy" / "_synthetic_raw_queue_replace.py",
            "def replace(schedule_data, events):\n    schedule_data.event_list = list(events)\n",
            "raw_schedule_data_event_list_lifecycle_assignment",
        ),
        (
            PRODUCTION_ROOT / "Load" / "_synthetic_raw_queue_reorder.py",
            "def reorder(event_list, event):\n    event_list.insert(0, event)\n",
            "raw_event_list_lifecycle_mutation",
        ),
        (
            PRODUCTION_ROOT / "Update" / "_synthetic_raw_queue_clear.py",
            "def clear(data):\n    data.event_list.clear()\n",
            "raw_data_event_list_lifecycle_mutation",
        ),
        (
            PRODUCTION_ROOT / "Enemy" / "_synthetic_raw_queue_pop.py",
            "def take(schedule_data):\n    return schedule_data.event_list.pop()\n",
            "raw_schedule_data_event_list_lifecycle_mutation",
        ),
        (
            PRODUCTION_ROOT / "Load" / "_synthetic_raw_handoff.py",
            (
                "def publish(schedule_data, missions, enemy, chars):\n"
                "    DamageEventJudge(0, missions, enemy, schedule_data.event_list, chars)\n"
            ),
            "raw_planned_queue_handoff",
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


def test_planned_queue_compatibility_view_guardrail_blocks_production_regressions() -> None:
    samples = [
        (
            PRODUCTION_ROOT / "Load" / "_synthetic_compatibility_view_publish.py",
            "def publish(queue, event):\n    queue.compatibility_view.append(event)\n",
            "queue.compatibility_view.append(event)",
        ),
        (
            PRODUCTION_ROOT / "ScheduledEvent" / "_synthetic_compatibility_view_read.py",
            "def read(queue):\n    return queue.compatibility_view\n",
            "queue.compatibility_view",
        ),
    ]

    allowed_keys = set(CURRENT_ROOT_ALLOWED_COMPATIBILITY_VIEW_READS)
    for path, source, expected_expression in samples:
        visitor = LegacyEventListDiscoveryVisitor(path, source)
        visitor.visit(ast.parse(source))

        assert len(visitor.findings) == 1
        finding = visitor.findings[0]
        assert finding.kind == "planned_queue_compatibility_view_read"
        assert finding.matched_expression == expected_expression
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


def test_raw_planned_queue_fallback_guardrail_blocks_local_compatibility_helpers() -> None:
    samples = [
        (
            PRODUCTION_ROOT / "data_struct" / "schedule_dispatch.py",
            (
                "class _ScheduleDataQueueOwner:\n"
                "    def _planned_event_queue(self):\n"
                "        return PlannedEventQueue(\n"
                "            get_events=lambda: schedule_data.event_list,\n"
                "            set_events=lambda events: setattr(schedule_data, 'event_list', events),\n"
                "        )\n"
            ),
            [
                "raw_planned_queue_fallback_read",
                "raw_schedule_data_event_list_lifecycle_assignment",
            ],
        ),
        (
            PRODUCTION_ROOT / "ScheduledEvent" / "__init__.py",
            (
                "class ScheduledEvent:\n"
                "    def _replace_planned_events(self, events):\n"
                "        self.data.event_list = events\n"
            ),
            ["raw_data_event_list_lifecycle_assignment"],
        ),
        (
            PRODUCTION_ROOT / "ScheduledEvent" / "runtime_command.py",
            (
                "def _planned_queue_compatibility_view(schedule_data):\n"
                "    return getattr(schedule_data, 'event_list', [])\n"
            ),
            ["raw_planned_queue_fallback_read"],
        ),
    ]

    allowed_keys = set(CURRENT_ROOT_ALLOWED_EVENT_QUEUE_MUTATIONS)
    for path, source, expected_kinds in samples:
        visitor = LegacyEventListDiscoveryVisitor(path, source)
        visitor.visit(ast.parse(source))

        assert [finding.kind for finding in visitor.findings] == expected_kinds
        assert not {
            _raw_append_key(finding) for finding in visitor.findings
        } & allowed_keys


def test_planned_queue_owner_helper_is_the_only_raw_fallback_owner() -> None:
    allowed_source = (
        "def ensure_event_list_migration_planned_event_queue(schedule_data):\n"
        "    return PlannedEventQueue(\n"
        "        get_events=lambda: schedule_data.event_list,\n"
        "        set_events=lambda events: setattr(schedule_data, 'event_list', events),\n"
        "    )\n"
    )
    path = PRODUCTION_ROOT / "data_struct" / "planned_queue.py"
    allowed_visitor = LegacyEventListDiscoveryVisitor(path, allowed_source)

    allowed_visitor.visit(ast.parse(allowed_source))

    assert allowed_visitor.findings == []

    disallowed_source = (
        "def ensure_planned_event_queue(schedule_data):\n"
        "    return PlannedEventQueue(\n"
        "        get_events=lambda: schedule_data.event_list,\n"
        "        set_events=lambda events: setattr(schedule_data, 'event_list', events),\n"
        "    )\n"
    )
    disallowed_visitor = LegacyEventListDiscoveryVisitor(path, disallowed_source)

    disallowed_visitor.visit(ast.parse(disallowed_source))

    assert [finding.kind for finding in disallowed_visitor.findings] == [
        "raw_planned_queue_fallback_read",
        "raw_schedule_data_event_list_lifecycle_assignment",
    ]


def test_generic_planned_queue_resolution_does_not_install_event_list_owner() -> None:
    path = PRODUCTION_ROOT / "data_struct" / "planned_queue.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    ensure_function = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.name == "ensure_planned_event_queue"
    )
    ensure_source = ast.get_source_segment(source, ensure_function)

    assert ensure_source is not None
    assert "ensure_event_list_migration_planned_event_queue" not in ensure_source
    assert "_EVENT_LIST_MIGRATION_OWNER_ATTR" in ensure_source
    assert "raise AttributeError" in ensure_source


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
