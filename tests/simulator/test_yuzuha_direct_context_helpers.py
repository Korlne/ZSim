from __future__ import annotations

import importlib
import inspect
import sys
from types import SimpleNamespace
from typing import Any

import zsim.define as define_module

sys.modules.setdefault("define", define_module)

trigger_module = importlib.import_module(
    "zsim.sim_progress.Buff.BuffXLogic.YuzuhaHardCandyShotTrigger"
)

YuzuhaHardCandyShotTrigger = trigger_module.YuzuhaHardCandyShotTrigger
YuzuhaHardCandyShotTriggerRecord = trigger_module.YuzuhaHardCandyShotTriggerRecord


class _FailFastEventList(list[object]):
    def append(self, item: object) -> None:
        raise AssertionError("Yuzuha hard candy trigger should not write raw event_list")


class _ForbiddenLayer:
    def __init__(self, label: str) -> None:
        self.label = label

    def __getattr__(self, name: str) -> Any:
        raise AssertionError(f"{self.label} should not be touched: {name}")

    def __call__(self, *args: object, **kwargs: object) -> None:
        raise AssertionError(f"{self.label} should not be called")


class _PreloadDataProbe:
    def __init__(self, *, occupied: bool) -> None:
        self.occupied = occupied
        self.calls: list[dict[str, int]] = []

    def char_occupied_check(self, *, char_cid: int, tick: int) -> bool:
        self.calls.append({"char_cid": char_cid, "tick": tick})
        return self.occupied


class _SkillNodeProbe:
    def __init__(self, *, char_name: str = "仪玄", hit: bool = True) -> None:
        self.char_name = char_name
        self.skill_tag = "ally_attack"
        self._hit = hit
        self.hit_ticks: list[int] = []

    def is_hit_now(self, *, tick: int) -> bool:
        self.hit_ticks.append(tick)
        return self._hit


class _YuzuhaProbe:
    NAME = "柚叶"
    CID = 1411

    def __init__(self, *, sugar_points: int, cinema: int = 0) -> None:
        self.sugar_points = sugar_points
        self.cinema = cinema
        self.resource_reads = 0
        self.spawn_calls: list[object | None] = []

    def get_resources(self) -> tuple[str, int]:
        self.resource_reads += 1
        return "甜度点", self.sugar_points

    def spawn_hard_candy_shot(self, update_signal: object | None = None) -> None:
        self.spawn_calls.append(update_signal)


class _BuffInstanceProbe:
    def __init__(self, *, sim_instance: SimpleNamespace) -> None:
        self.sim_instance = sim_instance
        self.ft = SimpleNamespace(index="Buff-角色-柚叶-硬糖射击触发")
        self.simple_start_calls: list[dict[str, object]] = []

    def simple_start(self, *, timenow: int, sub_exist_buff_dict: dict[str, object]) -> None:
        self.simple_start_calls.append(
            {"timenow": timenow, "sub_exist_buff_dict": sub_exist_buff_dict}
        )


def _build_trigger_harness(
    *,
    tick: int = 960,
    occupied: bool = False,
    sugar_points: int = 1,
    cinema: int = 0,
    last_update_tick: int | None = None,
) -> SimpleNamespace:
    preload_data = _PreloadDataProbe(occupied=occupied)
    sim_instance = SimpleNamespace(
        tick=tick,
        preload=SimpleNamespace(preload_data=preload_data),
        schedule_data=SimpleNamespace(
            event_list=_FailFastEventList(),
            change_process_state=_ForbiddenLayer("report-state mutation"),
        ),
        listener_manager=_ForbiddenLayer("listener broadcast"),
        runtime_command_port=_ForbiddenLayer("RuntimeCommandPort"),
    )
    char = _YuzuhaProbe(sugar_points=sugar_points, cinema=cinema)
    buff_instance = _BuffInstanceProbe(sim_instance=sim_instance)
    trigger = YuzuhaHardCandyShotTrigger(buff_instance)

    record = YuzuhaHardCandyShotTriggerRecord()
    record.char = char
    record.sub_exist_buff_dict = {buff_instance.ft.index: object()}
    record.cd = None
    record.last_update_tick = last_update_tick
    record.update_signal = None

    trigger.buff_0 = SimpleNamespace(history=SimpleNamespace(record=record))
    prepared_calls: list[dict[str, object]] = []

    def record_prepared_call(**kwargs: object) -> None:
        prepared_calls.append(kwargs)

    trigger.get_prepared = record_prepared_call

    return SimpleNamespace(
        trigger=trigger,
        record=record,
        char=char,
        buff_instance=buff_instance,
        sim_instance=sim_instance,
        preload_data=preload_data,
        prepared_calls=prepared_calls,
    )


