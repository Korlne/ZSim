from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping

from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.blocks.registry import BuffGraphBlockRegistry
from zsim.sim_progress.BuffGraph.runtime.compiler import compile_buff_graph_spec
from zsim.sim_progress.BuffGraph.spec import (
    BuffGraphEdge,
    BuffGraphNode,
    BuffGraphSpec,
    OwnerKind,
    RuntimeStatus,
    validate_buff_graph_spec,
)
from zsim.sim_progress.BuffGraph.spec.schema import NodeFamily


ACTIVATABLE_RUNTIME_STATUSES = frozenset(
    {
        RuntimeStatus.VISUAL_GRAPH_CANDIDATE,
        RuntimeStatus.VISUAL_GRAPH_DEFAULT,
    }
)


@dataclass(frozen=True, slots=True)
class BuffGraphActivationDiagnostic:
    code: str
    message: str
    graph_id: str | None = None
    source_path: str | None = None


@dataclass(frozen=True, slots=True)
class BuffGraphActivationDecision:
    use_graph: bool
    reason: str
    spec: BuffGraphSpec | None = None
    diagnostics: tuple[BuffGraphActivationDiagnostic, ...] = ()

    @property
    def use_legacy(self) -> bool:
        return not self.use_graph


@dataclass(frozen=True, slots=True)
class BuffGraphRuntimeActivationIndex:
    _by_buff_index: Mapping[str, tuple[BuffGraphSpec, ...]] = field(default_factory=dict)
    _by_xlogic_path: Mapping[str, tuple[BuffGraphSpec, ...]] = field(default_factory=dict)
    diagnostics: tuple[BuffGraphActivationDiagnostic, ...] = ()

    @classmethod
    def from_generated_spec_paths(
        cls,
        paths: Iterable[Path],
        *,
        block_registry: BuffGraphBlockRegistry | None = None,
    ) -> "BuffGraphRuntimeActivationIndex":
        registry = block_registry or build_default_block_registry()
        by_buff_index: dict[str, list[BuffGraphSpec]] = {}
        by_xlogic_path: dict[str, list[BuffGraphSpec]] = {}
        diagnostics: list[BuffGraphActivationDiagnostic] = []

        for path in paths:
            try:
                spec = _load_generated_spec(path)
            except Exception as exc:
                diagnostics.append(
                    BuffGraphActivationDiagnostic(
                        code="spec_load_failed",
                        message=str(exc),
                        source_path=path.as_posix(),
                    )
                )
                continue

            if spec.runtime_status not in ACTIVATABLE_RUNTIME_STATUSES:
                continue

            validation_errors = validate_buff_graph_spec(spec)
            if validation_errors:
                diagnostics.append(
                    BuffGraphActivationDiagnostic(
                        code="spec_validation_failed",
                        message="; ".join(error.code for error in validation_errors),
                        graph_id=spec.graph_id,
                        source_path=path.as_posix(),
                    )
                )
                continue

            compile_result = compile_buff_graph_spec(spec, block_registry=registry)
            if not compile_result.passed:
                diagnostics.append(
                    BuffGraphActivationDiagnostic(
                        code="spec_compile_failed",
                        message="; ".join(error.code for error in compile_result.errors),
                        graph_id=spec.graph_id,
                        source_path=path.as_posix(),
                    )
                )
                continue

            if spec.source_buff_index:
                by_buff_index.setdefault(spec.source_buff_index, []).append(spec)
            if spec.created_from_xlogic:
                by_xlogic_path.setdefault(_normalize_path(spec.created_from_xlogic), []).append(spec)

        return cls(
            _by_buff_index={key: tuple(value) for key, value in by_buff_index.items()},
            _by_xlogic_path={key: tuple(value) for key, value in by_xlogic_path.items()},
            diagnostics=tuple(diagnostics),
        )

    def choose_for_buff(
        self,
        *,
        source_buff_index: str | None = None,
        xlogic_path: str | None = None,
    ) -> BuffGraphActivationDecision:
        candidates: list[BuffGraphSpec] = []
        if source_buff_index:
            candidates.extend(self._by_buff_index.get(source_buff_index, ()))
        if xlogic_path:
            candidates.extend(self._by_xlogic_path.get(_normalize_path(xlogic_path), ()))

        unique_candidates = {spec.graph_id: spec for spec in candidates}
        if not unique_candidates:
            return BuffGraphActivationDecision(
                use_graph=False,
                reason="legacy_fallback_no_graph_candidate",
            )
        if len(unique_candidates) > 1:
            return BuffGraphActivationDecision(
                use_graph=False,
                reason="legacy_fallback_ambiguous_graph_candidate",
                diagnostics=(
                    BuffGraphActivationDiagnostic(
                        code="ambiguous_graph_candidate",
                        message=", ".join(sorted(unique_candidates)),
                    ),
                ),
            )
        spec = next(iter(unique_candidates.values()))
        return BuffGraphActivationDecision(
            use_graph=True,
            reason="visual_graph_candidate_selected",
            spec=spec,
        )


