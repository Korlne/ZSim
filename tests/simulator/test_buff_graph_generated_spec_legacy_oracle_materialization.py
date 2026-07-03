from __future__ import annotations

import json
from pathlib import Path

from zsim.api_src.models.buff_graph import BuffGraphSpecModel
from zsim.sim_progress.BuffGraph.runtime.parity import BuffGraphCandidateParityOracle
from zsim.sim_progress.BuffGraph.spec import RuntimeStatus

from tests.simulator.buff_graph_legacy_oracle_collector import (
    LegacyXLogicExecutionContext,
    LegacyXLogicOracleCase,
    LegacyXLogicRunResult,
    collect_legacy_xlogic_oracle,
)


FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "buff_graph"
ORACLE_FIXTURE = (
    FIXTURE_ROOT
    / "generated-spec-legacy-oracles"
    / "alice-cinema-6-trigger-legacy-oracle.json"
)
CANDIDATE_FIXTURE = (
    FIXTURE_ROOT
    / "runtime-candidate-harness"
    / "character-manager"
    / "alice-cinema-6-trigger-candidate.json"
)


def test_materialized_generated_spec_legacy_oracle_matches_collector_result() -> None:
    oracle_fixture = _read_json(ORACLE_FIXTURE)
    generated_wrapper = _read_json(Path(oracle_fixture["source_generated_spec"]))
    candidate_fixture = _read_json(CANDIDATE_FIXTURE)
    spec = BuffGraphSpecModel.model_validate(generated_wrapper["spec"]).to_domain()

    assert spec.graph_id == oracle_fixture["graph_id"]
    assert spec.runtime_status == RuntimeStatus.LEGACY_PYTHON
    assert spec.parity_metadata["parity_status"] == "not_run"
    assert oracle_fixture["full_parity_verified"] is False

    case = LegacyXLogicOracleCase(
        case_id=oracle_fixture["case_id"],
        source_xlogic_path=generated_wrapper["source_xlogic_path"],
        source_buff_index=spec.display_name,
        tick=oracle_fixture["tick"],
        phase="hit",
        legacy_kwargs={"skill_node": candidate_fixture["prepared_context"]["skill_node"]},
        prepared_context_fixture=candidate_fixture["prepared_context"],
        record_seed=oracle_fixture["legacy_oracle_result"]["record_before"],
    )

    result = collect_legacy_xlogic_oracle(
        case,
        runner=lambda context: _alice_cinema6_semantic_runner(
            context,
            candidate_fixture=candidate_fixture,
        ),
    )

    assert _json_shape(result.to_evidence()) == oracle_fixture["legacy_oracle_result"]


def test_materialized_oracle_fixture_can_feed_candidate_parity_oracle_shape() -> None:
    oracle_fixture = _read_json(ORACLE_FIXTURE)
    result = oracle_fixture["legacy_oracle_result"]

    oracle = BuffGraphCandidateParityOracle(
        case_id=result["case_id"],
        expected_final_output=result["expected_final_output"],
        expected_trace_kind_checkpoint=result["expected_trace_kind_checkpoint"],
        legacy_oracle=result["legacy_oracle"],
    )

    assert oracle.legacy_oracle == "legacy_python_collected"
    assert oracle.case_id == oracle_fixture["case_id"]
    assert oracle.expected_final_output == result["expected_final_output"]
    assert oracle.expected_trace_kind_checkpoint == result["expected_trace_kind_checkpoint"]


def _alice_cinema6_semantic_runner(
    context: LegacyXLogicExecutionContext,
    *,
    candidate_fixture: dict,
) -> LegacyXLogicRunResult:
    assert context.side_effect_policy == "spy_only"
    assert context.source_xlogic_path.endswith("AliceCinema6Trigger.py")
    expected_trace = _expected_trace(
        node_count=candidate_fixture["expected_trace_node_count"],
        effect_node_indexes=candidate_fixture["expected_trace_effect_node_indexes"],
    )
    return LegacyXLogicRunResult(
        judge_result=True,
        hit_result=True,
        expected_final_output=candidate_fixture["expected_final_output"],
        expected_trace_kind_checkpoint=expected_trace,
        record_after={"extra_attack_count": 1, "last_active_tick": context.tick},
        side_effects=(
            {
                "kind": "character_extra_attack_intent",
                "source_xlogic": context.source_xlogic_path,
                "target": "legacy_source_review_required",
                "tick": context.tick,
            },
        ),
    )


def _expected_trace(
    *,
    node_count: int,
    effect_node_indexes: list[int],
) -> tuple[tuple[str, str], ...]:
    events: list[tuple[str, str]] = [("graph_started", "")]
    effect_slots = set(effect_node_indexes)
    for index in range(node_count):
        events.append(("node_evaluated", "node_ready"))
        events.append(("adapter_executed", "adapter_executed"))
        if index in effect_slots:
            events.append(("effect_requested", "effect_requested"))
    events.append(("graph_finished", "graph_finished"))
    return tuple(events)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _json_shape(value: object) -> object:
    return json.loads(json.dumps(value, ensure_ascii=False))