def test_yuzuha_hard_candy_tick_and_preload_allow_local_action_path() -> None:
    harness = _build_trigger_harness(tick=960, occupied=False, sugar_points=2)
    skill_node = _SkillNodeProbe()

    assert harness.trigger.special_judge_logic(skill_node=skill_node) is True

    assert harness.prepared_calls == [{"char_CID": 1411}]
    assert skill_node.hit_ticks == [960]
    assert harness.preload_data.calls == [{"char_cid": 1411, "tick": 960}]
    assert harness.char.resource_reads == 1
    assert harness.record.update_signal is skill_node
    assert harness.record.cd == 480
    assert harness.buff_instance.simple_start_calls == []
    assert harness.char.spawn_calls == []

    harness.trigger.special_hit_logic()

    assert len(harness.buff_instance.simple_start_calls) == 1
    simple_start_call = harness.buff_instance.simple_start_calls[0]
    assert simple_start_call["timenow"] == 960
    assert simple_start_call["sub_exist_buff_dict"] is harness.record.sub_exist_buff_dict
    assert harness.char.spawn_calls == [skill_node]
    assert harness.record.last_update_tick == 960
    assert harness.record.update_signal is None
    assert harness.sim_instance.schedule_data.event_list == []


def test_yuzuha_hard_candy_preload_occupancy_blocks_local_action_path() -> None:
    harness = _build_trigger_harness(tick=960, occupied=True, sugar_points=2)
    skill_node = _SkillNodeProbe()

    assert harness.trigger.special_judge_logic(skill_node=skill_node) is False

    assert skill_node.hit_ticks == [960]
    assert harness.preload_data.calls == [{"char_cid": 1411, "tick": 960}]
    assert harness.char.resource_reads == 0
    assert harness.record.update_signal is None
    assert harness.buff_instance.simple_start_calls == []
    assert harness.char.spawn_calls == []
    assert harness.sim_instance.schedule_data.event_list == []


def test_yuzuha_hard_candy_cooldown_blocks_after_preload_and_resource_checks() -> None:
    harness = _build_trigger_harness(
        tick=960,
        occupied=False,
        sugar_points=2,
        last_update_tick=900,
    )
    skill_node = _SkillNodeProbe()

    assert harness.trigger.special_judge_logic(skill_node=skill_node) is False

    assert skill_node.hit_ticks == [960]
    assert harness.preload_data.calls == [{"char_cid": 1411, "tick": 960}]
    assert harness.char.resource_reads == 1
    assert harness.record.cd == 480
    assert harness.record.update_signal is None
    assert harness.buff_instance.simple_start_calls == []
    assert harness.char.spawn_calls == []
    assert harness.sim_instance.schedule_data.event_list == []


def test_yuzuha_hard_candy_trigger_stays_out_of_dispatch_and_runtime_boundaries() -> None:
    source = inspect.getsource(trigger_module.YuzuhaHardCandyShotTrigger)

    assert "sim_instance.tick" in source
    assert "char_occupied_check" in source
    for forbidden_term in (
        "ScheduleDispatchPort",
        "create_schedule_dispatch_port",
        "publish_scheduled",
        "RuntimeCommandPort",
        "create_runtime_command_port",
        "LegacyBuffRuntimeFacade",
        "BuffRuntimeReadPort",
        "listener_manager",
        "broadcast_event",
        "event_list",
    ):
        assert forbidden_term not in source
