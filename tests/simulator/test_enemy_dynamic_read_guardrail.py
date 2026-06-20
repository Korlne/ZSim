from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


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

EXCLUDED_RELATIVE_PREFIXES = {
    ("scripts", "ralph", "archive"),
    ("scripts", "ralph", "context"),
    ("scripts", "ralph", "logs"),
    ("scripts", "ralph", "run-logs"),
    ("scripts", "ralph", ".runs"),
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
    "zsim/sim_progress/Buff/BuffXLogic/enemy_anomaly_map_read.py": "approved helper boundary",
    "zsim/sim_progress/Buff/BuffXLogic/enemy_anomaly_read.py": "approved helper boundary",
    "zsim/sim_progress/Buff/BuffXLogic/enemy_debuff_mirror_read.py": "approved helper boundary",
    "zsim/sim_progress/Buff/BuffXLogic/enemy_edge_state_read.py": "approved helper boundary",
    "zsim/sim_progress/Buff/BuffXLogic/enemy_state_read.py": "approved helper boundary",
    "zsim/sim_progress/Buff/BuffXLogic/AnomalyDebuffExitJudge.py": "delegated anomaly-map read",
    "zsim/sim_progress/Buff/BuffXLogic/HugoCorePassiveEXStunBonus.py": "guarded-maintenance overlap",
    "zsim/sim_progress/Buff/BuffXLogic/HailstormShrineIceBonus.py": "delegated anomaly-map read",
    "zsim/sim_progress/Buff/BuffXLogic/JaneAdditionalAbilityPhyBuildupBonus.py": "simple enemy read",
    "zsim/sim_progress/Buff/BuffXLogic/LinaAdditionalSkillEleDMGBonus.py": "simple enemy read",
    "zsim/sim_progress/Buff/BuffXLogic/MarcatoDesireAtkBonus.py": "simple enemy read",
    "zsim/sim_progress/Buff/BuffXLogic/MiyabiAdditionalAbility_IgnoreIceRes.py": "delegated anomaly-map read",
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

APPROVED_ENEMY_STATE_PORT_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/HugoCorePassiveEXStunBonus.py",
}

APPROVED_COPIED_OUTPUT_ANOMALY_HELPER_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/VivianCinema6Trigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/VivianCorePassiveTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/YanagiPolarityDisorderTrigger.py",
}

APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/VivianDotTrigger.py",
}

YANAGI_COPIED_OUTPUT_ANOMALY_HELPER_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/YanagiPolarityDisorderTrigger.py",
}

APPROVED_COPIED_OUTPUT_STUN_HELPER_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/HugoCorePassiveTotalizeTrigger.py",
}

DELEGATED_COPIED_OUTPUT_ANOMALY_HELPER_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/VivianCinema6Trigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/VivianCorePassiveTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/YanagiPolarityDisorderTrigger.py",
}

APPROVED_COPIED_OUTPUT_HELPER_FILES_BY_NAME = {
    "read_enemy_anomaly_active": APPROVED_COPIED_OUTPUT_ANOMALY_HELPER_FILES,
    "read_enemy_stun_active": APPROVED_COPIED_OUTPUT_STUN_HELPER_FILES,
}

DELEGATED_COPIED_OUTPUT_HELPER_FILES = (
    APPROVED_COPIED_OUTPUT_STUN_HELPER_FILES | YANAGI_COPIED_OUTPUT_ANOMALY_HELPER_FILES
)

APPROVED_EDGE_FROZEN_HELPER_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/BranchBladeSongCritRateBonus.py",
}

APPROVED_EDGE_STATE_PORT_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/PolarMetalFreezeBonus.py",
}

APPROVED_EDGE_STUN_HELPER_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/LighterUniqueSkillStunTimeLimitBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/LyconAdditionalAbilityStunVulnerability.py",
    "zsim/sim_progress/Buff/BuffXLogic/QingYiCoreSkillStunDMGBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/WeepingGeminiApBonus.py",
}

APPROVED_EDGE_FROST_FROSTBITE_HELPER_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/MiyabiCoreSkill_FrostBurn.py",
}

APPROVED_DOT_RUNTIME_FROST_FROSTBITE_HELPER_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/MiyabiCoreSkill_IceFire.py",
}

APPROVED_DOT_DEBUFF_MIRROR_HELPER_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/MiyabiCoreSkill_IceFire.py",
}

APPROVED_FROST_FROSTBITE_HELPER_FILES = (
    APPROVED_EDGE_FROST_FROSTBITE_HELPER_FILES | APPROVED_DOT_RUNTIME_FROST_FROSTBITE_HELPER_FILES
)

APPROVED_ANOMALY_MAP_SINGLE_HELPER_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/AnomalyDebuffExitJudge.py",
}

APPROVED_ANOMALY_MAP_SNAPSHOT_HELPER_FILES = {
    "zsim/sim_progress/Buff/BuffXLogic/HailstormShrineIceBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/MiyabiAdditionalAbility_IgnoreIceRes.py",
}

APPROVED_ANOMALY_MAP_HELPER_FILES = (
    APPROVED_ANOMALY_MAP_SINGLE_HELPER_FILES | APPROVED_ANOMALY_MAP_SNAPSHOT_HELPER_FILES
)

APPROVED_ANOMALY_MAP_HELPER_FILES_BY_NAME = {
    "read_enemy_anomaly_state": APPROVED_ANOMALY_MAP_SINGLE_HELPER_FILES,
    "snapshot_enemy_anomaly_states": APPROVED_ANOMALY_MAP_SNAPSHOT_HELPER_FILES,
}

MIGRATED_HELPER_FILES_BY_NAME = {
    "read_enemy_anomaly_active": (
        APPROVED_ANOMALY_HELPER_FILES | APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES
    ),
    "read_enemy_shock_active": APPROVED_SHOCK_HELPER_FILES,
    "read_enemy_stun_active": APPROVED_STUN_HELPER_FILES,
    "EnemyStateReadPort": APPROVED_ENEMY_STATE_PORT_FILES,
    "EnemyEdgeStateReadPort": APPROVED_EDGE_STATE_PORT_FILES,
    "read_enemy_frozen_edge_state": APPROVED_EDGE_FROZEN_HELPER_FILES,
    "read_enemy_stun_edge_state": APPROVED_EDGE_STUN_HELPER_FILES,
    "read_enemy_frost_frostbite_edge_state": APPROVED_EDGE_FROST_FROSTBITE_HELPER_FILES,
    "MiyabiFrostburnDebuffMirrorReader": APPROVED_DOT_DEBUFF_MIRROR_HELPER_FILES,
    "read_enemy_anomaly_state": APPROVED_ANOMALY_MAP_SINGLE_HELPER_FILES,
    "snapshot_enemy_anomaly_states": APPROVED_ANOMALY_MAP_SNAPSHOT_HELPER_FILES,
}

