from __future__ import annotations

import inspect
from types import SimpleNamespace
from typing import Any, Sequence, cast

import pytest

import zsim.sim_progress.ScheduledEvent as scheduled_event_module
from zsim.sim_progress.ScheduledEvent.buff_runtime import BuffRuntimeReadPort
from zsim.sim_progress.ScheduledEvent.event_handlers.context import EventContext
from zsim.sim_progress.ScheduledEvent.event_handlers import (
    create_default_event_handler_factory,
    event_handler_factory,
    register_all_handlers,
)
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers import skill as skill_module
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers.polarized_assault import (
    PolarizedAssaultEventHandler,
)
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers.preload import (
    PreloadEventHandler,
)
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers.quick_assist import (
    QuickAssistEventHandler,
)
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers.stun_forced_termination import (
    StunForcedTerminationEventHandler,
)
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers.skill import SkillEventHandler
from zsim.sim_progress.data_struct.schedule_dispatch import (
    ScheduleDispatchPort,
    create_schedule_dispatch_port,
)
from zsim.sim_progress.data_struct.planned_queue import (
    PlannedEventQueue,
    ensure_event_list_migration_planned_event_queue,
)
from zsim.sim_progress.data_struct.SchedulePreload import SchedulePreload


class _RuntimeViewStub(BuffRuntimeReadPort):
    def get_active_buffs(self, beneficiary: str) -> Sequence[Any]:
        return ()

    def get_active_buff_view(self):
        return {}

    def get_exist_buff_snapshot(self, beneficiary: str):
        return {}

    def get_exist_buff_snapshot_view(self):
        return {}

    def get_legacy_dynamic_buff_dict(self):
        raise AssertionError("retained scheduler tests should not read legacy dynamic buff")

    def get_legacy_exist_buff_dict(self):
        raise AssertionError("retained scheduler tests should not read legacy exist buff")


class _RetainedEventProbe:
    def __init__(self, execute_tick: int) -> None:
        self.execute_tick = execute_tick
        self.executed: list[tuple[str, tuple[Any, ...]]] = []

    def execute_myself(self) -> None:
        self.executed.append(("execute_myself", ()))

    def execute_update(self, tick: int) -> None:
        self.executed.append(("execute_update", (tick,)))

    def execute(self) -> None:
        self.executed.append(("execute", ()))


class _QueueLifecycleEventProbe:
    def __init__(self, name: str, execute_tick: int, schedule_priority: int = 0) -> None:
        self.name = name
        self.execute_tick = execute_tick
        self.schedule_priority = schedule_priority


class _PlannedQueueOwnerProbe:
    def __init__(self, events: list[object]) -> None:
        self.events = list(events)
        self.calls: list[tuple[str, object]] = []

    def snapshot(self) -> list[object]:
        self.calls.append(("snapshot", tuple(self.events)))
        return list(self.events)

    def replace(self, events: list[object]) -> None:
        self.calls.append(("replace", tuple(events)))
        self.events = list(events)

    def remove(self, event: object) -> None:
        self.calls.append(("remove", event))
        self.events.remove(event)

    def has_events(self) -> bool:
        self.calls.append(("has_events", tuple(self.events)))
        return bool(self.events)


def _make_owner_shaped_schedule_data(
    events: list[object] | None = None,
    **attrs: object,
) -> SimpleNamespace:
    planned_events = [] if events is None else list(events)

    def _get_events() -> list[object]:
        return planned_events

    def _set_events(events: list[object]) -> None:
        nonlocal planned_events
        planned_events = list(events)

    return SimpleNamespace(
        **attrs,
        planned_event_queue=PlannedEventQueue(
            get_events=_get_events,
            set_events=_set_events,
        ),
    )


def _make_planned_event_queue(events: list[object]) -> PlannedEventQueue:
    def _set_events(next_events: list[object]) -> None:
        events[:] = list(next_events)

    return PlannedEventQueue(
        get_events=lambda: events,
        set_events=_set_events,
    )


