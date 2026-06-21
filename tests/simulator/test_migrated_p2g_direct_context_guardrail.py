from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUFF_XLOGIC_ROOT = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffXLogic"


@dataclass(frozen=True)
class P2GDirectContextTarget:
    path: Path
    node_path: tuple[str, ...]
    allowed_layers: frozenset[str]
    required_terms: tuple[str, ...]

    @property
    def key(self) -> str:
        relative_path = self.path.relative_to(PROJECT_ROOT).as_posix()
        return f"{relative_path}::{'.'.join(self.node_path)}"


@dataclass(frozen=True)
class P2GDirectContextFinding:
    path: str
    symbol: str
    line: int
    kind: str
    expression: str

    def message(self) -> str:
        return f"{self.path}::{self.symbol}:{self.line}: {self.kind} " f"({self.expression})"


P2G_DIRECT_CONTEXT_TARGETS = (
    P2GDirectContextTarget(
        path=BUFF_XLOGIC_ROOT / "YuzuhaHardCandyShotTrigger.py",
        node_path=("YuzuhaHardCandyShotTrigger",),
        allowed_layers=frozenset({"tick_preload"}),
        required_terms=("sim_instance.tick", "char_occupied_check"),
    ),
    P2GDirectContextTarget(
        path=BUFF_XLOGIC_ROOT / "YuzuhaCinema4QuickAssistTrigger.py",
        node_path=("YuzuhaCinema4QuickAssistTrigger",),
        allowed_layers=frozenset({"next_character", "report_state"}),
        required_terms=("quick_assist_system", "find_next_char_obj", "change_process_state"),
    ),
    P2GDirectContextTarget(
        path=BUFF_XLOGIC_ROOT / "YuzuhaCinema6SheelTrigger.py",
        node_path=("YuzuhaCinema6SheelTrigger",),
        allowed_layers=frozenset({"tick_preload", "scheduled_publish", "report_state"}),
        required_terms=(
            "build_preparation_context_from_buff",
            "preload_commands.schedule_preload_events",
            "change_process_state",
        ),
    ),
    P2GDirectContextTarget(
        path=BUFF_XLOGIC_ROOT / "AlicePolarizedAssaultTrigger.py",
        node_path=("AlicePolarizedAssaultTrigger", "special_effect_logic"),
        allowed_layers=frozenset({"scheduled_publish", "report_state"}),
        required_terms=(
            "PolarizedAssaultEvent",
            "deepcopy",
            "emit_scheduled",
            "change_process_state",
        ),
    ),
    P2GDirectContextTarget(
        path=BUFF_XLOGIC_ROOT / "YuzuhaCinema2Trigger.py",
        node_path=("YuzuhaCinema2Trigger",),
        allowed_layers=frozenset({"tick_preload", "report_state"}),
        required_terms=("read_enemy_stun_active", "is_last_hit", "change_process_state"),
    ),
    P2GDirectContextTarget(
        path=BUFF_XLOGIC_ROOT / "YuzuhaSugarBurstAnomalyBuildupBonus.py",
        node_path=("YuzuhaSugarBurstAnomalyBuildupBonus",),
        allowed_layers=frozenset({"tick_preload"}),
        required_terms=("preload_tick", "sim_instance.tick"),
    ),
    P2GDirectContextTarget(
        path=BUFF_XLOGIC_ROOT / "YixuanAdditionalAbilityDmgBonus.py",
        node_path=("YixuanAdditionalAbilityDmgBonus",),
        allowed_layers=frozenset({"enemy_context", "report_state"}),
        required_terms=("schedule_data.enemy", "read_enemy_stun_active"),
    ),
    P2GDirectContextTarget(
        path=BUFF_XLOGIC_ROOT / "HeartstringNocturne.py",
        node_path=("HeartstringNocturne", "special_judge_logic"),
        allowed_layers=frozenset({"listener_lookup"}),
        required_terms=("listener_manager.get_listener", "listener_exist"),
    ),
    P2GDirectContextTarget(
        path=BUFF_XLOGIC_ROOT / "CannonRotor.py",
        node_path=("CannonRotor", "special_judge_logic"),
        allowed_layers=frozenset({"rng_service", "attribute_read"}),
        required_terms=("rng_instance", "random_float", "read_full_crit_rate"),
    ),
    P2GDirectContextTarget(
        path=BUFF_XLOGIC_ROOT / "CannonRotor.py",
        node_path=("CannonRotor", "special_hit_logic"),
        allowed_layers=frozenset({"scheduled_publish"}),
        required_terms=("spawn_node", "LoadingMission", "emit_scheduled", "simple_start"),
    ),
    P2GDirectContextTarget(
        path=BUFF_XLOGIC_ROOT / "WoodpeckerElectroSet4_NA.py",
        node_path=("WoodpeckerElectroSet4_NA", "special_judge_logic"),
        allowed_layers=frozenset({"rng_service", "attribute_read"}),
        required_terms=("rng_instance", "random_float", "read_full_crit_rate"),
    ),
    P2GDirectContextTarget(
        path=BUFF_XLOGIC_ROOT / "WoodpeckerElectroSet4_E_EX.py",
        node_path=("WoodpeckerElectroSet4_E_EX", "special_judge_logic"),
        allowed_layers=frozenset({"rng_service", "attribute_read"}),
        required_terms=("rng_instance", "random_float", "read_full_crit_rate"),
    ),
    P2GDirectContextTarget(
        path=BUFF_XLOGIC_ROOT / "WoodpeckerElectroSet4_CA.py",
        node_path=("WoodpeckerElectroSet4_CA", "special_judge_logic"),
        allowed_layers=frozenset({"rng_service", "attribute_read"}),
        required_terms=("rng_instance", "random_float", "read_full_crit_rate"),
    ),
    P2GDirectContextTarget(
        path=BUFF_XLOGIC_ROOT / "AstraYaoCorePassiveAtkBonus.py",
        node_path=("AstraYaoCorePassiveAtkBonus", "special_start_logic"),
        allowed_layers=frozenset({"report_state"}),
        required_terms=("simple_start", "update_to_buff_0", "change_process_state"),
    ),
    P2GDirectContextTarget(
        path=BUFF_XLOGIC_ROOT / "YixuanCinema1Trigger.py",
        node_path=("YixuanCinema1Trigger", "special_hit_logic"),
        allowed_layers=frozenset({"scheduled_publish", "report_state"}),
        required_terms=(
            "spawn_node",
            "LoadingMission",
            "emit_scheduled",
            "update_adrenaline",
            "simple_start",
            "change_process_state",
        ),
    ),
)


