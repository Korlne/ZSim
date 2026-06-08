from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SIM_PROGRESS_ROOT = PROJECT_ROOT / "zsim" / "sim_progress"
BUFF_XLOGIC_ROOT = SIM_PROGRESS_ROOT / "Buff" / "BuffXLogic"
DOT_ROOT = SIM_PROGRESS_ROOT / "Dot"

P2E_MIGRATED_DOT_RUNTIME_FILES = (
    BUFF_XLOGIC_ROOT / "VivianDotTrigger.py",
    BUFF_XLOGIC_ROOT / "VivianCinema1Debuff.py",
    SIM_PROGRESS_ROOT / "Update" / "UpdateAnomaly.py",
    DOT_ROOT / "runtime_state.py",
    DOT_ROOT / "initialization.py",
    DOT_ROOT / "Dots" / "Shock.py",
)

P2E_DOT_RUNTIME_HELPER_FILES = {
    DOT_ROOT / "runtime_state.py",
    DOT_ROOT / "initialization.py",
}

P2E_SHOCK_DOT_FEATURE_FILE = DOT_ROOT / "Dots" / "Shock.py"


@dataclass(frozen=True)
class P2EDotRuntimeFinding:
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


class MigratedP2EDotRuntimeVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source: str) -> None:
        self.path = path
        self.source = source
        self.findings: list[P2EDotRuntimeFinding] = []
        self._parents: list[ast.AST] = []
        self._class_stack: list[str] = []

    def visit(self, node: ast.AST) -> Any:
        self._parents.append(node)
        try:
            return super().visit(node)
        finally:
            self._parents.pop()

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = f"{'.' * node.level}{node.module or ''}"
        for alias in node.names:
            if alias.name == "find_event_list":
                self._add_finding(
                    line=getattr(alias, "lineno", node.lineno),
                    kind="legacy_event_list_discovery",
                    expression=f"from {module} import find_event_list",
                )
            if self._is_helper_file() and (
                alias.name == "RuntimeCommandPort" or "runtime_command" in module
            ):
                self._add_finding(
                    line=getattr(alias, "lineno", node.lineno),
                    kind="runtime_command_port_in_dot_helper",
                    expression=f"from {module} import {alias.name}",
                )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if self._is_helper_file() and self._is_second_write_facade_class(node.name):
            self._add_finding(
                line=node.lineno,
                kind="second_same_tick_write_facade",
                expression=f"class {node.name}",
            )
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self._is_buff_runtime_write_method(node.name):
            self._add_finding(
                line=node.lineno,
                kind="buff_runtime_read_port_write_method",
                expression=f"def {node.name}",
            )
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if self._is_buff_runtime_write_method(node.name):
            self._add_finding(
                line=node.lineno,
                kind="buff_runtime_read_port_write_method",
                expression=f"async def {node.name}",
            )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if self._is_find_event_list_call(node.func):
            self._add_finding(
                line=node.lineno,
                kind="legacy_event_list_discovery",
                expression=self._source_for(node),
            )
        if self._is_event_list_preparation_request(node):
            self._add_finding(
                line=node.lineno,
                kind="event_list_preparation_request",
                expression=self._source_for(node),
            )
        if self._is_raw_event_list_append_call(node):
            self._add_finding(
                line=node.lineno,
                kind="raw_event_list_append",
                expression=self._source_for(node),
            )
        if self._is_scheduled_dot_payload_misuse(node):
            self._add_finding(
                line=node.lineno,
                kind="dot_runtime_state_as_scheduled_payload",
                expression=self._source_for(node),
            )
        if self._is_helper_file() and self._is_runtime_command_port_call(node):
            self._add_finding(
                line=node.lineno,
                kind="runtime_command_port_in_dot_helper",
                expression=self._source_for(node),
            )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if self._is_scheduler_event_list_attribute(node):
            direct_parent = self._parents[-2] if len(self._parents) >= 2 else None
            grandparent = self._parents[-3] if len(self._parents) >= 3 else None
            if not (
                isinstance(direct_parent, ast.Attribute)
                and direct_parent.attr == "append"
                and isinstance(grandparent, ast.Call)
            ):
                self._add_finding(
                    line=node.lineno,
                    kind="raw_event_list_access",
                    expression=self._attribute_context(node),
                )
        if self._is_shock_direct_sim_instance_read(node):
            self._add_finding(
                line=node.lineno,
                kind="shock_direct_retained_read",
                expression=self._attribute_context(node),
            )
        self.generic_visit(node)

    def _is_helper_file(self) -> bool:
        return self.path in P2E_DOT_RUNTIME_HELPER_FILES

    @staticmethod
    def _is_second_write_facade_class(class_name: str) -> bool:
        lowered = class_name.lower()
        return (
            "runtimecommand" in lowered
            or "runtimewrite" in lowered
            or "writefacade" in lowered
        )

    def _is_buff_runtime_write_method(self, method_name: str) -> bool:
        if not self._class_stack or self._class_stack[-1] != "BuffRuntimeReadPort":
            return False
        return method_name.startswith(
            ("write", "set", "add", "remove", "register", "replace", "update")
        )

    @staticmethod
    def _is_find_event_list_call(func: ast.expr) -> bool:
        if isinstance(func, ast.Name):
            return func.id == "find_event_list"
        if isinstance(func, ast.Attribute):
            return func.attr == "find_event_list"
        return False

    def _is_event_list_preparation_request(self, node: ast.Call) -> bool:
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
        return isinstance(target, ast.Attribute) and self._is_scheduler_event_list_attribute(
            target
        )

    def _is_scheduler_event_list_attribute(self, node: ast.Attribute) -> bool:
        if node.attr != "event_list":
            return False
        owner = self._dotted_name(node.value)
        return (
            owner in {"record", "self.record", "schedule_data"}
            or owner.endswith(".record")
            or owner.endswith(".schedule_data")
        )

    def _is_scheduled_dot_payload_misuse(self, node: ast.Call) -> bool:
        payload = self._scheduled_payload_arg(node)
        if payload is None:
            return False
        expression = self._source_for(payload)
        if "dot" not in expression.lower():
            return False
        return not self._is_allowed_dot_scheduled_payload(payload)

    def _scheduled_payload_arg(self, node: ast.Call) -> ast.expr | None:
        call_name = self._call_name(node.func)
        if call_name == "publish_scheduled":
            return node.args[0] if node.args else None
        if call_name == "_publish_scheduled_event":
            return node.args[1] if len(node.args) >= 2 else None
        return None

    @staticmethod
    def _is_allowed_dot_scheduled_payload(node: ast.expr) -> bool:
        chain = MigratedP2EDotRuntimeVisitor._attribute_chain(node)
        return bool(chain) and chain[-1] in {"skill_node_data", "anomaly_data"}

    @staticmethod
    def _is_runtime_command_port_call(node: ast.Call) -> bool:
        call_name = MigratedP2EDotRuntimeVisitor._call_name(node.func)
        return call_name in {"RuntimeCommandPort", "create_runtime_command_port"}

    def _is_shock_direct_sim_instance_read(self, node: ast.Attribute) -> bool:
        if self.path != P2E_SHOCK_DOT_FEATURE_FILE:
            return False
        chain = self._attribute_chain(node)
        return self._contains_subchain(
            chain, ("sim_instance", "init_data", "name_box")
        ) or self._contains_subchain(
            chain, ("sim_instance", "load_data", "exist_buff_dict")
        )

    @staticmethod
    def _contains_subchain(chain: list[str], subchain: tuple[str, ...]) -> bool:
        if len(chain) < len(subchain):
            return False
        return any(
            tuple(chain[index : index + len(subchain)]) == subchain
            for index in range(len(chain) - len(subchain) + 1)
        )

    @staticmethod
    def _call_name(func: ast.expr) -> str | None:
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return func.attr
        return None

    def _attribute_context(self, node: ast.Attribute) -> str:
        direct_parent = self._parents[-2] if len(self._parents) >= 2 else None
        grandparent = self._parents[-3] if len(self._parents) >= 3 else None
        if isinstance(direct_parent, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            return self._source_for(direct_parent)
        if isinstance(direct_parent, ast.Compare):
            return self._source_for(direct_parent)
        if (
            isinstance(direct_parent, ast.Attribute)
            and direct_parent.value is node
            and isinstance(grandparent, ast.Call)
        ):
            return self._source_for(grandparent)
        return self._source_for(node)

    def _add_finding(self, *, line: int, kind: str, expression: str) -> None:
        self.findings.append(
            P2EDotRuntimeFinding(
                path=self.path.relative_to(PROJECT_ROOT).as_posix(),
                line=line,
                matched_expression=self._normalize(expression),
                classification_suggestion=self._classification_for(kind),
                next_action=self._next_action_for(kind),
            )
        )

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
            "legacy_event_list_discovery": "legacy event_list discovery helper",
            "event_list_preparation_request": (
                "legacy event_list request through Buff preparation"
            ),
            "raw_event_list_append": "raw scheduler event_list append",
            "raw_event_list_access": "raw scheduler event_list access",
            "dot_runtime_state_as_scheduled_payload": (
                "dot runtime-state mutation converted into scheduled publish"
            ),
            "runtime_command_port_in_dot_helper": (
                "same-tick RuntimeCommandPort dependency in dot runtime-state helper"
            ),
            "second_same_tick_write_facade": "second same-tick write facade",
            "buff_runtime_read_port_write_method": (
                "write method added to BuffRuntimeReadPort"
            ),
            "shock_direct_retained_read": (
                "retained direct Shock initialization sim-instance read"
            ),
        }[kind]

    @staticmethod
    def _next_action_for(kind: str) -> str:
        return {
            "legacy_event_list_discovery": (
                "replace legacy discovery with ScheduleDispatchPort"
            ),
            "event_list_preparation_request": (
                "keep planned-event publication on ScheduleDispatchPort"
            ),
            "raw_event_list_append": (
                "publish planned payloads through ScheduleDispatchPort and keep dot "
                "runtime state on DotRuntimeStateAdapter"
            ),
            "raw_event_list_access": (
                "remove raw scheduled queue access from migrated P2-E files"
            ),
            "dot_runtime_state_as_scheduled_payload": (
                "keep registration/removal on DotRuntimeStateAdapter; publish only "
                "dot.skill_node_data or freeze _dot.anomaly_data follow-ups"
            ),
            "runtime_command_port_in_dot_helper": (
                "keep same-tick writes on existing runtime command boundary outside "
                "dot helpers"
            ),
            "second_same_tick_write_facade": (
                "use the existing RuntimeCommandPort / LegacyRuntimeCommandAdapter"
            ),
            "buff_runtime_read_port_write_method": (
                "keep BuffRuntimeReadPort read-only and route writes through existing "
                "facade paths"
            ),
            "shock_direct_retained_read": (
                "route name-box and Rina passive reads through "
                "DotInitializationReadContext"
            ),
        }[kind]

    @staticmethod
    def _dotted_name(node: ast.AST) -> str:
        chain = MigratedP2EDotRuntimeVisitor._attribute_chain(node)
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
) -> list[P2EDotRuntimeFinding]:
    tree = ast.parse(source, filename=str(path))
    visitor = MigratedP2EDotRuntimeVisitor(path, source)
    visitor.visit(tree)
    return visitor.findings


