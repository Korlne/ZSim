from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace

from zsim.sim_progress.Buff.BuffLoad import (
    _maybe_record_buff_graph_runtime_candidate_gate,
)
from zsim.sim_progress.BuffGraph.runtime.activation import (
    BuffGraphRuntimeActivationIndex,
)
from zsim.sim_progress.BuffGraph.spec import (
    BuffGraphEdge,
    BuffGraphSpec,
    OwnerKind,
    RuntimeStatus,
)
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry


def test_buffload_graph_candidate_gate_defaults_to_noop_when_disabled() -> None:
    sim = SimpleNamespace(enable_buff_graph_runtime_candidates=False)
    sim.buff_graph_runtime_activation_index = _DisabledIndexSentinel()

    result = _maybe_record_buff_graph_runtime_candidate_gate(
        buff_0=_buff(),
        mission=_mission(),
        time_now=42,
        sim_instance=sim,
    )

    assert result is None
    assert not hasattr(sim, "_buff_graph_runtime_candidate_gate_decisions")


def test_buffload_graph_candidate_gate_records_missing_index_fallback() -> None:
    sim = SimpleNamespace(enable_buff_graph_runtime_candidates=True)

    result = _maybe_record_buff_graph_runtime_candidate_gate(
        buff_0=_buff(),
        mission=_mission(),
        time_now=42,
        sim_instance=sim,
    )

    assert result is not None
    assert result.use_legacy is True
    assert result.reason == "legacy_fallback_missing_activation_index"
    assert sim._buff_graph_runtime_candidate_gate_decisions == [
        {
            "tick": 42,
            "buff_index": "Buff-Test-Activation",
            "mission_tag": "test-mission",
            "xlogic_path": "zsim/sim_progress/Buff/BuffXLogic/TestActivation.py",
            "use_graph": False,
            "use_legacy": True,
            "reason": "legacy_fallback_missing_activation_index",
            "graph_id": None,
            "diagnostics": [],
            "runtime_action": "legacy_python_fallback_until_graph_execution_pack",
        }
    ]


def test_buffload_graph_candidate_gate_records_legacy_fallback_no_candidate() -> None:
    sim = SimpleNamespace(
        enable_buff_graph_runtime_candidates=True,
        buff_graph_runtime_activation_index=BuffGraphRuntimeActivationIndex(),
    )

    result = _maybe_record_buff_graph_runtime_candidate_gate(
        buff_0=_buff(),
        mission=_mission(),
        time_now=42,
        sim_instance=sim,
    )

    assert result is not None
    assert result.use_legacy is True
    assert result.reason == "legacy_fallback_no_graph_candidate"
    assert sim._buff_graph_runtime_candidate_gate_decisions[0]["use_legacy"] is True


def test_buffload_graph_candidate_gate_records_selected_candidate_without_execution() -> None:
    spec = _spec(runtime_status=RuntimeStatus.VISUAL_GRAPH_CANDIDATE)
    sim = SimpleNamespace(
        enable_buff_graph_runtime_candidates=True,
        buff_graph_runtime_activation_index=BuffGraphRuntimeActivationIndex(
            _by_buff_index={"Buff-Test-Activation": (spec,)},
        ),
    )

    result = _maybe_record_buff_graph_runtime_candidate_gate(
        buff_0=_buff(),
        mission=_mission(),
        time_now=42,
        sim_instance=sim,
    )

    assert result is not None
    assert result.use_graph is True
    assert result.spec is spec
    assert sim._buff_graph_runtime_candidate_gate_decisions == [
        {
            "tick": 42,
            "buff_index": "Buff-Test-Activation",
            "mission_tag": "test-mission",
            "xlogic_path": "zsim/sim_progress/Buff/BuffXLogic/TestActivation.py",
            "use_graph": True,
            "use_legacy": False,
            "reason": "visual_graph_candidate_selected",
            "graph_id": "test-activation",
            "diagnostics": [],
            "runtime_action": "legacy_python_fallback_until_graph_execution_pack",
        }
    ]


def test_buffload_graph_candidate_gate_does_not_call_protected_ports() -> None:
    spec = _spec(runtime_status=RuntimeStatus.VISUAL_GRAPH_CANDIDATE)
    sim = _ProtectedPortSentinel(
        enable_buff_graph_runtime_candidates=True,
        buff_graph_runtime_activation_index=BuffGraphRuntimeActivationIndex(
            _by_buff_index={"Buff-Test-Activation": (spec,)},
        ),
    )

    _maybe_record_buff_graph_runtime_candidate_gate(
        buff_0=_buff(),
        mission=_mission(),
        time_now=42,
        sim_instance=sim,
    )

    assert sim._buff_graph_runtime_candidate_gate_decisions[0]["graph_id"] == (
        "test-activation"
    )


class _DisabledIndexSentinel:
    def choose_for_buff(self, **_kwargs: object) -> None:
        raise AssertionError("disabled BuffLoad graph gate should not query candidates")



class _ProtectedPortSentinel(SimpleNamespace):
    def __getattr__(self, name: str):
        if name in {
            "schedule_dispatch_port",
            "runtime_command_port",
            "legacy_runtime_command_adapter",
            "buff_runtime_read_port",
        }:
            raise AssertionError(f"protected port should not be accessed: {name}")
        raise AttributeError(name)


def _buff() -> SimpleNamespace:
    logic = _TestActivationLogic()
    return SimpleNamespace(
        ft=SimpleNamespace(index="Buff-Test-Activation"),
        logic=logic,
    )


def _mission() -> SimpleNamespace:
    return SimpleNamespace(mission_tag="test-mission")


class _TestActivationLogic:
    __module__ = "zsim.sim_progress.Buff.BuffXLogic.TestActivation"


def _spec(
    *,
    runtime_status: RuntimeStatus,
) -> BuffGraphSpec:
    registry = build_default_block_registry()
    trigger = registry.get("trigger.skill_hit").create_node(
        node_id="trigger",
        params={"skill_tag": "basic"},
    )
    effect = registry.get("effect.start_buff").create_node(
        node_id="effect",
        params={"buff_index": "Buff-Test-Activation"},
    )
    draft = BuffGraphSpec.draft_from_xlogic(
        graph_id="test-activation",
        display_name="Test Activation",
        owner_kind=OwnerKind.CHARACTER,
        owner_name="Test",
        source_buff_index="Buff-Test-Activation",
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/TestActivation.py",
        nodes=(trigger, effect),
        edges=(BuffGraphEdge("edge-1", "trigger", "effect"),),
    )
    return replace(draft, runtime_status=runtime_status)
