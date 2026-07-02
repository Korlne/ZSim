from typing import Any, Mapping

from zsim.sim_progress.BuffGraph.adapters import (
    BuffGraphAdapterContext,
    BuffGraphAdapterResult,
)
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.runtime.compiler import compile_buff_graph_spec
from zsim.sim_progress.BuffGraph.runtime.executor import execute_compiled_buff_graph
from zsim.sim_progress.BuffGraph.runtime.trace import validate_buff_graph_trace
from zsim.sim_progress.BuffGraph.spec import BuffGraphEdge, BuffGraphSpec, OwnerKind
from zsim.sim_progress.BuffGraph.spec.schema import BuffGraphNode, NodeFamily


class RecordingAdapter:
    def __init__(self, adapter_id: str, output: Mapping[str, Any]) -> None:
        self.adapter_id = adapter_id
        self.output = output
        self.calls: list[BuffGraphAdapterContext] = []

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        self.calls.append(context)
        return BuffGraphAdapterResult(
            outputs=self.output,
            trace={"node_id": context.node.node_id, "input_keys": tuple(context.inputs.keys())},
        )


def test_compiler_builds_registry_checked_execution_order() -> None:
    registry = build_default_block_registry()
    trigger = registry.get("trigger.skill_hit").create_node(node_id="trigger")
    effect = registry.get("effect.start_buff").create_node(node_id="effect")
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="alice-cinema6",
        display_name="Alice Cinema 6",
        owner_kind=OwnerKind.CHARACTER,
        owner_name="Alice",
        source_buff_index="Buff-角色-爱丽丝-影画6",
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/AliceCinema6Trigger.py",
        nodes=(effect, trigger),
        edges=(BuffGraphEdge(edge_id="edge-1", source_node_id="trigger", target_node_id="effect"),),
    )

    result = compile_buff_graph_spec(spec, block_registry=registry)

    assert result.passed is True
    assert result.compiled is not None
    assert result.compiled.execution_order == ("trigger", "effect")
    assert result.compiled.nodes["trigger"].block.block_id == "trigger.skill_hit"


def test_compiler_reports_unknown_block_adapter_mismatch_and_cycles() -> None:
    registry = build_default_block_registry()
    trigger = registry.get("trigger.skill_hit").create_node(node_id="trigger")
    bad_effect = BuffGraphNode(
        node_id="effect",
        family=NodeFamily.EFFECT,
        block_id="effect.start_buff",
        adapter_id="effect.wrong.v1",
    )
    unknown = BuffGraphNode(
        node_id="unknown",
        family=NodeFamily.CONDITION,
        block_id="condition.not_registered",
        adapter_id="condition.not_registered.v1",
    )
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="bad-graph",
        display_name="Bad Graph",
        owner_kind=OwnerKind.CHARACTER,
        owner_name="Alice",
        source_buff_index=None,
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/AliceCinema6Trigger.py",
        nodes=(trigger, bad_effect, unknown),
        edges=(
            BuffGraphEdge(edge_id="edge-1", source_node_id="trigger", target_node_id="effect"),
            BuffGraphEdge(edge_id="edge-2", source_node_id="effect", target_node_id="trigger"),
        ),
    )

    result = compile_buff_graph_spec(spec, block_registry=registry)

    assert result.compiled is None
    assert [error.code for error in result.errors] == [
        "adapter_mismatch",
        "unknown_block",
        "cycle_detected",
    ]


def test_executor_calls_registered_adapters_and_emits_ordered_trace() -> None:
    registry = build_default_block_registry()
    trigger = registry.get("trigger.skill_hit").create_node(node_id="trigger")
    effect = registry.get("effect.start_buff").create_node(node_id="effect")
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="alice-cinema6",
        display_name="Alice Cinema 6",
        owner_kind=OwnerKind.CHARACTER,
        owner_name="Alice",
        source_buff_index="Buff-角色-爱丽丝-影画6",
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/AliceCinema6Trigger.py",
        nodes=(trigger, effect),
        edges=(BuffGraphEdge(edge_id="edge-1", source_node_id="trigger", target_node_id="effect"),),
    )
    compiled = compile_buff_graph_spec(spec, block_registry=registry).compiled
    assert compiled is not None
    trigger_adapter = RecordingAdapter("trigger.skill_hit.v1", {"matched": True})
    effect_adapter = RecordingAdapter("effect.start_buff.v1", {"buff_started": True})

    result = execute_compiled_buff_graph(
        compiled,
        adapters={
            trigger_adapter.adapter_id: trigger_adapter,
            effect_adapter.adapter_id: effect_adapter,
        },
        tick=240,
        prepared_context={"owner": "Alice"},
    )

    assert result.passed is True
    assert result.outputs == {"buff_started": True}
    assert effect_adapter.calls[0].inputs == {"upstream": {"trigger": {"matched": True}}}
    assert effect_adapter.calls[0].prepared_context == {"owner": "Alice"}
    assert validate_buff_graph_trace(result.trace) == ()
    assert [event.kind.value for event in result.trace.events] == [
        "graph_started",
        "node_evaluated",
        "adapter_executed",
        "node_evaluated",
        "adapter_executed",
        "effect_requested",
        "graph_finished",
    ]


def test_executor_reports_missing_adapter_without_fallback_to_python() -> None:
    registry = build_default_block_registry()
    trigger = registry.get("trigger.skill_hit").create_node(node_id="trigger")
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="missing-adapter",
        display_name="Missing Adapter",
        owner_kind=OwnerKind.CHARACTER,
        owner_name="Alice",
        source_buff_index=None,
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/AliceCinema6Trigger.py",
        nodes=(trigger,),
    )
    compiled = compile_buff_graph_spec(spec, block_registry=registry).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(compiled, adapters={}, tick=1)

    assert result.passed is False
    assert [error.code for error in result.errors] == ["missing_adapter"]
    assert result.outputs == {}
    assert result.trace.events[-1].payload == {"passed": False}