def _collect_migrated_file_findings() -> list[P2EDotRuntimeFinding]:
    findings: list[P2EDotRuntimeFinding] = []
    for path in P2E_MIGRATED_DOT_RUNTIME_FILES:
        source = path.read_text(encoding="utf-8")
        findings.extend(_collect_findings_from_source(path, source))
    return findings


def test_migrated_p2e_files_do_not_regress_dot_runtime_boundaries() -> None:
    findings = _collect_migrated_file_findings()

    assert not findings, (
        "Migrated P2-E dot runtime-state files reintroduced forbidden boundaries:\n"
        + "\n".join(f"- {finding.message()}" for finding in findings)
    )


def test_migrated_p2e_guardrail_scope_is_exact_root_file_set() -> None:
    scanned_files = {
        path.relative_to(PROJECT_ROOT).as_posix()
        for path in P2E_MIGRATED_DOT_RUNTIME_FILES
    }

    assert scanned_files == {
        "zsim/sim_progress/Buff/BuffXLogic/VivianDotTrigger.py",
        "zsim/sim_progress/Buff/BuffXLogic/VivianCinema1Debuff.py",
        "zsim/sim_progress/Update/UpdateAnomaly.py",
        "zsim/sim_progress/Dot/runtime_state.py",
        "zsim/sim_progress/Dot/initialization.py",
        "zsim/sim_progress/Dot/Dots/Shock.py",
    }
    assert all(".codex_worktrees" not in path.parts for path in P2E_MIGRATED_DOT_RUNTIME_FILES)
    assert all(path.is_file() for path in P2E_MIGRATED_DOT_RUNTIME_FILES)
    assert (
        SIM_PROGRESS_ROOT / "Buff" / "BuffAddStrategy.py"
        not in P2E_MIGRATED_DOT_RUNTIME_FILES
    )
    assert SIM_PROGRESS_ROOT / "Load" / "LoadDamageEvent.py" not in P2E_MIGRATED_DOT_RUNTIME_FILES
    assert SIM_PROGRESS_ROOT / "Update" / "Update_Buff.py" not in P2E_MIGRATED_DOT_RUNTIME_FILES


