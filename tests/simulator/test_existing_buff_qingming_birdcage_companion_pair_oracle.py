from __future__ import annotations

import importlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT_PATH = (
    PROJECT_ROOT
    / "scripts"
    / "ralph"
    / "checkpoints"
    / "2026-06-30-US-001-existing-buff-qingming-birdcage-companion-pair-oracle.json"
)

ITEM_NAME = "青溟笼舍"
SUB_EXIST_BUFF_DICT = {"sub": "registry"}
TICK_NOW = 1314

SELECTED_ROWS = (
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/QingmingBirdcageCompanionEthDmgBonus.py",
        "module": "QingmingBirdcageCompanionEthDmgBonus",
        "logic": "QingmingBirdcageCompanionEthDmgBonus",
        "record": "QingmingBirdcageCompanionEthDmgBonusRecord",
        "item": ITEM_NAME,
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/QingmingBirdcageCompanionSheerAtkBonus.py",
        "module": "QingmingBirdcageCompanionSheerAtkBonus",
        "logic": "QingmingBirdcageCompanionSheerAtkBonus",
        "record": "QingmingBirdcageCompanionSheerAtkBonusRecord",
        "item": ITEM_NAME,
    },
)

SELECTED_FILES = tuple(row["file"] for row in SELECTED_ROWS)
EXCLUDED_OR_DEFERRED_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/FlamemakerShakerDmgBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/SharpenedStingerPhyDmgBonus.py",
)


def _module(row: dict[str, str]) -> Any:
    return importlib.import_module(
        f"zsim.sim_progress.Buff.BuffXLogic.{row['module']}"
    )


def _buff_0(*, record: object | None = None, count: int = 0) -> SimpleNamespace:
    return SimpleNamespace(
        history=SimpleNamespace(record=record),
        dy=SimpleNamespace(count=count, active=False, built_in_buff_box=[]),
    )


class _RecordingBuffInstance:
    def __init__(
        self,
        *,
        index: str = "qingming-template-index",
        tick: int = TICK_NOW,
        maxcount: int = 9,
    ) -> None:
        self.sim_instance = SimpleNamespace(tick=tick)
        self.ft = SimpleNamespace(index=index, maxcount=maxcount)
        self.dy = SimpleNamespace(count=0, active=False, built_in_buff_box=[])
        self.simple_start_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
        self.update_to_buff_0_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def simple_start(self, *args: object, **kwargs: object) -> None:
        self.simple_start_calls.append((args, dict(kwargs)))

    def update_to_buff_0(self, *args: object, **kwargs: object) -> None:
        self.update_to_buff_0_calls.append((args, dict(kwargs)))


def _install_equipper_lookup(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    item: str,
    index: str,
    buff_0: SimpleNamespace,
    registry: dict[str, dict[str, object]] | None = None,
) -> tuple[list[tuple[str, object]], list[object]]:
    equipper = f"equipper:{item}"
    lookup_registry = registry if registry is not None else {equipper: {index: buff_0}}
    equipper_calls: list[tuple[str, object]] = []
    existing_buff_calls: list[object] = []

    class FakePreparationContext:
        def __init__(self, sim_instance: object) -> None:
            self.sim_instance = sim_instance

        def find_equipper(self, item_name: str) -> str:
            equipper_calls.append((item_name, self.sim_instance))
            return equipper

        def find_sub_exist_buff_dict(self, owner_name: str) -> dict[str, object]:
            existing_buff_calls.append(self.sim_instance)
            return lookup_registry[owner_name]

    def fake_context_builder(buff_instance: object) -> FakePreparationContext:
        return FakePreparationContext(buff_instance.sim_instance)

    monkeypatch.setattr(module, "build_preparation_context_from_buff", fake_context_builder)
    return equipper_calls, existing_buff_calls


