from __future__ import annotations

from collections.abc import Callable, Iterable, MutableSequence
from collections.abc import Iterator
from typing import Any


class PlannedEventQueue:
    """Owns planned-event queue lifecycle with an explicit migration raw view."""

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

    def _raw_events_for_migration(self) -> MutableSequence[Any]:
        """Return the current raw list for explicit migration/test adapters."""
        return self._events()

    def enqueue(self, event: Any) -> None:
        self._events().append(event)

    def enqueue_batch(self, events: Iterable[Any]) -> None:
        for event in events:
            self.enqueue(event)

    def snapshot(self) -> list[Any]:
        return list(self._events())

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
    """Return the planned queue owner for real or test-shaped schedule data."""
    queue = getattr(schedule_data, "planned_event_queue", None)
    if queue is not None:
        return queue

    fallback_queue = getattr(schedule_data, "_planned_event_queue_compat_owner", None)
    if fallback_queue is None:
        fallback_queue = PlannedEventQueue(
            get_events=lambda: schedule_data.event_list,
            set_events=lambda events: setattr(schedule_data, "event_list", events),
        )
        setattr(schedule_data, "_planned_event_queue_compat_owner", fallback_queue)
    return fallback_queue
