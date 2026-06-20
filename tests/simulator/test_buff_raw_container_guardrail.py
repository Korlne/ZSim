from __future__ import annotations

import ast
import importlib
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pytest

from scripts.run_buff_refactor_validation import (
    RUNTIME_DEPENDENCY_CATEGORIES,
    RUNTIME_DEPENDENCY_STRICT_COMMAND,
    RUNTIME_DEPENDENCY_TRACKED_PRODUCTION_FAMILIES,
    RuntimeDependencyZeroScanner,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SCANNED_PRODUCTION_FILES = (
    PROJECT_ROOT / "zsim" / "simulator" / "dataclasses.py",
    PROJECT_ROOT / "zsim" / "simulator" / "simulator_class.py",
    PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent" / "buff_runtime.py",
    PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent" / "__init__.py",
    PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent" / "runtime_command.py",
    PROJECT_ROOT / "zsim" / "sim_progress" / "Update" / "Update_Buff.py",
    PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffLoad.py",
    PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffAdd.py",
    PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffAddStrategy.py",
    PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "ScheduleBuffSettle.py",
)

SCHEDULED_EVENT_DIR = PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent"
EVENT_HANDLERS_DIR = SCHEDULED_EVENT_DIR / "event_handlers"
SCHEDULED_EVENT_RUNTIME_GUARDRAIL_FILES = (
    SCHEDULED_EVENT_DIR / "__init__.py",
    SCHEDULED_EVENT_DIR / "buff_runtime.py",
    SCHEDULED_EVENT_DIR / "runtime_command.py",
    *sorted(EVENT_HANDLERS_DIR.rglob("*.py")),
)

CALCULATOR_READ_GUARDRAIL_FILES = (
    PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent" / "Calculator.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "AliceAdditionalAbilityApBonus.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "VivianCorePassiveTrigger.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "VivianCinema6Trigger.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "LinaCoreSkillPenRatioBonus.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "BranchBladeSongCritDamageBonus.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "LighterAdditionalAbility_IceFireBonus.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "MiyabiCoreSkill_IceFire.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "QingYiAdditionalAbilityStunConvertToATK.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "CannonRotor.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "TriggerAdditionalAbilityStunBonus.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "WoodpeckerElectroSet4_NA.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "WoodpeckerElectroSet4_E_EX.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "WoodpeckerElectroSet4_CA.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "YuzuhaAdditionalAbilityAnomalyDmgBonus.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "YuzuhaAdditionalAbilityAnomalyBuildupBonus.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "Soldier0AnbyCoreSkillCritDMGBonus.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "TimeweaverDisorderDmgMul.py",
)

RAW_CONTAINER_NAMES = {
    "DYNAMIC_BUFF_DICT",
    "LOADING_BUFF_DICT",
    "_enemy_debuff_mirror",
    "_dynamic_buff",
    "_dynamic_buff_dict",
    "_exist_buff_dict",
    "_loading_buff_dict",
    "dynamic_buff",
    "dynamic_buff_dict",
    "dynamic_debuff_list",
    "enemy_debuff_mirror",
    "exist_buff_dict",
    "existbuff_dict",
    "loading_buff",
    "loading_buff_dict",
    "sub_exist_buff_dict",
}

RAW_CONTAINER_ATTRS = {
    "DYNAMIC_BUFF_DICT",
    "LOADING_BUFF_DICT",
    "_enemy_debuff_mirror",
    "_dynamic_buff",
    "_dynamic_buff_dict",
    "_exist_buff_dict",
    "_loading_buff_dict",
    "dynamic_buff",
    "dynamic_debuff_list",
    "enemy_debuff_mirror",
    "exist_buff_dict",
    "loading_buff",
}

LEGACY_RUNTIME_GETTER_NAMES = {
    "_get_context_dynamic_buff",
    "_get_context_exist_buff_dict",
    "_get_context_legacy_dynamic_buff",
    "_get_context_legacy_exist_buff_dict",
    "get_dynamic_buff",
    "get_exist_buff_dict",
    "get_legacy_dynamic_buff_dict",
    "get_legacy_exist_buff_dict",
}

SCHEDULED_RUNTIME_NAMES = RAW_CONTAINER_NAMES | LEGACY_RUNTIME_GETTER_NAMES
SCHEDULED_RUNTIME_ATTRS = RAW_CONTAINER_ATTRS | LEGACY_RUNTIME_GETTER_NAMES

TRIAGE_NEXT_ACTION = (
    "migrate to an explicit facade/runtime port, retain as documented "
    "compatibility, or block the story"
)

CALCULATOR_READ_NEXT_ACTION = (
    "migrate read-only usage to CalculatorBuffAttributeReader, retain as "
    "documented formula/compatibility snapshot, or block the story"
)

RETAINED_XLOGIC_COMPATIBILITY_SNAPSHOT_ALLOWANCE = (
    "retained XLogic compatibility snapshot read"
)

XLOGIC_ADAPTER_DIRECT_ACTIVE_VIEW = (
    "active_buff_view=self.record.dynamic_buff_list"
)
XLOGIC_ADAPTER_DIRECT_READER_CONSTRUCTION = (
    "direct CalculatorBuffAttributeReader() construction"
)
XLOGIC_ADAPTER_BROAD_JUDGE_TOOLS_FIND = "broad JudgeTools.find_* call"
XLOGIC_ADAPTER_DIRECT_TRIGGER_REGISTRY_SCAN = "direct trigger_buff_0 registry scan"

XLOGIC_ADAPTER_CALCULATOR_SERVICE_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/AliceAdditionalAbilityApBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/BranchBladeSongCritDamageBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/CannonRotor.py",
    "zsim/sim_progress/Buff/BuffXLogic/JaneCinema1APTransToDmgBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/JaneCoreSkillStrikeCritRateBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/JanePassionStateAPTransToATK.py",
    "zsim/sim_progress/Buff/BuffXLogic/LighterAdditionalAbility_IceFireBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/LinaCoreSkillPenRatioBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/MiyabiCoreSkill_IceFire.py",
    "zsim/sim_progress/Buff/BuffXLogic/QingYiAdditionalAbilityStunConvertToATK.py",
    "zsim/sim_progress/Buff/BuffXLogic/Soldier0AnbyCoreSkillCritDMGBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/TimeweaverDisorderDmgMul.py",
    "zsim/sim_progress/Buff/BuffXLogic/TriggerAdditionalAbilityStunBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/VivianCinema6Trigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/VivianCorePassiveTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_CA.py",
    "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_E_EX.py",
    "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_NA.py",
    "zsim/sim_progress/Buff/BuffXLogic/YuzuhaAdditionalAbilityAnomalyBuildupBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/YuzuhaAdditionalAbilityAnomalyDmgBonus.py",
)
XLOGIC_ADAPTER_TRIGGER_REF_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/JaneCoreSkillStrikeCritRateBonus.py",
)

XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS = {
    path: frozenset(
        {
            XLOGIC_ADAPTER_DIRECT_ACTIVE_VIEW,
            XLOGIC_ADAPTER_DIRECT_READER_CONSTRUCTION,
        }
    )
    for path in XLOGIC_ADAPTER_CALCULATOR_SERVICE_FILES
}
for path in XLOGIC_ADAPTER_TRIGGER_REF_FILES:
    XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS[path] = XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS.get(
        path, frozenset()
    ) | frozenset({XLOGIC_ADAPTER_DIRECT_TRIGGER_REGISTRY_SCAN})

SCHEDULE_BUFF_SETTLE_RETAINED_BOUNDARY = (
    "legacy ScheduleBuffSettle command-adapter internals"
)

SCHEDULE_BUFF_SETTLE_RETAINED_SIGNATURES = {
    (
        "ScheduleBuffSettle",
        "raw_container_parameter",
        "ScheduleBuffSettle(..., exist_buff_dict, ...)",
        "registry/template old-container passthrough",
    ),
    (
        "ScheduleBuffSettle",
        "raw_container_parameter",
        "ScheduleBuffSettle(..., DYNAMIC_BUFF_DICT, ...)",
        "active store old-container passthrough",
    ),
    (
        "ScheduleBuffSettle",
        "raw_container_name",
        "sub_exist_buff_dict = exist_buff_dict[char_name]",
        "registry/template old-container passthrough",
    ),
    (
        "ScheduleBuffSettle",
        "raw_container_name",
        "exist_buff_dict[char_name]",
        "registry/template old-container passthrough",
    ),
    (
        "ScheduleBuffSettle",
        "raw_container_name",
        "sub_exist_buff_dict",
        "registry/template old-container passthrough",
    ),
    (
        "ScheduleBuffSettle",
        "raw_container_name",
        "DYNAMIC_BUFF_DICT",
        "active store old-container passthrough",
    ),
    (
        "process_schedule_on_field_buff",
        "raw_container_parameter",
        "process_schedule_on_field_buff(..., sub_exist_buff_dict, ...)",
        "registry/template old-container passthrough",
    ),
    (
        "process_schedule_on_field_buff",
        "raw_container_parameter",
        "process_schedule_on_field_buff(..., DYNAMIC_BUFF_DICT, ...)",
        "active store old-container passthrough",
    ),
    (
        "process_schedule_on_field_buff",
        "raw_container_name",
        "sub_exist_buff_dict",
        "registry/template old-container passthrough",
    ),
    (
        "process_schedule_on_field_buff",
        "raw_container_name",
        "DYNAMIC_BUFF_DICT",
        "active store old-container passthrough",
    ),
    (
        "process_schedule_backend_buff",
        "raw_container_parameter",
        "process_schedule_backend_buff(..., sub_exist_buff_dict, ...)",
        "registry/template old-container passthrough",
    ),
    (
        "process_schedule_backend_buff",
        "raw_container_parameter",
        "process_schedule_backend_buff(..., DYNAMIC_BUFF_DICT, ...)",
        "active store old-container passthrough",
    ),
    (
        "process_schedule_backend_buff",
        "raw_container_name",
        "sub_exist_buff_dict",
        "registry/template old-container passthrough",
    ),
    (
        "process_schedule_backend_buff",
        "raw_container_name",
        "DYNAMIC_BUFF_DICT",
        "active store old-container passthrough",
    ),
    (
        "add_schedule_buff",
        "raw_container_parameter",
        "add_schedule_buff(..., sub_exist_buff_dict, ...)",
        "registry/template old-container passthrough",
    ),
    (
        "add_schedule_buff",
        "raw_container_parameter",
        "add_schedule_buff(..., DYNAMIC_BUFF_DICT, ...)",
        "active store old-container passthrough",
    ),
    (
        "add_schedule_buff",
        "raw_container_name",
        "sub_exist_buff_dict",
        "registry/template old-container passthrough",
    ),
    (
        "add_schedule_buff",
        "raw_container_name",
        "DYNAMIC_BUFF_DICT[characters]",
        "active store old-container passthrough",
    ),
    (
        "add_schedule_buff",
        "raw_container_attribute",
        "enemy.dynamic.dynamic_debuff_list",
        "enemy debuff mirror old-container passthrough",
    ),
}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    kind: str
    matched_expression: str
    classification_suggestion: str
    next_action: str
    context: str

    def message(self) -> str:
        return (
            f"{self.path}:{self.line}: matched expression: {self.matched_expression}; "
            f"classification suggestion: {self.classification_suggestion}; "
            f"next action: {self.next_action}"
        )


@dataclass(frozen=True)
class XLogicAdapterGuardrailFinding:
    path: str
    line: int
    kind: str
    matched_expression: str

    def message(self) -> str:
        return (
            f"{self.path}:{self.line}: matched expression: {self.matched_expression}; "
            f"forbidden migrated-file pattern: {self.kind}"
        )


class RawContainerVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source: str) -> None:
        self.path = path
        self.source = source
        self.findings: list[Finding] = []
        self._parents: list[ast.AST] = []
        self._class_stack: list[str] = []
        self._function_stack: list[str] = []

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
        try:
            self._visit_arguments(node.name, node.args)
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            self._visit_arguments(node.name, node.args)
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in RAW_CONTAINER_NAMES:
            self._add_finding(
                line=node.lineno,
                kind="raw_container_name",
                expression=self._expression_context(node),
                container=node.id,
            )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in RAW_CONTAINER_ATTRS:
            self._add_finding(
                line=node.lineno,
                kind="raw_container_attribute",
                expression=self._expression_context(node),
                container=node.attr,
            )
        self.generic_visit(node)

    def visit_keyword(self, node: ast.keyword) -> None:
        if node.arg in RAW_CONTAINER_NAMES:
            line = getattr(node.value, "lineno", 0)
            self._add_finding(
                line=line,
                kind="raw_container_keyword",
                expression=self._source_for(node),
                container=node.arg,
            )
        self.generic_visit(node)

    def _visit_arguments(self, function_name: str, args: ast.arguments) -> None:
        all_args = [
            *args.posonlyargs,
            *args.args,
            *args.kwonlyargs,
        ]
        if args.vararg is not None:
            all_args.append(args.vararg)
        if args.kwarg is not None:
            all_args.append(args.kwarg)
        for arg in all_args:
            if arg.arg in RAW_CONTAINER_NAMES:
                self._add_finding(
                    line=arg.lineno,
                    kind="raw_container_parameter",
                    expression=f"{function_name}(..., {arg.arg}, ...)",
                    container=arg.arg,
                )

    def _add_finding(
        self, *, line: int, kind: str, expression: str, container: str
    ) -> None:
        self.findings.append(
            Finding(
                path=self._relative_path(),
                line=line,
                kind=kind,
                matched_expression=self._normalize(expression),
                classification_suggestion=self._classification_for(container),
                next_action=TRIAGE_NEXT_ACTION,
                context=self._context(),
            )
        )

    def _relative_path(self) -> str:
        return self.path.relative_to(PROJECT_ROOT).as_posix()

    def _context(self) -> str:
        parts = [*self._class_stack, *self._function_stack]
        if not parts:
            return "<module>"
        return ".".join(parts)

    def _expression_context(self, node: ast.AST) -> str:
        parent = self._parents[-2] if len(self._parents) >= 2 else None
        if isinstance(parent, ast.Subscript) and parent.value is node:
            return self._source_for(parent)
        if isinstance(parent, ast.Assign):
            return self._source_for(parent)
        if isinstance(parent, ast.AnnAssign):
            return self._source_for(parent)
        return self._source_for(node)

    def _source_for(self, node: ast.AST) -> str:
        segment = ast.get_source_segment(self.source, node)
        if segment is None:
            return f"<{type(node).__name__}>"
        return self._normalize(segment)

    @staticmethod
    def _normalize(expression: str) -> str:
        return " ".join(expression.strip().split())

    @staticmethod
    def _classification_for(container: str) -> str:
        if "debuff_mirror" in container or container == "dynamic_debuff_list":
            return "enemy debuff mirror old-container passthrough"
        if container in LEGACY_RUNTIME_GETTER_NAMES:
            return "compatibility-only legacy runtime getter"
        if "LOADING" in container or "loading" in container:
            return "pending queue old-container passthrough"
        if "DYNAMIC" in container or "dynamic" in container:
            return "active store old-container passthrough"
        return "registry/template old-container passthrough"


