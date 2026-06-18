from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUFF_XLOGIC_ROOT = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffXLogic"

EXCLUDED_PARTS = {
    ".codex_worktrees",
    ".git",
    "__pycache__",
    "archive",
    "logs",
    "run-logs",
    ".runs",
    "results",
}

ENEMY_DYNAMIC_READ_NAMES = {
    "is_under_anomaly",
    "get_active_anomaly",
    "get_active_anomaly_bar",
    "assault",
    "burn",
    "shock",
    "frozen",
    "frostbite",
    "frost_frostbite",
    "corruption",
    "stun",
    "dynamic_debuff_list",
    "dynamic_dot_list",
}

CLASSIFICATION_BY_FILE = {
    "zsim/sim_progress/Buff/BuffXLogic/ElectroLipGlossAtkAndDmgBonus.py": "simple enemy read",
    "zsim/sim_progress/Buff/BuffXLogic/enemy_anomaly_read.py": "approved helper boundary",
    "zsim/sim_progress/Buff/BuffXLogic/enemy_edge_state_read.py": "approved helper boundary",
    "zsim/sim_progress/Buff/BuffXLogic/enemy_state_read.py": "approved helper boundary",
    "zsim/sim_progress/Buff/BuffXLogic/HugoCorePassiveEXStunBonus.py": "guarded-maintenance overlap",
    "zsim/sim_progress/Buff/BuffXLogic/JaneAdditionalAbilityPhyBuildupBonus.py": "simple enemy read",
    "zsim/sim_progress/Buff/BuffXLogic/LinaAdditionalSkillEleDMGBonus.py": "simple enemy read",
    "zsim/sim_progress/Buff/BuffXLogic/MarcatoDesireAtkBonus.py": "simple enemy read",
    "zsim/sim_progress/Buff/BuffXLogic/Soldier11AdditionalSkillExtraFireDMGBonus.py": "simple enemy read",
    "zsim/sim_progress/Buff/BuffXLogic/TimeweaverApBonus.py": "simple enemy read",
    "zsim/sim_progress/Buff/BuffXLogic/YixuanAdditionalAbilityDmgBonus.py": "simple enemy read",
    "zsim/sim_progress/Buff/BuffXLogic/YixuanCinema2StunTimeLimitBonus.py": "simple enemy read",
    "zsim/sim_progress/Buff/BuffXLogic/YuzuhaCinema2Trigger.py": "simple enemy read",
    "zsim/sim_progress/Buff/BuffXLogic/BranchBladeSongCritRateBonus.py": "edge-detection read",
    "zsim/sim_progress/Buff/BuffXLogic/LighterUniqueSkillStunTimeLimitBonus.py": "edge-detection read",
    "zsim/sim_progress/Buff/BuffXLogic/LyconAdditionalAbilityStunVulnerability.py": "edge-detection read",
    "zsim/sim_progress/Buff/BuffXLogic/MiyabiCoreSkill_FrostBurn.py": "edge-detection read",
    "zsim/sim_progress/Buff/BuffXLogic/PolarMetalFreezeBonus.py": "edge-detection read",
    "zsim/sim_progress/Buff/BuffXLogic/QingYiCoreSkillStunDMGBonus.py": "edge-detection read",
    "zsim/sim_progress/Buff/BuffXLogic/WeepingGeminiApBonus.py": "edge-detection read",
    "zsim/sim_progress/Buff/BuffXLogic/HugoCorePassiveTotalizeTrigger.py": "copied-output-adjacent read",
    "zsim/sim_progress/Buff/BuffXLogic/VivianCinema6Trigger.py": "copied-output-adjacent read",
    "zsim/sim_progress/Buff/BuffXLogic/VivianCorePassiveTrigger.py": "copied-output-adjacent read",
    "zsim/sim_progress/Buff/BuffXLogic/YanagiPolarityDisorderTrigger.py": "copied-output-adjacent read",
    "zsim/sim_progress/Buff/BuffXLogic/MiyabiCoreSkill_IceFire.py": "dot/debuff runtime-state read",
    "zsim/sim_progress/Buff/BuffXLogic/VivianDotTrigger.py": "dot/debuff runtime-state read",
}

APPROVED_ANOMALY_HELPER_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/ElectroLipGlossAtkAndDmgBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/JaneAdditionalAbilityPhyBuildupBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/MarcatoDesireAtkBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/TimeweaverApBonus.py",
}

APPROVED_SHOCK_HELPER_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/LinaAdditionalSkillEleDMGBonus.py",
}

APPROVED_STUN_HELPER_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/Soldier11AdditionalSkillExtraFireDMGBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/YixuanAdditionalAbilityDmgBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/YixuanCinema2StunTimeLimitBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/YuzuhaCinema2Trigger.py",
}