APPROVED_HELPER_FILES_BY_NAME = {
    "read_enemy_anomaly_active": (
        APPROVED_ANOMALY_HELPER_FILES
        | APPROVED_COPIED_OUTPUT_ANOMALY_HELPER_FILES
        | APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES
    ),
    "read_enemy_shock_active": APPROVED_SHOCK_HELPER_FILES,
    "read_enemy_stun_active": (
        APPROVED_STUN_HELPER_FILES | APPROVED_COPIED_OUTPUT_STUN_HELPER_FILES
    ),
    "EnemyStateReadPort": APPROVED_ENEMY_STATE_PORT_FILES,
    "EnemyEdgeStateReadPort": APPROVED_EDGE_STATE_PORT_FILES,
    "read_enemy_frozen_edge_state": APPROVED_EDGE_FROZEN_HELPER_FILES,
    "read_enemy_stun_edge_state": APPROVED_EDGE_STUN_HELPER_FILES,
    "read_enemy_frost_frostbite_edge_state": APPROVED_FROST_FROSTBITE_HELPER_FILES,
    "MiyabiFrostburnDebuffMirrorReader": APPROVED_DOT_DEBUFF_MIRROR_HELPER_FILES,
    **APPROVED_ANOMALY_MAP_HELPER_FILES_BY_NAME,
}

APPROVED_HELPER_CLASSIFICATIONS_BY_NAME = {
    "read_enemy_anomaly_active": {
        "simple enemy read",
        "copied-output-adjacent read",
        "dot/debuff runtime-state read",
    },
    "read_enemy_shock_active": {"simple enemy read"},
    "read_enemy_stun_active": {
        "simple enemy read",
        "copied-output-adjacent read",
    },
    "EnemyStateReadPort": {"guarded-maintenance overlap"},
    "EnemyEdgeStateReadPort": {"edge-detection read"},
    "read_enemy_frozen_edge_state": {"edge-detection read"},
    "read_enemy_stun_edge_state": {"edge-detection read"},
    "read_enemy_frost_frostbite_edge_state": {
        "edge-detection read",
        "dot/debuff runtime-state read",
    },
    "MiyabiFrostburnDebuffMirrorReader": {"dot/debuff runtime-state read"},
    "read_enemy_anomaly_state": {"delegated anomaly-map read"},
    "snapshot_enemy_anomaly_states": {"delegated anomaly-map read"},
}

HELPER_NAMES_BY_FAMILY = {
    "simple anomaly": frozenset({"read_enemy_anomaly_active"}),
    "simple shock/stun": frozenset(
        {"read_enemy_shock_active", "read_enemy_stun_active", "EnemyStateReadPort"}
    ),
    "edge-state helpers": frozenset(
        {
            "read_enemy_frozen_edge_state",
            "read_enemy_stun_edge_state",
            "read_enemy_frost_frostbite_edge_state",
            "EnemyEdgeStateReadPort",
        }
    ),
    "anomaly-map helpers": frozenset(APPROVED_ANOMALY_MAP_HELPER_FILES_BY_NAME),
    "debuff mirror helpers": frozenset({"MiyabiFrostburnDebuffMirrorReader"}),
}

MIGRATED_HELPER_FILES = set().union(*MIGRATED_HELPER_FILES_BY_NAME.values())

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

ANOMALY_MAP_FUTURE_POOL_FILES: set[str] = set()

DELEGATED_ANOMALY_MAP_HELPER_FILES = APPROVED_ANOMALY_MAP_HELPER_FILES

EXCLUDED_RUNTIME_STATE_AND_ANOMALY_MAP_FILES = (
    DOT_DEBUFF_RUNTIME_STATE_FILES | ANOMALY_MAP_FUTURE_POOL_FILES
)

EXPECTED_DIRECT_READ_FILES = (
    set(CLASSIFICATION_BY_FILE) - MIGRATED_HELPER_FILES - DELEGATED_COPIED_OUTPUT_HELPER_FILES
)

