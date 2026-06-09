from __future__ import annotations

import sys
from collections.abc import Iterable
from types import SimpleNamespace
from typing import Any, SupportsIndex

import pytest
import zsim.define as define_module
import zsim.sim_progress.ScheduledEvent as scheduled_event_module
import zsim.sim_progress.ScheduledEvent.buff_runtime as buff_runtime_module
import zsim.sim_progress.ScheduledEvent.runtime_command as runtime_command_module
import zsim.sim_progress.data_struct.schedule_dispatch as schedule_dispatch_module

sys.modules.setdefault("define", define_module)

import zsim.sim_progress.Buff.BuffXLogic.RoaringRideBuffTrigger as roaring_module

from zsim.sim_progress.Buff import JudgeTools
from zsim.sim_progress.Buff.BuffXLogic.RoaringRideBuffTrigger import (
    RoaringRideBuffTrigger,
    RoaringRideBuffTriggerRecord,
)


class _FailFastEventList(list[Any]):
    def append(self, item: Any) -> None:
        raise AssertionError("Roaring Ride should not publish scheduled events")

    def extend(self, items: Iterable[Any]) -> None:
        raise AssertionError("Roaring Ride should not publish scheduled events")

    def insert(self, index: SupportsIndex, item: Any) -> None:
        raise AssertionError("Roaring Ride should not publish scheduled events")


class _FailFastLoadingBuffDict(dict[str, list[Any]]):
    def __getitem__(self, key: str) -> list[Any]:
        raise AssertionError("Roaring Ride should not touch LOADING_BUFF_DICT")

    def get(self, key: str, default: Any = None) -> Any:
        raise AssertionError("Roaring Ride should not touch LOADING_BUFF_DICT")

    def __setitem__(self, key: str, value: list[Any]) -> None:
        raise AssertionError("Roaring Ride should not touch LOADING_BUFF_DICT")


class _FixedRng:
    def __init__(self, value: float) -> None:
        self.value = value
        self.calls: list[str] = []

    def random_float(self) -> float:
        self.calls.append("random_float")
        return self.value


def _fail_listener_broadcast(*args: object, **kwargs: object) -> None:
    raise AssertionError("Roaring Ride should not broadcast listener events")


def _patch_runtime_boundary_guards(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_create_runtime_command_port(*args: object, **kwargs: object) -> None:
        raise AssertionError("Roaring Ride should not create RuntimeCommandPort")

    def fail_create_buff_runtime_read_port(*args: object, **kwargs: object) -> None:
        raise AssertionError("Roaring Ride should not create BuffRuntimeReadPort")

    def fail_create_schedule_dispatch_port(*args: object, **kwargs: object) -> None:
        raise AssertionError("Roaring Ride should not create ScheduleDispatchPort")

    monkeypatch.setattr(
        runtime_command_module,
        "create_runtime_command_port",
        fail_create_runtime_command_port,
    )
    monkeypatch.setattr(
        scheduled_event_module,
        "create_runtime_command_port",
        fail_create_runtime_command_port,
        raising=False,
    )
    monkeypatch.setattr(
        buff_runtime_module,
        "create_buff_runtime_read_port",
        fail_create_buff_runtime_read_port,
    )
    monkeypatch.setattr(
        scheduled_event_module,
        "create_buff_runtime_read_port",
        fail_create_buff_runtime_read_port,
        raising=False,
    )
    monkeypatch.setattr(
        schedule_dispatch_module,
        "create_schedule_dispatch_port",
        fail_create_schedule_dispatch_port,
    )


def _build_roaring_ride_harness(rng_value: float) -> SimpleNamespace:
    call_order: list[str] = []
    listener_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
    sub_exist_buff_dict = {"roaring-ride-trigger": object()}
    rng = _FixedRng(rng_value)
    sim_instance = SimpleNamespace(
        tick=106,
        rng_instance=rng,
        schedule_data=SimpleNamespace(event_list=_FailFastEventList()),
        load_data=SimpleNamespace(LOADING_BUFF_DICT=_FailFastLoadingBuffDict()),
        listener_manager=SimpleNamespace(
            broadcast_event=lambda *args, **kwargs: (
                listener_calls.append((args, kwargs)),
                _fail_listener_broadcast(*args, **kwargs),
            )
        ),
    )
    simple_start_calls: list[tuple[int, dict[str, object]]] = []

    def simple_start(timenow: int, sub_exist_buff_dict_arg: dict[str, object]) -> None:
        call_order.append("simple_start")
        simple_start_calls.append((timenow, sub_exist_buff_dict_arg))

    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index="roaring-ride-trigger", refinement=5),
        simple_start=simple_start,
    )
    logic = RoaringRideBuffTrigger(buff_instance)
    record = RoaringRideBuffTriggerRecord()
    record.sub_exist_buff_dict = sub_exist_buff_dict

    return SimpleNamespace(
        call_order=call_order,
        logic=logic,
        record=record,
        rng=rng,
        sim_instance=sim_instance,
        simple_start_calls=simple_start_calls,
        listener_calls=listener_calls,
    )


