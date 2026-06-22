from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest

import zsim.sim_progress.ScheduledEvent as scheduled_event_module
import zsim.sim_progress.Buff.BuffLoad as buff_load_module
import zsim.main as zsim_main
from zsim.sim_progress import Load as load_module
from zsim.sim_progress.Buff.BuffLoad import BuffLoadLoop
from zsim.sim_progress.ScheduledEvent.buff_runtime import (
    ActiveBuffStore,
    BuffRuntimeState,
    PendingBuffQueue,
)
from zsim.simulator import simulator_class
from zsim.simulator.simulator_class import Simulator


class _RuntimeProbe:
    def __init__(self, order: list[str]) -> None:
        self._order = order
        self._pending_owner_getter: Any = None
        self._runtime_state: BuffRuntimeState | None = None
        self.calls: list[tuple[int, Any]] = []
        self.load_ticks: list[int] = []
        self.activation_ticks: list[float] = []
        self.pending_load_owners: list[PendingBuffQueue] = []
        self.pending_activation_owners: list[PendingBuffQueue] = []
        self.active_activation_owners: list[ActiveBuffStore] = []
        self.drained_pending_markers: list[Any] = []
        self.activated_active_markers: list[tuple[str, Any]] = []

    def bind_pending_owner_getter(self, getter: Any) -> None:
        self._pending_owner_getter = getter

    def update_time_related_effects(self, *, tick: int, enemy: Any) -> None:
        self.calls.append((tick, enemy))
        self._order.append(f"tick_sweep:{tick}")

    def load_pending_buffs(
        self,
        *,
        time_now: int,
        load_mission_dict: dict[str, Any],
        character_name_box: list[str],
        all_name_order_box: dict[str, Any],
        sim_instance: Any,
    ) -> dict[str, list[Any]]:
        self.load_ticks.append(time_now)
        self._order.append(f"load_pending:{time_now}")
        record_rebuild_count = getattr(sim_instance, "_record_buff_runtime_rebuild_count", None)
        if record_rebuild_count is not None:
            record_rebuild_count("buff_load_loop")
        self._runtime_state = sim_instance.buff_runtime_state
        pending_queue = sim_instance.buff_runtime_state.pending_queue_owner()
        self.pending_load_owners.append(pending_queue)
        if self._pending_owner_getter is None:
            self.bind_pending_owner_getter(sim_instance.buff_runtime_state.pending_queue_owner)
        for character in [*character_name_box, "enemy"]:
            pending_queue.clear(character)
        pending_queue.enqueue(character_name_box[0] if character_name_box else "enemy", time_now)
        return pending_queue.as_compat_dict()

    def activate_pending_buffs(self, *, timenow: float) -> dict[str, list[Any]]:
        self.activation_ticks.append(timenow)
        self._order.append(f"activate_pending:{timenow}")
        if self._pending_owner_getter is not None:
            pending_queue = self._pending_owner_getter()
            self.pending_activation_owners.append(pending_queue)
            assert self._runtime_state is not None
            active_owner = self._runtime_state.active_store_owner()
            self.active_activation_owners.append(active_owner)
            for beneficiary in pending_queue.beneficiaries():
                for marker in pending_queue.drain(beneficiary):
                    self.drained_pending_markers.append(marker)
                    active_owner.append(beneficiary, marker)
                    self.activated_active_markers.append((beneficiary, marker))
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
        pending_buff_queue=loading_buff_dict,
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
    sim.buff_runtime_state = BuffRuntimeState(
        template_registry=exist_buff_dict,
        pending_queue=loading_buff_dict,
        active_store=dynamic_buff_dict,
        enemy_mirror=enemy.dynamic.dynamic_debuff_list,
    )
    return sim, exist_buff_dict, loading_buff_dict, dynamic_buff_dict, enemy


def _patch_main_loop_leaf_calls(
    monkeypatch: pytest.MonkeyPatch,
    order: list[str],
    scheduled_active_views: list[dict[str, list[Any]]] | None = None,
) -> None:
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
            if scheduled_active_views is not None:
                dynamic_buff = args[0]
                scheduled_active_views.append(
                    {
                        beneficiary: list(active_buffs)
                        for beneficiary, active_buffs in dynamic_buff.items()
                    }
                )
            order.append("scheduled_init")

        def event_start(self) -> None:
            order.append("scheduled_start")

    monkeypatch.setattr(simulator_class, "ScE", FakeScheduledEvent)


def _buff_load_loop_scan_metrics(sim: Any) -> dict[str, int] | None:
    metrics = getattr(sim, "_buff_load_loop_scan_metrics", None)
    if metrics is None:
        return None
    return dict(metrics)


def test_main_loop_routes_tick_sweep_and_activation_through_buff_runtime_facade(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    order: list[str] = []
    scheduled_active_views: list[dict[str, list[Any]]] = []
    runtime = _RuntimeProbe(order)

    def fake_create_facade() -> _RuntimeProbe:
        order.append("create_facade")
        return runtime

    _patch_main_loop_leaf_calls(
        monkeypatch,
        order,
        scheduled_active_views=scheduled_active_views,
    )
    sim, exist_buff_dict, loading_buff_dict, dynamic_buff_dict, enemy = _make_minimal_sim(order)
    monkeypatch.setattr(sim.buff_runtime_state, "create_facade", fake_create_facade)

    sim.main_loop(stop_tick=1, use_api=True)

    assert sim.buff_runtime_state.template_registry_for_compat() is exist_buff_dict
    assert sim.buff_runtime_state.pending_queue_for_compat() is loading_buff_dict
    assert isinstance(sim.buff_runtime_state.active_store_owner(), ActiveBuffStore)
    assert sim.buff_runtime_state.active_store_owner().as_compat_dict() is dynamic_buff_dict
    assert sim.buff_runtime_state.active_store_for_compat() is dynamic_buff_dict
    assert dynamic_buff_dict["enemy"] is enemy.dynamic.dynamic_debuff_list
    assert sim.buff_runtime_state.enemy_mirror_for_compat() is enemy.dynamic.dynamic_debuff_list
    assert runtime.calls == [(0, enemy), (1, enemy)]
    assert runtime.load_ticks == [0]
    assert runtime.activation_ticks == [0]
    assert runtime.pending_load_owners == [sim.buff_runtime_state.pending_queue_owner()]
    assert runtime.pending_activation_owners == [sim.buff_runtime_state.pending_queue_owner()]
    assert runtime.pending_load_owners[0] is runtime.pending_activation_owners[0]
    assert runtime.active_activation_owners == [sim.buff_runtime_state.active_store_owner()]
    assert runtime.drained_pending_markers == [0]
    assert runtime.activated_active_markers == [("alpha", 0)]
    assert scheduled_active_views == [{"alpha": [0], "enemy": []}]
    assert order == [
        "create_facade",
        "tick_sweep:0",
        "preload:0",
        "damage_judge",
        "load_pending:0",
        "activate_pending:0",
        "scheduled_init",
        "scheduled_start",
        "reset_processed_event",
        "tick_sweep:1",
        "preload:1",
        "stop_report_threads",
    ]


def test_main_loop_opt_in_preserves_runtime_api_order_and_pending_queue_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    order: list[str] = []
    runtime = _RuntimeProbe(order)

    def fake_create_facade() -> _RuntimeProbe:
        order.append("create_facade")
        return runtime

    _patch_main_loop_leaf_calls(monkeypatch, order)
    sim, _, loading_buff_dict, _, enemy = _make_minimal_sim(order)
    monkeypatch.setattr(sim.buff_runtime_state, "create_facade", fake_create_facade)

    sim.main_loop(stop_tick=1, use_api=True, use_indexed_buff_load_loop=True)

    assert sim.use_indexed_buff_load_loop is True
    assert sim.buff_runtime_state.pending_queue_owner().as_compat_dict() is loading_buff_dict
    assert sim.buff_runtime_state.pending_queue_for_compat() is loading_buff_dict
    assert runtime.calls == [(0, enemy), (1, enemy)]
    assert runtime.load_ticks == [0]
    assert runtime.activation_ticks == [0]
    assert runtime.pending_load_owners == [sim.buff_runtime_state.pending_queue_owner()]
    assert runtime.pending_activation_owners == [sim.buff_runtime_state.pending_queue_owner()]
    assert runtime.pending_load_owners[0] is runtime.pending_activation_owners[0]
    assert runtime.drained_pending_markers == [0]
    assert order == [
        "create_facade",
        "tick_sweep:0",
        "preload:0",
        "damage_judge",
        "load_pending:0",
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
    factory_calls: list[BuffRuntimeState] = []
    runtimes: list[_RuntimeProbe] = []

    def fake_create_facade() -> _RuntimeProbe:
        runtime = _RuntimeProbe(order)
        factory_calls.append(sim.buff_runtime_state)
        runtimes.append(runtime)
        order.append(f"create_facade:{len(factory_calls)}")
        return runtime

    _patch_main_loop_leaf_calls(monkeypatch, order)
    sim, _, _, _, enemy = _make_minimal_sim(order)
    monkeypatch.setattr(sim.buff_runtime_state, "create_facade", fake_create_facade)

    sim.main_loop(stop_tick=2, use_api=True)
    sim.main_loop(stop_tick=4, use_api=True)

    assert len(factory_calls) == 2
    assert runtimes[0].calls == [(0, enemy), (1, enemy), (2, enemy)]
    assert runtimes[0].load_ticks == [0, 1]
    assert runtimes[0].activation_ticks == [0, 1]
    assert runtimes[1].calls == [(2, enemy), (3, enemy), (4, enemy)]
    assert runtimes[1].load_ticks == [2, 3]
    assert runtimes[1].activation_ticks == [2, 3]


def test_rebuild_counting_is_inert_until_opted_in() -> None:
    sim = cast(Any, Simulator())

    sim._record_buff_runtime_rebuild_count("legacy_buff_runtime_facade")

    assert sim.get_buff_runtime_rebuild_counts() is None


def test_indexed_buff_load_loop_option_defaults_off_and_api_is_explicit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, bool, bool | None]] = []

    def fake_api_init_simulator(self: Simulator, common_cfg: Any, sim_cfg: Any) -> None:
        calls.append(("init", self.use_indexed_buff_load_loop, None))

    def fake_main_loop(self: Simulator, *args: Any, **kwargs: Any) -> None:
        calls.append(
            (
                "main_loop",
                self.use_indexed_buff_load_loop,
                kwargs.get("use_indexed_buff_load_loop"),
            )
        )

    monkeypatch.setattr(Simulator, "api_init_simulator", fake_api_init_simulator)
    monkeypatch.setattr(Simulator, "main_loop", fake_main_loop)

    default_sim = Simulator()
    ctor_opt_in_sim = Simulator(use_indexed_buff_load_loop=True)
    api_opt_in_sim = Simulator()
    api_explicit_false_sim = Simulator(use_indexed_buff_load_loop=True)
    common_cfg = SimpleNamespace(session_id="api-session")

    default_sim.api_run_simulator(common_cfg, sim_cfg=None, stop_tick=1)
    api_opt_in_sim.api_run_simulator(
        common_cfg,
        sim_cfg=None,
        stop_tick=1,
        use_indexed_buff_load_loop=True,
    )
    api_explicit_false_sim.api_run_simulator(
        common_cfg,
        sim_cfg=None,
        stop_tick=1,
        use_indexed_buff_load_loop=False,
    )

    assert default_sim.use_indexed_buff_load_loop is False
    assert ctor_opt_in_sim.use_indexed_buff_load_loop is True
    assert api_opt_in_sim.use_indexed_buff_load_loop is True
    assert api_explicit_false_sim.use_indexed_buff_load_loop is False
    assert calls == [
        ("init", False, None),
        ("main_loop", False, None),
        ("init", True, None),
        ("main_loop", True, None),
        ("init", False, None),
        ("main_loop", False, None),
    ]


