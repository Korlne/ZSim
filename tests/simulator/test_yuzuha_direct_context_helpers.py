from __future__ import annotations

import importlib
import inspect
import sys
from types import SimpleNamespace
from typing import Any

import pytest

import zsim.define as define_module

sys.modules.setdefault("define", define_module)

trigger_module = importlib.import_module(
    "zsim.sim_progress.Buff.BuffXLogic.YuzuhaHardCandyShotTrigger"
)
cinema4_trigger_module = importlib.import_module(
    "zsim.sim_progress.Buff.BuffXLogic.YuzuhaCinema4QuickAssistTrigger"
)
cinema6_trigger_module = importlib.import_module(
    "zsim.sim_progress.Buff.BuffXLogic.YuzuhaCinema6SheelTrigger"
)
cinema2_trigger_module = importlib.import_module(
    "zsim.sim_progress.Buff.BuffXLogic.YuzuhaCinema2Trigger"
)
sugar_burst_module = importlib.import_module(
    "zsim.sim_progress.Buff.BuffXLogic.YuzuhaSugarBurstAnomalyBuildupBonus"
)
schedule_preload_module = importlib.import_module(
    "zsim.sim_progress.data_struct.SchedulePreload"
)

YuzuhaHardCandyShotTrigger = trigger_module.YuzuhaHardCandyShotTrigger
YuzuhaHardCandyShotTriggerRecord = trigger_module.YuzuhaHardCandyShotTriggerRecord
YuzuhaCinema4QuickAssistTrigger = cinema4_trigger_module.YuzuhaCinema4QuickAssistTrigger
YuzuhaCinema4QuickAssistTriggerRecord = (
    cinema4_trigger_module.YuzuhaCinema4QuickAssistTriggerRecord
)
YuzuhaCinema6SheelTrigger = cinema6_trigger_module.YuzuhaCinema6SheelTrigger
YuzuhaCinema6SheelTriggerRecord = cinema6_trigger_module.YuzuhaCinema6SheelTriggerRecord
YuzuhaCinema2Trigger = cinema2_trigger_module.YuzuhaCinema2Trigger
YuzuhaCinema2TriggerRecord = cinema2_trigger_module.YuzuhaCinema2TriggerRecord
YuzuhaSugarBurstAnomalyBuildupBonus = (
    sugar_burst_module.YuzuhaSugarBurstAnomalyBuildupBonus
)
YuzuhaSugarBurstAnomalyBuildupBonusRecord = (
    sugar_burst_module.YuzuhaSugarBurstAnomalyBuildupBonusRecord
)


class _FailFastEventList(list[object]):
    def append(self, item: object) -> None:
        raise AssertionError("Yuzuha direct context helper should not write raw event_list")


class _RecordingDispatchPort:
    def __init__(self, *, order_log: list[str] | None = None) -> None:
        self.events: list[object] = []
        self.order_log = order_log

    def publish_scheduled(self, event: object) -> None:
        self.events.append(event)
        if self.order_log is not None:
            self.order_log.append("publish")


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


class _Cinema4SkillNodeProbe:
    def __init__(
        self, *, skill_tag: str = "1411_Assault_Aid", last_hit: bool = True
    ) -> None:
        self.skill_tag = skill_tag
        self._last_hit = last_hit
        self.last_hit_ticks: list[int] = []

    def is_last_hit(self, *, tick: int) -> bool:
        self.last_hit_ticks.append(tick)
        return self._last_hit


class _Cinema6SkillNodeProbe:
    def __init__(
        self,
        *,
        skill_tag: str = "1411_Assault_Aid_B",
        preload_tick: int = 1400,
        end_tick: int = 1600,
    ) -> None:
        self.skill_tag = skill_tag
        self.preload_tick = preload_tick
        self.end_tick = end_tick


class _Cinema2SkillNodeProbe:
    def __init__(
        self, *, skill_tag: str = "1411_E_EX_A", last_hit: bool = True
    ) -> None:
        self.skill_tag = skill_tag
        self._last_hit = last_hit
        self.last_hit_ticks: list[int] = []
        self.force_qte_trigger = False

    def is_last_hit(self, *, tick: int) -> bool:
        self.last_hit_ticks.append(tick)
        return self._last_hit


class _ExplodingEnemyDynamicState:
    @property
    def stun(self) -> bool:
        raise AssertionError("pending signal should short-circuit before stun reads")


class _PreloadTickSkillNodeProbe:
    def __init__(self, *, skill_tag: str = "1411_SNA_A", preload_tick: int) -> None:
        self.skill_tag = skill_tag
        self.preload_tick = preload_tick