def _install_preparation(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    harness: _RecordingBuffInstance,
    buff_0: SimpleNamespace,
    char: object,
    preload_data: object,
) -> list[dict[str, object]]:
    preparation_calls: list[dict[str, object]] = []

    def fake_check_preparation(
        *,
        buff_instance: object,
        buff_0: object,
        **kwargs: object,
    ) -> None:
        assert buff_instance is harness
        assert buff_0 is buff_0_ref
        observed_kwargs = dict(kwargs)
        observed_kwargs.pop("preparation_context", None)
        preparation_calls.append(observed_kwargs)
        record = buff_0_ref.history.record
        if kwargs.get("equipper") is not None:
            record.equipper = f"equipper:{kwargs['equipper']}"
            record.char = char_ref
        if kwargs.get("preload_data") is not None:
            record.preload_data = preload_data_ref
        if kwargs.get("sub_exist_buff_dict") is not None:
            record.sub_exist_buff_dict = SUB_EXIST_BUFF_DICT

    buff_0_ref = buff_0
    char_ref = char
    preload_data_ref = preload_data
    monkeypatch.setattr(module, "check_preparation", fake_check_preparation)
    return preparation_calls


def _skill_node(
    *,
    char_name: str = "Yuzuha",
    preload_tick: int = TICK_NOW,
    trigger_buff_level: int = 0,
) -> SimpleNamespace:
    return SimpleNamespace(
        char_name=char_name,
        preload_tick=preload_tick,
        skill_tag="E_EX",
        skill=SimpleNamespace(trigger_buff_level=trigger_buff_level),
    )


def _assert_selected_file_uses_helper_path(row: dict[str, str]) -> None:
    source = (PROJECT_ROOT / row["file"]).read_text(encoding="utf-8")

    assert "prepare_with_context(" in source
    assert "ensure_equipper_template_record(" in source
    assert "build_preparation_context_from_buff" in source
    assert f'item_name="{row["item"]}"' in source
    assert "JudgeTools.find_equipper" not in source
    assert "JudgeTools.find_exist_buff_dict" not in source


def test_us001_checkpoint_and_current_migration_scope_match_qingming_pair() -> None:
    checkpoint = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))

    assert checkpoint["schema"] == (
        "zsim-existing-buff-qingming-birdcage-companion-pair-oracle.v1"
    )
    assert checkpoint["safe_mechanical"] == []
    assert checkpoint["us002_target"] == (
        "existing-buff-qingming-birdcage-companion-pair-migration"
    )
    assert tuple(entry["file"] for entry in checkpoint["needs_focused_oracle"]) == (
        SELECTED_FILES
    )
    for row in SELECTED_ROWS:
        _assert_selected_file_uses_helper_path(row)
    assert tuple(entry["file"] for entry in checkpoint["excluded_or_deferred"][:2]) == (
        EXCLUDED_OR_DEFERRED_FILES
    )
    assert checkpoint["scan_summary"]["selected_needs_focused_oracle_count"] == 2
    assert checkpoint["scan_summary"]["excluded_or_deferred_count"] >= 2
    assert checkpoint["none_safe_to_implement_stop_evidence"] == []


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_qingming_check_record_module_pins_lookup_index_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, str],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, row["logic"])
    record_cls = getattr(module, row["record"])
    harness = _RecordingBuffInstance(index="qingming-template-index")
    logic = logic_cls(harness)
    template = _buff_0()
    equipper_calls, existing_buff_calls = _install_equipper_lookup(
        monkeypatch,
        module=module,
        item=row["item"],
        index=harness.ft.index,
        buff_0=template,
    )

    logic.check_record_module()

    assert equipper_calls == [(row["item"], harness.sim_instance)]
    assert existing_buff_calls == [harness.sim_instance]
    assert logic.equipper == f"equipper:{row['item']}"
    assert logic.buff_0 is template
    assert isinstance(template.history.record, record_cls)
    assert logic.record is template.history.record

    existing_record = logic.record
    logic.check_record_module()

    assert equipper_calls == [(row["item"], harness.sim_instance)]
    assert existing_buff_calls == [harness.sim_instance]
    assert logic.record is existing_record
    assert template.history.record is existing_record


