from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest

from zsim.sim_progress.Buff.BuffLoad import BuffLoadLoop
from zsim.simulator import simulator_class
from zsim.simulator.simulator_class import Simulator


class _RuntimeProbe:
    def __init__(self, order: list[str]) -> None:
        self._order = order
        self.calls: list[tuple[int, Any]] = []
        self.activation_ticks: list[float] = []

    def update_time_related_effects(self, *, tick: int, enemy: Any) -> None:
        self.calls.append((tick, enemy))
        self._order.append(f"tick_sweep:{tick}")

    def activate_pending_buffs(self, *, timenow: float) -> dict[str, list[Any]]:
        self.activation_ticks.append(timenow)
        self._order.append(f"activate_pending:{timenow}")
        return {}


def _make_minimal_sim(
    order: list[str],
) -> tuple[
    Any,
    dict[str, dict[str, Any]],
    dict[str, list[Any]],
    dict[str, list[Any]],
    Any,
]:
    sim = cast(Any, Simulator())
    sim.tick = 0
    exist_buff_dict: dict[str, dict[str, Any]] = {"alpha": {}}
    loading_buff_dict: dict[str, list[Any]] = {"alpha": []}
    dynamic_buff_dict: dict[str, list[Any]] = {"alpha": []}
    enemy = SimpleNamespace(dynamic=SimpleNamespace(dynamic_debuff_list=[]))
    sim.load_data = SimpleNamespace(
        exist_buff_dict=exist_buff_dict,
        LOADING_BUFF_DICT=loading_buff_dict,
        load_mission_dict={},
        name_dict={},
        action_stack=object(),
        all_name_order_box={},
    )
    sim.global_stats = SimpleNamespace(DYNAMIC_BUFF_DICT=dynamic_buff_dict)
    sim.schedule_data = SimpleNamespace(
        enemy=enemy,
        event_list=[],
        processed_state_this_tick=False,
        reset_processed_event=lambda: order.append("reset_processed_event"),
    )
    sim.init_data = SimpleNamespace(name_box=["alpha"])
    sim.char_data = SimpleNamespace(char_obj_list=[])
    sim.preload = SimpleNamespace(
        preload_data=SimpleNamespace(preload_action=[]),
        do_preload=lambda *args, **kwargs: order.append(f"preload:{args[0]}"),
    )
    return sim, exist_buff_dict, loading_buff_dict, dynamic_buff_dict, enemy


def _patch_main_loop_leaf_calls(monkeypatch: pytest.MonkeyPatch, order: list[str]) -> None:
    monkeypatch.setattr(
        simulator_class,
        "DamageEventJudge",
        lambda *args, **kwargs: order.append("damage_judge"),
    )
    monkeypatch.setattr(
        simulator_class,
        "BuffLoadLoop",
        lambda *args, **kwargs: order.append("buff_load"),
    )
    monkeypatch.setattr(
        simulator_class,
        "stop_report_threads",
        lambda: order.append("stop_report_threads"),
    )

    class FakeScheduledEvent:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            order.append("scheduled_init")

        def event_start(self) -> None:
            order.append("scheduled_start")

    monkeypatch.setattr(simulator_class, "ScE", FakeScheduledEvent)


