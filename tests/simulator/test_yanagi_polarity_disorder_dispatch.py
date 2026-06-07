from __future__ import annotations

import sys
from types import SimpleNamespace
from typing import Any, cast

import pytest
import zsim.define as define_module

sys.modules.setdefault("define", define_module)

import zsim.sim_progress.Buff.BuffXLogic.YanagiPolarityDisorderTrigger as yanagi_module

from zsim.sim_progress.Buff import JudgeTools
from zsim.sim_progress.Buff.BuffXLogic.YanagiPolarityDisorderTrigger import (
    YanagiPolarityDisorderTrigger,
    YanagiPolarityDisorderTriggerRecord,
)
from zsim.sim_progress.Load import LoadingMission
from zsim.sim_progress.Preload import SkillNode


class _FailFastEventList(list):
    def append(self, item):
        raise AssertionError("YanagiPolarityDisorderTrigger should publish via dispatch port")


class _RecordingDispatchPort:
    def __init__(self, call_order: list[str]) -> None:
        self.events: list[object] = []
        self._call_order = call_order

    def publish_scheduled(self, event: object) -> None:
        self._call_order.append("publish")
        self.events.append(event)


class _FakeAnomalyBar:
    def __init__(self, *, marker: str, settled: bool = False) -> None:
        self.marker = marker
        self.settled = settled
        self.settled_calls = 0

    def anomaly_settled(self) -> None:
        self.settled = True
        self.settled_calls += 1

    def __deepcopy__(self, memo):
        copied = type(self)(marker=self.marker, settled=self.settled)
        copied.settled_calls = self.settled_calls
        return copied


def _block_legacy_event_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_find_event_list(*args, **kwargs):
        raise AssertionError("YanagiPolarityDisorderTrigger should not read raw event_list")

    monkeypatch.setattr(
        JudgeTools, "find_event_list", fail_find_event_list, raising=False
    )


def _build_skill_node() -> SkillNode:
    skill = SimpleNamespace(
        skill_tag="1221_Q",
        char_name="鏌?",
        hit_times=1,
        labels=None,
        ticks=12,
        tick_list=[11],
        heavy_attack=False,
        element_type=0,
        trigger_buff_level=6,
    )
    return SkillNode(skill=skill, preload_tick=30)


def test_yanagi_polarity_disorder_trigger_publishes_spawn_output_via_dispatch_port(
    monkeypatch: pytest.MonkeyPatch,
):
    call_order: list[str] = []
    dispatch_port = _RecordingDispatchPort(call_order)
    active_anomaly_bar = _FakeAnomalyBar(marker="active-anomaly", settled=False)
    schedule_data = SimpleNamespace(event_list=_FailFastEventList())
    sim_instance = SimpleNamespace(tick=41, schedule_data=schedule_data)
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index="yanagi-trigger"),
    )
    logic = YanagiPolarityDisorderTrigger(buff_instance)
    record = YanagiPolarityDisorderTriggerRecord()
    record.char = SimpleNamespace(cinema=2)
    record.enemy = SimpleNamespace(
        dynamic=SimpleNamespace(is_under_anomaly=lambda: True),
        get_active_anomaly_bar=lambda: active_anomaly_bar,
    )
    record.e_counter = {"update_from": "prev-hit", "count": 2}
    monkeypatch.setattr(logic, "check_record_module", lambda: setattr(logic, "record", record))
    monkeypatch.setattr(logic, "get_prepared", lambda **kwargs: None)
    monkeypatch.setattr(
        yanagi_module,
        "create_schedule_dispatch_port",
        lambda *, sim_instance: dispatch_port,
    )
    monkeypatch.setattr(yanagi_module, "find_tick", lambda *, sim_instance: sim_instance.tick)
    _block_legacy_event_lookup(monkeypatch)

    skill_node = _build_skill_node()
    loading_mission = LoadingMission(skill_node)
    loading_mission.mission_start(skill_node.preload_tick, report=False)

    spawn_calls: list[tuple[str, object]] = []
    published_output = SimpleNamespace(marker="polarity-output")

    def fake_spawn_output(
        anomaly_bar,
        mode_number,
        polarity_ratio,
        skill_node,
        sim_instance,
    ):
        call_order.append("spawn_output")
        spawn_calls.extend(
            [
                ("mode_number", mode_number),
                ("polarity_ratio", polarity_ratio),
                ("skill_node", skill_node),
                ("sim_instance", sim_instance),
                ("settled", anomaly_bar.settled),
                ("same_object", anomaly_bar is active_anomaly_bar),
                ("marker", anomaly_bar.marker),
            ]
        )
        return published_output

    monkeypatch.setattr("zsim.sim_progress.Update.spawn_output", fake_spawn_output)

    assert logic.special_judge_logic(skill_node=cast(Any, loading_mission)) is True
    assert record.polarity_disorder_update_signal is True

    logic.special_effect_logic(skill_node=skill_node)

    assert dispatch_port.events == [published_output]
    assert schedule_data.event_list == []
    assert active_anomaly_bar.settled is False
    assert active_anomaly_bar.settled_calls == 0
    assert spawn_calls == [
        ("mode_number", 2),
        ("polarity_ratio", 0.5),
        ("skill_node", skill_node),
        ("sim_instance", sim_instance),
        ("settled", True),
        ("same_object", False),
        ("marker", "active-anomaly"),
    ]
    assert call_order == ["spawn_output", "publish"]
    assert record.e_counter == {"update_from": "", "count": 0}
    assert record.polarity_disorder_update_signal is False
    assert record.polarity_disorder_basic_dmg_ratio == 0.2
