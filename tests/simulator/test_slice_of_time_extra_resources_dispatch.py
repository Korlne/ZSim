from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest
import zsim.define as define_module

sys.modules.setdefault("define", define_module)

import zsim.sim_progress.Buff.BuffXLogic.SliceofTimeExtraResources as slice_module
from zsim.sim_progress.Buff import JudgeTools
from zsim.sim_progress.Buff.BuffXLogic.SliceofTimeExtraResources import (
    SliceofTimeExtraResources,
    SliceofTimeExtraResourcesRecord,
)
from zsim.sim_progress.data_struct.schedule_dispatch import (
    ScheduleDispatchPort,
    ScheduledEventEmitterProvider,
)
from zsim.sim_progress.data_struct.sp_update_data import ScheduleRefreshData


class _FailFastEventList(list):
    def append(self, item):
        raise AssertionError(
            "SliceofTimeExtraResources should publish combined refresh data via dispatch port"
        )


class _RecordingDispatchPort(ScheduleDispatchPort):
    def __init__(self, call_order: list[str]) -> None:
        self.events: list[object] = []
        self._call_order = call_order

    def publish_scheduled(self, event: object) -> None:
        self._call_order.append("publish")
        self.events.append(event)


def _block_legacy_event_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_find_event_list(*args, **kwargs):
        raise AssertionError("SliceofTimeExtraResources should not read raw event_list")

    monkeypatch.setattr(
        JudgeTools, "find_event_list", fail_find_event_list, raising=False
    )


def test_slice_of_time_extra_resources_publishes_mixed_refresh_via_dispatch_port(
    monkeypatch: pytest.MonkeyPatch,
):
    call_order: list[str] = []
    dispatch_port = _RecordingDispatchPort(call_order)
    sim_instance = SimpleNamespace(
        tick=91,
        schedule_data=SimpleNamespace(event_list=_FailFastEventList()),
    )
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(refinement=4),
    )
    logic = SliceofTimeExtraResources(
        buff_instance,
        scheduled_event_emitter_provider=ScheduledEventEmitterProvider(
            lambda: dispatch_port
        ),
    )
    sub_exist_buff_dict = {"slice": object()}
    action_now = SimpleNamespace(
        mission_node=SimpleNamespace(skill=SimpleNamespace(trigger_buff_level=5)),
        mission_character="actor",
    )
    record = SliceofTimeExtraResourcesRecord()
    record.char = SimpleNamespace(NAME="support")
    record.sub_exist_buff_dict = sub_exist_buff_dict
    record.action_stack = SimpleNamespace(peek=lambda: action_now)
    monkeypatch.setattr(logic, "check_record_module", lambda: setattr(logic, "record", record))
    monkeypatch.setattr(logic, "get_prepared", lambda **kwargs: None)
    _block_legacy_event_lookup(monkeypatch)

    def fake_simple_start(tick_now, target_sub_exist_buff_dict):
        call_order.append("simple_start")
        assert tick_now == 91
        assert target_sub_exist_buff_dict is sub_exist_buff_dict

    buff_instance.simple_start = fake_simple_start

    logic.special_start_logic()

    assert call_order == ["simple_start", "publish"]
    assert len(dispatch_port.events) == 1
    refresh_data = dispatch_port.events[0]
    assert isinstance(refresh_data, ScheduleRefreshData)
    assert refresh_data.sp_target == ("support",)
    assert refresh_data.sp_value == 1.0
    assert refresh_data.decibel_target == ("actor",)
    assert refresh_data.decibel_value == 50
    assert sim_instance.schedule_data.event_list == []
