from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, MutableSequence
from typing import Any


class PlannedEventQueue:
    """Owns planned-event queue lifecycle behind explicit owner APIs."""

    def __init__(
        self,
        *,
        get_events: Callable[[], MutableSequence[Any]],
        set_events: Callable[[list[Any]], None],
    ) -> None:
        self._get_events = get_events
        self._set_events = set_events

    def _events(self) -> MutableSequence[Any]:
        return self._get_events()

    def enqueue(self, event: Any) -> None:
        self._events().append(event)

    def enqueue_batch(self, events: Iterable[Any]) -> None:
        for event in events:
            self.enqueue(event)

    def snapshot(self) -> list[Any]:
        return list(self._events())

    def next_due_tick(
        self,
        *,
        after_tick: int,
        execute_tick_resolver: Callable[[Any], int | None] | None = None,
    ) -> int | None:
        """Return the next event due tick after after_tick, preserving owner access."""
        next_tick: int | None = None
        for event in self._events():
            execute_tick = (
                execute_tick_resolver(event)
                if execute_tick_resolver is not None
                else self._default_execute_tick(event)
            )
            if execute_tick is None:
                return after_tick + 1
            if execute_tick <= after_tick:
                return after_tick + 1
            if next_tick is None or execute_tick < next_tick:
                next_tick = execute_tick
        return next_tick

    @staticmethod
    def _default_execute_tick(event: Any) -> int | None:
        for attr_name in ("execute_tick", "preload_tick"):
            execute_tick = getattr(event, attr_name, None)
            if execute_tick is not None:
                return int(execute_tick)
        return None

    def __iter__(self) -> Iterator[Any]:
        return iter(self.snapshot())

    def remove(self, event: Any) -> None:
        self._events().remove(event)

    def replace(self, events: Iterable[Any]) -> None:
        self._set_events(list(events))

    def clear(self) -> None:
        self._events().clear()

    def reset(self) -> None:
        self.replace([])

    def has_events(self) -> bool:
        return bool(self._events())


def ensure_planned_event_queue(schedule_data: Any) -> PlannedEventQueue:
    """Return the planned queue owner exposed by ScheduleData."""
    queue = getattr(schedule_data, "planned_event_queue", None)
    if queue is not None:
        return queue

    raise AttributeError("schedule_data must expose planned_event_queue")
