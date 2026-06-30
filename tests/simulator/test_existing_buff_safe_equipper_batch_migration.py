from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from zsim.sim_progress.Buff.BuffXLogic._preparation_helpers import (
    ensure_equipper_template_record,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT_PATH = (
    PROJECT_ROOT
    / "scripts"
    / "ralph"
    / "checkpoints"
    / "2026-06-30-US-001-existing-buff-safe-equipper-batch-census.json"
)

EXPECTED_SAFE_MECHANICAL_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/ElectroLipGlossAtkAndDmgBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/FlightOfFancy.py",
    "zsim/sim_progress/Buff/BuffXLogic/FreedomBlues.py",
    "zsim/sim_progress/Buff/BuffXLogic/HailstormShrineIceBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/MagneticStormAlphaAMBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/MagneticStormBravoApBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/MarcatoDesireAtkBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/PuzzleSphereExDmgBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/ShadowHarmony4.py",
    "zsim/sim_progress/Buff/BuffXLogic/TheVault.py",
    "zsim/sim_progress/Buff/BuffXLogic/TimeweaverApBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_CA.py",
    "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_E_EX.py",
)

EXPECTED_ITEM_LOOKUP_LITERALS = {
    "zsim/sim_progress/Buff/BuffXLogic/ElectroLipGlossAtkAndDmgBonus.py": "触电唇彩",
    "zsim/sim_progress/Buff/BuffXLogic/FlightOfFancy.py": "飞鸟星梦",
    "zsim/sim_progress/Buff/BuffXLogic/FreedomBlues.py": "自由蓝调",
    "zsim/sim_progress/Buff/BuffXLogic/HailstormShrineIceBonus.py": "霰落星殿",
    "zsim/sim_progress/Buff/BuffXLogic/MagneticStormAlphaAMBonus.py": "「电磁暴」-壹式",
    "zsim/sim_progress/Buff/BuffXLogic/MagneticStormBravoApBonus.py": "「电磁暴」-贰式",
    "zsim/sim_progress/Buff/BuffXLogic/MarcatoDesireAtkBonus.py": "强音热望",
    "zsim/sim_progress/Buff/BuffXLogic/PuzzleSphereExDmgBonus.py": "幻变魔方",
    "zsim/sim_progress/Buff/BuffXLogic/ShadowHarmony4.py": "如影相随",
    "zsim/sim_progress/Buff/BuffXLogic/TheVault.py": "聚宝箱",
    "zsim/sim_progress/Buff/BuffXLogic/TimeweaverApBonus.py": "时流贤者",
    "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_CA.py": "啄木鸟电音",
    "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_E_EX.py": "啄木鸟电音",
}


def _safe_mechanical_entries() -> list[dict[str, str]]:
    with CHECKPOINT_PATH.open(encoding="utf-8") as handle:
        checkpoint = json.load(handle)
    assert checkpoint["schema"] == "zsim-existing-buff-safe-equipper-batch-census.v1"
    assert checkpoint["us002_target"] == (
        "existing-buff-safe-equipper-template-batch-migration"
    )
    return list(checkpoint["safe_mechanical"])


def test_us002_safe_equipper_batch_matches_us001_checkpoint_scope() -> None:
    entries = _safe_mechanical_entries()

    assert tuple(entry["file"] for entry in entries) == EXPECTED_SAFE_MECHANICAL_FILES
    assert "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_NA.py" not in {
        entry["file"] for entry in entries
    }


@pytest.mark.parametrize("entry", _safe_mechanical_entries())
def test_us002_safe_equipper_files_use_preparation_context_helper_path(
    entry: dict[str, str],
) -> None:
    source = (PROJECT_ROOT / entry["file"]).read_text(encoding="utf-8")

    assert "prepare_with_context(" in source
    assert "ensure_equipper_template_record(" in source
    assert "build_preparation_context_from_buff" in source
    assert f'item_name="{EXPECTED_ITEM_LOOKUP_LITERALS[entry["file"]]}"' in source
    assert "JudgeTools.find_equipper" not in source
    assert "JudgeTools.find_exist_buff_dict" not in source
    assert "from .. import Buff, JudgeTools" not in source


class _Record:
    pass


class _RecordingPreparationContext:
    def __init__(self, registry: dict[str, dict[str, object]]) -> None:
        self.registry = registry
        self.find_equipper_calls: list[str] = []
        self.find_sub_exist_buff_dict_calls: list[str] = []

    def find_equipper(self, item_name: str) -> str:
        self.find_equipper_calls.append(item_name)
        return f"equipper:{item_name}"

    def find_sub_exist_buff_dict(self, owner_name: str) -> dict[str, object]:
        self.find_sub_exist_buff_dict_calls.append(owner_name)
        return self.registry[owner_name]


def _logic(*, index: str = "template-index") -> SimpleNamespace:
    return SimpleNamespace(
        equipper=None,
        buff_0=None,
        record=None,
        buff_instance=SimpleNamespace(ft=SimpleNamespace(index=index)),
    )


def _buff_0(record: object | None = None) -> SimpleNamespace:
    return SimpleNamespace(history=SimpleNamespace(record=record))


def test_ensure_equipper_template_record_preserves_equipper_index_and_record_identity() -> None:
    template = _buff_0()
    context = _RecordingPreparationContext(
        {"equipper:item": {"template-index": template}}
    )
    logic = _logic()

    record = ensure_equipper_template_record(
        logic,
        item_name="item",
        record_factory=_Record,
        context_builder=lambda buff_instance: context,
    )

    assert context.find_equipper_calls == ["item"]
    assert context.find_sub_exist_buff_dict_calls == ["equipper:item"]
    assert logic.equipper == "equipper:item"
    assert logic.buff_0 is template
    assert isinstance(record, _Record)
    assert logic.record is record
    assert template.history.record is record

    second_record = ensure_equipper_template_record(
        logic,
        item_name="item",
        record_factory=lambda: pytest.fail("record should be reused"),
        context_builder=lambda buff_instance: context,
    )

    assert second_record is record
    assert context.find_equipper_calls == ["item"]
    assert context.find_sub_exist_buff_dict_calls == ["equipper:item"]


@pytest.mark.parametrize("registry", [{}, {"equipper:item": {}}])
def test_ensure_equipper_template_record_preserves_missing_equipper_or_index_errors(
    registry: dict[str, dict[str, object]],
) -> None:
    context = _RecordingPreparationContext(registry)

    with pytest.raises(KeyError):
        ensure_equipper_template_record(
            _logic(index="missing-index"),
            item_name="item",
            record_factory=_Record,
            context_builder=lambda buff_instance: context,
        )
