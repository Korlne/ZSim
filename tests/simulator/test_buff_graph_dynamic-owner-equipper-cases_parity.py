import json
from pathlib import Path

from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.migration import import_xlogic_to_graph
from zsim.sim_progress.BuffGraph.spec import OwnerKind


FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "buff_graph" / "dynamic-owner-equipper-cases"


def test_dynamic_owner_importer_surface_graphs_do_not_claim_prepared_context_parity() -> None:
    fixture = json.loads((FIXTURE_ROOT / "surface-import-cases.json").read_text(encoding="utf-8"))
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

        actual_pattern_ids = {pattern.pattern_id for pattern in import_result.unsupported_patterns}
        assert import_result.imported is case["expected_current_imported"]
        assert tuple(case["expected_block_hints"]["triggers"]) == import_result.classification.triggers
        assert tuple(case["expected_block_hints"]["conditions"]) == import_result.classification.conditions
        assert tuple(case["expected_block_hints"]["reads"]) == import_result.classification.reads
        assert tuple(case["expected_block_hints"]["state"]) == import_result.classification.state
        assert tuple(case["expected_block_hints"]["effects"]) == import_result.classification.effects

        if case["expected_current_imported"]:
            assert import_result.spec is not None
            current_blocks = {node.block_id for node in import_result.spec.nodes}
            missing_semantic_blocks = set(case["required_future_block_ids"]) - current_blocks
            assert missing_semantic_blocks == set(case["required_future_block_ids"])
        else:
            assert import_result.spec is None
            assert set(case["expected_unsupported_pattern_ids"]).issubset(actual_pattern_ids)
            assert actual_pattern_ids.issubset(
                set(case["expected_unsupported_pattern_ids"])
                | set(case.get("optional_unsupported_pattern_ids", []))
            )


def test_dynamic_owner_contracts_are_anchored_to_current_xlogic() -> None:
    fixture = json.loads((FIXTURE_ROOT / "prepared-context-contracts.json").read_text(encoding="utf-8"))

    for contract in fixture["contracts"]:
        source = Path(contract["xlogic_path"]).read_text(encoding="utf-8")
        for anchor in contract["source_anchors"]:
            assert anchor in source
        assert contract["status"] == "requires_future_building_block"
        assert "custom" not in contract["future_block_reason"].lower()


def test_dynamic_owner_wave_preserves_prepared_context_vocabulary() -> None:
    cases = json.loads((FIXTURE_ROOT / "surface-import-cases.json").read_text(encoding="utf-8"))
    contracts = json.loads((FIXTURE_ROOT / "prepared-context-contracts.json").read_text(encoding="utf-8"))

    observed = {
        block
        for case in cases["cases"]
        for block in case["required_future_block_ids"]
    } | {
        block
        for contract in contracts["contracts"]
        for block in contract["required_future_block_ids"]
    }

    assert {
        "read.prepared_equipper",
        "read.prepared_owner",
        "read.prepared_template_buff",
        "read.trigger_buff_state",
        "read.active_buffs_for_equipper",
        "condition.equipper_identity",
        "condition.trigger_buff_active",
        "condition.trigger_buff_count_compare",
        "effect.bind_prepared_record",
        "effect.update_template_buff",
        "effect.register_listener",
        "read.listener_signal",
        "effect.consume_listener_signal",
    }.issubset(observed)
    assert all("python" not in block and "script" not in block and "code" not in block for block in observed)
