from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from typing import Literal

import polars as pl
import pytest

from zsim.utils import main_loop_consistency as mlc
from zsim.utils.main_loop_consistency import (
    RuntimeSnapshot,
    build_consistency_report,
    build_parser,
    run_main_loop_consistency,
)
from zsim.utils.process_buff_result import _prepare_buff_timeline_data
from zsim.utils.process_dmg_result import _normalize_damage_schema, sort_df_by_UUID

from tests.teams import auto_register_teams

_DAMAGE_GOLDEN_DIR = Path("tests/fixtures/external_golden_parity/damage-golden")
_BUFF_CSV_GOLDEN_DIR = Path("tests/fixtures/external_golden_parity/buff-csv-golden")
_BUFF_JSON_GOLDEN_DIR = Path("tests/fixtures/external_golden_parity/buff-json-golden")
_MATCHING_DAMAGE_CSV = """tick,skill_tag,element_type,dmg_expect,dmg_crit,stun,buildup,is_anomaly,is_disorder,UUID
1,alpha,0,10.0,11.0,1.0,0.5,false,false,uuid-1
2,beta,4,20.0,22.0,2.0,1.5,true,false,uuid-2
3,beta,4,5.0,6.0,0.5,0.2,true,true,uuid-2
"""
_MATCHING_ATTRIBUTION = {
    "alpha": {"direct_damage": 10.0, "anomaly_damage": 0.0},
    "beta": {"direct_damage": 0.0, "anomaly_damage": 25.0},
}
_MATCHING_BUFF_TIMELINE_CSV = """time_tick,buff-a,buff-b
1,0,
2,2.0,1.5
3,2.0,0
"""
_MISMATCH_BUFF_TIMELINE_CSV = """time_tick,buff-a,buff-c
1,0,
2,2.5,4.0
3,2.5,4.0
"""
_MATCHING_BUFF_TIMELINE_JSON = {
    "alpha": [
        {"Task": "buff-a", "Start": 2, "Finish": 3, "Value": 2.0},
        {"Task": "buff-b", "Start": 2, "Finish": 2, "Value": 1.5},
    ]
}