class _QuickAssistSystemProbe:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def force_active_quick_assist(
        self, *, tick_now: int, skill_node: object, char_name: str
    ) -> None:
        self.calls.append(
            {
                "tick_now": tick_now,
                "skill_node": skill_node,
                "char_name": char_name,
            }
        )


class _CharDataProbe:
    def __init__(self, *, next_char_name: str = "仪玄") -> None:
        self.next_char = SimpleNamespace(NAME=next_char_name)
        self.calls: list[dict[str, int]] = []

    def find_next_char_obj(self, *, char_now: int, direction: int) -> SimpleNamespace:
        self.calls.append({"char_now": char_now, "direction": direction})
        return self.next_char


class _ScheduleDataReportProbe:
    def __init__(self, *, order_log: list[str] | None = None) -> None:
        self.event_list = _FailFastEventList()
        self.change_process_calls = 0
        self.order_log = order_log

    def change_process_state(self) -> None:
        self.change_process_calls += 1
        if self.order_log is not None:
            self.order_log.append("report")


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
        self.ft = SimpleNamespace(index="Buff-角色-柚叶-硬糖射击触发", maxcount=999)
        self.dy = SimpleNamespace(count=0)
        self.simple_start_calls: list[dict[str, object]] = []
        self.update_to_buff_0_calls: list[object] = []

    def simple_start(
        self,
        *,
        timenow: int,
        sub_exist_buff_dict: dict[str, object],
        **kwargs: object,
    ) -> None:
        call = {"timenow": timenow, "sub_exist_buff_dict": sub_exist_buff_dict}
        call.update(kwargs)
        self.simple_start_calls.append(call)

    def update_to_buff_0(self, *, buff_0: object) -> None:
        self.update_to_buff_0_calls.append(buff_0)


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


def _build_cinema4_trigger_harness(
    *,
    tick: int = 1440,
    next_char_name: str = "仪玄",
    report_state: bool = False,
) -> SimpleNamespace:
    quick_assist_system = _QuickAssistSystemProbe()
    char_data = _CharDataProbe(next_char_name=next_char_name)
    schedule_data = (
        _ScheduleDataReportProbe()
        if report_state
        else SimpleNamespace(
            event_list=_FailFastEventList(),
            change_process_state=_ForbiddenLayer("report-state mutation"),
        )
    )
    sim_instance = SimpleNamespace(
        tick=tick,
        preload=SimpleNamespace(
            preload_data=SimpleNamespace(quick_assist_system=quick_assist_system)
        ),
        char_data=char_data,
        schedule_data=schedule_data,
        listener_manager=_ForbiddenLayer("listener broadcast"),
        runtime_command_port=_ForbiddenLayer("RuntimeCommandPort"),
    )
    buff_instance = _BuffInstanceProbe(sim_instance=sim_instance)
    buff_instance.ft = SimpleNamespace(index="Buff-角色-柚叶-4画快速支援触发")
    trigger = YuzuhaCinema4QuickAssistTrigger(buff_instance)

    record = YuzuhaCinema4QuickAssistTriggerRecord()
    record.char = _YuzuhaProbe(sugar_points=0, cinema=4)
    trigger.buff_0 = SimpleNamespace(history=SimpleNamespace(record=record))
    prepared_calls: list[dict[str, object]] = []

    def record_prepared_call(**kwargs: object) -> None:
        prepared_calls.append(kwargs)

    trigger.get_prepared = record_prepared_call

    return SimpleNamespace(
        trigger=trigger,
        record=record,
        buff_instance=buff_instance,
        sim_instance=sim_instance,
        quick_assist_system=quick_assist_system,
        char_data=char_data,
        schedule_data=schedule_data,
        prepared_calls=prepared_calls,
    )


