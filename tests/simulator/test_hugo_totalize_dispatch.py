from __future__ import annotations

import sys
from types import SimpleNamespace
from typing import Any

import pytest
import zsim.define as define_module

sys.modules.setdefault("define", define_module)

import zsim.sim_progress.Buff.BuffXLogic.HugoCorePassiveTotalizeTrigger as hugo_module

from zsim.sim_progress.Buff import JudgeTools
from zsim.sim_progress.Buff.BuffXLogic.HugoCorePassiveTotalizeTrigger import (
    HugoCorePassiveTotalizeTrigger,
    HugoCorePassiveTotalizeTriggerRecord,
)
from zsim.sim_progress.Load import LoadingMission


class _FailFastEventList(list):
    def append(self, item):
        raise AssertionError("HugoCorePassiveTotalizeTrigger totalize_node should publish via dispatch port")


class _RecordingDispatchPort:
    def __init__(self, call_order: list[str]) -> None:
        self.call_order = call_order
        self.events: list[Any] = []

    def publish_scheduled(self, event: object) -> None:
        self.call_order.append("publish")
        self.events.append(event)


def _block_legacy_event_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_find_event_list(*args, **kwargs):
        raise AssertionError(
            "HugoCorePassiveTotalizeTrigger should not read raw event_list for totalize_node"
        )

    monkeypatch.setattr(JudgeTools, "find_event_list", fail_find_event_list)


def test_hugo_totalize_node_publishes_via_dispatch_port_before_any_raw_queue_access(
    monkeypatch: pytest.MonkeyPatch,
):
    call_order: list[str] = []
    dispatch_port = _RecordingDispatchPort(call_order)
    schedule_data = SimpleNamespace(event_list=_FailFastEventList())
    sim_instance = SimpleNamespace(tick=88, schedule_data=schedule_data)
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index="hugo-totalize"),
    )
    logic = HugoCorePassiveTotalizeTrigger(buff_instance)
    record = HugoCorePassiveTotalizeTriggerRecord()
    record.active_signal = 2
    record.char = SimpleNamespace(cinema=6)
    record.enemy = SimpleNamespace(
        dynamic=SimpleNamespace(stun=False),
        get_stun_rest_tick=lambda: 360,
    )
    record.preload_data = SimpleNamespace(skills=[])

    def fake_check_record_module() -> None:
        logic.record = record

    def fake_get_prepared(**kwargs) -> None:
        return None

    monkeypatch.setattr(logic, "check_record_module", fake_check_record_module)
    monkeypatch.setattr(logic, "get_prepared", fake_get_prepared)
    monkeypatch.setattr(
        hugo_module,
        "create_schedule_dispatch_port",
        lambda *, sim_instance: dispatch_port,
    )
    monkeypatch.setattr(hugo_module, "find_tick", lambda *, sim_instance: sim_instance.tick)
    _block_legacy_event_lookup(monkeypatch)

    buff_add_calls: list[tuple[str, dict[str, object]]] = []

    def fake_buff_add_strategy(buff_index, **kwargs):
        call_order.append(buff_index)
        buff_add_calls.append((buff_index, kwargs))

    monkeypatch.setattr(
        "zsim.sim_progress.Buff.BuffAddStrategy.buff_add_strategy",
        fake_buff_add_strategy,
    )

    spawned_skill = SimpleNamespace(
        skill_tag=record.E_totalize_tag,
        char_name="Hugo",
        preload_tick=88,
        hit_times=1,
        skill=SimpleNamespace(ticks=20, tick_list=[6], heavy_attack=False),
        end_tick=108,
        loading_mission=None,
    )

    def fake_spawn_node(tag, preload_tick, skills):
        assert tag == record.E_totalize_tag
        assert preload_tick == 88
        assert skills is record.preload_data.skills
        return spawned_skill

    monkeypatch.setattr("zsim.sim_progress.Preload.SkillsQueue.spawn_node", fake_spawn_node)

    original_mission_start = LoadingMission.mission_start

    def fake_mission_start(self, timenow: int, **kwargs) -> None:
        call_order.append("mission_start")
        assert timenow == 88
        original_mission_start(self, timenow, **kwargs)

    monkeypatch.setattr(LoadingMission, "mission_start", fake_mission_start)

    logic.special_hit_logic()

    assert call_order == [
        record.totalize_buff_index,
        record.cinema_1_buff_index,
        record.cinema_2_buff_index,
        record.cinema_6_buff_index,
        "mission_start",
        "publish",
    ]
    assert [buff_index for buff_index, _ in buff_add_calls] == [
        record.totalize_buff_index,
        record.cinema_1_buff_index,
        record.cinema_2_buff_index,
        record.cinema_6_buff_index,
    ]
    assert buff_add_calls[0][1]["specified_count"] == 2500.0
    for _, kwargs in buff_add_calls:
        assert kwargs["sim_instance"] is sim_instance
        assert isinstance(kwargs["benifit_list"], list)
        assert len(kwargs["benifit_list"]) == 1
        assert isinstance(kwargs["benifit_list"][0], str)
    assert len(dispatch_port.events) == 1
    published_node = dispatch_port.events[0]
    assert published_node is spawned_skill
    assert published_node.loading_mission is not None
    assert isinstance(published_node.loading_mission, LoadingMission)
    assert published_node.loading_mission.mission_node is published_node
    assert published_node.loading_mission.mission_active_state is True
    assert published_node.loading_mission.mission_start_tick == 88
    assert published_node.loading_mission.mission_dict[88.0] == "start"
    assert schedule_data.event_list == []
    assert record.active_signal is None