class ScheduledEventRuntimeVisitor(RawContainerVisitor):
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            if node.name in LEGACY_RUNTIME_GETTER_NAMES:
                self._add_finding(
                    line=node.lineno,
                    kind="legacy_runtime_getter_definition",
                    expression=f"def {node.name}(...)",
                    container=node.name,
                )
            self._visit_arguments(node.name, node.args)
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            if node.name in LEGACY_RUNTIME_GETTER_NAMES:
                self._add_finding(
                    line=node.lineno,
                    kind="legacy_runtime_getter_definition",
                    expression=f"async def {node.name}(...)",
                    container=node.name,
                )
            self._visit_arguments(node.name, node.args)
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in SCHEDULED_RUNTIME_NAMES:
            self._add_finding(
                line=node.lineno,
                kind="scheduled_runtime_name",
                expression=self._expression_context(node),
                container=node.id,
            )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in SCHEDULED_RUNTIME_ATTRS:
            self._add_finding(
                line=node.lineno,
                kind="scheduled_runtime_attribute",
                expression=self._expression_context(node),
                container=node.attr,
            )
        self.generic_visit(node)

    def visit_keyword(self, node: ast.keyword) -> None:
        if node.arg in RAW_CONTAINER_NAMES:
            line = getattr(node.value, "lineno", 0)
            self._add_finding(
                line=line,
                kind="scheduled_runtime_keyword",
                expression=self._source_for(node),
                container=node.arg,
            )
        self.generic_visit(node)


class CalculatorReadVisitor(RawContainerVisitor):
    def __init__(self, path: Path, source: str) -> None:
        super().__init__(path, source)
        self._multiplier_aliases = {"MultiplierData"}

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        if module.endswith("Calculator"):
            for alias in node.names:
                if alias.name == "MultiplierData":
                    self._multiplier_aliases.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if self._is_multiplier_constructor(node.func):
            self._add_calculator_finding(
                line=node.lineno,
                kind="calculator_multiplier_snapshot",
                expression=self._source_for(node),
                classification_suggestion="direct MultiplierData compatibility snapshot",
            )
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id == "dynamic_buff_list" and isinstance(node.ctx, ast.Load):
            self._add_calculator_finding(
                line=node.lineno,
                kind="calculator_dynamic_buff_list_read",
                expression=self._expression_context(node),
                classification_suggestion="raw dynamic_buff_list attribute-read input",
            )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr == "dynamic_buff_list" and isinstance(node.ctx, ast.Load):
            self._add_calculator_finding(
                line=node.lineno,
                kind="calculator_dynamic_buff_list_read",
                expression=self._expression_context(node),
                classification_suggestion="raw dynamic_buff_list attribute-read input",
            )
        self.generic_visit(node)

    def visit_keyword(self, node: ast.keyword) -> None:
        self.generic_visit(node)

    def _is_multiplier_constructor(self, func: ast.AST) -> bool:
        if isinstance(func, ast.Name):
            return func.id in self._multiplier_aliases
        if isinstance(func, ast.Attribute):
            return func.attr in self._multiplier_aliases
        return False

    def _add_calculator_finding(
        self,
        *,
        line: int,
        kind: str,
        expression: str,
        classification_suggestion: str,
    ) -> None:
        self.findings.append(
            Finding(
                path=self._relative_path(),
                line=line,
                kind=kind,
                matched_expression=self._normalize(expression),
                classification_suggestion=classification_suggestion,
                next_action=CALCULATOR_READ_NEXT_ACTION,
                context=self._context(),
            )
        )


def _collect_findings_from_source(path: Path, source: str) -> list[Finding]:
    tree = ast.parse(source, filename=str(path))
    visitor = RawContainerVisitor(path, source)
    visitor.visit(tree)
    return visitor.findings


def _collect_findings() -> list[Finding]:
    findings: list[Finding] = []
    for path in SCANNED_PRODUCTION_FILES:
        source = path.read_text(encoding="utf-8")
        findings.extend(_collect_findings_from_source(path, source))
    return findings


def _collect_scheduled_runtime_findings_from_source(
    path: Path, source: str
) -> list[Finding]:
    tree = ast.parse(source, filename=str(path))
    visitor = ScheduledEventRuntimeVisitor(path, source)
    visitor.visit(tree)
    return visitor.findings


def _collect_scheduled_runtime_findings() -> list[Finding]:
    findings: list[Finding] = []
    for path in SCHEDULED_EVENT_RUNTIME_GUARDRAIL_FILES:
        source = path.read_text(encoding="utf-8")
        findings.extend(_collect_scheduled_runtime_findings_from_source(path, source))
    return findings


def _collect_calculator_read_findings_from_source(
    path: Path, source: str
) -> list[Finding]:
    tree = ast.parse(source, filename=str(path))
    visitor = CalculatorReadVisitor(path, source)
    visitor.visit(tree)
    return visitor.findings


def _collect_calculator_read_findings() -> list[Finding]:
    findings: list[Finding] = []
    for path in CALCULATOR_READ_GUARDRAIL_FILES:
        source = path.read_text(encoding="utf-8")
        findings.extend(_collect_calculator_read_findings_from_source(path, source))
    return findings