def test_main_cli_parser_keeps_indexed_buff_load_loop_default_off() -> None:
    parser = zsim_main.build_parser()

    default_args = parser.parse_args([])
    opt_in_args = parser.parse_args(["--use-indexed-buff-load-loop"])

    assert not hasattr(default_args, "use_indexed_buff_load_loop")
    assert zsim_main.resolve_use_indexed_buff_load_loop(default_args) is False
    assert zsim_main.resolve_use_indexed_buff_load_loop(opt_in_args) is True


def test_buff_load_loop_records_count_only_when_opted_in() -> None:
    sim = cast(Any, Simulator())
    loading_buff_dict: dict[str, list[Any]] = {}

    BuffLoadLoop(
        time_now=0,
        load_mission_dict={},
        existbuff_dict={},
        character_name_box=[],
        pending_buff_queue=loading_buff_dict,
        all_name_order_box={},
        sim_instance=sim,
    )

    assert sim.get_buff_runtime_rebuild_counts() is None
    assert _buff_load_loop_scan_metrics(sim) is None
    assert loading_buff_dict == {"enemy": []}

    sim.enable_buff_runtime_rebuild_counting()
    BuffLoadLoop(
        time_now=1,
        load_mission_dict={},
        existbuff_dict={},
        character_name_box=[],
        pending_buff_queue=loading_buff_dict,
        all_name_order_box={},
        sim_instance=sim,
    )

    assert sim.get_buff_runtime_rebuild_counts() == {"buff_load_loop": 1}
    assert _buff_load_loop_scan_metrics(sim) == {
        "processed_tick_count": 1,
        "mission_count": 0,
        "character_count": 0,
        "registered_buff_count": 0,
        "trigger_candidate_count": 0,
        "on_field_candidate_count": 0,
        "backend_candidate_count": 0,
        "pending_queue_count": 0,
        "candidate_plan_count": 0,
        "candidate_plan_on_field_candidate_count": 0,
        "candidate_plan_backend_candidate_count": 0,
        "candidate_plan_mission_count": 0,
        "candidate_plan_character_count": 0,
        "candidate_plan_mismatch_count": 0,
    }


