from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest
import zsim.define as define_module

sys.modules.setdefault("define", define_module)

import zsim.sim_progress.Buff.BuffXLogic.ElegantVanitySpRecover as elegant_module
import zsim.sim_progress.Buff.BuffXLogic.LunarNoviluna as lunar_module
from zsim.sim_progress.Buff import JudgeTools
from zsim.sim_progress.Buff.BuffXLogic.ElegantVanitySpRecover import ElegantVanitySpRecover
from zsim.sim_progress.Buff.BuffXLogic.LunarNoviluna import LunarNoviluna
from zsim.sim_progress.data_struct.sp_update_data import ScheduleRefreshData


class _FailFastEventList(list):
    def append(self, item):
        raise AssertionError("xstart SP refresh producer should publish via dispatch port")


class _RecordingDispatchPort:
    def __init__(self) -> None:
        self.events: list[object] = []

    def publish_scheduled(self, event: object) -> None:
        self.events.append(event)


def _block_legacy_event_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_find_event_list(*args, **kwargs):
        raise AssertionError("xstart SP refresh producer should not read raw event_list")

    monkeypatch.setattr(JudgeTools, "find_event_list", fail_find_event_list)


def test_elegant_vanity_sp_recover_publishes_after_simple_start_via_dispatch_port(
    monkeypatch: pytest.MonkeyPatch,
):
    dispatch_port = _RecordingDispatchPort()
    sim_instance = SimpleNamespace(tick=27, schedule_data=SimpleNamespace(event_list=_FailFastEventList()))
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(refinement="3"),
    )
    logic = ElegantVanitySpRecover(buff_instance)
    call_order: list[tuple[str, int]] = []
    sub_exist_buff_dict = {"EV": object()}
    record = SimpleNamespace(
        sub_exist_buff_dict=sub_exist_buff_dict,
        energy_value_dict={1: 5, 2: 5.5, 3: 6, 4: 6.5, 5: 7},
        char=SimpleNamespace(NAME="可琳"),
    )
    logic.check_record_module = lambda: setattr(logic, "record", record)
    logic.get_prepared = lambda **kwargs: None
    monkeypatch.setattr(
        elegant_module,
        "create_schedule_dispatch_port",
        lambda *, sim_instance: dispatch_port,
    )
    _block_legacy_event_lookup(monkeypatch)

    def fake_simple_start(tick_now, target_sub_exist_buff_dict):
        call_order.append(("simple_start", tick_now))
        assert target_sub_exist_buff_dict is sub_exist_buff_dict

    buff_instance.simple_start = fake_simple_start

    logic.special_start_logic()

    assert call_order == [("simple_start", 27)]
    assert len(dispatch_port.events) == 1
    refresh_data = dispatch_port.events[0]
    assert isinstance(refresh_data, ScheduleRefreshData)
    assert refresh_data.sp_target == ("可琳",)
    assert refresh_data.sp_value == 6
    assert sim_instance.schedule_data.event_list == []


def test_lunar_noviluna_preserves_publish_then_simple_start_order_via_dispatch_port(
    monkeypatch: pytest.MonkeyPatch,
):
    dispatch_port = _RecordingDispatchPort()
    sim_instance = SimpleNamespace(tick=31, schedule_data=SimpleNamespace(event_list=_FailFastEventList()))
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(refinement=4),
    )
    logic = LunarNoviluna(buff_instance)
    call_order: list[str] = []
    sub_exist_buff_dict = {"LN": object()}
    record = SimpleNamespace(
        sub_exist_buff_dict=sub_exist_buff_dict,
        enegy_value_map={1: 3, 2: 3.5, 3: 4, 4: 4.5, 5: 5},
        char=SimpleNamespace(NAME="露娜"),
    )
    logic.check_record_module = lambda: setattr(logic, "record", record)
    logic.get_prepared = lambda **kwargs: None
    monkeypatch.setattr(
        lunar_module,
        "create_schedule_dispatch_port",
        lambda *, sim_instance: dispatch_port,
    )
    _block_legacy_event_lookup(monkeypatch)

    def fake_simple_start(tick_now, target_sub_exist_buff_dict):
        call_order.append("simple_start")
        assert tick_now == 31
        assert target_sub_exist_buff_dict is sub_exist_buff_dict

    buff_instance.simple_start = fake_simple_start

    logic.special_start_logic()

    assert len(dispatch_port.events) == 1
    refresh_data = dispatch_port.events[0]
    assert isinstance(refresh_data, ScheduleRefreshData)
    assert refresh_data.sp_target == ("露娜",)
    assert refresh_data.sp_value == 4.5
    assert call_order == ["simple_start"]
    assert sim_instance.schedule_data.event_list == []
