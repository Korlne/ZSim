from __future__ import annotations

import inspect
import sys
from types import SimpleNamespace
from typing import Any

import pytest
import zsim.define as define_module

sys.modules.setdefault("define", define_module)

import zsim.sim_progress.Buff.BuffXLogic.HeartstringNocturne as heartstring_module
import zsim.sim_progress.Preload as preload_module
from zsim.sim_progress.Buff.BuffXLogic.HeartstringNocturne import (
    HeartstringNocturne,
    HeartstringNocturneRecord,
)


class _FailFastEventList(list[object]):
    def append(self, item: object) -> None:
        raise AssertionError("listener manager context should not write raw event_list")


class _ForbiddenLayer:
    def __init__(self, label: str) -> None:
        self.label = label

    def __getattr__(self, name: str) -> Any:
        raise AssertionError(f"{self.label} should not be touched: {name}")

    def __call__(self, *args: object, **kwargs: object) -> None:
        raise AssertionError(f"{self.label} should not be called")


class _ScheduleDataProbe:
    def __init__(self) -> None:
        self.event_list = _FailFastEventList()
        self.change_process_calls = 0

    def change_process_state(self) -> None:
        self.change_process_calls += 1
        raise AssertionError("listener manager context should not report-state")


class _HeartstringSkillNodeProbe:
    def __init__(
        self,
        *,
        char_name: str,
        preload_tick: int,
        trigger_buff_level: int,
    ) -> None:
        self.char_name = char_name
        self.preload_tick = preload_tick
        self.skill = SimpleNamespace(trigger_buff_level=trigger_buff_level)


class _HeartstringListenerProbe:
    def __init__(self, *, active_signal: list[object] | None) -> None:
        self.active_signal = active_signal


class _RecordingListenerManager:
    def __init__(self, *, listener: _HeartstringListenerProbe) -> None:
        self.listener = listener
        self.get_listener_calls: list[dict[str, object]] = []

    def get_listener(self, *, listener_owner: object, listener_id: str) -> object:
        self.get_listener_calls.append(
            {"listener_owner": listener_owner, "listener_id": listener_id}
        )
        return self.listener

    def broadcast_event(self, *args: object, **kwargs: object) -> None:
        raise AssertionError("listener manager lookup test should not broadcast")


class _BuffInstanceProbe:
    def __init__(self, *, sim_instance: SimpleNamespace) -> None:
        self.sim_instance = sim_instance
        self.ft = SimpleNamespace(index="Buff-音擎-心弦夜响-攻击力提升")


def _build_heartstring_harness(
    *,
    active_signal: list[object] | None,
    tick: int = 880,
) -> SimpleNamespace:
    listener = _HeartstringListenerProbe(active_signal=active_signal)
    listener_manager = _RecordingListenerManager(listener=listener)
    schedule_data = _ScheduleDataProbe()
    sim_instance = SimpleNamespace(
        tick=tick,
        schedule_data=schedule_data,
        listener_manager=listener_manager,
        runtime_command_port=_ForbiddenLayer("RuntimeCommandPort"),
        legacy_runtime_facade=_ForbiddenLayer("LegacyBuffRuntimeFacade"),
        buff_runtime_read_port=_ForbiddenLayer("BuffRuntimeReadPort"),
    )
    buff_instance = _BuffInstanceProbe(sim_instance=sim_instance)
    trigger = HeartstringNocturne(buff_instance)

    record = HeartstringNocturneRecord()
    record.char = SimpleNamespace(NAME="Astra", CID=1311)
    trigger.record = record
    trigger.buff_0 = SimpleNamespace(history=SimpleNamespace(record=record))

    prepared_calls: list[dict[str, object]] = []

    def record_prepared_call(**kwargs: object) -> None:
        prepared_calls.append(kwargs)

    trigger.check_record_module = lambda: None
    trigger.get_prepared = record_prepared_call

    return SimpleNamespace(
        trigger=trigger,
        record=record,
        listener=listener,
        listener_manager=listener_manager,
        schedule_data=schedule_data,
        prepared_calls=prepared_calls,
    )


def test_heartstring_listener_active_signal_uses_listener_lookup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(preload_module, "SkillNode", _HeartstringSkillNodeProbe)
    active_event = SimpleNamespace(char_name="Astra")
    harness = _build_heartstring_harness(active_signal=[active_event])

    result = harness.trigger.special_judge_logic(
        skill_node=_HeartstringSkillNodeProbe(
            char_name="Other",
            preload_tick=harness.trigger.buff_instance.sim_instance.tick,
            trigger_buff_level=1,
        )
    )

    assert result is True
    assert harness.listener_manager.get_listener_calls == [
        {"listener_owner": harness.record.char, "listener_id": "Heartstring_Nocturne_1"}
    ]
    assert harness.record.listener is harness.listener
    assert harness.record.listener_exist is True
    assert harness.prepared_calls == [{"equipper": "心弦夜响"}]
    assert harness.schedule_data.event_list == []
    assert harness.schedule_data.change_process_calls == 0


def test_heartstring_listener_noop_reuses_cached_listener_without_boundary_writes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(preload_module, "SkillNode", _HeartstringSkillNodeProbe)
    harness = _build_heartstring_harness(active_signal=None)

    first_result = harness.trigger.special_judge_logic(
        skill_node=_HeartstringSkillNodeProbe(
            char_name="Other",
            preload_tick=880,
            trigger_buff_level=5,
        )
    )
    second_result = harness.trigger.special_judge_logic(
        skill_node=_HeartstringSkillNodeProbe(
            char_name="Astra",
            preload_tick=879,
            trigger_buff_level=5,
        )
    )

    assert first_result is False
    assert second_result is False
    assert harness.listener_manager.get_listener_calls == [
        {"listener_owner": harness.record.char, "listener_id": "Heartstring_Nocturne_1"}
    ]
    assert harness.record.listener is harness.listener
    assert harness.record.listener_exist is True
    assert harness.prepared_calls == [
        {"equipper": "心弦夜响"},
        {"equipper": "心弦夜响"},
    ]
    assert harness.schedule_data.event_list == []
    assert harness.schedule_data.change_process_calls == 0


def test_heartstring_source_keeps_listener_lookup_out_of_other_boundaries() -> None:
    source = inspect.getsource(heartstring_module.HeartstringNocturne.special_judge_logic)

    assert "listener_manager.get_listener" in source
    assert 'listener_id="Heartstring_Nocturne_1"' in source
    assert "listener_exist" in source
    for forbidden_term in (
        "ScheduleDispatchPort",
        "create_schedule_dispatch_port",
        "publish_scheduled",
        "RuntimeCommandPort",
        "create_runtime_command_port",
        "LegacyBuffRuntimeFacade",
        "BuffRuntimeReadPort",
        "change_process_state",
        "event_list",
        "broadcast_event",
    ):
        assert forbidden_term not in source
