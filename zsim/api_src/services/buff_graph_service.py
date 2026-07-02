from __future__ import annotations

from dataclasses import asdict
from typing import Any

from zsim.api_src.models.buff_graph import (
    BuffGraphCompilePayload,
    BuffGraphMatrixPayload,
    BuffGraphParityPayload,
    BuffGraphSpecModel,
    BuffGraphValidationPayload,
)
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.migration import classify_xlogic_source, import_xlogic_to_graph
from zsim.sim_progress.BuffGraph.runtime.compiler import compile_buff_graph_spec
from zsim.sim_progress.BuffGraph.spec import BuffGraphSpec, RuntimeStatus, validate_buff_graph_spec


class BuffGraphService:
    def __init__(self) -> None:
        self._graphs: dict[str, BuffGraphSpec] = {}
        self._block_registry = build_default_block_registry()

    def list_graphs(self) -> list[BuffGraphSpecModel]:
        return [BuffGraphSpecModel.from_domain(spec) for spec in self._graphs.values()]

    def get_graph(self, graph_id: str) -> BuffGraphSpecModel:
        return BuffGraphSpecModel.from_domain(self._require_graph(graph_id))

    def save_graph(self, spec_model: BuffGraphSpecModel) -> BuffGraphSpecModel:
        spec = spec_model.to_domain()
        self._graphs[spec.graph_id] = spec
        return BuffGraphSpecModel.from_domain(spec)

    def validate_graph(self, graph_id: str) -> BuffGraphValidationPayload:
        return self.validate_spec(self._require_graph(graph_id))

    def validate_spec(self, spec: BuffGraphSpec) -> BuffGraphValidationPayload:
        errors = validate_buff_graph_spec(spec)
        return BuffGraphValidationPayload(
            valid=not errors,
            errors=[asdict(error) for error in errors],
        )

    def compile_graph(self, graph_id: str) -> BuffGraphCompilePayload:
        result = compile_buff_graph_spec(
            self._require_graph(graph_id),
            block_registry=self._block_registry,
        )
        return BuffGraphCompilePayload(
            compiled=result.passed,
            errors=[asdict(error) for error in result.errors],
            execution_order=[] if result.compiled is None else list(result.compiled.execution_order),
        )

    def request_parity(self, graph_id: str) -> BuffGraphParityPayload:
        spec = self._require_graph(graph_id)
        compile_result = self.compile_graph(graph_id)
        if compile_result.compiled:
            return BuffGraphParityPayload(
                status="ready_for_oracle",
                graph_id=spec.graph_id,
                reason="Graph compiles; legacy-vs-graph parity execution is provided by later oracle/UI matrix packs.",
            )
        return BuffGraphParityPayload(
            status="not_available",
            graph_id=spec.graph_id,
            reason="Graph must compile before parity can run.",
        )

    def update_status(
        self,
        graph_id: str,
        *,
        runtime_status: RuntimeStatus,
        last_verified_at: str | None,
    ) -> BuffGraphSpecModel:
        spec = self._require_graph(graph_id)
        updated = BuffGraphSpec(
            schema_version=spec.schema_version,
            node_library_version=spec.node_library_version,
            adapter_contract_version=spec.adapter_contract_version,
            graph_id=spec.graph_id,
            display_name=spec.display_name,
            owner_kind=spec.owner_kind,
            owner_name=spec.owner_name,
            source_buff_index=spec.source_buff_index,
            created_from_xlogic=spec.created_from_xlogic,
            runtime_status=runtime_status,
            nodes=spec.nodes,
            edges=spec.edges,
            params=spec.params,
            parity_metadata=spec.parity_metadata,
            last_parity_baseline=spec.last_parity_baseline,
            last_verified_at=last_verified_at,
        )
        validation = self.validate_spec(updated)
        if not validation.valid:
            raise ValueError(f"Invalid graph status transition: {validation.errors}")
        self._graphs[graph_id] = updated
        return BuffGraphSpecModel.from_domain(updated)

    def migration_catalog(self) -> dict[str, Any]:
        return {
            "block_families": sorted(
                {block.family.value for block in self._block_registry.all()}
            ),
            "blocks": [
                {
                    "block_id": block.block_id,
                    "family": block.family.value,
                    "display_name": block.display_name,
                    "adapter_id": block.adapter_id,
                }
                for block in self._block_registry.all()
            ],
            "custom_python_nodes_allowed": False,
        }

    def census_sources(self, sources: dict[str, str]) -> list[dict[str, Any]]:
        return [
            {
                "xlogic_path": classification.xlogic_path,
                "triggers": list(classification.triggers),
                "conditions": list(classification.conditions),
                "reads": list(classification.reads),
                "effects": list(classification.effects),
                "state": list(classification.state),
                "migration_wave": classification.migration_wave,
                "unsupported_patterns": [
                    asdict(pattern) for pattern in classification.unsupported_patterns
                ],
            }
            for path, source in sources.items()
            for classification in (classify_xlogic_source(xlogic_path=path, source=source),)
        ]

    def import_xlogic(
        self,
        *,
        xlogic_path: str,
        source: str,
        owner_kind,
        owner_name: str,
        source_buff_index: str | None,
        graph_id: str | None,
        display_name: str | None,
    ) -> dict[str, Any]:
        result = import_xlogic_to_graph(
            xlogic_path=xlogic_path,
            source=source,
            owner_kind=owner_kind,
            owner_name=owner_name,
            source_buff_index=source_buff_index,
            graph_id=graph_id,
            display_name=display_name,
            block_registry=self._block_registry,
        )
        spec_model = None
        if result.spec is not None:
            self._graphs[result.spec.graph_id] = result.spec
            spec_model = BuffGraphSpecModel.from_domain(result.spec).model_dump(mode="json")
        return {
            "imported": result.imported,
            "spec": spec_model,
            "unsupported_patterns": [asdict(pattern) for pattern in result.unsupported_patterns],
            "validation_errors": [
                asdict(error) if hasattr(error, "__dataclass_fields__") else str(error)
                for error in result.validation_errors
            ],
        }

    def parity_matrix(self) -> BuffGraphMatrixPayload:
        return BuffGraphMatrixPayload(
            status="not_available",
            reason="UI-driven full simulation matrix command is produced by later validator/UI packs.",
            required_command=None,
        )

    def _require_graph(self, graph_id: str) -> BuffGraphSpec:
        try:
            return self._graphs[graph_id]
        except KeyError as exc:
            raise KeyError(f"Buff graph not found: {graph_id}") from exc
