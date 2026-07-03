from __future__ import annotations

import json
from pathlib import Path

import pytest


FIXTURE_PATH = (
    Path(__file__).parents[1]
    / "fixtures"
    / "buff_graph"
    / "yuzuha-additional-ability-count-semantics"
    / "timeline-oracle.json"
)


def test_yuzuha_additional_ability_timeline_oracle_captures_legacy_public_contract() -> None:
    fixture = _read_json(FIXTURE_PATH)

    assert fixture["schema"] == (
        "zsim-buffgraph-yuzuha-additional-ability-count-semantics.v1"
    )
    assert fixture["public_timeline_contract"]["normalization_allowed"] is False
    assert fixture["public_timeline_contract"]["comparison_tolerance_allowed"] is False

    observed_tasks = {case["task"] for case in fixture["observed_scenarios"]}
    assert observed_tasks == {
        "Buff-角色-柚叶-组队被动-属性异常与紊乱伤害增幅",
        "Buff-角色-柚叶-组队被动-积蓄值增幅",
    }

    for case in fixture["observed_scenarios"]:
        expected_raw = min(case["anomaly_mastery"] - 100, 100) * case["cinema_1_ratio"]
        assert case["legacy_raw_count"] == pytest.approx(expected_raw)

        # The matrix compares public timeline values, not the raw float before
        # legacy Buff timeline serialization.
        assert case["legacy_public_timeline_value"] == float(int(expected_raw))
        assert case["graph_candidate_observed_value"] == pytest.approx(expected_raw)
        assert case["graph_candidate_observed_value"] != case["legacy_public_timeline_value"]


def test_yuzuha_count_oracle_points_to_both_generated_specs_without_code_nodes() -> None:
    fixture = _read_json(FIXTURE_PATH)

    graph_ids = {spec["graph_id"] for spec in fixture["generated_specs"]}
    assert graph_ids == {
        "yuzuha-additional-ability-anomaly-buildup-bonus",
        "yuzuha-additional-ability-anomaly-dmg-bonus",
    }

    for spec_ref in fixture["generated_specs"]:
        wrapper = _read_json(Path(spec_ref["path"]))
        spec = wrapper["spec"]
        assert spec["graph_id"] == spec_ref["graph_id"]
        assert spec["created_from_xlogic"] in fixture["legacy_xlogic_paths"]
        assert spec["runtime_status"] == "visual_graph_candidate"
        assert spec["parity_metadata"]["full_parity_verified"] is False
        assert all(node["block_id"] != "custom.python" for node in spec["nodes"])
        assert all("code" not in node["block_id"] for node in spec["nodes"])

    serialized_specs = "\n".join(
        Path(spec_ref["path"]).read_text(encoding="utf-8")
        for spec_ref in fixture["generated_specs"]
    )
    assert "legacy_source_review_required" in serialized_specs


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
