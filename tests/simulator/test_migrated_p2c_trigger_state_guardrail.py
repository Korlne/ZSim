from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUFF_XLOGIC_ROOT = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffXLogic"

MIGRATED_P2C_TRIGGER_STATE_FILES = (
    BUFF_XLOGIC_ROOT / "FlamemakerShakerApBonus.py",
    BUFF_XLOGIC_ROOT / "SpectralGazeImpactBonus.py",
    BUFF_XLOGIC_ROOT / "SharpenedStingerAnomalyBuildupBonus.py",
    BUFF_XLOGIC_ROOT / "CordisGerminaSNAAndQIgnoreDefense.py",
    BUFF_XLOGIC_ROOT / "AstralVoice.py",
    BUFF_XLOGIC_ROOT / "JaneCinema1APTransToDmgBonus.py",
    BUFF_XLOGIC_ROOT / "JaneCoreSkillStrikeCritDmgBonus.py",
    BUFF_XLOGIC_ROOT / "JaneCoreSkillStrikeCritRateBonus.py",
    BUFF_XLOGIC_ROOT / "JanePassionStateAPTransToATK.py",
    BUFF_XLOGIC_ROOT / "JanePassionStatePhyBuildupBonus.py",
    BUFF_XLOGIC_ROOT / "Soldier0AnbyAdditionalSkillDMGBonus.py",
    BUFF_XLOGIC_ROOT / "Soldier0AnbyCinema4EleResReduce.py",
    BUFF_XLOGIC_ROOT / "Soldier0AnbyCoreSkillCritDMGBonus.py",
)

RETAINED_UNMIGRATED_TRIGGER_STATE_CANDIDATES = {
    BUFF_XLOGIC_ROOT / "SeveredInnocencELEDMGBonus.py",
    BUFF_XLOGIC_ROOT / "WeepingCradleDMGBonusIncrease.py",
    BUFF_XLOGIC_ROOT / "YangiCinema1ApBonus.py",
    BUFF_XLOGIC_ROOT / "YunkuiTalesSheerAtkBonus.py",
}

RETAINED_P2A_P2B_MIGRATED_FILES = {
    BUFF_XLOGIC_ROOT / "AliceAdditionalAbilityApBonus.py",
    BUFF_XLOGIC_ROOT / "YuzuhaAdditionalAbilityAnomalyBuildupBonus.py",
    BUFF_XLOGIC_ROOT / "YuzuhaAdditionalAbilityAnomalyDmgBonus.py",
    BUFF_XLOGIC_ROOT / "LighterAdditionalAbility_IceFireBonus.py",
    BUFF_XLOGIC_ROOT / "QingYiAdditionalAbilityStunConvertToATK.py",
    BUFF_XLOGIC_ROOT / "TriggerAdditionalAbilityStunBonus.py",
    BUFF_XLOGIC_ROOT / "CannonRotor.py",
    BUFF_XLOGIC_ROOT / "MiyabiCoreSkill_IceFire.py",
    BUFF_XLOGIC_ROOT / "WoodpeckerElectroSet4_NA.py",
    BUFF_XLOGIC_ROOT / "WoodpeckerElectroSet4_E_EX.py",
    BUFF_XLOGIC_ROOT / "WoodpeckerElectroSet4_CA.py",
}

RETAINED_FORMULA_SNAPSHOT_FILES = {
    PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent" / "Calculator.py",
    PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent" / "CalAnomaly.py",
}

RETAINED_BUFF_ADD_STRATEGY_FILES = {
    PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffAddStrategy.py",
}

FORBIDDEN_TRIGGER_STATE_FIELDS = {"active", "count", "built_in_buff_box"}


@dataclass(frozen=True)
class DirectTriggerStateFinding:
    path: str
    line: int
    expression: str
    field: str

    def message(self) -> str:
        return (
            f"{self.path}:{self.line}: direct_trigger_state_chain: {self.expression} | "
            f"classification suggestion: migrated P2-C trigger-state read for `{self.field}` | "
            "next action: read through `read_trigger_buff_state(record)` after the existing "
            "`get_prepared(..., trigger_buff_0=...)` call"
        )


class MigratedP2CTriggerStateVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source: str) -> None:
        self.path = path
        self.source = source
        self.findings: list[DirectTriggerStateFinding] = []

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in FORBIDDEN_TRIGGER_STATE_FIELDS and self._is_trigger_state_chain(node):
            self.findings.append(
                DirectTriggerStateFinding(
                    path=self.path.relative_to(PROJECT_ROOT).as_posix(),
                    line=node.lineno,
                    expression=self._source_for(node),
                    field=node.attr,
                )
            )
        self.generic_visit(node)

    def _is_trigger_state_chain(self, node: ast.Attribute) -> bool:
        return self._attribute_chain(node)[-4:] == [
            "record",
            "trigger_buff_0",
            "dy",
            node.attr,
        ]

    def _attribute_chain(self, node: ast.AST) -> list[str]:
        parts: list[str] = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return list(reversed(parts))

    def _source_for(self, node: ast.AST) -> str:
        segment = ast.get_source_segment(self.source, node)
        if segment is None:
            return f"<{type(node).__name__}>"
        return " ".join(segment.strip().split())


