from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tests.simulator import test_buff_raw_container_guardrail as raw_guardrail

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SIM_PROGRESS_ROOT = PROJECT_ROOT / "zsim" / "sim_progress"
BUFF_ADD_STRATEGY_FILE = SIM_PROGRESS_ROOT / "Buff" / "BuffAddStrategy.py"
BUFF_RUNTIME_FILE = SIM_PROGRESS_ROOT / "ScheduledEvent" / "buff_runtime.py"

P2F_BUFF_ADD_STRATEGY_FILES = (
    BUFF_ADD_STRATEGY_FILE,
    BUFF_RUNTIME_FILE,
)

RAW_PENDING_FIELDS = {
    "LOADING_BUFF_DICT",
    "_loading_buff_dict",
    "loading_buff",
    "loading_buff_dict",
}
RAW_ACTIVE_FIELDS = {
    "DYNAMIC_BUFF_DICT",
    "_dynamic_buff",
    "_dynamic_buff_dict",
    "dynamic_buff",
    "dynamic_buff_dict",
}
RAW_ENEMY_MIRROR_FIELDS = {
    "_enemy_debuff_mirror",
    "dynamic_debuff_list",
    "enemy_debuff_mirror",
}
RAW_WRITE_METHODS = {
    "append",
    "clear",
    "extend",
    "insert",
    "pop",
    "remove",
    "setdefault",
    "update",
}
READ_PORT_WRITE_PREFIXES = (
    "activate",
    "add",
    "append",
    "clear",
    "drain",
    "end",
    "enqueue",
    "register",
    "remove",
    "replace",
    "set",
    "settle",
    "sync",
    "update",
    "write",
)


@dataclass(frozen=True)
class P2FBuffAddStrategyFinding:
    path: str
    line: int
    field_or_api: str
    context: str
    matched_expression: str
    classification_suggestion: str
    suggested_replacement_boundary: str

    def message(self) -> str:
        return (
            f"{self.path}:{self.line}: field/API: {self.field_or_api}; "
            f"context: {self.context}; matched expression: {self.matched_expression}; "
            f"classification suggestion: {self.classification_suggestion}; "
            f"suggested replacement boundary: {self.suggested_replacement_boundary}"
        )


