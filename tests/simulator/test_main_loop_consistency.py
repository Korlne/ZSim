from __future__ import annotations

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


def test_build_consistency_report_keeps_required_json_fields():
    legacy_snapshot = RuntimeSnapshot(
        runtime_label="legacy",
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
    assert report["total_damage"] == {"legacy": 123.4, "candidate": 130.0}
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
            "--legacy-runtime",
            "legacy-a",
            "--candidate-runtime",
            "candidate-b",
            "--json",
        ]
    )

    assert args.team == "team-a"
    assert args.apl == "./zsim/data/APLData/example.toml"
    assert args.legacy_runtime == "legacy-a"
    assert args.candidate_runtime == "candidate-b"
    assert args.json is True


def test_run_main_loop_consistency_uses_runtime_labels_and_cleanup(monkeypatch: pytest.MonkeyPatch):
    snapshots_by_session: dict[str, RuntimeSnapshot] = {
        "101": RuntimeSnapshot(
            runtime_label="legacy-label",
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
    submitted_payloads: list[tuple[dict[str, Any], int]] = []
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

        def submit(self, func, common_cfg_data, stop_tick):
            submitted_payloads.append((common_cfg_data, stop_tick))
            return FakeFuture(common_cfg_data["session_id"])

    monkeypatch.setattr(mlc, "ProcessPoolExecutor", FakeExecutor)
    monkeypatch.setattr(mlc, "_load_runtime_snapshot", lambda label, sid: snapshots_by_session[sid])
    monkeypatch.setattr(mlc, "_cleanup_result_artifacts", cleaned_sessions.append)

    report = run_main_loop_consistency(
        team="fake-team",
        apl="./override.toml",
        stop_tick=77,
        legacy_runtime="legacy-label",
        candidate_runtime="candidate-label",
        cleanup=True,
    )

    assert created_session_ids == ["101", "102"]
    assert [payload["session_id"] for payload, _ in submitted_payloads] == ["101", "102"]
    assert all(stop_tick == 77 for _, stop_tick in submitted_payloads)
    assert report["legacy_runtime"] == "legacy-label"
    assert report["candidate_runtime"] == "candidate-label"
    assert report["runtime_selection"]["mode"] == "label-only-current-runtime"
    assert report["apl"] == "./override.toml"
    assert cleaned_sessions == ["101", "102"]


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
            "legacy_runtime": "legacy",
            "candidate_runtime": "candidate",
            "total_damage": {"legacy": 1.0, "candidate": 1.0},
            "event_counts": {"legacy": {}, "candidate": {}},
            "buff_timeline": {"legacy": {}, "candidate": {}},
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
