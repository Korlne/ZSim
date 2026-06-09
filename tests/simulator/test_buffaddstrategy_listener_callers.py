from __future__ import annotations

import sys
from collections.abc import Iterable
from types import SimpleNamespace
from typing import Any, SupportsIndex

import pytest
import zsim.define as define_module
import zsim.sim_progress.Character.character as character_module
import zsim.sim_progress.ScheduledEvent as scheduled_event_module
import zsim.sim_progress.ScheduledEvent.buff_runtime as buff_runtime_module
import zsim.sim_progress.ScheduledEvent.runtime_command as runtime_command_module
import zsim.sim_progress.data_struct.BattleEventListener.AliceCinema2DisorderDmgBonus as alice_c2_module
import zsim.sim_progress.data_struct.schedule_dispatch as schedule_dispatch_module

sys.modules.setdefault("define", define_module)

from zsim.models.event_enums import ListenerBroadcastSignal as LBS
from zsim.sim_progress.data_struct import SingleHit
from zsim.sim_progress.data_struct.BattleEventListener.AliceCinema2DisorderDmgBonus import (
    AliceCinema2DisorderDmgBonus,
)
from zsim.sim_progress.data_struct.BattleEventListener.HugoCorePassiveBuffListener import (
    HugoCorePassiveBuffListener,
)
from zsim.sim_progress.data_struct.BattleEventListener.PracticedPerfectionPhyDmgBonusListener import (
    PracticedPerfectionPhyDmgBonusListener,
)


class _FailFastEventList(list[Any]):
    def append(self, item: Any) -> None:
        raise AssertionError("Listener caller should not publish scheduled events")

    def extend(self, items: Iterable[Any]) -> None:
        raise AssertionError("Listener caller should not publish scheduled events")

    def insert(self, index: SupportsIndex, item: Any) -> None:
        raise AssertionError("Listener caller should not publish scheduled events")

    def __setitem__(self, key: SupportsIndex | slice, value: Any) -> None:
        raise AssertionError("Listener caller should not mutate scheduled event queues")


class _FailFastLoadingBuffDict(dict[str, list[Any]]):
    def __getitem__(self, key: str) -> list[Any]:
        raise AssertionError("Listener caller should not touch LOADING_BUFF_DICT")

    def get(self, key: str, default: Any = None) -> Any:
        raise AssertionError("Listener caller should not touch LOADING_BUFF_DICT")

    def __setitem__(self, key: str, value: list[Any]) -> None:
        raise AssertionError("Listener caller should not touch LOADING_BUFF_DICT")


class _ScheduleDataStub:
    def __init__(self) -> None:
        self.event_list = _FailFastEventList()
        self.process_state_changes = 0

    def change_process_state(self) -> None:
        self.process_state_changes += 1


class _CharacterStub:
    def __init__(self, name: str = "派派", weapon_level: int = 3) -> None:
        self.NAME = name
        self.weapon_ID = "十方锻星"
        self.weapon_level = weapon_level


def _fail_listener_broadcast(*args: object, **kwargs: object) -> None:
    raise AssertionError("Listener caller should not broadcast listener events")