RUNTIME_BOUNDARY_NAMES = {
    "RuntimeCommandPort",
    "create_runtime_command_port",
    "LegacyRuntimeCommandAdapter",
    "LegacyBuffRuntimeFacade",
    "create_legacy_buff_runtime_facade",
    "BuffRuntimeReadPort",
    "create_buff_runtime_read_port",
}

SCHEDULED_PUBLISH_NAMES = {
    "ScheduleDispatchPort",
    "create_schedule_dispatch_port",
    "emit_scheduled",
    "publish_scheduled",
    "schedule_preload_events",
    "schedule_preload_event_factory",
}


class P2GDirectContextVisitor(ast.NodeVisitor):
    def __init__(
        self,
        *,
        path: Path,
        symbol: str,
        source: str,
        allowed_layers: frozenset[str],
    ) -> None:
        self.path = path
        self.symbol = symbol
        self.source = source
        self.allowed_layers = allowed_layers
        self.findings: list[P2GDirectContextFinding] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._check_name(alias.name, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self._check_name(node.module, node.lineno)
        for alias in node.names:
            self._check_name(alias.name, node.lineno)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        self._check_name(node.id, node.lineno)

    def visit_Call(self, node: ast.Call) -> None:
        call_name = self._dotted_name(node.func)
        expression = self._source_for(node)

        if self._is_event_list_mutator(node):
            self._add_finding(
                line=node.lineno,
                kind="raw scheduled queue mutation",
                expression=expression,
            )
            return

        if "find_event_list" in call_name:
            self._add_finding(
                line=node.lineno,
                kind="legacy event-list discovery",
                expression=expression,
            )
            return

        if self._contains_any(call_name, RUNTIME_BOUNDARY_NAMES):
            self._add_finding(
                line=node.lineno,
                kind="runtime command/facade boundary",
                expression=expression,
            )
            return

        if self._contains_any(call_name, SCHEDULED_PUBLISH_NAMES) and (
            "scheduled_publish" not in self.allowed_layers
        ):
            self._add_finding(
                line=node.lineno,
                kind="scheduled publish boundary",
                expression=expression,
            )
            return

        if call_name.endswith("broadcast_event"):
            self._add_finding(
                line=node.lineno,
                kind="listener broadcast boundary",
                expression=expression,
            )
            return

        if "listener_manager" in call_name:
            if not (
                "listener_lookup" in self.allowed_layers and call_name.endswith("get_listener")
            ):
                self._add_finding(
                    line=node.lineno,
                    kind="listener manager boundary",
                    expression=expression,
                )
                return

        if call_name.endswith("change_process_state") and (
            "report_state" not in self.allowed_layers
        ):
            self._add_finding(
                line=node.lineno,
                kind="report-state mutation",
                expression=expression,
            )
            return

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self._check_assignment_target(target, node.lineno)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._check_assignment_target(node.target, node.lineno)
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self._check_assignment_target(node.target, node.lineno)
        self.generic_visit(node)

    def visit_Delete(self, node: ast.Delete) -> None:
        for target in node.targets:
            self._check_assignment_target(target, node.lineno)
        self.generic_visit(node)

    def visit_keyword(self, node: ast.keyword) -> None:
        if node.arg == "event_list":
            self._add_finding(
                line=node.lineno,
                kind="raw scheduled queue passthrough",
                expression=self._source_for(node.value),
            )
            return
        self.generic_visit(node)

    def _check_name(self, name: str, line: int) -> None:
        if self._contains_any(name, RUNTIME_BOUNDARY_NAMES):
            self._add_finding(
                line=line,
                kind="runtime command/facade boundary",
                expression=name,
            )
        if self._contains_any(name, SCHEDULED_PUBLISH_NAMES) and (
            "scheduled_publish" not in self.allowed_layers
        ):
            self._add_finding(
                line=line,
                kind="scheduled publish boundary",
                expression=name,
            )

    def _check_assignment_target(self, target: ast.AST, line: int) -> None:
        if self._is_event_list_target(target):
            self._add_finding(
                line=line,
                kind="raw scheduled queue mutation",
                expression=self._source_for(target),
            )

    def _is_event_list_mutator(self, node: ast.Call) -> bool:
        if not isinstance(node.func, ast.Attribute):
            return False
        if node.func.attr not in {"append", "extend", "insert", "clear", "pop", "remove"}:
            return False
        return self._is_event_list_target(node.func.value)

    def _is_event_list_target(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            return node.id == "event_list"
        if isinstance(node, ast.Attribute):
            return node.attr == "event_list" or self._is_event_list_target(node.value)
        if isinstance(node, ast.Subscript):
            return self._is_event_list_target(node.value)
        if isinstance(node, ast.Starred):
            return self._is_event_list_target(node.value)
        if isinstance(node, (ast.Tuple, ast.List)):
            return any(self._is_event_list_target(elt) for elt in node.elts)
        return False

    def _add_finding(self, *, line: int, kind: str, expression: str) -> None:
        finding = P2GDirectContextFinding(
            path=self.path.relative_to(PROJECT_ROOT).as_posix(),
            symbol=self.symbol,
            line=line,
            kind=kind,
            expression=expression,
        )
        if finding not in self.findings:
            self.findings.append(finding)

    def _source_for(self, node: ast.AST) -> str:
        source = ast.get_source_segment(self.source, node)
        if source is not None:
            return " ".join(source.split())
        return type(node).__name__

    @staticmethod
    def _contains_any(name: str, terms: set[str]) -> bool:
        return any(term in name for term in terms)

    @staticmethod
    def _dotted_name(node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            prefix = P2GDirectContextVisitor._dotted_name(node.value)
            if prefix:
                return f"{prefix}.{node.attr}"
            return node.attr
        if isinstance(node, ast.Call):
            return f"{P2GDirectContextVisitor._dotted_name(node.func)}()"
        if isinstance(node, ast.Subscript):
            return P2GDirectContextVisitor._dotted_name(node.value)
        return ""


def _find_node(root: ast.Module, node_path: tuple[str, ...]) -> ast.AST:
    current: ast.AST = root
    for name in node_path:
        body = getattr(current, "body", None)
        if not isinstance(body, list):
            raise AssertionError(f"Cannot descend into {'.'.join(node_path)}")
        for child in body:
            if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if child.name == name:
                    current = child
                    break
        else:
            raise AssertionError(f"Missing symbol {'.'.join(node_path)}")
    return current


def _source_for_target(target: P2GDirectContextTarget) -> str:
    source = target.path.read_text(encoding="utf-8")
    node = _find_node(ast.parse(source), target.node_path)
    return ast.get_source_segment(source, node) or ""


def _collect_findings_from_source(
    path: Path,
    source: str,
    *,
    node_path: tuple[str, ...],
    allowed_layers: frozenset[str],
) -> list[P2GDirectContextFinding]:
    root = ast.parse(source)
    node = _find_node(root, node_path)
    visitor = P2GDirectContextVisitor(
        path=path,
        symbol=".".join(node_path),
        source=source,
        allowed_layers=allowed_layers,
    )
    visitor.visit(node)
    return visitor.findings


def _collect_target_findings() -> list[P2GDirectContextFinding]:
    findings: list[P2GDirectContextFinding] = []
    for target in P2G_DIRECT_CONTEXT_TARGETS:
        source = target.path.read_text(encoding="utf-8")
        findings.extend(
            _collect_findings_from_source(
                target.path,
                source,
                node_path=target.node_path,
                allowed_layers=target.allowed_layers,
            )
        )
    return findings


def test_migrated_p2g_direct_context_files_do_not_regress_boundaries() -> None:
    findings = _collect_target_findings()

    assert (
        not findings
    ), "Migrated P2-G direct-context targets reintroduced forbidden boundaries:\n" + "\n".join(
        f"- {finding.message()}" for finding in findings
    )


def test_migrated_p2g_guardrail_scope_is_exact_root_service_set() -> None:
    expected_keys = {
        "zsim/sim_progress/Buff/BuffXLogic/YuzuhaHardCandyShotTrigger.py::YuzuhaHardCandyShotTrigger",
        "zsim/sim_progress/Buff/BuffXLogic/YuzuhaCinema4QuickAssistTrigger.py::YuzuhaCinema4QuickAssistTrigger",
        "zsim/sim_progress/Buff/BuffXLogic/YuzuhaCinema6SheelTrigger.py::YuzuhaCinema6SheelTrigger",
        "zsim/sim_progress/Buff/BuffXLogic/AlicePolarizedAssaultTrigger.py::AlicePolarizedAssaultTrigger.special_effect_logic",
        "zsim/sim_progress/Buff/BuffXLogic/YuzuhaCinema2Trigger.py::YuzuhaCinema2Trigger",
        "zsim/sim_progress/Buff/BuffXLogic/YuzuhaSugarBurstAnomalyBuildupBonus.py::YuzuhaSugarBurstAnomalyBuildupBonus",
        "zsim/sim_progress/Buff/BuffXLogic/YixuanAdditionalAbilityDmgBonus.py::YixuanAdditionalAbilityDmgBonus",
        "zsim/sim_progress/Buff/BuffXLogic/HeartstringNocturne.py::HeartstringNocturne.special_judge_logic",
        "zsim/sim_progress/Buff/BuffXLogic/CannonRotor.py::CannonRotor.special_judge_logic",
        "zsim/sim_progress/Buff/BuffXLogic/CannonRotor.py::CannonRotor.special_hit_logic",
        "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_NA.py::WoodpeckerElectroSet4_NA.special_judge_logic",
        "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_E_EX.py::WoodpeckerElectroSet4_E_EX.special_judge_logic",
        "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_CA.py::WoodpeckerElectroSet4_CA.special_judge_logic",
        "zsim/sim_progress/Buff/BuffXLogic/AstraYaoCorePassiveAtkBonus.py::AstraYaoCorePassiveAtkBonus.special_start_logic",
        "zsim/sim_progress/Buff/BuffXLogic/YixuanCinema1Trigger.py::YixuanCinema1Trigger.special_hit_logic",
    }

    actual_keys = {target.key for target in P2G_DIRECT_CONTEXT_TARGETS}
    assert actual_keys == expected_keys

    for target in P2G_DIRECT_CONTEXT_TARGETS:
        relative_parts = target.path.relative_to(PROJECT_ROOT).parts
        assert ".codex_worktrees" not in relative_parts
        assert "__pycache__" not in relative_parts
        assert relative_parts[:3] != ("scripts", "ralph", "archive")
        assert target.path.suffix == ".py"
        assert target.path.is_file()


def test_migrated_p2g_guardrail_preserves_service_family_markers() -> None:
    for target in P2G_DIRECT_CONTEXT_TARGETS:
        source = _source_for_target(target)
        missing_terms = [term for term in target.required_terms if term not in source]
        assert not missing_terms, f"{target.key} missing {missing_terms}"


def test_migrated_p2g_guardrail_reports_forbidden_boundaries_with_context() -> None:
    source = """
class Fixture:
    def special_judge_logic(self):
        self.buff_instance.sim_instance.schedule_data.event_list.append("raw")
        JudgeTools.find_event_list()
        create_runtime_command_port(data=data, exist_buff_dict=buffs)
        self.buff_instance.sim_instance.listener_manager.broadcast_event("event")
        create_schedule_dispatch_port(sim_instance=sim).publish_scheduled(node)
        self._scheduled_event_emitter().emit_scheduled(node)
        self.context.preload_commands.schedule_preload_events(
            preload_tick_list=[1],
            skill_tag_list=["fixture"],
        )
"""

    findings = _collect_findings_from_source(
        BUFF_XLOGIC_ROOT / "_migrated_p2g_fixture.py",
        source,
        node_path=("Fixture", "special_judge_logic"),
        allowed_layers=frozenset(),
    )
    messages = [finding.message() for finding in findings]

    assert len(findings) == 7
    assert any("raw scheduled queue mutation" in message for message in messages)
    assert any("legacy event-list discovery" in message for message in messages)
    assert any("runtime command/facade boundary" in message for message in messages)
    assert any("listener broadcast boundary" in message for message in messages)
    assert any(
        "scheduled publish boundary" in message
        and "create_schedule_dispatch_port(sim_instance=sim).publish_scheduled(node)"
        in message
        for message in messages
    )
    assert any(
        "scheduled publish boundary" in message
        and "self._scheduled_event_emitter().emit_scheduled(node)" in message
        for message in messages
    )
    assert any(
        "scheduled publish boundary" in message
        and "self.context.preload_commands.schedule_preload_events" in message
        for message in messages
    )


def test_migrated_p2g_guardrail_uses_ast_not_text_matching_and_allows_retained_layers() -> None:
    source = """
class Fixture:
    def special_judge_logic(self):
        note = "event_list create_runtime_command_port broadcast_event"
        self.buff_instance.sim_instance.schedule_data.change_process_state()
        return self.buff_instance.sim_instance.listener_manager.get_listener(
            listener_owner=self,
            listener_id="Fixture",
        )
"""

    findings = _collect_findings_from_source(
        BUFF_XLOGIC_ROOT / "_migrated_p2g_fixture.py",
        source,
        node_path=("Fixture", "special_judge_logic"),
        allowed_layers=frozenset({"listener_lookup", "report_state"}),
    )

    assert findings == []