def _write_result_dir(
    result_dir: Path,
    *,
    damage_csv: str | None = _MATCHING_DAMAGE_CSV,
    damage_attribution: dict[str, Any] | None = _MATCHING_ATTRIBUTION,
    buff_timeline_json: dict[str, Any] | None = None,
    buff_csvs: dict[str, str] | None = None,
) -> Path:
    result_dir.mkdir(parents=True, exist_ok=True)
    if damage_csv is not None:
        (result_dir / "damage.csv").write_text(damage_csv, encoding="utf-8")
    if damage_attribution is not None:
        (result_dir / "damage_attribution.json").write_text(
            json.dumps(damage_attribution, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if buff_timeline_json is not None or buff_csvs is not None:
        buff_log_dir = result_dir / "buff_log"
        buff_log_dir.mkdir(parents=True, exist_ok=True)
        if buff_timeline_json is not None:
            (buff_log_dir / "buff_timeline_data.json").write_text(
                json.dumps(buff_timeline_json, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        for source, csv_text in (buff_csvs or {}).items():
            (buff_log_dir / f"{source}.csv").write_text(csv_text, encoding="utf-8")
    return result_dir


def _build_external_damage_report(
    *,
    golden_result_dir: Path,
    candidate_result_path: Path,
) -> dict[str, Any]:
    return mlc.build_external_golden_parity_report(
        golden_result_dir=golden_result_dir,
        candidate_session_id="candidate-damage",
        candidate_result_path=candidate_result_path,
        run_config_identity={
            "kind": "team",
            "team": "fixture-team",
            "common_cfg_path": None,
            "source_session_id": "fixture-source",
        },
        apl="./fixture.toml",
        stop_tick=9,
    )


def test_build_consistency_report_keeps_required_json_fields():
    legacy_snapshot = RuntimeSnapshot(
        runtime_label="default-current",
        session_id="1",
        total_damage=123.4,
        event_counts={
            "total": 2,
            "anomaly_total": 1,
            "disorder_total": 0,
            "by_skill_tag": {"alpha": 1, "beta": 1},
            "by_skill_name": {"Alpha": 1, "Beta": 1},
            "by_element_type": {"1": 2},
        },
        buff_timeline={
            "alpha": [
                {"Task": "buff-a", "Start": 1, "Finish": 3, "Value": 1.0},
            ]
        },
    )
    candidate_snapshot = RuntimeSnapshot(
        runtime_label="candidate",
        session_id="2",
        total_damage=130.0,
        event_counts={
            "total": 3,
            "anomaly_total": 1,
            "disorder_total": 1,
            "by_skill_tag": {"alpha": 1, "beta": 2},
            "by_skill_name": {"Alpha": 1, "Beta": 2},
            "by_element_type": {"1": 2, "3": 1},
        },
        buff_timeline={
            "alpha": [
                {"Task": "buff-a", "Start": 1, "Finish": 3, "Value": 1.0},
                {"Task": "buff-b", "Start": 5, "Finish": 6, "Value": 2.0},
            ]
        },
    )

    report = build_consistency_report(
        team="team-a",
        apl="./zsim/data/APLData/example.toml",
        stop_tick=120,
        legacy_snapshot=legacy_snapshot,
        candidate_snapshot=candidate_snapshot,
    )

    assert report["team"] == "team-a"
    assert report["apl"] == "./zsim/data/APLData/example.toml"
    assert report["runtime_selection"]["mode"] == "label-only-current-runtime"
    assert report["baseline_runtime"] == "default-current"
    assert report["legacy_runtime"] == "default-current"
    assert report["report_compatibility"]["legacy_runtime"] == "alias for baseline_runtime"
    assert report["total_damage"] == {
        "baseline": 123.4,
        "legacy": 123.4,
        "candidate": 130.0,
    }
    assert report["event_counts"]["baseline"]["by_skill_tag"] == {"alpha": 1, "beta": 1}
    assert report["event_counts"]["legacy"]["by_skill_tag"] == {"alpha": 1, "beta": 1}
    assert report["buff_timeline"]["candidate"]["alpha"][1]["Task"] == "buff-b"
    assert report["differences"]["total_damage"] == 6.6
    assert report["differences"]["event_counts"]["total"] == 1
    assert report["differences"]["event_counts"]["disorder_total"] == 1
    assert report["differences"]["buff_timeline"]["candidate_only_count"] == 1
    assert report["differences"]["matches"] is False


def test_buff_timeline_processing_keeps_public_cache_record_keys():
    timeline = _prepare_buff_timeline_data(
        pl.DataFrame(
            {
                "time_tick": [1, 2, 3],
                "buff-a": [0.0, 2.0, 2.0],
                "buff-b": [None, 1.5, 0.0],
            }
        )
    )

    assert [tuple(entry) for entry in timeline] == [
        ("Task", "Start", "Finish", "Value"),
        ("Task", "Start", "Finish", "Value"),
    ]
    assert timeline == [
        {"Task": "buff-a", "Start": 2, "Finish": 3, "Value": 2.0},
        {"Task": "buff-b", "Start": 2, "Finish": 2, "Value": 1.5},
    ]


def test_build_parser_accepts_required_cli_flags():
    parser = build_parser()

    args = parser.parse_args(
        [
            "--team",
            "team-a",
            "--apl",
            "./zsim/data/APLData/example.toml",
            "--baseline-runtime",
            "default-a",
            "--candidate-runtime",
            "candidate-b",
            "--json",
        ]
    )
    compat_args = parser.parse_args(
        [
            "--team",
            "team-a",
            "--legacy-runtime",
            "legacy-a",
            "--candidate-runtime",
            "candidate-b",
        ]
    )
    flagged_args = parser.parse_args(
        [
            "--team",
            "team-a",
            "--candidate-use-indexed-buff-load-loop",
        ]
    )
    multi_team_args = parser.parse_args(
        [
            "--teams",
            "team-a",
            "team-b",
            "team-c",
            "--stop-ticks",
            "120",
            "600",
            "--summary-json",
            "scripts/ralph/benchmarks/summary.json",
            "--candidate-use-indexed-buff-load-loop",
        ]
    )

    assert args.team == "team-a"
    assert args.apl == "./zsim/data/APLData/example.toml"
    assert args.baseline_runtime == "default-a"
    assert args.candidate_runtime == "candidate-b"
    assert args.json is True
    assert compat_args.baseline_runtime == "legacy-a"
    assert not hasattr(args, "legacy_runtime")
    assert args.candidate_use_indexed_buff_load_loop is False
    assert flagged_args.candidate_use_indexed_buff_load_loop is True
    assert multi_team_args.teams == ["team-a", "team-b", "team-c"]
    assert multi_team_args.stop_ticks == [120, 600]
    assert multi_team_args.summary_json == "scripts/ralph/benchmarks/summary.json"
    assert multi_team_args.candidate_use_indexed_buff_load_loop is True
    help_text = parser.format_help()
    assert "--baseline-runtime" in help_text
    assert "Compatibility alias for --baseline-runtime" in help_text
    assert "not old runtime selection" in help_text


def test_external_golden_parser_accepts_required_cli_flags():
    parser = mlc.build_external_golden_parser()

    team_args = parser.parse_args(
        [
            "--golden-result-dir",
            "tests/fixtures/external_golden_parity/minimal-golden",
            "--team",
            "team-a",
            "--apl",
            "./zsim/data/APLData/example.toml",
            "--stop-tick",
            "25",
            "--output-json",
            "scripts/ralph/artifacts/external-golden.json",
        ]
    )
    common_cfg_args = parser.parse_args(
        [
            "--golden-result-dir",
            "tests/fixtures/external_golden_parity/minimal-golden",
            "--common-cfg",
            "common-cfg.json",
            "--output-json",
            "scripts/ralph/artifacts/external-golden.json",
        ]
    )

    assert team_args.golden_result_dir == "tests/fixtures/external_golden_parity/minimal-golden"
    assert team_args.team == "team-a"
    assert team_args.common_cfg is None
    assert team_args.apl == "./zsim/data/APLData/example.toml"
    assert team_args.stop_tick == 25
    assert team_args.output_json == "scripts/ralph/artifacts/external-golden.json"
    assert common_cfg_args.team is None
    assert common_cfg_args.common_cfg == "common-cfg.json"
    with pytest.raises(SystemExit) as missing_config:
        parser.parse_args(
            [
                "--golden-result-dir",
                "tests/fixtures/external_golden_parity/minimal-golden",
                "--output-json",
                "scripts/ralph/artifacts/external-golden.json",
            ]
        )
    with pytest.raises(SystemExit) as ambiguous_config:
        parser.parse_args(
            [
                "--golden-result-dir",
                "tests/fixtures/external_golden_parity/minimal-golden",
                "--team",
                "team-a",
                "--common-cfg",
                "common-cfg.json",
                "--output-json",
                "scripts/ralph/artifacts/external-golden.json",
            ]
        )
    assert missing_config.value.code == 2
    assert ambiguous_config.value.code == 2


def test_external_golden_matrix_parser_accepts_config_and_row_json():
    parser = mlc.build_external_golden_matrix_parser()

    config_args = parser.parse_args(
        [
            "--matrix-config",
            "tests/fixtures/external_golden_parity/fixture-matrix.json",
            "--output-json",
            "scripts/ralph/artifacts/external-golden-matrix.json",
        ]
    )
    row_args = parser.parse_args(
        [
            "--row-json",
            '{"row_id":"row-a"}',
            "--row-json",
            '{"row_id":"row-b"}',
            "--output-json",
            "scripts/ralph/artifacts/external-golden-matrix.json",
        ]
    )

    assert config_args.matrix_config == "tests/fixtures/external_golden_parity/fixture-matrix.json"
    assert config_args.row_json is None
    assert row_args.matrix_config is None
    assert row_args.row_json == ['{"row_id":"row-a"}', '{"row_id":"row-b"}']
    with pytest.raises(SystemExit) as missing_source:
        parser.parse_args(
            [
                "--output-json",
                "scripts/ralph/artifacts/external-golden-matrix.json",
            ]
        )
    with pytest.raises(SystemExit) as ambiguous_source:
        parser.parse_args(
            [
                "--matrix-config",
                "matrix.json",
                "--row-json",
                '{"row_id":"row-a"}',
                "--output-json",
                "scripts/ralph/artifacts/external-golden-matrix.json",
            ]
        )
    assert missing_source.value.code == 2
    assert ambiguous_source.value.code == 2


def _fixture_matrix_row(**overrides: Any) -> dict[str, Any]:
    row = {
        "row_id": "fixture-row",
        "row_kind": "fixture",
        "golden_result_dir": "tests/fixtures/external_golden_parity/buff-csv-golden",
        "run_config": {"team": "fake-team"},
        "apl": "./fixture.toml",
        "stop_tick": 9,
        "expected_domains": ["buff_timeline"],
        "tolerance_policy": {
            "damage_total_abs": 0.0,
            "damage_row_abs": 0.0,
            "damage_attribution_abs": 0.0,
            "buff_timeline": "exact-normalized",
        },
        "signoff_label": "base-parity",
        "missing_input_policy": "block",
    }
    row.update(overrides)
    return row


def test_run_external_golden_matrix_writes_pass_summary(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    candidate_dir = _write_result_dir(
        tmp_path / "candidate-result",
        damage_csv=None,
        damage_attribution=None,
        buff_csvs={"alpha": _MATCHING_BUFF_TIMELINE_CSV},
    )
    report = _build_external_damage_report(
        golden_result_dir=_BUFF_CSV_GOLDEN_DIR,
        candidate_result_path=candidate_dir,
    )
    captured_calls: list[dict[str, Any]] = []

    def fake_run_external_golden_parity(**kwargs: Any) -> dict[str, Any]:
        captured_calls.append(kwargs)
        return report

    monkeypatch.setattr(mlc, "run_external_golden_parity", fake_run_external_golden_parity)
    output_path = tmp_path / "external-golden-matrix.json"

    summary = mlc.run_external_golden_matrix(
        rows=[_fixture_matrix_row()],
        output_path=output_path,
    )

    assert len(captured_calls) == 1
    captured_call = dict(captured_calls[0])
    captured_call["golden_result_dir"] = captured_call["golden_result_dir"].replace("\\", "/")
    assert captured_call == {
        "golden_result_dir": "tests/fixtures/external_golden_parity/buff-csv-golden",
        "team": "fake-team",
        "common_cfg": None,
        "apl": "./fixture.toml",
        "stop_tick": 9,
    }
    assert summary["schema"] == mlc.EXTERNAL_GOLDEN_MATRIX_SCHEMA
    assert summary["schema_version"] == 1
    assert summary["row_schema"] == mlc.EXTERNAL_GOLDEN_MATRIX_ROW_SCHEMA
    assert summary["row_count"] == 1
    assert summary["counts"] == {"pass": 1, "fail": 0, "skip": 0, "blocked": 0}
    assert summary["fixture_only_signoff"] is True
    row = summary["rows"][0]
    assert row["schema"] == mlc.EXTERNAL_GOLDEN_MATRIX_ROW_SCHEMA
    assert row["status"] == "pass"
    assert row["config_identity"]["kind"] == "team"
    assert row["diff_domain_status"]["buff_timeline"] == {
        "expected": True,
        "implemented": True,
        "status": "match",
        "matches": True,
    }
    assert row["diff_domain_status"]["damage"]["expected"] is False
    assert row["mismatch_samples"] == {}
    artifact = json.loads(output_path.read_text(encoding="utf-8"))
    assert artifact == summary


def test_run_external_golden_matrix_blocks_missing_golden_dir(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    captured_calls: list[dict[str, Any]] = []
    monkeypatch.setattr(
        mlc,
        "run_external_golden_parity",
        lambda **kwargs: captured_calls.append(kwargs),
    )

    summary = mlc.run_external_golden_matrix(
        rows=[
            _fixture_matrix_row(
                row_id="missing-golden",
                golden_result_dir=str(tmp_path / "missing-golden"),
            )
        ],
    )

    assert captured_calls == []
    assert summary["counts"] == {"pass": 0, "fail": 0, "skip": 0, "blocked": 1}
    assert summary["signoff_status"] == "blocked"
    row = summary["rows"][0]
    assert row["status"] == "blocked"
    assert row["reason_code"] == "missing-golden-result-dir"
    assert row["diff_domain_status"] == {}


def test_run_external_golden_matrix_reports_bounded_row_failure_samples(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    candidate_dir = _write_result_dir(
        tmp_path / "candidate-result",
        damage_csv=None,
        damage_attribution=None,
        buff_csvs={"alpha": _MISMATCH_BUFF_TIMELINE_CSV},
    )
    report = _build_external_damage_report(
        golden_result_dir=_BUFF_CSV_GOLDEN_DIR,
        candidate_result_path=candidate_dir,
    )
    monkeypatch.setattr(mlc, "run_external_golden_parity", lambda **_: report)

    summary = mlc.run_external_golden_matrix(rows=[_fixture_matrix_row(row_id="mismatch")])

    assert summary["counts"] == {"pass": 0, "fail": 1, "skip": 0, "blocked": 0}
    assert summary["signoff_status"] == "failed"
    row = summary["rows"][0]
    assert row["status"] == "fail"
    assert row["reason_code"] == "expected-domain-mismatch"
    assert row["diff_domain_status"]["buff_timeline"]["matches"] is False
    assert row["mismatch_samples"]["buff_timeline"]["sample_changed"] == [
        {
            "source": "alpha",
            "Task": "buff-a",
            "Start": 2,
            "Finish": 3,
            "golden_values": [2.0],
            "candidate_values": [2.5],
        }
    ]


def test_run_external_golden_parity_writes_damage_domain_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    base_cfg = mlc.CommonCfg.model_validate(
        {
            "session_id": "base",
            "char_config": [{"name": "a"}, {"name": "b"}, {"name": "c"}],
            "enemy_config": {"index_id": 11412, "adjustment_id": 22412, "difficulty": 8.74},
            "apl_path": "./default.toml",
        }
    )
    submitted_payloads: list[tuple[dict[str, Any], int, bool]] = []

    def fake_prepare_common_cfg(team: str, apl: str | None) -> mlc.CommonCfg:
        assert team == "fake-team"
        return base_cfg.model_copy(update={"apl_path": apl or base_cfg.apl_path}, deep=True)

    class FakeFuture:
        def __init__(self, session_id: str):
            self._session_id = session_id

        def result(self) -> str:
            return self._session_id

    class FakeExecutor:
        def __init__(self, max_workers: int):
            self.max_workers = max_workers

        def __enter__(self) -> "FakeExecutor":
            return self

        def __exit__(self, exc_type, exc, tb) -> Literal[False]:
            return False

        def submit(
            self,
            func,
            common_cfg_data,
            stop_tick,
            use_indexed_buff_load_loop=False,
        ):
            submitted_payloads.append((common_cfg_data, stop_tick, use_indexed_buff_load_loop))
            return FakeFuture(common_cfg_data["session_id"])

    monkeypatch.setattr(mlc, "_prepare_common_cfg", fake_prepare_common_cfg)
    monkeypatch.setattr(mlc, "_build_session_id", lambda: "candidate-001")
    monkeypatch.setattr(mlc, "ProcessPoolExecutor", FakeExecutor)
    output_path = tmp_path / "external-golden.json"

    report = mlc.run_external_golden_parity(
        golden_result_dir=Path("tests/fixtures/external_golden_parity/minimal-golden"),
        team="fake-team",
        apl="./override.toml",
        stop_tick=33,
        output_path=output_path,
    )

    assert len(submitted_payloads) == 1
    submitted_cfg, submitted_stop_tick, submitted_indexed_flag = submitted_payloads[0]
    assert submitted_cfg["session_id"] == "candidate-001"
    assert submitted_cfg["apl_path"] == "./override.toml"
    assert submitted_stop_tick == 33
    assert submitted_indexed_flag is False
    assert report["schema"] == mlc.EXTERNAL_GOLDEN_PARITY_SCHEMA
    assert report["golden_result_dir"].endswith(
        "tests\\fixtures\\external_golden_parity\\minimal-golden"
    ) or report["golden_result_dir"].endswith(
        "tests/fixtures/external_golden_parity/minimal-golden"
    )
    assert report["candidate"]["session_id"] == "candidate-001"
    assert report["candidate"]["result_path"].endswith("results\\candidate-001") or report[
        "candidate"
    ]["result_path"].endswith("results/candidate-001")
    assert report["run_config"]["identity"]["kind"] == "team"
    assert report["run_config"]["team"] == "fake-team"
    assert report["run_config"]["common_cfg"] is None
    assert report["run_config"]["apl"] == "./override.toml"
    assert report["run_config"]["stop_tick"] == 33
    assert report["comparison"]["candidate_run_count"] == 1
    assert report["comparison"]["implemented_domains"] == [
        "damage",
        "damage_attribution",
        "buff_timeline",
    ]
    assert report["diffs"]["matches"] is True
    assert report["diffs"]["domains"]["damage"]["implemented"] is True
    assert report["diffs"]["domains"]["damage"]["matches"] is True
    assert report["diffs"]["domains"]["damage"]["golden"]["present"] is False
    assert report["diffs"]["domains"]["damage"]["candidate"]["present"] is False
    assert report["diffs"]["domains"]["damage_attribution"]["status"] == "not_provided"
    assert report["diffs"]["domains"]["buff_timeline"]["implemented"] is True
    assert report["diffs"]["domains"]["buff_timeline"]["status"] == "not_provided"

    artifact = json.loads(output_path.read_text(encoding="utf-8"))
    assert artifact == report


def test_build_external_golden_parity_report_compares_matching_damage_fixture(
    tmp_path: Path,
):
    candidate_dir = _write_result_dir(tmp_path / "candidate-result")

    report = _build_external_damage_report(
        golden_result_dir=_DAMAGE_GOLDEN_DIR,
        candidate_result_path=candidate_dir,
    )

    damage = report["diffs"]["domains"]["damage"]
    attribution = report["diffs"]["domains"]["damage_attribution"]
    assert report["comparison"]["implemented_domains"] == [
        "damage",
        "damage_attribution",
        "buff_timeline",
    ]
    assert report["diffs"]["matches"] is True
    assert damage["implemented"] is True
    assert damage["matches"] is True
    assert damage["status"] == "match"
    assert damage["golden"]["row_count"] == 3
    assert damage["golden"]["uuid_count"] == 2
    assert damage["golden"]["total_damage"] == 35.0
    assert damage["golden"]["anomaly_total"] == 1
    assert damage["golden"]["disorder_total"] == 1
    assert damage["golden"]["by_skill_tag"] == {"alpha": 1, "beta": 1}
    assert damage["golden"]["by_skill_cn_name"] == {"alpha": 1, "beta": 1}
    assert damage["golden"]["by_element_type"] == {"0": 1, "4": 1}
    assert damage["differences"]["total_damage"] == 0.0
    assert damage["differences"]["row_count"] == 0
    assert damage["differences"]["uuid_aggregation"]["changed_count"] == 0
    assert damage["differences"]["field_counts"]["skill_tag"] == {}
    assert attribution["implemented"] is True
    assert attribution["matches"] is True
    assert attribution["differences"]["structure"]["compared"] is True
    assert attribution["differences"]["values"]["matches"] is True


def test_build_external_golden_parity_report_reports_damage_mismatch_samples(
    tmp_path: Path,
):
    mismatch_csv = """tick,skill_tag,element_type,dmg_expect,dmg_crit,stun,buildup,is_anomaly,is_disorder,UUID
1,beta,4,20.0,22.0,2.0,1.5,true,false,uuid-2
2,beta,4,6.0,6.0,0.5,0.2,true,true,uuid-2
3,gamma,5,7.0,8.0,0.2,0.1,false,false,uuid-3
"""
    candidate_dir = _write_result_dir(
        tmp_path / "candidate-result",
        damage_csv=mismatch_csv,
        damage_attribution={
            "beta": {"direct_damage": 0.0, "anomaly_damage": 26.0},
            "gamma": {"direct_damage": 7.0, "anomaly_damage": 0.0},
        },
    )

    report = _build_external_damage_report(
        golden_result_dir=_DAMAGE_GOLDEN_DIR,
        candidate_result_path=candidate_dir,
    )

    damage = report["diffs"]["domains"]["damage"]
    attribution = report["diffs"]["domains"]["damage_attribution"]
    uuid_diff = damage["differences"]["uuid_aggregation"]
    assert report["diffs"]["matches"] is False
    assert damage["matches"] is False
    assert damage["differences"]["total_damage"] == -2.0
    assert damage["differences"]["field_counts"]["skill_tag"] == {"alpha": -1, "gamma": 1}
    assert damage["differences"]["field_counts"]["element_type"] == {"0": -1, "5": 1}
    assert uuid_diff["golden_only_count"] == 1
    assert uuid_diff["candidate_only_count"] == 1
    assert uuid_diff["changed_count"] == 1
    assert uuid_diff["sample_golden_only"][0]["UUID"] == "uuid-1"
    assert uuid_diff["sample_candidate_only"][0]["UUID"] == "uuid-3"
    assert uuid_diff["sample_changed"] == [
        {
            "UUID": "uuid-2",
            "fields": {
                "dmg_expect_sum": {"golden": 25.0, "candidate": 26.0},
            },
        }
    ]
    assert attribution["matches"] is False
    assert attribution["differences"]["structure"]["sample_golden_only_paths"] == [
        "$.alpha",
        "$.alpha.anomaly_damage",
        "$.alpha.direct_damage",
    ]
    assert attribution["differences"]["structure"]["sample_candidate_only_paths"] == [
        "$.gamma",
        "$.gamma.anomaly_damage",
        "$.gamma.direct_damage",
    ]
    assert attribution["differences"]["values"]["sample_changed_values"] == [
        {"path": "$.beta.anomaly_damage", "golden": 25.0, "candidate": 26.0}
    ]


def test_external_damage_parity_normalizes_anomaly_schema_forms(tmp_path: Path):
    missing_anomaly_csv = """tick,skill_tag,element_type,dmg_expect,dmg_crit,stun,buildup,is_disorder,UUID
1,alpha,0,10.0,11.0,1.0,0.5,false,uuid-1
"""
    all_null_anomaly_csv = """tick,skill_tag,element_type,dmg_expect,dmg_crit,stun,buildup,is_anomaly,is_disorder,UUID
1,alpha,0,10.0,11.0,1.0,0.5,,false,uuid-1
"""
    string_anomaly_csv = """tick,skill_tag,element_type,dmg_expect,dmg_crit,stun,buildup,is_anomaly,is_disorder,UUID
1,alpha,0,10.0,11.0,1.0,0.5,FALSE,false,uuid-1
"""
    golden_dir = _write_result_dir(
        tmp_path / "golden-missing-anomaly",
        damage_csv=missing_anomaly_csv,
        damage_attribution=None,
    )
    all_null_candidate_dir = _write_result_dir(
        tmp_path / "candidate-all-null-anomaly",
        damage_csv=all_null_anomaly_csv,
        damage_attribution=None,
    )
    string_candidate_dir = _write_result_dir(
        tmp_path / "candidate-string-anomaly",
        damage_csv=string_anomaly_csv,
        damage_attribution=None,
    )

    all_null_report = _build_external_damage_report(
        golden_result_dir=golden_dir,
        candidate_result_path=all_null_candidate_dir,
    )
    string_report = _build_external_damage_report(
        golden_result_dir=golden_dir,
        candidate_result_path=string_candidate_dir,
    )

    assert all_null_report["diffs"]["domains"]["damage"]["matches"] is True
    assert string_report["diffs"]["domains"]["damage"]["matches"] is True
    assert all_null_report["diffs"]["domains"]["damage"]["golden"]["anomaly_total"] == 0
    assert string_report["diffs"]["domains"]["damage"]["candidate"]["anomaly_total"] == 0


def test_external_damage_attribution_reports_presence_mismatch(tmp_path: Path):
    candidate_dir = _write_result_dir(
        tmp_path / "candidate-result",
        damage_attribution=None,
    )

    report = _build_external_damage_report(
        golden_result_dir=_DAMAGE_GOLDEN_DIR,
        candidate_result_path=candidate_dir,
    )

    attribution = report["diffs"]["domains"]["damage_attribution"]
    assert attribution["implemented"] is True
    assert attribution["matches"] is False
    assert attribution["status"] == "mismatch"
    assert attribution["differences"]["presence"] == {
        "golden_damage_attribution": True,
        "candidate_damage_attribution": False,
    }


def test_external_buff_timeline_compares_csv_golden_fixture(tmp_path: Path):
    candidate_dir = _write_result_dir(
        tmp_path / "candidate-result",
        damage_csv=None,
        damage_attribution=None,
        buff_csvs={"alpha": _MATCHING_BUFF_TIMELINE_CSV},
    )

    report = _build_external_damage_report(
        golden_result_dir=_BUFF_CSV_GOLDEN_DIR,
        candidate_result_path=candidate_dir,
    )

    timeline = report["diffs"]["domains"]["buff_timeline"]
    assert timeline["implemented"] is True
    assert timeline["matches"] is True
    assert timeline["status"] == "match"
    assert timeline["public_fields"] == ["Task", "Start", "Finish", "Value"]
    assert timeline["golden"]["source_type"] == "csv"
    assert timeline["candidate"]["source_type"] == "csv"
    assert timeline["golden"]["entry_count"] == 2
    assert timeline["candidate"]["entry_count"] == 2
    assert timeline["differences"]["baseline_only_count"] == 0
    assert timeline["differences"]["candidate_only_count"] == 0
    assert timeline["differences"]["changed_entry_count"] == 0
    assert report["diffs"]["matches"] is True


def test_external_buff_timeline_compares_json_golden_fixture_to_candidate_csv(
    tmp_path: Path,
):
    candidate_dir = _write_result_dir(
        tmp_path / "candidate-result",
        damage_csv=None,
        damage_attribution=None,
        buff_csvs={"alpha": _MATCHING_BUFF_TIMELINE_CSV},
    )

    report = _build_external_damage_report(
        golden_result_dir=_BUFF_JSON_GOLDEN_DIR,
        candidate_result_path=candidate_dir,
    )

    timeline = report["diffs"]["domains"]["buff_timeline"]
    assert timeline["matches"] is True
    assert timeline["golden"]["source_type"] == "json"
    assert timeline["candidate"]["source_type"] == "csv"
    assert timeline["golden"]["public_fields"] == ["Task", "Start", "Finish", "Value"]
    assert timeline["candidate"]["public_fields"] == ["Task", "Start", "Finish", "Value"]
    assert timeline["differences"]["sample_baseline_only"] == []
    assert timeline["differences"]["sample_candidate_only"] == []
    assert timeline["differences"]["sample_changed"] == []


def test_external_buff_timeline_reports_bounded_mismatch_samples(tmp_path: Path):
    candidate_dir = _write_result_dir(
        tmp_path / "candidate-result",
        damage_csv=None,
        damage_attribution=None,
        buff_csvs={"alpha": _MISMATCH_BUFF_TIMELINE_CSV},
    )

    report = _build_external_damage_report(
        golden_result_dir=_BUFF_CSV_GOLDEN_DIR,
        candidate_result_path=candidate_dir,
    )

    timeline = report["diffs"]["domains"]["buff_timeline"]
    differences = timeline["differences"]
    assert report["diffs"]["matches"] is False
    assert timeline["matches"] is False
    assert timeline["status"] == "mismatch"
    assert differences["baseline_only_count"] == 1
    assert differences["golden_only_count"] == 1
    assert differences["candidate_only_count"] == 1
    assert differences["changed_entry_count"] == 1
    assert differences["sample_baseline_only"] == [
        {"source": "alpha", "Task": "buff-b", "Start": 2, "Finish": 2, "Value": 1.5}
    ]
    assert differences["sample_candidate_only"] == [
        {"source": "alpha", "Task": "buff-c", "Start": 2, "Finish": 3, "Value": 4.0}
    ]
    assert differences["sample_changed"] == [
        {
            "source": "alpha",
            "Task": "buff-a",
            "Start": 2,
            "Finish": 3,
            "golden_values": [2.0],
            "candidate_values": [2.5],
        }
    ]


def test_run_external_golden_parity_rejects_missing_golden_dir(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="golden result directory does not exist"):
        mlc.run_external_golden_parity(
            golden_result_dir=tmp_path / "missing-golden",
            team="fake-team",
            stop_tick=1,
        )


def test_run_main_loop_consistency_uses_runtime_labels_and_cleanup(monkeypatch: pytest.MonkeyPatch):
    snapshots_by_session: dict[str, RuntimeSnapshot] = {
        "101": RuntimeSnapshot(
            runtime_label="default-label",
            session_id="101",
            total_damage=100.0,
            event_counts={
                "total": 1,
                "anomaly_total": 0,
                "disorder_total": 0,
                "by_skill_tag": {},
                "by_skill_name": {},
                "by_element_type": {},
            },
            buff_timeline={},
        ),
        "102": RuntimeSnapshot(
            runtime_label="candidate-label",
            session_id="102",
            total_damage=101.0,
            event_counts={
                "total": 1,
                "anomaly_total": 0,
                "disorder_total": 0,
                "by_skill_tag": {},
                "by_skill_name": {},
                "by_element_type": {},
            },
            buff_timeline={},
        ),
    }
    created_session_ids: list[str] = []
    submitted_payloads: list[tuple[dict[str, Any], int, bool]] = []
    cleaned_sessions: list[str] = []

    monkeypatch.setattr(
        mlc,
        "_prepare_common_cfg",
        lambda team, apl: mlc.CommonCfg.model_validate(
            {
                "session_id": "base",
                "char_config": [
                    {"name": "a"},
                    {"name": "b"},
                    {"name": "c"},
                ],
                "enemy_config": {"index_id": 11412, "adjustment_id": 22412, "difficulty": 8.74},
                "apl_path": apl or "./default.toml",
            }
        ),
    )

    session_id_iter = iter(["101", "102"])

    def fake_build_session_id() -> str:
        session_id = next(session_id_iter)
        created_session_ids.append(session_id)
        return session_id

    monkeypatch.setattr(mlc, "_build_session_id", fake_build_session_id)

    class FakeFuture:
        def __init__(self, session_id: str):
            self._session_id = session_id

        def result(self) -> str:
            return self._session_id

    class FakeExecutor:
        def __init__(self, max_workers: int):
            self.max_workers = max_workers

        def __enter__(self) -> "FakeExecutor":
            return self

        def __exit__(self, exc_type, exc, tb) -> Literal[False]:
            return False

        def submit(
            self,
            func,
            common_cfg_data,
            stop_tick,
            use_indexed_buff_load_loop=False,
        ):
            submitted_payloads.append((common_cfg_data, stop_tick, use_indexed_buff_load_loop))
            return FakeFuture(common_cfg_data["session_id"])

    monkeypatch.setattr(mlc, "ProcessPoolExecutor", FakeExecutor)
    monkeypatch.setattr(mlc, "_load_runtime_snapshot", lambda label, sid: snapshots_by_session[sid])
    monkeypatch.setattr(mlc, "_cleanup_result_artifacts", cleaned_sessions.append)

    report = run_main_loop_consistency(
        team="fake-team",
        apl="./override.toml",
        stop_tick=77,
        baseline_runtime="default-label",
        candidate_runtime="candidate-label",
        cleanup=True,
    )

    assert created_session_ids == ["101", "102"]
    assert [payload["session_id"] for payload, _, _ in submitted_payloads] == ["101", "102"]
    assert all(stop_tick == 77 for _, stop_tick, _ in submitted_payloads)
    assert [flag for _, _, flag in submitted_payloads] == [False, False]
    assert report["baseline_runtime"] == "default-label"
    assert report["legacy_runtime"] == "default-label"
    assert report["candidate_runtime"] == "candidate-label"
    assert report["runtime_selection"]["mode"] == "label-only-current-runtime"
    assert report["apl"] == "./override.toml"
    assert cleaned_sessions == ["101", "102"]


def test_run_main_loop_consistency_candidate_opt_in_only_flags_candidate(
    monkeypatch: pytest.MonkeyPatch,
):
    snapshots_by_session: dict[str, RuntimeSnapshot] = {
        "201": RuntimeSnapshot(
            runtime_label="default-label",
            session_id="201",
            total_damage=100.0,
            event_counts={
                "total": 1,
                "anomaly_total": 0,
                "disorder_total": 0,
                "by_skill_tag": {},
                "by_skill_name": {},
                "by_element_type": {},
            },
            buff_timeline={},
        ),
        "202": RuntimeSnapshot(
            runtime_label="candidate-label",
            session_id="202",
            total_damage=100.0,
            event_counts={
                "total": 1,
                "anomaly_total": 0,
                "disorder_total": 0,
                "by_skill_tag": {},
                "by_skill_name": {},
                "by_element_type": {},
            },
            buff_timeline={},
        ),
    }
    submitted_flags: list[bool] = []

    monkeypatch.setattr(
        mlc,
        "_prepare_common_cfg",
        lambda team, apl: mlc.CommonCfg.model_validate(
            {
                "session_id": "base",
                "char_config": [{"name": "a"}, {"name": "b"}, {"name": "c"}],
                "enemy_config": {"index_id": 11412, "adjustment_id": 22412, "difficulty": 8.74},
                "apl_path": apl or "./default.toml",
            }
        ),
    )
    session_id_iter = iter(["201", "202"])
    monkeypatch.setattr(mlc, "_build_session_id", lambda: next(session_id_iter))

    class FakeFuture:
        def __init__(self, session_id: str):
            self._session_id = session_id

        def result(self) -> str:
            return self._session_id

    class FakeExecutor:
        def __init__(self, max_workers: int):
            self.max_workers = max_workers

        def __enter__(self) -> "FakeExecutor":
            return self

        def __exit__(self, exc_type, exc, tb) -> Literal[False]:
            return False

        def submit(
            self,
            func,
            common_cfg_data,
            stop_tick,
            use_indexed_buff_load_loop=False,
        ):
            submitted_flags.append(use_indexed_buff_load_loop)
            return FakeFuture(common_cfg_data["session_id"])

    monkeypatch.setattr(mlc, "ProcessPoolExecutor", FakeExecutor)
    monkeypatch.setattr(mlc, "_load_runtime_snapshot", lambda label, sid: snapshots_by_session[sid])
    monkeypatch.setattr(mlc, "_cleanup_result_artifacts", lambda _: None)

    report = run_main_loop_consistency(
        team="fake-team",
        apl=None,
        stop_tick=77,
        baseline_runtime="default-label",
        candidate_runtime="candidate-label",
        candidate_use_indexed_buff_load_loop=True,
    )

    assert submitted_flags == [False, True]
    assert report["runtime_selection"]["mode"] == "candidate-explicit-opt-in-indexed-buff-load-loop"
    assert report["runtime_selection"]["default_off"] is True


def _matching_opt_in_report(team: str, stop_tick: int = 120) -> dict[str, Any]:
    legacy_snapshot = RuntimeSnapshot(
        runtime_label="default-current-path",
        session_id=f"{team}-legacy",
        total_damage=123.4,
        event_counts={
            "total": 2,
            "anomaly_total": 0,
            "disorder_total": 0,
            "by_skill_tag": {"alpha": 2},
            "by_skill_name": {"Alpha": 2},
            "by_element_type": {"1": 2},
        },
        buff_timeline={
            "alpha": [{"Task": "buff-a", "Start": 1, "Finish": 2, "Value": 1.0}]
        },
    )
    candidate_snapshot = RuntimeSnapshot(
        runtime_label="opt-in-indexed-path",
        session_id=f"{team}-candidate",
        total_damage=123.4,
        event_counts=dict(legacy_snapshot.event_counts),
        buff_timeline=dict(legacy_snapshot.buff_timeline),
    )
    return build_consistency_report(
        team=team,
        apl=f"./{team}.toml",
        stop_tick=stop_tick,
        legacy_snapshot=legacy_snapshot,
        candidate_snapshot=candidate_snapshot,
        candidate_use_indexed_buff_load_loop=True,
    )


def _matching_default_report(team: str, stop_tick: int = 120) -> dict[str, Any]:
    legacy_snapshot = RuntimeSnapshot(
        runtime_label="default-current-path",
        session_id=f"{team}-legacy",
        total_damage=123.4,
        event_counts={
            "total": 2,
            "anomaly_total": 0,
            "disorder_total": 0,
            "by_skill_tag": {"alpha": 2},
            "by_skill_name": {"Alpha": 2},
            "by_element_type": {"1": 2},
        },
        buff_timeline={
            "alpha": [{"Task": "buff-a", "Start": 1, "Finish": 2, "Value": 1.0}]
        },
    )
    candidate_snapshot = RuntimeSnapshot(
        runtime_label="candidate-current-path",
        session_id=f"{team}-candidate",
        total_damage=123.4,
        event_counts=dict(legacy_snapshot.event_counts),
        buff_timeline=dict(legacy_snapshot.buff_timeline),
    )
    return build_consistency_report(
        team=team,
        apl=f"./{team}.toml",
        stop_tick=stop_tick,
        legacy_snapshot=legacy_snapshot,
        candidate_snapshot=candidate_snapshot,
    )


def test_build_multi_team_consistency_summary_records_parity_fields():
    reports = [
        _matching_opt_in_report("team-a"),
        _matching_opt_in_report("team-b"),
        _matching_opt_in_report("team-c"),
    ]

    summary = mlc.build_multi_team_consistency_summary(
        reports=reports,
        generated_at="2026-06-22T00:00:00+0800",
    )

    assert summary["schema"] == mlc.MULTI_TEAM_CONSISTENCY_SCHEMA
    assert summary["team_count"] == 3
    assert summary["teams"] == ["team-a", "team-b", "team-c"]
    assert summary["stop_ticks"] == [120]
    assert summary["stop_tick_count"] == 1
    assert summary["matrix_row_count"] == 3
    assert summary["minimum_stop_tick_met"] is True
    assert summary["candidate_use_indexed_buff_load_loop"] is True
    assert summary["default_indexed_execution"] == "blocked"
    assert summary["all_match"] is True
    assert summary["mismatch_count"] == 0
    assert summary["matrix_results"] == summary["team_results"]
    first_result = summary["team_results"][0]
    assert first_result["runtime_labels"] == {
        "default_path": "default-current-path",
        "opt_in_indexed_path": "opt-in-indexed-path",
    }
    assert first_result["candidate_use_indexed_buff_load_loop"] is True
    assert first_result["opt_in_flag_status"] == "candidate_explicit_opt_in"
    assert first_result["damage_parity"]["matches"] is True
    assert first_result["event_count_parity"]["matches"] is True
    assert first_result["buff_timeline_parity"]["matches"] is True
    assert first_result["mismatch_count"] == 0


def test_build_multi_team_consistency_summary_records_stop_tick_matrix_fields():
    reports = [
        _matching_opt_in_report("team-a", stop_tick=120),
        _matching_opt_in_report("team-a", stop_tick=600),
        _matching_opt_in_report("team-b", stop_tick=120),
        _matching_opt_in_report("team-b", stop_tick=600),
    ]

    summary = mlc.build_multi_team_consistency_summary(
        reports=reports,
        generated_at="2026-06-22T00:00:00+0800",
    )

    assert summary["team_count"] == 2
    assert summary["teams"] == ["team-a", "team-b"]
    assert summary["stop_ticks"] == [120, 600]
    assert summary["stop_tick_count"] == 2
    assert summary["matrix_row_count"] == 4
    assert summary["mismatch_count"] == 0
    matrix_keys = [
        (row["team"], row["stop_tick"], row["candidate_use_indexed_buff_load_loop"])
        for row in summary["matrix_results"]
    ]
    assert matrix_keys == [
        ("team-a", 120, True),
        ("team-a", 600, True),
        ("team-b", 120, True),
        ("team-b", 600, True),
    ]

    stop_600_result = summary["matrix_results"][1]
    assert stop_600_result["runtime_labels"] == {
        "default_path": "default-current-path",
        "opt_in_indexed_path": "opt-in-indexed-path",
    }
    assert stop_600_result["opt_in_flag_status"] == "candidate_explicit_opt_in"
    assert stop_600_result["damage_parity"]["matches"] is True
    assert stop_600_result["event_count_parity"]["matches"] is True
    assert stop_600_result["buff_timeline_parity"]["matches"] is True
    assert stop_600_result["mismatch_count"] == 0


def test_run_multi_team_main_loop_consistency_writes_summary_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    captured_calls: list[dict[str, Any]] = []

    def fake_run_main_loop_consistency(**kwargs: Any) -> dict[str, Any]:
        captured_calls.append(kwargs)
        return _matching_opt_in_report(kwargs["team"], kwargs["stop_tick"])

    monkeypatch.setattr(mlc, "run_main_loop_consistency", fake_run_main_loop_consistency)
    output_path = tmp_path / "multi-team-consistency.json"

    summary = mlc.run_multi_team_main_loop_consistency(
        teams=["team-a", "team-b", "team-c"],
        stop_tick=120,
        cleanup=True,
        candidate_use_indexed_buff_load_loop=True,
        output_path=output_path,
    )

    assert [call["team"] for call in captured_calls] == ["team-a", "team-b", "team-c"]
    assert [call["stop_tick"] for call in captured_calls] == [120, 120, 120]
    assert [call["candidate_use_indexed_buff_load_loop"] for call in captured_calls] == [
        True,
        True,
        True,
    ]
    assert [call["baseline_runtime"] for call in captured_calls] == [
        "default-current-path",
        "default-current-path",
        "default-current-path",
    ]
    assert [call["candidate_runtime"] for call in captured_calls] == [
        "opt-in-indexed-path",
        "opt-in-indexed-path",
        "opt-in-indexed-path",
    ]
    assert summary["all_match"] is True
    assert summary["matrix_row_count"] == 3

    artifact = json.loads(output_path.read_text(encoding="utf-8"))
    assert artifact["teams"] == ["team-a", "team-b", "team-c"]
    assert artifact["candidate_use_indexed_buff_load_loop"] is True
    assert artifact["matrix_row_count"] == 3
    assert artifact["team_results"][0]["damage_parity"]["delta"] == 0.0


def test_run_multi_team_main_loop_consistency_accepts_stop_tick_matrix(
    monkeypatch: pytest.MonkeyPatch,
):
    captured_calls: list[dict[str, Any]] = []

    def fake_run_main_loop_consistency(**kwargs: Any) -> dict[str, Any]:
        captured_calls.append(kwargs)
        return _matching_opt_in_report(kwargs["team"], kwargs["stop_tick"])

    monkeypatch.setattr(mlc, "run_main_loop_consistency", fake_run_main_loop_consistency)

    summary = mlc.run_multi_team_main_loop_consistency(
        teams=["team-a", "team-b"],
        stop_tick=120,
        stop_ticks=[120, 600],
        cleanup=True,
        candidate_use_indexed_buff_load_loop=True,
    )

    assert [(call["team"], call["stop_tick"]) for call in captured_calls] == [
        ("team-a", 120),
        ("team-a", 600),
        ("team-b", 120),
        ("team-b", 600),
    ]
    assert summary["teams"] == ["team-a", "team-b"]
    assert summary["stop_ticks"] == [120, 600]
    assert summary["matrix_row_count"] == 4
    assert summary["candidate_use_indexed_buff_load_loop"] is True


def test_run_multi_team_main_loop_consistency_defaults_candidate_flag_off(
    monkeypatch: pytest.MonkeyPatch,
):
    captured_calls: list[dict[str, Any]] = []

    def fake_run_main_loop_consistency(**kwargs: Any) -> dict[str, Any]:
        captured_calls.append(kwargs)
        return _matching_default_report(kwargs["team"], kwargs["stop_tick"])

    monkeypatch.setattr(mlc, "run_main_loop_consistency", fake_run_main_loop_consistency)

    summary = mlc.run_multi_team_main_loop_consistency(
        teams=["team-a"],
        stop_tick=120,
        stop_ticks=[120, 600],
        cleanup=True,
        candidate_use_indexed_buff_load_loop=False,
    )

    assert [(call["team"], call["stop_tick"]) for call in captured_calls] == [
        ("team-a", 120),
        ("team-a", 600),
    ]
    assert [call["candidate_use_indexed_buff_load_loop"] for call in captured_calls] == [
        False,
        False,
    ]
    assert summary["candidate_use_indexed_buff_load_loop"] is False
    assert summary["default_indexed_execution"] == "blocked"
    assert [
        row["opt_in_flag_status"] for row in summary["matrix_results"]
    ] == ["default_off_label_only", "default_off_label_only"]


def test_load_runtime_snapshot_falls_back_for_blank_anomaly_column(
    monkeypatch: pytest.MonkeyPatch,
):
    raw_damage_df = pl.DataFrame(
        {
            "tick": [13],
            "skill_tag": ["alpha"],
            "element_type": [0],
            "dmg_expect": [10.0],
            "dmg_crit": [11.0],
            "stun": [1.0],
            "buildup": [0.0],
            "is_anomaly": [None],
            "is_disorder": [None],
            "UUID": ["uuid-1"],
        }
    )

    def raise_blank_anomaly(_: str):
        raise ValueError("DataFrame 中缺少有效的列: is_anomaly")

    async def fake_prepare_buff_data_and_cache(_: str):
        return {}

    monkeypatch.setattr(mlc, "prepare_dmg_data_and_cache", raise_blank_anomaly)
    monkeypatch.setattr(mlc, "_load_damage_result_df", lambda _: raw_damage_df)
    monkeypatch.setattr(mlc, "prepare_buff_data_and_cache", fake_prepare_buff_data_and_cache)

    snapshot = mlc._load_runtime_snapshot("facade", "101")

    assert snapshot.total_damage == 10.0
    assert snapshot.event_counts["total"] == 1
    assert snapshot.event_counts["anomaly_total"] == 0
    assert snapshot.event_counts["by_skill_tag"] == {"alpha": 1}


def test_damage_schema_normalizes_string_anomaly_column():
    raw_damage_df = pl.DataFrame(
        {
            "tick": [13, 14],
            "skill_tag": ["alpha", "beta"],
            "element_type": [0, 4],
            "dmg_expect": [10.0, 20.0],
            "dmg_crit": [11.0, 22.0],
            "stun": [1.0, 2.0],
            "buildup": [0.0, 0.0],
            "is_anomaly": [None, "false"],
            "UUID": ["uuid-1", "uuid-2"],
        }
    )

    normalized_df = _normalize_damage_schema(raw_damage_df)
    uuid_df = sort_df_by_UUID(normalized_df)

    assert normalized_df["is_anomaly"].dtype == pl.Boolean
    assert normalized_df["is_anomaly"].to_list() == [False, False]
    assert uuid_df["is_anomaly"].to_list() == [False, False]


def test_yixuan_astra_trigger_team_is_registered_for_phase5_route():
    registry = auto_register_teams()
    team_config = registry.get_team("仪玄-耀嘉音-扳机试点队")

    assert team_config is not None
    common_cfg = team_config.create_config()
    assert [char.name for char in common_cfg.char_config] == ["仪玄", "耀嘉音", "扳机"]
    assert common_cfg.apl_path == "./zsim/data/APLData/仪玄-耀嘉音-扳机.toml"


def test_script_entrypoint_runs_with_json_output(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    script_path = Path("scripts/run_buff_main_loop_consistency.py").resolve()

    def fake_run_main_loop_consistency(**_: Any) -> dict[str, Any]:
        return {
            "team": "fake-team",
            "apl": "./fake.toml",
            "stop_tick": 20,
            "baseline_runtime": "default-current",
            "legacy_runtime": "default-current",
            "candidate_runtime": "candidate",
            "total_damage": {"baseline": 1.0, "legacy": 1.0, "candidate": 1.0},
            "event_counts": {"baseline": {}, "legacy": {}, "candidate": {}},
            "buff_timeline": {"baseline": {}, "legacy": {}, "candidate": {}},
            "differences": {
                "matches": True,
                "total_damage": 0.0,
                "event_counts": {},
                "buff_timeline": {
                    "legacy_only_count": 0,
                    "candidate_only_count": 0,
                    "sample_legacy_only": [],
                    "sample_candidate_only": [],
                },
            },
        }

    monkeypatch.setattr(mlc, "run_main_loop_consistency", fake_run_main_loop_consistency)

    namespace: dict[str, Any] = {"__name__": "__main__", "__file__": str(script_path)}
    argv_before = list(mlc.sys.argv)
    try:
        mlc.sys.argv = [str(script_path), "--team", "fake-team", "--json"]
        with pytest.raises(SystemExit) as excinfo:
            exec(script_path.read_text(encoding="utf-8"), namespace)
        assert excinfo.value.code == 0
        output = capsys.readouterr().out
        assert '"team": "fake-team"' in output
        assert '"matches": true' in output
    finally:
        mlc.sys.argv = argv_before


def test_script_entrypoint_importable_from_scripts_directory():
    script_path = Path("scripts/run_buff_main_loop_consistency.py").resolve()
    content = script_path.read_text(encoding="utf-8")

    assert "sys.path.insert(0, str(PROJECT_ROOT))" in content
    assert "from zsim.utils.main_loop_consistency import main" in content
