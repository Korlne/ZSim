import json
from pathlib import Path


ROOT = Path(__file__).parents[2]
XLOGIC_ROOT = ROOT / "zsim" / "sim_progress" / "Buff" / "BuffXLogic"
GENERATED_ROOT = ROOT / "zsim" / "sim_progress" / "BuffGraph" / "generated_specs"
MANIFEST_ROOT = GENERATED_ROOT / "remaining-unsupported-patterns"
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "buff_graph" / "generated_specs" / "remaining-unsupported-patterns"


def test_remaining_unsupported_manifest_covers_every_xlogic_without_generated_spec() -> None:
    current_xlogic = _current_non_helper_xlogic_paths()
    generated_sources = _generated_spec_sources()
    manifest = json.loads((MANIFEST_ROOT / "manifest.json").read_text(encoding="utf-8"))
    unsupported_sources = {case["source_xlogic_path"] for case in manifest["unsupported_cases"]}

    assert manifest["status"] == "blocked_by_missing_controlled_blocks"
    assert manifest["runtime_status"] == "legacy_python"
    assert manifest["current_non_helper_xlogic_count"] == len(current_xlogic) == 150
    assert manifest["generated_spec_source_count"] == len(generated_sources & current_xlogic)
    assert manifest["unsupported_case_count"] == len(unsupported_sources)
    assert generated_sources & unsupported_sources == set()
    assert current_xlogic == (generated_sources & current_xlogic) | unsupported_sources
    assert (FIXTURE_ROOT / "manifest.json").read_text(encoding="utf-8") == (
        MANIFEST_ROOT / "manifest.json"
    ).read_text(encoding="utf-8")

    for case in manifest["unsupported_cases"]:
        assert case["legacy_runtime_status"] == "legacy_python"
        assert case["unsupported_pattern_ids"]
        assert case["required_future_block_ids"]
        joined = " ".join(case["unsupported_pattern_ids"] + case["required_future_block_ids"]).lower()
        assert "custom_python" not in joined
        assert "script_node" not in joined
        assert "code_node" not in joined


def _current_non_helper_xlogic_paths() -> set[str]:
    excluded = {"__init__.py", "BasicComplexBuffClass.py", "BackendJudge.py"}
    return {
        path.relative_to(ROOT).as_posix()
        for path in XLOGIC_ROOT.glob("*.py")
        if path.name not in excluded and not path.name.startswith("_")
    }


def _generated_spec_sources() -> set[str]:
    sources: set[str] = set()
    for spec_path in GENERATED_ROOT.glob("*/*.buffgraph.json"):
        payload = json.loads(spec_path.read_text(encoding="utf-8"))
        source = payload.get("source_xlogic_path") or payload.get("spec", {}).get("created_from_xlogic")
        if source:
            sources.add(source)
    return sources
