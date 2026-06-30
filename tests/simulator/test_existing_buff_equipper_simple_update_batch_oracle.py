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
    / "2026-06-30-US-001-existing-buff-equipper-simple-update-batch-oracle.json"
)

SUB_EXIST_BUFF_DICT = {"sub": "registry"}
TICK_NOW = 912

SELECTED_ROWS = (
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/KaboomTheCannon.py",
        "module": "KaboomTheCannon",
        "logic": "KaboomTheCannon",
        "record": "KaboomTheCannonRecord",
        "item": "好斗的阿炮",
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/SteamOven.py",
        "module": "SteamOven",
        "logic": "SteamOven",
        "record": "SteamOvenRecord",
        "item": "人为刀俎",
    },
)

SELECTED_FILES = tuple(row["file"] for row in SELECTED_ROWS)
EXCLUDED_OR_DEFERRED_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/FlamemakerShakerDmgBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/QingmingBirdcageCompanionEthDmgBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/QingmingBirdcageCompanionSheerAtkBonus.py",
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
        index: str = "equipper-template-index",
        tick: int = TICK_NOW,
        maxduration: int = 360,
        maxcount: int = 9,
    ) -> None:
        self.sim_instance = SimpleNamespace(tick=tick)
        self.ft = SimpleNamespace(
            index=index,
            maxduration=maxduration,
            maxcount=maxcount,
        )
        self.dy = SimpleNamespace(
            count=0,
            active=False,
            built_in_buff_box=[],
        )
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

    def fake_find_equipper(item_name: str, *, sim_instance: object) -> str:
        equipper_calls.append((item_name, sim_instance))
        return equipper

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        existing_buff_calls.append(sim_instance)
        return lookup_registry

    monkeypatch.setattr(module.JudgeTools, "find_equipper", fake_find_equipper)
    monkeypatch.setattr(
        module.JudgeTools,
        "find_exist_buff_dict",
        fake_find_exist_buff_dict,
    )
    return equipper_calls, existing_buff_calls


def _install_tick(monkeypatch: pytest.MonkeyPatch, module: Any) -> None:
    monkeypatch.setattr(
        module.JudgeTools,
        "find_tick",
        lambda *, sim_instance: sim_instance.tick,
        raising=False,
    )


class _ActionStack:
    def __init__(self, current: object) -> None:
        self._current = current

    def peek(self) -> object:
        return self._current