def _allowance_for(finding: Finding) -> str | None:
    path = finding.path
    context = finding.context
    if path == "zsim/simulator/dataclasses.py":
        return "core Load/Schedule/GlobalStats container ownership"
    if path == "zsim/sim_progress/ScheduledEvent/buff_runtime.py":
        return "legacy facade adapter internals"
    if path == "zsim/simulator/simulator_class.py":
        if context == "Simulator.__init_data_struct":
            return "BuffRuntimeState owner construction"
        if context == "Simulator._create_buff_runtime_facade":
            return "legacy facade construction"
        if context == "Simulator.main_loop":
            return "retained ScheduledEvent main-loop boundary"
    if path == "zsim/sim_progress/Buff/BuffLoad.py":
        return "retained BuffLoadLoop trigger judgement and pending queue population"
    if path == "zsim/sim_progress/Buff/BuffAdd.py":
        if context == "buff_add":
            return "legacy buff_add pending-to-active compatibility path"
        if context == "add_debuff_to_enemy":
            return "legacy buff_add enemy debuff mirror sync"
    if path == "zsim/sim_progress/Buff/ScheduleBuffSettle.py":
        signature = (
            context,
            finding.kind,
            finding.matched_expression,
            finding.classification_suggestion,
        )
        if signature in SCHEDULE_BUFF_SETTLE_RETAINED_SIGNATURES:
            return SCHEDULE_BUFF_SETTLE_RETAINED_BOUNDARY
    if path == "zsim/sim_progress/Update/Update_Buff.py":
        if context == "update_time_related_effect":
            return "retained Update_Buff time-effect compatibility wrapper"
        if context == "update_buff":
            return "retained Update_Buff active-store traversal and no-facade fallback"
        if context == "KickOutBuff":
            return "legacy KickOutBuff active-removal compatibility path"
    if path == "zsim/sim_progress/ScheduledEvent/__init__.py":
        return "retained ScheduledEvent raw-container boundary"
    if path == "zsim/sim_progress/ScheduledEvent/runtime_command.py":
        return "RuntimeCommandPort compatibility reads"
    return None


def _scheduled_runtime_allowance_for(finding: Finding) -> str | None:
    path = finding.path
    context = finding.context
    expression = finding.matched_expression

    if path == "zsim/sim_progress/ScheduledEvent/__init__.py":
        if context == "ScheduledEvent.__init__":
            return "retained ScheduledEvent constructor setup"
        if context == "ScheduledEvent._create_runtime_ports":
            return "runtime view / command adapter setup"
        if context == "ScheduledEvent.event_start" and expression in {
            "dynamic_buff=self.data.dynamic_buff",
            "self.data.dynamic_buff",
        }:
            return "retained SPUpdateData runtime read candidate"

    if path == "zsim/sim_progress/ScheduledEvent/buff_runtime.py":
        return "runtime view / facade adapter internals"

    if path == "zsim/sim_progress/ScheduledEvent/runtime_command.py":
        return "existing RuntimeCommandPort adapter reads"

    if path == "zsim/sim_progress/ScheduledEvent/event_handlers/handlers/skill.py":
        if context == "SkillEventHandler._calculate_damage":
            return "runtime view passed to Calculator formula boundary"

    if path in {
        "zsim/sim_progress/ScheduledEvent/event_handlers/handlers/abloom.py",
        "zsim/sim_progress/ScheduledEvent/event_handlers/handlers/anomaly.py",
        "zsim/sim_progress/ScheduledEvent/event_handlers/handlers/disorder.py",
        "zsim/sim_progress/ScheduledEvent/event_handlers/handlers/polarity_disorder.py",
    }:
        if context.endswith(".handle"):
            return "runtime view passed to anomaly formula boundary"

    return None


def _calculator_read_allowance_for(finding: Finding) -> str | None:
    path = finding.path
    context = finding.context

    if path == "zsim/sim_progress/ScheduledEvent/Calculator.py":
        if (
            context == "Calculator.__init__"
            and finding.kind == "calculator_multiplier_snapshot"
        ):
            return "Calculator formula snapshot construction"

    if path in {
        "zsim/sim_progress/Buff/BuffXLogic/BranchBladeSongCritDamageBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/TimeweaverDisorderDmgMul.py",
    }:
        if (
            context.endswith(".special_judge_logic")
            and finding.kind == "calculator_dynamic_buff_list_read"
        ):
            return "migrated attribute-reader active_buff_view input"

    if path.startswith("zsim/sim_progress/Buff/BuffXLogic/"):
        return RETAINED_XLOGIC_COMPATIBILITY_SNAPSHOT_ALLOWANCE

    return None


