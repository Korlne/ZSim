import json
from pathlib import Path

from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.migration import import_xlogic_to_graph
from zsim.sim_progress.BuffGraph.spec import OwnerKind


FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "buff_graph" / "enemy-state-edge-triggers"


def test_enemy_state_edge_xlogic_is_preserved_as_unsupported_until_blocks_exist() -> None:
    fixture = json.loads((FIXTURE_ROOT / "unsupported-cases.json").read_text(encoding="utf-8"))
    registry = build_default_block_registry()

    for case in fixture["cases"]:
        xlogic_path = Path(case["xlogic_path"])
        import_result = import_xlogic_to_graph(
            xlogic_path=case["xlogic_path"],
            source=xlogic_path.read_text(encoding="utf-8"),
            owner_kind=OwnerKind(case["owner_kind"]),
            owner_name=case["owner_name"],
            source_buff_index=case["source_buff_index"],
            block_registry=registry,
        )

        assert import_result.imported is False
        assert import_result.spec is None
        assert {pattern.pattern_id for pattern in import_result.unsupported_patterns} == set(
            case["expected_unsupported_pattern_ids"]
        )
        assert tuple(case["expected_block_hints"]["triggers"]) == import_result.classification.triggers
        assert tuple(case["expected_block_hints"]["conditions"]) == import_result.classification.conditions
        assert tuple(case["expected_block_hints"]["reads"]) == import_result.classification.reads
        assert tuple(case["expected_block_hints"]["state"]) == import_result.classification.state
        assert tuple(case["expected_block_hints"]["effects"]) == import_result.classification.effects


def test_enemy_state_edge_truth_tables_record_future_adapter_oracles() -> None:
    fixture = json.loads((FIXTURE_ROOT / "edge-truth-tables.json").read_text(encoding="utf-8"))

    assert fixture["tables"]
    for table in fixture["tables"]:
        assert "custom" not in table["future_block_reason"].lower()
        for row in table["rows"]:
            expected = row["previous_active"] is True and row["current_active"] is False
            assert row["expected_exit"] is expected


def test_enemy_state_edge_wave_preserves_candidate_breadth() -> None:
    fixture = json.loads((FIXTURE_ROOT / "unsupported-cases.json").read_text(encoding="utf-8"))

    expected_future_blocks = {
        "read.enemy_anomaly_state",
        "read.enemy_edge_state",
        "read.dot_runtime_state",
        "state.edge_memory",
        "condition.enemy_state",
        "condition.edge_transition",
    }
    observed = {
        block
        for case in fixture["cases"]
        for block in case["required_future_block_ids"]
    }

    assert expected_future_blocks.issubset(observed)
    assert all("python" not in block and "script" not in block and "code" not in block for block in observed)
