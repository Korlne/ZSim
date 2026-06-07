from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest

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