def _load_generated_spec(path: Path) -> BuffGraphSpec:
    payload = json.loads(path.read_text(encoding="utf-8"))
    spec_payload = payload.get("spec") if isinstance(payload, dict) else None
    if not isinstance(spec_payload, dict):
        spec_payload = payload
    return _spec_from_mapping(spec_payload)


def _spec_from_mapping(payload: Mapping[str, object]) -> BuffGraphSpec:
    return BuffGraphSpec(
        schema_version=str(payload["schema_version"]),
        node_library_version=str(payload["node_library_version"]),
        adapter_contract_version=str(payload["adapter_contract_version"]),
        graph_id=str(payload["graph_id"]),
        display_name=str(payload["display_name"]),
        owner_kind=OwnerKind(str(payload["owner_kind"])),
        owner_name=str(payload["owner_name"]),
        source_buff_index=(
            str(payload["source_buff_index"])
            if payload.get("source_buff_index") is not None
            else None
        ),
        created_from_xlogic=(
            str(payload["created_from_xlogic"])
            if payload.get("created_from_xlogic") is not None
            else None
        ),
        runtime_status=RuntimeStatus(str(payload["runtime_status"])),
        nodes=tuple(_node_from_mapping(node) for node in payload.get("nodes", ())),
        edges=tuple(_edge_from_mapping(edge) for edge in payload.get("edges", ())),
        params=_mapping(payload.get("params")),
        parity_metadata=_mapping(payload.get("parity_metadata")),
        last_parity_baseline=(
            str(payload["last_parity_baseline"])
            if payload.get("last_parity_baseline") is not None
            else None
        ),
        last_verified_at=(
            str(payload["last_verified_at"])
            if payload.get("last_verified_at") is not None
            else None
        ),
    )


def _node_from_mapping(payload: object) -> BuffGraphNode:
    if not isinstance(payload, Mapping):
        raise TypeError("node payload must be a mapping")
    return BuffGraphNode(
        node_id=str(payload["node_id"]),
        family=NodeFamily(str(payload["family"])),
        block_id=str(payload["block_id"]),
        adapter_id=str(payload["adapter_id"]),
        params=_mapping(payload.get("params")),
        display_name=str(payload.get("display_name", "")),
    )


def _edge_from_mapping(payload: object) -> BuffGraphEdge:
    if not isinstance(payload, Mapping):
        raise TypeError("edge payload must be a mapping")
    return BuffGraphEdge(
        edge_id=str(payload["edge_id"]),
        source_node_id=str(payload["source_node_id"]),
        target_node_id=str(payload["target_node_id"]),
        source_port=str(payload.get("source_port", "out")),
        target_port=str(payload.get("target_port", "in")),
    )


def _mapping(value: object) -> Mapping[str, object]:
    return value if isinstance(value, Mapping) else {}


def _normalize_path(value: str) -> str:
    return value.replace("\\", "/").casefold()