def test_migrated_p2e_guardrail_reports_raw_queue_and_discovery_findings() -> None:
    source = (
        "from zsim.sim_progress.Buff.JudgeTools.FindMain import find_event_list\n"
        "def publish(record, schedule_data, event_list):\n"
        "    queue = JudgeTools.find_event_list(record)\n"
        "    event_list.append('legacy')\n"
        "    record.event_list.append('legacy')\n"
        "    schedule_data.event_list.append('legacy')\n"
        "    check_preparation(buff_instance=buff, event_list=True)\n"
        "    get_prepared(**{'event_list': 1})\n"
        "    return queue\n"
    )
    path = SIM_PROGRESS_ROOT / "Update" / "_migrated_p2e_fixture.py"

    messages = [
        finding.message() for finding in _collect_findings_from_source(path, source)
    ]

    assert any("matched expression: from zsim.sim_progress.Buff.JudgeTools.FindMain import find_event_list" in message for message in messages)
    assert any("matched expression: JudgeTools.find_event_list(record)" in message for message in messages)
    assert any("matched expression: event_list.append('legacy')" in message for message in messages)
    assert any("matched expression: record.event_list.append('legacy')" in message for message in messages)
    assert any("matched expression: schedule_data.event_list.append('legacy')" in message for message in messages)
    assert any("matched expression: check_preparation(buff_instance=buff, event_list=True)" in message for message in messages)
    assert any("matched expression: get_prepared(**{'event_list': 1})" in message for message in messages)
    assert any("classification suggestion: legacy event_list discovery helper" in message for message in messages)
    assert any("classification suggestion: raw scheduler event_list append" in message for message in messages)
    assert any("next action: publish planned payloads through ScheduleDispatchPort" in message for message in messages)


