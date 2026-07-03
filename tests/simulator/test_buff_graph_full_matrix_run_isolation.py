from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.buff_agents import run_all_apl_zimyuan_parity as parity_tool
from scripts.buff_agents import run_buff_graph_ui_full_matrix as ui_runner


def _manifest(tmp_path: Path, rows=None, run_kind: str = "diagnostic") -> dict:
    return parity_tool.build_matrix_run_manifest(
        old_root=tmp_path / "old",
        new_root=tmp_path / "new",
        stop_tick=120,
        rows_to_run=rows or [parity_tool.MATRIX_ROWS[0]],
        run_kind=run_kind,
        gap_scenario_ids=["gap-a"],
        output_root=tmp_path / "matrix",
        created_at_utc="20260703T010203Z",
        git_commit="abc123",
        candidate_manifest_hash="candidate-hash",
    )


def _phase_receipt(root: Path, manifest: dict, phase_id: str) -> None:
    root.mkdir(parents=True)
    parity_tool._write_phase_receipt(
        output_root=root,
        manifest=manifest,
        phase_id=phase_id,
        summary={"status": "pass", "rows": []},
        phase_metadata={},
    )


def test_matrix_run_manifest_id_uses_timestamp_and_input_hash(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)

    assert manifest["contract_version"] == "2026-07-03.1"
    assert manifest["matrix_run_id"].startswith("20260703T010203Z-")
    assert len(manifest["matrix_run_id"].split("-")[-1]) == 12
    assert manifest["input_hash_payload"]["contract_version"] == manifest["contract_version"]
    assert manifest["input_hash_payload"]["git_commit"] == "abc123"
    assert manifest["input_hash_payload"]["candidate_generated_spec_manifest_hash"] == "candidate-hash"
    assert manifest["rows"][0]["session_id"]
    assert manifest["rows"][0]["rng_seed"] is not None


def test_final_candidate_requires_full_rows_and_gap_scenarios(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="full matrix row set"):
        parity_tool.build_matrix_run_manifest(
            old_root=tmp_path / "old",
            new_root=tmp_path / "new",
            stop_tick=120,
            rows_to_run=[parity_tool.MATRIX_ROWS[0]],
            run_kind="final_candidate",
            gap_scenario_ids=["gap-a"],
        )

    manifest = parity_tool.build_matrix_run_manifest(
        old_root=tmp_path / "old",
        new_root=tmp_path / "new",
        stop_tick=120,
        rows_to_run=parity_tool.MATRIX_ROWS,
        run_kind="final_candidate",
        gap_scenario_ids=["gap-a"],
        created_at_utc="20260703T010203Z",
        git_commit="abc123",
        candidate_manifest_hash="candidate-hash",
    )

    assert manifest["row_count"] == len(parity_tool.MATRIX_ROWS)
    assert manifest["gap_scenario_ids"] == ["gap-a"]


def test_generation_writes_phase_receipt_with_matrix_run_id(
    tmp_path: Path,
    monkeypatch,
) -> None:
    row = parity_tool.MATRIX_ROWS[0]
    manifest = _manifest(tmp_path, rows=[row])
    output_root = tmp_path / "old-baseline"

    def fake_run_one_row(**kwargs):
        return {
            "returncode": 0,
            "artifacts": {artifact: True for artifact in parity_tool.PUBLIC_ARTIFACTS},
            "row_id": kwargs["row"].row_id,
        }

    monkeypatch.setattr(parity_tool, "_run_one_row", fake_run_one_row)

    summary = parity_tool.run_generation(
        mode="old-baseline",
        root=tmp_path / "old",
        output_root=output_root,
        stop_tick=120,
        rows_to_run=[row],
        manifest=manifest,
    )

    receipt = parity_tool.json.loads(
        (output_root / parity_tool.PHASE_RECEIPT_FILENAME).read_text(encoding="utf-8")
    )
    assert summary["completed_count"] == 1
    assert receipt["matrix_run_id"] == manifest["matrix_run_id"]
    assert receipt["phase_id"] == "old-baseline"
    assert receipt["row_ids"] == [row.row_id]


def test_compare_requires_matching_phase_receipts(tmp_path: Path) -> None:
    row = parity_tool.MATRIX_ROWS[0]
    manifest = _manifest(tmp_path, rows=[row])

    with pytest.raises(ValueError, match="missing required phase receipt"):
        parity_tool.compare_outputs(
            baseline_root=tmp_path / "old-baseline",
            candidate_root=tmp_path / "graph-candidate",
            output_root=tmp_path / "comparison",
            strict=True,
            rows_to_run=[row],
            manifest=manifest,
        )


