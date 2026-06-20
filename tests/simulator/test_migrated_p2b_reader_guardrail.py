from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

BUFF_XLOGIC_ROOT = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffXLogic"

MIGRATED_P2B_READER_FILES = (
    BUFF_XLOGIC_ROOT / "LighterAdditionalAbility_IceFireBonus.py",
    BUFF_XLOGIC_ROOT / "QingYiAdditionalAbilityStunConvertToATK.py",
    BUFF_XLOGIC_ROOT / "TriggerAdditionalAbilityStunBonus.py",
    BUFF_XLOGIC_ROOT / "Soldier0AnbyCoreSkillCritDMGBonus.py",
    BUFF_XLOGIC_ROOT / "CannonRotor.py",
    BUFF_XLOGIC_ROOT / "MiyabiCoreSkill_IceFire.py",
    BUFF_XLOGIC_ROOT / "WoodpeckerElectroSet4_NA.py",
    BUFF_XLOGIC_ROOT / "WoodpeckerElectroSet4_E_EX.py",
    BUFF_XLOGIC_ROOT / "WoodpeckerElectroSet4_CA.py",
)

SELECTED_IMPACT_CRIT_STUN_READER_FILES = (
    BUFF_XLOGIC_ROOT / "LighterAdditionalAbility_IceFireBonus.py",
    BUFF_XLOGIC_ROOT / "QingYiAdditionalAbilityStunConvertToATK.py",
    BUFF_XLOGIC_ROOT / "TriggerAdditionalAbilityStunBonus.py",
    BUFF_XLOGIC_ROOT / "Soldier0AnbyCoreSkillCritDMGBonus.py",
)

SELECTED_READER_METHODS = {
    "LighterAdditionalAbility_IceFireBonus.py": "read_impact",
    "QingYiAdditionalAbilityStunConvertToATK.py": "read_impact",
    "TriggerAdditionalAbilityStunBonus.py": "read_personal_crit_rate",
    "Soldier0AnbyCoreSkillCritDMGBonus.py": "read_personal_crit_damage",
}

MIGRATED_READER_METHODS = {
    "LighterAdditionalAbility_IceFireBonus.py": "read_impact",
    "QingYiAdditionalAbilityStunConvertToATK.py": "read_impact",
    "TriggerAdditionalAbilityStunBonus.py": "read_personal_crit_rate",
    "Soldier0AnbyCoreSkillCritDMGBonus.py": "read_personal_crit_damage",
    "CannonRotor.py": "read_full_crit_rate",
    "MiyabiCoreSkill_IceFire.py": "read_full_crit_rate",
    "WoodpeckerElectroSet4_NA.py": "read_full_crit_rate",
    "WoodpeckerElectroSet4_E_EX.py": "read_full_crit_rate",
    "WoodpeckerElectroSet4_CA.py": "read_full_crit_rate",
}

RETAINED_FORMULA_SNAPSHOT_FILES = {
    PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent" / "Calculator.py",
    PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent" / "CalAnomaly.py",
}

RETAINED_NON_MIGRATED_PHASE2_CANDIDATE_FILES = {
    BUFF_XLOGIC_ROOT / "BranchBladeSongCritDamageBonus.py",
    BUFF_XLOGIC_ROOT / "Soldier0AnbyCoreSkillDMGBonus.py",
    BUFF_XLOGIC_ROOT / "TimeweaverDisorderDmgMul.py",
}

FORBIDDEN_CALCULATOR_READS = {
    ("StunMul", "cal_imp"),
    ("RegularMul", "cal_crit_rate"),
    ("RegularMul", "cal_personal_crit_rate"),
    ("RegularMul", "cal_personal_crit_dmg"),
}

SELECTED_FORBIDDEN_BOUNDARY_TOKENS = {
    "BuffRuntimeReadPort",
    "LegacyRuntimeCommandAdapter",
    "RuntimeCommandPort",
    "ScheduleDispatchPort",
    "create_schedule_dispatch_port",
    "event_list",
    "find_event_list",
    "listener_manager.broadcast_event",
    "publish_scheduled",
    "schedule_data.event_list",
}

GUARDRAIL_SOURCE_SCAN_EXCLUDED_PARTS = {
    ".codex_worktrees",
    "archive",
    "codex-runlogs",
    "context",
    "logs",
    "results",
    "run-logs",
}


@dataclass(frozen=True)
class LegacyP2BReadFinding:
    path: str
    line: int
    kind: str
    expression: str

    def message(self) -> str:
        return f"{self.path}:{self.line}: {self.kind}: {self.expression}"


