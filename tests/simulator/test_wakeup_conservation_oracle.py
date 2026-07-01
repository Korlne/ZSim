from __future__ import annotations

import pytest

from zsim.sim_progress.SimulationEngine import (
    FixedTickWakeupSource,
    PlannedEventQueueWakeupSource,
    SimulationClock,
    StopTickWakeupSource,
)
from zsim.sim_progress.data_struct.planned_queue import PlannedEventQueue


class _Event:
    def __init__(self, execute_tick: int) -> None:
        self.execute_tick = execute_tick


def test_clock_never_skips_before_earliest_subsystem_or_stop_tick() -> None:
    clock = SimulationClock()

    assert (
        clock.next_wakeup_tick(
            current_tick=100,
            wakeup_sources=[
                FixedTickWakeupSource(name="apl", tick=150),
                FixedTickWakeupSource(name="buff-duration", tick=120),
                StopTickWakeupSource(110),
            ],
        )
        == 110
    )


def test_planned_queue_source_conserves_stale_events_as_next_tick() -> None:
    events = [_Event(90)]
    queue = PlannedEventQueue(
        get_events=lambda: events,
        set_events=lambda new_events: events.__setitem__(slice(None), new_events),
    )

    assert PlannedEventQueueWakeupSource(queue).next_wakeup_tick(100) == 101


def test_clock_fails_closed_when_no_wakeup_source_can_advance() -> None:
    clock = SimulationClock()

    with pytest.raises(ValueError, match="at least one future"):
        clock.next_wakeup_tick(
            current_tick=10,
            wakeup_sources=[FixedTickWakeupSource(name="idle", tick=None)],
        )
