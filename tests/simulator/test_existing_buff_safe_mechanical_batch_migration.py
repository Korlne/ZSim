from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from zsim.sim_progress.Buff.BuffXLogic._preparation_helpers import (
    ensure_owner_template_record,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT_PATH = (
    PROJECT_ROOT
    / "scripts"
    / "ralph"
    / "checkpoints"
    / "2026-06-30-US-001-existing-buff-safe-mechanical-batch-census.json"
)

EXPECTED_SAFE_MECHANICAL_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/HugoAdditionalAbilityExtraQTEDmgBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/HugoCorePassiveEXStunBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/JaneAdditionalAbilityPhyBuildupBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/JaneCoreSkillStrikeCritDmgBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/JanePassionStatePhyBuildupBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/JanePassionStateTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/LighterUniqueSkillStunTimeLimitBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/LinaAdditionalSkillEleDMGBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/LyconAdditionalAbilityStunVulnerability.py",
    "zsim/sim_progress/Buff/BuffXLogic/MiyabiAdditionalAbility_IgnoreIceRes.py",
    "zsim/sim_progress/Buff/BuffXLogic/MiyabiCoreSkill_FrostBurn.py",
    "zsim/sim_progress/Buff/BuffXLogic/NikoleCoreSkillDefReduction.py",
    "zsim/sim_progress/Buff/BuffXLogic/SeedCinema4Bonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/SeedCinema4Trigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/SeedDirectStrikeBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/SeedDirectStrikeTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/SeedOnslaughtBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/Soldier11AdditionalSkillExtraFireDMGBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/TriggerCoreSkillStunDMGBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/VivianCinema1Debuff.py",
    "zsim/sim_progress/Buff/BuffXLogic/YanagiCinema6EXDmgBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/YuzuhaCinem1EleResReduce.py",
    "zsim/sim_progress/Buff/BuffXLogic/YuzuhaCorePassiveSweetScare.py",
)


def _safe_mechanical_entries() -> list[dict[str, str]]:
    with CHECKPOINT_PATH.open(encoding="utf-8") as handle:
        checkpoint = json.load(handle)
    assert checkpoint["schema"] == "zsim-existing-buff-safe-mechanical-batch-census.v1"
    assert checkpoint["us002_target"] == (
        "existing-buff-safe-mechanical-owner-template-batch-migration"
    )
    return list(checkpoint["safe_mechanical"])


def test_us002_safe_mechanical_batch_matches_us001_checkpoint_scope() -> None:
    entries = _safe_mechanical_entries()

    assert tuple(entry["file"] for entry in entries) == EXPECTED_SAFE_MECHANICAL_FILES
    assert "zsim/sim_progress/Buff/BuffXLogic/YanagiPolarityDisorderTrigger.py" not in {
        entry["file"] for entry in entries
    }


@pytest.mark.parametrize("entry", _safe_mechanical_entries())
def test_us002_safe_mechanical_files_use_preparation_context_helper_path(
    entry: dict[str, str],
) -> None:
    source = (PROJECT_ROOT / entry["file"]).read_text(encoding="utf-8")

    assert "prepare_with_context(" in source
    assert "ensure_owner_template_record(" in source
    assert "build_preparation_context_from_buff" in source
    assert f"owner_name={entry['owner']!r}" in source
    assert "JudgeTools.find_exist_buff_dict" not in source
    assert "from .. import Buff, JudgeTools" not in source


class _Record:
    pass


class _RecordingPreparationContext:
    def __init__(self, registry: dict[str, dict[str, object]]) -> None:
        self.registry = registry
        self.calls: list[str] = []

    def find_sub_exist_buff_dict(self, owner_name: str) -> dict[str, object]:
        self.calls.append(owner_name)
        return self.registry[owner_name]


def _logic(*, index: str = "template-index") -> SimpleNamespace:
    return SimpleNamespace(
        buff_0=None,
        record=None,
        buff_instance=SimpleNamespace(ft=SimpleNamespace(index=index)),
    )


def _buff_0(record: object | None = None) -> SimpleNamespace:
    return SimpleNamespace(history=SimpleNamespace(record=record))


def test_ensure_owner_template_record_preserves_owner_index_and_record_identity() -> None:
    template = _buff_0()
    context = _RecordingPreparationContext({"owner": {"template-index": template}})
    logic = _logic()

    record = ensure_owner_template_record(
        logic,
        owner_name="owner",
        record_factory=_Record,
        context_builder=lambda buff_instance: context,
    )

    assert context.calls == ["owner"]
    assert logic.buff_0 is template
    assert isinstance(record, _Record)
    assert logic.record is record
    assert template.history.record is record

    second_record = ensure_owner_template_record(
        logic,
        owner_name="owner",
        record_factory=lambda: pytest.fail("record should be reused"),
        context_builder=lambda buff_instance: context,
    )

    assert second_record is record
    assert context.calls == ["owner"]


@pytest.mark.parametrize("registry", [{}, {"owner": {}}])
def test_ensure_owner_template_record_preserves_missing_owner_or_index_errors(
    registry: dict[str, dict[str, object]],
) -> None:
    context = _RecordingPreparationContext(registry)

    with pytest.raises(KeyError):
        ensure_owner_template_record(
            _logic(index="missing-index"),
            owner_name="owner",
            record_factory=_Record,
            context_builder=lambda buff_instance: context,
        )
