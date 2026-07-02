from __future__ import annotations

from dataclasses import dataclass

from zsim.sim_progress.BuffGraph.blocks import BuffGraphBlockRegistry, build_default_block_registry
from zsim.sim_progress.BuffGraph.spec import BuffGraphEdge, BuffGraphNode, BuffGraphSpec, OwnerKind
from zsim.sim_progress.BuffGraph.spec.schema import validate_buff_graph_spec

from .unsupported_patterns import UnsupportedXLogicPattern
from .xlogic_census import XLogicClassification, classify_xlogic_source


@dataclass(frozen=True, slots=True)
class XLogicGraphImportResult:
    classification: XLogicClassification
    spec: BuffGraphSpec | None
    unsupported_patterns: tuple[UnsupportedXLogicPattern, ...]
    validation_errors: tuple[object, ...]

    @property
    def imported(self) -> bool:
        return self.spec is not None and not self.unsupported_patterns and not self.validation_errors


def import_xlogic_to_graph(
    *,
    xlogic_path: str,
    source: str,
    owner_kind: OwnerKind,
    owner_name: str,
    source_buff_index: str | None,
    graph_id: str | None = None,
    display_name: str | None = None,
    block_registry: BuffGraphBlockRegistry | None = None,
) -> XLogicGraphImportResult:
    registry = build_default_block_registry() if block_registry is None else block_registry
    classification = classify_xlogic_source(xlogic_path=xlogic_path, source=source)
    if classification.unsupported_patterns:
        return XLogicGraphImportResult(
            classification=classification,
            spec=None,
            unsupported_patterns=classification.unsupported_patterns,
            validation_errors=(),
        )

    nodes = _nodes_from_classification(classification=classification, registry=registry)
    edges = _linear_edges(nodes)
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id=graph_id or _graph_id_from_path(xlogic_path),
        display_name=display_name or _display_name_from_path(xlogic_path),
        owner_kind=owner_kind,
        owner_name=owner_name,
        source_buff_index=source_buff_index,
        xlogic_path=xlogic_path,
        nodes=tuple(nodes),
        edges=tuple(edges),
    )
    validation_errors = validate_buff_graph_spec(spec)
    return XLogicGraphImportResult(
        classification=classification,
        spec=spec,
        unsupported_patterns=(),
        validation_errors=validation_errors,
    )


def _nodes_from_classification(
    *,
    classification: XLogicClassification,
    registry: BuffGraphBlockRegistry,
) -> list[BuffGraphNode]:
    block_ids = (
        *classification.triggers,
        *classification.conditions,
        *classification.reads,
        *classification.state,
        *classification.effects,
    )
    nodes: list[BuffGraphNode] = []
    for index, block_id in enumerate(block_ids):
        block = registry.get(block_id)
        params = _default_params(block_id=block_id, xlogic_path=classification.xlogic_path)
        nodes.append(block.create_node(node_id=f"{block.family.value}-{index}", params=params))
    return nodes


def _default_params(*, block_id: str, xlogic_path: str) -> dict[str, object]:
    params: dict[str, object] = {"source_xlogic": xlogic_path}
    if block_id in {"effect.start_buff", "effect.update_buff_count", "condition.buff_active"}:
        params["buff_index"] = _display_name_from_path(xlogic_path)
    if block_id == "trigger.skill_hit":
        params["skill_tag"] = "unknown"
    if block_id == "state.cooldown_gate":
        params["cooldown_ticks"] = 0
    return params


def _linear_edges(nodes: list[BuffGraphNode]) -> list[BuffGraphEdge]:
    return [
        BuffGraphEdge(
            edge_id=f"edge-{index}",
            source_node_id=nodes[index].node_id,
            target_node_id=nodes[index + 1].node_id,
        )
        for index in range(len(nodes) - 1)
    ]


def _graph_id_from_path(path: str) -> str:
    return _display_name_from_path(path).replace("_", "-").replace(" ", "-").lower()


def _display_name_from_path(path: str) -> str:
    return path.rsplit("/", 1)[-1].removesuffix(".py")
