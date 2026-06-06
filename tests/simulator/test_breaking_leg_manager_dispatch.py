from __future__ import annotations

import sys
from importlib import import_module
from types import SimpleNamespace
from typing import Any

import pytest
import zsim.define as define_module

sys.modules.setdefault("define", define_module)

import zsim.sim_progress.Buff as buff_module
from zsim.sim_progress.data_struct.sp_update_data import ScheduleRefreshData

breaking_module = import_module("zsim.sim_progress.Enemy.EnemyUniqueMechanic.BreakingLegManager")
BreakingEvent = breaking_module.BreakingEvent


class _FailFastEventList(list):
    def append(self, item):
        raise AssertionError("BreakingEvent should publish refresh data via dispatch port")


class _RecordingDispatchPort:
    def __init__(self, call_order: list[str]) -> None:
        self.call_order = call_order
        self.events: list[object] = []

    def publish_scheduled(self, event: object) -> None:
        self.call_order.append("publish")
        self.events.append(event)


class _EnemyDynamic:
    stun = False

    def get_status(self) -> dict[str, object]:
        return {}


class _FakeEnemy:
    def __init__(self, sim_instance: object, call_order: list[str]) -> None:
        self.max_stun = 2000
        self.max_HP = 100000
        self.sim_instance = sim_instance
        self.dynamic = _EnemyDynamic()
        self.call_order = call_order
        self.stun_updates: list[float] = []
        self.hp_updates: list[float] = []
        self.stun_judge_calls: list[tuple[int, object]] = []
        self._Enemy__HP_update = self._hp_update

    def update_stun(self, stun_value: float) -> None:
        self.call_order.append("update_stun")
        self.stun_updates.append(stun_value)

    def stun_judge(self, tick: int, *, single_hit: object) -> None:
        self.call_order.append("stun_judge")
        self.stun_judge_calls.append((tick, single_hit))

    def _hp_update(self, dmg_value: float) -> None:
        self.call_order.append("hp_update")
        self.hp_updates.append(dmg_value)


def _patch_breaking_dependencies(
    monkeypatch: pytest.MonkeyPatch,
    *,
    dispatch_port: _RecordingDispatchPort,
    expected_sim_instance: object,
    call_order: list[str],
) -> list[tuple[int, object]]:
    find_calls: list[tuple[int, object]] = []

    def fake_find_char_from_cid(char_cid: int, found_sim_instance: object) -> object:
        find_calls.append((char_cid, found_sim_instance))
        return SimpleNamespace(NAME="安比")

    def fake_report_dmg_result(**kwargs: Any) -> None:
        call_order.append("report")
        assert kwargs["tick"] == 120
        assert kwargs["skill_tag"] == "破腿"
        assert kwargs["dmg_expect"] == 5500
        assert kwargs["stun"] == 300

    def fake_create_schedule_dispatch_port(
        *, sim_instance: object
    ) -> _RecordingDispatchPort:
        assert sim_instance is expected_sim_instance
        return dispatch_port

    monkeypatch.setattr(buff_module, "find_char_from_CID", fake_find_char_from_cid)
    monkeypatch.setattr(
        breaking_module,
        "create_schedule_dispatch_port",
        fake_create_schedule_dispatch_port,
    )
    monkeypatch.setattr(breaking_module, "report_dmg_result", fake_report_dmg_result)
    return find_calls


def test_breaking_event_publishes_part_break_refresh_before_same_tick_side_effects(
    monkeypatch: pytest.MonkeyPatch,
):
    call_order: list[str] = []
    dispatch_port = _RecordingDispatchPort(call_order)
    schedule_data = SimpleNamespace(event_list=_FailFastEventList())
    sim_instance = SimpleNamespace(schedule_data=schedule_data)
    enemy = _FakeEnemy(sim_instance, call_order)
    single_hit = SimpleNamespace(skill_tag="1301_TEST_1")
    find_calls = _patch_breaking_dependencies(
        monkeypatch,
        dispatch_port=dispatch_port,
        expected_sim_instance=sim_instance,
        call_order=call_order,
    )

    BreakingEvent(enemy).active(single_hit, tick=120)

    assert call_order == ["publish", "update_stun", "stun_judge", "hp_update", "report"]
    assert len(dispatch_port.events) == 1
    refresh_data = dispatch_port.events[0]
    assert isinstance(refresh_data, ScheduleRefreshData)
    assert refresh_data.sp_target == ("安比",)
    assert refresh_data.decibel_target == ("安比",)
    assert refresh_data.decibel_value == 1000
    assert schedule_data.event_list == []
    assert enemy.stun_updates == [300]
    assert enemy.stun_judge_calls == [(120, single_hit)]
    assert enemy.hp_updates == [5500]
    assert find_calls == [(1301, sim_instance)]


def test_breaking_event_reuses_cached_char_for_repeated_part_break_rewards(
    monkeypatch: pytest.MonkeyPatch,
):
    call_order: list[str] = []
    dispatch_port = _RecordingDispatchPort(call_order)
    schedule_data = SimpleNamespace(event_list=_FailFastEventList())
    sim_instance = SimpleNamespace(schedule_data=schedule_data)
    enemy = _FakeEnemy(sim_instance, call_order)
    event = BreakingEvent(enemy)
    find_calls = _patch_breaking_dependencies(
        monkeypatch,
        dispatch_port=dispatch_port,
        expected_sim_instance=sim_instance,
        call_order=call_order,
    )

    event.update_decibel(SimpleNamespace(skill_tag="1301_TEST_1"))
    event.update_decibel(SimpleNamespace(skill_tag="1301_TEST_2"))

    assert len(dispatch_port.events) == 2
    assert all(isinstance(event, ScheduleRefreshData) for event in dispatch_port.events)
    assert find_calls == [(1301, sim_instance)]
    assert schedule_data.event_list == []
