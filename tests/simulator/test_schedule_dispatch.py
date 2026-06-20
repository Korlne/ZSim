from types import SimpleNamespace
from typing import Any, cast

import pytest

from zsim.sim_progress.Dot.BaseDot import Dot
from zsim.sim_progress.Load.LoadDamageEvent import (
    DamageEventJudge,
    ProcessTimeUpdateDots,
)
from zsim.sim_progress.Load.loading_mission import LoadingMission
from zsim.sim_progress.data_struct.schedule_dispatch import (
    LegacyEventListScheduleDispatchAdapter,
    ScheduleDispatchPort,
    create_schedule_dispatch_port,
)


class _RecordingSchedulePublisher:
    def __init__(self) -> None:
        self.events: list[object] = []

    def publish_scheduled(self, event: object) -> None:
        self.events.append(event)


class _ReadyDot(Dot):
    def __init__(
        self,
        *,
        anomaly_data: object | None,
        skill_node_data: object | None,
    ) -> None:
        super().__init__(bar=None, sim_instance=None)
        self.ft.effect_rules = 1
        self.ft.update_cd = 0
        self.ft.max_effect_times = 30
        self.ft.complex_exit_logic = False
        self.anomaly_data = anomaly_data
        self.skill_node_data = skill_node_data
        self.dy.ready = True
        self.dy.effect_times = 0


def _make_loading_mission(tag: str, hit_tick: int) -> LoadingMission:
    skill = SimpleNamespace(ticks=20, tick_list=[], heavy_attack=False)
    mission_node = SimpleNamespace(
        preload_tick=0,
        hit_times=2,
        skill_tag=tag,
        end_tick=99,
        char_name="Alice",
        skill=skill,
    )
    mission = LoadingMission(cast(Any, mission_node))
    mission.mission_active_state = True
    mission.mission_dict = {hit_tick: "hit"}
    return mission


def test_legacy_event_list_schedule_dispatch_adapter_preserves_queue_order():
    event_list = []
    dispatch_port = LegacyEventListScheduleDispatchAdapter(event_list)

    dispatch_port.publish_scheduled("first")
    dispatch_port.publish_scheduled_batch(["second", "third"])

    assert event_list == ["first", "second", "third"]


def test_create_schedule_dispatch_port_uses_schedule_data_without_exposing_event_list():
    schedule_data = SimpleNamespace(event_list=[])

    dispatch_port = create_schedule_dispatch_port(schedule_data=schedule_data)

    assert isinstance(dispatch_port, ScheduleDispatchPort)
    assert not hasattr(dispatch_port, "event_list")

    dispatch_port.publish_scheduled("scheduled-event")

    assert schedule_data.event_list == ["scheduled-event"]


def test_create_schedule_dispatch_port_supports_sim_instance():
    sim_instance = SimpleNamespace(schedule_data=SimpleNamespace(event_list=[]))

    dispatch_port = create_schedule_dispatch_port(sim_instance=sim_instance)
    dispatch_port.publish_scheduled_batch(["alpha", "beta"])

    assert sim_instance.schedule_data.event_list == ["alpha", "beta"]


def test_create_schedule_dispatch_port_rebinds_to_current_schedule_data_event_list():
    schedule_data = SimpleNamespace(event_list=[])
    old_event_list = schedule_data.event_list
    stale_port = create_schedule_dispatch_port(schedule_data=schedule_data)
    stale_port.publish_scheduled("old-event")

    schedule_data.event_list = []
    dispatch_port = create_schedule_dispatch_port(schedule_data=schedule_data)
    dispatch_port.publish_scheduled("new-event")

    assert old_event_list == ["old-event"]
    assert schedule_data.event_list == ["new-event"]


def test_schedule_dispatch_port_public_api_does_not_expose_raw_queue_mutation():
    adapter = LegacyEventListScheduleDispatchAdapter([])
    expected_public_api = {"publish_scheduled", "publish_scheduled_batch"}
    raw_queue_api = {
        "append",
        "clear",
        "event_list",
        "event_queue",
        "extend",
        "insert",
        "pop",
        "queue",
        "remove",
    }

    assert {
        name
        for name in dir(ScheduleDispatchPort)
        if not name.startswith("_") and callable(getattr(ScheduleDispatchPort, name))
    } == expected_public_api
    assert {
        name
        for name in dir(adapter)
        if not name.startswith("_") and callable(getattr(adapter, name))
    } == expected_public_api
    for raw_name in raw_queue_api:
        assert not hasattr(ScheduleDispatchPort, raw_name)
        assert not hasattr(adapter, raw_name)


def test_damage_event_judge_publishes_loading_missions_in_current_order():
    first_mission = _make_loading_mission("1001_First", hit_tick=5)
    second_mission = _make_loading_mission("1001_Second", hit_tick=5)
    publisher = _RecordingSchedulePublisher()
    enemy = SimpleNamespace(dynamic=SimpleNamespace(dynamic_dot_list=[]))

    DamageEventJudge(
        5,
        {"first": first_mission, "second": second_mission},
        cast(Any, enemy),
        publisher,
        [],
    )

    assert publisher.events == [first_mission, second_mission]
    assert first_mission.hitted_count == 1
    assert second_mission.hitted_count == 1


def test_process_time_update_dots_publishes_anomaly_then_skill_node_payloads():
    anomaly_payload = object()
    hidden_skill_payload = object()
    skill_payload = object()
    anomaly_dot = _ReadyDot(
        anomaly_data=anomaly_payload,
        skill_node_data=hidden_skill_payload,
    )
    skill_dot = _ReadyDot(anomaly_data=None, skill_node_data=skill_payload)
    publisher = _RecordingSchedulePublisher()

    ProcessTimeUpdateDots(12, [anomaly_dot, skill_dot], publisher)

    assert publisher.events == [anomaly_payload, skill_payload]
    assert anomaly_dot.dy.effect_times == 1
    assert skill_dot.dy.effect_times == 1


def test_create_schedule_dispatch_port_requires_context():
    with pytest.raises(ValueError, match="sim_instance"):
        create_schedule_dispatch_port()
