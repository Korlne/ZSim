import json
from pathlib import Path

from zsim.api_src.models.buff_graph import BuffGraphSpecModel
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.runtime.compiler import compile_buff_graph_spec
from zsim.sim_progress.BuffGraph.spec import RuntimeStatus, validate_buff_graph_spec


ROOT = Path(__file__).parents[2]
SPEC_ROOT = (
    ROOT
    / "zsim"
    / "sim_progress"
    / "BuffGraph"
    / "generated_specs"
    / "runtime-command-scheduled-producers"
)
FIXTURE_ROOT = (
    ROOT
    / "tests"
    / "fixtures"
    / "buff_graph"
    / "generated_specs"
    / "runtime-command-scheduled-producers"
)
REMAINING_ROOT = (
    ROOT
    / "zsim"
    / "sim_progress"
    / "BuffGraph"
    / "generated_specs"
    / "remaining-unsupported-patterns"
)


def test_runtime_scheduled_unblocked_generated_specs_validate_compile_and_mirror() -> None:
    manifest = json.loads((SPEC_ROOT / "manifest.json").read_text(encoding="utf-8"))

    assert manifest["status"] == "generated_candidate_partial"
    assert manifest["runtime_status"] == "legacy_python"
    assert manifest["generated_spec_count"] == 26
    assert manifest["blocked_false_positive_count"] == 0
    assert manifest["blocked_case_count"] == 11
    assert (FIXTURE_ROOT / "manifest.json").read_text(encoding="utf-8") == (
        SPEC_ROOT / "manifest.json"
    ).read_text(encoding="utf-8")

    registry = build_default_block_registry()
    registry_block_ids = {block.block_id for block in registry.all()}
    for spec_file in manifest["generated_specs"]:
        production_payload = json.loads((SPEC_ROOT / spec_file).read_text(encoding="utf-8"))
        fixture_payload = json.loads((FIXTURE_ROOT / spec_file).read_text(encoding="utf-8"))
        assert fixture_payload == production_payload

        spec = BuffGraphSpecModel.model_validate(production_payload["spec"]).to_domain()
        assert spec.runtime_status is RuntimeStatus.LEGACY_PYTHON
        assert spec.created_from_xlogic == production_payload["source_xlogic_path"]
        assert spec.parity_metadata["parity_status"] == "not_run"
        assert validate_buff_graph_spec(spec) == ()

        block_ids = {node.block_id for node in spec.nodes}
        assert {
            "effect.issue_runtime_command",
            "effect.emit_scheduled_event",
            "condition.tick_window",
            "read.skill_node",
            "state.scheduled_signal",
        } <= block_ids
        assert block_ids <= registry_block_ids

        compile_result = compile_buff_graph_spec(spec, block_registry=registry)
        assert compile_result.passed is True
        assert all("code" not in node.block_id.lower() for node in spec.nodes)
        assert all("python" not in node.block_id.lower() for node in spec.nodes)
        assert all("script" not in node.block_id.lower() for node in spec.nodes)


def test_runtime_scheduled_generated_sources_are_removed_from_remaining_unsupported_manifest() -> None:
    runtime_manifest = json.loads((SPEC_ROOT / "manifest.json").read_text(encoding="utf-8"))
    remaining_manifest = json.loads((REMAINING_ROOT / "manifest.json").read_text(encoding="utf-8"))
    generated_sources = {
        json.loads((SPEC_ROOT / spec_file).read_text(encoding="utf-8"))["source_xlogic_path"]
        for spec_file in runtime_manifest["generated_specs"]
    }
    remaining_sources = {
        case["source_xlogic_path"] for case in remaining_manifest["unsupported_cases"]
    }

    assert remaining_manifest["current_non_helper_xlogic_count"] == 150
    assert remaining_manifest["generated_spec_source_count"] >= len(generated_sources)
    assert remaining_manifest["unsupported_case_count"] == len(remaining_sources)
    assert generated_sources.isdisjoint(remaining_sources)