def test_migrated_p2e_guardrail_blocks_dot_runtime_scheduled_publish_misuse() -> None:
    source = (
        "def publish(dot, new_dot, _dot, dispatch_port):\n"
        "    dispatch_port.publish_scheduled(dot)\n"
        "    dispatch_port.publish_scheduled(new_dot.skill_node_data)\n"
        "    _publish_scheduled_event(dispatch_port, new_dot)\n"
        "    _publish_scheduled_event(dispatch_port, _dot.anomaly_data)\n"
    )
    path = SIM_PROGRESS_ROOT / "Update" / "_migrated_p2e_fixture.py"

    findings = _collect_findings_from_source(path, source)
    messages = [finding.message() for finding in findings]

    assert len(findings) == 2
    assert any("matched expression: dispatch_port.publish_scheduled(dot)" in message for message in messages)
    assert any("matched expression: _publish_scheduled_event(dispatch_port, new_dot)" in message for message in messages)
    assert all(
        "classification suggestion: dot runtime-state mutation converted into scheduled publish"
        in message
        for message in messages
    )
    assert any("next action: keep registration/removal on DotRuntimeStateAdapter" in message for message in messages)


def test_migrated_p2e_guardrail_blocks_helper_runtime_write_boundaries() -> None:
    source = (
        "from zsim.sim_progress.ScheduledEvent.runtime_command import RuntimeCommandPort\n"
        "class DotRuntimeWriteFacade:\n"
        "    pass\n"
        "class BuffRuntimeReadPort:\n"
        "    def write_dot(self, dot):\n"
        "        pass\n"
        "def create():\n"
        "    return RuntimeCommandPort()\n"
    )
    path = DOT_ROOT / "runtime_state.py"

    messages = [
        finding.message() for finding in _collect_findings_from_source(path, source)
    ]

    assert any("matched expression: from zsim.sim_progress.ScheduledEvent.runtime_command import RuntimeCommandPort" in message for message in messages)
    assert any("matched expression: class DotRuntimeWriteFacade" in message for message in messages)
    assert any("matched expression: def write_dot" in message for message in messages)
    assert any("matched expression: RuntimeCommandPort()" in message for message in messages)
    assert any("classification suggestion: same-tick RuntimeCommandPort dependency in dot runtime-state helper" in message for message in messages)
    assert any("classification suggestion: second same-tick write facade" in message for message in messages)
    assert any("classification suggestion: write method added to BuffRuntimeReadPort" in message for message in messages)


