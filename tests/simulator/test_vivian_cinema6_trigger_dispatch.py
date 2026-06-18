from __future__ import annotations

import sys
from types import SimpleNamespace
from typing import Any

import pytest
import zsim.define as define_module

sys.modules.setdefault("define", define_module)

import zsim.sim_progress.Buff.BuffXLogic.VivianCinema6Trigger as trigger_module

from zsim.sim_progress.Buff import JudgeTools
from zsim.sim_progress.Buff.BuffXLogic.VivianCinema6Trigger import (
    VivianCinema6Trigger,
    VivianCinema6TriggerRecord,
)
from zsim.sim_progress.Preload import SkillNode
from zsim.sim_progress.anomaly_bar import AnomalyBar
from zsim.sim_progress.anomaly_bar.CopyAnomalyForOutput import DirgeOfDestinyAnomaly


class _FailFastEventList(list):
    def append(self, item):
        raise AssertionError("VivianCinema6Trigger should publish via dispatch port")


class _RecordingDispatchPort:
    def __init__(
        self, action_log: list[tuple[str, object]] | None = None
    ) -> None:
        self.events: list[object] = []
        self.action_log = action_log

    def publish_scheduled(self, event: object) -> None:
        if self.action_log is not None:
            self.action_log.append(("publish_scheduled", event))
        self.events.append(event)


class _FeatherManagerProbe:
    def __init__(
        self,
        *,
        guard_feather: int,
        c1_counter: int,
        flight_feather: int,
        action_log: list[tuple[str, object]],
    ) -> None:
        self._guard_feather = guard_feather
        self._c1_counter = c1_counter
        self._flight_feather = flight_feather
        self.action_log = action_log
        self.mutation_log: list[tuple[str, object]] = []
        self.update_calls: list[bool] = []

    def _record(self, field: str, value: object) -> None:
        entry = (field, value)
        self.mutation_log.append(entry)
        self.action_log.append(entry)

    @property
    def guard_feather(self) -> int:
        return self._guard_feather

    @guard_feather.setter
    def guard_feather(self, value: int) -> None:
        self._record("guard_feather", value)
        self._guard_feather = value

    @property
    def c1_counter(self) -> int:
        return self._c1_counter

    @c1_counter.setter
    def c1_counter(self, value: int) -> None:
        self._record("c1_counter", value)
        self._c1_counter = value

    @property
    def flight_feather(self) -> int:
        return self._flight_feather

    @flight_feather.setter
    def flight_feather(self, value: int) -> None:
        self._record("flight_feather", value)
        self._flight_feather = value

    def update_myself(self, *, c6_signal: bool) -> None:
        self.update_calls.append(c6_signal)
        self.action_log.append(("update_myself", c6_signal))


class _FakeMultiplierData:
    instances: list["_FakeMultiplierData"] = []

    def __init__(self, enemy: object, dynamic_buff_list: object, char: object) -> None:
        self.enemy = enemy
        self.dynamic_buff_list = dynamic_buff_list
        self.char = char
        self.instances.append(self)


class _DynamicReadProbe:
    def __init__(self, active_anomalies: list[AnomalyBar]) -> None:
        self.active_anomalies = active_anomalies
        self.calls: list[str] = []

    @property
    def is_under_anomaly(self) -> bool:
        self.calls.append("is_under_anomaly")
        return bool(self.active_anomalies)

    def get_active_anomaly(self) -> list[AnomalyBar]:
        self.calls.append("get_active_anomaly")
        return self.active_anomalies


def _block_legacy_event_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_find_event_list(*args, **kwargs):
        raise AssertionError("VivianCinema6Trigger should not read raw event_list")

    monkeypatch.setattr(
        JudgeTools, "find_event_list", fail_find_event_list, raising=False
    )


def _build_active_anomaly(*, sim_instance: object) -> AnomalyBar:
    anomaly_bar = AnomalyBar.__new__(AnomalyBar)
    anomaly_bar.sim_instance = sim_instance
    anomaly_bar.element_type = 4
    anomaly_bar.settled = False
    anomaly_bar.settled_calls = 0
    anomaly_bar.marker = "c6-active-anomaly"
    anomaly_bar.activated_by = None
    return anomaly_bar


def _build_skill_node(*, uuid: str = "vivian-cinema6-node") -> SkillNode:
    skill_node = SkillNode.__new__(SkillNode)
    skill_node.skill_tag = "1331_SNA_2"
    skill_node.UUID = uuid
    return skill_node


def _build_logic_harness(*, active_anomalies: list[AnomalyBar]) -> tuple[
    VivianCinema6Trigger,
    VivianCinema6TriggerRecord,
    _RecordingDispatchPort,
    SimpleNamespace,
]:
    action_log: list[tuple[str, object]] = []
    dispatch_port = _RecordingDispatchPort(action_log=action_log)
    schedule_data = SimpleNamespace(
        event_list=_FailFastEventList(),
        change_process_state=lambda: None,
    )
    feather_manager = _FeatherManagerProbe(
        guard_feather=3,
        c1_counter=1,
        flight_feather=2,
        action_log=action_log,
    )
    char = SimpleNamespace(
        NAME="\u8587\u8587\u5b89",
        cinema=6,
        feather_manager=feather_manager,
        get_special_stats=lambda: {},
    )
    sim_instance = SimpleNamespace(
        schedule_data=schedule_data,
        char_data=SimpleNamespace(
            find_char_obj=lambda CID: char if CID == 1331 else None,
        ),
    )
    dynamic = _DynamicReadProbe(active_anomalies)
    enemy = SimpleNamespace(sim_instance=sim_instance, dynamic=dynamic)
    dynamic_buff_list: dict[str, list[Any]] = {"enemy": []}
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index="vivian-cinema6"),
    )
    logic = VivianCinema6Trigger(buff_instance)
    record = VivianCinema6TriggerRecord()
    record.char = char
    record.enemy = enemy
    record.dynamic_buff_list = dynamic_buff_list
    record.guard_feather = 3
    return logic, record, dispatch_port, SimpleNamespace(
        sim_instance=sim_instance,
        schedule_data=schedule_data,
        char=char,
        feather_manager=feather_manager,
        feather_updates=feather_manager.update_calls,
        dynamic_buff_list=dynamic_buff_list,
        action_log=action_log,
        dynamic=dynamic,
    )


