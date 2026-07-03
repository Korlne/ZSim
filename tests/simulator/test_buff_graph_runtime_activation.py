from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from zsim.sim_progress.BuffGraph.runtime.activation import (
    BuffGraphRuntimeActivationIndex,
)
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.spec import (
    BuffGraphEdge,
    BuffGraphSpec,
    OwnerKind,
    RuntimeStatus,
)


def test_activation_index_defaults_to_legacy_when_no_visual_candidate(tmp_path: Path) -> None:
    spec = _spec(runtime_status=RuntimeStatus.LEGACY_PYTHON)
    path = _write_generated_spec(tmp_path, spec)

    index = BuffGraphRuntimeActivationIndex.from_generated_spec_paths([path])
    decision = index.choose_for_buff(source_buff_index=spec.source_buff_index)

    assert decision.use_legacy is True
    assert decision.reason == "legacy_fallback_no_graph_candidate"


def test_activation_index_selects_valid_compiled_candidate_by_buff_index(
    tmp_path: Path,
) -> None:
    spec = _spec(runtime_status=RuntimeStatus.VISUAL_GRAPH_CANDIDATE)
    path = _write_generated_spec(tmp_path, spec)

    index = BuffGraphRuntimeActivationIndex.from_generated_spec_paths([path])
    decision = index.choose_for_buff(source_buff_index="Buff-Test-Activation")

    assert decision.use_graph is True
    assert decision.reason == "visual_graph_candidate_selected"
    assert decision.spec is not None
    assert decision.spec.graph_id == "test-activation"
    assert decision.spec.runtime_status == RuntimeStatus.VISUAL_GRAPH_CANDIDATE


def test_activation_index_selects_candidate_by_xlogic_path(tmp_path: Path) -> None:
    spec = _spec(runtime_status=RuntimeStatus.VISUAL_GRAPH_CANDIDATE)
    path = _write_generated_spec(tmp_path, spec)

    index = BuffGraphRuntimeActivationIndex.from_generated_spec_paths([path])
    decision = index.choose_for_buff(
        xlogic_path="zsim\\sim_progress\\Buff\\BuffXLogic\\TestActivation.py"
    )

    assert decision.use_graph is True
    assert decision.spec is not None
    assert decision.spec.graph_id == spec.graph_id


def test_activation_index_refuses_ambiguous_candidates(tmp_path: Path) -> None:
    first = _spec(
        graph_id="first",
        runtime_status=RuntimeStatus.VISUAL_GRAPH_CANDIDATE,
    )
    second = _spec(
        graph_id="second",
        runtime_status=RuntimeStatus.VISUAL_GRAPH_CANDIDATE,
    )
    paths = [
        _write_generated_spec(tmp_path, first),
        _write_generated_spec(tmp_path, second),
    ]

    index = BuffGraphRuntimeActivationIndex.from_generated_spec_paths(paths)
    decision = index.choose_for_buff(source_buff_index="Buff-Test-Activation")

    assert decision.use_legacy is True
    assert decision.reason == "legacy_fallback_ambiguous_graph_candidate"
    assert decision.diagnostics[0].code == "ambiguous_graph_candidate"


def test_activation_index_filters_uncompiled_candidates(tmp_path: Path) -> None:
    spec = _spec(runtime_status=RuntimeStatus.VISUAL_GRAPH_CANDIDATE)
    broken = replace(
        spec,
        edges=(
            BuffGraphEdge(
                edge_id="bad-edge",
                source_node_id="trigger",
                target_node_id="missing",
            ),
        ),
    )
    path = _write_generated_spec(tmp_path, broken)

    index = BuffGraphRuntimeActivationIndex.from_generated_spec_paths([path])
    decision = index.choose_for_buff(source_buff_index="Buff-Test-Activation")

    assert decision.use_legacy is True
    assert decision.reason == "legacy_fallback_no_graph_candidate"
    assert index.diagnostics[0].code == "spec_validation_failed"


def _spec(
    *,
    graph_id: str = "test-activation",
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
        graph_id=graph_id,
        display_name="Test Activation",
        owner_kind=OwnerKind.CHARACTER,
        owner_name="Test",
        source_buff_index="Buff-Test-Activation",
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/TestActivation.py",
        nodes=(trigger, effect),
        edges=(BuffGraphEdge("edge-1", "trigger", "effect"),),
    )
    return replace(draft, runtime_status=runtime_status)


def _write_generated_spec(tmp_path: Path, spec: BuffGraphSpec) -> Path:
    path = tmp_path / f"{spec.graph_id}.buffgraph.json"
    payload = {
        "schema": "zsim-buffgraph-generated-spec.v1",
        "spec": {
            "schema_version": spec.schema_version,
            "node_library_version": spec.node_library_version,
            "adapter_contract_version": spec.adapter_contract_version,
            "graph_id": spec.graph_id,
            "display_name": spec.display_name,
            "owner_kind": spec.owner_kind.value,
            "owner_name": spec.owner_name,
            "source_buff_index": spec.source_buff_index,
            "created_from_xlogic": spec.created_from_xlogic,
            "runtime_status": spec.runtime_status.value,
            "nodes": [
                {
                    "node_id": node.node_id,
                    "family": node.family.value,
                    "block_id": node.block_id,
                    "adapter_id": node.adapter_id,
                    "params": dict(node.params),
                    "display_name": node.display_name,
                }
                for node in spec.nodes
            ],
            "edges": [
                {
                    "edge_id": edge.edge_id,
                    "source_node_id": edge.source_node_id,
                    "target_node_id": edge.target_node_id,
                    "source_port": edge.source_port,
                    "target_port": edge.target_port,
                }
                for edge in spec.edges
            ],
            "params": dict(spec.params),
            "parity_metadata": dict(spec.parity_metadata),
            "last_parity_baseline": spec.last_parity_baseline,
            "last_verified_at": spec.last_verified_at,
        },
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path
