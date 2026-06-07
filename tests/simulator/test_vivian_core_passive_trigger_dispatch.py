from __future__ import annotations

import sys
from types import SimpleNamespace
from typing import Any

import pytest
import zsim.define as define_module

sys.modules.setdefault("define", define_module)

import zsim.sim_progress.Buff.BuffXLogic.VivianCorePassiveTrigger as trigger_module

from zsim.sim_progress.Buff import JudgeTools
from zsim.sim_progress.Buff.BuffXLogic.VivianCorePassiveTrigger import (
    VivianCorePassiveTrigger,
    VivianCorePassiveTriggerRecord,
)
from zsim.sim_progress.anomaly_bar import AnomalyBar
from zsim.sim_progress.anomaly_bar.CopyAnomalyForOutput import DirgeOfDestinyAnomaly


class _FailFastEventList(list):
    def append(self, item):
        raise AssertionError("VivianCorePassiveTrigger should publish via dispatch port")


class _RecordingDispatchPort:
    def __init__(self) -> None:
        self.events: list[object] = []

    def publish_scheduled(self, event: object) -> None:
        self.events.append(event)


class _FakeMultiplierData:
    instances: list["_FakeMultiplierData"] = []

    def __init__(self, enemy: object, dynamic_buff_list: object, char: object) -> None:
        self.enemy = enemy
        self.dynamic_buff_list = dynamic_buff_list
        self.char = char
        self.instances.append(self)


def _block_legacy_event_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_find_event_list(*args, **kwargs):
        raise AssertionError("VivianCorePassiveTrigger should not read raw event_list")

    monkeypatch.setattr(
        JudgeTools, "find_event_list", fail_find_event_list, raising=False
    )


def _build_active_anomaly(*, sim_instance: object) -> AnomalyBar:
    anomaly_bar = AnomalyBar.__new__(AnomalyBar)
    anomaly_bar.sim_instance = sim_instance
    anomaly_bar.element_type = 3
    anomaly_bar.settled = False
    anomaly_bar.settled_calls = 0
    anomaly_bar.marker = "active-anomaly"
    anomaly_bar.activated_by = None
    return anomaly_bar


def test_vivian_core_passive_publishes_dirge_anomaly_via_dispatch_port(
    monkeypatch: pytest.MonkeyPatch,
):
    dispatch_port = _RecordingDispatchPort()
    schedule_data = SimpleNamespace(
        event_list=_FailFastEventList(),
        change_process_state=lambda: None,
    )
    char = SimpleNamespace(NAME="\u8587\u8587\u5b89", cinema=2)
    sim_instance = SimpleNamespace(
        schedule_data=schedule_data,
        char_data=SimpleNamespace(
            find_char_obj=lambda CID: char if CID == 1331 else None,
        ),
    )
    active_anomaly = _build_active_anomaly(sim_instance=sim_instance)
    dynamic = SimpleNamespace(
        dynamic_debuff_list=[],
        dynamic_dot_list=[],
        get_active_anomaly=lambda: [active_anomaly],
    )
    enemy = SimpleNamespace(sim_instance=sim_instance, dynamic=dynamic)
    dynamic_buff_list: dict[str, list[Any]] = {"enemy": []}
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index="vivian-core-passive"),
    )
    logic = VivianCorePassiveTrigger(buff_instance)
    record = VivianCorePassiveTriggerRecord()
    record.char = char
    record.enemy = enemy
    record.dynamic_buff_list = dynamic_buff_list
    monkeypatch.setattr(logic, "check_record_module", lambda: setattr(logic, "record", record))
    monkeypatch.setattr(logic, "get_prepared", lambda **kwargs: None)
    monkeypatch.setattr(
        trigger_module,
        "create_schedule_dispatch_port",
        lambda *, sim_instance: dispatch_port,
    )
    _block_legacy_event_lookup(monkeypatch)

    def fake_anomaly_settled(self: AnomalyBar) -> None:
        self.settled = True
        self.settled_calls = getattr(self, "settled_calls", 0) + 1

    monkeypatch.setattr(AnomalyBar, "anomaly_settled", fake_anomaly_settled)
    _FakeMultiplierData.instances.clear()
    monkeypatch.setattr(trigger_module, "Mul", _FakeMultiplierData)
    cal_ap_inputs: list[object] = []

    def fake_cal_ap(mul_data: object) -> float:
        cal_ap_inputs.append(mul_data)
        return 250.0

    monkeypatch.setattr(trigger_module.Cal.AnomalyMul, "cal_ap", fake_cal_ap)

    logic.special_effect_logic()

    assert len(dispatch_port.events) == 1
    published_event = dispatch_port.events[0]
    assert isinstance(published_event, DirgeOfDestinyAnomaly)
    assert published_event is not active_anomaly
    assert published_event.marker == "active-anomaly"
    assert published_event.element_type == 3
    assert published_event.settled is True
    assert published_event.settled_calls == 1
    assert published_event.sim_instance is sim_instance
    assert published_event.activated_by.char_name == "\u8587\u8587\u5b89"
    assert published_event.activated_by.skill_tag == "1331"
    assert published_event.anomaly_dmg_ratio == pytest.approx(1.04)
    assert record.cinema_ratio == 1.3
    assert active_anomaly.settled is False
    assert active_anomaly.settled_calls == 0
    assert schedule_data.event_list == []
    assert len(_FakeMultiplierData.instances) == 1
    assert _FakeMultiplierData.instances[0].enemy is enemy
    assert _FakeMultiplierData.instances[0].dynamic_buff_list is dynamic_buff_list
    assert _FakeMultiplierData.instances[0].char is char
    assert cal_ap_inputs == [_FakeMultiplierData.instances[0]]