APPROVED_EDGE_FROZEN_HELPER_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/BranchBladeSongCritRateBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/PolarMetalFreezeBonus.py",
}

APPROVED_EDGE_STUN_HELPER_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/LighterUniqueSkillStunTimeLimitBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/LyconAdditionalAbilityStunVulnerability.py",
    "zsim/sim_progress/Buff/BuffXLogic/QingYiCoreSkillStunDMGBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/WeepingGeminiApBonus.py",
}

APPROVED_HELPER_FILES_BY_NAME = {
    "read_enemy_anomaly_active": APPROVED_ANOMALY_HELPER_FILES,
    "read_enemy_shock_active": APPROVED_SHOCK_HELPER_FILES,
    "read_enemy_stun_active": APPROVED_STUN_HELPER_FILES,
    "read_enemy_frozen_edge_state": APPROVED_EDGE_FROZEN_HELPER_FILES,
    "read_enemy_stun_edge_state": APPROVED_EDGE_STUN_HELPER_FILES,
}

APPROVED_HELPER_CLASSIFICATION_BY_NAME = {
    "read_enemy_anomaly_active": "simple enemy read",
    "read_enemy_shock_active": "simple enemy read",
    "read_enemy_stun_active": "simple enemy read",
    "read_enemy_frozen_edge_state": "edge-detection read",
    "read_enemy_stun_edge_state": "edge-detection read",
}

MIGRATED_HELPER_FILES = (
    APPROVED_ANOMALY_HELPER_FILES
    | APPROVED_SHOCK_HELPER_FILES
    | APPROVED_STUN_HELPER_FILES
    | APPROVED_EDGE_FROZEN_HELPER_FILES
    | APPROVED_EDGE_STUN_HELPER_FILES
)

EDGE_DETECTION_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/BranchBladeSongCritRateBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/LighterUniqueSkillStunTimeLimitBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/LyconAdditionalAbilityStunVulnerability.py",
    "zsim/sim_progress/Buff/BuffXLogic/MiyabiCoreSkill_FrostBurn.py",
    "zsim/sim_progress/Buff/BuffXLogic/PolarMetalFreezeBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/QingYiCoreSkillStunDMGBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/WeepingGeminiApBonus.py",
}

COPIED_OUTPUT_ADJACENT_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/HugoCorePassiveTotalizeTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/VivianCinema6Trigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/VivianCorePassiveTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/YanagiPolarityDisorderTrigger.py",
}

DOT_DEBUFF_RUNTIME_STATE_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/MiyabiCoreSkill_IceFire.py",
    "zsim/sim_progress/Buff/BuffXLogic/VivianDotTrigger.py",
}

EXPECTED_DIRECT_READ_FILES = set(CLASSIFICATION_BY_FILE) - MIGRATED_HELPER_FILES

CLASSIFICATION_BUCKETS = {
    "approved helper boundary",
    "simple enemy read",
    "edge-detection read",
    "copied-output-adjacent read",
    "dot/debuff runtime-state read",
    "guarded-maintenance overlap",
    "unrelated retained compatibility",
}

@dataclass(frozen=True)
class EnemyDynamicReadFinding:
    path: str
    line: int
    matched_expression: str
    classification_suggestion: str

    def message(self) -> str:
        return (
            f"{self.path}:{self.line}: matched expression: {self.matched_expression}; "
            f"classification suggestion: {self.classification_suggestion}; "
            "next action: classify the read family before helper design or migration"
        )


class EnemyDynamicReadVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source: str) -> None:
        self.path = path
        self.source = source
        self.findings: list[EnemyDynamicReadFinding] = []
        self._parents: list[ast.AST] = []

    def visit(self, node: ast.AST) -> Any:
        self._parents.append(node)
        try:
            return super().visit(node)
        finally:
            self._parents.pop()

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute) and self._is_enemy_dynamic_read(node.func):
            self._add_finding(line=node.lineno, expression=self._source_for(node))
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if self._is_enemy_dynamic_read(node) and not self._is_call_target(node):
            self._add_finding(line=node.lineno, expression=self._attribute_context(node))
        self.generic_visit(node)

    def _add_finding(self, *, line: int, expression: str) -> None:
        rel_path = self.path.relative_to(PROJECT_ROOT).as_posix()
        self.findings.append(
            EnemyDynamicReadFinding(
                path=rel_path,
                line=line,
                matched_expression=self._normalize(expression),
                classification_suggestion=CLASSIFICATION_BY_FILE.get(
                    rel_path, "unrelated retained compatibility"
                ),
            )
        )

    def _is_call_target(self, node: ast.Attribute) -> bool:
        parent = self._parents[-2] if len(self._parents) >= 2 else None
        return isinstance(parent, ast.Call) and parent.func is node

    def _is_enemy_dynamic_read(self, node: ast.Attribute) -> bool:
        if node.attr not in ENEMY_DYNAMIC_READ_NAMES:
            return False
        chain = self._attribute_chain(node)
        if len(chain) < 3:
            return False
        return chain[-3:-1] == ["enemy", "dynamic"]

    def _attribute_context(self, node: ast.Attribute) -> str:
        direct_parent = self._parents[-2] if len(self._parents) >= 2 else None
        if isinstance(direct_parent, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Compare)):
            return self._source_for(direct_parent)
        if isinstance(direct_parent, ast.UnaryOp):
            return self._source_for(direct_parent)
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
    def _attribute_chain(node: ast.AST) -> list[str]:
        parts: list[str] = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return list(reversed(parts))


