from __future__ import annotations

import sys
from types import SimpleNamespace
from typing import Any, cast

import pytest
import zsim.define as define_module

sys.modules.setdefault("define", define_module)

import zsim.sim_progress.Buff.BuffXLogic.VivianDotTrigger as vivian_module

from zsim.sim_progress.Buff import JudgeTools
from zsim.sim_progress.Buff.BuffXLogic.VivianDotTrigger import (
    VivianDotTrigger,
    VivianDotTriggerRecord,
)
from zsim.sim_progress.Load import LoadingMission
from zsim.sim_progress.Preload import SkillNode


class _FailFastEventList(list):
    def append(self, item):
        raise AssertionError("VivianDotTrigger should publish via dispatch port")


class _RecordingDispatchPort:
    def __init__(self, call_order: list[str]) -> None:
        self.events: list[object] = []
        self._call_order = call_order

    def publish_scheduled(self, event: object) -> None:
        self._call_order.append("publish")
        self.events.append(event)


class _RecordingDotList(list):
    def __init__(self, call_order: list[str]) -> None:
        super().__init__()
        self._call_order = call_order

    def append(self, item):
        self._call_order.append("register_dot")
        super().append(item)


class _FakeViviansProphecy:
    def __init__(self, skill_node_data: SkillNode, call_order: list[str]) -> None:
        self.ft = SimpleNamespace(index="ViviansProphecy")
        self.skill_node_data = skill_node_data
        self.started_at: int | None = None
        self._call_order = call_order

    def start(self, timenow: int) -> None:
        self._call_order.append("dot_start")
        self.started_at = timenow


def _block_legacy_event_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_find_event_list(*args, **kwargs):
        raise AssertionError("VivianDotTrigger should not read raw event_list")

    monkeypatch.setattr(JudgeTools, "find_event_list", fail_find_event_list)


def test_vivian_dot_trigger_registers_dot_and_publishes_skill_node_via_dispatch_port(
    monkeypatch: pytest.MonkeyPatch,
):
    call_order: list[str] = []
    dispatch_port = _RecordingDispatchPort(call_order)
    schedule_data = SimpleNamespace(
        event_list=_FailFastEventList(),
        change_process_state=lambda: None,
    )
    sim_instance = SimpleNamespace(tick=96, schedule_data=schedule_data)
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index="Buff-角色-薇薇安-核心被动-Dot触发器"),
    )
    logic = VivianDotTrigger(buff_instance)

    dynamic_dot_list = _RecordingDotList(call_order)
    enemy = SimpleNamespace(
        dynamic=SimpleNamespace(dynamic_dot_list=dynamic_dot_list),
    )
    enemy.find_dot = lambda dot_index: next(
        (dot for dot in enemy.dynamic.dynamic_dot_list if dot.ft.index == dot_index),
        None,
    )
    record = VivianDotTriggerRecord()
    record.enemy = enemy
    record.char = SimpleNamespace(NAME="薇薇安")

    dot_skill = SimpleNamespace(
        skill_tag="1331_Core_Passive",
        char_name="薇薇安",
        hit_times=2,
        labels=None,
        ticks=18,
        tick_list=[6, 14],
        heavy_attack=False,
        element_type=4,
    )
    dot_skill_node = SkillNode(dot_skill, 96)
    fake_dot = _FakeViviansProphecy(dot_skill_node, call_order)
    spawn_calls: list[str] = []

    def fake_spawn_normal_dot(dot_index: str, *, sim_instance: object) -> _FakeViviansProphecy:
        spawn_calls.append(dot_index)
        assert dot_index == "ViviansProphecy"
        assert sim_instance is logic.buff_instance.sim_instance
        return fake_dot

    monkeypatch.setattr(logic, "check_record_module", lambda: setattr(logic, "record", record))
    monkeypatch.setattr(logic, "get_prepared", lambda **kwargs: None)
    monkeypatch.setattr(vivian_module, "VIVIAN_REPORT", False)
    monkeypatch.setattr(
        vivian_module,
        "create_schedule_dispatch_port",
        lambda *, sim_instance: dispatch_port,
    )
    monkeypatch.setattr(
        "zsim.sim_progress.Update.UpdateAnomaly.spawn_normal_dot",
        fake_spawn_normal_dot,
    )
    _block_legacy_event_lookup(monkeypatch)

    original_mission_start = LoadingMission.mission_start

    def fake_mission_start(self, timenow: int, **kwargs) -> None:
        call_order.append("mission_start")
        assert timenow == 96
        original_mission_start(self, timenow, **kwargs)

    monkeypatch.setattr(LoadingMission, "mission_start", fake_mission_start)

    logic.special_hit_logic()

    assert call_order == ["dot_start", "mission_start", "register_dot", "publish"]
    assert spawn_calls == ["ViviansProphecy"]
    assert dynamic_dot_list == [fake_dot]
    assert fake_dot.started_at == 96
    assert len(dispatch_port.events) == 1
    published_node = cast(Any, dispatch_port.events[0])
    assert published_node is dot_skill_node
    assert isinstance(published_node, SkillNode)
    assert published_node.skill_tag == "1331_Core_Passive"
    assert published_node.preload_tick == 96
    assert published_node.loading_mission is not None
    assert isinstance(published_node.loading_mission, LoadingMission)
    assert published_node.loading_mission.mission_node is published_node
    assert published_node.loading_mission.mission_active_state is True
    assert published_node.loading_mission.mission_start_tick == 96
    assert published_node.loading_mission.mission_dict[96.0] == "start"
    assert published_node.loading_mission.mission_dict[102] == "hit"
    assert published_node.loading_mission.mission_dict[110] == "hit"
    assert schedule_data.event_list == []

    logic.special_hit_logic()

    assert spawn_calls == ["ViviansProphecy"]
    assert dynamic_dot_list == [fake_dot]
    assert len(dispatch_port.events) == 1
    assert call_order == ["dot_start", "mission_start", "register_dot", "publish"]
