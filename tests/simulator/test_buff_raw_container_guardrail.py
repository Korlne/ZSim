from __future__ import annotations

import ast
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


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
        if context == "Simulator._create_buff_runtime_facade":
            return "legacy facade construction"
        if context == "Simulator.main_loop":
            return "retained BuffLoadLoop/ScheduledEvent main-loop boundary"
    if path == "zsim/sim_progress/Buff/BuffLoad.py":
        return "retained BuffLoadLoop trigger judgement and pending queue population"
    if path == "zsim/sim_progress/Buff/BuffAdd.py":
        if context == "buff_add":
            return "legacy buff_add pending-to-active compatibility path"
        if context == "add_debuff_to_enemy":
            return "legacy buff_add enemy debuff mirror sync"
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

    if path == "zsim/sim_progress/ScheduledEvent/event_handlers/context.py":
        if context in {
            "EventContext.get_legacy_dynamic_buff_dict",
            "EventContext.get_legacy_exist_buff_dict",
            "EventContext.get_dynamic_buff",
            "EventContext.get_exist_buff_dict",
        }:
            return "documented EventContext compatibility getters"

    if path == "zsim/sim_progress/ScheduledEvent/event_handlers/base.py":
        if context in {
            "BaseEventHandler._get_context_legacy_dynamic_buff",
            "BaseEventHandler._get_context_legacy_exist_buff_dict",
            "BaseEventHandler._get_context_dynamic_buff",
            "BaseEventHandler._get_context_exist_buff_dict",
        }:
            return "documented BaseEventHandler compatibility getters"

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
        return "retained XLogic compatibility snapshot read"

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
    "legacy facade adapter internals": 59,
    "legacy facade construction": 8,
    "retained BuffLoadLoop/ScheduledEvent main-loop boundary": 4,
    "retained BuffLoadLoop trigger judgement and pending queue population": 41,
    "legacy buff_add pending-to-active compatibility path": 10,
    "legacy buff_add enemy debuff mirror sync": 3,
    "retained Update_Buff time-effect compatibility wrapper": 5,
    "retained Update_Buff active-store traversal and no-facade fallback": 7,
    "legacy KickOutBuff active-removal compatibility path": 5,
    "retained ScheduledEvent raw-container boundary": 21,
    "RuntimeCommandPort compatibility reads": 10,
}

EXPECTED_SCHEDULED_RUNTIME_REFERENCE_CEILINGS = {
    "retained ScheduledEvent constructor setup": 13,
    "runtime view / command adapter setup": 6,
    "retained SPUpdateData runtime read candidate": 2,
    "runtime view / facade adapter internals": 63,
    "existing RuntimeCommandPort adapter reads": 10,
    "documented EventContext compatibility getters": 8,
    "documented BaseEventHandler compatibility getters": 8,
    "runtime view passed to Calculator formula boundary": 3,
    "runtime view passed to anomaly formula boundary": 4,
}

EXPECTED_CALCULATOR_READ_REFERENCE_CEILINGS = {
    "Calculator formula snapshot construction": 1,
    "migrated attribute-reader active_buff_view input": 2,
    "retained XLogic compatibility snapshot read": 25,
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
