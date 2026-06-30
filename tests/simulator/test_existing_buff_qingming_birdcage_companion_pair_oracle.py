from __future__ import annotations

import ast
import importlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUFFXLOGIC_ROOT = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffXLogic"
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


def _install_direct_equipper_lookup(
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

    def fake_find_equipper(item_name: str, *, sim_instance: object) -> str:
        equipper_calls.append((item_name, sim_instance))
        return equipper

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        existing_buff_calls.append(sim_instance)
        return lookup_registry

    monkeypatch.setattr(module.JudgeTools, "find_equipper", fake_find_equipper)
    monkeypatch.setattr(module.JudgeTools, "find_exist_buff_dict", fake_find_exist_buff_dict)
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
        preparation_calls.append(dict(kwargs))
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


def _find_equipper_literal(source: str) -> str:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "find_equipper" or not node.args:
            continue
        first_arg = node.args[0]
        if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
            return first_arg.value
    raise AssertionError("expected JudgeTools.find_equipper literal")


def _raw_qingming_companion_scan() -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for path in sorted(BUFFXLOGIC_ROOT.glob("*.py")):
        source = path.read_text(encoding="utf-8") or ""
        if not all(
            token in source
            for token in (
                "JudgeTools.find_equipper",
                "JudgeTools.find_exist_buff_dict",
                ITEM_NAME,
                "update_signal",
                "personal_node_stack",
                "simple_start",
                "update_to_buff_0",
            )
        ):
            continue
        rel_path = path.relative_to(PROJECT_ROOT).as_posix()
        hits.append({"file": rel_path, "item": _find_equipper_literal(source)})
    return hits


def test_us001_checkpoint_matches_current_bounded_qingming_companion_census() -> None:
    checkpoint = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
    raw_hits = _raw_qingming_companion_scan()

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
    assert tuple(entry["file"] for entry in raw_hits) == SELECTED_FILES
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
    equipper_calls, existing_buff_calls = _install_direct_equipper_lookup(
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
    _install_direct_equipper_lookup(
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
    _install_direct_equipper_lookup(
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
    _install_direct_equipper_lookup(
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