def test_compare_uses_manifest_rows_and_rejects_undeclared_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    row = parity_tool.MATRIX_ROWS[0]
    manifest = _manifest(tmp_path, rows=[row])
    baseline_root = tmp_path / "old-baseline"
    candidate_root = tmp_path / "graph-candidate"
    comparison_root = tmp_path / "comparison"
    _phase_receipt(baseline_root, manifest, "old-baseline")
    _phase_receipt(candidate_root, manifest, "graph-candidate")

    undeclared = next(item for item in parity_tool.MATRIX_ROWS if item.row_id != row.row_id)
    (baseline_root / undeclared.row_id).mkdir()

    with pytest.raises(ValueError, match="undeclared row artifacts"):
        parity_tool.compare_outputs(
            baseline_root=baseline_root,
            candidate_root=candidate_root,
            output_root=comparison_root,
            strict=True,
            manifest=manifest,
        )

    (baseline_root / undeclared.row_id).rmdir()

    def fake_compare_artifact(**kwargs):
        return parity_tool.ArtifactDiff(
            artifact=kwargs["artifact"],
            matches=True,
            baseline_present=True,
            candidate_present=True,
            old_only_sample=[],
            new_only_sample=[],
            changed_sample=[],
        )

    def fake_compare_trace(**kwargs):
        return {
            "matches": True,
            "baseline_present": True,
            "candidate_present": True,
            "baseline": {},
            "candidate": {},
        }

    monkeypatch.setattr(parity_tool, "compare_artifact", fake_compare_artifact)
    monkeypatch.setattr(parity_tool, "compare_trace", fake_compare_trace)

    summary = parity_tool.compare_outputs(
        baseline_root=baseline_root,
        candidate_root=candidate_root,
        output_root=comparison_root,
        strict=True,
        manifest=manifest,
    )

    assert summary["row_count"] == 1
    assert summary["rows"][0]["row_id"] == row.row_id
    assert (comparison_root / parity_tool.PHASE_RECEIPT_FILENAME).exists()


def test_ui_preflight_blocks_final_candidate_without_gap_receipts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        ui_runner,
        "audit_generated_specs",
        lambda: {
            "spec_count": 150,
            "unique_source_xlogic_count": 150,
            "custom_code_node_candidate_count": 0,
            "runtime_status_counts": ui_runner.EXPECTED_GENERATED_SPEC_RUNTIME_STATUS,
            "parity_status_counts": ui_runner.EXPECTED_GENERATED_SPEC_PARITY_STATUS,
            "candidate_only_count": 150,
            "full_parity_verified_count": 0,
            "visual_graph_default_count": 0,
        },
    )
    monkeypatch.setattr(
        ui_runner,
        "audit_materialized_legacy_oracles",
        lambda: {"fixture_count": 150},
    )

    preflight = ui_runner.build_preflight(
        tmp_path / "matrix",
        run_kind="final_candidate",
    )

    assert preflight["run_kind"] == "final_candidate"
    assert preflight["missing_gap_receipts"]
    assert any("gap scenario phase receipts" in blocker for blocker in preflight["blockers"])


def test_ui_execute_does_not_write_final_evidence(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(ui_runner, "FINAL_EVIDENCE_PATH", tmp_path / "final.json")
    monkeypatch.setattr(
        ui_runner,
        "build_preflight",
        lambda output_root, **kwargs: {
            "schema": ui_runner.SCHEMA,
            "campaign_id": ui_runner.CAMPAIGN_ID,
            "blockers": [],
            "manifest": kwargs["manifest"],
            "matrix_run_id": kwargs["manifest"]["matrix_run_id"],
            "run_kind": kwargs["manifest"]["run_kind"],
            "full_parity_verified": False,
        },
    )

    def fake_run(command, cwd):
        return subprocess.CompletedProcess(command, 0, "ok", "")

    monkeypatch.setattr(ui_runner, "_run", fake_run)

    result = ui_runner.execute(
        tmp_path / "matrix",
        allow_blocked=False,
        run_kind="diagnostic",
        row_ids=[parity_tool.MATRIX_ROWS[0].row_id],
        clean_output_root=False,
    )

    assert result["status"] == "blocked_final_evidence_forbidden_in_this_pack"
    assert result["full_parity_verified"] is False
    assert not (tmp_path / "final.json").exists()