def test_migrated_p2e_guardrail_reports_shock_direct_read_retained_boundary() -> None:
    source = (
        "class Shock:\n"
        "    class DotFeature:\n"
        "        def __post_init__(self):\n"
        "            self.char_name_box = self.sim_instance.init_data.name_box\n"
        "            self.exist_buff_dict = self.sim_instance.load_data.exist_buff_dict\n"
    )

    messages = [
        finding.message()
        for finding in _collect_findings_from_source(P2E_SHOCK_DOT_FEATURE_FILE, source)
    ]

    assert any(
        "matched expression: self.char_name_box = self.sim_instance.init_data.name_box"
        in message
        for message in messages
    )
    assert any(
        "matched expression: self.exist_buff_dict = self.sim_instance.load_data.exist_buff_dict"
        in message
        for message in messages
    )
    assert all(
        "classification suggestion: retained direct Shock initialization sim-instance read"
        in message
        for message in messages
    )
    assert any("next action: route name-box and Rina passive reads through DotInitializationReadContext" in message for message in messages)


def test_migrated_p2e_guardrail_uses_ast_not_text_matching_and_allows_followups() -> None:
    source = (
        "def clean(dot, _dot, dispatch_port):\n"
        "    '''event_list.append record.event_list JudgeTools.find_event_list'''\n"
        "    # RuntimeCommandPort BuffRuntimeReadPort self.sim_instance.init_data.name_box\n"
        "    event_list_value.append(dot)\n"
        "    dispatch_port.publish_scheduled(dot.skill_node_data)\n"
        "    _publish_scheduled_event(dispatch_port, _dot.anomaly_data)\n"
        "    check_preparation(buff_instance=buff, event_list=False)\n"
        "    dot_runtime_state.register(dot)\n"
    )
    path = SIM_PROGRESS_ROOT / "Update" / "_migrated_p2e_fixture.py"

    assert _collect_findings_from_source(path, source) == []