def _make_scheduled_event_for_sim(sim_instance: Any, tick: int = 10) -> Any:
    dynamic_buff: dict[str, list[object]] = {"alpha": []}
    exist_buff_dict: dict[str, dict[str, object]] = {"alpha": {}}
    loading_buff: dict[str, list[object]] = {"alpha": []}
    enemy = SimpleNamespace(dynamic=SimpleNamespace(dynamic_dot_list=[]))
    schedule_data = _make_owner_shaped_schedule_data(
        enemy=enemy,
        char_obj_list=[],
        change_process_state=lambda: None,
    )
    sim_instance.tick = tick
    sim_instance.schedule_data = schedule_data
    sim_instance.listener_manager = SimpleNamespace(broadcast_event=lambda **kwargs: None)

    return scheduled_event_module.ScheduledEvent(
        dynamic_buff,
        schedule_data,
        tick,
        exist_buff_dict,
        SimpleNamespace(),
        loading_buff=loading_buff,
        legacy_raw_container_compat=True,
        sim_instance=cast(Any, sim_instance),
    )


def test_default_event_handler_factory_cache_clear_reset_is_deterministic() -> None:
    factory = create_default_event_handler_factory()
    event = SchedulePreload(10, "registry_probe")

    first_handler = factory.get_handler(event)
    second_handler = factory.get_handler(event)

    assert first_handler is not None
    assert first_handler.event_type == "preload"
    assert second_handler is first_handler
    assert factory.get_cache_stats()["cache_misses"] == 1
    assert factory.get_cache_stats()["cache_hits"] == 1

    factory.clear_cache()

    assert factory.get_cache_stats()["total_requests"] == 0
    assert factory.get_handler(event) is first_handler
    assert factory.get_cache_stats()["cache_misses"] == 1

    factory.clear_handlers()

    assert factory.list_handlers() == []
    assert factory.get_cache_stats()["total_requests"] == 0

    register_all_handlers(factory)

    assert factory.list_handlers() == [
        "skill",
        "anomaly",
        "disorder",
        "polarity_disorder",
        "abloom",
        "refresh",
        "quick_assist",
        "preload",
        "stun_forced_termination",
        "polarized_assault",
    ]


def test_repeated_scheduled_event_construction_uses_isolated_handler_factories() -> None:
    first = _make_scheduled_event_for_sim(SimpleNamespace(name="sim-a"))
    second = _make_scheduled_event_for_sim(SimpleNamespace(name="sim-b"))
    first_factory = cast(Any, first)._event_handler_factory
    second_factory = cast(Any, second)._event_handler_factory

    assert first_factory is not second_factory
    assert first_factory.list_handlers() == second_factory.list_handlers()

    first_handler = first_factory.get_handler(SchedulePreload(10, "first"))

    assert first_handler is not None
    assert first_factory.get_cache_stats()["total_requests"] == 1
    assert second_factory.get_cache_stats()["total_requests"] == 0


def test_scheduled_event_handler_registry_is_isolated_between_simulator_instances() -> None:
    try:
        event_handler_factory.clear_handlers()
        assert event_handler_factory.list_handlers() == []

        first_sim = SimpleNamespace(name="first-simulator")
        second_sim = SimpleNamespace(name="second-simulator")
        first = _make_scheduled_event_for_sim(first_sim)
        second = _make_scheduled_event_for_sim(second_sim)

        assert cast(Any, first).sim_instance is first_sim
        assert cast(Any, second).sim_instance is second_sim
        assert cast(Any, first)._event_handler_factory is not cast(Any, second)._event_handler_factory
        assert cast(Any, first)._event_handler_factory.list_handlers()
        assert cast(Any, second)._event_handler_factory.list_handlers()
        assert event_handler_factory.list_handlers() == []
    finally:
        register_all_handlers()


@pytest.mark.parametrize(
    "handler_cls",
    [
        PreloadEventHandler,
        QuickAssistEventHandler,
        PolarizedAssaultEventHandler,
        StunForcedTerminationEventHandler,
    ],
)
def test_retained_scheduler_handlers_requeue_future_events_without_executing(
    handler_cls: type[Any],
) -> None:
    schedule_data = _make_owner_shaped_schedule_data()
    context = EventContext(
        data=cast(Any, schedule_data),
        tick=10,
        enemy=cast(Any, SimpleNamespace()),
        buff_runtime_view=_RuntimeViewStub(),
        runtime_command_port=cast(Any, SimpleNamespace()),
        action_stack=cast(Any, SimpleNamespace()),
        sim_instance=cast(Any, SimpleNamespace()),
    )
    event = _RetainedEventProbe(execute_tick=11)

    handler_cls().handle(cast(Any, event), context)

    assert schedule_data.planned_event_queue.snapshot() == [event]
    assert event.executed == []


