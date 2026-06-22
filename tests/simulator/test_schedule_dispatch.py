import inspect
from types import SimpleNamespace
from typing import Any, cast

import pytest

import zsim.sim_progress.data_struct.schedule_dispatch as schedule_dispatch_module
from zsim.sim_progress.Dot.BaseDot import Dot
from zsim.sim_progress.Load.LoadDamageEvent import (
    DamageEventJudge,
    ProcessTimeUpdateDots,
)
from zsim.sim_progress.Load.loading_mission import LoadingMission
from zsim.sim_progress.data_struct.schedule_dispatch import (
    LegacyEventListScheduleDispatchAdapter,
    ScheduleDispatchPort,
    ScheduledEventEmitterProvider,
    create_schedule_dispatch_port,
)


class _RecordingSchedulePublisher:
    def __init__(self) -> None:
        self.events: list[object] = []

    def publish_scheduled(self, event: object) -> None:
        self.events.append(event)


class _RecordingProviderDispatchPort(ScheduleDispatchPort):
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
    assert not isinstance(dispatch_port, LegacyEventListScheduleDispatchAdapter)
    assert not hasattr(dispatch_port, "event_list")

    dispatch_port.publish_scheduled("scheduled-event")

    assert schedule_data.event_list == ["scheduled-event"]


def test_create_schedule_dispatch_port_supports_sim_instance():
    sim_instance = SimpleNamespace(schedule_data=SimpleNamespace(event_list=[]))

    dispatch_port = create_schedule_dispatch_port(sim_instance=sim_instance)
    dispatch_port.publish_scheduled_batch(["alpha", "beta"])

    assert sim_instance.schedule_data.event_list == ["alpha", "beta"]


def test_create_schedule_dispatch_port_follows_rebound_schedule_data_event_list():
    schedule_data = SimpleNamespace(event_list=[])
    old_event_list = schedule_data.event_list
    dispatch_port = create_schedule_dispatch_port(schedule_data=schedule_data)
    dispatch_port.publish_scheduled("old-event")

    schedule_data.event_list = []
    dispatch_port.publish_scheduled("new-event")

    assert old_event_list == ["old-event"]
    assert schedule_data.event_list == ["new-event"]


def test_scheduled_event_provider_from_sim_instance_creates_fresh_dispatch_port_each_emitter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sim_instance = SimpleNamespace(schedule_data=SimpleNamespace(event_list=[]))
    created_ports: list[_RecordingProviderDispatchPort] = []

    def create_recording_dispatch_port(
        *,
        sim_instance: object | None = None,
        schedule_data: object | None = None,
    ) -> _RecordingProviderDispatchPort:
        assert sim_instance is sim_instance_arg
        assert schedule_data is None
        port = _RecordingProviderDispatchPort()
        created_ports.append(port)
        return port

    sim_instance_arg = sim_instance
    monkeypatch.setattr(
        schedule_dispatch_module,
        "create_schedule_dispatch_port",
        create_recording_dispatch_port,
    )

    provider = ScheduledEventEmitterProvider.from_sim_instance(cast(Any, sim_instance))
    first_emitter = provider.create_emitter()
    second_emitter = provider.create_emitter()

    first_emitter.emit_scheduled("first")
    second_emitter.emit_scheduled("second")

    assert len(created_ports) == 2
    assert created_ports[0].events == ["first"]
    assert created_ports[1].events == ["second"]


def test_scheduled_event_provider_from_sim_instance_getter_uses_current_simulator_each_emitter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_sim = SimpleNamespace(schedule_data=SimpleNamespace(event_list=[]))
    second_sim = SimpleNamespace(schedule_data=SimpleNamespace(event_list=[]))
    current = {"sim_instance": first_sim}
    requested_sim_instances: list[object | None] = []
    created_ports: list[_RecordingProviderDispatchPort] = []

    def create_recording_dispatch_port(
        *,
        sim_instance: object | None = None,
        schedule_data: object | None = None,
    ) -> _RecordingProviderDispatchPort:
        assert schedule_data is None
        requested_sim_instances.append(sim_instance)
        port = _RecordingProviderDispatchPort()
        created_ports.append(port)
        return port

    monkeypatch.setattr(
        schedule_dispatch_module,
        "create_schedule_dispatch_port",
        create_recording_dispatch_port,
    )

    provider = ScheduledEventEmitterProvider.from_sim_instance_getter(
        lambda: cast(Any, current["sim_instance"])
    )
    first_emitter = provider.create_emitter()
    current["sim_instance"] = second_sim
    second_emitter = provider.create_emitter()

    first_emitter.emit_scheduled("first")
    second_emitter.emit_scheduled("second")

    assert requested_sim_instances == [first_sim, second_sim]
    assert len(created_ports) == 2
    assert created_ports[0].events == ["first"]
    assert created_ports[1].events == ["second"]


