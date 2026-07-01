from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from zsim.sim_progress.data_struct.planned_queue import PlannedEventQueue


class WakeupSource(Protocol):
    """Declares the next behavior-relevant Simulation Tick for one subsystem."""

    name: str

    def next_wakeup_tick(self, current_tick: int) -> int | None:
        """Return the next tick strictly after current_tick, or None if idle."""


@dataclass(frozen=True, slots=True)
class FixedTickWakeupSource:
    name: str
    tick: int | None

    def next_wakeup_tick(self, current_tick: int) -> int | None:
        if self.tick is None or self.tick <= current_tick:
            return None
        return self.tick


@dataclass(frozen=True, slots=True)
class StopTickWakeupSource:
    """Wakeup source that preserves the configured simulation stop boundary."""

    tick: int | None
    name: str = "stop-tick"

    def next_wakeup_tick(self, current_tick: int) -> int | None:
        if self.tick is None or self.tick <= current_tick:
            return None
        return self.tick


@dataclass(frozen=True, slots=True)
class ConservativeTickWakeupSource:
    """Temporary per-tick wakeup while a subsystem still has hidden polling needs."""

    name: str = "conservative-next-tick"

    def next_wakeup_tick(self, current_tick: int) -> int:
        return current_tick + 1


@dataclass(frozen=True, slots=True)
class PlannedEventQueueWakeupSource:
    planned_queue: PlannedEventQueue
    name: str = "planned-event-queue"

    def next_wakeup_tick(self, current_tick: int) -> int | None:
        return self.planned_queue.next_due_tick(after_tick=current_tick)


class SimulationClock:
    """Owns Simulation Tick advancement without knowing subsystem internals."""

    def next_wakeup_tick(
        self,
        *,
        current_tick: int,
        wakeup_sources: Iterable[WakeupSource],
    ) -> int:
        candidates: list[tuple[int, str]] = []
        for source in wakeup_sources:
            tick = source.next_wakeup_tick(current_tick)
            if tick is None:
                continue
            if tick <= current_tick:
                raise ValueError(
                    f"WakeupSource {source.name!r} returned non-future tick "
                    f"{tick} for current tick {current_tick}"
                )
            candidates.append((tick, source.name))

        if not candidates:
            raise ValueError("SimulationClock requires at least one future WakeupSource")

        return min(tick for tick, _ in candidates)