def test_retained_scheduler_handler_requeue_uses_rebound_schedule_queue() -> None:
    stale_event_list: list[object] = []
    current_event_list: list[object] = []
    schedule_data = SimpleNamespace(event_list=stale_event_list)
    ensure_event_list_migration_planned_event_queue(schedule_data)
    context = EventContext(
        data=cast(Any, schedule_data),
        tick=10,
        enemy=cast(Any, SimpleNamespace()),
        buff_runtime_view=_RuntimeViewStub(),
        runtime_command_port=cast(Any, SimpleNamespace()),
        action_stack=cast(Any, SimpleNamespace()),
        sim_instance=cast(Any, SimpleNamespace()),
    )
    event = _RetainedEventProbe(execute_tick=11)

    schedule_data.event_list = current_event_list

    PreloadEventHandler().handle(cast(Any, event), context)

    assert current_event_list == [event]
    assert stale_event_list == []
    assert event.executed == []


@pytest.mark.parametrize(
    "handler_cls",
    [
        PreloadEventHandler,
        QuickAssistEventHandler,
        PolarizedAssaultEventHandler,
        StunForcedTerminationEventHandler,
    ],
)
def test_retained_scheduler_handlers_requeue_only_through_event_context_api(
    handler_cls: type[Any],
) -> None:
    source = inspect.getsource(handler_cls.handle)

    assert "context.requeue_event(event)" in source
    for forbidden_token in (
        ".event_list.append",
        "publish_scheduled",
        "ScheduleDispatchPort",
        "runtime_command_port",
        "RuntimeCommandPort",
        "listener_manager",
        "broadcast_event",
    ):
        assert forbidden_token not in source


@pytest.mark.parametrize(
    ("handler_cls", "expected_call"),
    [
        (PreloadEventHandler, ("execute_myself", ())),
        (QuickAssistEventHandler, ("execute_update", (10,))),
        (PolarizedAssaultEventHandler, ("execute", ())),
        (StunForcedTerminationEventHandler, ("execute_myself", ())),
    ],
)
def test_retained_scheduler_handlers_execute_due_events_without_requeue(
    handler_cls: type[Any],
    expected_call: tuple[str, tuple[Any, ...]],
) -> None:
    schedule_data = _make_owner_shaped_schedule_data()
    context = EventContext(
        data=cast(Any, schedule_data),
        tick=10,
        enemy=cast(Any, SimpleNamespace()),
        buff_runtime_view=_RuntimeViewStub(),
        runtime_command_port=cast(Any, SimpleNamespace()),
        action_stack=cast(Any, SimpleNamespace()),
        sim_instance=cast(Any, SimpleNamespace()),
    )
    event = _RetainedEventProbe(execute_tick=10)

    handler_cls().handle(cast(Any, event), context)

    assert schedule_data.planned_event_queue.snapshot() == []
    assert event.executed == [expected_call]


def test_scheduled_event_process_event_recurses_after_context_requeue() -> None:
    first_event = object()
    requeued_event = object()
    schedule_data = _make_owner_shaped_schedule_data([first_event], processed_times=0)
    processed: list[object] = []

    scheduled_event = cast(
        Any,
        scheduled_event_module.ScheduledEvent.__new__(scheduled_event_module.ScheduledEvent),
    )
    scheduled_event.data = schedule_data
    scheduled_event.solve_buff = lambda: None
    scheduled_event.select_processable_event = (
        lambda planned_queue=None: schedule_data.planned_event_queue.snapshot()
    )
    scheduled_event.check_all_event = lambda: False

    context = EventContext(
        data=cast(Any, schedule_data),
        tick=10,
        enemy=cast(Any, SimpleNamespace()),
        buff_runtime_view=_RuntimeViewStub(),
        runtime_command_port=cast(Any, SimpleNamespace()),
        action_stack=cast(Any, SimpleNamespace()),
        sim_instance=cast(Any, SimpleNamespace()),
    )

    def _process_single_event(event: object) -> None:
        processed.append(event)
        if event is first_event:
            context.requeue_event(requeued_event)

    scheduled_event._process_single_event = _process_single_event

    scheduled_event.process_event()

    assert processed == [first_event, requeued_event]
    assert schedule_data.planned_event_queue.snapshot() == []
    assert schedule_data.processed_times == 2


