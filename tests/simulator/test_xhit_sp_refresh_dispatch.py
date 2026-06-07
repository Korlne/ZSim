from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest
import zsim.define as define_module

sys.modules.setdefault("define", define_module)

import zsim.sim_progress.Buff.BuffXLogic.MagneticStormCharlieSpRecover as magnetic_module
import zsim.sim_progress.Buff.BuffXLogic.SeedAdditionalAbilityTrigger as seed_module
from zsim.sim_progress.Buff import JudgeTools
from zsim.sim_progress.Buff.BuffXLogic.MagneticStormCharlieSpRecover import (
    MagneticStormCharlieSpRecover,
)
from zsim.sim_progress.Buff.BuffXLogic.SeedAdditionalAbilityTrigger import (
    SeedAdditionalAbilityTrigger,
    SeedAdditionalAbilityTriggerRecord,
)
from zsim.sim_progress.data_struct.sp_update_data import ScheduleRefreshData


class _FailFastEventList(list):
    def append(self, item):
        raise AssertionError("xhit SP refresh producer should publish via dispatch port")


class _RecordingDispatchPort:
    def __init__(self) -> None:
        self.events: list[object] = []

    def publish_scheduled(self, event: object) -> None:
        self.events.append(event)


def _block_legacy_event_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_find_event_list(*args, **kwargs):
        raise AssertionError("xhit SP refresh producer should not read raw event_list")

    monkeypatch.setattr(
        JudgeTools, "find_event_list", fail_find_event_list, raising=False
    )


def test_magnetic_storm_charlie_sp_recover_publishes_after_simple_start_via_dispatch_port(
    monkeypatch: pytest.MonkeyPatch,
):
    dispatch_port = _RecordingDispatchPort()
    sim_instance = SimpleNamespace(
        tick=42,
        schedule_data=SimpleNamespace(event_list=_FailFastEventList()),
    )
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(refinement="5"),
    )
    logic = MagneticStormCharlieSpRecover(buff_instance)
    call_order: list[tuple[str, int]] = []
    sub_exist_buff_dict = {"MSC": object()}
    record = SimpleNamespace(
        sub_exist_buff_dict=sub_exist_buff_dict,
        energy_value_dict={1: 3.5, 2: 4, 3: 4.5, 4: 5, 5: 5.5},
        char=SimpleNamespace(NAME="青衣"),
    )
    monkeypatch.setattr(logic, "check_record_module", lambda: setattr(logic, "record", record))
    monkeypatch.setattr(logic, "get_prepared", lambda **kwargs: None)
    monkeypatch.setattr(
        magnetic_module,
        "create_schedule_dispatch_port",
        lambda *, sim_instance: dispatch_port,
    )
    _block_legacy_event_lookup(monkeypatch)

    def fake_simple_start(tick_now, target_sub_exist_buff_dict):
        call_order.append(("simple_start", tick_now))
        assert target_sub_exist_buff_dict is sub_exist_buff_dict

    buff_instance.simple_start = fake_simple_start

    logic.special_hit_logic()

    assert call_order == [("simple_start", 42)]
    assert len(dispatch_port.events) == 1
    refresh_data = dispatch_port.events[0]
    assert isinstance(refresh_data, ScheduleRefreshData)
    assert refresh_data.sp_target == ("青衣",)
    assert refresh_data.sp_value == 5.5
    assert sim_instance.schedule_data.event_list == []


def test_seed_additional_ability_trigger_publishes_for_vanguard_via_dispatch_port(
    monkeypatch: pytest.MonkeyPatch,
):
    dispatch_port = _RecordingDispatchPort()
    schedule_data = SimpleNamespace(
        event_list=_FailFastEventList(),
        change_process_state=lambda: None,
    )
    sim_instance = SimpleNamespace(
        tick=73,
        schedule_data=schedule_data,
    )
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index="seed-trigger"),
    )
    logic = SeedAdditionalAbilityTrigger(buff_instance)
    record = SeedAdditionalAbilityTriggerRecord()
    record.char = SimpleNamespace(
        NAME="席德",
        vanguard=SimpleNamespace(NAME="柯蕾妲"),
    )
    monkeypatch.setattr(logic, "check_record_module", lambda: setattr(logic, "record", record))
    monkeypatch.setattr(logic, "get_prepared", lambda **kwargs: None)
    monkeypatch.setattr(
        seed_module,
        "create_schedule_dispatch_port",
        lambda *, sim_instance: dispatch_port,
    )

    logic.special_hit_logic()

    assert len(dispatch_port.events) == 1
    refresh_data = dispatch_port.events[0]
    assert isinstance(refresh_data, ScheduleRefreshData)
    assert refresh_data.sp_target == ("柯蕾妲",)
    assert refresh_data.sp_value == 2
    assert record.last_active_tick == 73
    assert sim_instance.schedule_data.event_list == []
