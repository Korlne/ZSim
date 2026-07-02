import json
from dataclasses import replace
from pathlib import Path

from zsim.sim_progress.BuffGraph.adapters.compose_adapters import build_low_risk_compose_adapters
from zsim.sim_progress.BuffGraph.adapters.condition_adapters import (
    build_low_risk_condition_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.effect_adapters import build_low_risk_effect_adapters
from zsim.sim_progress.BuffGraph.adapters.read_adapters import build_low_risk_read_adapters
from zsim.sim_progress.BuffGraph.adapters.state_adapters import build_low_risk_state_adapters
from zsim.sim_progress.BuffGraph.adapters.trigger_adapters import build_low_risk_trigger_adapters
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.migration import import_xlogic_to_graph
from zsim.sim_progress.BuffGraph.runtime.parity import (
    BuffGraphCandidateParityOracle,
    run_buff_graph_candidate_parity,
)
from zsim.sim_progress.BuffGraph.spec import OwnerKind, RuntimeStatus


FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "buff_graph"


def test_low_risk_candidate_harness_matches_legacy_fixture_without_runtime_cutover() -> None:
    case = _read_json(FIXTURE_ROOT / "runtime-candidate-harness" / "alice-cinema6-candidate-parity.json")
    legacy_fixture = _read_json(Path(case["source_fixture"]))
    registry = build_default_block_registry()
    import_result = import_xlogic_to_graph(
        xlogic_path=legacy_fixture["xlogic_path"],
        source=legacy_fixture["source"],
        owner_kind=OwnerKind(legacy_fixture["owner_kind"]),
        owner_name=legacy_fixture["owner_name"],
        source_buff_index=legacy_fixture["source_buff_index"],
        block_registry=registry,
    )
    assert import_result.imported is True
    assert import_result.spec is not None
    assert import_result.spec.runtime_status == RuntimeStatus.LEGACY_PYTHON

    candidate_spec = replace(
        import_result.spec,
        runtime_status=RuntimeStatus.VISUAL_GRAPH_CANDIDATE,
        parity_metadata={
            "parity_status": "candidate_oracle_fixture",
            "candidate_harness_case_id": case["case_id"],
        },
    )

    result = run_buff_graph_candidate_parity(
        candidate_spec,
        block_registry=registry,
        adapters=_low_risk_adapters(),
        tick=case["tick"],
        prepared_context=legacy_fixture["prepared_context"],
        oracle=BuffGraphCandidateParityOracle(
            case_id=case["case_id"],
            expected_final_output=legacy_fixture["expected_final_output"],
            expected_trace_kind_checkpoint=legacy_fixture["expected_trace_kind_checkpoint"],
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
    assert result.actual_final_output == legacy_fixture["expected_final_output"]
    assert result.to_evidence()["legacy_oracle"] == "legacy_python_fixture"


def test_candidate_harness_rejects_visual_graph_default_promotion() -> None:
    case = _read_json(FIXTURE_ROOT / "runtime-candidate-harness" / "alice-cinema6-candidate-parity.json")
    legacy_fixture = _read_json(Path(case["source_fixture"]))
    registry = build_default_block_registry()
    import_result = import_xlogic_to_graph(
        xlogic_path=legacy_fixture["xlogic_path"],
        source=legacy_fixture["source"],
        owner_kind=OwnerKind(legacy_fixture["owner_kind"]),
        owner_name=legacy_fixture["owner_name"],
        source_buff_index=legacy_fixture["source_buff_index"],
        block_registry=registry,
    )
    assert import_result.spec is not None

    default_spec = replace(
        import_result.spec,
        runtime_status=RuntimeStatus.VISUAL_GRAPH_DEFAULT,
        last_verified_at="2026-07-03T00:00:00Z",
    )

    result = run_buff_graph_candidate_parity(
        default_spec,
        block_registry=registry,
        adapters=_low_risk_adapters(),
        tick=case["tick"],
        prepared_context=legacy_fixture["prepared_context"],
        oracle=BuffGraphCandidateParityOracle(
            case_id=case["case_id"],
            expected_final_output=legacy_fixture["expected_final_output"],
            expected_trace_kind_checkpoint=legacy_fixture["expected_trace_kind_checkpoint"],
            legacy_oracle=case["legacy_oracle"],
        ),
    )

    assert result.passed is False
    assert "visual_graph_default is not allowed in candidate parity harness" in result.errors


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _low_risk_adapters() -> dict[str, object]:
    adapters: dict[str, object] = {}
    for group in (
        build_low_risk_trigger_adapters(),
        build_low_risk_condition_adapters(),
        build_low_risk_read_adapters(),
        build_low_risk_effect_adapters(),
        build_low_risk_state_adapters(),
        build_low_risk_compose_adapters(),
    ):
        adapters.update(group)
    return adapters