def test_scheduled_event_process_event_drains_same_tick_requeue_after_current_batch() -> None:
    first_event = _QueueLifecycleEventProbe("first", execute_tick=10)
    second_event = _QueueLifecycleEventProbe("second", execute_tick=10)
    requeued_event = _QueueLifecycleEventProbe("requeued", execute_tick=10, schedule_priority=-10)
    schedule_data = _make_owner_shaped_schedule_data(
        [first_event, second_event],
        processed_times=0,
    )
    processed: list[object] = []

    scheduled_event = cast(
        Any,
        scheduled_event_module.ScheduledEvent.__new__(scheduled_event_module.ScheduledEvent),
    )
    scheduled_event.data = schedule_data
    scheduled_event.tick = 10
    scheduled_event.get_execute_tick = lambda event: event.execute_tick
    scheduled_event.solve_buff = lambda: None

    context = EventContext(
        data=cast(Any, schedule_data),
        tick=10,
        enemy=cast(Any, SimpleNamespace()),
        buff_runtime_view=_RuntimeViewStub(),
        runtime_command_port=cast(Any, SimpleNamespace()),
        action_stack=cast(Any, SimpleNamespace()),
        sim_instance=cast(Any, SimpleNamespace()),
    )

    def _process_single_event(event: object) -> None:
        processed.append(event)
        if event is first_event:
            context.requeue_event(requeued_event)

    scheduled_event._process_single_event = _process_single_event

    scheduled_event.process_event()

    assert processed == [first_event, second_event, requeued_event]
    assert schedule_data.planned_event_queue.snapshot() == []
    assert schedule_data.processed_times == 3


def test_scheduled_event_process_event_recurses_after_rebound_context_requeue() -> None:
    first_event = _QueueLifecycleEventProbe("first", execute_tick=10)
    requeued_event = _QueueLifecycleEventProbe("requeued", execute_tick=10)
    original_events: list[object] = [first_event]
    rebound_events: list[object] = []
    original_queue = _make_planned_event_queue(original_events)
    rebound_queue = _make_planned_event_queue(rebound_events)
    schedule_data = SimpleNamespace(
        planned_event_queue=original_queue,
        processed_times=0,
    )
    processed: list[object] = []

    scheduled_event = cast(
        Any,
        scheduled_event_module.ScheduledEvent.__new__(scheduled_event_module.ScheduledEvent),
    )
    scheduled_event.data = schedule_data
    scheduled_event.tick = 10
    scheduled_event.get_execute_tick = lambda event: event.execute_tick
    scheduled_event.solve_buff = lambda: None
    scheduled_event.check_all_event = lambda: False

    context = EventContext(
        data=cast(Any, schedule_data),
        tick=10,
        enemy=cast(Any, SimpleNamespace()),
        buff_runtime_view=_RuntimeViewStub(),
        runtime_command_port=cast(Any, SimpleNamespace()),
        action_stack=cast(Any, SimpleNamespace()),
        sim_instance=cast(Any, SimpleNamespace()),
    )

    def _process_single_event(event: object) -> None:
        processed.append(event)
        if event is first_event:
            schedule_data.planned_event_queue = rebound_queue
            context.requeue_event(requeued_event)

    scheduled_event._process_single_event = _process_single_event

    scheduled_event.process_event()

    assert processed == [first_event, requeued_event]
    assert original_queue.snapshot() == []
    assert rebound_queue.snapshot() == []
    assert schedule_data.processed_times == 2