def _build_cinema6_trigger_harness(
    *,
    tick: int = 1440,
    sugar_points: int = 1,
    charging_tick: int = 24,
    sheel_counter: int = 0,
    report_state: bool = False,
    order_log: list[str] | None = None,
) -> SimpleNamespace:
    preload_data = SimpleNamespace(label="cinema6-preload-data")
    schedule_data = (
        _ScheduleDataReportProbe(order_log=order_log)
        if report_state
        else SimpleNamespace(
            event_list=_FailFastEventList(),
            change_process_state=_ForbiddenLayer("report-state mutation"),
        )
    )
    sim_instance = SimpleNamespace(
        tick=tick,
        preload=SimpleNamespace(preload_data=preload_data),
        schedule_data=schedule_data,
        listener_manager=_ForbiddenLayer("listener broadcast"),
        runtime_command_port=_ForbiddenLayer("RuntimeCommandPort"),
    )
    buff_instance = _BuffInstanceProbe(sim_instance=sim_instance)
    buff_instance.ft = SimpleNamespace(index="Buff-角色-柚叶-6画炮弹触发")
    trigger = YuzuhaCinema6SheelTrigger(buff_instance)

    record = YuzuhaCinema6SheelTriggerRecord()
    record.char = _YuzuhaProbe(sugar_points=sugar_points, cinema=6)
    record.charging_tick = charging_tick
    record.sheel_counter = sheel_counter
    trigger.buff_0 = SimpleNamespace(history=SimpleNamespace(record=record))
    prepared_calls: list[dict[str, object]] = []

    def record_prepared_call(**kwargs: object) -> None:
        prepared_calls.append(kwargs)

    trigger.get_prepared = record_prepared_call

    return SimpleNamespace(
        trigger=trigger,
        record=record,
        buff_instance=buff_instance,
        sim_instance=sim_instance,
        preload_data=preload_data,
        schedule_data=schedule_data,
        prepared_calls=prepared_calls,
    )


def _build_cinema2_trigger_harness(
    *,
    tick: int = 1500,
    last_update_tick: int | None = None,
    report_state: bool = False,
    enemy_stunned: bool = False,
) -> SimpleNamespace:
    schedule_data = (
        _ScheduleDataReportProbe()
        if report_state
        else SimpleNamespace(
            event_list=_FailFastEventList(),
            change_process_state=_ForbiddenLayer("report-state mutation"),
        )
    )
    sim_instance = SimpleNamespace(
        tick=tick,
        schedule_data=schedule_data,
        listener_manager=_ForbiddenLayer("listener broadcast"),
        runtime_command_port=_ForbiddenLayer("RuntimeCommandPort"),
        calculator=_ForbiddenLayer("formula"),
        formula=_ForbiddenLayer("formula"),
        dynamic_buff=_ForbiddenLayer("old-container"),
        exist_buff_dict=_ForbiddenLayer("old-container"),
        loading_buff=_ForbiddenLayer("old-container"),
    )
    buff_instance = _BuffInstanceProbe(sim_instance=sim_instance)
    buff_instance.ft = SimpleNamespace(index="Buff-角色-柚叶-2画触发", maxcount=999)
    trigger = YuzuhaCinema2Trigger(buff_instance)

    record = YuzuhaCinema2TriggerRecord()
    record.enemy = SimpleNamespace(dynamic=SimpleNamespace(stun=enemy_stunned))
    record.last_update_tick = last_update_tick
    trigger.buff_0 = SimpleNamespace(history=SimpleNamespace(record=record))
    prepared_calls: list[dict[str, object]] = []

    def record_prepared_call(**kwargs: object) -> None:
        prepared_calls.append(kwargs)

    trigger.get_prepared = record_prepared_call

    return SimpleNamespace(
        trigger=trigger,
        record=record,
        buff_instance=buff_instance,
        sim_instance=sim_instance,
        schedule_data=schedule_data,
        prepared_calls=prepared_calls,
    )


def _assert_cinema2_no_forbidden_side_effects(
    harness: SimpleNamespace,
    skill_node: _Cinema2SkillNodeProbe,
) -> None:
    assert harness.sim_instance.schedule_data.event_list == []
    assert harness.buff_instance.simple_start_calls == []
    assert harness.buff_instance.update_to_buff_0_calls == []
    assert skill_node.force_qte_trigger is False


