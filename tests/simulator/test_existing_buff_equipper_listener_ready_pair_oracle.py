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
    / "2026-06-30-US-001-existing-buff-equipper-listener-ready-pair-oracle.json"
)

TICK_NOW = 1440

SELECTED_ROWS = (
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/CinderCobaltAtkBonus.py",
        "module": "CinderCobaltAtkBonus",
        "logic": "CinderCobaltAtkBonus",
        "record": "CinderCobaltAtkBonusRecord",
        "item": "「灰烬」-钴蓝",
        "listener_id": "cinder-listener-id",
        "listener_id_source": "buff_ft",
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/HormonePunkAtkBonus.py",
        "module": "HormonePunkAtkBonus",
        "logic": "HormonePunkAtkBonus",
        "record": "HormonePunkAtkBonusRecord",
        "item": "激素朋克",
        "listener_id": "Hormone_Punk_1",
        "listener_id_source": "literal",
    },
)

SELECTED_FILES = tuple(row["file"] for row in SELECTED_ROWS)
EXCLUDED_OR_DEFERRED_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/ZanshinHerbCase.py",
    "zsim/sim_progress/Buff/BuffXLogic/FlamemakerShakerDmgBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/SharpenedStingerPhyDmgBonus.py",
)


def _module(row: dict[str, str]) -> Any:
    return importlib.import_module(
        f"zsim.sim_progress.Buff.BuffXLogic.{row['module']}"
    )


class _TemplateBuff:
    def __init__(self, *, record: object | None = None, ready: bool = True) -> None:
        self.history = SimpleNamespace(record=record)
        self.ready = ready
        self.is_ready_calls: list[int] = []

    def is_ready(self, tick: int) -> bool:
        self.is_ready_calls.append(tick)
        return self.ready


class _RecordingListenerManager:
    def __init__(self, registry: tuple[tuple[object, str, object], ...]) -> None:
        self.registry = {
            (id(listener_owner), listener_id): listener
            for listener_owner, listener_id, listener in registry
        }
        self.calls: list[tuple[object, str]] = []

    def get_listener(self, *, listener_owner: object, listener_id: str) -> object:
        self.calls.append((listener_owner, listener_id))
        return self.registry[(id(listener_owner), listener_id)]


class _RecordingBuffInstance:
    def __init__(
        self,
        *,
        index: str = "listener-ready-template-index",
        listener_id: str = "cinder-listener-id",
        tick: int = TICK_NOW,
        listener_manager: object | None = None,
    ) -> None:
        self.sim_instance = SimpleNamespace(tick=tick, listener_manager=listener_manager)
        self.ft = SimpleNamespace(index=index, listener_id=listener_id)