def test_buff_load_loop_records_opt_in_scan_metric_shape(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeLoadingMission:
        def __init__(self, mission_character: str) -> None:
            self.mission_character = mission_character

    def fake_process_on_field_buff(
        sub_exist_buff_dict: dict[str, Any],
        mission: Any,
        time_now: int,
        pending_buff_queue: dict[str, list[Any]],
        all_name_order_box: dict[str, Any],
        exist_buff_dict: dict[str, dict[str, Any]],
        sim_instance: Any,
    ) -> None:
        pending_buff_queue["alpha"].append("alpha-pending")

    def fake_process_backend_buff(
        sub_exist_buff_dict: dict[str, Any],
        all_name_order_box: dict[str, Any],
        mission: Any,
        time_now: int,
        pending_buff_queue: dict[str, list[Any]],
        exist_buff_dict: dict[str, dict[str, Any]],
        sim_instance: Any,
    ) -> None:
        pending_buff_queue["bravo"].append("bravo-pending")

    summary_calls: list[tuple[tuple[str, ...], tuple[str, ...]]] = []
    original_summary = buff_load_module._summarize_buff_load_loop_candidate_plan

    def fail_describe_candidate_plan(*args: Any, **kwargs: Any) -> dict[str, object]:
        raise AssertionError("metrics execution must not materialize detailed plan")

    def spy_summarize_candidate_plan(
        load_mission_dict_arg: dict[str, Any],
        buff_registry_by_character_arg: dict[str, dict[str, Any]],
        character_name_box_arg: list[str],
    ) -> dict[str, object]:
        summary_calls.append(
            (tuple(load_mission_dict_arg), tuple(character_name_box_arg))
        )
        summary = original_summary(
            load_mission_dict_arg,
            buff_registry_by_character_arg,
            character_name_box_arg,
        )
        assert "steps" not in summary
        assert "buff_keys" not in summary
        return summary

    monkeypatch.setattr(load_module, "LoadingMission", FakeLoadingMission)
    monkeypatch.setattr(
        buff_load_module,
        "_describe_buff_load_loop_candidate_plan",
        fail_describe_candidate_plan,
    )
    monkeypatch.setattr(
        buff_load_module,
        "_summarize_buff_load_loop_candidate_plan",
        spy_summarize_candidate_plan,
    )
    monkeypatch.setattr(
        buff_load_module,
        "process_on_field_buff",
        fake_process_on_field_buff,
    )
    monkeypatch.setattr(
        buff_load_module,
        "process_backend_buff",
        fake_process_backend_buff,
    )
    sim = cast(Any, Simulator())
    sim.enable_buff_runtime_rebuild_counting()
    loading_buff_dict: dict[str, list[Any]] = {}

    result = BuffLoadLoop(
        time_now=5,
        load_mission_dict={"m1": FakeLoadingMission("alpha")},
        existbuff_dict={
            "alpha": {"alpha-a": object(), "alpha-b": object()},
            "bravo": {"bravo-a": object()},
            "enemy": {"enemy-a": object()},
        },
        character_name_box=["alpha", "bravo"],
        pending_buff_queue=loading_buff_dict,
        all_name_order_box={
            "alpha": ["alpha", "bravo", "enemy"],
            "bravo": ["bravo", "alpha", "enemy"],
        },
        sim_instance=sim,
    )

    assert result is loading_buff_dict
    assert summary_calls == [(("m1",), ("alpha", "bravo"))]
    assert loading_buff_dict == {
        "alpha": ["alpha-pending"],
        "bravo": ["bravo-pending"],
        "enemy": [],
    }
    assert _buff_load_loop_scan_metrics(sim) == {
        "processed_tick_count": 1,
        "mission_count": 1,
        "character_count": 2,
        "registered_buff_count": 3,
        "trigger_candidate_count": 3,
        "on_field_candidate_count": 2,
        "backend_candidate_count": 1,
        "pending_queue_count": 2,
        "candidate_plan_count": 3,
        "candidate_plan_on_field_candidate_count": 2,
        "candidate_plan_backend_candidate_count": 1,
        "candidate_plan_mission_count": 1,
        "candidate_plan_character_count": 2,
        "candidate_plan_mismatch_count": 0,
    }


def test_buff_load_loop_opt_in_metrics_use_summary_without_detailed_plan(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeLoadingMission:
        def __init__(self, name: str, mission_character: str) -> None:
            self.name = name
            self.mission_character = mission_character

    existbuff_dict: dict[str, dict[str, Any]] = {
        "alpha": {"alpha-a": object(), "alpha-b": object()},
        "bravo": {"bravo-a": object()},
        "enemy": {"enemy-a": object()},
    }
    registry_owner_by_id = {id(registry): owner for owner, registry in existbuff_dict.items()}
    load_mission_dict = {
        "first": FakeLoadingMission("first", "alpha"),
        "second": FakeLoadingMission("second", "bravo"),
    }
    character_name_box = ["alpha", "bravo"]
    summary_calls: list[tuple[tuple[str, ...], tuple[str, ...]]] = []
    iterated_candidate_steps: list[tuple[tuple[str, ...], tuple[str, ...]]] = []
    calls: list[tuple[str, str, str, tuple[str, ...]]] = []
    original_summary = buff_load_module._summarize_buff_load_loop_candidate_plan
    original_iter_candidate_steps = buff_load_module._iter_buff_load_loop_candidate_steps

    def fail_describe_candidate_plan(*args: Any, **kwargs: Any) -> dict[str, object]:
        raise AssertionError("metrics execution must not materialize detailed plan")

    def spy_summarize_candidate_plan(
        load_mission_dict_arg: dict[str, Any],
        buff_registry_by_character_arg: dict[str, dict[str, Any]],
        character_name_box_arg: list[str],
    ) -> dict[str, object]:
        summary_calls.append(
            (tuple(load_mission_dict_arg), tuple(character_name_box_arg))
        )
        summary = original_summary(
            load_mission_dict_arg,
            buff_registry_by_character_arg,
            character_name_box_arg,
        )
        assert "steps" not in summary
        assert "buff_keys" not in summary
        return summary

    def spy_iter_candidate_steps(
        load_mission_dict_arg: dict[str, Any],
        buff_registry_by_character_arg: dict[str, dict[str, Any]],
        character_name_box_arg: list[str],
    ) -> Any:
        iterated_candidate_steps.append(
            (tuple(load_mission_dict_arg), tuple(character_name_box_arg))
        )
        yield from original_iter_candidate_steps(
            load_mission_dict_arg,
            buff_registry_by_character_arg,
            character_name_box_arg,
        )

    def fake_process_on_field_buff(
        sub_exist_buff_dict: dict[str, Any],
        mission: Any,
        time_now: int,
        pending_buff_queue: dict[str, list[Any]],
        all_name_order_box: dict[str, Any],
        exist_buff_dict: dict[str, dict[str, Any]],
        sim_instance: Any,
    ) -> None:
        owner = registry_owner_by_id[id(sub_exist_buff_dict)]
        calls.append(("on_field", mission.name, owner, tuple(sub_exist_buff_dict)))
        pending_buff_queue[owner].append(f"on:{mission.name}:{time_now}")

    def fake_process_backend_buff(
        sub_exist_buff_dict: dict[str, Any],
        all_name_order_box: dict[str, Any],
        mission: Any,
        time_now: int,
        pending_buff_queue: dict[str, list[Any]],
        exist_buff_dict: dict[str, dict[str, Any]],
        sim_instance: Any,
    ) -> None:
        owner = registry_owner_by_id[id(sub_exist_buff_dict)]
        calls.append(("backend", mission.name, owner, tuple(sub_exist_buff_dict)))
        pending_buff_queue[owner].append(f"back:{mission.name}:{time_now}")

    monkeypatch.setattr(load_module, "LoadingMission", FakeLoadingMission)
    monkeypatch.setattr(
        buff_load_module,
        "_describe_buff_load_loop_candidate_plan",
        fail_describe_candidate_plan,
    )
    monkeypatch.setattr(
        buff_load_module,
        "_summarize_buff_load_loop_candidate_plan",
        spy_summarize_candidate_plan,
    )
    monkeypatch.setattr(
        buff_load_module,
        "_iter_buff_load_loop_candidate_steps",
        spy_iter_candidate_steps,
    )
    monkeypatch.setattr(
        buff_load_module,
        "process_on_field_buff",
        fake_process_on_field_buff,
    )
    monkeypatch.setattr(
        buff_load_module,
        "process_backend_buff",
        fake_process_backend_buff,
    )
    sim = cast(Any, Simulator(use_indexed_buff_load_loop=True))
    sim.enable_buff_runtime_rebuild_counting()
    loading_buff_dict: dict[str, list[Any]] = {}

    result = BuffLoadLoop(
        time_now=7,
        load_mission_dict=load_mission_dict,
        existbuff_dict=existbuff_dict,
        character_name_box=character_name_box,
        pending_buff_queue=loading_buff_dict,
        all_name_order_box={},
        sim_instance=sim,
    )

    assert result is loading_buff_dict
    assert summary_calls == [(("first", "second"), ("alpha", "bravo"))]
    assert iterated_candidate_steps == [(("first", "second"), ("alpha", "bravo"))]
    assert calls == [
        ("on_field", "first", "alpha", ("alpha-a", "alpha-b")),
        ("backend", "first", "bravo", ("bravo-a",)),
        ("backend", "second", "alpha", ("alpha-a", "alpha-b")),
        ("on_field", "second", "bravo", ("bravo-a",)),
    ]
    assert loading_buff_dict == {
        "alpha": ["on:first:7", "back:second:7"],
        "bravo": ["back:first:7", "on:second:7"],
        "enemy": [],
    }
    assert _buff_load_loop_scan_metrics(sim) == {
        "processed_tick_count": 1,
        "mission_count": 2,
        "character_count": 2,
        "registered_buff_count": 3,
        "trigger_candidate_count": 6,
        "on_field_candidate_count": 3,
        "backend_candidate_count": 3,
        "pending_queue_count": 4,
        "candidate_plan_count": 6,
        "candidate_plan_on_field_candidate_count": 3,
        "candidate_plan_backend_candidate_count": 3,
        "candidate_plan_mission_count": 2,
        "candidate_plan_character_count": 2,
        "candidate_plan_mismatch_count": 0,
    }


def test_buff_load_loop_metrics_preserve_queue_order_and_zero_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeLoadingMission:
        def __init__(self, name: str, mission_character: str) -> None:
            self.name = name
            self.mission_character = mission_character

    load_mission_dict = {
        "first": FakeLoadingMission("first", "alpha"),
        "second": FakeLoadingMission("second", "bravo"),
    }
    character_name_box = ["alpha", "bravo", "charlie"]
    summary_calls: list[tuple[tuple[str, ...], tuple[str, ...]]] = []
    iterated_candidate_steps: list[tuple[tuple[str, ...], tuple[str, ...]]] = []
    original_summary = buff_load_module._summarize_buff_load_loop_candidate_plan
    original_iter_candidate_steps = buff_load_module._iter_buff_load_loop_candidate_steps

    def make_existbuff_dict() -> dict[str, dict[str, Any]]:
        return {
            "alpha": {"alpha-a": object(), "alpha-b": object()},
            "bravo": {"bravo-a": object()},
            "charlie": {
                "charlie-a": object(),
                "charlie-b": object(),
                "charlie-c": object(),
            },
            "enemy": {"enemy-a": object()},
        }

    def fail_describe_candidate_plan(*args: Any, **kwargs: Any) -> dict[str, object]:
        raise AssertionError("metrics execution must not materialize detailed plan")

    def spy_summarize_candidate_plan(
        load_mission_dict_arg: dict[str, Any],
        buff_registry_by_character_arg: dict[str, dict[str, Any]],
        character_name_box_arg: list[str],
    ) -> dict[str, object]:
        summary_calls.append(
            (tuple(load_mission_dict_arg), tuple(character_name_box_arg))
        )
        return original_summary(
            load_mission_dict_arg,
            buff_registry_by_character_arg,
            character_name_box_arg,
        )

    def spy_iter_candidate_steps(
        load_mission_dict_arg: dict[str, Any],
        buff_registry_by_character_arg: dict[str, dict[str, Any]],
        character_name_box_arg: list[str],
    ) -> Any:
        iterated_candidate_steps.append(
            (tuple(load_mission_dict_arg), tuple(character_name_box_arg))
        )
        yield from original_iter_candidate_steps(
            load_mission_dict_arg,
            buff_registry_by_character_arg,
            character_name_box_arg,
        )

    def fake_process_on_field_buff(
        sub_exist_buff_dict: dict[str, Any],
        mission: Any,
        time_now: int,
        pending_buff_queue: dict[str, list[Any]],
        all_name_order_box: dict[str, Any],
        exist_buff_dict: dict[str, dict[str, Any]],
        sim_instance: Any,
    ) -> None:
        owner = sim_instance._registry_owner_by_id[id(sub_exist_buff_dict)]
        sim_instance._observed_buff_load_calls.append(
            ("on_field", mission.name, owner, tuple(sub_exist_buff_dict))
        )
        pending_buff_queue[owner].append(f"on:{mission.name}:{owner}:{time_now}")

    def fake_process_backend_buff(
        sub_exist_buff_dict: dict[str, Any],
        all_name_order_box: dict[str, Any],
        mission: Any,
        time_now: int,
        pending_buff_queue: dict[str, list[Any]],
        exist_buff_dict: dict[str, dict[str, Any]],
        sim_instance: Any,
    ) -> None:
        owner = sim_instance._registry_owner_by_id[id(sub_exist_buff_dict)]
        sim_instance._observed_buff_load_calls.append(
            ("backend", mission.name, owner, tuple(sub_exist_buff_dict))
        )
        pending_buff_queue[owner].append(f"back:{mission.name}:{owner}:{time_now}")

    monkeypatch.setattr(load_module, "LoadingMission", FakeLoadingMission)
    monkeypatch.setattr(
        buff_load_module,
        "_describe_buff_load_loop_candidate_plan",
        fail_describe_candidate_plan,
    )
    monkeypatch.setattr(
        buff_load_module,
        "_summarize_buff_load_loop_candidate_plan",
        spy_summarize_candidate_plan,
    )
    monkeypatch.setattr(
        buff_load_module,
        "_iter_buff_load_loop_candidate_steps",
        spy_iter_candidate_steps,
    )
    monkeypatch.setattr(
        buff_load_module,
        "process_on_field_buff",
        fake_process_on_field_buff,
    )
    monkeypatch.setattr(
        buff_load_module,
        "process_backend_buff",
        fake_process_backend_buff,
    )

    expected_calls = [
        ("on_field", "first", "alpha", ("alpha-a", "alpha-b")),
        ("backend", "first", "bravo", ("bravo-a",)),
        ("backend", "first", "charlie", ("charlie-a", "charlie-b", "charlie-c")),
        ("backend", "second", "alpha", ("alpha-a", "alpha-b")),
        ("on_field", "second", "bravo", ("bravo-a",)),
        ("backend", "second", "charlie", ("charlie-a", "charlie-b", "charlie-c")),
    ]
    expected_metrics = {
        "processed_tick_count": 1,
        "mission_count": 2,
        "character_count": 3,
        "registered_buff_count": 6,
        "trigger_candidate_count": 12,
        "on_field_candidate_count": 3,
        "backend_candidate_count": 9,
        "pending_queue_count": 6,
        "candidate_plan_count": 12,
        "candidate_plan_on_field_candidate_count": 3,
        "candidate_plan_backend_candidate_count": 9,
        "candidate_plan_mission_count": 2,
        "candidate_plan_character_count": 3,
        "candidate_plan_mismatch_count": 0,
    }

    for use_indexed_execution in (False, True):
        existbuff_dict = make_existbuff_dict()
        loading_buff_dict: dict[str, list[Any]] = {}
        sim = cast(
            Any,
            Simulator(use_indexed_buff_load_loop=use_indexed_execution),
        )
        sim.enable_buff_runtime_rebuild_counting()
        sim._registry_owner_by_id = {
            id(registry): owner for owner, registry in existbuff_dict.items()
        }
        sim._observed_buff_load_calls = []

        result = BuffLoadLoop(
            time_now=11,
            load_mission_dict=load_mission_dict,
            existbuff_dict=existbuff_dict,
            character_name_box=character_name_box,
            pending_buff_queue=loading_buff_dict,
            all_name_order_box={},
            sim_instance=sim,
        )

        assert result is loading_buff_dict
        assert list(result) == ["alpha", "bravo", "charlie", "enemy"]
        assert sim._observed_buff_load_calls == expected_calls
        assert _buff_load_loop_scan_metrics(sim) == expected_metrics

    assert summary_calls == [
        (("first", "second"), ("alpha", "bravo", "charlie")),
        (("first", "second"), ("alpha", "bravo", "charlie")),
    ]
    assert iterated_candidate_steps == [
        (("first", "second"), ("alpha", "bravo", "charlie"))
    ]


def test_buff_load_loop_raw_dict_compat_adapter_resets_pending_queue_in_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeLoadingMission:
        pass

    monkeypatch.setattr(load_module, "LoadingMission", FakeLoadingMission)
    loading_buff_dict: dict[str, list[Any]] = {}
    sim = cast(Any, Simulator())

    result = BuffLoadLoop(
        time_now=0,
        load_mission_dict={},
        existbuff_dict={},
        character_name_box=["alpha", "bravo", "charlie"],
        pending_buff_queue=loading_buff_dict,
        all_name_order_box={},
        sim_instance=sim,
    )

    assert result is loading_buff_dict
    assert list(loading_buff_dict) == ["alpha", "bravo", "charlie", "enemy"]
    assert loading_buff_dict == {
        "alpha": [],
        "bravo": [],
        "charlie": [],
        "enemy": [],
    }


def test_buff_load_loop_owner_backed_steps_enqueue_through_pending_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeLoadingMission:
        def __init__(self, mission_character: str) -> None:
            self.mission_character = mission_character

    class TrackingPendingBuffQueue(PendingBuffQueue):
        def __init__(self, queues: dict[str, list[Any]]) -> None:
            super().__init__(queues)
            self.enqueue_calls: list[tuple[str, Any]] = []

        def enqueue(self, beneficiary: str, buff: Any) -> None:
            self.enqueue_calls.append((beneficiary, buff))
            super().enqueue(beneficiary, buff)

    def fake_process_on_field_buff(
        sub_exist_buff_dict: dict[str, Any],
        mission: Any,
        time_now: int,
        pending_buff_queue: PendingBuffQueue,
        all_name_order_box: dict[str, Any],
        exist_buff_dict: dict[str, dict[str, Any]],
        sim_instance: Any,
    ) -> None:
        buff_load_module._enqueue_pending_buff(
            pending_buff_queue,
            mission.mission_character,
            f"on:{time_now}",
        )

    def fake_process_backend_buff(
        sub_exist_buff_dict: dict[str, Any],
        all_name_order_box: dict[str, Any],
        mission: Any,
        time_now: int,
        pending_buff_queue: PendingBuffQueue,
        exist_buff_dict: dict[str, dict[str, Any]],
        sim_instance: Any,
    ) -> None:
        buff_load_module._enqueue_pending_buff(
            pending_buff_queue,
            "bravo",
            f"back:{time_now}",
        )

    monkeypatch.setattr(load_module, "LoadingMission", FakeLoadingMission)
    monkeypatch.setattr(
        buff_load_module,
        "process_on_field_buff",
        fake_process_on_field_buff,
    )
    monkeypatch.setattr(
        buff_load_module,
        "process_backend_buff",
        fake_process_backend_buff,
    )
    loading_buff_dict: dict[str, list[Any]] = {}
    pending_owner = TrackingPendingBuffQueue(loading_buff_dict)
    sim = cast(Any, Simulator())

    result = BuffLoadLoop(
        time_now=9,
        load_mission_dict={"mission": FakeLoadingMission("alpha")},
        existbuff_dict={"alpha": {"alpha-buff": object()}, "bravo": {"bravo-buff": object()}},
        character_name_box=["alpha", "bravo"],
        pending_buff_queue=pending_owner,
        all_name_order_box={},
        sim_instance=sim,
    )

    assert result is loading_buff_dict
    assert pending_owner.enqueue_calls == [
        ("alpha", "on:9"),
        ("bravo", "back:9"),
    ]
    assert loading_buff_dict == {
        "alpha": ["on:9"],
        "bravo": ["back:9"],
        "enemy": [],
    }


def test_buff_load_loop_uses_pending_owner_reset_and_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeLoadingMission:
        pass

    class TrackingPendingBuffQueue(PendingBuffQueue):
        def __init__(self, queues: dict[str, list[Any]]) -> None:
            super().__init__(queues)
            self.reset_calls: list[tuple[str, ...]] = []
            self.count_calls = 0

        def reset_for_beneficiaries(self, beneficiaries: list[str]) -> None:
            self.reset_calls.append(tuple(beneficiaries))
            super().reset_for_beneficiaries(beneficiaries)

        def count(self) -> int:
            self.count_calls += 1
            return super().count()

    monkeypatch.setattr(load_module, "LoadingMission", FakeLoadingMission)
    stale_buff = object()
    loading_buff_dict: dict[str, list[Any]] = {"stale": [stale_buff]}
    pending_owner = TrackingPendingBuffQueue(loading_buff_dict)
    sim = cast(Any, Simulator())
    sim.enable_buff_runtime_rebuild_counting()

    result = BuffLoadLoop(
        time_now=0,
        load_mission_dict={},
        existbuff_dict={},
        character_name_box=["alpha", "bravo"],
        pending_buff_queue=pending_owner,
        all_name_order_box={},
        sim_instance=sim,
    )

    assert result is loading_buff_dict
    assert pending_owner.reset_calls == [("alpha", "bravo", "enemy")]
    assert pending_owner.count_calls == 1
    assert loading_buff_dict == {
        "stale": [stale_buff],
        "alpha": [],
        "bravo": [],
        "enemy": [],
    }
    scan_metrics = _buff_load_loop_scan_metrics(sim)
    assert scan_metrics is not None
    assert scan_metrics["pending_queue_count"] == 1


def test_buff_load_loop_visits_mission_registries_in_character_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeLoadingMission:
        def __init__(self, name: str, mission_character: str) -> None:
            self.name = name
            self.mission_character = mission_character

    existbuff_dict: dict[str, dict[str, Any]] = {
        "alpha": {
            "alpha-schedule": object(),
            "alpha-passive": object(),
            "alpha-live": object(),
        },
        "bravo": {
            "bravo-backend-inactive": object(),
            "bravo-live": object(),
        },
        "charlie": {
            "charlie-live": object(),
        },
    }
    registry_owner_by_id = {id(registry): owner for owner, registry in existbuff_dict.items()}
    calls: list[tuple[str, str, str, tuple[str, ...]]] = []

    def fake_process_on_field_buff(
        sub_exist_buff_dict: dict[str, Any],
        mission: Any,
        time_now: int,
        pending_buff_queue: dict[str, list[Any]],
        all_name_order_box: dict[str, Any],
        exist_buff_dict: dict[str, dict[str, Any]],
        sim_instance: Any,
    ) -> None:
        calls.append(
            (
                "on_field",
                mission.name,
                registry_owner_by_id[id(sub_exist_buff_dict)],
                tuple(sub_exist_buff_dict),
            )
        )

    def fake_process_backend_buff(
        sub_exist_buff_dict: dict[str, Any],
        all_name_order_box: dict[str, Any],
        mission: Any,
        time_now: int,
        pending_buff_queue: dict[str, list[Any]],
        exist_buff_dict: dict[str, dict[str, Any]],
        sim_instance: Any,
    ) -> None:
        calls.append(
            (
                "backend",
                mission.name,
                registry_owner_by_id[id(sub_exist_buff_dict)],
                tuple(sub_exist_buff_dict),
            )
        )

    monkeypatch.setattr(load_module, "LoadingMission", FakeLoadingMission)
    monkeypatch.setattr(
        buff_load_module,
        "process_on_field_buff",
        fake_process_on_field_buff,
    )
    monkeypatch.setattr(
        buff_load_module,
        "process_backend_buff",
        fake_process_backend_buff,
    )

    result = BuffLoadLoop(
        time_now=10,
        load_mission_dict={
            "first": FakeLoadingMission("first", "bravo"),
            "second": FakeLoadingMission("second", "alpha"),
        },
        existbuff_dict=existbuff_dict,
        character_name_box=["alpha", "bravo", "charlie"],
        pending_buff_queue={},
        all_name_order_box={},
        sim_instance=cast(Any, Simulator()),
    )

    assert result == {"alpha": [], "bravo": [], "charlie": [], "enemy": []}
    assert calls == [
        (
            "backend",
            "first",
            "alpha",
            ("alpha-schedule", "alpha-passive", "alpha-live"),
        ),
        (
            "on_field",
            "first",
            "bravo",
            ("bravo-backend-inactive", "bravo-live"),
        ),
        ("backend", "first", "charlie", ("charlie-live",)),
        (
            "on_field",
            "second",
            "alpha",
            ("alpha-schedule", "alpha-passive", "alpha-live"),
        ),
        (
            "backend",
            "second",
            "bravo",
            ("bravo-backend-inactive", "bravo-live"),
        ),
        ("backend", "second", "charlie", ("charlie-live",)),
    ]


def test_buff_load_loop_candidate_plan_summary_matches_detailed_counts() -> None:
    class FakeLoadingMission:
        def __init__(self, mission_character: str) -> None:
            self.mission_character = mission_character

    existbuff_dict: dict[str, dict[str, Any]] = {
        "alpha": {
            "alpha-schedule": object(),
            "alpha-passive": object(),
            "alpha-live": object(),
        },
        "bravo": {
            "bravo-backend-inactive": object(),
            "bravo-live": object(),
        },
        "charlie": {
            "charlie-live": object(),
        },
    }
    load_mission_dict = {
        "first": FakeLoadingMission("bravo"),
        "second": FakeLoadingMission("alpha"),
    }
    character_name_box = ["alpha", "bravo", "charlie"]

    summary = buff_load_module._summarize_buff_load_loop_candidate_plan(
        load_mission_dict,
        existbuff_dict,
        character_name_box,
    )
    detailed = buff_load_module._describe_buff_load_loop_candidate_plan(
        load_mission_dict,
        existbuff_dict,
        character_name_box,
    )

    for key in (
        "pending_queue_order",
        "mission_order",
        "mission_count",
        "character_count",
        "candidate_count",
        "on_field_candidate_count",
        "backend_candidate_count",
    ):
        assert summary[key] == detailed[key]


def test_buff_load_loop_candidate_plan_summary_reads_each_registry_length_once() -> None:
    class FakeLoadingMission:
        def __init__(self, mission_character: str) -> None:
            self.mission_character = mission_character

    class CountingRegistry(dict[str, Any]):
        def __init__(self, owner: str, values: dict[str, object]) -> None:
            super().__init__(values)
            self.owner = owner

        def __len__(self) -> int:
            length_reads.append(self.owner)
            return super().__len__()

    length_reads: list[str] = []
    existbuff_dict: dict[str, CountingRegistry] = {
        "alpha": CountingRegistry(
            "alpha",
            {
                "alpha-schedule": object(),
                "alpha-passive": object(),
                "alpha-live": object(),
            },
        ),
        "bravo": CountingRegistry(
            "bravo",
            {
                "bravo-backend-inactive": object(),
                "bravo-live": object(),
            },
        ),
        "charlie": CountingRegistry("charlie", {"charlie-live": object()}),
    }
    load_mission_dict = {
        "first": FakeLoadingMission("bravo"),
        "second": FakeLoadingMission("alpha"),
        "third": FakeLoadingMission("alpha"),
    }
    character_name_box = ["alpha", "bravo", "charlie"]

    summary = buff_load_module._summarize_buff_load_loop_candidate_plan(
        load_mission_dict,
        existbuff_dict,
        character_name_box,
    )
    detailed = buff_load_module._describe_buff_load_loop_candidate_plan(
        load_mission_dict,
        {
            character_name: dict(registry)
            for character_name, registry in existbuff_dict.items()
        },
        character_name_box,
    )

    assert length_reads == ["alpha", "bravo", "charlie"]
    for key in (
        "pending_queue_order",
        "mission_order",
        "mission_count",
        "character_count",
        "candidate_count",
        "on_field_candidate_count",
        "backend_candidate_count",
    ):
        assert summary[key] == detailed[key]


def test_buff_load_loop_registry_length_snapshot_matches_detailed_counts() -> None:
    class FakeLoadingMission:
        def __init__(self, mission_character: str) -> None:
            self.mission_character = mission_character

    existbuff_dict: dict[str, dict[str, Any]] = {
        "alpha": {
            "alpha-schedule": object(),
            "alpha-passive": object(),
            "alpha-live": object(),
        },
        "bravo": {
            "bravo-backend-inactive": object(),
            "bravo-live": object(),
        },
        "charlie": {
            "charlie-live": object(),
        },
    }
    load_mission_dict = {
        "first": FakeLoadingMission("bravo"),
        "second": FakeLoadingMission("alpha"),
    }
    character_name_box = ["alpha", "bravo", "charlie"]

    snapshot = buff_load_module._snapshot_buff_load_loop_registry_lengths(
        load_mission_dict,
        existbuff_dict,
        character_name_box,
    )
    detailed = buff_load_module._describe_buff_load_loop_candidate_plan(
        load_mission_dict,
        existbuff_dict,
        character_name_box,
    )
    registry_lengths = dict(
        cast(tuple[tuple[str, int], ...], snapshot["character_registry_lengths"])
    )
    detailed_steps = cast(tuple[dict[str, Any], ...], detailed["steps"])

    assert snapshot == {
        "character_registry_lengths": (("alpha", 3), ("bravo", 2), ("charlie", 1)),
        "registered_candidate_count": 6,
    }
    assert [
        step["candidate_count"]
        for step in detailed_steps
    ] == [
        registry_lengths[cast(str, step["character_name"])]
        for step in detailed_steps
    ]
    assert sum(
        cast(int, step["candidate_count"]) for step in detailed_steps
    ) == detailed["candidate_count"]


def test_buff_load_loop_registry_length_snapshot_excludes_detailed_payload() -> None:
    class FakeLoadingMission:
        def __init__(self, mission_character: str) -> None:
            self.mission_character = mission_character

    alpha_buff = object()
    bravo_buff = object()
    snapshot = buff_load_module._snapshot_buff_load_loop_registry_lengths(
        {"first": FakeLoadingMission("alpha")},
        {
            "alpha": {"alpha-a": alpha_buff},
            "bravo": {"bravo-a": bravo_buff, "bravo-b": object()},
        },
        ["alpha", "bravo"],
    )

    assert set(snapshot) == {
        "character_registry_lengths",
        "registered_candidate_count",
    }
    assert "steps" not in snapshot
    assert "buff_keys" not in snapshot
    assert "processor" not in snapshot
    assert "selected_targets" not in snapshot
    assert snapshot["character_registry_lengths"] == (("alpha", 1), ("bravo", 2))
    for character_name, registry_length in cast(
        tuple[tuple[str, int], ...], snapshot["character_registry_lengths"]
    ):
        assert isinstance(character_name, str)
        assert isinstance(registry_length, int)
    assert alpha_buff not in snapshot.values()
    assert bravo_buff not in snapshot.values()


def test_buff_load_loop_registry_length_snapshot_preserves_missing_registry_failures() -> None:
    class FakeLoadingMission:
        def __init__(self, mission_character: str) -> None:
            self.mission_character = mission_character

    missing_actor_missions = {"first": FakeLoadingMission("bravo")}
    missing_character_missions = {"first": FakeLoadingMission("alpha")}

    with pytest.raises(ValueError, match="当前角色的Buff源并未创建！"):
        buff_load_module._snapshot_buff_load_loop_registry_lengths(
            missing_actor_missions,
            {"alpha": {}},
            ["alpha"],
        )
    with pytest.raises(ValueError, match="当前角色的Buff源并未创建！"):
        buff_load_module._describe_buff_load_loop_candidate_plan(
            missing_actor_missions,
            {"alpha": {}},
            ["alpha"],
        )

    with pytest.raises(KeyError, match="bravo"):
        buff_load_module._snapshot_buff_load_loop_registry_lengths(
            missing_character_missions,
            {"alpha": {}},
            ["alpha", "bravo"],
        )
    with pytest.raises(KeyError, match="bravo"):
        buff_load_module._describe_buff_load_loop_candidate_plan(
            missing_character_missions,
            {"alpha": {}},
            ["alpha", "bravo"],
        )


def test_buff_load_loop_candidate_plan_summary_excludes_detailed_payload() -> None:
    class FakeLoadingMission:
        def __init__(self, mission_character: str) -> None:
            self.mission_character = mission_character

    summary = buff_load_module._summarize_buff_load_loop_candidate_plan(
        {"first": FakeLoadingMission("alpha")},
        {
            "alpha": {"alpha-a": object()},
            "bravo": {"bravo-a": object(), "bravo-b": object()},
            "enemy": {"enemy-a": object()},
        },
        ["alpha", "bravo"],
    )

    assert "steps" not in summary
    assert "buff_keys" not in summary
    assert summary == {
        "pending_queue_order": ("alpha", "bravo", "enemy"),
        "mission_order": ("first",),
        "mission_count": 1,
        "character_count": 2,
        "candidate_count": 3,
        "on_field_candidate_count": 1,
        "backend_candidate_count": 2,
    }


def test_buff_load_loop_candidate_plan_matches_current_scan_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeLoadingMission:
        def __init__(self, name: str, mission_character: str) -> None:
            self.name = name
            self.mission_character = mission_character

    existbuff_dict: dict[str, dict[str, Any]] = {
        "alpha": {
            "alpha-schedule": object(),
            "alpha-passive": object(),
            "alpha-live": object(),
        },
        "bravo": {
            "bravo-backend-inactive": object(),
            "bravo-live": object(),
        },
        "charlie": {
            "charlie-live": object(),
        },
    }
    registry_owner_by_id = {id(registry): owner for owner, registry in existbuff_dict.items()}
    load_mission_dict = {
        "first": FakeLoadingMission("first", "bravo"),
        "second": FakeLoadingMission("second", "alpha"),
    }
    character_name_box = ["alpha", "bravo", "charlie"]
    calls: list[tuple[str, str, str, tuple[str, ...]]] = []

    def fake_process_on_field_buff(
        sub_exist_buff_dict: dict[str, Any],
        mission: Any,
        time_now: int,
        pending_buff_queue: dict[str, list[Any]],
        all_name_order_box: dict[str, Any],
        exist_buff_dict: dict[str, dict[str, Any]],
        sim_instance: Any,
    ) -> None:
        calls.append(
            (
                "on_field",
                mission.name,
                registry_owner_by_id[id(sub_exist_buff_dict)],
                tuple(sub_exist_buff_dict),
            )
        )

    def fake_process_backend_buff(
        sub_exist_buff_dict: dict[str, Any],
        all_name_order_box: dict[str, Any],
        mission: Any,
        time_now: int,
        pending_buff_queue: dict[str, list[Any]],
        exist_buff_dict: dict[str, dict[str, Any]],
        sim_instance: Any,
    ) -> None:
        calls.append(
            (
                "backend",
                mission.name,
                registry_owner_by_id[id(sub_exist_buff_dict)],
                tuple(sub_exist_buff_dict),
            )
        )

    plan = buff_load_module._describe_buff_load_loop_candidate_plan(
        load_mission_dict,
        existbuff_dict,
        character_name_box,
    )
    plan_steps = cast(tuple[dict[str, Any], ...], plan["steps"])
    plan_order = [
        (
            step["processor"],
            step["mission_key"],
            step["character_name"],
            step["buff_keys"],
        )
        for step in plan_steps
    ]

    monkeypatch.setattr(load_module, "LoadingMission", FakeLoadingMission)
    monkeypatch.setattr(
        buff_load_module,
        "process_on_field_buff",
        fake_process_on_field_buff,
    )
    monkeypatch.setattr(
        buff_load_module,
        "process_backend_buff",
        fake_process_backend_buff,
    )

    result = BuffLoadLoop(
        time_now=10,
        load_mission_dict=load_mission_dict,
        existbuff_dict=existbuff_dict,
        character_name_box=character_name_box,
        pending_buff_queue={},
        all_name_order_box={},
        sim_instance=cast(Any, Simulator()),
    )

    expected_order = [
        (
            "backend",
            "first",
            "alpha",
            ("alpha-schedule", "alpha-passive", "alpha-live"),
        ),
        (
            "on_field",
            "first",
            "bravo",
            ("bravo-backend-inactive", "bravo-live"),
        ),
        ("backend", "first", "charlie", ("charlie-live",)),
        (
            "on_field",
            "second",
            "alpha",
            ("alpha-schedule", "alpha-passive", "alpha-live"),
        ),
        (
            "backend",
            "second",
            "bravo",
            ("bravo-backend-inactive", "bravo-live"),
        ),
        ("backend", "second", "charlie", ("charlie-live",)),
    ]

    assert result == {"alpha": [], "bravo": [], "charlie": [], "enemy": []}
    assert calls == expected_order
    assert plan_order == expected_order
    assert plan["pending_queue_order"] == ("alpha", "bravo", "charlie", "enemy")
    assert plan["mission_order"] == ("first", "second")
    assert plan["mission_count"] == 2
    assert plan["character_count"] == 3
    assert plan["candidate_count"] == 12
    assert plan["on_field_candidate_count"] == 5
    assert plan["backend_candidate_count"] == 7


def test_buff_load_loop_opt_in_candidate_iterator_matches_default_without_plan(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeLoadingMission:
        def __init__(self, name: str, mission_character: str) -> None:
            self.name = name
            self.mission_character = mission_character

    existbuff_dict: dict[str, dict[str, Any]] = {
        "alpha": {"alpha-a": object(), "alpha-b": object()},
        "bravo": {"bravo-a": object()},
        "charlie": {"charlie-a": object()},
    }
    registry_owner_by_id = {id(registry): owner for owner, registry in existbuff_dict.items()}
    load_mission_dict = {
        "first": FakeLoadingMission("first", "bravo"),
        "second": FakeLoadingMission("second", "alpha"),
    }
    character_name_box = ["alpha", "bravo", "charlie"]

    def fail_describe(*args: Any, **kwargs: Any) -> dict[str, object]:
        raise AssertionError("non-metrics opt-in execution must not materialize a plan")

    def fake_process_on_field_buff(
        sub_exist_buff_dict: dict[str, Any],
        mission: Any,
        time_now: int,
        pending_buff_queue: dict[str, list[Any]],
        all_name_order_box: dict[str, Any],
        exist_buff_dict: dict[str, dict[str, Any]],
        sim_instance: Any,
    ) -> None:
        owner = registry_owner_by_id[id(sub_exist_buff_dict)]
        sim_instance._observed_buff_load_calls.append(
            ("on_field", mission.name, owner, tuple(sub_exist_buff_dict))
        )
        pending_buff_queue[owner].append(f"on:{mission.name}:{owner}:{time_now}")

    def fake_process_backend_buff(
        sub_exist_buff_dict: dict[str, Any],
        all_name_order_box: dict[str, Any],
        mission: Any,
        time_now: int,
        pending_buff_queue: dict[str, list[Any]],
        exist_buff_dict: dict[str, dict[str, Any]],
        sim_instance: Any,
    ) -> None:
        owner = registry_owner_by_id[id(sub_exist_buff_dict)]
        sim_instance._observed_buff_load_calls.append(
            ("backend", mission.name, owner, tuple(sub_exist_buff_dict))
        )
        pending_buff_queue[owner].append(f"back:{mission.name}:{owner}:{time_now}")

    monkeypatch.setattr(load_module, "LoadingMission", FakeLoadingMission)
    monkeypatch.setattr(
        buff_load_module,
        "_describe_buff_load_loop_candidate_plan",
        fail_describe,
    )
    monkeypatch.setattr(
        buff_load_module,
        "process_on_field_buff",
        fake_process_on_field_buff,
    )
    monkeypatch.setattr(
        buff_load_module,
        "process_backend_buff",
        fake_process_backend_buff,
    )

    default_sim = cast(Any, Simulator())
    default_sim._observed_buff_load_calls = []
    opt_in_sim = cast(Any, Simulator(use_indexed_buff_load_loop=True))
    opt_in_sim._observed_buff_load_calls = []
    default_pending: dict[str, list[Any]] = {}
    opt_in_pending: dict[str, list[Any]] = {}

    default_result = BuffLoadLoop(
        time_now=10,
        load_mission_dict=load_mission_dict,
        existbuff_dict=existbuff_dict,
        character_name_box=character_name_box,
        pending_buff_queue=default_pending,
        all_name_order_box={},
        sim_instance=default_sim,
    )
    opt_in_result = BuffLoadLoop(
        time_now=10,
        load_mission_dict=load_mission_dict,
        existbuff_dict=existbuff_dict,
        character_name_box=character_name_box,
        pending_buff_queue=opt_in_pending,
        all_name_order_box={},
        sim_instance=opt_in_sim,
    )

    assert default_result is default_pending
    assert opt_in_result is opt_in_pending
    assert default_pending == opt_in_pending
    assert default_sim._observed_buff_load_calls == opt_in_sim._observed_buff_load_calls


def test_buff_load_loop_candidate_plan_is_per_call_snapshot_without_pending_queue_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeLoadingMission:
        def __init__(self, mission_character: str) -> None:
            self.mission_character = mission_character

    class RaisingBuff:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise AssertionError("candidate planning must not construct Buff")

    monkeypatch.setattr(buff_load_module, "Buff", RaisingBuff)
    pending_queue = {"alpha": ["stale-pending"]}
    existbuff_dict: dict[str, dict[str, Any]] = {"alpha": {"alpha-old": object()}}

    first_plan = buff_load_module._describe_buff_load_loop_candidate_plan(
        {"first": FakeLoadingMission("alpha")},
        existbuff_dict,
        ["alpha"],
    )
    first_steps = cast(tuple[dict[str, Any], ...], first_plan["steps"])
    existbuff_dict["alpha"]["alpha-new"] = object()
    second_plan = buff_load_module._describe_buff_load_loop_candidate_plan(
        {"second": FakeLoadingMission("alpha")},
        existbuff_dict,
        ["alpha"],
    )
    second_steps = cast(tuple[dict[str, Any], ...], second_plan["steps"])

    assert pending_queue == {"alpha": ["stale-pending"]}
    assert first_steps is not second_steps
    assert first_steps[0]["buff_keys"] == ("alpha-old",)
    assert first_steps[0]["candidate_count"] == 1
    assert second_steps[0]["buff_keys"] == ("alpha-old", "alpha-new")
    assert second_steps[0]["candidate_count"] == 2
    assert first_plan["candidate_count"] == 1
    assert second_plan["candidate_count"] == 2


def test_buff_load_loop_opt_in_candidate_iterator_is_not_cached_between_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeLoadingMission:
        def __init__(self, mission_character: str) -> None:
            self.mission_character = mission_character

    calls: list[tuple[str, ...]] = []

    def fail_describe(*args: Any, **kwargs: Any) -> dict[str, object]:
        raise AssertionError("non-metrics opt-in execution must not materialize a plan")

    def fake_process_on_field_buff(
        sub_exist_buff_dict: dict[str, Any],
        mission: Any,
        time_now: int,
        pending_buff_queue: dict[str, list[Any]],
        all_name_order_box: dict[str, Any],
        exist_buff_dict: dict[str, dict[str, Any]],
        sim_instance: Any,
    ) -> None:
        keys = tuple(sub_exist_buff_dict)
        calls.append(keys)
        pending_buff_queue["alpha"].append(keys)

    def fail_backend_call(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("single-character on-field case should not call backend")

    monkeypatch.setattr(load_module, "LoadingMission", FakeLoadingMission)
    monkeypatch.setattr(
        buff_load_module,
        "_describe_buff_load_loop_candidate_plan",
        fail_describe,
    )
    monkeypatch.setattr(
        buff_load_module,
        "process_on_field_buff",
        fake_process_on_field_buff,
    )
    monkeypatch.setattr(buff_load_module, "process_backend_buff", fail_backend_call)
    sim = cast(Any, Simulator(use_indexed_buff_load_loop=True))
    loading_buff_dict: dict[str, list[Any]] = {"alpha": ["stale-pending"]}
    existbuff_dict: dict[str, dict[str, Any]] = {"alpha": {"alpha-old": object()}}
    load_mission_dict = {"first": FakeLoadingMission("alpha")}

    first_result = BuffLoadLoop(
        time_now=1,
        load_mission_dict=load_mission_dict,
        existbuff_dict=existbuff_dict,
        character_name_box=["alpha"],
        pending_buff_queue=loading_buff_dict,
        all_name_order_box={},
        sim_instance=sim,
    )
    existbuff_dict["alpha"]["alpha-new"] = object()
    loading_buff_dict["alpha"].append("stale-between-calls")
    second_result = BuffLoadLoop(
        time_now=2,
        load_mission_dict=load_mission_dict,
        existbuff_dict=existbuff_dict,
        character_name_box=["alpha"],
        pending_buff_queue=loading_buff_dict,
        all_name_order_box={},
        sim_instance=sim,
    )

    assert first_result is loading_buff_dict
    assert second_result is loading_buff_dict
    assert calls == [("alpha-old",), ("alpha-old", "alpha-new")]
    assert loading_buff_dict == {"alpha": [("alpha-old", "alpha-new")], "enemy": []}


def test_buff_load_processing_helpers_own_candidate_filters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeBuff:
        def __init__(
            self,
            index: str,
            *,
            operator: str,
            schedule_judge: bool,
            passively_updating: bool,
            backend_acitve: bool,
        ) -> None:
            self.ft = SimpleNamespace(
                index=index,
                operator=operator,
                schedule_judge=schedule_judge,
                passively_updating=passively_updating,
                backend_acitve=backend_acitve,
                add_buff_to=1000,
            )

    process_calls: list[tuple[str, str, tuple[str, ...]]] = []

    def fake_process_buff(
        buff_0: Any,
        sub_exist_buff_dict: dict[str, Any],
        mission: Any,
        time_now: int,
        selected_characters: list[str],
        pending_buff_queue: dict[str, list[Any]],
        exist_buff_dict: dict[str, dict[str, Any]],
        sim_instance: Any,
    ) -> None:
        process_calls.append((mission.name, buff_0.ft.index, tuple(selected_characters)))

    monkeypatch.setattr(buff_load_module, "Buff", FakeBuff)
    monkeypatch.setattr(buff_load_module, "process_buff", fake_process_buff)

    mission = SimpleNamespace(name="mission")
    loading_buff_dict: dict[str, list[Any]] = {
        "alpha": [],
        "bravo": [],
        "enemy": [],
    }
    exist_buff_dict: dict[str, dict[str, Any]] = {"alpha": {}, "bravo": {}, "enemy": {}}
    all_name_order_box = {
        "alpha": ["alpha", "bravo", "charlie", "enemy"],
        "bravo": ["bravo", "alpha", "charlie", "enemy"],
    }
    opt_in_sim = cast(Any, Simulator(use_indexed_buff_load_loop=True))

    buff_load_module.process_on_field_buff(
        {
            "on-schedule": FakeBuff(
                "on-schedule",
                operator="alpha",
                schedule_judge=True,
                passively_updating=False,
                backend_acitve=True,
            ),
            "on-passive": FakeBuff(
                "on-passive",
                operator="alpha",
                schedule_judge=False,
                passively_updating=True,
                backend_acitve=True,
            ),
            "on-eligible": FakeBuff(
                "on-eligible",
                operator="alpha",
                schedule_judge=False,
                passively_updating=False,
                backend_acitve=False,
            ),
        },
        mission,
        10,
        loading_buff_dict,
        all_name_order_box,
        exist_buff_dict,
        sim_instance=opt_in_sim,
    )
    buff_load_module.process_backend_buff(
        {
            "back-schedule": FakeBuff(
                "back-schedule",
                operator="bravo",
                schedule_judge=True,
                passively_updating=False,
                backend_acitve=True,
            ),
            "back-passive": FakeBuff(
                "back-passive",
                operator="bravo",
                schedule_judge=False,
                passively_updating=True,
                backend_acitve=True,
            ),
            "back-inactive": FakeBuff(
                "back-inactive",
                operator="bravo",
                schedule_judge=False,
                passively_updating=False,
                backend_acitve=False,
            ),
            "back-eligible": FakeBuff(
                "back-eligible",
                operator="bravo",
                schedule_judge=False,
                passively_updating=False,
                backend_acitve=True,
            ),
        },
        all_name_order_box,
        mission,
        10,
        loading_buff_dict,
        exist_buff_dict,
        sim_instance=opt_in_sim,
    )

    assert opt_in_sim.use_indexed_buff_load_loop is True
    assert process_calls == [
        ("mission", "on-eligible", ("alpha",)),
        ("mission", "back-eligible", ("bravo",)),
    ]


def test_buff_runtime_facade_load_pending_buffs_owns_load_containers() -> None:
    sim = cast(Any, Simulator())
    sim.enable_buff_runtime_rebuild_counting()
    exist_buff_dict: dict[str, dict[str, Any]] = {"alpha": {}}
    loading_buff_dict: dict[str, list[Any]] = {"alpha": [object()]}
    runtime_state = BuffRuntimeState(
        template_registry=exist_buff_dict,
        pending_queue=loading_buff_dict,
        active_store={"alpha": []},
        enemy_mirror=[],
    )

    result = runtime_state.create_facade().load_pending_buffs(
        time_now=0,
        load_mission_dict={},
        character_name_box=["alpha"],
        all_name_order_box={},
        sim_instance=sim,
    )

    assert result is loading_buff_dict
    assert runtime_state.pending_queue_owner().as_compat_dict() is loading_buff_dict
    assert runtime_state.pending_queue_for_compat() is loading_buff_dict
    assert loading_buff_dict == {"alpha": [], "enemy": []}
    assert sim.get_buff_runtime_rebuild_counts() == {"buff_load_loop": 1}
    assert _buff_load_loop_scan_metrics(sim) == {
        "processed_tick_count": 1,
        "mission_count": 0,
        "character_count": 1,
        "registered_buff_count": 0,
        "trigger_candidate_count": 0,
        "on_field_candidate_count": 0,
        "backend_candidate_count": 0,
        "pending_queue_count": 0,
        "candidate_plan_count": 0,
        "candidate_plan_on_field_candidate_count": 0,
        "candidate_plan_backend_candidate_count": 0,
        "candidate_plan_mission_count": 0,
        "candidate_plan_character_count": 1,
        "candidate_plan_mismatch_count": 0,
    }


def test_buff_runtime_facade_load_pending_buffs_passes_pending_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sim = cast(Any, Simulator())
    exist_buff_dict: dict[str, dict[str, Any]] = {"alpha": {}}
    loading_buff_dict: dict[str, list[Any]] = {"alpha": [object()]}
    runtime_state = BuffRuntimeState(
        template_registry=exist_buff_dict,
        pending_queue=loading_buff_dict,
        active_store={"alpha": []},
        enemy_mirror=[],
    )
    captured: dict[str, Any] = {}

    def fake_buff_load_loop(
        time_now: int,
        load_mission_dict: dict[str, Any],
        existbuff_dict: dict[str, dict[str, Any]],
        character_name_box: list[str],
        pending_buff_queue: PendingBuffQueue,
        all_name_order_box: dict[str, Any],
        sim_instance: Any,
    ) -> dict[str, list[Any]]:
        captured["time_now"] = time_now
        captured["existbuff_dict"] = existbuff_dict
        captured["pending_owner"] = pending_buff_queue
        captured["sim_instance"] = sim_instance
        pending_buff_queue.reset_for_beneficiaries([*character_name_box, "enemy"])
        pending_buff_queue.enqueue("alpha", "pending-alpha")
        return cast(dict[str, list[Any]], pending_buff_queue.as_compat_dict())

    monkeypatch.setattr(buff_load_module, "BuffLoadLoop", fake_buff_load_loop)

    result = runtime_state.create_facade().load_pending_buffs(
        time_now=7,
        load_mission_dict={},
        character_name_box=["alpha"],
        all_name_order_box={},
        sim_instance=sim,
    )

    assert captured == {
        "time_now": 7,
        "existbuff_dict": exist_buff_dict,
        "pending_owner": runtime_state.pending_queue_owner(),
        "sim_instance": sim,
    }
    assert result is loading_buff_dict
    assert loading_buff_dict == {"alpha": ["pending-alpha"], "enemy": []}


def test_scheduled_event_records_opt_in_construction_and_runtime_port_counts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dynamic_buff: dict[str, list[Any]] = {"alpha": [], "enemy": []}
    exist_buff_dict: dict[str, dict[str, Any]] = {"alpha": {}, "enemy": {}}
    schedule_data = SimpleNamespace(
        enemy=SimpleNamespace(),
        event_list=[],
        char_obj_list=[],
    )
    action_stack = SimpleNamespace()
    sim = cast(Any, Simulator())
    runtime_state = BuffRuntimeState(
        template_registry=exist_buff_dict,
        pending_queue={},
        active_store=dynamic_buff,
        enemy_mirror=[],
    )
    read_port = object()
    command_port = object()
    captured_runtime_command_kwargs: dict[str, Any] = {}

    monkeypatch.setattr(
        scheduled_event_module.ScheduledEvent,
        "_ensure_handlers_registered",
        lambda self: None,
    )
    monkeypatch.setattr(runtime_state, "create_read_port", lambda: read_port)

    def fake_create_runtime_command_port(**kwargs: Any) -> object:
        captured_runtime_command_kwargs.update(kwargs)
        return command_port

    monkeypatch.setattr(
        scheduled_event_module,
        "create_runtime_command_port",
        fake_create_runtime_command_port,
    )

    scheduled_event_module.ScheduledEvent(
        dynamic_buff,
        schedule_data,
        0,
        exist_buff_dict,
        action_stack,
        buff_runtime_state=runtime_state,
        sim_instance=sim,
    )

    assert sim.get_buff_runtime_rebuild_counts() is None

    sim.enable_buff_runtime_rebuild_counting()
    scheduled_event = scheduled_event_module.ScheduledEvent(
        dynamic_buff,
        schedule_data,
        1,
        exist_buff_dict,
        action_stack,
        buff_runtime_state=runtime_state,
        sim_instance=sim,
    )

    assert sim.get_buff_runtime_rebuild_counts() == {
        "scheduled_event": 1,
        "scheduled_event_runtime_ports": 1,
    }
    assert scheduled_event.buff_runtime_view is read_port
    assert scheduled_event.runtime_command_port is command_port
    assert scheduled_event.buff_runtime_state is runtime_state
    assert captured_runtime_command_kwargs["data"] is schedule_data
    assert captured_runtime_command_kwargs["buff_runtime_state"] is runtime_state
    assert "exist_buff_dict" not in captured_runtime_command_kwargs
    assert captured_runtime_command_kwargs["action_stack"] is action_stack
    assert captured_runtime_command_kwargs["sim_instance"] is sim
    assert captured_runtime_command_kwargs["buff_runtime_view"] is read_port


def test_main_loop_records_opt_in_facade_and_buff_load_counts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    order: list[str] = []
    runtime = _RuntimeProbe(order)

    def fake_create_facade() -> _RuntimeProbe:
        order.append("create_facade")
        return runtime

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
    monkeypatch.setattr(sim.buff_runtime_state, "create_facade", fake_create_facade)
    sim.enable_buff_runtime_rebuild_counting()

    sim.main_loop(stop_tick=2, use_api=True)

    assert sim.get_buff_runtime_rebuild_counts() == {
        "legacy_buff_runtime_facade": 1,
        "buff_load_loop": 2,
    }
    assert runtime.calls == [(0, enemy), (1, enemy), (2, enemy)]
    assert runtime.load_ticks == [0, 1]
    assert runtime.activation_ticks == [0, 1]
    assert runtime.pending_load_owners == [
        sim.buff_runtime_state.pending_queue_owner(),
        sim.buff_runtime_state.pending_queue_owner(),
    ]
    assert runtime.pending_activation_owners == [
        sim.buff_runtime_state.pending_queue_owner(),
        sim.buff_runtime_state.pending_queue_owner(),
    ]
    assert runtime.drained_pending_markers == [0, 1]
    assert loading_buff_dict == {"alpha": [], "enemy": []}
