from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SIM_PROGRESS_ROOT = PROJECT_ROOT / "zsim" / "sim_progress"
BUFF_XLOGIC_ROOT = SIM_PROGRESS_ROOT / "Buff" / "BuffXLogic"
RESOURCE_REFRESH_COMMAND_CHECKPOINT_PATH = (
    PROJECT_ROOT
    / "scripts"
    / "ralph"
    / "checkpoints"
    / "2026-06-21-US-006-resource-refresh-command-family-checkpoint.json"
)

P2D_MIGRATED_SCHEDULED_PUBLISH_FILES = (
    BUFF_XLOGIC_ROOT / "AlicePolarizedAssaultTrigger.py",
    BUFF_XLOGIC_ROOT / "CannonRotor.py",
    BUFF_XLOGIC_ROOT / "ElegantVanitySpRecover.py",
    BUFF_XLOGIC_ROOT / "HugoCorePassiveTotalizeTrigger.py",
    BUFF_XLOGIC_ROOT / "LunarNoviluna.py",
    BUFF_XLOGIC_ROOT / "MagneticStormCharlieSpRecover.py",
    BUFF_XLOGIC_ROOT / "MiyabiCoreSkill_IceFire.py",
    BUFF_XLOGIC_ROOT / "SeedAdditionalAbilityTrigger.py",
    BUFF_XLOGIC_ROOT / "SliceofTimeExtraResources.py",
    BUFF_XLOGIC_ROOT / "VivianCinema6Trigger.py",
    BUFF_XLOGIC_ROOT / "VivianCorePassiveTrigger.py",
    BUFF_XLOGIC_ROOT / "VivianDotTrigger.py",
    BUFF_XLOGIC_ROOT / "YanagiPolarityDisorderTrigger.py",
    BUFF_XLOGIC_ROOT / "YixuanCinema1Trigger.py",
    SIM_PROGRESS_ROOT / "Character" / "Yuzuha" / "__init__.py",
    SIM_PROGRESS_ROOT / "Enemy" / "EnemyUniqueMechanic" / "BreakingLegManager.py",
    SIM_PROGRESS_ROOT / "Update" / "UpdateAnomaly.py",
    SIM_PROGRESS_ROOT / "data_struct" / "BattleEventListener" / "AliceDotTriggerListener.py",
    SIM_PROGRESS_ROOT / "data_struct" / "DecibelManager" / "DecibelManagerClass.py",
    SIM_PROGRESS_ROOT / "data_struct" / "PolarizedAssaultEventClass.py",
    SIM_PROGRESS_ROOT / "data_struct" / "QuickAssistSystem" / "__init__.py",
)

RESOURCE_REFRESH_COMMAND_FILES = (
    BUFF_XLOGIC_ROOT / "ElegantVanitySpRecover.py",
    BUFF_XLOGIC_ROOT / "LunarNoviluna.py",
    BUFF_XLOGIC_ROOT / "MagneticStormCharlieSpRecover.py",
    BUFF_XLOGIC_ROOT / "SeedAdditionalAbilityTrigger.py",
    BUFF_XLOGIC_ROOT / "SliceofTimeExtraResources.py",
)

RETAINED_CORE_SCHEDULE_FILES = {
    SIM_PROGRESS_ROOT / "data_struct" / "schedule_dispatch.py",
    SIM_PROGRESS_ROOT / "data_struct" / "SchedulePreload.py",
    SIM_PROGRESS_ROOT / "ScheduledEvent" / "runtime_command.py",
}

RETAINED_LOCAL_CHARACTER_EVENT_GROUP_FILES = {
    SIM_PROGRESS_ROOT / "Character" / "Yixuan" / "AdrenalineManagerClass.py",
}


@dataclass(frozen=True)
class P2DScheduledPublishFinding:
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


