from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

from zsim.sim_progress.Character.Yixuan.AdrenalineEventClass import (
    AuricArray,
    AuricInkUndercurrent,
    BaseAdrenalineEvent,
)
from zsim.sim_progress.Character.Yixuan.AdrenalineManagerClass import adrenaline_event_factory


class _FailFastScheduleData:
    @property
    def event_list(self) -> list[object]:
        raise AssertionError("Yixuan adrenaline events are a local event group")


def _build_yixuan_like(
    *, additional_abililty_active: bool, schedule_data: object | None = None
) -> Any:
    return SimpleNamespace(
        NAME="仪玄",
        additional_abililty_active=additional_abililty_active,
        sim_instance=SimpleNamespace(
            tick=0,
            schedule_data=schedule_data or _FailFastScheduleData(),
        ),
    )


def test_yixuan_adrenaline_factory_builds_local_base_events_without_raw_schedule_access():
    char = _build_yixuan_like(additional_abililty_active=True)

    events = adrenaline_event_factory(char_instance=cast(Any, char))

    assert [type(event) for event in events] == [AuricArray, AuricInkUndercurrent]
    assert all(isinstance(event, BaseAdrenalineEvent) for event in events)
    assert [cast(Any, event).char for event in events] == [char, char]


def test_yixuan_adrenaline_factory_does_not_mutate_planned_schedule_queue():
    planned_schedule_queue: list[object] = []
    char = _build_yixuan_like(
        additional_abililty_active=True,
        schedule_data=SimpleNamespace(event_list=planned_schedule_queue),
    )

    events = adrenaline_event_factory(char_instance=cast(Any, char))

    assert [type(event) for event in events] == [AuricArray, AuricInkUndercurrent]
    assert planned_schedule_queue == []


def test_yixuan_adrenaline_factory_preserves_additional_ability_filter():
    char = _build_yixuan_like(additional_abililty_active=False)

    events = adrenaline_event_factory(char_instance=cast(Any, char))

    assert [type(event) for event in events] == [AuricArray]
    assert all(isinstance(event, BaseAdrenalineEvent) for event in events)
    assert cast(Any, events[0]).char is char
