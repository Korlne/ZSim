from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Sequence, cast

import pytest

import zsim.sim_progress.ScheduledEvent as scheduled_event_module
from zsim.sim_progress.ScheduledEvent.buff_runtime import BuffRuntimeReadPort
from zsim.sim_progress.ScheduledEvent.event_handlers.context import EventContext
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
    schedule_data = SimpleNamespace(event_list=[])
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

    assert schedule_data.event_list == [event]
    assert event.executed == []


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
    schedule_data = SimpleNamespace(event_list=[])
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

    assert schedule_data.event_list == []
    assert event.executed == [expected_call]


def test_scheduled_event_process_event_recurses_after_context_requeue() -> None:
    first_event = object()
    requeued_event = object()
    schedule_data = SimpleNamespace(event_list=[first_event], processed_times=0)
    processed: list[object] = []

    scheduled_event = cast(
        Any,
        scheduled_event_module.ScheduledEvent.__new__(scheduled_event_module.ScheduledEvent),
    )
    scheduled_event.data = schedule_data
    scheduled_event.solve_buff = lambda: None
    scheduled_event.select_processable_event = lambda: list(schedule_data.event_list)
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
    assert schedule_data.event_list == []
    assert schedule_data.processed_times == 2


def test_skill_handler_damage_effect_continuation_uses_current_schedule_queue(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    event_list: list[object] = []
    dot_list: list[object] = [object()]
    data = SimpleNamespace(event_list=event_list)
    enemy = SimpleNamespace(dynamic=SimpleNamespace(dynamic_dot_list=dot_list))
    event = object()
    call_order: list[tuple[str, object, object, object | None]] = []

    def _process_hit(tick: int, received_dot_list: list[object], received_event_list: list[object]) -> None:
        call_order.append(("hit", tick, received_dot_list, received_event_list))
        received_event_list.append("hit-continuation")

    def _process_freeze(*, timetick: int, enemy: object, event_list: list[object], event: object) -> bool:
        call_order.append(("freeze", timetick, enemy, event_list))
        event_list.append(event)
        return True

    monkeypatch.setattr(skill_module, "ProcessHitUpdateDots", _process_hit)
    monkeypatch.setattr(skill_module, "ProcessFreezLikeDots", _process_freeze)

    SkillEventHandler()._update_damage_effects(10, cast(Any, enemy), cast(Any, data), cast(Any, event))

    assert call_order == [
        ("hit", 10, dot_list, event_list),
        ("freeze", 10, enemy, event_list),
    ]
    assert event_list == ["hit-continuation", event]


def test_scheduled_event_start_preserves_sp_update_then_process_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dynamic_buff = {"alpha": [object()]}
    call_order: list[str] = []
    captured: dict[str, object] = {}

    class _SPUpdateDataProbe:
        def __init__(self, *, char_obj: object, dynamic_buff: object) -> None:
            captured["sp_char"] = char_obj
            captured["sp_dynamic_buff"] = dynamic_buff
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
    scheduled_event.process_event = lambda: call_order.append("process_event")

    monkeypatch.setattr(scheduled_event_module, "SPUpdateData", _SPUpdateDataProbe)

    scheduled_event.event_start()

    assert captured["sp_char"] is character
    assert captured["sp_dynamic_buff"] is dynamic_buff
    assert isinstance(captured["received_sp_update_data"], _SPUpdateDataProbe)
    assert call_order == [
        "sp_update_data",
        "update_sp_and_decibel",
        "refresh_myself",
        "process_event",
    ]


def test_schedule_dispatch_port_publish_scheduled_remains_queue_only_boundary() -> None:
    event_list: list[object] = []
    schedule_data = SimpleNamespace(event_list=event_list)
    listener_calls: list[object] = []

    dispatch_port = create_schedule_dispatch_port(schedule_data=cast(Any, schedule_data))

    assert isinstance(dispatch_port, ScheduleDispatchPort)

    dispatch_port.publish_scheduled("queued-event")

    assert event_list == ["queued-event"]
    assert listener_calls == []