def _allowance_counts(findings: list[Finding]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for finding in findings:
        allowance = _allowance_for(finding)
        if allowance is not None:
            counts[allowance] += 1
    return counts


def _scheduled_runtime_allowance_counts(findings: list[Finding]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for finding in findings:
        allowance = _scheduled_runtime_allowance_for(finding)
        if allowance is not None:
            counts[allowance] += 1
    return counts


def _calculator_read_allowance_counts(findings: list[Finding]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for finding in findings:
        allowance = _calculator_read_allowance_for(finding)
        if allowance is not None:
            counts[allowance] += 1
    return counts


EXPECTED_RETAINED_REFERENCE_CEILINGS = {
    "core Load/Schedule/GlobalStats container ownership": 16,
    "BuffRuntimeState owner construction": 4,
    "legacy facade adapter internals": 59,
    "legacy facade construction": 8,
    "retained ScheduledEvent main-loop boundary": 2,
    "retained BuffLoadLoop trigger judgement and pending queue population": 41,
    "legacy buff_add pending-to-active compatibility path": 10,
    "legacy buff_add enemy debuff mirror sync": 3,
    SCHEDULE_BUFF_SETTLE_RETAINED_BOUNDARY: 26,
    "retained Update_Buff time-effect compatibility wrapper": 5,
    "retained Update_Buff active-store traversal and no-facade fallback": 7,
    "legacy KickOutBuff active-removal compatibility path": 5,
    "retained ScheduledEvent raw-container boundary": 21,
    "RuntimeCommandPort compatibility reads": 11,
}

EXPECTED_SCHEDULED_RUNTIME_REFERENCE_CEILINGS = {
    "retained ScheduledEvent constructor setup": 16,
    "runtime view / command adapter setup": 6,
    "retained SPUpdateData runtime read candidate": 2,
    "runtime view / facade adapter internals": 63,
    "existing RuntimeCommandPort adapter reads": 11,
    "runtime view passed to Calculator formula boundary": 3,
    "runtime view passed to anomaly formula boundary": 4,
}

EXPECTED_CALCULATOR_READ_RETAINED_SNAPSHOT_COUNTS = {
    # US-001 freezes the US-013 retained snapshot backlog by file. Later
    # migration stories may lower these counts with focused evidence.
    "zsim/sim_progress/Buff/BuffXLogic/AliceAdditionalAbilityApBonus.py": 2,
    "zsim/sim_progress/Buff/BuffXLogic/CannonRotor.py": 1,
    "zsim/sim_progress/Buff/BuffXLogic/LighterAdditionalAbility_IceFireBonus.py": 1,
    "zsim/sim_progress/Buff/BuffXLogic/MiyabiCoreSkill_IceFire.py": 1,
    "zsim/sim_progress/Buff/BuffXLogic/QingYiAdditionalAbilityStunConvertToATK.py": 1,
    "zsim/sim_progress/Buff/BuffXLogic/Soldier0AnbyCoreSkillCritDMGBonus.py": 1,
    "zsim/sim_progress/Buff/BuffXLogic/TriggerAdditionalAbilityStunBonus.py": 1,
    "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_CA.py": 1,
    "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_E_EX.py": 1,
    "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_NA.py": 1,
    "zsim/sim_progress/Buff/BuffXLogic/YuzuhaAdditionalAbilityAnomalyBuildupBonus.py": 1,
    "zsim/sim_progress/Buff/BuffXLogic/YuzuhaAdditionalAbilityAnomalyDmgBonus.py": 1,
}

EXPECTED_CALCULATOR_READ_REFERENCE_CEILINGS = {
    "Calculator formula snapshot construction": 1,
    "migrated attribute-reader active_buff_view input": 2,
    RETAINED_XLOGIC_COMPATIBILITY_SNAPSHOT_ALLOWANCE: sum(
        EXPECTED_CALCULATOR_READ_RETAINED_SNAPSHOT_COUNTS.values()
    ),
}


def _calculator_read_retained_snapshot_counts(
    findings: list[Finding],
) -> Counter[str]:
    counts: Counter[str] = Counter()
    for finding in findings:
        if (
            _calculator_read_allowance_for(finding)
            == RETAINED_XLOGIC_COMPATIBILITY_SNAPSHOT_ALLOWANCE
        ):
            counts[finding.path] += 1
    return counts


def _calculator_read_retained_snapshot_expansions(
    findings: list[Finding],
) -> dict[str, int]:
    counts = _calculator_read_retained_snapshot_counts(findings)
    return {
        path: count
        for path, count in counts.items()
        if count > EXPECTED_CALCULATOR_READ_RETAINED_SNAPSHOT_COUNTS.get(path, 0)
    }


def _is_calculator_reader_constructor(func: ast.expr) -> bool:
    if isinstance(func, ast.Name):
        return func.id == "CalculatorBuffAttributeReader"
    if isinstance(func, ast.Attribute):
        return func.attr == "CalculatorBuffAttributeReader"
    return False


def _is_judge_tools_find_call(func: ast.expr) -> bool:
    return (
        isinstance(func, ast.Attribute)
        and func.attr.startswith("find_")
        and isinstance(func.value, ast.Name)
        and func.value.id == "JudgeTools"
    )


def _is_find_exist_buff_dict_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    if isinstance(node.func, ast.Name):
        return node.func.id == "find_exist_buff_dict"
    return (
        isinstance(node.func, ast.Attribute)
        and node.func.attr == "find_exist_buff_dict"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "JudgeTools"
    )


def _is_direct_trigger_registry_scan(node: ast.AST) -> bool:
    if not isinstance(node, ast.Subscript):
        return False
    if not _is_find_exist_buff_dict_call(node.value):
        return False
    return not isinstance(node.slice, ast.Constant)


def _is_self_record_dynamic_buff_list(node: ast.expr) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "dynamic_buff_list"
        and isinstance(node.value, ast.Attribute)
        and node.value.attr == "record"
        and isinstance(node.value.value, ast.Name)
        and node.value.value.id == "self"
    )


def _adapter_source_for(source: str, node: ast.AST) -> str:
    segment = ast.get_source_segment(source, node)
    if segment is None:
        return f"<{type(node).__name__}>"
    return " ".join(segment.strip().split())


def _collect_xlogic_adapter_guardrail_findings_from_source(
    path: Path,
    source: str,
    forbidden_kinds: frozenset[str],
) -> list[XLogicAdapterGuardrailFinding]:
    findings: list[XLogicAdapterGuardrailFinding] = []
    tree = ast.parse(source, filename=str(path))
    relative_path = path.relative_to(PROJECT_ROOT).as_posix()

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Subscript)
            and XLOGIC_ADAPTER_DIRECT_TRIGGER_REGISTRY_SCAN in forbidden_kinds
            and _is_direct_trigger_registry_scan(node)
        ):
            findings.append(
                XLogicAdapterGuardrailFinding(
                    path=relative_path,
                    line=node.lineno,
                    kind=XLOGIC_ADAPTER_DIRECT_TRIGGER_REGISTRY_SCAN,
                    matched_expression=_adapter_source_for(source, node),
                )
            )

        if not isinstance(node, ast.Call):
            continue

        if (
            XLOGIC_ADAPTER_DIRECT_READER_CONSTRUCTION in forbidden_kinds
            and _is_calculator_reader_constructor(node.func)
        ):
            findings.append(
                XLogicAdapterGuardrailFinding(
                    path=relative_path,
                    line=node.lineno,
                    kind=XLOGIC_ADAPTER_DIRECT_READER_CONSTRUCTION,
                    matched_expression=_adapter_source_for(source, node),
                )
            )

        if (
            XLOGIC_ADAPTER_BROAD_JUDGE_TOOLS_FIND in forbidden_kinds
            and _is_judge_tools_find_call(node.func)
        ):
            findings.append(
                XLogicAdapterGuardrailFinding(
                    path=relative_path,
                    line=node.lineno,
                    kind=XLOGIC_ADAPTER_BROAD_JUDGE_TOOLS_FIND,
                    matched_expression=_adapter_source_for(source, node),
                )
            )

        if XLOGIC_ADAPTER_DIRECT_ACTIVE_VIEW in forbidden_kinds:
            for keyword in node.keywords:
                if (
                    keyword.arg == "active_buff_view"
                    and _is_self_record_dynamic_buff_list(keyword.value)
                ):
                    findings.append(
                        XLogicAdapterGuardrailFinding(
                            path=relative_path,
                            line=keyword.value.lineno,
                            kind=XLOGIC_ADAPTER_DIRECT_ACTIVE_VIEW,
                            matched_expression=_adapter_source_for(source, keyword),
                        )
                    )

    return findings


def _collect_xlogic_adapter_guardrail_findings() -> list[XLogicAdapterGuardrailFinding]:
    findings: list[XLogicAdapterGuardrailFinding] = []
    for relative_path, forbidden_kinds in XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS.items():
        path = PROJECT_ROOT / relative_path
        findings.extend(
            _collect_xlogic_adapter_guardrail_findings_from_source(
                path,
                path.read_text(encoding="utf-8"),
                forbidden_kinds,
            )
        )
    return findings


