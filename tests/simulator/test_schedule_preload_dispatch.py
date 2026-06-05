from types import SimpleNamespace

import pytest

from zsim.sim_progress.Buff import JudgeTools
from zsim.sim_progress.data_struct.SchedulePreload import (
    SchedulePreload,
    schedule_preload_event_factory,
)


def test_schedule_preload_event_factory_preserves_queue_order_without_raw_event_list_access(
    monkeypatch: pytest.MonkeyPatch,
):
    sim_instance = SimpleNamespace(
        tick=10,
        schedule_data=SimpleNamespace(event_list=[]),
    )
    preload_data = object()

    def fail_find_event_list(*args, **kwargs):
        raise AssertionError("schedule_preload_event_factory should publish via dispatch port")

    monkeypatch.setattr(JudgeTools, "find_event_list", fail_find_event_list)

    schedule_preload_event_factory(
        preload_tick_list=[11, 13],
        skill_tag_list=["alpha", "beta"],
        preload_data=preload_data,
        sim_instance=sim_instance,
        apl_priority_list=[2, 1],
        active_generation_list=[False, True],
    )

    event_list = sim_instance.schedule_data.event_list

    assert [event.skill_tag for event in event_list] == ["alpha", "beta"]
    assert [event.execute_tick for event in event_list] == [11, 13]
    assert [event.apl_priority for event in event_list] == [2, 1]
    assert [event.active_generation for event in event_list] == [False, True]
    assert all(isinstance(event, SchedulePreload) for event in event_list)
    assert all(event.preload_data is preload_data for event in event_list)
    assert all(event.sim_instance is sim_instance for event in event_list)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        (
            {"preload_tick_list": [11, 12], "skill_tag_list": ["alpha"]},
            "preload_tick_list和skill_tag_list的长度不一致",
        ),
        (
            {"apl_priority_list": [1, 2]},
            "apl_priority_list和skill_tag_list的长度不一致",
        ),
        (
            {"active_generation_list": [True, False]},
            "active_generation_list和skill_tag_list的长度不一致",
        ),
    ],
)
def test_schedule_preload_event_factory_keeps_length_validation(
    kwargs: dict[str, list[int] | list[str] | list[bool]],
    message: str,
):
    sim_instance = SimpleNamespace(
        tick=10,
        schedule_data=SimpleNamespace(event_list=[]),
    )
    base_kwargs = {
        "preload_tick_list": [11],
        "skill_tag_list": ["alpha"],
        "preload_data": object(),
        "sim_instance": sim_instance,
        "apl_priority_list": [0],
        "active_generation_list": [False],
    }
    base_kwargs.update(kwargs)

    with pytest.raises(ValueError, match=message):
        schedule_preload_event_factory(**base_kwargs)


def test_schedule_preload_event_factory_rejects_past_ticks():
    sim_instance = SimpleNamespace(
        tick=10,
        schedule_data=SimpleNamespace(event_list=[]),
    )

    with pytest.raises(ValueError, match="不能添加过去的Preload计划事件"):
        schedule_preload_event_factory(
            preload_tick_list=[9],
            skill_tag_list=["alpha"],
            preload_data=object(),
            sim_instance=sim_instance,
        )