CLASSIFICATION_BUCKETS = {
    "approved helper boundary",
    "simple enemy read",
    "edge-detection read",
    "copied-output-adjacent read",
    "dot/debuff runtime-state read",
    "same-phase future anomaly-map read",
    "delegated anomaly-map read",
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
        elif self._is_enemy_dynamic_getattr(node):
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

    def _is_enemy_dynamic_getattr(self, node: ast.Call) -> bool:
        if not isinstance(node.func, ast.Name) or node.func.id != "getattr":
            return False
        if len(node.args) < 2:
            return False
        dynamic_arg = node.args[0]
        if not isinstance(dynamic_arg, ast.Attribute):
            return False
        chain = self._attribute_chain(dynamic_arg)
        if len(chain) < 2:
            return False
        return chain[-2:] == ["enemy", "dynamic"]

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
    return any(part in EXCLUDED_PARTS for part in rel_parts) or any(
        rel_parts[: len(prefix)] == prefix for prefix in EXCLUDED_RELATIVE_PREFIXES
    )


def _production_python_files() -> list[Path]:
    return sorted(path for path in BUFF_XLOGIC_ROOT.rglob("*.py") if not _is_excluded_path(path))


def _collect_findings_from_source(path: Path, source: str) -> list[EnemyDynamicReadFinding]:
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
        if CLASSIFICATION_BY_FILE.get(rel_path) == "approved helper boundary":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name in references:
                        references[alias.name]["imports"].add(rel_path)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in references:
                    references[node.func.id]["calls"].add(rel_path)
                elif isinstance(node.func, ast.Attribute) and node.func.attr in references:
                    references[node.func.attr]["calls"].add(rel_path)
    return references


def _helper_references_for_names(
    references: dict[str, dict[str, set[str]]],
    helper_names: Iterable[str],
) -> dict[str, set[str]]:
    family_references: dict[str, set[str]] = {"imports": set(), "calls": set()}
    for helper_name in helper_names:
        family_references["imports"].update(references[helper_name]["imports"])
        family_references["calls"].update(references[helper_name]["calls"])
    return family_references


def test_enemy_dynamic_read_guardrail_scope_excludes_generated_and_duplicate_trees() -> None:
    scanned_files = {
        path.relative_to(PROJECT_ROOT).as_posix() for path in _production_python_files()
    }
    excluded_examples = [
        PROJECT_ROOT / ".codex_worktrees" / "old" / "zsim" / "legacy.py",
        PROJECT_ROOT / ".git" / "objects" / "legacy.py",
        PROJECT_ROOT / "scripts" / "ralph" / "archive" / "old.py",
        PROJECT_ROOT / "scripts" / "ralph" / "context" / "generated.py",
        PROJECT_ROOT / "scripts" / "ralph" / "logs" / "run.py",
        PROJECT_ROOT / "scripts" / "ralph" / "run-logs" / "run.py",
        PROJECT_ROOT / "scripts" / "ralph" / ".runs" / "run.py",
        PROJECT_ROOT / "logs" / "sim.py",
        PROJECT_ROOT / "results" / "sim.py",
    ]

    assert scanned_files
    assert all(_is_excluded_path(path) for path in excluded_examples)
    assert not _is_excluded_path(BUFF_XLOGIC_ROOT / "MiyabiCoreSkill_IceFire.py")
    assert all(".codex_worktrees" not in path for path in scanned_files)
    assert all(".git" not in path for path in scanned_files)
    assert all("scripts/ralph/archive" not in path for path in scanned_files)
    assert all("scripts/ralph/context" not in path for path in scanned_files)
    assert all("scripts/ralph/logs" not in path for path in scanned_files)
    assert all("scripts/ralph/run-logs" not in path for path in scanned_files)
    assert all("scripts/ralph/.runs" not in path for path in scanned_files)
    assert all("logs/" not in path for path in scanned_files)
    assert all("results/" not in path for path in scanned_files)
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


def test_enemy_dynamic_read_guardrail_classifies_getattr_anomaly_maps_as_future_pool() -> None:
    findings = _collect_findings()
    getattr_findings = [
        finding for finding in findings if finding.matched_expression.startswith("getattr(")
    ]
    helper_boundary_path = "zsim/sim_progress/Buff/BuffXLogic/enemy_anomaly_map_read.py"
    helper_getattr_findings = [
        finding for finding in getattr_findings if finding.path == helper_boundary_path
    ]
    state_machine_getattr_findings = [
        finding for finding in getattr_findings if finding.path != helper_boundary_path
    ]

    assert {
        finding.path for finding in state_machine_getattr_findings
    } == ANOMALY_MAP_FUTURE_POOL_FILES
    assert {finding.path for finding in state_machine_getattr_findings}.isdisjoint(
        DELEGATED_ANOMALY_MAP_HELPER_FILES
    )
    assert all(
        finding.classification_suggestion == "same-phase future anomaly-map read"
        for finding in state_machine_getattr_findings
    )
    assert {finding.path for finding in helper_getattr_findings} == {helper_boundary_path}
    assert all(
        finding.classification_suggestion == "approved helper boundary"
        for finding in helper_getattr_findings
    )
    assert ANOMALY_MAP_FUTURE_POOL_FILES.isdisjoint(EDGE_DETECTION_FILES)
    assert ANOMALY_MAP_FUTURE_POOL_FILES.isdisjoint(COPIED_OUTPUT_ADJACENT_FILES)
    assert ANOMALY_MAP_FUTURE_POOL_FILES.isdisjoint(DOT_DEBUFF_RUNTIME_STATE_FILES)


def test_enemy_dynamic_read_guardrail_limits_helper_to_approved_subset() -> None:
    references = _collect_helper_reference_paths()

    assert (
        CLASSIFICATION_BY_FILE["zsim/sim_progress/Buff/BuffXLogic/enemy_state_read.py"]
        == "approved helper boundary"
    )
    for helper_name, approved_files in APPROVED_HELPER_FILES_BY_NAME.items():
        helper_references = references[helper_name]
        approved_classifications = APPROVED_HELPER_CLASSIFICATIONS_BY_NAME[helper_name]
        migrated_files = MIGRATED_HELPER_FILES_BY_NAME[helper_name]
        classified_files = {
            path
            for path, classification in CLASSIFICATION_BY_FILE.items()
            if classification in approved_classifications
        }

        assert migrated_files <= helper_references["imports"]
        assert migrated_files <= helper_references["calls"]
        assert helper_references["imports"] <= approved_files
        assert helper_references["calls"] <= approved_files
        assert approved_files <= classified_files
        assert helper_references["imports"].isdisjoint(classified_files - approved_files)
        assert helper_references["calls"].isdisjoint(classified_files - approved_files)
        assert all(
            CLASSIFICATION_BY_FILE[path] in approved_classifications
            for path in helper_references["imports"] | helper_references["calls"]
        )


def test_enemy_dynamic_read_guardrail_tracks_helper_references_by_family() -> None:
    references = _collect_helper_reference_paths()
    family_references = {
        family_name: _helper_references_for_names(references, helper_names)
        for family_name, helper_names in HELPER_NAMES_BY_FAMILY.items()
    }
    migrated_shock_stun_files = (
        APPROVED_SHOCK_HELPER_FILES
        | APPROVED_STUN_HELPER_FILES
        | APPROVED_ENEMY_STATE_PORT_FILES
    )
    approved_shock_stun_files = migrated_shock_stun_files | APPROVED_COPIED_OUTPUT_STUN_HELPER_FILES
    edge_state_files = (
        APPROVED_EDGE_FROZEN_HELPER_FILES
        | APPROVED_EDGE_STUN_HELPER_FILES
        | APPROVED_EDGE_FROST_FROSTBITE_HELPER_FILES
        | APPROVED_EDGE_STATE_PORT_FILES
    )
    approved_edge_state_references = (
        edge_state_files | APPROVED_DOT_RUNTIME_FROST_FROSTBITE_HELPER_FILES
    )

    assert (
        APPROVED_ANOMALY_HELPER_FILES | APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES
        <= family_references["simple anomaly"]["imports"]
        <= APPROVED_HELPER_FILES_BY_NAME["read_enemy_anomaly_active"]
    )
    assert (
        APPROVED_ANOMALY_HELPER_FILES | APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES
        <= family_references["simple anomaly"]["calls"]
        <= APPROVED_HELPER_FILES_BY_NAME["read_enemy_anomaly_active"]
    )
    assert (
        migrated_shock_stun_files
        <= family_references["simple shock/stun"]["imports"]
        <= approved_shock_stun_files
    )
    assert (
        migrated_shock_stun_files
        <= family_references["simple shock/stun"]["calls"]
        <= approved_shock_stun_files
    )
    assert family_references["edge-state helpers"]["imports"] == approved_edge_state_references
    assert family_references["edge-state helpers"]["calls"] == approved_edge_state_references
    assert edge_state_files == EDGE_DETECTION_FILES
    assert APPROVED_DOT_RUNTIME_FROST_FROSTBITE_HELPER_FILES <= (DOT_DEBUFF_RUNTIME_STATE_FILES)
    assert family_references["anomaly-map helpers"]["imports"] == DELEGATED_ANOMALY_MAP_HELPER_FILES
    assert family_references["anomaly-map helpers"]["calls"] == DELEGATED_ANOMALY_MAP_HELPER_FILES
    assert (
        family_references["debuff mirror helpers"]["imports"]
        == APPROVED_DOT_DEBUFF_MIRROR_HELPER_FILES
    )
    assert (
        family_references["debuff mirror helpers"]["calls"]
        == APPROVED_DOT_DEBUFF_MIRROR_HELPER_FILES
    )


def test_enemy_dynamic_read_guardrail_limits_frozen_edge_helper_to_exact_files() -> None:
    references = _collect_helper_reference_paths()["read_enemy_frozen_edge_state"]
    helper_references = references["imports"] | references["calls"]

    assert references["imports"] == APPROVED_EDGE_FROZEN_HELPER_FILES
    assert references["calls"] == APPROVED_EDGE_FROZEN_HELPER_FILES
    assert helper_references <= EDGE_DETECTION_FILES
    assert helper_references.isdisjoint(EDGE_DETECTION_FILES - APPROVED_EDGE_FROZEN_HELPER_FILES)
    assert helper_references.isdisjoint(COPIED_OUTPUT_ADJACENT_FILES)
    assert helper_references.isdisjoint(DOT_DEBUFF_RUNTIME_STATE_FILES)
    assert all(CLASSIFICATION_BY_FILE[path] == "edge-detection read" for path in helper_references)


def test_enemy_dynamic_read_guardrail_limits_stun_edge_helper_to_exact_files() -> None:
    references = _collect_helper_reference_paths()["read_enemy_stun_edge_state"]
    helper_references = references["imports"] | references["calls"]

    assert references["imports"] == APPROVED_EDGE_STUN_HELPER_FILES
    assert references["calls"] == APPROVED_EDGE_STUN_HELPER_FILES
    assert helper_references <= EDGE_DETECTION_FILES
    assert helper_references.isdisjoint(EDGE_DETECTION_FILES - APPROVED_EDGE_STUN_HELPER_FILES)
    assert helper_references.isdisjoint(COPIED_OUTPUT_ADJACENT_FILES)
    assert helper_references.isdisjoint(DOT_DEBUFF_RUNTIME_STATE_FILES)
    assert all(CLASSIFICATION_BY_FILE[path] == "edge-detection read" for path in helper_references)


def test_enemy_dynamic_read_guardrail_limits_frost_frostbite_edge_helper_to_exact_files() -> None:
    references = _collect_helper_reference_paths()["read_enemy_frost_frostbite_edge_state"]
    helper_references = references["imports"] | references["calls"]

    assert references["imports"] == APPROVED_FROST_FROSTBITE_HELPER_FILES
    assert references["calls"] == APPROVED_FROST_FROSTBITE_HELPER_FILES
    assert helper_references <= (
        EDGE_DETECTION_FILES | APPROVED_DOT_RUNTIME_FROST_FROSTBITE_HELPER_FILES
    )
    assert (helper_references & EDGE_DETECTION_FILES) == APPROVED_EDGE_FROST_FROSTBITE_HELPER_FILES
    assert (
        helper_references & DOT_DEBUFF_RUNTIME_STATE_FILES
    ) == APPROVED_DOT_RUNTIME_FROST_FROSTBITE_HELPER_FILES
    assert helper_references.isdisjoint(
        EDGE_DETECTION_FILES - APPROVED_EDGE_FROST_FROSTBITE_HELPER_FILES
    )
    assert helper_references.isdisjoint(COPIED_OUTPUT_ADJACENT_FILES)
    assert helper_references.isdisjoint(
        DOT_DEBUFF_RUNTIME_STATE_FILES - APPROVED_DOT_RUNTIME_FROST_FROSTBITE_HELPER_FILES
    )
    assert helper_references.isdisjoint(ANOMALY_MAP_FUTURE_POOL_FILES)
    assert all(
        CLASSIFICATION_BY_FILE[path] in {"edge-detection read", "dot/debuff runtime-state read"}
        for path in helper_references
    )


def test_enemy_dynamic_read_guardrail_approves_copied_output_predicate_helpers_by_exact_path() -> (
    None
):
    copied_output_approved_files = (
        APPROVED_COPIED_OUTPUT_ANOMALY_HELPER_FILES | APPROVED_COPIED_OUTPUT_STUN_HELPER_FILES
    )

    assert set(APPROVED_COPIED_OUTPUT_HELPER_FILES_BY_NAME) == {
        "read_enemy_anomaly_active",
        "read_enemy_stun_active",
    }
    assert (
        APPROVED_COPIED_OUTPUT_HELPER_FILES_BY_NAME["read_enemy_anomaly_active"]
        == APPROVED_COPIED_OUTPUT_ANOMALY_HELPER_FILES
    )
    assert (
        APPROVED_COPIED_OUTPUT_HELPER_FILES_BY_NAME["read_enemy_stun_active"]
        == APPROVED_COPIED_OUTPUT_STUN_HELPER_FILES
    )
    assert copied_output_approved_files == COPIED_OUTPUT_ADJACENT_FILES
    assert copied_output_approved_files.isdisjoint(DOT_DEBUFF_RUNTIME_STATE_FILES)
    assert copied_output_approved_files.isdisjoint(ANOMALY_MAP_FUTURE_POOL_FILES)
    assert copied_output_approved_files.isdisjoint(EDGE_DETECTION_FILES)
    assert all(
        CLASSIFICATION_BY_FILE[path] == "copied-output-adjacent read"
        for path in copied_output_approved_files
    )


def test_enemy_dynamic_read_guardrail_approves_anomaly_map_helpers_by_exact_path() -> None:
    references = _collect_helper_reference_paths()

    assert APPROVED_ANOMALY_MAP_HELPER_FILES_BY_NAME == {
        "read_enemy_anomaly_state": {
            "zsim/sim_progress/Buff/BuffXLogic/AnomalyDebuffExitJudge.py",
        },
        "snapshot_enemy_anomaly_states": {
            "zsim/sim_progress/Buff/BuffXLogic/HailstormShrineIceBonus.py",
            "zsim/sim_progress/Buff/BuffXLogic/MiyabiAdditionalAbility_IgnoreIceRes.py",
        },
    }
    assert APPROVED_ANOMALY_MAP_HELPER_FILES == (
        DELEGATED_ANOMALY_MAP_HELPER_FILES | ANOMALY_MAP_FUTURE_POOL_FILES
    )
    assert APPROVED_ANOMALY_MAP_HELPER_FILES.isdisjoint(DOT_DEBUFF_RUNTIME_STATE_FILES)
    assert APPROVED_ANOMALY_MAP_HELPER_FILES.isdisjoint(COPIED_OUTPUT_ADJACENT_FILES)
    assert APPROVED_ANOMALY_MAP_HELPER_FILES.isdisjoint(EDGE_DETECTION_FILES)
    assert all(
        CLASSIFICATION_BY_FILE[path] == "same-phase future anomaly-map read"
        for path in ANOMALY_MAP_FUTURE_POOL_FILES
    )
    assert all(
        CLASSIFICATION_BY_FILE[path] == "delegated anomaly-map read"
        for path in DELEGATED_ANOMALY_MAP_HELPER_FILES
    )
    assert references["read_enemy_anomaly_state"]["imports"] == (
        APPROVED_ANOMALY_MAP_SINGLE_HELPER_FILES
    )
    assert references["read_enemy_anomaly_state"]["calls"] == (
        APPROVED_ANOMALY_MAP_SINGLE_HELPER_FILES
    )
    assert references["snapshot_enemy_anomaly_states"]["imports"] == (
        APPROVED_ANOMALY_MAP_SNAPSHOT_HELPER_FILES
    )
    assert references["snapshot_enemy_anomaly_states"]["calls"] == (
        APPROVED_ANOMALY_MAP_SNAPSHOT_HELPER_FILES
    )


def test_enemy_dynamic_read_guardrail_limits_hugo_copied_output_stun_helper_to_exact_file() -> None:
    references = _collect_helper_reference_paths()["read_enemy_stun_active"]
    copied_output_imports = references["imports"] & COPIED_OUTPUT_ADJACENT_FILES
    copied_output_calls = references["calls"] & COPIED_OUTPUT_ADJACENT_FILES

    assert APPROVED_COPIED_OUTPUT_STUN_HELPER_FILES == {
        "zsim/sim_progress/Buff/BuffXLogic/HugoCorePassiveTotalizeTrigger.py"
    }
    assert copied_output_imports == APPROVED_COPIED_OUTPUT_STUN_HELPER_FILES
    assert copied_output_calls == APPROVED_COPIED_OUTPUT_STUN_HELPER_FILES
    assert copied_output_imports.isdisjoint(APPROVED_COPIED_OUTPUT_ANOMALY_HELPER_FILES)
    assert copied_output_calls.isdisjoint(APPROVED_COPIED_OUTPUT_ANOMALY_HELPER_FILES)
    assert copied_output_imports.isdisjoint(DOT_DEBUFF_RUNTIME_STATE_FILES)
    assert copied_output_calls.isdisjoint(DOT_DEBUFF_RUNTIME_STATE_FILES)
    assert copied_output_imports.isdisjoint(ANOMALY_MAP_FUTURE_POOL_FILES)
    assert copied_output_calls.isdisjoint(ANOMALY_MAP_FUTURE_POOL_FILES)


def test_enemy_dynamic_read_guardrail_limits_copied_output_anomaly_helper_to_exact_files() -> None:
    references = _collect_helper_reference_paths()["read_enemy_anomaly_active"]
    copied_output_imports = references["imports"] & COPIED_OUTPUT_ADJACENT_FILES
    copied_output_calls = references["calls"] & COPIED_OUTPUT_ADJACENT_FILES

    assert DELEGATED_COPIED_OUTPUT_ANOMALY_HELPER_FILES == {
        "zsim/sim_progress/Buff/BuffXLogic/VivianCinema6Trigger.py",
        "zsim/sim_progress/Buff/BuffXLogic/VivianCorePassiveTrigger.py",
        "zsim/sim_progress/Buff/BuffXLogic/YanagiPolarityDisorderTrigger.py",
    }
    assert copied_output_imports == DELEGATED_COPIED_OUTPUT_ANOMALY_HELPER_FILES
    assert copied_output_calls == DELEGATED_COPIED_OUTPUT_ANOMALY_HELPER_FILES
    assert copied_output_imports <= APPROVED_COPIED_OUTPUT_ANOMALY_HELPER_FILES
    assert copied_output_calls <= APPROVED_COPIED_OUTPUT_ANOMALY_HELPER_FILES
    assert copied_output_imports.isdisjoint(APPROVED_COPIED_OUTPUT_STUN_HELPER_FILES)
    assert copied_output_calls.isdisjoint(APPROVED_COPIED_OUTPUT_STUN_HELPER_FILES)
    assert copied_output_imports.isdisjoint(DOT_DEBUFF_RUNTIME_STATE_FILES)
    assert copied_output_calls.isdisjoint(DOT_DEBUFF_RUNTIME_STATE_FILES)
    assert copied_output_imports.isdisjoint(ANOMALY_MAP_FUTURE_POOL_FILES)
    assert copied_output_calls.isdisjoint(ANOMALY_MAP_FUTURE_POOL_FILES)


def test_enemy_dynamic_read_guardrail_limits_vivian_dot_judge_helper_to_exact_file() -> None:
    references = _collect_helper_reference_paths()["read_enemy_anomaly_active"]
    dot_runtime_imports = references["imports"] & DOT_DEBUFF_RUNTIME_STATE_FILES
    dot_runtime_calls = references["calls"] & DOT_DEBUFF_RUNTIME_STATE_FILES

    assert APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES == {
        "zsim/sim_progress/Buff/BuffXLogic/VivianDotTrigger.py"
    }
    assert dot_runtime_imports == APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES
    assert dot_runtime_calls == APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES
    assert dot_runtime_imports.isdisjoint(
        DOT_DEBUFF_RUNTIME_STATE_FILES - APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES
    )
    assert dot_runtime_calls.isdisjoint(
        DOT_DEBUFF_RUNTIME_STATE_FILES - APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES
    )
    assert dot_runtime_imports.isdisjoint(COPIED_OUTPUT_ADJACENT_FILES)
    assert dot_runtime_calls.isdisjoint(COPIED_OUTPUT_ADJACENT_FILES)
    assert dot_runtime_imports.isdisjoint(ANOMALY_MAP_FUTURE_POOL_FILES)
    assert dot_runtime_calls.isdisjoint(ANOMALY_MAP_FUTURE_POOL_FILES)
    assert all(
        CLASSIFICATION_BY_FILE[path] == "dot/debuff runtime-state read"
        for path in APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES
    )


def test_enemy_dynamic_read_guardrail_limits_miyabi_debuff_mirror_reader_to_exact_file() -> (
    None
):
    references = _collect_helper_reference_paths()["MiyabiFrostburnDebuffMirrorReader"]
    helper_references = references["imports"] | references["calls"]

    assert APPROVED_DOT_DEBUFF_MIRROR_HELPER_FILES == {
        "zsim/sim_progress/Buff/BuffXLogic/MiyabiCoreSkill_IceFire.py"
    }
    assert references["imports"] == APPROVED_DOT_DEBUFF_MIRROR_HELPER_FILES
    assert references["calls"] == APPROVED_DOT_DEBUFF_MIRROR_HELPER_FILES
    assert helper_references <= DOT_DEBUFF_RUNTIME_STATE_FILES
    assert helper_references.isdisjoint(
        DOT_DEBUFF_RUNTIME_STATE_FILES - APPROVED_DOT_DEBUFF_MIRROR_HELPER_FILES
    )
    assert helper_references.isdisjoint(COPIED_OUTPUT_ADJACENT_FILES)
    assert helper_references.isdisjoint(ANOMALY_MAP_FUTURE_POOL_FILES)
    assert all(
        CLASSIFICATION_BY_FILE[path] == "dot/debuff runtime-state read"
        for path in helper_references
    )


def test_enemy_dynamic_read_guardrail_limits_yanagi_copied_output_anomaly_helper_to_exact_file() -> (
    None
):
    references = _collect_helper_reference_paths()["read_enemy_anomaly_active"]
    copied_output_imports = references["imports"] & COPIED_OUTPUT_ADJACENT_FILES
    copied_output_calls = references["calls"] & COPIED_OUTPUT_ADJACENT_FILES

    assert YANAGI_COPIED_OUTPUT_ANOMALY_HELPER_FILES == {
        "zsim/sim_progress/Buff/BuffXLogic/YanagiPolarityDisorderTrigger.py"
    }
    assert copied_output_imports & YANAGI_COPIED_OUTPUT_ANOMALY_HELPER_FILES == (
        YANAGI_COPIED_OUTPUT_ANOMALY_HELPER_FILES
    )
    assert copied_output_calls & YANAGI_COPIED_OUTPUT_ANOMALY_HELPER_FILES == (
        YANAGI_COPIED_OUTPUT_ANOMALY_HELPER_FILES
    )
    assert YANAGI_COPIED_OUTPUT_ANOMALY_HELPER_FILES <= (
        APPROVED_COPIED_OUTPUT_ANOMALY_HELPER_FILES
    )
    assert YANAGI_COPIED_OUTPUT_ANOMALY_HELPER_FILES.isdisjoint(
        APPROVED_COPIED_OUTPUT_STUN_HELPER_FILES
    )
    assert YANAGI_COPIED_OUTPUT_ANOMALY_HELPER_FILES.isdisjoint(DOT_DEBUFF_RUNTIME_STATE_FILES)
    assert YANAGI_COPIED_OUTPUT_ANOMALY_HELPER_FILES.isdisjoint(ANOMALY_MAP_FUTURE_POOL_FILES)
    assert YANAGI_COPIED_OUTPUT_ANOMALY_HELPER_FILES.isdisjoint(EDGE_DETECTION_FILES)


def test_enemy_dynamic_read_guardrail_keeps_excluded_families_out_of_helper_scope() -> None:
    references = _collect_helper_reference_paths()
    anomaly_references_by_kind = _helper_references_for_names(
        references, HELPER_NAMES_BY_FAMILY["simple anomaly"]
    )
    shock_stun_references_by_kind = _helper_references_for_names(
        references, HELPER_NAMES_BY_FAMILY["simple shock/stun"]
    )
    edge_state_references_by_kind = _helper_references_for_names(
        references, HELPER_NAMES_BY_FAMILY["edge-state helpers"]
    )
    anomaly_map_references_by_kind = _helper_references_for_names(
        references, HELPER_NAMES_BY_FAMILY["anomaly-map helpers"]
    )
    debuff_mirror_references_by_kind = _helper_references_for_names(
        references, HELPER_NAMES_BY_FAMILY["debuff mirror helpers"]
    )
    shock_stun_references = (
        shock_stun_references_by_kind["imports"] | shock_stun_references_by_kind["calls"]
    )
    anomaly_references = anomaly_references_by_kind["imports"] | anomaly_references_by_kind["calls"]
    edge_state_references = (
        edge_state_references_by_kind["imports"] | edge_state_references_by_kind["calls"]
    )
    anomaly_map_references = (
        anomaly_map_references_by_kind["imports"] | anomaly_map_references_by_kind["calls"]
    )
    debuff_mirror_references = (
        debuff_mirror_references_by_kind["imports"]
        | debuff_mirror_references_by_kind["calls"]
    )

    assert all(
        CLASSIFICATION_BY_FILE[path] == "edge-detection read" for path in EDGE_DETECTION_FILES
    )
    assert all(
        CLASSIFICATION_BY_FILE[path] == "copied-output-adjacent read"
        for path in COPIED_OUTPUT_ADJACENT_FILES
    )
    assert all(
        CLASSIFICATION_BY_FILE[path] == "dot/debuff runtime-state read"
        for path in DOT_DEBUFF_RUNTIME_STATE_FILES
    )
    assert anomaly_references.isdisjoint(EDGE_DETECTION_FILES)
    assert (
        anomaly_references & COPIED_OUTPUT_ADJACENT_FILES
    ) <= APPROVED_COPIED_OUTPUT_ANOMALY_HELPER_FILES
    assert anomaly_references.isdisjoint(
        COPIED_OUTPUT_ADJACENT_FILES - APPROVED_COPIED_OUTPUT_ANOMALY_HELPER_FILES
    )
    assert (
        anomaly_references & DOT_DEBUFF_RUNTIME_STATE_FILES
    ) == APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES
    assert anomaly_references.isdisjoint(
        DOT_DEBUFF_RUNTIME_STATE_FILES - APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES
    )
    assert anomaly_references.isdisjoint(ANOMALY_MAP_FUTURE_POOL_FILES)
    assert shock_stun_references.isdisjoint(EDGE_DETECTION_FILES)
    assert (
        shock_stun_references & COPIED_OUTPUT_ADJACENT_FILES
    ) <= APPROVED_COPIED_OUTPUT_STUN_HELPER_FILES
    assert shock_stun_references.isdisjoint(
        COPIED_OUTPUT_ADJACENT_FILES - APPROVED_COPIED_OUTPUT_STUN_HELPER_FILES
    )
    assert shock_stun_references.isdisjoint(DOT_DEBUFF_RUNTIME_STATE_FILES)
    assert shock_stun_references.isdisjoint(ANOMALY_MAP_FUTURE_POOL_FILES)
    assert edge_state_references <= (
        EDGE_DETECTION_FILES | APPROVED_DOT_RUNTIME_FROST_FROSTBITE_HELPER_FILES
    )
    assert edge_state_references.isdisjoint(COPIED_OUTPUT_ADJACENT_FILES)
    assert (
        edge_state_references & DOT_DEBUFF_RUNTIME_STATE_FILES
    ) == APPROVED_DOT_RUNTIME_FROST_FROSTBITE_HELPER_FILES
    assert edge_state_references.isdisjoint(
        DOT_DEBUFF_RUNTIME_STATE_FILES - APPROVED_DOT_RUNTIME_FROST_FROSTBITE_HELPER_FILES
    )
    assert edge_state_references.isdisjoint(ANOMALY_MAP_FUTURE_POOL_FILES)
    assert anomaly_map_references == DELEGATED_ANOMALY_MAP_HELPER_FILES
    assert debuff_mirror_references == APPROVED_DOT_DEBUFF_MIRROR_HELPER_FILES
    assert debuff_mirror_references <= DOT_DEBUFF_RUNTIME_STATE_FILES
    assert debuff_mirror_references.isdisjoint(
        DOT_DEBUFF_RUNTIME_STATE_FILES - APPROVED_DOT_DEBUFF_MIRROR_HELPER_FILES
    )
    assert debuff_mirror_references.isdisjoint(COPIED_OUTPUT_ADJACENT_FILES)
    assert debuff_mirror_references.isdisjoint(ANOMALY_MAP_FUTURE_POOL_FILES)


def test_enemy_dynamic_read_guardrail_preserves_excluded_pool_guardrails() -> None:
    findings = _collect_findings()
    finding_paths = {finding.path for finding in findings}
    references = _collect_helper_reference_paths()
    direct_excluded_read_files = (
        EXCLUDED_RUNTIME_STATE_AND_ANOMALY_MAP_FILES
        - APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES
        - APPROVED_DOT_DEBUFF_MIRROR_HELPER_FILES
    )
    copied_output_approved_files: set[str] = set()
    for approved_files in APPROVED_COPIED_OUTPUT_HELPER_FILES_BY_NAME.values():
        copied_output_approved_files.update(approved_files)

    assert DOT_DEBUFF_RUNTIME_STATE_FILES == {
        "zsim/sim_progress/Buff/BuffXLogic/MiyabiCoreSkill_IceFire.py",
        "zsim/sim_progress/Buff/BuffXLogic/VivianDotTrigger.py",
    }
    assert ANOMALY_MAP_FUTURE_POOL_FILES == set()
    assert direct_excluded_read_files <= EXPECTED_DIRECT_READ_FILES
    assert direct_excluded_read_files <= finding_paths
    assert APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES <= DOT_DEBUFF_RUNTIME_STATE_FILES
    assert APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES.isdisjoint(finding_paths)
    assert APPROVED_DOT_RUNTIME_FROST_FROSTBITE_HELPER_FILES <= DOT_DEBUFF_RUNTIME_STATE_FILES
    assert APPROVED_DOT_DEBUFF_MIRROR_HELPER_FILES <= DOT_DEBUFF_RUNTIME_STATE_FILES
    assert APPROVED_DOT_DEBUFF_MIRROR_HELPER_FILES.isdisjoint(finding_paths)
    assert all(
        CLASSIFICATION_BY_FILE[path] == "dot/debuff runtime-state read"
        for path in DOT_DEBUFF_RUNTIME_STATE_FILES
    )
    assert all(
        CLASSIFICATION_BY_FILE[path] == "same-phase future anomaly-map read"
        for path in ANOMALY_MAP_FUTURE_POOL_FILES
    )
    assert all(
        CLASSIFICATION_BY_FILE[path] == "delegated anomaly-map read"
        for path in DELEGATED_ANOMALY_MAP_HELPER_FILES
    )
    assert copied_output_approved_files == COPIED_OUTPUT_ADJACENT_FILES
    assert copied_output_approved_files.isdisjoint(EXCLUDED_RUNTIME_STATE_AND_ANOMALY_MAP_FILES)

    for helper_name, helper_references in references.items():
        referenced_files = helper_references["imports"] | helper_references["calls"]

        if helper_name == "read_enemy_anomaly_active":
            assert (
                APPROVED_HELPER_FILES_BY_NAME[helper_name]
                & EXCLUDED_RUNTIME_STATE_AND_ANOMALY_MAP_FILES
            ) == APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES
            assert (
                referenced_files & EXCLUDED_RUNTIME_STATE_AND_ANOMALY_MAP_FILES
            ) == APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES
            assert referenced_files.isdisjoint(ANOMALY_MAP_FUTURE_POOL_FILES)
            assert referenced_files.isdisjoint(
                DOT_DEBUFF_RUNTIME_STATE_FILES - APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES
            )
            continue
        if helper_name == "read_enemy_frost_frostbite_edge_state":
            assert (
                APPROVED_HELPER_FILES_BY_NAME[helper_name]
                & EXCLUDED_RUNTIME_STATE_AND_ANOMALY_MAP_FILES
            ) == APPROVED_DOT_RUNTIME_FROST_FROSTBITE_HELPER_FILES
            assert (
                referenced_files & EXCLUDED_RUNTIME_STATE_AND_ANOMALY_MAP_FILES
            ) == APPROVED_DOT_RUNTIME_FROST_FROSTBITE_HELPER_FILES
            assert referenced_files.isdisjoint(ANOMALY_MAP_FUTURE_POOL_FILES)
            assert referenced_files.isdisjoint(
                DOT_DEBUFF_RUNTIME_STATE_FILES - APPROVED_DOT_RUNTIME_FROST_FROSTBITE_HELPER_FILES
            )
            continue
        if helper_name == "MiyabiFrostburnDebuffMirrorReader":
            assert (
                APPROVED_HELPER_FILES_BY_NAME[helper_name]
                & EXCLUDED_RUNTIME_STATE_AND_ANOMALY_MAP_FILES
            ) == APPROVED_DOT_DEBUFF_MIRROR_HELPER_FILES
            assert (
                referenced_files & EXCLUDED_RUNTIME_STATE_AND_ANOMALY_MAP_FILES
            ) == APPROVED_DOT_DEBUFF_MIRROR_HELPER_FILES
            assert referenced_files.isdisjoint(
                DOT_DEBUFF_RUNTIME_STATE_FILES - APPROVED_DOT_DEBUFF_MIRROR_HELPER_FILES
            )
            assert referenced_files.isdisjoint(COPIED_OUTPUT_ADJACENT_FILES)
            assert referenced_files.isdisjoint(ANOMALY_MAP_FUTURE_POOL_FILES)
            continue
        if helper_name == "read_enemy_anomaly_state":
            assert (
                APPROVED_HELPER_FILES_BY_NAME[helper_name]
                == APPROVED_ANOMALY_MAP_SINGLE_HELPER_FILES
            )
            assert referenced_files == APPROVED_ANOMALY_MAP_SINGLE_HELPER_FILES
            assert referenced_files <= DELEGATED_ANOMALY_MAP_HELPER_FILES
            assert referenced_files.isdisjoint(EXCLUDED_RUNTIME_STATE_AND_ANOMALY_MAP_FILES)
            continue
        if helper_name == "snapshot_enemy_anomaly_states":
            assert (
                APPROVED_HELPER_FILES_BY_NAME[helper_name]
                == APPROVED_ANOMALY_MAP_SNAPSHOT_HELPER_FILES
            )
            assert referenced_files == APPROVED_ANOMALY_MAP_SNAPSHOT_HELPER_FILES
            assert referenced_files <= DELEGATED_ANOMALY_MAP_HELPER_FILES
            assert referenced_files.isdisjoint(EXCLUDED_RUNTIME_STATE_AND_ANOMALY_MAP_FILES)
            continue
        assert APPROVED_HELPER_FILES_BY_NAME[helper_name].isdisjoint(
            EXCLUDED_RUNTIME_STATE_AND_ANOMALY_MAP_FILES
        )
        assert referenced_files.isdisjoint(EXCLUDED_RUNTIME_STATE_AND_ANOMALY_MAP_FILES)


def test_enemy_dynamic_read_guardrail_keeps_runtime_state_rollback_packet_exact() -> None:
    references = _collect_helper_reference_paths()
    copied_output_approved_files: set[str] = set()
    for approved_files in APPROVED_COPIED_OUTPUT_HELPER_FILES_BY_NAME.values():
        copied_output_approved_files.update(approved_files)

    assert DOT_DEBUFF_RUNTIME_STATE_FILES == {
        "zsim/sim_progress/Buff/BuffXLogic/MiyabiCoreSkill_IceFire.py",
        "zsim/sim_progress/Buff/BuffXLogic/VivianDotTrigger.py",
    }
    assert APPROVED_DOT_DEBUFF_MIRROR_HELPER_FILES == {
        "zsim/sim_progress/Buff/BuffXLogic/MiyabiCoreSkill_IceFire.py"
    }
    assert references["MiyabiFrostburnDebuffMirrorReader"] == {
        "imports": APPROVED_DOT_DEBUFF_MIRROR_HELPER_FILES,
        "calls": APPROVED_DOT_DEBUFF_MIRROR_HELPER_FILES,
    }
    assert references["read_enemy_anomaly_active"]["imports"] & (
        DOT_DEBUFF_RUNTIME_STATE_FILES
    ) == APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES
    assert references["read_enemy_anomaly_active"]["calls"] & (
        DOT_DEBUFF_RUNTIME_STATE_FILES
    ) == APPROVED_DOT_RUNTIME_JUDGE_ANOMALY_HELPER_FILES
    assert references["read_enemy_shock_active"]["imports"].isdisjoint(
        DOT_DEBUFF_RUNTIME_STATE_FILES
    )
    assert references["read_enemy_shock_active"]["calls"].isdisjoint(
        DOT_DEBUFF_RUNTIME_STATE_FILES
    )
    assert references["read_enemy_stun_active"]["imports"].isdisjoint(
        DOT_DEBUFF_RUNTIME_STATE_FILES
    )
    assert references["read_enemy_stun_active"]["calls"].isdisjoint(
        DOT_DEBUFF_RUNTIME_STATE_FILES
    )
    assert references["read_enemy_frost_frostbite_edge_state"]["imports"] & (
        DOT_DEBUFF_RUNTIME_STATE_FILES
    ) == APPROVED_DOT_RUNTIME_FROST_FROSTBITE_HELPER_FILES
    assert references["read_enemy_frost_frostbite_edge_state"]["calls"] & (
        DOT_DEBUFF_RUNTIME_STATE_FILES
    ) == APPROVED_DOT_RUNTIME_FROST_FROSTBITE_HELPER_FILES
    assert references["read_enemy_anomaly_state"]["imports"].isdisjoint(
        DOT_DEBUFF_RUNTIME_STATE_FILES
    )
    assert references["read_enemy_anomaly_state"]["calls"].isdisjoint(
        DOT_DEBUFF_RUNTIME_STATE_FILES
    )
    assert references["snapshot_enemy_anomaly_states"]["imports"].isdisjoint(
        DOT_DEBUFF_RUNTIME_STATE_FILES
    )
    assert references["snapshot_enemy_anomaly_states"]["calls"].isdisjoint(
        DOT_DEBUFF_RUNTIME_STATE_FILES
    )
    assert copied_output_approved_files.isdisjoint(DOT_DEBUFF_RUNTIME_STATE_FILES)


def test_enemy_dynamic_read_guardrail_keeps_copied_output_matrix_exact() -> None:
    findings = _collect_findings()
    copied_findings = [
        finding for finding in findings if finding.path in COPIED_OUTPUT_ADJACENT_FILES
    ]
    copied_output_direct_read_files = (
        COPIED_OUTPUT_ADJACENT_FILES - DELEGATED_COPIED_OUTPUT_HELPER_FILES
    )
    matched_by_path = {
        path: [finding.matched_expression for finding in copied_findings if finding.path == path]
        for path in COPIED_OUTPUT_ADJACENT_FILES
    }
    references = _collect_helper_reference_paths()

    assert {finding.path for finding in copied_findings} == copied_output_direct_read_files
    assert matched_by_path == {
        "zsim/sim_progress/Buff/BuffXLogic/HugoCorePassiveTotalizeTrigger.py": [],
        "zsim/sim_progress/Buff/BuffXLogic/VivianCinema6Trigger.py": [
            "self.record.enemy.dynamic.get_active_anomaly()",
        ],
        "zsim/sim_progress/Buff/BuffXLogic/VivianCorePassiveTrigger.py": [
            "self.record.enemy.dynamic.get_active_anomaly()",
        ],
        "zsim/sim_progress/Buff/BuffXLogic/YanagiPolarityDisorderTrigger.py": [],
    }
    assert all(
        finding.classification_suggestion == "copied-output-adjacent read"
        for finding in copied_findings
    )
    for helper_name, helper_reference in references.items():
        copied_output_references = (
            helper_reference["imports"] | helper_reference["calls"]
        ) & COPIED_OUTPUT_ADJACENT_FILES
        approved_files = APPROVED_COPIED_OUTPUT_HELPER_FILES_BY_NAME.get(helper_name, set())

        assert copied_output_references <= approved_files


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
    assert any(
        "zsim/sim_progress/Buff/BuffXLogic/_synthetic_enemy_dynamic_fixture.py:2"
        in message
        for message in messages
    )
    assert any(
        "zsim/sim_progress/Buff/BuffXLogic/_synthetic_enemy_dynamic_fixture.py:3"
        in message
        for message in messages
    )
    assert all(
        "classification suggestion: unrelated retained compatibility" in message
        for message in messages
    )
    assert all(
        "next action: classify the read family before helper design or migration"
        in message
        for message in messages
    )
    assert any(
        "matched expression: record.enemy.dynamic.is_under_anomaly()" in message
        for message in messages
    )
    assert any("matched expression: record.enemy.dynamic.stun" in message for message in messages)


def test_enemy_dynamic_read_guardrail_detects_getattr_enemy_dynamic_reads() -> None:
    source = (
        "def judge(record, name):\n"
        "    dynamic_read = getattr(record.enemy.dynamic, name)\n"
        "    ignored = getattr(record.enemy_dynamic, name)\n"
        "    return dynamic_read, ignored\n"
    )
    path = BUFF_XLOGIC_ROOT / "_synthetic_enemy_dynamic_fixture.py"

    findings = _collect_findings_from_source(path, source)

    assert len(findings) == 1
    assert findings[0].matched_expression == "getattr(record.enemy.dynamic, name)"
    assert findings[0].classification_suggestion == "unrelated retained compatibility"


def test_enemy_dynamic_read_guardrail_uses_ast_not_text_matching() -> None:
    source = (
        "def clean(record):\n"
        "    '''record.enemy.dynamic.stun enemy.dynamic.is_under_anomaly()'''\n"
        "    # record.enemy.dynamic.frozen is historical evidence only.\n"
        "    return record.enemy_dynamic_stun\n"
    )
    path = BUFF_XLOGIC_ROOT / "_synthetic_enemy_dynamic_fixture.py"

    assert _collect_findings_from_source(path, source) == []
