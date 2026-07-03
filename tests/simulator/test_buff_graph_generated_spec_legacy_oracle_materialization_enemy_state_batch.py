from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from zsim.api_src.models.buff_graph import BuffGraphSpecModel
from zsim.api_src.services.buff_graph_service import _candidate_harness_adapters
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.runtime.compiler import compile_buff_graph_spec
from zsim.sim_progress.BuffGraph.runtime.executor import execute_compiled_buff_graph
from zsim.sim_progress.BuffGraph.runtime.parity import (
    BuffGraphCandidateParityOracle,
    run_buff_graph_candidate_parity,
)
from zsim.sim_progress.BuffGraph.spec import RuntimeStatus


GENERATED_DIR = Path("zsim/sim_progress/BuffGraph/generated_specs/enemy-state-edge-triggers")
ORACLE_ROOT = Path("tests/fixtures/buff_graph/generated-spec-legacy-oracles")


def test_enemy_state_generated_spec_legacy_oracle_batch_is_complete_and_consumable() -> None:
    wrappers = _generated_specs()
    registry = build_default_block_registry()
    adapters = _candidate_harness_adapters()

    assert len(wrappers) == 32

    for spec_path, wrapper in wrappers:
        spec = BuffGraphSpecModel.model_validate(wrapper["spec"]).to_domain()
        fixture_path = ORACLE_ROOT / f"{spec.graph_id}-legacy-oracle.json"

        assert fixture_path.exists(), spec.graph_id
        fixture = _read_json(fixture_path)
        assert fixture["schema"] == "zsim-buffgraph-generated-spec-legacy-oracle.v1"
        assert fixture["source_generated_spec"] == spec_path.as_posix()
        assert fixture["source_xlogic_path"] == wrapper["source_xlogic_path"]
        assert fixture["graph_id"] == spec.graph_id
        assert fixture["migration_wave"] == "enemy-state-edge-triggers"
        assert fixture["parity_status"] == "legacy_oracle_materialized_only"
        assert fixture["full_parity_verified"] is False
        assert fixture["legacy_oracle"] == "legacy_python_collected"

        assert spec.runtime_status == RuntimeStatus.LEGACY_PYTHON
        assert spec.parity_metadata["parity_status"] == "not_run"

        expected = fixture["legacy_oracle_result"]
        execution = _execute_graph_candidate(spec)
        assert execution["expected_final_output"] == expected["expected_final_output"]
        assert execution["expected_trace_kind_checkpoint"] == expected[
            "expected_trace_kind_checkpoint"
        ]

        parity = run_buff_graph_candidate_parity(
            replace(spec, runtime_status=RuntimeStatus.VISUAL_GRAPH_CANDIDATE),
            block_registry=registry,
            adapters=adapters,
            tick=int(fixture["tick"]),
            prepared_context={},
            oracle=BuffGraphCandidateParityOracle(
                case_id=fixture["case_id"],
                expected_final_output=expected["expected_final_output"],
                expected_trace_kind_checkpoint=expected["expected_trace_kind_checkpoint"],
                legacy_oracle=expected["legacy_oracle"],
            ),
        )
        assert parity.passed, (spec.graph_id, parity.errors)
        assert parity.output_passed is True
        assert parity.trace_checkpoint_passed is True
        assert parity.runtime_status == RuntimeStatus.VISUAL_GRAPH_CANDIDATE.value


def _generated_specs() -> list[tuple[Path, dict]]:
    return [(path, _read_json(path)) for path in sorted(GENERATED_DIR.glob("*.buffgraph.json"))]


def _execute_graph_candidate(spec) -> dict:
    registry = build_default_block_registry()
    compile_result = compile_buff_graph_spec(spec, block_registry=registry)
    assert compile_result.passed
    assert compile_result.compiled is not None
    execution = execute_compiled_buff_graph(
        compile_result.compiled,
        adapters=_candidate_harness_adapters(),
        tick=600,
        prepared_context={},
    )
    assert execution.passed
    return {
        "expected_final_output": json.loads(
            json.dumps(execution.outputs, ensure_ascii=False)
        ),
        "expected_trace_kind_checkpoint": [
            [event.kind.value, event.checkpoint] for event in execution.trace.events
        ],
    }


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
