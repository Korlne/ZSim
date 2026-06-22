from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest

import zsim.sim_progress.ScheduledEvent as scheduled_event_module
import zsim.sim_progress.Buff.BuffLoad as buff_load_module
import zsim.main as zsim_main
from zsim.sim_progress import Load as load_module
from zsim.sim_progress.Buff.BuffLoad import BuffLoadLoop
from zsim.sim_progress.ScheduledEvent.buff_runtime import BuffRuntimeState
from zsim.simulator import simulator_class
from zsim.simulator.simulator_class import Simulator


class _RuntimeProbe:
    def __init__(self, order: list[str]) -> None:
        self._order = order
        self.calls: list[tuple[int, Any]] = []
        self.load_ticks: list[int] = []
        self.activation_ticks: list[float] = []

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
        pending_queue = sim_instance.buff_runtime_state.pending_queue_for_compat()
        for character in [*character_name_box, "enemy"]:
            pending_queue[character] = []
        return pending_queue

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
    sim.buff_runtime_state = BuffRuntimeState(
        template_registry=exist_buff_dict,
        pending_queue=loading_buff_dict,
        active_store=dynamic_buff_dict,
        enemy_mirror=enemy.dynamic.dynamic_debuff_list,
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
        "stop_report_threads",
        lambda: order.append("stop_report_threads"),
    )

    class FakeScheduledEvent:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
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
    runtime = _RuntimeProbe(order)

    def fake_create_facade() -> _RuntimeProbe:
        order.append("create_facade")
        return runtime

    _patch_main_loop_leaf_calls(monkeypatch, order)
    sim, exist_buff_dict, loading_buff_dict, dynamic_buff_dict, enemy = _make_minimal_sim(order)
    monkeypatch.setattr(sim.buff_runtime_state, "create_facade", fake_create_facade)

    sim.main_loop(stop_tick=1, use_api=True)

    assert sim.buff_runtime_state.template_registry_for_compat() is exist_buff_dict
    assert sim.buff_runtime_state.pending_queue_for_compat() is loading_buff_dict
    assert sim.buff_runtime_state.active_store_for_compat() is dynamic_buff_dict
    assert dynamic_buff_dict["enemy"] is enemy.dynamic.dynamic_debuff_list
    assert sim.buff_runtime_state.enemy_mirror_for_compat() is enemy.dynamic.dynamic_debuff_list
    assert runtime.calls == [(0, enemy), (1, enemy)]
    assert runtime.load_ticks == [0]
    assert runtime.activation_ticks == [0]
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
    common_cfg = SimpleNamespace(session_id="api-session")

    default_sim.api_run_simulator(common_cfg, sim_cfg=None, stop_tick=1)
    api_opt_in_sim.api_run_simulator(
        common_cfg,
        sim_cfg=None,
        stop_tick=1,
        use_indexed_buff_load_loop=True,
    )

    assert default_sim.use_indexed_buff_load_loop is False
    assert ctor_opt_in_sim.use_indexed_buff_load_loop is True
    assert api_opt_in_sim.use_indexed_buff_load_loop is True
    assert calls == [
        ("init", False, None),
        ("main_loop", False, None),
        ("init", True, None),
        ("main_loop", True, None),
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
        LOADING_BUFF_DICT=loading_buff_dict,
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
        LOADING_BUFF_DICT=loading_buff_dict,
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
        LOADING_BUFF_DICT: dict[str, list[Any]],
        all_name_order_box: dict[str, Any],
        exist_buff_dict: dict[str, dict[str, Any]],
        sim_instance: Any,
    ) -> None:
        LOADING_BUFF_DICT["alpha"].append("alpha-pending")

    def fake_process_backend_buff(
        sub_exist_buff_dict: dict[str, Any],
        all_name_order_box: dict[str, Any],
        mission: Any,
        time_now: int,
        LOADING_BUFF_DICT: dict[str, list[Any]],
        exist_buff_dict: dict[str, dict[str, Any]],
        sim_instance: Any,
    ) -> None:
        LOADING_BUFF_DICT["bravo"].append("bravo-pending")

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
        LOADING_BUFF_DICT=loading_buff_dict,
        all_name_order_box={
            "alpha": ["alpha", "bravo", "enemy"],
            "bravo": ["bravo", "alpha", "enemy"],
        },
        sim_instance=sim,
    )

    assert result is loading_buff_dict
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


def test_buff_load_loop_resets_pending_queue_in_character_order_and_returns_same_object(
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
        LOADING_BUFF_DICT=loading_buff_dict,
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
        LOADING_BUFF_DICT: dict[str, list[Any]],
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
        LOADING_BUFF_DICT: dict[str, list[Any]],
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
        LOADING_BUFF_DICT={},
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
        LOADING_BUFF_DICT: dict[str, list[Any]],
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
        LOADING_BUFF_DICT: dict[str, list[Any]],
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
        LOADING_BUFF_DICT={},
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
        LOADING_BUFF_DICT: dict[str, list[Any]],
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
        sim_instance=cast(Any, Simulator()),
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
        sim_instance=cast(Any, Simulator()),
    )

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
    assert loading_buff_dict == {"alpha": [], "enemy": []}