def test_scheduled_event_provider_from_schedule_data_creates_fresh_dispatch_port_each_emitter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    schedule_data = SimpleNamespace(event_list=[])
    created_ports: list[_RecordingProviderDispatchPort] = []

    def create_recording_dispatch_port(
        *,
        sim_instance: object | None = None,
        schedule_data: object | None = None,
    ) -> _RecordingProviderDispatchPort:
        assert sim_instance is None
        assert schedule_data is schedule_data_arg
        port = _RecordingProviderDispatchPort()
        created_ports.append(port)
        return port

    schedule_data_arg = schedule_data
    monkeypatch.setattr(
        schedule_dispatch_module,
        "create_schedule_dispatch_port",
        create_recording_dispatch_port,
    )

    provider = ScheduledEventEmitterProvider.from_schedule_data(cast(Any, schedule_data))
    first_emitter = provider.create_emitter()
    second_emitter = provider.create_emitter()

    first_emitter.emit_scheduled("first")
    second_emitter.emit_scheduled("second")

    assert len(created_ports) == 2
    assert created_ports[0].events == ["first"]
    assert created_ports[1].events == ["second"]


@pytest.mark.parametrize(
    "provider_factory",
    [
        lambda schedule_data: ScheduledEventEmitterProvider.from_sim_instance(
            cast(Any, SimpleNamespace(schedule_data=schedule_data))
        ),
        lambda schedule_data: ScheduledEventEmitterProvider.from_sim_instance_getter(
            lambda: cast(Any, SimpleNamespace(schedule_data=schedule_data))
        ),
        lambda schedule_data: ScheduledEventEmitterProvider.from_schedule_data(
            cast(Any, schedule_data)
        ),
    ],
)
def test_scheduled_event_provider_emit_follows_rebound_schedule_data_event_list(
    provider_factory: Any,
) -> None:
    schedule_data = SimpleNamespace(event_list=[])
    old_event_list = schedule_data.event_list
    provider = provider_factory(schedule_data)
    emitter = provider.create_emitter()

    schedule_data.event_list = []
    emitter.emit_scheduled("rebound-event")

    assert old_event_list == []
    assert schedule_data.event_list == ["rebound-event"]


def test_scheduled_event_provider_retains_callable_factory_only() -> None:
    schedule_data = SimpleNamespace(event_list=[])
    provider = ScheduledEventEmitterProvider.from_schedule_data(cast(Any, schedule_data))
    before_create = dict(provider.__dict__)

    provider.create_emitter()

    assert set(provider.__dict__) == {"_dispatch_port_factory"}
    assert provider.__dict__ == before_create
    assert callable(provider.__dict__["_dispatch_port_factory"])


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


def test_schedule_dispatch_module_remains_queue_only_boundary():
    source = inspect.getsource(schedule_dispatch_module)

    assert "self._queue_owner.enqueue(event)" in source
    assert source.count("self._event_queue.append(event)") == 2
    for forbidden_token in (
        "listener_manager",
        "broadcast_event",
        "RuntimeCommandPort",
        "runtime_command",
        "create_runtime_command_port",
        "run_update_anomaly",
        "dot_runtime",
    ):
        assert forbidden_token not in source


def test_legacy_event_list_adapter_is_documented_as_compatibility_only():
    doc = LegacyEventListScheduleDispatchAdapter.__doc__ or ""

    assert "Compatibility wrapper" in doc
    assert "create_schedule_dispatch_port" in doc


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
