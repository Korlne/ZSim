from __future__ import annotations

from collections.abc import Iterable
from types import SimpleNamespace
from typing import Any, SupportsIndex

import pytest
import zsim.sim_progress.Character.Seed as seed_character_module
import zsim.sim_progress.Character.Seed.ExStateManager as seed_ex_state_module
import zsim.sim_progress.ScheduledEvent as scheduled_event_module
import zsim.sim_progress.ScheduledEvent.buff_runtime as buff_runtime_module
import zsim.sim_progress.ScheduledEvent.runtime_command as runtime_command_module
import zsim.sim_progress.data_struct.schedule_dispatch as schedule_dispatch_module

from zsim.sim_progress.Character.Seed.ExStateManager import (
    SeedEXState,
    SeedEXStateManager,
)
from zsim.sim_progress.Character.Yanagi.StanceManager import StanceManager


class _FailFastEventList(list[Any]):
    def append(self, item: Any) -> None:
        raise AssertionError("Character caller should not publish scheduled events")

    def extend(self, items: Iterable[Any]) -> None:
        raise AssertionError("Character caller should not publish scheduled events")

    def insert(self, index: SupportsIndex, item: Any) -> None:
        raise AssertionError("Character caller should not publish scheduled events")

    def __setitem__(self, key: SupportsIndex | slice, value: Any) -> None:
        raise AssertionError("Character caller should not mutate scheduled queues")


class _FailFastLoadingBuffDict(dict[str, list[Any]]):
    def __getitem__(self, key: str) -> list[Any]:
        raise AssertionError("Character caller should not touch LOADING_BUFF_DICT")

    def get(self, key: str, default: Any = None) -> Any:
        raise AssertionError("Character caller should not touch LOADING_BUFF_DICT")

    def __setitem__(self, key: str, value: list[Any]) -> None:
        raise AssertionError("Character caller should not touch LOADING_BUFF_DICT")


class _ScheduleDataStub:
    def __init__(self) -> None:
        self.event_list = _FailFastEventList()
        self.pending = _FailFastEventList()
        self.process_state_changes = 0

    def change_process_state(self) -> None:
        self.process_state_changes += 1


class _SeedStub:
    NAME = "席德"

    def __init__(self, *, cinema: int = 2, sim_instance: object | None = None) -> None:
        self.NAME = "席德"
        self.cinema = cinema
        self.sim_instance = sim_instance


def _fail_listener_broadcast(*args: object, **kwargs: object) -> None:
    raise AssertionError("Character caller should not broadcast listener events")


