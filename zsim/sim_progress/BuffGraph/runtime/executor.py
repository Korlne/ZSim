from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from zsim.sim_progress.BuffGraph.adapters import (
    BuffGraphAdapter,
    BuffGraphAdapterContext,
)
from zsim.sim_progress.BuffGraph.spec.schema import NodeFamily

from .compiler import CompiledBuffGraph
from .trace import BuffGraphTrace, BuffGraphTraceEvent, BuffGraphTraceKind


@dataclass(frozen=True, slots=True)
class BuffGraphExecutionError:
    code: str
    message: str
    path: str


@dataclass(frozen=True, slots=True)
class BuffGraphExecutionResult:
    outputs: Mapping[str, Any]
    node_outputs: Mapping[str, Mapping[str, Any]]
    trace: BuffGraphTrace
    errors: tuple[BuffGraphExecutionError, ...] = ()

    @property
    def passed(self) -> bool:
        return not self.errors


def execute_compiled_buff_graph(
    graph: CompiledBuffGraph,
    *,
    adapters: Mapping[str, BuffGraphAdapter],
    tick: int,
    prepared_context: Mapping[str, Any] | None = None,
) -> BuffGraphExecutionResult:
    context_payload = {} if prepared_context is None else dict(prepared_context)
    trace = BuffGraphTrace(graph_id=graph.graph_id).append(
        BuffGraphTraceEvent(
            tick=tick,
            sequence=0,
            kind=BuffGraphTraceKind.GRAPH_STARTED,
            graph_id=graph.graph_id,
        )
    )
    sequence = 1
    node_outputs: dict[str, Mapping[str, Any]] = {}
    errors: list[BuffGraphExecutionError] = []

    for node_id in graph.execution_order:
        compiled_node = graph.nodes[node_id]
        node = compiled_node.node
        adapter = adapters.get(node.adapter_id)
        if adapter is None:
            errors.append(
                BuffGraphExecutionError(
                    "missing_adapter",
                    f"No adapter registered for {node.adapter_id!r}",
                    f"nodes.{node.node_id}.adapter_id",
                )
            )
            break

        inputs = _collect_inputs(node.node_id, graph=graph, node_outputs=node_outputs)
        trace = trace.append(
            BuffGraphTraceEvent(
                tick=tick,
                sequence=sequence,
                kind=BuffGraphTraceKind.NODE_EVALUATED,
                graph_id=graph.graph_id,
                node_id=node.node_id,
                block_id=node.block_id,
                adapter_id=node.adapter_id,
                checkpoint="node_ready",
                payload={"inputs": inputs},
            )
        )
        sequence += 1

        adapter_result = adapter.execute(
            BuffGraphAdapterContext(
                graph_id=graph.graph_id,
                node=node,
                inputs=inputs,
                prepared_context=context_payload,
            )
        )
        node_outputs[node.node_id] = dict(adapter_result.outputs)
        trace = trace.append(
            BuffGraphTraceEvent(
                tick=tick,
                sequence=sequence,
                kind=BuffGraphTraceKind.ADAPTER_EXECUTED,
                graph_id=graph.graph_id,
                node_id=node.node_id,
                block_id=node.block_id,
                adapter_id=node.adapter_id,
                checkpoint="adapter_executed",
                payload={
                    "outputs": adapter_result.outputs,
                    "adapter_trace": adapter_result.trace,
                },
            )
        )
        sequence += 1

        if node.family == NodeFamily.EFFECT:
            trace = trace.append(
                BuffGraphTraceEvent(
                    tick=tick,
                    sequence=sequence,
                    kind=BuffGraphTraceKind.EFFECT_REQUESTED,
                    graph_id=graph.graph_id,
                    node_id=node.node_id,
                    block_id=node.block_id,
                    adapter_id=node.adapter_id,
                    checkpoint="effect_requested",
                    payload={"outputs": adapter_result.outputs},
                )
            )
            sequence += 1

    trace = trace.append(
        BuffGraphTraceEvent(
            tick=tick,
            sequence=sequence,
            kind=BuffGraphTraceKind.GRAPH_FINISHED,
            graph_id=graph.graph_id,
            checkpoint="graph_finished",
            payload={"passed": not errors},
        )
    )

    return BuffGraphExecutionResult(
        outputs={} if not node_outputs else dict(node_outputs[graph.execution_order[-1]]),
        node_outputs=node_outputs,
        trace=trace,
        errors=tuple(errors),
    )


def _collect_inputs(
    node_id: str,
    *,
    graph: CompiledBuffGraph,
    node_outputs: Mapping[str, Mapping[str, Any]],
) -> Mapping[str, Any]:
    upstream = {
        edge.source_node_id: node_outputs[edge.source_node_id]
        for edge in graph.edges
        if edge.target_node_id == node_id and edge.source_node_id in node_outputs
    }
    return {"upstream": upstream}
