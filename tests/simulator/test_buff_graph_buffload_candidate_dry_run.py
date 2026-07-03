from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace

from zsim.sim_progress.Buff.BuffLoad import (
    _maybe_dry_run_buff_graph_runtime_candidate,
    _maybe_record_buff_graph_runtime_candidate_gate,
)
from zsim.sim_progress.BuffGraph.adapters import (
    BuffGraphAdapterContext,
    BuffGraphAdapterResult,
)
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.runtime.activation import (
    BuffGraphRuntimeActivationIndex,
)
from zsim.sim_progress.BuffGraph.spec import (
    BuffGraphEdge,
    BuffGraphSpec,
    OwnerKind,
    RuntimeStatus,
)


def test_buffload_graph_runtime_dry_run_defaults_to_noop_when_disabled() -> None:
    spec = _spec(runtime_status=RuntimeStatus.VISUAL_GRAPH_CANDIDATE)
    sim = SimpleNamespace(
        enable_buff_graph_runtime_candidates=True,
        enable_buff_graph_runtime_candidate_dry_run=False,
        buff_graph_runtime_activation_index=BuffGraphRuntimeActivationIndex(
            _by_buff_index={"Buff-Test-Activation": (spec,)},
        ),
        buff_graph_runtime_adapters=_adapters_for(spec),
    )
    decision = _select_decision(sim)

    result = _maybe_dry_run_buff_graph_runtime_candidate(
        buff_0=_buff(),
        mission=_mission(),
        time_now=42,
        sim_instance=sim,
        decision=decision,
    )

    assert result is None
    assert not hasattr(sim, "_buff_graph_runtime_candidate_dry_run_results")


def test_buffload_graph_runtime_dry_run_requires_injected_adapters() -> None:
    spec = _spec(runtime_status=RuntimeStatus.VISUAL_GRAPH_CANDIDATE)
    sim = SimpleNamespace(
        enable_buff_graph_runtime_candidates=True,
        enable_buff_graph_runtime_candidate_dry_run=True,
        buff_graph_runtime_activation_index=BuffGraphRuntimeActivationIndex(
            _by_buff_index={"Buff-Test-Activation": (spec,)},
        ),
    )
    decision = _select_decision(sim)

    result = _maybe_dry_run_buff_graph_runtime_candidate(
        buff_0=_buff(),
        mission=_mission(),
        time_now=42,
        sim_instance=sim,
        decision=decision,
    )

    assert result is not None
    assert result["dry_run_executed"] is False
    assert result["passed"] is False
    assert result["reason"] == "skipped_missing_adapter_mapping"
    assert result["legacy_python_active_path"] is True
    assert sim._buff_graph_runtime_candidate_dry_run_results == [result]


def test_buffload_graph_runtime_dry_run_executes_selected_candidate_trace() -> None:
    spec = _spec(runtime_status=RuntimeStatus.VISUAL_GRAPH_CANDIDATE)
    adapters = _adapters_for(spec)
    sim = SimpleNamespace(
        enable_buff_graph_runtime_candidates=True,
        enable_buff_graph_runtime_candidate_dry_run=True,
        buff_graph_runtime_activation_index=BuffGraphRuntimeActivationIndex(
            _by_buff_index={"Buff-Test-Activation": (spec,)},
        ),
        buff_graph_runtime_adapters=adapters,
    )
    decision = _select_decision(sim)

    result = _maybe_dry_run_buff_graph_runtime_candidate(
        buff_0=_buff(),
        mission=_mission(),
        time_now=42,
        sim_instance=sim,
        decision=decision,
    )

    assert result is not None
    assert result["dry_run_executed"] is True
    assert result["passed"] is True
    assert result["reason"] == "executed"
    assert result["runtime_action"] == "graph_runtime_dry_run_legacy_python_still_active"
    assert result["legacy_python_active_path"] is True
    assert result["graph_id"] == "test-activation"
    assert [event["kind"] for event in result["trace_events"]] == [
        "graph_started",
        "node_evaluated",
        "adapter_executed",
        "node_evaluated",
        "adapter_executed",
        "effect_requested",
        "graph_finished",
    ]
    assert set(result["node_outputs"]) == {"trigger", "effect"}
    assert all(adapter.calls for adapter in adapters.values())


def test_buffload_graph_runtime_dry_run_does_not_call_protected_ports() -> None:
    spec = _spec(runtime_status=RuntimeStatus.VISUAL_GRAPH_CANDIDATE)
    sim = _ProtectedPortSentinel(
        enable_buff_graph_runtime_candidates=True,
        enable_buff_graph_runtime_candidate_dry_run=True,
        buff_graph_runtime_activation_index=BuffGraphRuntimeActivationIndex(
            _by_buff_index={"Buff-Test-Activation": (spec,)},
        ),
        buff_graph_runtime_adapters=_adapters_for(spec),
    )
    decision = _select_decision(sim)

    result = _maybe_dry_run_buff_graph_runtime_candidate(
        buff_0=_buff(),
        mission=_mission(),
        time_now=42,
        sim_instance=sim,
        decision=decision,
    )

    assert result is not None
    assert result["passed"] is True


class _RecordingAdapter:
    def __init__(self, adapter_id: str) -> None:
        self.adapter_id = adapter_id
        self.calls: list[BuffGraphAdapterContext] = []

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        self.calls.append(context)
        return BuffGraphAdapterResult(
            outputs={
                "adapter_id": self.adapter_id,
                "node_id": context.node.node_id,
                "prepared_buff_index": context.prepared_context["buff_index"],
                "upstream": context.inputs["upstream"],
            },
            trace={"node_id": context.node.node_id},
        )


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


def _select_decision(sim: SimpleNamespace):
    return _maybe_record_buff_graph_runtime_candidate_gate(
        buff_0=_buff(),
        mission=_mission(),
        time_now=42,
        sim_instance=sim,
    )


def _adapters_for(spec: BuffGraphSpec) -> dict[str, _RecordingAdapter]:
    return {
        node.adapter_id: _RecordingAdapter(node.adapter_id)
        for node in spec.nodes
    }


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