def _install_preparation(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    harness: _RecordingBuffInstance,
    buff_0: SimpleNamespace,
    char: object,
    action_stack: object,
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
        if kwargs.get("char") is not None or kwargs.get("action_stack") is not None:
            record.char = char_ref
        if kwargs.get("sub_exist_buff_dict") is not None:
            record.sub_exist_buff_dict = SUB_EXIST_BUFF_DICT
        if kwargs.get("action_stack") is not None:
            record.action_stack = action_stack_ref

    buff_0_ref = buff_0
    char_ref = char
    action_stack_ref = action_stack
    monkeypatch.setattr(module, "check_preparation", fake_check_preparation)
    return preparation_calls


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


def _equipper_simple_update_scan() -> dict[str, list[dict[str, str]]]:
    selected: list[dict[str, str]] = []
    excluded: list[dict[str, str]] = []
    for path in sorted(BUFFXLOGIC_ROOT.glob("*.py")):
        source = path.read_text(encoding="utf-8") or ""
        if not all(
            token in source
            for token in (
                "JudgeTools.find_equipper",
                "JudgeTools.find_exist_buff_dict",
                "simple_start",
                "update_to_buff_0",
            )
        ):
            continue
        rel_path = path.relative_to(PROJECT_ROOT).as_posix()
        row = {"file": rel_path, "item": _find_equipper_literal(source)}
        if rel_path in SELECTED_FILES:
            selected.append(row)
        else:
            excluded.append(row)
    return {"needs_focused_oracle": selected, "excluded_or_deferred": excluded}


def test_us001_checkpoint_matches_current_bounded_equipper_simple_update_census() -> None:
    checkpoint = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
    scan = _equipper_simple_update_scan()

    assert checkpoint["schema"] == (
        "zsim-existing-buff-equipper-simple-update-batch-oracle.v1"
    )
    assert checkpoint["safe_mechanical"] == []
    assert checkpoint["us002_target"] == (
        "existing-buff-equipper-simple-update-batch-migration"
    )
    assert tuple(entry["file"] for entry in checkpoint["needs_focused_oracle"]) == (
        SELECTED_FILES
    )
    assert tuple(entry["file"] for entry in scan["needs_focused_oracle"]) == SELECTED_FILES
    assert tuple(entry["file"] for entry in scan["excluded_or_deferred"]) == (
        EXCLUDED_OR_DEFERRED_FILES
    )
    assert checkpoint["scan_summary"]["selected_needs_focused_oracle_count"] == 2
    assert checkpoint["scan_summary"]["excluded_or_deferred_count"] == 4
    assert checkpoint["none_safe_to_implement_stop_evidence"] == []


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_equipper_simple_update_check_record_module_pins_lookup_index_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, str],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, row["logic"])
    record_cls = getattr(module, row["record"])
    harness = _RecordingBuffInstance(index="equipper-template-index")
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
def test_equipper_simple_update_check_record_module_pins_missing_equipper_or_index_errors(
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


def test_kaboom_oracle_pins_preparation_simple_start_update_and_active_character(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from zsim.sim_progress.Buff.BuffXLogic import KaboomTheCannon as module

    buff_0 = _buff_0()
    harness = _RecordingBuffInstance(maxduration=300)
    logic = module.KaboomTheCannon(harness)
    _install_equipper_lookup(
        monkeypatch,
        module=module,
        item="好斗的阿炮",
        index=harness.ft.index,
        buff_0=buff_0,
    )
    _install_tick(monkeypatch, module)
    action_stack = _ActionStack(SimpleNamespace(mission_character="Nicole"))
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=buff_0,
        char=SimpleNamespace(sp=0),
        action_stack=action_stack,
    )

    logic.special_hit_logic()

    assert preparation_calls == [
        {"equipper": "好斗的阿炮", "action_stack": 1, "sub_exist_buff_dict": 1}
    ]
    assert harness.simple_start_calls == [
        ((TICK_NOW, SUB_EXIST_BUFF_DICT), {"not_count": True})
    ]
    assert harness.dy.built_in_buff_box == [[TICK_NOW, TICK_NOW + harness.ft.maxduration]]
    assert buff_0.history.record.active_char_dict == {
        "Nicole": [TICK_NOW, TICK_NOW + harness.ft.maxduration]
    }
    assert harness.update_to_buff_0_calls == [((buff_0,), {})]


def test_steam_oven_oracle_pins_preparation_energy_count_simple_start_and_update(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from zsim.sim_progress.Buff.BuffXLogic import SteamOven as module

    buff_0 = _buff_0()
    harness = _RecordingBuffInstance(maxcount=9)
    logic = module.SteamOven(harness)
    _install_equipper_lookup(
        monkeypatch,
        module=module,
        item="人为刀俎",
        index=harness.ft.index,
        buff_0=buff_0,
    )
    _install_tick(monkeypatch, module)
    current_action = SimpleNamespace(
        mission_tag="E_EX",
        mission_node=SimpleNamespace(skill=SimpleNamespace(ticks=48, sp_consume=25)),
    )
    action_stack = _ActionStack(current_action)
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=buff_0,
        char=SimpleNamespace(sp=67),
        action_stack=action_stack,
    )

    logic.special_effect_logic()

    assert preparation_calls == [
        {"equipper": "人为刀俎", "sub_exist_buff_dict": 1, "action_stack": 1}
    ]
    assert harness.simple_start_calls == [((TICK_NOW, SUB_EXIST_BUFF_DICT), {})]
    assert harness.dy.count == 9
    assert buff_0.history.record.last_update_count == 9
    assert buff_0.history.record.last_update_tick == TICK_NOW
    assert buff_0.history.record.E_EX_started is True
    assert buff_0.history.record.E_EX_endtick == TICK_NOW + 48
    assert harness.update_to_buff_0_calls == [((buff_0,), {})]
