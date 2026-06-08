from __future__ import annotations

import sys
from types import SimpleNamespace
from typing import Any, Callable

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
from zsim.sim_progress.data_struct import StunForcedTerminationEvent


class _FailFastEventList(list):
    def append(self, item):
        raise AssertionError(
            "HugoCorePassiveTotalizeTrigger should publish planned events via dispatch port"
        )


class _RecordingDispatchPort:
    def __init__(self, call_order: list[str]) -> None:
        self.call_order = call_order
        self.events: list[Any] = []
        self.on_publish: Callable[[object], None] | None = None

    def publish_scheduled(self, event: object) -> None:
        self.call_order.append("publish")
        self.events.append(event)
        if self.on_publish is not None:
            self.on_publish(event)


def _block_legacy_event_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_find_event_list(*args, **kwargs):
        raise AssertionError(
            "HugoCorePassiveTotalizeTrigger should not read raw event_list"
        )

    monkeypatch.setattr(
        JudgeTools, "find_event_list", fail_find_event_list, raising=False
    )


def _build_hugo_harness(
    *,
    active_signal: int,
    cinema: int,
    enemy_stun: bool,
    rest_tick: int = 360,
) -> SimpleNamespace:
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
    record.active_signal = active_signal
    record.char = SimpleNamespace(cinema=cinema)
    record.enemy = SimpleNamespace(
        dynamic=SimpleNamespace(stun=enemy_stun),
        get_stun_rest_tick=lambda: rest_tick,
    )
    record.preload_data = SimpleNamespace(skills=[])
    publish_signal_states: list[int | None] = []
    dispatch_port.on_publish = lambda event: publish_signal_states.append(
        record.active_signal
    )
    return SimpleNamespace(
        call_order=call_order,
        dispatch_port=dispatch_port,
        schedule_data=schedule_data,
        sim_instance=sim_instance,
        logic=logic,
        record=record,
        publish_signal_states=publish_signal_states,
    )


def _patch_hugo_dependencies(
    monkeypatch: pytest.MonkeyPatch,
    harness: SimpleNamespace,
) -> None:
    def fake_check_record_module() -> None:
        harness.logic.record = harness.record

    def fake_get_prepared(**kwargs) -> None:
        return None

    monkeypatch.setattr(harness.logic, "check_record_module", fake_check_record_module)
    monkeypatch.setattr(harness.logic, "get_prepared", fake_get_prepared)
    monkeypatch.setattr(
        hugo_module,
        "create_schedule_dispatch_port",
        lambda *, sim_instance: harness.dispatch_port,
    )
    monkeypatch.setattr(
        hugo_module,
        "find_tick",
        lambda *, sim_instance: sim_instance.tick,
    )
    _block_legacy_event_lookup(monkeypatch)

    buff_add_calls: list[tuple[str, dict[str, object]]] = []

    def fake_buff_add_strategy(buff_index, **kwargs):
        harness.call_order.append(buff_index)
        buff_add_calls.append((buff_index, kwargs))

    monkeypatch.setattr(
        "zsim.sim_progress.Buff.BuffAddStrategy.buff_add_strategy",
        fake_buff_add_strategy,
    )

    expected_node_tag = (
        harness.record.E_totalize_tag
        if harness.record.active_signal == 2
        else harness.record.Q_totalize_tag
    )
    spawned_skill = SimpleNamespace(
        skill_tag=expected_node_tag,
        char_name="Hugo",
        preload_tick=88,
        hit_times=1,
        skill=SimpleNamespace(ticks=20, tick_list=[6], heavy_attack=False),
        end_tick=108,
        loading_mission=None,
    )

    def fake_spawn_node(tag, preload_tick, skills):
        assert tag == expected_node_tag
        assert preload_tick == 88
        assert skills is harness.record.preload_data.skills
        return spawned_skill

    monkeypatch.setattr("zsim.sim_progress.Preload.SkillsQueue.spawn_node", fake_spawn_node)

    original_mission_start = LoadingMission.mission_start

    def fake_mission_start(self, timenow: int, **kwargs) -> None:
        harness.call_order.append("mission_start")
        assert timenow == 88
        original_mission_start(self, timenow, **kwargs)

    monkeypatch.setattr(LoadingMission, "mission_start", fake_mission_start)

    harness.buff_add_calls = buff_add_calls
    harness.spawned_skill = spawned_skill