def _patch_runtime_boundary_guards(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_create_runtime_command_port(*args: object, **kwargs: object) -> None:
        raise AssertionError("Character caller should not create RuntimeCommandPort")

    def fail_create_buff_runtime_read_port(*args: object, **kwargs: object) -> None:
        raise AssertionError("Character caller should not create BuffRuntimeReadPort")

    def fail_create_schedule_dispatch_port(*args: object, **kwargs: object) -> None:
        raise AssertionError("Character caller should not create ScheduleDispatchPort")

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


def _build_character_harness() -> SimpleNamespace:
    listener_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def fail_broadcast_event(*args: object, **kwargs: object) -> None:
        listener_calls.append((args, kwargs))
        _fail_listener_broadcast(*args, **kwargs)

    sim_instance = SimpleNamespace(
        tick=1461,
        schedule_data=_ScheduleDataStub(),
        load_data=SimpleNamespace(LOADING_BUFF_DICT=_FailFastLoadingBuffDict()),
        listener_manager=SimpleNamespace(broadcast_event=fail_broadcast_event),
    )
    return SimpleNamespace(listener_calls=listener_calls, sim_instance=sim_instance)


def _patch_character_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> list[tuple[str, dict[str, object]]]:
    _patch_runtime_boundary_guards(monkeypatch)
    monkeypatch.setattr(seed_character_module, "Seed", _SeedStub)
    monkeypatch.setattr(seed_ex_state_module, "SEED_REPORT", False)

    buff_add_calls: list[tuple[str, dict[str, object]]] = []

    def fake_buff_add_strategy(buff_index: str, **kwargs: object) -> None:
        buff_add_calls.append((buff_index, kwargs))

    monkeypatch.setattr(
        "zsim.sim_progress.Buff.BuffAddStrategy.buff_add_strategy",
        fake_buff_add_strategy,
    )
    return buff_add_calls


def _assert_no_cross_layer_writes(harness: SimpleNamespace) -> None:
    assert harness.listener_calls == []
    assert harness.sim_instance.schedule_data.event_list == []
    assert harness.sim_instance.schedule_data.pending == []
    assert harness.sim_instance.schedule_data.process_state_changes == 0
    assert isinstance(
        harness.sim_instance.load_data.LOADING_BUFF_DICT,
        _FailFastLoadingBuffDict,
    )


def test_seed_ex_state_finish_forwards_explicit_target_count_and_sim_instance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _build_character_harness()
    buff_add_calls = _patch_character_dependencies(monkeypatch)
    seed = _SeedStub(cinema=2, sim_instance=harness.sim_instance)
    manager = SeedEXStateManager(seed)
    manager.e_ex_state = SeedEXState.FINISH
    manager.repeat_count = 4
    skill_node = SimpleNamespace(
        is_additional_damage=False,
        skill_tag="1461_SNA_1",
        skill=SimpleNamespace(skill_text="自动衔接重击"),
    )

    manager.update_ex_state(skill_node)

    assert manager.e_ex_state == SeedEXState.IDLE
    assert buff_add_calls == [
        (
            "Buff-角色-席德-影画-2画-耗能转化增伤",
            {
                "benifit_list": ["席德"],
                "specified_count": 4,
                "sim_instance": harness.sim_instance,
            },
        )
    ]
    _assert_no_cross_layer_writes(harness)


def test_seed_ex_state_idle_sna_keeps_forced_write_noop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _build_character_harness()
    buff_add_calls = _patch_character_dependencies(monkeypatch)
    seed = _SeedStub(cinema=2, sim_instance=harness.sim_instance)
    manager = SeedEXStateManager(seed)
    skill_node = SimpleNamespace(
        is_additional_damage=False,
        skill_tag="1461_SNA_1",
        skill=SimpleNamespace(skill_text="普通重击"),
    )

    manager.update_ex_state(skill_node)

    assert manager.e_ex_state == SeedEXState.IDLE
    assert buff_add_calls == []
    _assert_no_cross_layer_writes(harness)


def test_yanagi_stance_update_forwards_sim_instance_and_toggles_stance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _build_character_harness()
    buff_add_calls = _patch_character_dependencies(monkeypatch)
    yanagi = SimpleNamespace(cinema=0, sim_instance=harness.sim_instance)
    manager = StanceManager(yanagi)
    skill_node = SimpleNamespace(skill_tag="1221_E")

    manager.update_myself(skill_node)

    assert manager.stance_now is False
    assert manager.last_update_node is skill_node
    assert buff_add_calls == [
        (
            "Buff-角色-柳-额外能力-积蓄效率",
            {"sim_instance": harness.sim_instance},
        )
    ]
    _assert_no_cross_layer_writes(harness)


def test_yanagi_stance_update_ignores_unrelated_skill_without_forced_write(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _build_character_harness()
    buff_add_calls = _patch_character_dependencies(monkeypatch)
    yanagi = SimpleNamespace(cinema=0, sim_instance=harness.sim_instance)
    manager = StanceManager(yanagi)

    manager.update_myself(SimpleNamespace(skill_tag="0000_E"))

    assert manager.stance_now is True
    assert manager.last_update_node is None
    assert buff_add_calls == []
    _assert_no_cross_layer_writes(harness)
