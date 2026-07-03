import json
from dataclasses import replace
from pathlib import Path

import pytest

from zsim.sim_progress.BuffGraph.adapters.compose_adapters import build_low_risk_compose_adapters
from zsim.sim_progress.BuffGraph.adapters.condition_adapters import (
    build_enemy_anomaly_state_condition_adapters,
    build_low_risk_condition_adapters,
    build_prepared_context_condition_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.effect_adapters import (
    build_low_risk_effect_adapters,
    build_prepared_context_effect_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.read_adapters import (
    build_enemy_anomaly_state_read_adapters,
    build_low_risk_read_adapters,
    build_prepared_context_read_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.state_adapters import (
    build_enemy_anomaly_state_state_adapters,
    build_low_risk_state_adapters,
)
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.runtime.parity import (
    BuffGraphCandidateParityOracle,
    run_buff_graph_candidate_parity,
)
from zsim.sim_progress.BuffGraph.spec import (
    BuffGraphEdge,
    BuffGraphNode,
    BuffGraphSpec,
    OwnerKind,
    RuntimeStatus,
)
from zsim.sim_progress.BuffGraph.spec.schema import NodeFamily


FIXTURE_ROOT = (
    Path(__file__).parents[1]
    / "fixtures"
    / "buff_graph"
    / "runtime-candidate-harness"
    / "enemy-state"
)


@pytest.mark.parametrize(
    "fixture_name",
    [
        "anomaly-debuff-exit-judge-candidate.json",
        "miyabi-core-skill-frost-burn-candidate.json",
        "branch-blade-song-crit-rate-bonus-candidate.json",
    ],
)
def test_enemy_state_generated_spec_candidate_harness_matches_fixture(
    fixture_name: str,
) -> None:
    case = _read_json(FIXTURE_ROOT / fixture_name)
    spec = _load_generated_spec(Path(case["source_generated_spec"]))
    assert spec.runtime_status == RuntimeStatus.LEGACY_PYTHON

    candidate_spec = replace(
        spec,
        runtime_status=RuntimeStatus.VISUAL_GRAPH_CANDIDATE,
        parity_metadata={
            "parity_status": "candidate_oracle_fixture",
            "candidate_harness_case_id": case["case_id"],
        },
    )

    result = run_buff_graph_candidate_parity(
        candidate_spec,
        block_registry=build_default_block_registry(),
        adapters=_enemy_state_candidate_adapters(),
        tick=case["tick"],
        prepared_context=case["prepared_context"],
        oracle=BuffGraphCandidateParityOracle(
            case_id=case["case_id"],
            expected_final_output=case["expected_final_output"],
            expected_trace_kind_checkpoint=case["expected_trace_kind_checkpoint"],
            legacy_oracle=case["legacy_oracle"],
        ),
    )

    assert result.passed is True
    assert result.runtime_status == "visual_graph_candidate"
    assert result.compile_passed is True
    assert result.execution_passed is True
    assert result.output_passed is True
    assert result.trace_valid is True
    assert result.trace_checkpoint_passed is True
    assert result.actual_final_output == case["expected_final_output"]
    assert result.to_evidence()["legacy_oracle"] == (
        "generated_spec_fixture_pending_legacy_python_oracle"
    )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_generated_spec(path: Path) -> BuffGraphSpec:
    wrapper = _read_json(path)
    payload = wrapper["spec"]
    return BuffGraphSpec(
        schema_version=payload["schema_version"],
        node_library_version=payload["node_library_version"],
        adapter_contract_version=payload["adapter_contract_version"],
        graph_id=payload["graph_id"],
        display_name=payload["display_name"],
        owner_kind=OwnerKind(payload["owner_kind"]),
        owner_name=payload["owner_name"],
        source_buff_index=payload.get("source_buff_index"),
        created_from_xlogic=payload.get("created_from_xlogic"),
        runtime_status=RuntimeStatus(payload["runtime_status"]),
        nodes=tuple(
            BuffGraphNode(
                node_id=node["node_id"],
                family=NodeFamily(node["family"]),
                block_id=node["block_id"],
                adapter_id=node["adapter_id"],
                params=node.get("params", {}),
                display_name=node.get("display_name", ""),
            )
            for node in payload["nodes"]
        ),
        edges=tuple(
            BuffGraphEdge(
                edge_id=edge["edge_id"],
                source_node_id=edge["source_node_id"],
                target_node_id=edge["target_node_id"],
                source_port=edge.get("source_port", "out"),
                target_port=edge.get("target_port", "in"),
            )
            for edge in payload["edges"]
        ),
        params=payload.get("params", {}),
        parity_metadata=payload.get("parity_metadata", {}),
        last_parity_baseline=payload.get("last_parity_baseline"),
        last_verified_at=payload.get("last_verified_at"),
    )


def _enemy_state_candidate_adapters() -> dict[str, object]:
    adapters: dict[str, object] = {}
    for group in (
        build_low_risk_compose_adapters(),
        build_low_risk_condition_adapters(),
        build_prepared_context_condition_adapters(),
        build_enemy_anomaly_state_condition_adapters(),
        build_low_risk_effect_adapters(),
        build_prepared_context_effect_adapters(),
        build_low_risk_read_adapters(),
        build_prepared_context_read_adapters(),
        build_enemy_anomaly_state_read_adapters(),
        build_low_risk_state_adapters(),
        build_enemy_anomaly_state_state_adapters(),
    ):
        adapters.update(group)
    return adapters
