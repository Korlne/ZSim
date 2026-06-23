from __future__ import annotations

from collections.abc import Callable, Iterable, MutableSequence
from collections.abc import Iterator
from typing import Any


class PlannedEventQueue:
    """Owns planned-event queue lifecycle while preserving a raw compatibility view."""

    def __init__(
        self,
        *,
        get_events: Callable[[], MutableSequence[Any]],
        set_events: Callable[[list[Any]], None],
    ) -> None:
        self._get_events = get_events
        self._set_events = set_events

    @property
    def compatibility_view(self) -> MutableSequence[Any]:
        """Return the current raw list view for migration/test compatibility."""
        return self._get_events()

    def enqueue(self, event: Any) -> None:
        self.compatibility_view.append(event)

    def enqueue_batch(self, events: Iterable[Any]) -> None:
        for event in events:
            self.enqueue(event)

    def snapshot(self) -> list[Any]:
        return list(self.compatibility_view)

    def __iter__(self) -> Iterator[Any]:
        return iter(self.snapshot())

    def remove(self, event: Any) -> None:
        self.compatibility_view.remove(event)

    def replace(self, events: Iterable[Any]) -> None:
        self._set_events(list(events))

    def clear(self) -> None:
        self.compatibility_view.clear()

    def reset(self) -> None:
        self.replace([])

    def has_events(self) -> bool:
        return bool(self.compatibility_view)