class MigratedP2DScheduledPublishVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source: str) -> None:
        self.path = path
        self.source = source
        self.findings: list[P2DScheduledPublishFinding] = []
        self._parents: list[ast.AST] = []
        self._class_stack: list[str] = []
        self._function_depth = 0

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

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function_depth += 1
        self.generic_visit(node)
        self._function_depth -= 1

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function_depth += 1
        self.generic_visit(node)
        self._function_depth -= 1

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            if alias.name == "find_event_list":
                module = f"{'.' * node.level}{node.module or ''}"
                self._add_finding(
                    line=getattr(alias, "lineno", node.lineno),
                    kind="legacy_event_list_discovery",
                    expression=f"from {module} import find_event_list",
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
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        self._check_dispatch_adapter_assignment(node.targets, node.value, node.lineno)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None:
            self._check_dispatch_adapter_assignment(
                [node.target], node.value, node.lineno
            )
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self._check_dispatch_adapter_assignment([node.target], node.value, node.lineno)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr == "event_list":
            owner = self._dotted_name(node.value)
            if owner in {"record", "self.record"}:
                self._add_finding(
                    line=node.lineno,
                    kind="record_event_list_access",
                    expression=self._attribute_context(node),
                )
            elif owner == "schedule_data" or owner.endswith(".schedule_data"):
                self._add_finding(
                    line=node.lineno,
                    kind="schedule_data_event_list_access",
                    expression=self._attribute_context(node),
                )
        self.generic_visit(node)

    def _check_dispatch_adapter_assignment(
        self, targets: list[ast.expr], value: ast.expr, line: int
    ) -> None:
        if not self._is_dispatch_factory_call(value):
            return
        for target in targets:
            if self._is_persistent_dispatch_target(target):
                self._add_finding(
                    line=line,
                    kind="cached_dispatch_adapter",
                    expression=self._source_for(target),
                )

    def _is_persistent_dispatch_target(self, target: ast.expr) -> bool:
        chain = self._attribute_chain(target)
        if not chain or not any("dispatch" in part.lower() for part in chain):
            return False
        if self._function_depth == 0 and self._class_stack:
            return True
        if chain[0] in {"self", "record"}:
            return True
        return "record" in chain

    @staticmethod
    def _is_dispatch_factory_call(node: ast.expr) -> bool:
        if not isinstance(node, ast.Call):
            return False
        if isinstance(node.func, ast.Name):
            return node.func.id == "create_schedule_dispatch_port"
        if isinstance(node.func, ast.Attribute):
            return node.func.attr in {
                "create_schedule_dispatch_port",
                "_create_dispatch_port",
            }
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
    def _is_find_event_list_call(func: ast.expr) -> bool:
        if isinstance(func, ast.Name):
            return func.id == "find_event_list"
        if isinstance(func, ast.Attribute):
            return func.attr == "find_event_list"
        return False

    @staticmethod
    def _call_name(func: ast.expr) -> str | None:
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return func.attr
        return None

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
            P2DScheduledPublishFinding(
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
            "cached_dispatch_adapter": "long-lived cached ScheduleDispatchPort adapter",
            "event_list_preparation_request": (
                "legacy event_list request through Buff preparation"
            ),
            "legacy_event_list_discovery": "legacy event_list discovery helper",
            "record_event_list_access": "raw record.event_list scheduled queue access",
            "schedule_data_event_list_access": (
                "raw schedule_data.event_list scheduled queue access"
            ),
        }[kind]

    @staticmethod
    def _next_action_for(kind: str) -> str:
        return {
            "cached_dispatch_adapter": (
                "create the ScheduleDispatchPort on demand from current sim_instance "
                "or schedule_data"
            ),
            "event_list_preparation_request": (
                "route planned-event publication through ScheduleDispatchPort"
            ),
            "legacy_event_list_discovery": (
                "replace legacy discovery with an explicit schedule dispatch boundary"
            ),
            "record_event_list_access": (
                "publish through ScheduleDispatchPort instead of record.event_list"
            ),
            "schedule_data_event_list_access": (
                "publish through ScheduleDispatchPort instead of schedule_data.event_list"
            ),
        }[kind]

    @staticmethod
    def _dotted_name(node: ast.AST) -> str:
        chain = MigratedP2DScheduledPublishVisitor._attribute_chain(node)
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
) -> list[P2DScheduledPublishFinding]:
    tree = ast.parse(source, filename=str(path))
    visitor = MigratedP2DScheduledPublishVisitor(path, source)
    visitor.visit(tree)
    return visitor.findings


