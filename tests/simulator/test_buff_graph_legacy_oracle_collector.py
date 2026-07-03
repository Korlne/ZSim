from __future__ import annotations

from pathlib import Path

from zsim.sim_progress.BuffGraph.runtime.parity import BuffGraphCandidateParityOracle

from tests.simulator.buff_graph_legacy_oracle_collector import (
    LegacyXLogicExecutionContext,
    LegacyXLogicOracleCase,
    LegacyXLogicRunResult,
    collect_legacy_xlogic_oracle,
    fixture_case_from_legacy_parity_fixture,
)


FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "buff_graph"
ALICE_FIXTURE = (
    FIXTURE_ROOT / "low-risk-xlogic-parity" / "alice-cinema6-hit-start-buff.json"
)


def test_collector_materializes_alice_legacy_fixture_with_record_delta() -> None:
    case = fixture_case_from_legacy_parity_fixture(
        ALICE_FIXTURE,
        case_id="alice-cinema6-hit-start-buff",
        phase="hit",
        tick=600,
        legacy_kwargs={"beneficiary": "Alice"},
        record_seed={"last_active_tick": None, "extra_attack_count": 0},
    )

    def runner(context: LegacyXLogicExecutionContext) -> LegacyXLogicRunResult:
        assert context.side_effect_policy == "spy_only"
        assert context.source_xlogic_path.endswith("AliceCinema6Trigger.py")
        assert context.legacy_kwargs["beneficiary"] == "Alice"
        fixture = _read_fixture(ALICE_FIXTURE)
        return LegacyXLogicRunResult(
            hit_result=True,
            expected_final_output=fixture["expected_final_output"],
            expected_trace_kind_checkpoint=fixture["expected_trace_kind_checkpoint"],
            record_after={"last_active_tick": context.tick, "extra_attack_count": 1},
            side_effects=(
                {
                    "kind": "character_extra_attack_intent",
                    "target": "Alice",
                    "tick": context.tick,
                },
                {
                    "kind": "buff_command_intent",
                    "payload": fixture["expected_final_output"]["command"],
                },
            ),
        )

    result = collect_legacy_xlogic_oracle(case, runner=runner)

    assert result.legacy_oracle == "legacy_python_collected"
    assert result.blocked_reason is None
    assert result.hit_result is True
    assert result.expected_final_output == _read_fixture(ALICE_FIXTURE)["expected_final_output"]
    assert result.record_delta == {
        "extra_attack_count": {"before": 0, "after": 1},
        "last_active_tick": {"before": None, "after": 600},
    }
    assert result.side_effects[0]["kind"] == "character_extra_attack_intent"


def test_collector_result_feeds_candidate_parity_oracle_shape() -> None:
    fixture = _read_fixture(ALICE_FIXTURE)
    case = fixture_case_from_legacy_parity_fixture(
        ALICE_FIXTURE,
        case_id="alice-cinema6-hit-start-buff",
        phase="hit",
        tick=600,
    )
    result = collect_legacy_xlogic_oracle(
        case,
        runner=lambda _context: LegacyXLogicRunResult(
            expected_final_output=fixture["expected_final_output"],
            expected_trace_kind_checkpoint=fixture["expected_trace_kind_checkpoint"],
        ),
    )

    oracle = BuffGraphCandidateParityOracle(
        case_id=result.case_id,
        expected_final_output=result.expected_final_output,
        expected_trace_kind_checkpoint=result.expected_trace_kind_checkpoint,
        legacy_oracle=result.legacy_oracle,
    )

    assert oracle.legacy_oracle == "legacy_python_collected"
    assert oracle.expected_final_output == fixture["expected_final_output"]
    assert tuple(oracle.expected_trace_kind_checkpoint) == tuple(
        tuple(row) for row in fixture["expected_trace_kind_checkpoint"]
    )


def test_collector_blocks_without_explicit_legacy_runner() -> None:
    case = LegacyXLogicOracleCase(
        case_id="pending-generated-spec",
        source_xlogic_path="zsim/sim_progress/Buff/BuffXLogic/YuzuhaCinema2Trigger.py",
        source_buff_index="Buff-Yuzuha-Cinema2",
        tick=1500,
        phase="hit",
        record_seed={"last_active_tick": 299},
    )

    result = collect_legacy_xlogic_oracle(case, runner=None)

    assert result.legacy_oracle == "legacy_python_collector_blocked"
    assert result.blocked_reason == "legacy_xlogic_runner_required"
    assert result.record_before == {"last_active_tick": 299}
    assert result.record_after == {"last_active_tick": 299}
    assert result.record_delta == {}


def _read_fixture(path: Path) -> dict:
    import json

    return json.loads(path.read_text(encoding="utf-8"))