def _is_excluded_path(path: Path) -> bool:
    try:
        rel_parts = path.relative_to(PROJECT_ROOT).parts
    except ValueError:
        return True
    return any(part in EXCLUDED_PARTS for part in rel_parts)


def _production_python_files() -> list[Path]:
    return sorted(
        path
        for path in BUFF_XLOGIC_ROOT.rglob("*.py")
        if not _is_excluded_path(path)
    )


def _collect_findings_from_source(
    path: Path, source: str
) -> list[EnemyDynamicReadFinding]:
    tree = ast.parse(source, filename=str(path))
    visitor = EnemyDynamicReadVisitor(path, source)
    visitor.visit(tree)
    return visitor.findings


def _collect_findings() -> list[EnemyDynamicReadFinding]:
    findings: list[EnemyDynamicReadFinding] = []
    for path in _production_python_files():
        findings.extend(_collect_findings_from_source(path, path.read_text(encoding="utf-8")))
    return findings


def _collect_helper_reference_paths() -> dict[str, dict[str, set[str]]]:
    references: dict[str, dict[str, set[str]]] = {
        helper_name: {"imports": set(), "calls": set()}
        for helper_name in APPROVED_HELPER_FILES_BY_NAME
    }
    for path in _production_python_files():
        rel_path = path.relative_to(PROJECT_ROOT).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name in references:
                        references[alias.name]["imports"].add(rel_path)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in references:
                    references[node.func.id]["calls"].add(rel_path)
                elif (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr in references
                ):
                    references[node.func.attr]["calls"].add(rel_path)
    return references


def test_enemy_dynamic_read_guardrail_scope_excludes_generated_and_duplicate_trees() -> None:
    scanned_files = {path.relative_to(PROJECT_ROOT).as_posix() for path in _production_python_files()}

    assert scanned_files
    assert all(".codex_worktrees" not in path for path in scanned_files)
    assert all("scripts/ralph/archive" not in path for path in scanned_files)
    assert all("scripts/ralph/logs" not in path for path in scanned_files)
    assert all("scripts/ralph/run-logs" not in path for path in scanned_files)
    assert all("logs/" not in path for path in scanned_files)
    assert set(CLASSIFICATION_BY_FILE).issubset(scanned_files)


def test_enemy_dynamic_read_guardrail_classifies_all_current_root_matches() -> None:
    findings = _collect_findings()
    finding_paths = {finding.path for finding in findings}
    unexpected = [
        finding
        for finding in findings
        if finding.path not in CLASSIFICATION_BY_FILE
        or finding.classification_suggestion not in CLASSIFICATION_BUCKETS
    ]

    assert not unexpected, (
        "Enemy dynamic read guardrail found unclassified current-root matches:\n"
        + "\n".join(f"- {finding.message()}" for finding in unexpected)
    )
    assert finding_paths == EXPECTED_DIRECT_READ_FILES
    assert {finding.classification_suggestion for finding in findings} == {
        CLASSIFICATION_BY_FILE[path] for path in EXPECTED_DIRECT_READ_FILES
    }


def test_enemy_dynamic_read_guardrail_limits_helper_to_approved_subset() -> None:
    references = _collect_helper_reference_paths()

    assert CLASSIFICATION_BY_FILE[
        "zsim/sim_progress/Buff/BuffXLogic/enemy_state_read.py"
    ] == "approved helper boundary"
    for helper_name, approved_files in APPROVED_HELPER_FILES_BY_NAME.items():
        helper_references = references[helper_name]
        approved_classification = APPROVED_HELPER_CLASSIFICATION_BY_NAME[helper_name]
        classified_files = {
            path
            for path, classification in CLASSIFICATION_BY_FILE.items()
            if classification == approved_classification
        }

        assert helper_references["imports"] == approved_files
        assert helper_references["calls"] == approved_files
        if approved_classification == "simple enemy read":
            assert approved_files < classified_files
        else:
            assert approved_files <= classified_files
        assert helper_references["imports"].isdisjoint(classified_files - approved_files)
        assert helper_references["calls"].isdisjoint(classified_files - approved_files)
        assert all(
            CLASSIFICATION_BY_FILE[path] == approved_classification
            for path in helper_references["imports"] | helper_references["calls"]
        )