def _collect_migrated_file_findings() -> list[P2DScheduledPublishFinding]:
    findings: list[P2DScheduledPublishFinding] = []
    for path in P2D_MIGRATED_SCHEDULED_PUBLISH_FILES:
        source = path.read_text(encoding="utf-8")
        findings.extend(_collect_findings_from_source(path, source))
    return findings


def _schedule_refresh_constructor_names(tree: ast.AST) -> set[str]:
    constructor_names = {"ScheduleRefreshData"}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        for alias in node.names:
            if alias.name == "ScheduleRefreshData":
                constructor_names.add(alias.asname or alias.name)
    return constructor_names


def _collect_schedule_refresh_constructor_findings_from_source(
    path: Path, source: str
) -> list[str]:
    tree = ast.parse(source, filename=str(path))
    constructor_names = _schedule_refresh_constructor_names(tree)
    relative_path = path.relative_to(PROJECT_ROOT).as_posix()
    findings: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id in constructor_names:
            findings.append(f"{relative_path}:{node.lineno}: {node.func.id}(...)")
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "ScheduleRefreshData"
        ):
            findings.append(
                f"{relative_path}:{node.lineno}: "
                f"{ast.unparse(node.func) if hasattr(ast, 'unparse') else node.func.attr}(...)"
            )
    return findings


def _collect_resource_refresh_constructor_findings() -> list[str]:
    findings: list[str] = []
    for path in RESOURCE_REFRESH_COMMAND_FILES:
        source = path.read_text(encoding="utf-8")
        findings.extend(
            _collect_schedule_refresh_constructor_findings_from_source(path, source)
        )
    return findings


def test_migrated_p2d_files_do_not_use_raw_queue_or_cached_dispatch_adapter() -> None:
    findings = _collect_migrated_file_findings()

    assert not findings, (
        "Migrated P2-D scheduled-publish files reintroduced forbidden queue access:\n"
        + "\n".join(f"- {finding.message()}" for finding in findings)
    )