def test_runtime_dependency_zero_scanner_reports_required_schema_and_families() -> None:
    report = RuntimeDependencyZeroScanner(PROJECT_ROOT).build_report(
        expected_zero=True
    )

    assert report["schemaVersion"] == "zsim-runtime-dependency-zero.v1"
    assert report["profile"] == "runtime-dependency-zero"
    assert report["strictExpectedZero"] is True
    assert report["strictCommand"] == RUNTIME_DEPENDENCY_STRICT_COMMAND
    assert report["categorySchema"] == list(RUNTIME_DEPENDENCY_CATEGORIES)
    assert set(report["categories"]) == set(RUNTIME_DEPENDENCY_CATEGORIES)
    assert (
        set(RUNTIME_DEPENDENCY_TRACKED_PRODUCTION_FAMILIES)
        <= set(report["trackedProductionFamilies"])
    )
    assert (
        set(RUNTIME_DEPENDENCY_TRACKED_PRODUCTION_FAMILIES)
        <= set(report["families"])
    )
    assert report["productionRuntimeTotal"] == 0
    assert report["productionRuntimeFamilies"] == []
    assert report["findingCount"] > 0


def test_runtime_dependency_zero_scanner_classifies_reference_categories() -> None:
    scanner = RuntimeDependencyZeroScanner(PROJECT_ROOT)
    fixture_source = (
        "# DYNAMIC_BUFF_DICT comment only\n"
        "class UsesPort(RuntimeCommandPort):\n"
        "    def run(self, exist_buff_dict):\n"
        "        return exist_buff_dict\n"
    )

    production_findings = scanner.scan_source("zsim/simulator/_fixture.py", fixture_source)
    test_findings = scanner.scan_source("tests/simulator/_fixture.py", fixture_source)
    docs_findings = scanner.scan_source("docs/_fixture.md", "LegacyBuffRuntimeFacade\n")
    migration_findings = scanner.scan_source(
        "scripts/run_buff_refactor_validation.py",
        "LegacyBuffRuntimeReadAdapter\n",
    )
    runtime_owner_findings = scanner.scan_source(
        "zsim/sim_progress/Buff/BuffLoad.py",
        "def load(exist_buff_dict, LOADING_BUFF_DICT):\n"
        "    return exist_buff_dict, LOADING_BUFF_DICT\n",
    )
    api_findings = scanner.scan_source(
        "zsim/api_src/_fixture.py",
        "def leak(sim_instance):\n"
        "    return sim_instance.load_data.exist_buff_dict\n",
    )

    assert "production runtime" in {
        finding.category for finding in production_findings
    }
    assert "comment" in {finding.category for finding in production_findings}
    assert "stable contract name" in {
        finding.category for finding in production_findings
    }
    assert {finding.category for finding in test_findings} == {
        "comment",
        "stable contract name",
        "test-only",
    }
    assert {finding.category for finding in docs_findings} == {"docs-only"}
    assert {finding.category for finding in migration_findings} == {"migration-only"}
    assert {finding.category for finding in runtime_owner_findings} == {
        "migration-only"
    }
    assert "production runtime" in {
        finding.category for finding in api_findings
    }


def test_raw_old_container_passthroughs_stay_inside_retained_boundaries() -> None:
    findings = _collect_findings()
    disallowed = [finding for finding in findings if _allowance_for(finding) is None]

    assert not disallowed, (
        "Raw old-container guardrail found disallowed production uses:\n"
        + "\n".join(f"- {finding.message()}" for finding in disallowed)
    )


def test_raw_old_container_retained_boundary_counts_do_not_expand() -> None:
    findings = _collect_findings()
    counts = _allowance_counts(findings)
    expanded = {
        allowance: count
        for allowance, count in counts.items()
        if count > EXPECTED_RETAINED_REFERENCE_CEILINGS[allowance]
    }

    assert not expanded, (
        "Raw old-container guardrail found widened retained-boundary references:\n"
        + "\n".join(
            f"- {allowance}: {count} > {EXPECTED_RETAINED_REFERENCE_CEILINGS[allowance]}"
            for allowance, count in sorted(expanded.items())
        )
    )


def test_main_loop_keeps_buffload_pending_queue_behind_runtime_api() -> None:
    findings = [
        finding
        for finding in _collect_findings()
        if finding.path == "zsim/simulator/simulator_class.py"
        and finding.context == "Simulator.main_loop"
    ]

    assert all(
        finding.classification_suggestion != "pending queue old-container passthrough"
        for finding in findings
    )


def test_update_buff_active_sweep_is_runtime_owned_without_kickout_fallback() -> None:
    findings = [
        finding
        for finding in _collect_findings()
        if finding.path == "zsim/sim_progress/Update/Update_Buff.py"
    ]

    assert all(finding.context not in {"update_buff", "KickOutBuff"} for finding in findings)

    report = RuntimeDependencyZeroScanner(PROJECT_ROOT).build_report(expected_zero=False)
    assert report["families"]["Update_Buff no-facade fallback"]["production runtime"] == 0


def test_retained_buff_add_module_is_migration_only_without_raw_activation() -> None:
    buff_add_module = importlib.import_module("zsim.sim_progress.Buff.BuffAdd")

    with pytest.raises(RuntimeError, match="migration-only"):
        getattr(buff_add_module, "buff_add")()
    with pytest.raises(RuntimeError, match="migration-only"):
        getattr(buff_add_module, "add_debuff_to_enemy")()

    findings = [
        finding
        for finding in _collect_findings()
        if finding.path == "zsim/sim_progress/Buff/BuffAdd.py"
    ]
    assert findings == []

    report = RuntimeDependencyZeroScanner(PROJECT_ROOT).build_report(expected_zero=False)
    assert report["families"]["retained BuffAdd.py activation"]["production runtime"] == 0


def test_raw_old_container_guardrail_failure_message_includes_triage_fields() -> None:
    source = (
        "def spread(sim_instance):\n"
        "    return handler(sim_instance.global_stats.DYNAMIC_BUFF_DICT)\n"
    )
    path = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffXLogic" / "_fixture.py"
    findings = _collect_findings_from_source(path, source)

    assert len(findings) == 1
    message = findings[0].message()
    assert "zsim/sim_progress/Buff/BuffXLogic/_fixture.py:2" in message
    assert "matched expression: sim_instance.global_stats.DYNAMIC_BUFF_DICT" in message
    assert "classification suggestion: active store old-container passthrough" in message
    assert f"next action: {TRIAGE_NEXT_ACTION}" in message


def test_raw_old_container_guardrail_classifies_enemy_debuff_mirror_passthrough() -> None:
    source = (
        "def spread(enemy):\n"
        "    return handler(enemy.dynamic.dynamic_debuff_list)\n"
    )
    path = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffXLogic" / "_fixture.py"
    findings = _collect_findings_from_source(path, source)

    assert len(findings) == 1
    message = findings[0].message()
    assert "zsim/sim_progress/Buff/BuffXLogic/_fixture.py:2" in message
    assert "matched expression: enemy.dynamic.dynamic_debuff_list" in message
    assert "classification suggestion: enemy debuff mirror old-container passthrough" in message
    assert f"next action: {TRIAGE_NEXT_ACTION}" in message


