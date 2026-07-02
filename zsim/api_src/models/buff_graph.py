from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from zsim.sim_progress.BuffGraph.spec import (
    BuffGraphEdge,
    BuffGraphNode,
    BuffGraphSpec,
    OwnerKind,
    RuntimeStatus,
)
from zsim.sim_progress.BuffGraph.spec.schema import NodeFamily


class BuffGraphAPIResponse(BaseModel):
    code: int = 200
    message: str = "Success"
    data: Any | None = None


class BuffGraphNodeModel(BaseModel):
    node_id: str
    family: NodeFamily
    block_id: str
    adapter_id: str
    params: dict[str, Any] = Field(default_factory=dict)
    display_name: str = ""

    @classmethod
    def from_domain(cls, node: BuffGraphNode) -> "BuffGraphNodeModel":
        return cls(
            node_id=node.node_id,
            family=node.family,
            block_id=node.block_id,
            adapter_id=node.adapter_id,
            params=dict(node.params),
            display_name=node.display_name,
        )

    def to_domain(self) -> BuffGraphNode:
        return BuffGraphNode(
            node_id=self.node_id,
            family=self.family,
            block_id=self.block_id,
            adapter_id=self.adapter_id,
            params=dict(self.params),
            display_name=self.display_name,
        )


class BuffGraphEdgeModel(BaseModel):
    edge_id: str
    source_node_id: str
    target_node_id: str
    source_port: str = "out"
    target_port: str = "in"

    @classmethod
    def from_domain(cls, edge: BuffGraphEdge) -> "BuffGraphEdgeModel":
        return cls(
            edge_id=edge.edge_id,
            source_node_id=edge.source_node_id,
            target_node_id=edge.target_node_id,
            source_port=edge.source_port,
            target_port=edge.target_port,
        )

    def to_domain(self) -> BuffGraphEdge:
        return BuffGraphEdge(
            edge_id=self.edge_id,
            source_node_id=self.source_node_id,
            target_node_id=self.target_node_id,
            source_port=self.source_port,
            target_port=self.target_port,
        )


class BuffGraphSpecModel(BaseModel):
    schema_version: str
    node_library_version: str
    adapter_contract_version: str
    graph_id: str
    display_name: str
    owner_kind: OwnerKind
    owner_name: str
    source_buff_index: str | None = None
    created_from_xlogic: str | None = None
    runtime_status: RuntimeStatus = RuntimeStatus.LEGACY_PYTHON
    nodes: list[BuffGraphNodeModel] = Field(default_factory=list)
    edges: list[BuffGraphEdgeModel] = Field(default_factory=list)
    params: dict[str, Any] = Field(default_factory=dict)
    parity_metadata: dict[str, Any] = Field(default_factory=dict)
    last_parity_baseline: str | None = None
    last_verified_at: str | None = None

    @classmethod
    def from_domain(cls, spec: BuffGraphSpec) -> "BuffGraphSpecModel":
        return cls(
            schema_version=spec.schema_version,
            node_library_version=spec.node_library_version,
            adapter_contract_version=spec.adapter_contract_version,
            graph_id=spec.graph_id,
            display_name=spec.display_name,
            owner_kind=spec.owner_kind,
            owner_name=spec.owner_name,
            source_buff_index=spec.source_buff_index,
            created_from_xlogic=spec.created_from_xlogic,
            runtime_status=spec.runtime_status,
            nodes=[BuffGraphNodeModel.from_domain(node) for node in spec.nodes],
            edges=[BuffGraphEdgeModel.from_domain(edge) for edge in spec.edges],
            params=dict(spec.params),
            parity_metadata=dict(spec.parity_metadata),
            last_parity_baseline=spec.last_parity_baseline,
            last_verified_at=spec.last_verified_at,
        )

    def to_domain(self) -> BuffGraphSpec:
        return BuffGraphSpec(
            schema_version=self.schema_version,
            node_library_version=self.node_library_version,
            adapter_contract_version=self.adapter_contract_version,
            graph_id=self.graph_id,
            display_name=self.display_name,
            owner_kind=self.owner_kind,
            owner_name=self.owner_name,
            source_buff_index=self.source_buff_index,
            created_from_xlogic=self.created_from_xlogic,
            runtime_status=self.runtime_status,
            nodes=tuple(node.to_domain() for node in self.nodes),
            edges=tuple(edge.to_domain() for edge in self.edges),
            params=dict(self.params),
            parity_metadata=dict(self.parity_metadata),
            last_parity_baseline=self.last_parity_baseline,
            last_verified_at=self.last_verified_at,
        )


class BuffGraphCreateRequest(BaseModel):
    spec: BuffGraphSpecModel


class BuffGraphUpdateRequest(BaseModel):
    spec: BuffGraphSpecModel


class BuffGraphStatusRequest(BaseModel):
    runtime_status: RuntimeStatus
    last_verified_at: str | None = None


class BuffGraphXLogicImportRequest(BaseModel):
    xlogic_path: str
    source: str
    owner_kind: OwnerKind = OwnerKind.UNKNOWN
    owner_name: str
    source_buff_index: str | None = None
    graph_id: str | None = None
    display_name: str | None = None


class BuffGraphCensusRequest(BaseModel):
    sources: dict[str, str]


class BuffGraphValidationPayload(BaseModel):
    valid: bool
    errors: list[dict[str, str]]


class BuffGraphCompilePayload(BaseModel):
    compiled: bool
    errors: list[dict[str, str]]
    execution_order: list[str] = Field(default_factory=list)


class BuffGraphParityPayload(BaseModel):
    status: Literal["not_available", "ready_for_oracle"]
    graph_id: str
    reason: str


class BuffGraphMatrixPayload(BaseModel):
    status: Literal["not_available"]
    reason: str
    required_command: str | None = None
