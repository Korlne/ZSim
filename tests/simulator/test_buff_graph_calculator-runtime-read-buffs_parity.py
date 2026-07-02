import json
from pathlib import Path

from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.migration import import_xlogic_to_graph
from zsim.sim_progress.BuffGraph.spec import OwnerKind


FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "buff_graph" / "calculator-runtime-read-buffs"


def test_calculator_runtime_read_xlogic_requires_controlled_reader_blocks() -> None:
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


def test_calculator_runtime_read_conversion_truth_tables_are_fixed() -> None:
    fixture = json.loads((FIXTURE_ROOT / "conversion-truth-tables.json").read_text(encoding="utf-8"))

    for table in fixture["tables"]:
        assert "custom" not in table["future_block_reason"].lower()
        for row in table["rows"]:
            expected = _evaluate_formula(table["formula_id"], row)
            assert row["expected_output"] == expected


def test_calculator_runtime_read_wave_preserves_future_block_vocabulary() -> None:
    fixture = json.loads((FIXTURE_ROOT / "unsupported-cases.json").read_text(encoding="utf-8"))
    observed = {
        block
        for case in fixture["cases"]
        for block in case["required_future_block_ids"]
    }

    assert {
        "read.calculator_attribute",
        "read.enemy_context",
        "condition.numeric_compare",
        "compose.numeric_formula",
        "effect.start_buff",
        "effect.update_buff_count",
    }.issubset(observed)
    assert all("python" not in block and "script" not in block and "code" not in block for block in observed)


def _evaluate_formula(formula_id: str, row: dict[str, object]) -> dict[str, object]:
    if formula_id == "alice_am_to_ap_count":
        anomaly_mastery = float(row["anomaly_mastery"])
        if anomaly_mastery < 140:
            return {"active": False, "count": 0}
        return {"active": True, "count": (anomaly_mastery - 140) * 1.6}
    if formula_id == "qingyi_impact_to_atk_count":
        impact = float(row["impact"])
        max_count = float(row["max_count"])
        return {"active": True, "count": min((impact - 120) * 6, max_count)}
    if formula_id == "yuzuha_am_to_buildup_count":
        anomaly_mastery = float(row["anomaly_mastery"])
        cinema_1_ratio = float(row["cinema_1_ratio"])
        if anomaly_mastery < 100:
            return {"active": False, "count": 0}
        return {"active": True, "count": min(anomaly_mastery - 100, 100) * cinema_1_ratio}
    raise AssertionError(f"Unknown formula_id: {formula_id}")