def test_vivian_cinema6_publishes_extra_dirge_anomaly_via_dispatch_port(
    monkeypatch: pytest.MonkeyPatch,
):
    active_anomaly = _build_active_anomaly(sim_instance=SimpleNamespace())
    logic, record, dispatch_port, harness = _build_logic_harness(
        active_anomalies=[active_anomaly]
    )
    active_anomaly.sim_instance = harness.sim_instance

    monkeypatch.setattr(logic, "check_record_module", lambda: setattr(logic, "record", record))
    monkeypatch.setattr(logic, "get_prepared", lambda **kwargs: None)
    monkeypatch.setattr(trigger_module, "VIVIAN_REPORT", False)
    dispatch_factory_calls: list[object] = []

    def fake_create_schedule_dispatch_port(*, sim_instance: object) -> _RecordingDispatchPort:
        dispatch_factory_calls.append(sim_instance)
        harness.action_log.append(("create_schedule_dispatch_port", sim_instance))
        return dispatch_port

    monkeypatch.setattr(
        trigger_module,
        "create_schedule_dispatch_port",
        fake_create_schedule_dispatch_port,
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

    skill_node = _build_skill_node()

    assert logic.special_judge_logic(skill_node=skill_node) is True
    assert harness.dynamic.calls == ["is_under_anomaly"]
    assert record.last_update_node is skill_node
    assert record.guard_feather == 3
    assert harness.feather_manager.guard_feather == 0
    assert harness.feather_manager.c1_counter == 0
    assert harness.feather_manager.flight_feather == 3
    assert dispatch_factory_calls == []
    assert dispatch_port.events == []

    logic.special_effect_logic()

    assert len(dispatch_port.events) == 1
    published_event = dispatch_port.events[0]
    assert dispatch_factory_calls == [harness.sim_instance]
    assert harness.dynamic.calls == ["is_under_anomaly", "get_active_anomaly"]
    assert [entry[0] for entry in harness.action_log] == [
        "guard_feather",
        "c1_counter",
        "c1_counter",
        "flight_feather",
        "create_schedule_dispatch_port",
        "publish_scheduled",
        "update_myself",
    ]
    assert harness.action_log[4][1] is harness.sim_instance
    assert harness.action_log[5][1] is published_event
    assert isinstance(published_event, DirgeOfDestinyAnomaly)
    assert published_event is not active_anomaly
    assert published_event.marker == "c6-active-anomaly"
    assert published_event.element_type == 4
    assert published_event.settled is True
    assert published_event.settled_calls == 1
    assert published_event.sim_instance is logic.buff_instance.sim_instance
    assert published_event.activated_by.char_name == "\u8587\u8587\u5b89"
    assert published_event.activated_by.skill_tag == "1331"
    assert published_event.anomaly_dmg_ratio == pytest.approx(4.797)
    assert record.cinema_ratio == 1.3
    assert record.guard_feather == 0
    assert harness.feather_updates == [True]
    assert active_anomaly.settled is False
    assert active_anomaly.settled_calls == 0
    assert harness.schedule_data.event_list == []
    assert len(_FakeMultiplierData.instances) == 1
    assert _FakeMultiplierData.instances[0].enemy is record.enemy
    assert _FakeMultiplierData.instances[0].dynamic_buff_list is harness.dynamic_buff_list
    assert _FakeMultiplierData.instances[0].char is harness.char
    assert cal_ap_inputs == [_FakeMultiplierData.instances[0]]


def test_vivian_cinema6_no_anomaly_branch_updates_feathers_without_publish(
    monkeypatch: pytest.MonkeyPatch,
):
    logic, record, dispatch_port, harness = _build_logic_harness(active_anomalies=[])
    record.guard_feather = 4

    monkeypatch.setattr(logic, "check_record_module", lambda: setattr(logic, "record", record))
    monkeypatch.setattr(logic, "get_prepared", lambda **kwargs: None)
    monkeypatch.setattr(trigger_module, "VIVIAN_REPORT", False)
    monkeypatch.setattr(
        trigger_module,
        "create_schedule_dispatch_port",
        lambda *, sim_instance: dispatch_port,
    )
    _block_legacy_event_lookup(monkeypatch)

    skill_node = _build_skill_node()

    assert logic.special_judge_logic(skill_node=skill_node) is True
    assert harness.dynamic.calls == ["is_under_anomaly"]

    logic.special_effect_logic()

    assert dispatch_port.events == []
    assert harness.schedule_data.event_list == []
    assert harness.dynamic.calls == ["is_under_anomaly", "get_active_anomaly"]
    assert record.guard_feather == 0
    assert harness.feather_updates == [True, True]