def test_raw_old_container_guardrail_uses_ast_not_text_matching() -> None:
    source = (
        "def clean():\n"
        "    '''DYNAMIC_BUFF_DICT LOADING_BUFF_DICT exist_buff_dict dynamic_buff loading_buff'''\n"
        "    # ScheduleData.dynamic_buff remains a historical note only.\n"
        "    return None\n"
    )
    path = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffXLogic" / "_fixture.py"

    assert _collect_findings_from_source(path, source) == []


def test_raw_old_container_guardrail_classifies_schedule_buff_settle_boundary() -> None:
    findings = [
        finding
        for finding in _collect_findings()
        if finding.path == "zsim/sim_progress/Buff/ScheduleBuffSettle.py"
    ]
    allowances = {_allowance_for(finding) for finding in findings}
    classifications = {finding.classification_suggestion for finding in findings}

    assert findings
    assert allowances == {SCHEDULE_BUFF_SETTLE_RETAINED_BOUNDARY}
    assert "active store old-container passthrough" in classifications
    assert "enemy debuff mirror old-container passthrough" in classifications
    assert (
        len(findings)
        == EXPECTED_RETAINED_REFERENCE_CEILINGS[SCHEDULE_BUFF_SETTLE_RETAINED_BOUNDARY]
    )


def test_raw_old_container_guardrail_blocks_new_schedule_buff_settle_raw_write() -> None:
    source = (
        "def unexpected_schedule_write(DYNAMIC_BUFF_DICT, buff):\n"
        "    DYNAMIC_BUFF_DICT['enemy'].append(buff)\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "ScheduleBuffSettle.py"
    )
    findings = _collect_findings_from_source(path, source)
    disallowed = [finding for finding in findings if _allowance_for(finding) is None]

    assert disallowed
    write_finding = next(finding for finding in disallowed if finding.line == 2)
    message = write_finding.message()
    assert "zsim/sim_progress/Buff/ScheduleBuffSettle.py:2" in message
    assert "matched expression: DYNAMIC_BUFF_DICT['enemy']" in message
    assert "classification suggestion: active store old-container passthrough" in message
    assert f"next action: {TRIAGE_NEXT_ACTION}" in message


def test_raw_old_container_guardrail_classifies_buff_add_strategy_boundary() -> None:
    findings = [
        finding
        for finding in _collect_findings()
        if finding.path == "zsim/sim_progress/Buff/BuffAddStrategy.py"
    ]

    assert findings == []


def test_raw_old_container_guardrail_blocks_new_buff_add_strategy_pending_write() -> None:
    source = (
        "def let_buff_start(sim_instance, buff):\n"
        "    sim_instance.load_data.LOADING_BUFF_DICT['enemy'].append(buff)\n"
    )
    path = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffAddStrategy.py"
    findings = _collect_findings_from_source(path, source)
    disallowed = [finding for finding in findings if _allowance_for(finding) is None]

    assert len(disallowed) == 1
    message = disallowed[0].message()
    assert "zsim/sim_progress/Buff/BuffAddStrategy.py:2" in message
    assert "classification suggestion: pending queue old-container passthrough" in message
    assert f"next action: {TRIAGE_NEXT_ACTION}" in message


def test_scheduled_event_raw_runtime_access_stays_inside_allowlist() -> None:
    findings = _collect_scheduled_runtime_findings()
    disallowed = [
        finding
        for finding in findings
        if _scheduled_runtime_allowance_for(finding) is None
    ]

    assert not disallowed, (
        "ScheduledEvent raw runtime guardrail found disallowed production uses:\n"
        + "\n".join(f"- {finding.message()}" for finding in disallowed)
    )


def test_scheduled_event_context_and_base_do_not_define_legacy_raw_getters() -> None:
    forbidden_contexts = {
        "EventContext.get_legacy_dynamic_buff_dict",
        "EventContext.get_legacy_exist_buff_dict",
        "EventContext.get_dynamic_buff",
        "EventContext.get_exist_buff_dict",
        "BaseEventHandler._get_context_legacy_dynamic_buff",
        "BaseEventHandler._get_context_legacy_exist_buff_dict",
        "BaseEventHandler._get_context_dynamic_buff",
        "BaseEventHandler._get_context_exist_buff_dict",
    }
    findings = _collect_scheduled_runtime_findings()
    retained = [
        finding
        for finding in findings
        if finding.kind == "legacy_runtime_getter_definition"
        and finding.context in forbidden_contexts
    ]

    assert not retained, (
        "ScheduledEvent production context/base legacy raw getter definitions remain:\n"
        + "\n".join(f"- {finding.message()}" for finding in retained)
    )


def test_scheduled_event_raw_runtime_retained_counts_do_not_expand() -> None:
    findings = _collect_scheduled_runtime_findings()
    counts = _scheduled_runtime_allowance_counts(findings)
    expanded = {
        allowance: count
        for allowance, count in counts.items()
        if count > EXPECTED_SCHEDULED_RUNTIME_REFERENCE_CEILINGS[allowance]
    }

    assert not expanded, (
        "ScheduledEvent raw runtime guardrail found widened retained references:\n"
        + "\n".join(
            f"- {allowance}: {count} > "
            f"{EXPECTED_SCHEDULED_RUNTIME_REFERENCE_CEILINGS[allowance]}"
            for allowance, count in sorted(expanded.items())
        )
    )


def test_scheduled_event_raw_runtime_guardrail_failure_message_includes_triage_fields() -> None:
    source = (
        "class NewHandler:\n"
        "    def handle(self, context):\n"
        "        return context.get_dynamic_buff()\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "ScheduledEvent"
        / "event_handlers"
        / "handlers"
        / "_fixture.py"
    )
    findings = _collect_scheduled_runtime_findings_from_source(path, source)

    assert len(findings) == 1
    message = findings[0].message()
    assert (
        "zsim/sim_progress/ScheduledEvent/event_handlers/handlers/_fixture.py:3"
        in message
    )
    assert "matched expression: context.get_dynamic_buff" in message
    assert "classification suggestion: compatibility-only legacy runtime getter" in message
    assert f"next action: {TRIAGE_NEXT_ACTION}" in message


def test_scheduled_event_raw_runtime_guardrail_uses_ast_not_text_matching() -> None:
    source = (
        "def clean():\n"
        "    '''get_dynamic_buff get_legacy_dynamic_buff_dict dynamic_buff loading_buff'''\n"
        "    # context.get_exist_buff_dict() remains a historical note only.\n"
        "    return None\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "ScheduledEvent"
        / "event_handlers"
        / "handlers"
        / "_fixture.py"
    )

    assert _collect_scheduled_runtime_findings_from_source(path, source) == []


def test_calculator_read_surfaces_stay_inside_allowlist() -> None:
    findings = _collect_calculator_read_findings()
    disallowed = [
        finding
        for finding in findings
        if _calculator_read_allowance_for(finding) is None
    ]

    assert not disallowed, (
        "Calculator-read guardrail found disallowed production uses:\n"
        + "\n".join(f"- {finding.message()}" for finding in disallowed)
    )