def _build_sugar_burst_trigger_harness(
    *,
    tick: int = 1800,
    na_skill_level: int = 8,
) -> SimpleNamespace:
    sim_instance = SimpleNamespace(
        tick=tick,
        schedule_data=SimpleNamespace(
            event_list=_FailFastEventList(),
            change_process_state=_ForbiddenLayer("report-state mutation"),
        ),
        listener_manager=_ForbiddenLayer("listener broadcast"),
        runtime_command_port=_ForbiddenLayer("RuntimeCommandPort"),
    )
    buff_instance = _BuffInstanceProbe(sim_instance=sim_instance)
    buff_instance.ft = SimpleNamespace(index="Buff-角色-柚叶-彩糖花火积蓄值提升", maxcount=999)
    trigger = YuzuhaSugarBurstAnomalyBuildupBonus(buff_instance)

    record = YuzuhaSugarBurstAnomalyBuildupBonusRecord()
    record.na_skill_level = na_skill_level
    record.sub_exist_buff_dict = {buff_instance.ft.index: object()}
    trigger.buff_0 = SimpleNamespace(history=SimpleNamespace(record=record))
    prepared_calls: list[dict[str, object]] = []

    def record_prepared_call(**kwargs: object) -> None:
        prepared_calls.append(kwargs)

    trigger.get_prepared = record_prepared_call

    return SimpleNamespace(
        trigger=trigger,
        record=record,
        buff_instance=buff_instance,
        sim_instance=sim_instance,
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


def test_yuzuha_cinema4_quick_assist_reads_context_and_forwards_tick(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(cinema4_trigger_module, "YUZUHA_REPORT", False)
    harness = _build_cinema4_trigger_harness(tick=1440, next_char_name="仪玄")
    skill_node = _Cinema4SkillNodeProbe()

    assert harness.trigger.special_judge_logic(skill_node=skill_node) is True

    assert harness.prepared_calls == [{"char_CID": 1411}]
    assert skill_node.last_hit_ticks == [1440]
    assert harness.record.trigger_skill_node is skill_node

    harness.trigger.special_hit_logic()

    assert harness.prepared_calls == [{"char_CID": 1411}, {"char_CID": 1411}]
    assert harness.char_data.calls == [{"char_now": 1411, "direction": 1}]
    assert harness.quick_assist_system.calls == [
        {"tick_now": 1440, "skill_node": skill_node, "char_name": "仪玄"}
    ]
    assert harness.record.trigger_skill_node is None
    assert harness.sim_instance.schedule_data.event_list == []


def test_yuzuha_cinema4_non_last_hit_blocks_quick_assist_context(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(cinema4_trigger_module, "YUZUHA_REPORT", False)
    harness = _build_cinema4_trigger_harness(tick=1440)
    skill_node = _Cinema4SkillNodeProbe(last_hit=False)

    assert harness.trigger.special_judge_logic(skill_node=skill_node) is False

    assert harness.prepared_calls == [{"char_CID": 1411}]
    assert skill_node.last_hit_ticks == [1440]
    assert harness.record.trigger_skill_node is None
    assert harness.quick_assist_system.calls == []
    assert harness.char_data.calls == []
    assert harness.buff_instance.simple_start_calls == []
    assert harness.sim_instance.schedule_data.event_list == []


def test_yuzuha_cinema4_report_state_stays_out_of_dispatch_and_runtime(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(cinema4_trigger_module, "YUZUHA_REPORT", True)
    harness = _build_cinema4_trigger_harness(report_state=True)
    skill_node = _Cinema4SkillNodeProbe()

    assert harness.trigger.special_judge_logic(skill_node=skill_node) is True
    harness.trigger.special_hit_logic()

    assert harness.quick_assist_system.calls == [
        {"tick_now": 1440, "skill_node": skill_node, "char_name": "仪玄"}
    ]
    assert harness.schedule_data.change_process_calls == 1
    assert harness.schedule_data.event_list == []


def test_yuzuha_cinema4_trigger_stays_out_of_dispatch_and_runtime_boundaries() -> None:
    source = inspect.getsource(cinema4_trigger_module.YuzuhaCinema4QuickAssistTrigger)

    assert "quick_assist_system" in source
    assert "find_next_char_obj(char_now=1411, direction=1)" in source
    assert "tick_now=sim_instance.tick" in source
    assert "schedule_data.change_process_state()" in source
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


def test_yuzuha_cinema6_preload_publish_uses_current_tick_and_preload_data(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(cinema6_trigger_module, "YUZUHA_REPORT", False)
    dispatch_port = _RecordingDispatchPort()
    monkeypatch.setattr(
        schedule_preload_module,
        "create_schedule_dispatch_port",
        lambda *, sim_instance: dispatch_port,
    )
    harness = _build_cinema6_trigger_harness(
        tick=1440,
        sugar_points=2,
        charging_tick=24,
        sheel_counter=2,
    )
    skill_node = _Cinema6SkillNodeProbe(preload_tick=1400, end_tick=1600)

    assert harness.trigger.special_judge_logic(skill_node=skill_node) is True
    harness.trigger.special_effect_logic()

    assert harness.prepared_calls == [{"char_CID": 1411}, {"char_CID": 1411}]
    assert harness.record.charging_start is True
    assert harness.record.char.resource_reads == 1
    assert len(dispatch_port.events) == 1
    published_event = dispatch_port.events[0]
    assert isinstance(published_event, schedule_preload_module.SchedulePreload)
    assert published_event.execute_tick == 1440
    assert published_event.skill_tag == "1411_Cinema_6"
    assert published_event.preload_data is harness.preload_data
    assert published_event.apl_priority == 0
    assert published_event.active_generation is False
    assert published_event.sim_instance is harness.sim_instance
    assert harness.record.sheel_counter == 3
    assert harness.record.charging_tick == 0
    assert harness.sim_instance.schedule_data.event_list == []


def test_yuzuha_cinema6_charge_gate_blocks_preload_publish_and_context_reads(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(cinema6_trigger_module, "YUZUHA_REPORT", False)
    dispatch_port = _RecordingDispatchPort()
    monkeypatch.setattr(
        schedule_preload_module,
        "create_schedule_dispatch_port",
        lambda *, sim_instance: dispatch_port,
    )
    harness = _build_cinema6_trigger_harness(
        tick=1440,
        sugar_points=2,
        charging_tick=0,
    )
    skill_node = _Cinema6SkillNodeProbe(preload_tick=1430, end_tick=1600)

    assert harness.trigger.special_judge_logic(skill_node=skill_node) is False

    assert harness.prepared_calls == [{"char_CID": 1411}]
    assert harness.record.charging_start is False
    assert harness.record.char.resource_reads == 0
    assert dispatch_port.events == []
    assert harness.sim_instance.schedule_data.event_list == []


def test_yuzuha_cinema6_report_state_stays_separate_from_publish_and_runtime(
    monkeypatch: Any,
) -> None:
    order_log: list[str] = []
    monkeypatch.setattr(cinema6_trigger_module, "YUZUHA_REPORT", True)
    dispatch_port = _RecordingDispatchPort(order_log=order_log)
    monkeypatch.setattr(
        schedule_preload_module,
        "create_schedule_dispatch_port",
        lambda *, sim_instance: dispatch_port,
    )
    harness = _build_cinema6_trigger_harness(
        tick=1500,
        sugar_points=2,
        charging_tick=24,
        report_state=True,
        order_log=order_log,
    )
    skill_node = _Cinema6SkillNodeProbe(preload_tick=1400, end_tick=1600)

    assert harness.trigger.special_judge_logic(skill_node=skill_node) is True
    harness.trigger.special_effect_logic()

    assert order_log == ["publish", "report"]
    assert len(dispatch_port.events) == 1
    assert harness.schedule_data.change_process_calls == 1
    assert harness.schedule_data.event_list == []


def test_yuzuha_cinema6_trigger_keeps_publish_report_and_runtime_boundaries() -> None:
    source = inspect.getsource(cinema6_trigger_module.YuzuhaCinema6SheelTrigger)

    assert "preload_tick_list = [sim_instance.tick]" in source
    assert "preload_data = sim_instance.preload.preload_data" in source
    assert "schedule_preload_event_factory(" in source
    assert "schedule_data.change_process_state()" in source
    for forbidden_term in (
        "RuntimeCommandPort",
        "create_runtime_command_port",
        "LegacyBuffRuntimeFacade",
        "BuffRuntimeReadPort",
        "listener_manager",
        "broadcast_event",
        "event_list",
    ):
        assert forbidden_term not in source


def test_yuzuha_cinema2_report_state_sets_qte_without_dispatch_or_runtime(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(cinema2_trigger_module, "YUZUHA_REPORT", True)
    harness = _build_cinema2_trigger_harness(tick=1500, report_state=True)
    skill_node = _Cinema2SkillNodeProbe()

    assert harness.trigger.special_judge_logic(skill_node=skill_node) is True

    assert harness.prepared_calls == [{"char_CID": 1411, "enemy": 1}]
    assert skill_node.last_hit_ticks == [1500]
    assert harness.record.skill_node_be_changed is skill_node

    harness.trigger.special_hit_logic()

    assert harness.prepared_calls == [
        {"char_CID": 1411, "enemy": 1},
        {"char_CID": 1411},
    ]
    assert skill_node.force_qte_trigger is True
    assert harness.schedule_data.change_process_calls == 1
    assert harness.schedule_data.event_list == []
    assert harness.record.skill_node_be_changed is None
    assert harness.record.last_update_tick == 1500


def test_yuzuha_cinema2_stunned_enemy_blocks_before_last_hit_without_side_effects(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(cinema2_trigger_module, "YUZUHA_REPORT", False)
    harness = _build_cinema2_trigger_harness(enemy_stunned=True)
    skill_node = _Cinema2SkillNodeProbe()

    assert harness.trigger.special_judge_logic(skill_node=skill_node) is False

    assert harness.prepared_calls == [{"char_CID": 1411, "enemy": 1}]
    assert skill_node.last_hit_ticks == []
    assert harness.record.skill_node_be_changed is None
    _assert_cinema2_no_forbidden_side_effects(harness, skill_node)


def test_yuzuha_cinema2_cooldown_blocks_tick_branch_without_report_state(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(cinema2_trigger_module, "YUZUHA_REPORT", False)
    harness = _build_cinema2_trigger_harness(tick=1500, last_update_tick=1490)
    skill_node = _Cinema2SkillNodeProbe()

    assert harness.trigger.special_judge_logic(skill_node=skill_node) is False

    assert harness.prepared_calls == [{"char_CID": 1411, "enemy": 1}]
    assert skill_node.last_hit_ticks == []
    assert harness.record.skill_node_be_changed is None
    _assert_cinema2_no_forbidden_side_effects(harness, skill_node)


def test_yuzuha_cinema2_pending_signal_exception_precedes_stun_helper(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(cinema2_trigger_module, "YUZUHA_REPORT", False)
    harness = _build_cinema2_trigger_harness()
    pending_signal = object()
    harness.record.skill_node_be_changed = pending_signal
    harness.record.enemy = SimpleNamespace(dynamic=_ExplodingEnemyDynamicState())
    skill_node = _Cinema2SkillNodeProbe()

    with pytest.raises(ValueError, match="尚未处理"):
        harness.trigger.special_judge_logic(skill_node=skill_node)

    assert harness.prepared_calls == [{"char_CID": 1411, "enemy": 1}]
    assert skill_node.last_hit_ticks == []
    assert harness.record.skill_node_be_changed is pending_signal
    _assert_cinema2_no_forbidden_side_effects(harness, skill_node)


def test_yuzuha_cinema2_trigger_keeps_report_state_out_of_dispatch_and_runtime() -> None:
    source = inspect.getsource(cinema2_trigger_module.YuzuhaCinema2Trigger)

    assert "if read_enemy_stun_active(self.record.enemy):" in source
    assert "self.record.enemy.dynamic.stun" not in source
    assert "skill_node.is_last_hit(tick=tick)" in source
    assert "schedule_data.change_process_state()" in source
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


def test_yuzuha_sugar_burst_tick_match_updates_count_without_boundary_writes() -> None:
    harness = _build_sugar_burst_trigger_harness(tick=1800, na_skill_level=8)
    skill_node = _PreloadTickSkillNodeProbe(preload_tick=1800)

    assert harness.trigger.special_judge_logic(skill_node=skill_node) is True
    harness.trigger.special_hit_logic()

    assert harness.prepared_calls == [
        {"char_CID": 1411},
        {"char_CID": 1411, "na_skill_level": 1, "sub_exist_buff_dict": 1},
    ]
    assert harness.buff_instance.simple_start_calls == [
        {
            "timenow": 1800,
            "sub_exist_buff_dict": harness.record.sub_exist_buff_dict,
            "no_count": 1,
        }
    ]
    assert harness.buff_instance.dy.count == 18.0
    assert harness.buff_instance.update_to_buff_0_calls == [harness.trigger.buff_0]
    assert harness.sim_instance.schedule_data.event_list == []


def test_yuzuha_sugar_burst_preload_tick_mismatch_blocks_tick_branch() -> None:
    harness = _build_sugar_burst_trigger_harness(tick=1800)
    skill_node = _PreloadTickSkillNodeProbe(preload_tick=1799)

    assert harness.trigger.special_judge_logic(skill_node=skill_node) is False

    assert harness.prepared_calls == [{"char_CID": 1411}]
    assert harness.buff_instance.simple_start_calls == []
    assert harness.buff_instance.update_to_buff_0_calls == []
    assert harness.sim_instance.schedule_data.event_list == []


def test_yuzuha_sugar_burst_trigger_keeps_tick_only_out_of_dispatch_and_runtime() -> None:
    source = inspect.getsource(sugar_burst_module.YuzuhaSugarBurstAnomalyBuildupBonus)

    assert "skill_node.preload_tick != self.buff_instance.sim_instance.tick" in source
    assert "timenow=self.buff_instance.sim_instance.tick" in source
    for forbidden_term in (
        "schedule_data.change_process_state",
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
