import json
from pathlib import Path

from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.migration import import_xlogic_to_graph
from zsim.sim_progress.BuffGraph.spec import OwnerKind


FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "buff_graph" / "runtime-command-scheduled-producers"


def test_runtime_command_scheduled_xlogic_requires_controlled_port_blocks() -> None:
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

        actual_pattern_ids = {pattern.pattern_id for pattern in import_result.unsupported_patterns}
        required_pattern_ids = set(case["expected_unsupported_pattern_ids"])
        optional_pattern_ids = set(case.get("optional_unsupported_pattern_ids", []))

        assert import_result.imported is False
        assert import_result.spec is None
        assert required_pattern_ids.issubset(actual_pattern_ids)
        assert actual_pattern_ids.issubset(required_pattern_ids | optional_pattern_ids)
        assert tuple(case["expected_block_hints"]["triggers"]) == import_result.classification.triggers
        assert tuple(case["expected_block_hints"]["conditions"]) == import_result.classification.conditions
        assert tuple(case["expected_block_hints"]["reads"]) == import_result.classification.reads
        assert tuple(case["expected_block_hints"]["state"]) == import_result.classification.state
        assert tuple(case["expected_block_hints"]["effects"]) == import_result.classification.effects


def test_runtime_command_contracts_are_anchored_to_current_xlogic() -> None:
    fixture = json.loads((FIXTURE_ROOT / "producer-contracts.json").read_text(encoding="utf-8"))

    for contract in fixture["contracts"]:
        source = Path(contract["xlogic_path"]).read_text(encoding="utf-8")
        for anchor in contract["source_anchors"]:
            assert anchor in source
        assert contract["status"] == "requires_future_building_block"
        assert "custom" not in contract["future_block_reason"].lower()


def test_runtime_command_wave_preserves_protected_port_vocabulary() -> None:
    cases = json.loads((FIXTURE_ROOT / "unsupported-cases.json").read_text(encoding="utf-8"))
    contracts = json.loads((FIXTURE_ROOT / "producer-contracts.json").read_text(encoding="utf-8"))

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
        "effect.publish_resource_refresh",
        "effect.emit_scheduled_event",
        "effect.spawn_planned_skill_node",
        "effect.issue_allowed_runtime_command",
        "condition.hit_frame",
        "condition.skill_tag_in",
    }.issubset(observed)
    assert all("python" not in block and "script" not in block and "code" not in block for block in observed)