def _patch_roaring_ride_dependencies(
    monkeypatch: pytest.MonkeyPatch,
    harness: SimpleNamespace,
) -> list[tuple[str, dict[str, object]]]:
    _patch_runtime_boundary_guards(monkeypatch)

    def fail_find_event_list(*args: object, **kwargs: object) -> None:
        raise AssertionError("Roaring Ride should not read raw event_list")

    def fake_check_record_module() -> None:
        harness.logic.record = harness.record

    prepared_calls: list[dict[str, object]] = []

    def fake_get_prepared(**kwargs: object) -> None:
        prepared_calls.append(kwargs)

    buff_add_calls: list[tuple[str, dict[str, object]]] = []

    def fake_buff_add_strategy(buff_index: str, **kwargs: object) -> None:
        harness.call_order.append("buff_add_strategy")
        buff_add_calls.append((buff_index, kwargs))

    monkeypatch.setattr(JudgeTools, "find_event_list", fail_find_event_list, raising=False)
    monkeypatch.setattr(harness.logic, "check_record_module", fake_check_record_module)
    monkeypatch.setattr(harness.logic, "get_prepared", fake_get_prepared)
    monkeypatch.setattr(
        "zsim.sim_progress.Buff.BuffAddStrategy.buff_add_strategy",
        fake_buff_add_strategy,
    )
    monkeypatch.setattr(
        roaring_module,
        "find_tick",
        lambda *, sim_instance: sim_instance.tick,
    )

    harness.prepared_calls = prepared_calls
    return buff_add_calls


@pytest.mark.parametrize(
    ("rng_value", "expected_buff_index"),
    [
        (0.0, "Buff-武器-精5轰鸣座驾-攻击力"),
        (1 / 3, "Buff-武器-精5轰鸣座驾-精通提升"),
        ((2 / 3) - 1e-9, "Buff-武器-精5轰鸣座驾-精通提升"),
        (2 / 3, "Buff-武器-精5轰鸣座驾-属性异常积蓄"),
        (0.999, "Buff-武器-精5轰鸣座驾-属性异常积蓄"),
    ],
)
def test_roaring_ride_rng_branches_use_buff_add_strategy_forced_write_boundary(
    rng_value: float,
    expected_buff_index: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _build_roaring_ride_harness(rng_value)
    buff_add_calls = _patch_roaring_ride_dependencies(monkeypatch, harness)

    harness.logic.special_hit_logic()

    assert harness.rng.calls == ["random_float"]
    assert harness.prepared_calls == [
        {"equipper": "轰鸣座驾", "sub_exist_buff_dict": 1}
    ]
    assert buff_add_calls == [
        (expected_buff_index, {"sim_instance": harness.sim_instance})
    ]
    assert harness.call_order == ["buff_add_strategy", "simple_start"]
    assert harness.simple_start_calls == [
        (harness.sim_instance.tick, harness.record.sub_exist_buff_dict)
    ]
    assert harness.listener_calls == []
    assert harness.sim_instance.schedule_data.event_list == []
    assert harness.record.buff_map == {
        0: "Buff-武器-精5轰鸣座驾-攻击力",
        1: "Buff-武器-精5轰鸣座驾-精通提升",
        2: "Buff-武器-精5轰鸣座驾-属性异常积蓄",
    }