def _patch_runtime_boundary_guards(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_create_runtime_command_port(*args: object, **kwargs: object) -> None:
        raise AssertionError("Listener caller should not create RuntimeCommandPort")

    def fail_create_buff_runtime_read_port(*args: object, **kwargs: object) -> None:
        raise AssertionError("Listener caller should not create BuffRuntimeReadPort")

    def fail_create_schedule_dispatch_port(*args: object, **kwargs: object) -> None:
        raise AssertionError("Listener caller should not create ScheduleDispatchPort")

    monkeypatch.setattr(
        runtime_command_module,
        "create_runtime_command_port",
        fail_create_runtime_command_port,
    )
    monkeypatch.setattr(
        scheduled_event_module,
        "create_runtime_command_port",
        fail_create_runtime_command_port,
        raising=False,
    )
    monkeypatch.setattr(
        buff_runtime_module,
        "create_buff_runtime_read_port",
        fail_create_buff_runtime_read_port,
    )
    monkeypatch.setattr(
        scheduled_event_module,
        "create_buff_runtime_read_port",
        fail_create_buff_runtime_read_port,
        raising=False,
    )
    monkeypatch.setattr(
        schedule_dispatch_module,
        "create_schedule_dispatch_port",
        fail_create_schedule_dispatch_port,
    )


def _build_listener_harness() -> SimpleNamespace:
    listener_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def fail_broadcast_event(*args: object, **kwargs: object) -> None:
        listener_calls.append((args, kwargs))
        _fail_listener_broadcast(*args, **kwargs)

    sim_instance = SimpleNamespace(
        tick=2508,
        schedule_data=_ScheduleDataStub(),
        load_data=SimpleNamespace(LOADING_BUFF_DICT=_FailFastLoadingBuffDict()),
        listener_manager=SimpleNamespace(broadcast_event=fail_broadcast_event),
    )
    return SimpleNamespace(listener_calls=listener_calls, sim_instance=sim_instance)


def _patch_listener_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> list[tuple[str | None, dict[str, object]]]:
    _patch_runtime_boundary_guards(monkeypatch)
    monkeypatch.setattr(alice_c2_module, "ALICE_REPORT", False)
    monkeypatch.setattr(define_module, "HUGO_REPORT", False, raising=False)

    buff_add_calls: list[tuple[str | None, dict[str, object]]] = []

    def fake_buff_add_strategy(buff_index: str | None, **kwargs: object) -> None:
        buff_add_calls.append((buff_index, kwargs))

    monkeypatch.setattr(
        "zsim.sim_progress.Buff.BuffAddStrategy.buff_add_strategy",
        fake_buff_add_strategy,
    )
    return buff_add_calls


def _assert_no_cross_layer_writes(harness: SimpleNamespace) -> None:
    assert harness.listener_calls == []
    assert harness.sim_instance.schedule_data.event_list == []
    assert harness.sim_instance.schedule_data.process_state_changes == 0
    assert isinstance(
        harness.sim_instance.load_data.LOADING_BUFF_DICT,
        _FailFastLoadingBuffDict,
    )


def test_alice_cinema2_enemy_target_forwards_sim_instance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _build_listener_harness()
    buff_add_calls = _patch_listener_dependencies(monkeypatch)
    listener = AliceCinema2DisorderDmgBonus(sim_instance=harness.sim_instance)

    listener.listener_active()

    assert buff_add_calls == [
        (
            "Buff-角色-爱丽丝-影画-2画-紊乱伤害提升",
            {"benifit_list": ["enemy"], "sim_instance": harness.sim_instance},
        )
    ]
    _assert_no_cross_layer_writes(harness)


def test_hugo_core_passive_stun_event_forwards_explicit_target(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _build_listener_harness()
    buff_add_calls = _patch_listener_dependencies(monkeypatch)
    listener = HugoCorePassiveBuffListener(sim_instance=harness.sim_instance)
    hit = SingleHit(
        skill_tag="1291_core_passive_source",
        snapshot=(0, 0.0, ()),
        stun=0.0,
        dmg_expect=0.0,
        dmg_crit=0.0,
        hitted_count=1,
        proactive=True,
        skill_node=None,
    )

    listener.listening_event(hit, LBS.STUN)

    assert buff_add_calls == [
        (
            "Buff-角色-雨果-核心被动-暗渊回响",
            {"benifit_list": ["雨果"], "sim_instance": harness.sim_instance},
        )
    ]
    _assert_no_cross_layer_writes(harness)


def test_practiced_perfection_enter_battle_repeats_for_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _build_listener_harness()
    buff_add_calls = _patch_listener_dependencies(monkeypatch)
    monkeypatch.setattr(character_module, "Character", _CharacterStub)
    listener = PracticedPerfectionPhyDmgBonusListener(
        sim_instance=harness.sim_instance
    )
    listener.owner = _CharacterStub(name="派派", weapon_level=3)

    listener.listening_event(event=None, signal=LBS.ENTER_BATTLE)

    assert buff_add_calls == [
        (
            "Buff-武器-精3十方锻星-物理伤害增加",
            {
                "benifit_list": ["派派"],
                "specified_count": 2,
                "sim_instance": harness.sim_instance,
            },
        ),
        (
            "Buff-武器-精3十方锻星-物理伤害增加",
            {"benifit_list": ["派派"], "sim_instance": harness.sim_instance},
        ),
    ]
    _assert_no_cross_layer_writes(harness)


def test_practiced_perfection_assault_signal_keeps_forced_write_noop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _build_listener_harness()
    buff_add_calls = _patch_listener_dependencies(monkeypatch)
    monkeypatch.setattr(character_module, "Character", _CharacterStub)
    listener = PracticedPerfectionPhyDmgBonusListener(
        sim_instance=harness.sim_instance
    )
    listener.owner = _CharacterStub(name="派派", weapon_level=3)

    listener.listening_event(event=None, signal=LBS.ASSAULT_SPAWN)

    assert listener.buff_index == "Buff-武器-精3十方锻星-物理伤害增加"
    assert buff_add_calls == []
    _assert_no_cross_layer_writes(harness)