def test_hugo_totalize_node_publishes_via_dispatch_port_before_any_raw_queue_access(
    monkeypatch: pytest.MonkeyPatch,
):
    harness = _build_hugo_harness(active_signal=2, cinema=6, enemy_stun=False)
    _patch_hugo_dependencies(monkeypatch, harness)

    harness.logic.special_hit_logic()

    assert harness.call_order == [
        harness.record.totalize_buff_index,
        harness.record.cinema_1_buff_index,
        harness.record.cinema_2_buff_index,
        harness.record.cinema_6_buff_index,
        "mission_start",
        "publish",
    ]
    assert [buff_index for buff_index, _ in harness.buff_add_calls] == [
        harness.record.totalize_buff_index,
        harness.record.cinema_1_buff_index,
        harness.record.cinema_2_buff_index,
        harness.record.cinema_6_buff_index,
    ]
    assert harness.buff_add_calls[0][1]["specified_count"] == 2500.0
    for _, kwargs in harness.buff_add_calls:
        assert kwargs["sim_instance"] is harness.sim_instance
        assert isinstance(kwargs["benifit_list"], list)
        assert len(kwargs["benifit_list"]) == 1
        assert isinstance(kwargs["benifit_list"][0], str)
    assert len(harness.dispatch_port.events) == 1
    published_node = harness.dispatch_port.events[0]
    assert published_node is harness.spawned_skill
    assert published_node.loading_mission is not None
    assert isinstance(published_node.loading_mission, LoadingMission)
    assert published_node.loading_mission.mission_node is published_node
    assert published_node.loading_mission.mission_active_state is True
    assert published_node.loading_mission.mission_start_tick == 88
    assert published_node.loading_mission.mission_dict[88.0] == "start"
    assert harness.publish_signal_states == [2]
    assert harness.schedule_data.event_list == []
    assert harness.record.active_signal is None


def test_hugo_stun_event_publishes_via_dispatch_port_when_branch_conditions_match(
    monkeypatch: pytest.MonkeyPatch,
):
    harness = _build_hugo_harness(active_signal=2, cinema=1, enemy_stun=True)
    _patch_hugo_dependencies(monkeypatch, harness)

    harness.logic.special_hit_logic()

    assert harness.call_order == [
        harness.record.totalize_buff_index,
        harness.record.cinema_1_buff_index,
        "mission_start",
        "publish",
        "publish",
    ]
    assert [buff_index for buff_index, _ in harness.buff_add_calls] == [
        harness.record.totalize_buff_index,
        harness.record.cinema_1_buff_index,
    ]
    assert len(harness.dispatch_port.events) == 2
    assert harness.dispatch_port.events[0] is harness.spawned_skill
    published_stun_event = harness.dispatch_port.events[1]
    assert isinstance(published_stun_event, StunForcedTerminationEvent)
    assert published_stun_event.enemy is harness.record.enemy
    assert published_stun_event.feed_back_ratio == 0.25
    assert published_stun_event.execute_tick == 88
    assert harness.publish_signal_states == [2, 2]
    assert harness.schedule_data.event_list == []
    assert harness.record.active_signal is None


def test_hugo_cinema_two_ultimate_keeps_stun_event_skipped_after_gateway_migration(
    monkeypatch: pytest.MonkeyPatch,
):
    harness = _build_hugo_harness(active_signal=6, cinema=2, enemy_stun=True)
    _patch_hugo_dependencies(monkeypatch, harness)

    harness.logic.special_hit_logic()

    assert harness.call_order == [
        harness.record.totalize_buff_index,
        harness.record.cinema_1_buff_index,
        harness.record.cinema_2_buff_index,
        "mission_start",
        "publish",
    ]
    assert [buff_index for buff_index, _ in harness.buff_add_calls] == [
        harness.record.totalize_buff_index,
        harness.record.cinema_1_buff_index,
        harness.record.cinema_2_buff_index,
    ]
    assert len(harness.dispatch_port.events) == 1
    assert harness.dispatch_port.events[0] is harness.spawned_skill
    assert harness.publish_signal_states == [6]
    assert harness.schedule_data.event_list == []
    assert harness.record.active_signal is None


def test_hugo_active_signal_zero_resets_without_scheduled_publish(
    monkeypatch: pytest.MonkeyPatch,
):
    harness = _build_hugo_harness(active_signal=0, cinema=6, enemy_stun=False)
    _patch_hugo_dependencies(monkeypatch, harness)

    harness.logic.special_hit_logic()

    assert harness.call_order == [harness.record.abyss_reverb_buff_index]
    assert [buff_index for buff_index, _ in harness.buff_add_calls] == [
        harness.record.abyss_reverb_buff_index,
    ]
    assert harness.buff_add_calls[0][1]["sim_instance"] is harness.sim_instance
    assert harness.buff_add_calls[0][1]["benifit_list"] == ["雨果"]
    assert harness.dispatch_port.events == []
    assert harness.publish_signal_states == []
    assert harness.schedule_data.event_list == []
    assert harness.record.active_signal is None