def test_enemy_dynamic_read_guardrail_limits_frozen_edge_helper_to_exact_files() -> None:
    references = _collect_helper_reference_paths()["read_enemy_frozen_edge_state"]
    helper_references = references["imports"] | references["calls"]

    assert references["imports"] == APPROVED_EDGE_FROZEN_HELPER_FILES
    assert references["calls"] == APPROVED_EDGE_FROZEN_HELPER_FILES
    assert helper_references <= EDGE_DETECTION_FILES
    assert helper_references.isdisjoint(
        EDGE_DETECTION_FILES - APPROVED_EDGE_FROZEN_HELPER_FILES
    )
    assert helper_references.isdisjoint(COPIED_OUTPUT_ADJACENT_FILES)
    assert helper_references.isdisjoint(DOT_DEBUFF_RUNTIME_STATE_FILES)
    assert all(
        CLASSIFICATION_BY_FILE[path] == "edge-detection read"
        for path in helper_references
    )


def test_enemy_dynamic_read_guardrail_limits_stun_edge_helper_to_exact_files() -> None:
    references = _collect_helper_reference_paths()["read_enemy_stun_edge_state"]
    helper_references = references["imports"] | references["calls"]

    assert references["imports"] == APPROVED_EDGE_STUN_HELPER_FILES
    assert references["calls"] == APPROVED_EDGE_STUN_HELPER_FILES
    assert helper_references <= EDGE_DETECTION_FILES
    assert helper_references.isdisjoint(
        EDGE_DETECTION_FILES - APPROVED_EDGE_STUN_HELPER_FILES
    )
    assert helper_references.isdisjoint(COPIED_OUTPUT_ADJACENT_FILES)
    assert helper_references.isdisjoint(DOT_DEBUFF_RUNTIME_STATE_FILES)
    assert all(
        CLASSIFICATION_BY_FILE[path] == "edge-detection read"
        for path in helper_references
    )


def test_enemy_dynamic_read_guardrail_keeps_excluded_families_out_of_shock_stun_helpers() -> None:
    references = _collect_helper_reference_paths()
    shock_stun_references = (
        references["read_enemy_shock_active"]["imports"]
        | references["read_enemy_shock_active"]["calls"]
        | references["read_enemy_stun_active"]["imports"]
        | references["read_enemy_stun_active"]["calls"]
    )

    assert all(
        CLASSIFICATION_BY_FILE[path] == "edge-detection read"
        for path in EDGE_DETECTION_FILES
    )
    assert all(
        CLASSIFICATION_BY_FILE[path] == "copied-output-adjacent read"
        for path in COPIED_OUTPUT_ADJACENT_FILES
    )
    assert all(
        CLASSIFICATION_BY_FILE[path] == "dot/debuff runtime-state read"
        for path in DOT_DEBUFF_RUNTIME_STATE_FILES
    )
    assert shock_stun_references.isdisjoint(EDGE_DETECTION_FILES)
    assert shock_stun_references.isdisjoint(COPIED_OUTPUT_ADJACENT_FILES)
    assert shock_stun_references.isdisjoint(DOT_DEBUFF_RUNTIME_STATE_FILES)


def test_enemy_dynamic_read_guardrail_failure_message_classifies_unknown_matches() -> None:
    source = (
        "def judge(record):\n"
        "    if record.enemy.dynamic.is_under_anomaly():\n"
        "        return record.enemy.dynamic.stun\n"
    )
    path = BUFF_XLOGIC_ROOT / "_synthetic_enemy_dynamic_fixture.py"

    findings = _collect_findings_from_source(path, source)
    messages = [finding.message() for finding in findings]

    assert len(findings) == 2
    assert all(
        "classification suggestion: unrelated retained compatibility" in message
        for message in messages
    )
    assert any("matched expression: record.enemy.dynamic.is_under_anomaly()" in message for message in messages)
    assert any("matched expression: record.enemy.dynamic.stun" in message for message in messages)


def test_enemy_dynamic_read_guardrail_uses_ast_not_text_matching() -> None:
    source = (
        "def clean(record):\n"
        "    '''record.enemy.dynamic.stun enemy.dynamic.is_under_anomaly()'''\n"
        "    # record.enemy.dynamic.frozen is historical evidence only.\n"
        "    return record.enemy_dynamic_stun\n"
    )
    path = BUFF_XLOGIC_ROOT / "_synthetic_enemy_dynamic_fixture.py"

    assert _collect_findings_from_source(path, source) == []