def test_scheduled_event_process_event_uses_planned_queue_owner_lifecycle() -> None:
    future_event = _QueueLifecycleEventProbe("future", execute_tick=11, schedule_priority=0)
    due_low_priority = _QueueLifecycleEventProbe("due-low", execute_tick=10, schedule_priority=0)
    due_high_priority = _QueueLifecycleEventProbe("due-high", execute_tick=10, schedule_priority=10)
    queue_owner = _PlannedQueueOwnerProbe([future_event, due_low_priority, due_high_priority])
    schedule_data = SimpleNamespace(
        planned_event_queue=queue_owner,
        processed_times=0,
    )
    processed: list[object] = []
    scheduled_event = cast(
        Any,
        scheduled_event_module.ScheduledEvent.__new__(scheduled_event_module.ScheduledEvent),
    )
    scheduled_event.data = schedule_data
    scheduled_event.tick = 10
    scheduled_event.get_execute_tick = lambda event: event.execute_tick
    scheduled_event._process_single_event = processed.append

    scheduled_event.process_event()

    assert processed == [due_low_priority, due_high_priority]
    assert queue_owner.events == [future_event]
    assert schedule_data.processed_times == 2
    assert ("replace", (future_event, due_low_priority, due_high_priority)) in queue_owner.calls
    assert ("remove", due_low_priority) in queue_owner.calls
    assert ("remove", due_high_priority) in queue_owner.calls


def test_scheduled_event_solve_buff_reorders_through_planned_queue_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeBuff:
        pass

    non_buff_event = object()
    buff_event = _FakeBuff()
    queue_owner = _PlannedQueueOwnerProbe([non_buff_event, buff_event])
    scheduled_event = cast(
        Any,
        scheduled_event_module.ScheduledEvent.__new__(scheduled_event_module.ScheduledEvent),
    )
    scheduled_event.data = SimpleNamespace(
        planned_event_queue=queue_owner,
    )
    monkeypatch.setattr(scheduled_event_module.Buff, "Buff", _FakeBuff)

    scheduled_event.solve_buff()

    assert queue_owner.events == [buff_event, non_buff_event]
    assert ("replace", (buff_event, non_buff_event)) in queue_owner.calls


def test_scheduled_event_queue_lifecycle_avoids_raw_event_list_mutation() -> None:
    source = inspect.getsource(scheduled_event_module.ScheduledEvent)

    assert "self._planned_event_queue.snapshot()" in source
    assert "self.select_processable_event(planned_queue)" in source
    assert "planned_queue.remove(event)" in source
    assert "self._planned_event_queue.has_events()" in source
    assert "self._planned_event_queue.replace(buff_events + other_events)" in source
    assert "return ensure_planned_event_queue(self.data)" in source
    for forbidden_token in (
        "self.data.event_list.remove(",
        "self.data.event_list = buff_events + other_events",
        "for event in self.data.event_list",
        "for _event in self.data.event_list",
        "_fallback_planned_event_queue",
        "def _replace_planned_events",
    ):
        assert forbidden_token not in source


def test_scheduled_event_context_requeue_uses_current_schedule_queue_after_rebind() -> None:
    stale_event_list: list[object] = []
    current_event_list: list[object] = []
    schedule_data = SimpleNamespace(event_list=stale_event_list)
    ensure_event_list_migration_planned_event_queue(schedule_data)
    scheduled_event = cast(
        Any,
        scheduled_event_module.ScheduledEvent.__new__(scheduled_event_module.ScheduledEvent),
    )
    scheduled_event.data = schedule_data
    scheduled_event.tick = 10
    scheduled_event.enemy = SimpleNamespace()
    scheduled_event.buff_runtime_view = _RuntimeViewStub()
    scheduled_event.runtime_command_port = SimpleNamespace()
    scheduled_event.action_stack = SimpleNamespace()
    scheduled_event.sim_instance = SimpleNamespace()

    context = scheduled_event._create_event_context()
    schedule_data.event_list = current_event_list

    context.requeue_event("queued")

    assert current_event_list == ["queued"]
    assert stale_event_list == []


def test_event_context_requeue_uses_schedule_dispatch_port() -> None:
    source = inspect.getsource(EventContext.requeue_event)

    assert "create_schedule_dispatch_port" in source
    assert ".event_list.append" not in source