def _collect_direct_trigger_state_findings_from_source(
    path: Path, source: str
) -> list[DirectTriggerStateFinding]:
    tree = ast.parse(source, filename=str(path))
    visitor = MigratedP2CTriggerStateVisitor(path, source)
    visitor.visit(tree)
    return visitor.findings


def _collect_migrated_file_findings() -> list[DirectTriggerStateFinding]:
    findings: list[DirectTriggerStateFinding] = []
    for path in MIGRATED_P2C_TRIGGER_STATE_FILES:
        source = path.read_text(encoding="utf-8")
        findings.extend(_collect_direct_trigger_state_findings_from_source(path, source))
    return findings


def test_migrated_p2c_files_do_not_use_direct_trigger_state_chains() -> None:
    findings = _collect_migrated_file_findings()

    assert not findings, (
        "Migrated P2-C trigger-state files reintroduced direct old-template state reads:\n"
        + "\n".join(f"- {finding.message()}" for finding in findings)
    )


def test_migrated_p2c_guardrail_scope_is_exact_root_file_set() -> None:
    scanned_files = {
        path.relative_to(PROJECT_ROOT).as_posix()
        for path in MIGRATED_P2C_TRIGGER_STATE_FILES
    }

    assert scanned_files == {
        "zsim/sim_progress/Buff/BuffXLogic/FlamemakerShakerApBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/SpectralGazeImpactBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/SharpenedStingerAnomalyBuildupBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/CordisGerminaSNAAndQIgnoreDefense.py",
        "zsim/sim_progress/Buff/BuffXLogic/AstralVoice.py",
        "zsim/sim_progress/Buff/BuffXLogic/JaneCinema1APTransToDmgBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/JaneCoreSkillStrikeCritDmgBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/JaneCoreSkillStrikeCritRateBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/JanePassionStateAPTransToATK.py",
        "zsim/sim_progress/Buff/BuffXLogic/JanePassionStatePhyBuildupBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/Soldier0AnbyAdditionalSkillDMGBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/Soldier0AnbyCinema4EleResReduce.py",
        "zsim/sim_progress/Buff/BuffXLogic/Soldier0AnbyCoreSkillCritDMGBonus.py",
    }
    assert all(".codex_worktrees" not in path.parts for path in MIGRATED_P2C_TRIGGER_STATE_FILES)
    assert all(path.is_file() for path in MIGRATED_P2C_TRIGGER_STATE_FILES)
    assert not RETAINED_UNMIGRATED_TRIGGER_STATE_CANDIDATES & set(
        MIGRATED_P2C_TRIGGER_STATE_FILES
    )
    assert not RETAINED_P2A_P2B_MIGRATED_FILES & set(MIGRATED_P2C_TRIGGER_STATE_FILES)
    assert not RETAINED_FORMULA_SNAPSHOT_FILES & set(MIGRATED_P2C_TRIGGER_STATE_FILES)
    assert not RETAINED_BUFF_ADD_STRATEGY_FILES & set(MIGRATED_P2C_TRIGGER_STATE_FILES)


def test_migrated_p2c_guardrail_reports_direct_trigger_state_chains() -> None:
    source = (
        "class LegacyGate:\n"
        "    def judge(self, record):\n"
        "        if self.record.trigger_buff_0.dy.active:\n"
        "            return record.trigger_buff_0.dy.count == 3\n"
        "        return len(self.record.trigger_buff_0.dy.built_in_buff_box) == 2\n"
    )
    path = BUFF_XLOGIC_ROOT / "_migrated_p2c_fixture.py"

    findings = _collect_direct_trigger_state_findings_from_source(path, source)
    messages = [finding.message() for finding in findings]

    assert len(findings) == 3
    assert any("direct_trigger_state_chain: self.record.trigger_buff_0.dy.active" in message for message in messages)
    assert any("classification suggestion: migrated P2-C trigger-state read for `active`" in message for message in messages)
    assert any("direct_trigger_state_chain: record.trigger_buff_0.dy.count" in message for message in messages)
    assert any("classification suggestion: migrated P2-C trigger-state read for `count`" in message for message in messages)
    assert any("direct_trigger_state_chain: self.record.trigger_buff_0.dy.built_in_buff_box" in message for message in messages)
    assert any("next action: read through `read_trigger_buff_state(record)`" in message for message in messages)


def test_migrated_p2c_guardrail_uses_ast_not_text_matching() -> None:
    source = (
        "def clean():\n"
        "    '''record.trigger_buff_0.dy.active record.trigger_buff_0.dy.count'''\n"
        "    # record.trigger_buff_0.dy.built_in_buff_box remains a historical note only.\n"
        "    return read_trigger_buff_state(record).count\n"
    )
    path = BUFF_XLOGIC_ROOT / "_migrated_p2c_fixture.py"

    assert _collect_direct_trigger_state_findings_from_source(path, source) == []