def test_migrated_p2d_guardrail_scope_is_exact_root_file_set() -> None:
    scanned_files = {
        path.relative_to(PROJECT_ROOT).as_posix()
        for path in P2D_MIGRATED_SCHEDULED_PUBLISH_FILES
    }

    assert scanned_files == {
        "zsim/sim_progress/Buff/BuffXLogic/AlicePolarizedAssaultTrigger.py",
        "zsim/sim_progress/Buff/BuffXLogic/CannonRotor.py",
        "zsim/sim_progress/Buff/BuffXLogic/ElegantVanitySpRecover.py",
        "zsim/sim_progress/Buff/BuffXLogic/HugoCorePassiveTotalizeTrigger.py",
        "zsim/sim_progress/Buff/BuffXLogic/LunarNoviluna.py",
        "zsim/sim_progress/Buff/BuffXLogic/MagneticStormCharlieSpRecover.py",
        "zsim/sim_progress/Buff/BuffXLogic/MiyabiCoreSkill_IceFire.py",
        "zsim/sim_progress/Buff/BuffXLogic/SeedAdditionalAbilityTrigger.py",
        "zsim/sim_progress/Buff/BuffXLogic/SliceofTimeExtraResources.py",
        "zsim/sim_progress/Buff/BuffXLogic/VivianCinema6Trigger.py",
        "zsim/sim_progress/Buff/BuffXLogic/VivianCorePassiveTrigger.py",
        "zsim/sim_progress/Buff/BuffXLogic/VivianDotTrigger.py",
        "zsim/sim_progress/Buff/BuffXLogic/YanagiPolarityDisorderTrigger.py",
        "zsim/sim_progress/Buff/BuffXLogic/YixuanCinema1Trigger.py",
        "zsim/sim_progress/Character/Yuzuha/__init__.py",
        "zsim/sim_progress/Enemy/EnemyUniqueMechanic/BreakingLegManager.py",
        "zsim/sim_progress/Update/UpdateAnomaly.py",
        "zsim/sim_progress/data_struct/BattleEventListener/AliceDotTriggerListener.py",
        "zsim/sim_progress/data_struct/DecibelManager/DecibelManagerClass.py",
        "zsim/sim_progress/data_struct/PolarizedAssaultEventClass.py",
        "zsim/sim_progress/data_struct/QuickAssistSystem/__init__.py",
    }
    assert all(
        ".codex_worktrees" not in path.parts
        for path in P2D_MIGRATED_SCHEDULED_PUBLISH_FILES
    )
    assert all(path.is_file() for path in P2D_MIGRATED_SCHEDULED_PUBLISH_FILES)
    assert not RETAINED_CORE_SCHEDULE_FILES & set(P2D_MIGRATED_SCHEDULED_PUBLISH_FILES)
    assert not RETAINED_LOCAL_CHARACTER_EVENT_GROUP_FILES & set(
        P2D_MIGRATED_SCHEDULED_PUBLISH_FILES
    )


def test_resource_refresh_command_guardrail_scope_is_exact_selected_file_set() -> None:
    scanned_files = {
        path.relative_to(PROJECT_ROOT).as_posix()
        for path in RESOURCE_REFRESH_COMMAND_FILES
    }

    assert scanned_files == {
        "zsim/sim_progress/Buff/BuffXLogic/ElegantVanitySpRecover.py",
        "zsim/sim_progress/Buff/BuffXLogic/LunarNoviluna.py",
        "zsim/sim_progress/Buff/BuffXLogic/MagneticStormCharlieSpRecover.py",
        "zsim/sim_progress/Buff/BuffXLogic/SeedAdditionalAbilityTrigger.py",
        "zsim/sim_progress/Buff/BuffXLogic/SliceofTimeExtraResources.py",
    }
    assert set(RESOURCE_REFRESH_COMMAND_FILES) <= set(
        P2D_MIGRATED_SCHEDULED_PUBLISH_FILES
    )
    assert all(path.is_file() for path in RESOURCE_REFRESH_COMMAND_FILES)


def test_resource_refresh_command_files_do_not_directly_construct_schedule_refresh_data() -> None:
    findings = _collect_resource_refresh_constructor_findings()

    assert not findings, (
        "Migrated resource-refresh BuffXLogic files directly construct "
        "ScheduleRefreshData:\n"
        + "\n".join(f"- {finding}" for finding in findings)
    )


def test_resource_refresh_command_guardrail_reports_constructor_regressions() -> None:
    source = (
        "from zsim.sim_progress.data_struct.sp_update_data import ScheduleRefreshData\n"
        "from zsim.sim_progress.data_struct.sp_update_data import ScheduleRefreshData as Refresh\n"
        "import zsim.sim_progress.data_struct.sp_update_data as sp_update_data\n"
        "def bad():\n"
        "    ScheduleRefreshData(sp_target=('a',), sp_value=1)\n"
        "    Refresh(decibel_target=('b',), decibel_value=2)\n"
        "    sp_update_data.ScheduleRefreshData(sp_value=3)\n"
    )
    path = BUFF_XLOGIC_ROOT / "_resource_refresh_fixture.py"

    findings = _collect_schedule_refresh_constructor_findings_from_source(path, source)

    assert len(findings) == 3
    assert any("ScheduleRefreshData(...)" in finding for finding in findings)
    assert any("Refresh(...)" in finding for finding in findings)
    assert any(
        "sp_update_data.ScheduleRefreshData(...)" in finding
        for finding in findings
    )