def test_skill_handler_damage_effect_continuation_uses_current_schedule_queue(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stale_event_list: list[object] = []
    current_event_list: list[object] = []
    dot_list: list[object] = [object()]
    data = SimpleNamespace(event_list=stale_event_list)
    ensure_event_list_migration_planned_event_queue(data)
    enemy = SimpleNamespace(dynamic=SimpleNamespace(dynamic_dot_list=dot_list))
    event = object()
    call_order: list[tuple[str, object, object, object]] = []

    def _process_hit(tick: int, received_dot_list: list[object], schedule_publisher: Any) -> None:
        call_order.append(("hit", tick, received_dot_list, schedule_publisher))
        data.event_list = current_event_list
        schedule_publisher.publish_scheduled("hit-continuation")

    def _process_freeze(
        *,
        timetick: int,
        enemy: object,
        schedule_publisher: Any,
        event: object,
    ) -> bool:
        call_order.append(("freeze", timetick, enemy, schedule_publisher))
        schedule_publisher.publish_scheduled(event)
        return True

    monkeypatch.setattr(skill_module, "ProcessHitUpdateDots", _process_hit)
    monkeypatch.setattr(skill_module, "ProcessFreezLikeDots", _process_freeze)

    SkillEventHandler()._update_damage_effects(10, cast(Any, enemy), cast(Any, data), cast(Any, event))

    assert call_order == [
        ("hit", 10, dot_list, call_order[0][3]),
        ("freeze", 10, enemy, call_order[1][3]),
    ]
    assert all(isinstance(entry[3], ScheduleDispatchPort) for entry in call_order)
    assert stale_event_list == []
    assert current_event_list == ["hit-continuation", event]


def test_skill_handler_damage_effects_use_schedule_dispatch_port() -> None:
    source = inspect.getsource(SkillEventHandler._update_damage_effects)

    assert "create_schedule_dispatch_port" in source
    assert "schedule_publisher=schedule_dispatch_port" in source
    assert "data.event_list" not in source


def test_scheduled_event_start_preserves_sp_update_then_process_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dynamic_buff = {"alpha": [object()]}
    runtime_view = _RuntimeViewStub()
    sim_instance = SimpleNamespace(marker="sim")
    call_order: list[str] = []
    captured: dict[str, object] = {}

    class _SPUpdateDataProbe:
        def __init__(
            self,
            *,
            char_obj: object,
            runtime_view: object,
            sim_instance: object,
        ) -> None:
            captured["sp_char"] = char_obj
            captured["sp_runtime_view"] = runtime_view
            captured["sp_sim_instance"] = sim_instance
            call_order.append("sp_update_data")

    character = SimpleNamespace()

    def _update_sp_and_decibel(sp_update_data: object) -> None:
        captured["received_sp_update_data"] = sp_update_data
        call_order.append("update_sp_and_decibel")

    def _refresh_myself() -> None:
        call_order.append("refresh_myself")

    character.update_sp_and_decibel = _update_sp_and_decibel
    character.refresh_myself = _refresh_myself

    scheduled_event = cast(
        Any,
        scheduled_event_module.ScheduledEvent.__new__(scheduled_event_module.ScheduledEvent),
    )
    scheduled_event.data = SimpleNamespace(
        char_obj_list=[character],
        dynamic_buff=dynamic_buff,
    )
    scheduled_event.buff_runtime_view = runtime_view
    scheduled_event.sim_instance = sim_instance
    scheduled_event.process_event = lambda: call_order.append("process_event")

    monkeypatch.setattr(scheduled_event_module, "SPUpdateData", _SPUpdateDataProbe)

    scheduled_event.event_start()

    assert captured["sp_char"] is character
    assert captured["sp_runtime_view"] is runtime_view
    assert captured["sp_sim_instance"] is sim_instance
    assert isinstance(captured["received_sp_update_data"], _SPUpdateDataProbe)
    assert call_order == [
        "sp_update_data",
        "update_sp_and_decibel",
        "refresh_myself",
        "process_event",
    ]


def test_schedule_dispatch_port_publish_scheduled_remains_queue_only_boundary() -> None:
    schedule_data = _make_owner_shaped_schedule_data()
    listener_calls: list[object] = []

    dispatch_port = create_schedule_dispatch_port(schedule_data=cast(Any, schedule_data))

    assert isinstance(dispatch_port, ScheduleDispatchPort)

    dispatch_port.publish_scheduled("queued-event")

    assert schedule_data.planned_event_queue.snapshot() == ["queued-event"]
    assert listener_calls == []