class MigratedP2BReaderVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source: str) -> None:
        self.path = path
        self.source = source
        self.findings: list[LegacyP2BReadFinding] = []
        self._multiplier_aliases = {"MultiplierData", "Mul"}
        self._calculator_aliases = {"Calculator", "Cal"}

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        if module.endswith("Calculator"):
            for alias in node.names:
                if alias.name == "MultiplierData":
                    self._multiplier_aliases.add(alias.asname or alias.name)
                    self._add_finding(
                        line=getattr(alias, "lineno", node.lineno),
                        kind="legacy_multiplier_import",
                        expression=self._source_for(alias),
                    )
                if alias.name == "Calculator":
                    self._calculator_aliases.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if self._is_multiplier_constructor(node.func):
            self._add_finding(
                line=node.lineno,
                kind="legacy_multiplier_constructor",
                expression=self._source_for(node),
            )
        if self._is_direct_impact_or_crit_calculator_call(node.func):
            self._add_finding(
                line=node.lineno,
                kind="legacy_p2b_calculator_call",
                expression=self._source_for(node.func),
            )
        self.generic_visit(node)

    def _is_multiplier_constructor(self, func: ast.AST) -> bool:
        if isinstance(func, ast.Name):
            return func.id in self._multiplier_aliases
        if isinstance(func, ast.Attribute):
            return func.attr in self._multiplier_aliases
        return False

    def _is_direct_impact_or_crit_calculator_call(self, func: ast.AST) -> bool:
        chain = self._attribute_chain(func)
        return (
            len(chain) >= 3
            and (chain[-2], chain[-1]) in FORBIDDEN_CALCULATOR_READS
            and chain[-3] in self._calculator_aliases
        )

    def _attribute_chain(self, node: ast.AST) -> list[str]:
        parts: list[str] = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return list(reversed(parts))

    def _add_finding(self, *, line: int, kind: str, expression: str) -> None:
        self.findings.append(
            LegacyP2BReadFinding(
                path=self.path.relative_to(PROJECT_ROOT).as_posix(),
                line=line,
                kind=kind,
                expression=self._normalize(expression),
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


def _collect_legacy_p2b_read_findings_from_source(
    path: Path, source: str
) -> list[LegacyP2BReadFinding]:
    tree = ast.parse(source, filename=str(path))
    visitor = MigratedP2BReaderVisitor(path, source)
    visitor.visit(tree)
    return visitor.findings


def _collect_migrated_file_findings() -> list[LegacyP2BReadFinding]:
    findings: list[LegacyP2BReadFinding] = []
    for path in MIGRATED_P2B_READER_FILES:
        source = path.read_text(encoding="utf-8")
        findings.extend(_collect_legacy_p2b_read_findings_from_source(path, source))
    return findings


def test_migrated_p2b_files_do_not_use_legacy_impact_or_crit_reads() -> None:
    findings = _collect_migrated_file_findings()

    assert not findings, (
        "Migrated P2-B impact / crit files reintroduced direct legacy reads:\n"
        + "\n".join(f"- {finding.message()}" for finding in findings)
    )


def test_migrated_p2b_guardrail_scope_is_exact_root_file_set() -> None:
    scanned_files = {
        path.relative_to(PROJECT_ROOT).as_posix() for path in MIGRATED_P2B_READER_FILES
    }

    assert scanned_files == {
        "zsim/sim_progress/Buff/BuffXLogic/LighterAdditionalAbility_IceFireBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/QingYiAdditionalAbilityStunConvertToATK.py",
        "zsim/sim_progress/Buff/BuffXLogic/TriggerAdditionalAbilityStunBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/Soldier0AnbyCoreSkillCritDMGBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/CannonRotor.py",
        "zsim/sim_progress/Buff/BuffXLogic/MiyabiCoreSkill_IceFire.py",
        "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_NA.py",
        "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_E_EX.py",
        "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_CA.py",
    }
    assert all(".codex_worktrees" not in path.parts for path in MIGRATED_P2B_READER_FILES)
    assert all(path.is_file() for path in MIGRATED_P2B_READER_FILES)
    assert not RETAINED_FORMULA_SNAPSHOT_FILES & set(MIGRATED_P2B_READER_FILES)
    assert not RETAINED_NON_MIGRATED_PHASE2_CANDIDATE_FILES & set(
        MIGRATED_P2B_READER_FILES
    )


def test_selected_impact_crit_stun_files_keep_reader_boundary() -> None:
    for path in SELECTED_IMPACT_CRIT_STUN_READER_FILES:
        source = path.read_text(encoding="utf-8")

        assert "CalculatorBuffAttributeReader" not in source
        assert "create_anomaly_attribute_read_context" not in source
        assert "create_calculator_runtime_read_context_from_sim_instance" in source
        assert "get_calculator_buff_attribute_reader_service" in source
        assert "active_buff_view=self.record.dynamic_buff_list" not in source
        assert SELECTED_READER_METHODS[path.name] in source


def test_migrated_p2b_files_use_runtime_reader_context() -> None:
    for path in MIGRATED_P2B_READER_FILES:
        source = path.read_text(encoding="utf-8")

        assert "CalculatorBuffAttributeReader" not in source
        assert "create_anomaly_attribute_read_context" not in source
        assert "create_calculator_runtime_read_context_from_sim_instance" in source
        assert "get_calculator_buff_attribute_reader_service" in source
        assert "active_buff_view=self.record.dynamic_buff_list" not in source
        assert MIGRATED_READER_METHODS[path.name] in source


def test_selected_impact_crit_stun_files_keep_runtime_layers_out_of_scope() -> None:
    for path in SELECTED_IMPACT_CRIT_STUN_READER_FILES:
        source = path.read_text(encoding="utf-8")
        forbidden = sorted(
            token for token in SELECTED_FORBIDDEN_BOUNDARY_TOKENS if token in source
        )

        assert forbidden == [], (
            f"{path.relative_to(PROJECT_ROOT).as_posix()} introduced event/runtime "
            f"boundary shortcuts: {forbidden}"
        )


def test_selected_impact_crit_stun_scan_set_excludes_generated_sources() -> None:
    scanned_files = {
        path.relative_to(PROJECT_ROOT).as_posix()
        for path in SELECTED_IMPACT_CRIT_STUN_READER_FILES
    }

    assert scanned_files == {
        "zsim/sim_progress/Buff/BuffXLogic/LighterAdditionalAbility_IceFireBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/QingYiAdditionalAbilityStunConvertToATK.py",
        "zsim/sim_progress/Buff/BuffXLogic/TriggerAdditionalAbilityStunBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/Soldier0AnbyCoreSkillCritDMGBonus.py",
    }
    assert all(path.is_file() for path in SELECTED_IMPACT_CRIT_STUN_READER_FILES)
    assert all(
        not (set(path.parts) & GUARDRAIL_SOURCE_SCAN_EXCLUDED_PARTS)
        for path in SELECTED_IMPACT_CRIT_STUN_READER_FILES
    )
    assert not RETAINED_FORMULA_SNAPSHOT_FILES & set(
        SELECTED_IMPACT_CRIT_STUN_READER_FILES
    )
    assert not RETAINED_NON_MIGRATED_PHASE2_CANDIDATE_FILES & set(
        SELECTED_IMPACT_CRIT_STUN_READER_FILES
    )


def test_migrated_p2b_guardrail_reports_legacy_patterns() -> None:
    source = (
        "from zsim.sim_progress.ScheduledEvent.Calculator import Calculator, MultiplierData\n"
        "from zsim.sim_progress.ScheduledEvent.Calculator import Calculator as Cal, MultiplierData as Mul\n"
        "def legacy(record):\n"
        "    direct = MultiplierData(record.enemy, record.dynamic_buff_list, record.char)\n"
        "    alias = Mul(record.enemy, record.dynamic_buff_list, record.char)\n"
        "    impact = Calculator.StunMul.cal_imp(direct)\n"
        "    full_rate = Calculator.RegularMul.cal_crit_rate(direct)\n"
        "    personal_rate = Cal.RegularMul.cal_personal_crit_rate(alias)\n"
        "    personal_dmg = Cal.RegularMul.cal_personal_crit_dmg(alias)\n"
        "    return impact + full_rate + personal_rate + personal_dmg\n"
    )
    path = BUFF_XLOGIC_ROOT / "_migrated_p2b_fixture.py"
    findings = _collect_legacy_p2b_read_findings_from_source(path, source)
    messages = [finding.message() for finding in findings]

    assert len(findings) == 8
    assert any("legacy_multiplier_import: MultiplierData" in message for message in messages)
    assert any("legacy_multiplier_import: MultiplierData as Mul" in message for message in messages)
    assert any("legacy_multiplier_constructor: MultiplierData(" in message for message in messages)
    assert any("legacy_multiplier_constructor: Mul(" in message for message in messages)
    assert any(
        "legacy_p2b_calculator_call: Calculator.StunMul.cal_imp" in message
        for message in messages
    )
    assert any(
        "legacy_p2b_calculator_call: Calculator.RegularMul.cal_crit_rate" in message
        for message in messages
    )
    assert any(
        "legacy_p2b_calculator_call: Cal.RegularMul.cal_personal_crit_rate" in message
        for message in messages
    )
    assert any(
        "legacy_p2b_calculator_call: Cal.RegularMul.cal_personal_crit_dmg" in message
        for message in messages
    )


def test_migrated_p2b_guardrail_uses_ast_not_text_matching() -> None:
    source = (
        "def clean():\n"
        "    '''MultiplierData(...) MultiplierData as Mul Mul(...) Calculator.StunMul.cal_imp'''\n"
        "    # Cal.RegularMul.cal_crit_rate remains a historical note only.\n"
        "    # Calculator.RegularMul.cal_personal_crit_rate and cal_personal_crit_dmg too.\n"
        "    return None\n"
    )
    path = BUFF_XLOGIC_ROOT / "_migrated_p2b_fixture.py"

    assert _collect_legacy_p2b_read_findings_from_source(path, source) == []