def test_main_loop_routes_tick_sweep_and_activation_through_buff_runtime_facade(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    order: list[str] = []
    runtime = _RuntimeProbe(order)
    captured_factory_kwargs: dict[str, Any] = {}

    def fake_create_legacy_buff_runtime_facade(**kwargs: Any) -> _RuntimeProbe:
        captured_factory_kwargs.update(kwargs)
        order.append("create_facade")
        return runtime

    monkeypatch.setattr(
        simulator_class,
        "create_legacy_buff_runtime_facade",
        fake_create_legacy_buff_runtime_facade,
    )
    _patch_main_loop_leaf_calls(monkeypatch, order)
    sim, exist_buff_dict, loading_buff_dict, dynamic_buff_dict, enemy = _make_minimal_sim(
        order
    )

    sim.main_loop(stop_tick=1, use_api=True)

    assert captured_factory_kwargs["exist_buff_dict"] is exist_buff_dict
    assert captured_factory_kwargs["loading_buff_dict"] is loading_buff_dict
    assert captured_factory_kwargs["dynamic_buff_dict"] is dynamic_buff_dict
    assert captured_factory_kwargs["enemy_debuff_mirror"] is enemy.dynamic.dynamic_debuff_list
    assert runtime.calls == [(0, enemy), (1, enemy)]
    assert runtime.activation_ticks == [0]
    assert order == [
        "create_facade",
        "tick_sweep:0",
        "preload:0",
        "damage_judge",
        "buff_load",
        "activate_pending:0",
        "scheduled_init",
        "scheduled_start",
        "reset_processed_event",
        "tick_sweep:1",
        "preload:1",
        "stop_report_threads",
    ]


def test_main_loop_creates_one_buff_runtime_facade_per_run_not_per_tick(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    order: list[str] = []
    factory_calls: list[dict[str, Any]] = []
    runtimes: list[_RuntimeProbe] = []

    def fake_create_legacy_buff_runtime_facade(**kwargs: Any) -> _RuntimeProbe:
        runtime = _RuntimeProbe(order)
        factory_calls.append(kwargs)
        runtimes.append(runtime)
        order.append(f"create_facade:{len(factory_calls)}")
        return runtime

    monkeypatch.setattr(
        simulator_class,
        "create_legacy_buff_runtime_facade",
        fake_create_legacy_buff_runtime_facade,
    )
    _patch_main_loop_leaf_calls(monkeypatch, order)
    sim, _, _, _, enemy = _make_minimal_sim(order)

    sim.main_loop(stop_tick=2, use_api=True)
    sim.main_loop(stop_tick=4, use_api=True)

    assert len(factory_calls) == 2
    assert runtimes[0].calls == [(0, enemy), (1, enemy), (2, enemy)]
    assert runtimes[0].activation_ticks == [0, 1]
    assert runtimes[1].calls == [(2, enemy), (3, enemy), (4, enemy)]
    assert runtimes[1].activation_ticks == [2, 3]


def test_rebuild_counting_is_inert_until_opted_in() -> None:
    sim = cast(Any, Simulator())

    sim._record_buff_runtime_rebuild_count("legacy_buff_runtime_facade")

    assert sim.get_buff_runtime_rebuild_counts() is None


def test_buff_load_loop_records_count_only_when_opted_in() -> None:
    sim = cast(Any, Simulator())
    loading_buff_dict: dict[str, list[Any]] = {}

    BuffLoadLoop(
        time_now=0,
        load_mission_dict={},
        existbuff_dict={},
        character_name_box=[],
        LOADING_BUFF_DICT=loading_buff_dict,
        all_name_order_box={},
        sim_instance=sim,
    )

    assert sim.get_buff_runtime_rebuild_counts() is None
    assert loading_buff_dict == {"enemy": []}

    sim.enable_buff_runtime_rebuild_counting()
    BuffLoadLoop(
        time_now=1,
        load_mission_dict={},
        existbuff_dict={},
        character_name_box=[],
        LOADING_BUFF_DICT=loading_buff_dict,
        all_name_order_box={},
        sim_instance=sim,
    )

    assert sim.get_buff_runtime_rebuild_counts() == {"buff_load_loop": 1}


def test_main_loop_records_opt_in_facade_and_buff_load_counts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    order: list[str] = []
    runtime = _RuntimeProbe(order)

    def fake_create_legacy_buff_runtime_facade(**kwargs: Any) -> _RuntimeProbe:
        order.append("create_facade")
        return runtime

    monkeypatch.setattr(
        simulator_class,
        "create_legacy_buff_runtime_facade",
        fake_create_legacy_buff_runtime_facade,
    )
    monkeypatch.setattr(
        simulator_class,
        "DamageEventJudge",
        lambda *args, **kwargs: order.append("damage_judge"),
    )
    monkeypatch.setattr(
        simulator_class,
        "stop_report_threads",
        lambda: order.append("stop_report_threads"),
    )

    class FakeScheduledEvent:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            order.append("scheduled_init")

        def event_start(self) -> None:
            order.append("scheduled_start")

    monkeypatch.setattr(simulator_class, "ScE", FakeScheduledEvent)
    sim, _, loading_buff_dict, _, enemy = _make_minimal_sim(order)
    sim.enable_buff_runtime_rebuild_counting()

    sim.main_loop(stop_tick=2, use_api=True)

    assert sim.get_buff_runtime_rebuild_counts() == {
        "legacy_buff_runtime_facade": 1,
        "buff_load_loop": 2,
    }
    assert runtime.calls == [(0, enemy), (1, enemy), (2, enemy)]
    assert runtime.activation_ticks == [0, 1]
    assert loading_buff_dict == {"alpha": [], "enemy": []}
