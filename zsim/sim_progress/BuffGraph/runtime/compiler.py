from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from zsim.sim_progress.BuffGraph.blocks import BuffGraphBlockDefinition, BuffGraphBlockRegistry
from zsim.sim_progress.BuffGraph.spec import (
    BuffGraphEdge,
    BuffGraphNode,
    BuffGraphSpec,
    validate_buff_graph_spec,
)


@dataclass(frozen=True, slots=True)
class BuffGraphCompileError:
    code: str
    message: str
    path: str


@dataclass(frozen=True, slots=True)
class CompiledBuffGraphNode:
    node: BuffGraphNode
    block: BuffGraphBlockDefinition


@dataclass(frozen=True, slots=True)
class CompiledBuffGraph:
    graph_id: str
    nodes: Mapping[str, CompiledBuffGraphNode]
    edges: tuple[BuffGraphEdge, ...]
    execution_order: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BuffGraphCompileResult:
    compiled: CompiledBuffGraph | None
    errors: tuple[BuffGraphCompileError, ...]

    @property
    def passed(self) -> bool:
        return self.compiled is not None and not self.errors


def compile_buff_graph_spec(
    spec: BuffGraphSpec,
    *,
    block_registry: BuffGraphBlockRegistry,
) -> BuffGraphCompileResult:
    errors: list[BuffGraphCompileError] = [
        BuffGraphCompileError(error.code, error.message, error.path)
        for error in validate_buff_graph_spec(spec)
    ]

    compiled_nodes: dict[str, CompiledBuffGraphNode] = {}
    for index, node in enumerate(spec.nodes):
        path = f"nodes[{index}]"
        try:
            block = block_registry.get(node.block_id)
        except KeyError:
            errors.append(
                BuffGraphCompileError(
                    "unknown_block",
                    f"Unknown Buff graph block id: {node.block_id}",
                    f"{path}.block_id",
                )
            )
            continue

        if block.family != node.family:
            errors.append(
                BuffGraphCompileError(
                    "block_family_mismatch",
                    f"Node family {node.family.value!r} does not match block family {block.family.value!r}",
                    f"{path}.family",
                )
            )
        if block.adapter_id != node.adapter_id:
            errors.append(
                BuffGraphCompileError(
                    "adapter_mismatch",
                    f"Node adapter {node.adapter_id!r} does not match block adapter {block.adapter_id!r}",
                    f"{path}.adapter_id",
                )
            )
        compiled_nodes[node.node_id] = CompiledBuffGraphNode(node=node, block=block)

    execution_order, order_errors = _topological_order(
        node_ids=tuple(node.node_id for node in spec.nodes),
        edges=spec.edges,
    )
    errors.extend(order_errors)

    if errors:
        return BuffGraphCompileResult(compiled=None, errors=tuple(errors))

    return BuffGraphCompileResult(
        compiled=CompiledBuffGraph(
            graph_id=spec.graph_id,
            nodes=compiled_nodes,
            edges=spec.edges,
            execution_order=execution_order,
        ),
        errors=(),
    )


def _topological_order(
    *,
    node_ids: tuple[str, ...],
    edges: tuple[BuffGraphEdge, ...],
) -> tuple[tuple[str, ...], tuple[BuffGraphCompileError, ...]]:
    incoming_count = {node_id: 0 for node_id in node_ids}
    outgoing: dict[str, list[str]] = {node_id: [] for node_id in node_ids}
    for edge in edges:
        if edge.source_node_id in outgoing and edge.target_node_id in incoming_count:
            outgoing[edge.source_node_id].append(edge.target_node_id)
            incoming_count[edge.target_node_id] += 1

    ready = [node_id for node_id in node_ids if incoming_count[node_id] == 0]
    order: list[str] = []
    while ready:
        node_id = ready.pop(0)
        order.append(node_id)
        for target_node_id in outgoing[node_id]:
            incoming_count[target_node_id] -= 1
            if incoming_count[target_node_id] == 0:
                ready.append(target_node_id)

    if len(order) != len(node_ids):
        return (), (
            BuffGraphCompileError(
                "cycle_detected",
                "Buff graph edges must form an acyclic execution graph",
                "edges",
            ),
        )

    return tuple(order), ()