def test_calculator_read_retained_counts_do_not_expand() -> None:
    findings = _collect_calculator_read_findings()
    counts = _calculator_read_allowance_counts(findings)
    expanded = {
        allowance: count
        for allowance, count in counts.items()
        if count > EXPECTED_CALCULATOR_READ_REFERENCE_CEILINGS[allowance]
    }

    assert not expanded, (
        "Calculator-read guardrail found widened retained references:\n"
        + "\n".join(
            f"- {allowance}: {count} > "
            f"{EXPECTED_CALCULATOR_READ_REFERENCE_CEILINGS[allowance]}"
            for allowance, count in sorted(expanded.items())
        )
    )


def test_calculator_read_retained_snapshot_backlog_files_do_not_expand() -> None:
    findings = _collect_calculator_read_findings()
    expanded = _calculator_read_retained_snapshot_expansions(findings)

    assert not expanded, (
        "Calculator-read guardrail found widened retained snapshot files:\n"
        + "\n".join(
            f"- {path}: {count} > "
            f"{EXPECTED_CALCULATOR_READ_RETAINED_SNAPSHOT_COUNTS.get(path, 0)}"
            for path, count in sorted(expanded.items())
        )
    )


def test_xlogic_adapter_migrated_files_do_not_reintroduce_legacy_inputs() -> None:
    findings = _collect_xlogic_adapter_guardrail_findings()

    assert not findings, (
        "Migrated BuffXLogic adapter guardrail found legacy inputs:\n"
        + "\n".join(f"- {finding.message()}" for finding in findings)
    )


def test_xlogic_adapter_guardrail_flags_calculator_reader_regressions() -> None:
    source = (
        "def read(self):\n"
        "    reader = CalculatorBuffAttributeReader()\n"
        "    return reader.read_anomaly_mastery(\n"
        "        active_buff_view=self.record.dynamic_buff_list,\n"
        "    )\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "BuffXLogic"
        / "_adapter_fixture.py"
    )

    findings = _collect_xlogic_adapter_guardrail_findings_from_source(
        path,
        source,
        frozenset(
            {
                XLOGIC_ADAPTER_DIRECT_ACTIVE_VIEW,
                XLOGIC_ADAPTER_DIRECT_READER_CONSTRUCTION,
            }
        ),
    )

    assert {finding.kind for finding in findings} == {
        XLOGIC_ADAPTER_DIRECT_ACTIVE_VIEW,
        XLOGIC_ADAPTER_DIRECT_READER_CONSTRUCTION,
    }
    messages = [finding.message() for finding in findings]
    assert any("CalculatorBuffAttributeReader()" in message for message in messages)
    assert any(
        "active_buff_view=self.record.dynamic_buff_list" in message
        for message in messages
    )


def test_xlogic_adapter_guardrail_can_freeze_migrated_judgetools_find_calls() -> None:
    source = (
        "def prepare(self):\n"
        "    return JudgeTools.find_exist_buff_dict(\n"
        "        sim_instance=self.buff_instance.sim_instance,\n"
        "    )\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "BuffXLogic"
        / "_adapter_fixture.py"
    )

    findings = _collect_xlogic_adapter_guardrail_findings_from_source(
        path,
        source,
        frozenset({XLOGIC_ADAPTER_BROAD_JUDGE_TOOLS_FIND}),
    )

    assert len(findings) == 1
    message = findings[0].message()
    assert "JudgeTools.find_exist_buff_dict" in message
    assert XLOGIC_ADAPTER_BROAD_JUDGE_TOOLS_FIND in message


def test_xlogic_adapter_guardrail_flags_trigger_registry_scans() -> None:
    source = (
        "def prepare(self, operator):\n"
        "    trigger_buff_0 = JudgeTools.find_exist_buff_dict(\n"
        "        sim_instance=self.buff_instance.sim_instance,\n"
        "    )[operator]\n"
        "    return trigger_buff_0\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "BuffXLogic"
        / "_adapter_fixture.py"
    )

    findings = _collect_xlogic_adapter_guardrail_findings_from_source(
        path,
        source,
        frozenset({XLOGIC_ADAPTER_DIRECT_TRIGGER_REGISTRY_SCAN}),
    )

    assert len(findings) == 1
    message = findings[0].message()
    assert "find_exist_buff_dict" in message
    assert "[operator]" in message
    assert XLOGIC_ADAPTER_DIRECT_TRIGGER_REGISTRY_SCAN in message


def test_calculator_read_guardrail_rejects_unlisted_retained_snapshot_file() -> None:
    source = (
        "def read(record):\n"
        "    return record.dynamic_buff_list\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "BuffXLogic"
        / "_new_retained_calculator_snapshot.py"
    )
    findings = _collect_calculator_read_findings() + (
        _collect_calculator_read_findings_from_source(path, source)
    )

    relative_path = path.relative_to(PROJECT_ROOT).as_posix()
    expanded = _calculator_read_retained_snapshot_expansions(findings)

    assert expanded == {relative_path: 1}


def test_calculator_read_guardrail_failure_message_includes_triage_fields() -> None:
    source = (
        "from .Calculator import MultiplierData as MulData\n"
        "def read(record, enemy, char):\n"
        "    return MulData(enemy, record.dynamic_buff_list, char)\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "BuffXLogic"
        / "_calculator_read_fixture.py"
    )
    findings = _collect_calculator_read_findings_from_source(path, source)

    assert len(findings) == 2
    messages = [finding.message() for finding in findings]
    assert any(
        "zsim/sim_progress/Buff/BuffXLogic/_calculator_read_fixture.py:3"
        in message
        and "matched expression: MulData(enemy, record.dynamic_buff_list, char)"
        in message
        and "classification suggestion: direct MultiplierData compatibility snapshot"
        in message
        and f"next action: {CALCULATOR_READ_NEXT_ACTION}" in message
        for message in messages
    )
    assert any(
        "matched expression: record.dynamic_buff_list" in message
        and "classification suggestion: raw dynamic_buff_list attribute-read input"
        in message
        and f"next action: {CALCULATOR_READ_NEXT_ACTION}" in message
        for message in messages
    )


def test_calculator_read_guardrail_uses_ast_not_text_matching() -> None:
    source = (
        "def clean():\n"
        "    '''MultiplierData(...) Mul(...) dynamic_buff_list'''\n"
        "    # Planned-event producer notes are not Calculator read evidence.\n"
        "    return None\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "BuffXLogic"
        / "_calculator_read_fixture.py"
    )

    assert _collect_calculator_read_findings_from_source(path, source) == []


def test_calculator_read_guardrail_does_not_flag_dispatch_only_producer() -> None:
    source = (
        "from zsim.sim_progress.data_struct.schedule_dispatch import create_schedule_dispatch_port\n"
        "def publish(schedule_data, payload):\n"
        "    create_schedule_dispatch_port(schedule_data).publish(payload)\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "BuffXLogic"
        / "_dispatch_fixture.py"
    )

    assert _collect_calculator_read_findings_from_source(path, source) == []
