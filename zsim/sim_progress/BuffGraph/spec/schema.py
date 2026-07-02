from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping

from .versions import (
    CURRENT_ADAPTER_CONTRACT_VERSION,
    CURRENT_NODE_LIBRARY_VERSION,
    CURRENT_SCHEMA_VERSION,
)


class OwnerKind(StrEnum):
    CHARACTER = "character"
    W_ENGINE = "w_engine"
    DRIVE_DISC = "drive_disc"
    CINEMA = "cinema"
    CORE_PASSIVE = "core_passive"
    TEAM_EFFECT = "team_effect"
    UNKNOWN = "unknown"


class RuntimeStatus(StrEnum):
    LEGACY_PYTHON = "legacy_python"
    VISUAL_GRAPH_CANDIDATE = "visual_graph_candidate"
    VISUAL_GRAPH_DEFAULT = "visual_graph_default"
    VISUAL_GRAPH_DISABLED = "visual_graph_disabled"


class NodeFamily(StrEnum):
    TRIGGER = "trigger"
    CONDITION = "condition"
    READ = "read"
    EFFECT = "effect"
    STATE = "state"
    COMPOSE = "compose"


FORBIDDEN_NODE_FAMILIES = {"code", "python", "script", "custom_python"}


@dataclass(frozen=True, slots=True)
class BuffGraphNode:
    node_id: str
    family: NodeFamily
    block_id: str
    adapter_id: str
    params: Mapping[str, Any] = field(default_factory=dict)
    display_name: str = ""


@dataclass(frozen=True, slots=True)
class BuffGraphEdge:
    edge_id: str
    source_node_id: str
    target_node_id: str
    source_port: str = "out"
    target_port: str = "in"


@dataclass(frozen=True, slots=True)
class BuffGraphValidationError:
    code: str
    message: str
    path: str


@dataclass(frozen=True, slots=True)
class BuffGraphSpec:
    schema_version: str
    node_library_version: str
    adapter_contract_version: str
    graph_id: str
    display_name: str
    owner_kind: OwnerKind
    owner_name: str
    source_buff_index: str | None
    created_from_xlogic: str | None
    runtime_status: RuntimeStatus
    nodes: tuple[BuffGraphNode, ...]
    edges: tuple[BuffGraphEdge, ...]
    params: Mapping[str, Any] = field(default_factory=dict)
    parity_metadata: Mapping[str, Any] = field(default_factory=dict)
    last_parity_baseline: str | None = None
    last_verified_at: str | None = None

    @classmethod
    def draft_from_xlogic(
        cls,
        *,
        graph_id: str,
        display_name: str,
        owner_kind: OwnerKind,
        owner_name: str,
        source_buff_index: str | None,
        xlogic_path: str,
        nodes: tuple[BuffGraphNode, ...] = (),
        edges: tuple[BuffGraphEdge, ...] = (),
    ) -> "BuffGraphSpec":
        return cls(
            schema_version=CURRENT_SCHEMA_VERSION,
            node_library_version=CURRENT_NODE_LIBRARY_VERSION,
            adapter_contract_version=CURRENT_ADAPTER_CONTRACT_VERSION,
            graph_id=graph_id,
            display_name=display_name,
            owner_kind=owner_kind,
            owner_name=owner_name,
            source_buff_index=source_buff_index,
            created_from_xlogic=xlogic_path,
            runtime_status=RuntimeStatus.LEGACY_PYTHON,
            nodes=nodes,
            edges=edges,
        )


def validate_buff_graph_spec(spec: BuffGraphSpec) -> tuple[BuffGraphValidationError, ...]:
    errors: list[BuffGraphValidationError] = []
    _require_text(spec.graph_id, "graph_id", errors)
    _require_text(spec.display_name, "display_name", errors)
    _require_text(spec.owner_name, "owner_name", errors)

    if spec.runtime_status == RuntimeStatus.VISUAL_GRAPH_DEFAULT and spec.last_verified_at is None:
        errors.append(
            BuffGraphValidationError(
                code="default_requires_verification",
                message="visual_graph_default requires a last_verified_at parity timestamp",
                path="runtime_status",
            )
        )

    node_ids: set[str] = set()
    for index, node in enumerate(spec.nodes):
        path = f"nodes[{index}]"
        if node.node_id in node_ids:
            errors.append(
                BuffGraphValidationError(
                    code="duplicate_node_id",
                    message=f"Duplicate node id: {node.node_id}",
                    path=f"{path}.node_id",
                )
            )
        node_ids.add(node.node_id)
        _validate_node(node, path, errors)

    edge_ids: set[str] = set()
    for index, edge in enumerate(spec.edges):
        path = f"edges[{index}]"
        if edge.edge_id in edge_ids:
            errors.append(
                BuffGraphValidationError(
                    code="duplicate_edge_id",
                    message=f"Duplicate edge id: {edge.edge_id}",
                    path=f"{path}.edge_id",
                )
            )
        edge_ids.add(edge.edge_id)
        if edge.source_node_id not in node_ids:
            errors.append(
                BuffGraphValidationError(
                    code="unknown_source_node",
                    message=f"Unknown source node id: {edge.source_node_id}",
                    path=f"{path}.source_node_id",
                )
            )
        if edge.target_node_id not in node_ids:
            errors.append(
                BuffGraphValidationError(
                    code="unknown_target_node",
                    message=f"Unknown target node id: {edge.target_node_id}",
                    path=f"{path}.target_node_id",
                )
            )

    return tuple(errors)


def _validate_node(
    node: BuffGraphNode,
    path: str,
    errors: list[BuffGraphValidationError],
) -> None:
    _require_text(node.node_id, f"{path}.node_id", errors)
    _require_text(node.block_id, f"{path}.block_id", errors)
    _require_text(node.adapter_id, f"{path}.adapter_id", errors)
    unsafe_tokens = FORBIDDEN_NODE_FAMILIES | {"eval", "exec"}
    combined = f"{node.family.value} {node.block_id} {node.adapter_id}".lower()
    if any(token in combined for token in unsafe_tokens):
        errors.append(
            BuffGraphValidationError(
                code="custom_python_node_forbidden",
                message="BuffGraphSpec nodes must use controlled building blocks, not Python/script/code nodes",
                path=path,
            )
        )


def _require_text(
    value: str | None,
    path: str,
    errors: list[BuffGraphValidationError],
) -> None:
    if value is None or not value.strip():
        errors.append(
            BuffGraphValidationError(
                code="required_text",
                message=f"{path} must be non-empty text",
                path=path,
            )
        )