def test_resource_refresh_command_checkpoint_matches_guardrail_scope() -> None:
    with RESOURCE_REFRESH_COMMAND_CHECKPOINT_PATH.open(encoding="utf-8") as handle:
        checkpoint = json.load(handle)

    selected_files = {entry["path"] for entry in checkpoint["selectedFiles"]}
    helper_boundaries = {
        boundary["name"] for boundary in checkpoint["helperBoundaries"]
    }
    blocked_patterns = set(checkpoint["blockedPatterns"])
    preserved_guardrail_families = set(checkpoint["preservedGuardrailFamilies"])
    exclusions = {family["name"] for family in checkpoint["exclusions"]}

    assert checkpoint["schemaVersion"] == "zsim-resource-refresh-command-checkpoint.v1"
    assert checkpoint["storyId"] == "US-006"
    assert selected_files == {
        path.relative_to(PROJECT_ROOT).as_posix()
        for path in RESOURCE_REFRESH_COMMAND_FILES
    }
    assert {
        "ResourceRefreshCommandPort.publish_refresh",
        "ScheduledEventEmitterProvider",
        "ScheduledEventEmitter.emit_scheduled",
    } <= helper_boundaries
    assert {
        "direct ScheduleRefreshData(...) construction",
        "raw record.event_list scheduled queue access",
        "raw schedule_data.event_list scheduled queue access",
        "legacy event_list request through Buff preparation",
        "long-lived cached ScheduleDispatchPort adapter",
    } <= blocked_patterns
    assert {
        "P2D raw event_list",
        "P2D event-list preparation",
        "P2D cached dispatch adapter",
        "trigger tuple",
        "active-view",
        "Calculator reader",
        "enemy helper",
        "frozen-edge equipment/template",
        "event/preload",
        "record/template cache",
    } <= preserved_guardrail_families
    assert {
        "DecibelManager non-XLogic",
        "copied-output",
        "trigger tuple",
        "frozen-edge equipment/template",
        "active-view calculator",
        "dot/debuff runtime-state",
        "anomaly-map",
        "lifecycle",
        "main-loop",
        "broad preparation/template",
    } <= exclusions
    assert checkpoint["broadDeletionReadiness"] == {
        "find_exist_buff_dict": False,
        "find_equipper": False,
        "get_prepared": False,
        "oldBuffContainerDeletion": False,
    }
    assert checkpoint["validation"] == [
        "uv run pytest tests/simulator/test_xstart_sp_refresh_dispatch.py tests/simulator/test_xhit_sp_refresh_dispatch.py tests/simulator/test_slice_of_time_extra_resources_dispatch.py tests/simulator/test_migrated_p2d_scheduled_publish_guardrail.py tests/simulator/test_buff_raw_container_guardrail.py -q",
        "uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events",
        "uv run python scripts/run_buff_refactor_validation.py --typecheck-profile runtime-dependency-zero --runtime-dependency-expected-zero",
    ]