class MigratedP2FBuffAddStrategyVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source: str) -> None:
        self.path = path
        self.source = source
        self.findings: list[P2FBuffAddStrategyFinding] = []
        self._parents: list[ast.AST] = []
        self._class_stack: list[str] = []
        self._function_stack: list[str] = []

    def visit(self, node: ast.AST) -> Any:
        self._parents.append(node)
        try:
            return super().visit(node)
        finally:
            self._parents.pop()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name.endswith("FindMain") or alias.name.endswith("find_event_list"):
                self._add_finding(
                    line=getattr(alias, "lineno", node.lineno),
                    kind="deleted_discovery_surface",
                    expression=self._source_for(node),
                    field_or_api="find_event_list",
                )
            if alias.name.endswith("schedule_dispatch"):
                self._add_finding(
                    line=getattr(alias, "lineno", node.lineno),
                    kind="scheduled_queue_conversion",
                    expression=self._source_for(node),
                    field_or_api=alias.name,
                )
            if alias.name.endswith("runtime_command"):
                self._add_finding(
                    line=getattr(alias, "lineno", node.lineno),
                    kind="runtime_command_port_creation",
                    expression=self._source_for(node),
                    field_or_api=alias.name,
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = f"{'.' * node.level}{node.module or ''}"
        for alias in node.names:
            if alias.name == "find_event_list":
                self._add_finding(
                    line=getattr(alias, "lineno", node.lineno),
                    kind="deleted_discovery_surface",
                    expression=f"from {module} import {alias.name}",
                    field_or_api=alias.name,
                )
            if alias.name in {"ScheduleDispatchPort", "create_schedule_dispatch_port"}:
                self._add_finding(
                    line=getattr(alias, "lineno", node.lineno),
                    kind="scheduled_queue_conversion",
                    expression=f"from {module} import {alias.name}",
                    field_or_api=alias.name,
                )
            if alias.name in {"RuntimeCommandPort", "create_runtime_command_port"}:
                self._add_finding(
                    line=getattr(alias, "lineno", node.lineno),
                    kind="runtime_command_port_creation",
                    expression=f"from {module} import {alias.name}",
                    field_or_api=alias.name,
                )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            self._check_read_port_write_api(node)
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            self._check_read_port_write_api(node)
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self._check_raw_write_target(target)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._check_raw_write_target(node.target)
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self._check_raw_write_target(node.target)
        self.generic_visit(node)

    def visit_Delete(self, node: ast.Delete) -> None:
        for target in node.targets:
            self._check_raw_write_target(target)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        call_name = self._call_name(node.func)
        if self._is_find_event_list_call(node.func):
            self._add_finding(
                line=node.lineno,
                kind="deleted_discovery_surface",
                expression=self._source_for(node),
                field_or_api="find_event_list",
            )
        if self._is_event_list_request(node):
            self._add_finding(
                line=node.lineno,
                kind="deleted_discovery_surface",
                expression=self._source_for(node),
                field_or_api="event_list",
            )
        if self._is_raw_event_list_append_call(node):
            self._add_finding(
                line=node.lineno,
                kind="scheduled_queue_conversion",
                expression=self._source_for(node),
                field_or_api="event_list",
            )
        if call_name in {
            "ScheduleDispatchPort",
            "create_schedule_dispatch_port",
            "publish_scheduled",
        }:
            self._add_finding(
                line=node.lineno,
                kind="scheduled_queue_conversion",
                expression=self._source_for(node),
                field_or_api=call_name,
            )
        if call_name in {"RuntimeCommandPort", "create_runtime_command_port"}:
            self._add_finding(
                line=node.lineno,
                kind="runtime_command_port_creation",
                expression=self._source_for(node),
                field_or_api=call_name,
            )
        if call_name == "broadcast_event" or self._dotted_name(node.func).endswith(
            "listener_manager.broadcast_event"
        ):
            self._add_finding(
                line=node.lineno,
                kind="listener_broadcast_conversion",
                expression=self._source_for(node),
                field_or_api="broadcast_event",
            )
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in RAW_WRITE_METHODS
            and self._checks_raw_forced_write_boundary()
        ):
            raw_field = self._raw_field_for(node.func.value)
            if raw_field is not None:
                self._add_raw_write_finding(
                    line=node.lineno,
                    field=raw_field,
                    expression=self._source_for(node),
                )
        self.generic_visit(node)

    def _check_read_port_write_api(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        if not self._class_stack or self._class_stack[-1] != "BuffRuntimeReadPort":
            return
        if node.name.startswith(READ_PORT_WRITE_PREFIXES):
            self._add_finding(
                line=node.lineno,
                kind="read_port_write_api",
                expression=f"def {node.name}",
                field_or_api=node.name,
            )

    def _check_raw_write_target(self, target: ast.AST) -> None:
        if not self._checks_raw_forced_write_boundary():
            return
        raw_field = self._raw_field_for(target)
        if raw_field is None:
            return
        self._add_raw_write_finding(
            line=getattr(target, "lineno", 0),
            field=raw_field,
            expression=self._source_for(target),
        )

    def _add_raw_write_finding(self, *, line: int, field: str, expression: str) -> None:
        self._add_finding(
            line=line,
            kind=self._raw_write_kind_for(field),
            expression=expression,
            field_or_api=field,
        )

    def _checks_raw_forced_write_boundary(self) -> bool:
        return self.path == BUFF_ADD_STRATEGY_FILE

    @staticmethod
    def _raw_write_kind_for(field: str) -> str:
        if field in RAW_PENDING_FIELDS:
            return "raw_pending_queue_write"
        if field in RAW_ENEMY_MIRROR_FIELDS:
            return "raw_enemy_mirror_write"
        return "raw_active_store_write"

    @staticmethod
    def _raw_field_for(node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            if node.id in RAW_PENDING_FIELDS | RAW_ACTIVE_FIELDS | RAW_ENEMY_MIRROR_FIELDS:
                return node.id
            return None
        if isinstance(node, ast.Attribute):
            if node.attr in RAW_PENDING_FIELDS | RAW_ACTIVE_FIELDS | RAW_ENEMY_MIRROR_FIELDS:
                return node.attr
            return MigratedP2FBuffAddStrategyVisitor._raw_field_for(node.value)
        if isinstance(node, ast.Subscript):
            return MigratedP2FBuffAddStrategyVisitor._raw_field_for(node.value)
        return None

    @staticmethod
    def _is_find_event_list_call(func: ast.expr) -> bool:
        if isinstance(func, ast.Name):
            return func.id == "find_event_list"
        if isinstance(func, ast.Attribute):
            return func.attr == "find_event_list"
        return False

    def _is_event_list_request(self, node: ast.Call) -> bool:
        if self._call_name(node.func) not in {"check_preparation", "get_prepared"}:
            return False
        for keyword in node.keywords:
            if keyword.arg == "event_list" and self._may_request_event_list(
                keyword.value
            ):
                return True
            if keyword.arg is None:
                for value in self._unpacked_event_list_values(keyword.value):
                    if self._may_request_event_list(value):
                        return True
        return False

    @staticmethod
    def _may_request_event_list(value: ast.expr) -> bool:
        if isinstance(value, ast.Constant):
            return bool(value.value)
        return True

    @staticmethod
    def _unpacked_event_list_values(value: ast.expr) -> list[ast.expr]:
        if not isinstance(value, ast.Dict):
            return []
        matches: list[ast.expr] = []
        for key, item in zip(value.keys, value.values, strict=True):
            if isinstance(key, ast.Constant) and key.value == "event_list":
                matches.append(item)
        return matches

    def _is_raw_event_list_append_call(self, node: ast.Call) -> bool:
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "append":
            return False
        target = node.func.value
        if isinstance(target, ast.Name) and target.id == "event_list":
            return True
        if isinstance(target, ast.Attribute) and target.attr == "event_list":
            return True
        if isinstance(target, ast.Subscript):
            return self._dotted_name(target.value).endswith("event_list")
        return False

    @staticmethod
    def _call_name(func: ast.expr) -> str | None:
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return func.attr
        return None

    def _add_finding(
        self, *, line: int, kind: str, expression: str, field_or_api: str
    ) -> None:
        self.findings.append(
            P2FBuffAddStrategyFinding(
                path=self.path.relative_to(PROJECT_ROOT).as_posix(),
                line=line,
                field_or_api=field_or_api,
                context=self._context(),
                matched_expression=self._normalize(expression),
                classification_suggestion=self._classification_for(kind),
                suggested_replacement_boundary=self._replacement_boundary_for(kind),
            )
        )

    def _context(self) -> str:
        parts = [*self._class_stack, *self._function_stack]
        if not parts:
            return "<module>"
        return ".".join(parts)

    def _source_for(self, node: ast.AST) -> str:
        segment = ast.get_source_segment(self.source, node)
        if segment is None:
            return f"<{type(node).__name__}>"
        return self._normalize(segment)

    @staticmethod
    def _normalize(expression: str) -> str:
        return " ".join(expression.strip().split())

    @staticmethod
    def _classification_for(kind: str) -> str:
        return {
            "deleted_discovery_surface": "deleted event-list discovery surface",
            "listener_broadcast_conversion": "forced Buff write converted to listener broadcast",
            "raw_active_store_write": "raw active-store write",
            "raw_enemy_mirror_write": "raw enemy mirror write",
            "raw_pending_queue_write": "raw pending queue write",
            "read_port_write_api": "write API added to BuffRuntimeReadPort",
            "runtime_command_port_creation": "new RuntimeCommandPort creation in P2-F boundary",
            "scheduled_queue_conversion": "forced Buff write converted to scheduled queue",
        }[kind]

    @staticmethod
    def _replacement_boundary_for(kind: str) -> str:
        return {
            "deleted_discovery_surface": (
                "keep P2-F forced Buff writes on LegacyBuffRuntimeFacade; planned "
                "events use ScheduleDispatchPort without legacy discovery"
            ),
            "listener_broadcast_conversion": (
                "keep synchronous listener broadcasts outside the BuffAddStrategy "
                "forced-write boundary"
            ),
            "raw_active_store_write": (
                "route active-store writes through LegacyBuffRuntimeFacade."
                "append_active_buff/remove_active_buff"
            ),
            "raw_enemy_mirror_write": (
                "route enemy mirror sync through LegacyBuffRuntimeFacade."
                "sync_enemy_debuff_mirror"
            ),
            "raw_pending_queue_write": (
                "keep BuffAddStrategy off LOADING_BUFF_DICT pending queues; use the "
                "existing facade-backed same-tick write path"
            ),
            "read_port_write_api": (
                "keep BuffRuntimeReadPort read-only and route writes through "
                "existing facade paths"
            ),
            "runtime_command_port_creation": (
                "use the existing RuntimeCommandPort/LegacyRuntimeCommandAdapter "
                "only at the scheduled-handler command boundary"
            ),
            "scheduled_queue_conversion": (
                "keep forced Buff/Debuff writes on LegacyBuffRuntimeFacade; use "
                "ScheduleDispatchPort only for planned-event payloads"
            ),
        }[kind]

    @staticmethod
    def _dotted_name(node: ast.AST) -> str:
        chain = MigratedP2FBuffAddStrategyVisitor._attribute_chain(node)
        return ".".join(chain)

    @staticmethod
    def _attribute_chain(node: ast.AST) -> list[str]:
        parts: list[str] = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return list(reversed(parts))


def _collect_findings_from_source(
    path: Path, source: str
) -> list[P2FBuffAddStrategyFinding]:
    tree = ast.parse(source, filename=str(path))
    visitor = MigratedP2FBuffAddStrategyVisitor(path, source)
    visitor.visit(tree)
    return visitor.findings


def _collect_migrated_file_findings() -> list[P2FBuffAddStrategyFinding]:
    findings: list[P2FBuffAddStrategyFinding] = []
    for path in P2F_BUFF_ADD_STRATEGY_FILES:
        source = path.read_text(encoding="utf-8")
        findings.extend(_collect_findings_from_source(path, source))
    return findings


def test_migrated_p2f_files_do_not_regress_buff_add_strategy_boundaries() -> None:
    findings = _collect_migrated_file_findings()

    assert not findings, (
        "Migrated P2-F BuffAddStrategy files reintroduced forbidden boundaries:\n"
        + "\n".join(f"- {finding.message()}" for finding in findings)
    )


def test_migrated_p2f_guardrail_scope_is_exact_root_file_set() -> None:
    scanned_files = {
        path.relative_to(PROJECT_ROOT).as_posix()
        for path in P2F_BUFF_ADD_STRATEGY_FILES
    }

    assert scanned_files == {
        "zsim/sim_progress/Buff/BuffAddStrategy.py",
        "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
    }
    assert all(path.is_file() for path in P2F_BUFF_ADD_STRATEGY_FILES)
    assert all(
        ".codex_worktrees" not in path.parts for path in P2F_BUFF_ADD_STRATEGY_FILES
    )
    assert all("__pycache__" not in path.parts for path in P2F_BUFF_ADD_STRATEGY_FILES)
    assert all(
        "archive" not in {part.lower() for part in path.parts}
        for path in P2F_BUFF_ADD_STRATEGY_FILES
    )


def test_migrated_p2f_guardrail_preserves_retained_raw_container_compatibility() -> None:
    findings = [
        finding
        for finding in raw_guardrail._collect_findings()
        if finding.path == "zsim/sim_progress/Buff/BuffAddStrategy.py"
    ]
    allowances = {raw_guardrail._allowance_for(finding) for finding in findings}

    assert {
        "legacy BuffAddStrategy facade construction",
        "legacy BuffAddStrategy beneficiary selection registry read",
        "legacy BuffAddStrategy template clone registry compatibility",
        "legacy BuffAddStrategy inactive diagnostic helper",
    }.issubset(allowances)


def test_migrated_p2f_guardrail_reports_forbidden_boundaries_with_context() -> None:
    source = (
        "from zsim.sim_progress.Buff.JudgeTools.FindMain import find_event_list\n"
        "from zsim.sim_progress.ScheduledEvent.runtime_command import RuntimeCommandPort\n"
        "from zsim.sim_progress.data_struct.schedule_dispatch import create_schedule_dispatch_port\n"
        "class Probe:\n"
        "    def write(self, sim_instance, buff):\n"
        "        sim_instance.load_data.LOADING_BUFF_DICT['enemy'].append(buff)\n"
        "        sim_instance.global_stats.DYNAMIC_BUFF_DICT['enemy'].append(buff)\n"
        "        sim_instance.schedule_data.enemy.dynamic.dynamic_debuff_list.append(buff)\n"
        "        find_event_list(self)\n"
        "        check_preparation(buff_instance=buff, event_list=True)\n"
        "        create_schedule_dispatch_port(sim_instance=sim_instance).publish_scheduled(buff)\n"
        "        sim_instance.listener_manager.broadcast_event(event=buff, signal='x')\n"
        "        return RuntimeCommandPort()\n"
    )

    messages = [
        finding.message()
        for finding in _collect_findings_from_source(BUFF_ADD_STRATEGY_FILE, source)
    ]

    assert any("field/API: LOADING_BUFF_DICT" in message for message in messages)
    assert any("field/API: DYNAMIC_BUFF_DICT" in message for message in messages)
    assert any("field/API: dynamic_debuff_list" in message for message in messages)
    assert any("field/API: find_event_list" in message for message in messages)
    assert any("field/API: event_list" in message for message in messages)
    assert any("field/API: publish_scheduled" in message for message in messages)
    assert any("field/API: broadcast_event" in message for message in messages)
    assert any("field/API: RuntimeCommandPort" in message for message in messages)
    assert any("context: Probe.write" in message for message in messages)
    assert any("classification suggestion: raw pending queue write" in message for message in messages)
    assert any("classification suggestion: raw active-store write" in message for message in messages)
    assert any("classification suggestion: raw enemy mirror write" in message for message in messages)
    assert any("classification suggestion: deleted event-list discovery surface" in message for message in messages)
    assert any("classification suggestion: forced Buff write converted to scheduled queue" in message for message in messages)
    assert any("classification suggestion: forced Buff write converted to listener broadcast" in message for message in messages)
    assert any("classification suggestion: new RuntimeCommandPort creation in P2-F boundary" in message for message in messages)
    assert any("suggested replacement boundary: route active-store writes through LegacyBuffRuntimeFacade" in message for message in messages)


def test_migrated_p2f_guardrail_blocks_read_port_write_api() -> None:
    source = (
        "class BuffRuntimeReadPort:\n"
        "    def get_active_buffs(self):\n"
        "        pass\n"
        "    def set_active_buffs(self, buffs):\n"
        "        pass\n"
        "    async def write_enemy_debuff_mirror(self, buff):\n"
        "        pass\n"
    )

    messages = [
        finding.message()
        for finding in _collect_findings_from_source(BUFF_RUNTIME_FILE, source)
    ]

    assert len(messages) == 2
    assert any("field/API: set_active_buffs" in message for message in messages)
    assert any("field/API: write_enemy_debuff_mirror" in message for message in messages)
    assert all("context: BuffRuntimeReadPort." in message for message in messages)
    assert all(
        "classification suggestion: write API added to BuffRuntimeReadPort" in message
        for message in messages
    )
    assert any(
        "suggested replacement boundary: keep BuffRuntimeReadPort read-only" in message
        for message in messages
    )


def test_migrated_p2f_guardrail_uses_ast_not_text_matching_and_allows_retained_reads() -> None:
    source = (
        "def clean(sim_instance, runtime_facade, buff):\n"
        "    '''LOADING_BUFF_DICT DYNAMIC_BUFF_DICT dynamic_debuff_list find_event_list "
        "publish_scheduled broadcast_event RuntimeCommandPort BuffRuntimeReadPort'''\n"
        "    pending = sim_instance.load_data.LOADING_BUFF_DICT\n"
        "    active = sim_instance.global_stats.DYNAMIC_BUFF_DICT\n"
        "    mirror = sim_instance.schedule_data.enemy.dynamic.dynamic_debuff_list\n"
        "    runtime_facade.append_active_buff('enemy', buff)\n"
        "    runtime_facade.sync_enemy_debuff_mirror(buff)\n"
        "    check_preparation(buff_instance=buff, event_list=False)\n"
        "    return pending, active, mirror\n"
    )

    assert _collect_findings_from_source(BUFF_ADD_STRATEGY_FILE, source) == []