@pytest.mark.parametrize("row", SELECTED_ROWS)
@pytest.mark.parametrize("registry", [{}, {"EQUIPPER": {}}])
def test_qingming_check_record_module_pins_missing_equipper_or_index_errors(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, str],
    registry: dict[str, dict[str, object]],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, row["logic"])
    harness = _RecordingBuffInstance(index="missing-template-index")
    logic = logic_cls(harness)
    normalized_registry = (
        registry
        if not registry
        else {f"equipper:{row['item']}": registry["EQUIPPER"]}
    )
    _install_equipper_lookup(
        monkeypatch,
        module=module,
        item=row["item"],
        index=harness.ft.index,
        buff_0=_buff_0(),
        registry=normalized_registry,
    )

    with pytest.raises(KeyError):
        logic.check_record_module()


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_qingming_judge_pins_preload_tick_personal_stack_gating_and_update_signals(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, str],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, row["logic"])
    harness = _RecordingBuffInstance()
    logic = logic_cls(harness)
    buff_0 = _buff_0()
    _install_equipper_lookup(
        monkeypatch,
        module=module,
        item=row["item"],
        index=harness.ft.index,
        buff_0=buff_0,
    )
    char = SimpleNamespace(NAME="Yuzuha", CID=101)
    preload_data = SimpleNamespace(personal_node_stack={101: [_skill_node()]})
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=buff_0,
        char=char,
        preload_data=preload_data,
    )

    assert logic.special_judge_logic() is False
    assert logic.special_judge_logic(skill_node=_skill_node(preload_tick=TICK_NOW - 1)) is False
    assert logic.special_judge_logic(skill_node=_skill_node(char_name="Nicole")) is False
    assert logic.record.update_signal is None

    assert logic.special_judge_logic(skill_node=_skill_node()) is True
    assert logic.record.update_signal == 0
    with pytest.raises(ValueError, match="尚未处理的更新信号"):
        logic.special_judge_logic(skill_node=_skill_node())

    logic.record.update_signal = None
    preload_data.personal_node_stack[101] = [_skill_node(), _skill_node()]
    assert logic.special_judge_logic(
        skill_node=_skill_node(trigger_buff_level=1)
    ) is False
    assert logic.record.update_signal is None
    assert logic.special_judge_logic(
        skill_node=_skill_node(trigger_buff_level=2)
    ) is True
    assert logic.record.update_signal == 1

    assert preparation_calls == [
        {"equipper": ITEM_NAME, "preload_data": 1},
        {"equipper": ITEM_NAME, "preload_data": 1},
        {"equipper": ITEM_NAME, "preload_data": 1},
        {"equipper": ITEM_NAME, "preload_data": 1},
        {"equipper": ITEM_NAME, "preload_data": 1},
        {"equipper": ITEM_NAME, "preload_data": 1},
        {"equipper": ITEM_NAME, "preload_data": 1},
    ]


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_qingming_start_pins_update_signal_reset_simple_start_and_manual_update(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, str],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, row["logic"])
    harness = _RecordingBuffInstance()
    logic = logic_cls(harness)
    buff_0 = _buff_0()
    _install_equipper_lookup(
        monkeypatch,
        module=module,
        item=row["item"],
        index=harness.ft.index,
        buff_0=buff_0,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=buff_0,
        char=SimpleNamespace(NAME="Yuzuha", CID=101),
        preload_data=SimpleNamespace(personal_node_stack={101: []}),
    )

    with pytest.raises(ValueError, match="并未检测到有效的更新信号"):
        logic.special_start_logic()

    logic.record.update_signal = 0
    logic.special_start_logic()

    assert harness.simple_start_calls == [
        ((), {"timenow": TICK_NOW, "sub_exist_buff_dict": SUB_EXIST_BUFF_DICT, "no_count": 1})
    ]
    assert harness.dy.count == 2
    assert harness.update_to_buff_0_calls == [((buff_0,), {})]
    assert logic.record.update_signal is None

    logic.record.update_signal = 1
    logic.special_start_logic()

    assert harness.simple_start_calls[-1] == (
        (),
        {"timenow": TICK_NOW, "sub_exist_buff_dict": SUB_EXIST_BUFF_DICT},
    )
    assert harness.update_to_buff_0_calls == [((buff_0,), {})]
    assert logic.record.update_signal is None

    logic.record.update_signal = 99
    with pytest.raises(ValueError, match="无法解析的更新信号"):
        logic.special_start_logic()

    assert preparation_calls == [
        {"equipper": ITEM_NAME, "sub_exist_buff_dict": 1},
        {"equipper": ITEM_NAME, "sub_exist_buff_dict": 1},
        {"equipper": ITEM_NAME, "sub_exist_buff_dict": 1},
        {"equipper": ITEM_NAME, "sub_exist_buff_dict": 1},
    ]