def test_migrated_p2d_guardrail_reports_raw_queue_and_discovery_findings() -> None:
    source = (
        "from zsim.sim_progress.Buff.JudgeTools.FindMain import find_event_list\n"
        "def publish(record, schedule_data):\n"
        "    queue = JudgeTools.find_event_list(record)\n"
        "    record.event_list.append('legacy')\n"
        "    schedule_data.event_list.append('legacy')\n"
        "    check_preparation(buff_instance=buff, event_list=True)\n"
        "    get_prepared(**{'event_list': 1})\n"
        "    return queue\n"
    )
    path = BUFF_XLOGIC_ROOT / "_migrated_p2d_fixture.py"

    messages = [
        finding.message() for finding in _collect_findings_from_source(path, source)
    ]

    assert any("matched expression: from zsim.sim_progress.Buff.JudgeTools.FindMain import find_event_list" in message for message in messages)
    assert any("matched expression: JudgeTools.find_event_list(record)" in message for message in messages)
    assert any("matched expression: record.event_list.append('legacy')" in message for message in messages)
    assert any("matched expression: schedule_data.event_list.append('legacy')" in message for message in messages)
    assert any("matched expression: check_preparation(buff_instance=buff, event_list=True)" in message for message in messages)
    assert any("matched expression: get_prepared(**{'event_list': 1})" in message for message in messages)
    assert any("classification suggestion: legacy event_list discovery helper" in message for message in messages)
    assert any("classification suggestion: raw record.event_list scheduled queue access" in message for message in messages)
    assert any("classification suggestion: raw schedule_data.event_list scheduled queue access" in message for message in messages)
    assert any("next action: publish through ScheduleDispatchPort" in message for message in messages)


def test_migrated_p2d_guardrail_blocks_cached_dispatch_adapter_assignments() -> None:
    source = (
        "class BadProducer:\n"
        "    class_dispatch_port = create_schedule_dispatch_port(sim_instance=sim)\n"
        "    def __init__(self, record):\n"
        "        self.cached_dispatch = create_schedule_dispatch_port(sim_instance=sim)\n"
        "        record.dispatch_port = self._create_dispatch_port()\n"
        "        self.record.dispatch_adapter = self._create_dispatch_port()\n"
        "    def publish(self):\n"
        "        dispatch_port = self._create_dispatch_port()\n"
        "        dispatch_port.publish_scheduled(object())\n"
    )
    path = BUFF_XLOGIC_ROOT / "_migrated_p2d_fixture.py"

    findings = _collect_findings_from_source(path, source)
    messages = [finding.message() for finding in findings]

    assert len(findings) == 4
    assert any("matched expression: class_dispatch_port" in message for message in messages)
    assert any("matched expression: self.cached_dispatch" in message for message in messages)
    assert any("matched expression: record.dispatch_port" in message for message in messages)
    assert any("matched expression: self.record.dispatch_adapter" in message for message in messages)
    assert all(
        "classification suggestion: long-lived cached ScheduleDispatchPort adapter"
        in message
        for message in messages
    )
    assert any("next action: create the ScheduleDispatchPort on demand" in message for message in messages)


def test_migrated_p2d_guardrail_uses_ast_not_text_matching() -> None:
    source = (
        "def clean(record, schedule_data):\n"
        "    '''record.event_list schedule_data.event_list.append find_event_list'''\n"
        "    # self.cached_dispatch = create_schedule_dispatch_port(sim_instance=sim)\n"
        "    dot.dynamic_dot_list.append('runtime-dot-layer')\n"
        "    dispatch_port = self._create_dispatch_port()\n"
        "    dispatch_port.publish_scheduled(object())\n"
        "    check_preparation(buff_instance=buff, event_list=False)\n"
        "    return record, schedule_data\n"
    )
    path = BUFF_XLOGIC_ROOT / "_migrated_p2d_fixture.py"

    assert _collect_findings_from_source(path, source) == []


def test_resource_refresh_command_port_boundary_avoids_raw_queue_and_cached_dispatch() -> None:
    path = SIM_PROGRESS_ROOT / "Buff" / "JudgeTools" / "PreparationContext.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    class_node = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "ResourceRefreshCommandPort"
    )

    forbidden_nodes: list[str] = []
    for node in ast.walk(class_node):
        if isinstance(node, ast.Attribute) and node.attr == "event_list":
            forbidden_nodes.append("event_list")
        if isinstance(node, ast.Name) and node.id in {
            "ScheduleDispatchPort",
            "ScheduledEvent",
            "create_schedule_dispatch_port",
        }:
            forbidden_nodes.append(node.id)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "publish_scheduled"
        ):
            forbidden_nodes.append("publish_scheduled")

    assert forbidden_nodes == []