def _install_direct_lookup(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    item: str,
    index: str,
    buff_0: _TemplateBuff,
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
    buff_0: _TemplateBuff,
    char: object,
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

    buff_0_ref = buff_0
    char_ref = char
    monkeypatch.setattr(module, "check_preparation", fake_check_preparation)
    return preparation_calls


def _install_tick(monkeypatch: pytest.MonkeyPatch, module: Any) -> list[object]:
    tick_calls: list[object] = []

    def fake_find_tick(*, sim_instance: object) -> int:
        tick_calls.append(sim_instance)
        return sim_instance.tick

    monkeypatch.setattr(module, "find_tick", fake_find_tick)
    return tick_calls


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


def _raw_equipper_listener_ready_scan() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted(BUFFXLOGIC_ROOT.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        if not all(
            token in source
            for token in (
                "JudgeTools.find_equipper",
                "JudgeTools.find_exist_buff_dict",
                "listener_manager.get_listener",
                "active_signal",
                "is_ready(find_tick",
            )
        ):
            continue
        rel_path = path.relative_to(PROJECT_ROOT).as_posix()
        rows.append({"file": rel_path, "item": _find_equipper_literal(source)})
    return rows


def test_us001_checkpoint_and_current_census_match_listener_ready_pair() -> None:
    checkpoint = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
    bounded_rows = _raw_equipper_listener_ready_scan()

    assert checkpoint["schema"] == (
        "zsim-existing-buff-equipper-listener-ready-pair-oracle.v1"
    )
    assert checkpoint["safe_mechanical"] == []
    assert checkpoint["us002_target"] == (
        "existing-buff-equipper-listener-ready-pair-migration"
    )
    assert tuple(entry["file"] for entry in checkpoint["needs_focused_oracle"]) == (
        SELECTED_FILES
    )
    assert tuple(row["file"] for row in bounded_rows) == SELECTED_FILES
    assert tuple(entry["file"] for entry in checkpoint["excluded_or_deferred"][:3]) == (
        EXCLUDED_OR_DEFERRED_FILES
    )
    assert checkpoint["scan_summary"]["selected_needs_focused_oracle_count"] == 2
    assert checkpoint["scan_summary"]["excluded_or_deferred_count"] >= 3
    assert checkpoint["none_safe_to_implement_stop_evidence"] == []
    assert checkpoint["us002_target_allowed_values"] == [
        "existing-buff-equipper-listener-ready-pair-migration",
        "none-safe-to-implement",
    ]


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_listener_ready_check_record_module_pins_lookup_index_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, str],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, row["logic"])
    record_cls = getattr(module, row["record"])
    harness = _RecordingBuffInstance(index="listener-ready-template-index")
    logic = logic_cls(harness)
    template = _TemplateBuff()
    equipper_calls, existing_buff_calls = _install_direct_lookup(
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
def test_listener_ready_check_record_module_pins_missing_equipper_or_index_errors(
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
    _install_direct_lookup(
        monkeypatch,
        module=module,
        item=row["item"],
        index=harness.ft.index,
        buff_0=_TemplateBuff(),
        registry=normalized_registry,
    )

    with pytest.raises(KeyError):
        logic.check_record_module()


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_listener_ready_judge_pins_preparation_listener_identity_and_ready_gating(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, str],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, row["logic"])
    char = SimpleNamespace(NAME="Anby")
    other_char = SimpleNamespace(NAME="Nicole")
    listener = SimpleNamespace(active_signal=None)
    listener_manager = _RecordingListenerManager(((char, row["listener_id"], listener),))
    harness = _RecordingBuffInstance(
        listener_id="cinder-listener-id",
        listener_manager=listener_manager,
    )
    logic = logic_cls(harness)
    template = _TemplateBuff(ready=False)
    _install_direct_lookup(
        monkeypatch,
        module=module,
        item=row["item"],
        index=harness.ft.index,
        buff_0=template,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char=char,
    )
    tick_calls = _install_tick(monkeypatch, module)

    assert logic.special_judge_logic() is False
    assert listener.active_signal is None
    assert listener_manager.calls == [(char, row["listener_id"])]

    listener.active_signal = (other_char,)
    assert logic.special_judge_logic() is False
    assert listener.active_signal == (other_char,)

    listener.active_signal = (char,)
    assert logic.special_judge_logic() is False
    assert listener.active_signal is None
    assert template.is_ready_calls == [TICK_NOW]
    assert tick_calls == [harness.sim_instance]

    template.ready = True
    listener.active_signal = (char,)
    assert logic.special_judge_logic() is True
    assert listener.active_signal is None
    assert template.is_ready_calls == [TICK_NOW, TICK_NOW]
    assert tick_calls == [harness.sim_instance, harness.sim_instance]
    assert listener_manager.calls == [(char, row["listener_id"])]
    assert preparation_calls == [
        {"equipper": row["item"]},
        {"equipper": row["item"]},
        {"equipper": row["item"]},
        {"equipper": row["item"]},
    ]


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_listener_ready_judge_pins_missing_listener_error(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, str],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, row["logic"])
    char = SimpleNamespace(NAME="Anby")
    listener_manager = _RecordingListenerManager(())
    harness = _RecordingBuffInstance(listener_manager=listener_manager)
    logic = logic_cls(harness)
    template = _TemplateBuff()
    _install_direct_lookup(
        monkeypatch,
        module=module,
        item=row["item"],
        index=harness.ft.index,
        buff_0=template,
    )
    _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char=char,
    )

    with pytest.raises(KeyError):
        logic.special_judge_logic()

    assert listener_manager.calls == [(char, row["listener_id"])]
