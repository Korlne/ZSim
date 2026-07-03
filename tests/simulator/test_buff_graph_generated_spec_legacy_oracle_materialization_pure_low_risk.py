from __future__ import annotations

import json
from pathlib import Path

from zsim.api_src.models.buff_graph import BuffGraphSpecModel
from zsim.sim_progress.BuffGraph.spec import RuntimeStatus

from tests.simulator.buff_graph_legacy_oracle_collector import (
    LegacyXLogicExecutionContext,
    LegacyXLogicOracleCase,
    LegacyXLogicRunResult,
    collect_legacy_xlogic_oracle,
)


FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "buff_graph"
ORACLE_ROOT = FIXTURE_ROOT / "generated-spec-legacy-oracles"

PURE_LOW_RISK_CASES = [
    (
        "cordis-germina-crit-rate-bonus-legacy-oracle.json",
        "pure-low-risk/cordis-germina-crit-rate-bonus-candidate.json",
    ),
    (
        "astra-yao-idyllic-cadenza-legacy-oracle.json",
        "pure-low-risk/astra-yao-idyllic-cadenza-candidate.json",
    ),
]


def test_pure_low_risk_generated_spec_legacy_oracles_match_collector() -> None:
    for oracle_name, candidate_suffix in PURE_LOW_RISK_CASES:
        oracle_fixture = _read_json(ORACLE_ROOT / oracle_name)
        candidate_fixture = _read_json(
            FIXTURE_ROOT / "runtime-candidate-harness" / candidate_suffix
        )
        generated_wrapper = _read_json(Path(oracle_fixture["source_generated_spec"]))
        spec = BuffGraphSpecModel.model_validate(generated_wrapper["spec"]).to_domain()

        assert spec.graph_id == oracle_fixture["graph_id"]
        assert spec.runtime_status == RuntimeStatus.LEGACY_PYTHON
        assert spec.parity_metadata["parity_status"] == "not_run"
        assert oracle_fixture["full_parity_verified"] is False

        result = collect_legacy_xlogic_oracle(
            LegacyXLogicOracleCase(
                case_id=oracle_fixture["case_id"],
                source_xlogic_path=generated_wrapper["source_xlogic_path"],
                source_buff_index=spec.display_name,
                tick=oracle_fixture["tick"],
                phase="judge",
                prepared_context_fixture=candidate_fixture["prepared_context"],
                record_seed=oracle_fixture["legacy_oracle_result"]["record_before"],
            ),
            runner=lambda context, fixture=candidate_fixture: _state_only_runner(
                context,
                candidate_fixture=fixture,
            ),
        )

        assert _json_shape(result.to_evidence()) == oracle_fixture["legacy_oracle_result"]


def test_pure_low_risk_oracle_fixtures_do_not_claim_full_parity() -> None:
    for oracle_name, _candidate_suffix in PURE_LOW_RISK_CASES:
        oracle_fixture = _read_json(ORACLE_ROOT / oracle_name)

        assert oracle_fixture["parity_status"] == "legacy_oracle_materialized_only"
        assert oracle_fixture["full_parity_verified"] is False
        assert oracle_fixture["legacy_oracle"] == "legacy_python_collected"


def _state_only_runner(
    context: LegacyXLogicExecutionContext,
    *,
    candidate_fixture: dict,
) -> LegacyXLogicRunResult:
    assert context.side_effect_policy == "spy_only"
    return LegacyXLogicRunResult(
        judge_result=True,
        expected_final_output=candidate_fixture["expected_final_output"],
        expected_trace_kind_checkpoint=candidate_fixture[
            "expected_trace_kind_checkpoint"
        ],
        record_after=candidate_fixture["expected_final_output"],
    )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _json_shape(value: object) -> object:
    return json.loads(json.dumps(value, ensure_ascii=False))
