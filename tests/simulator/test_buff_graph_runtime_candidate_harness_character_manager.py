import json
from dataclasses import replace
from pathlib import Path

import pytest

from zsim.api_src.models.buff_graph import BuffGraphSpecModel
from zsim.sim_progress.BuffGraph.adapters.compose_adapters import build_low_risk_compose_adapters
from zsim.sim_progress.BuffGraph.adapters.condition_adapters import (
    build_character_manager_side_effect_condition_adapters,
    build_enemy_anomaly_state_condition_adapters,
    build_low_risk_condition_adapters,
    build_prepared_context_condition_adapters,
    build_runtime_command_scheduled_signal_condition_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.effect_adapters import (
    build_character_manager_side_effect_effect_adapters,
    build_low_risk_effect_adapters,
    build_prepared_context_effect_adapters,
    build_runtime_command_scheduled_signal_effect_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.read_adapters import (
    build_character_manager_side_effect_read_adapters,
    build_enemy_anomaly_state_read_adapters,
    build_low_risk_read_adapters,
    build_prepared_context_read_adapters,
    build_runtime_command_scheduled_signal_read_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.state_adapters import (
    build_character_manager_side_effect_state_adapters,
    build_enemy_anomaly_state_state_adapters,
    build_low_risk_state_adapters,
    build_runtime_command_scheduled_signal_state_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.trigger_adapters import build_low_risk_trigger_adapters
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.runtime.parity import (
    BuffGraphCandidateParityOracle,
    run_buff_graph_candidate_parity,
)
from zsim.sim_progress.BuffGraph.spec import BuffGraphSpec, RuntimeStatus


FIXTURE_ROOT = (
    Path(__file__).parents[1]
    / "fixtures"
    / "buff_graph"
    / "runtime-candidate-harness"
    / "character-manager"
)


@pytest.mark.parametrize(
    "fixture_name",
    [
        "alice-cinema-6-trigger-candidate.json",
        "vivian-coattack-trigger-candidate.json",
        "yixuan-cinema-1-trigger-candidate.json",
    ],
)
def test_character_manager_generated_spec_candidate_harness_matches_fixture(
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
        adapters=_character_manager_candidate_adapters(),
        tick=case["tick"],
        prepared_context=case["prepared_context"],
        oracle=BuffGraphCandidateParityOracle(
            case_id=case["case_id"],
            expected_final_output=case["expected_final_output"],
            expected_trace_kind_checkpoint=_expected_trace(
                node_count=case["expected_trace_node_count"],
                effect_node_indexes=case["expected_trace_effect_node_indexes"],
            ),
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
    return BuffGraphSpecModel.model_validate(wrapper["spec"]).to_domain()


def _character_manager_candidate_adapters() -> dict[str, object]:
    adapters: dict[str, object] = {}
    for group in (
        build_low_risk_trigger_adapters(),
        build_low_risk_compose_adapters(),
        build_low_risk_condition_adapters(),
        build_prepared_context_condition_adapters(),
        build_runtime_command_scheduled_signal_condition_adapters(),
        build_enemy_anomaly_state_condition_adapters(),
        build_character_manager_side_effect_condition_adapters(),
        build_low_risk_effect_adapters(),
        build_prepared_context_effect_adapters(),
        build_runtime_command_scheduled_signal_effect_adapters(),
        build_character_manager_side_effect_effect_adapters(),
        build_low_risk_read_adapters(),
        build_prepared_context_read_adapters(),
        build_runtime_command_scheduled_signal_read_adapters(),
        build_enemy_anomaly_state_read_adapters(),
        build_character_manager_side_effect_read_adapters(),
        build_low_risk_state_adapters(),
        build_runtime_command_scheduled_signal_state_adapters(),
        build_enemy_anomaly_state_state_adapters(),
        build_character_manager_side_effect_state_adapters(),
    ):
        adapters.update(group)
    return adapters


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
