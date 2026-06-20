from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any
from typing import Literal

import polars as pl
import pytest

from zsim.utils import main_loop_consistency as mlc
from zsim.utils import runtime_benchmark as rb
from zsim.utils.runtime_benchmark import (
    RuntimeBenchmarkSnapshot,
    build_parser,
    build_runtime_benchmark_report,
    run_runtime_benchmark,
)


def test_build_runtime_benchmark_report_keeps_required_json_fields():
    legacy_snapshot = RuntimeBenchmarkSnapshot(
        runtime_label="legacy",
        session_id="1",
        total_runtime_ms=120.5,
        hotspots={
            "simulator_run_ms": 100.0,
            "damage_report_ms": 15.0,
            "buff_report_ms": 5.5,
        },
    )
    candidate_snapshot = RuntimeBenchmarkSnapshot(
        runtime_label="candidate",
        session_id="2",
        total_runtime_ms=100.0,
        hotspots={
            "simulator_run_ms": 80.0,
            "damage_report_ms": 14.0,
            "buff_report_ms": 6.0,
        },
    )

    assert legacy_snapshot.rebuild_counts is None
    assert candidate_snapshot.rebuild_counts is None

    report = build_runtime_benchmark_report(
        team="team-a",
        apl="./zsim/data/APLData/example.toml",
        stop_tick=120,
        legacy_snapshot=legacy_snapshot,
        candidate_snapshot=candidate_snapshot,
    )

    assert report["team"] == "team-a"
    assert report["apl"] == "./zsim/data/APLData/example.toml"
    assert report["stop_tick"] == 120
    assert report["runtime_selection"]["mode"] == "label-only-current-runtime"
    assert report["total_runtime_ms"] == {"legacy": 120.5, "candidate": 100.0}
    assert report["hotspots"]["legacy"][0]["name"] == "simulator_run_ms"
    assert report["hotspots"]["candidate"][0]["runtime_ms"] == 80.0
    assert report["comparisons"]["total_runtime_ms"] == -20.5
    assert report["comparisons"]["hotspots"]["simulator_run_ms"] == -20.0
    assert report["comparisons"]["faster_runtime"] == "candidate"
    assert report["comparisons"]["candidate_vs_legacy_ratio"] == 0.8299
    assert "buff_runtime_rebuild_counts" not in report
    assert "buff_runtime_rebuild_counts" not in report["comparisons"]


def test_build_runtime_benchmark_report_includes_rebuild_counts_when_opted_in():
    legacy_snapshot = RuntimeBenchmarkSnapshot(
        runtime_label="legacy",
        session_id="1",
        total_runtime_ms=120.5,
        hotspots={
            "simulator_run_ms": 100.0,
            "damage_report_ms": 15.0,
            "buff_report_ms": 5.5,
        },
    )
    candidate_snapshot = RuntimeBenchmarkSnapshot(
        runtime_label="candidate",
        session_id="2",
        total_runtime_ms=100.0,
        hotspots={
            "simulator_run_ms": 80.0,
            "damage_report_ms": 14.0,
            "buff_report_ms": 6.0,
        },
    )

    report = build_runtime_benchmark_report(
        team="team-a",
        apl="./zsim/data/APLData/example.toml",
        stop_tick=120,
        legacy_snapshot=legacy_snapshot,
        candidate_snapshot=candidate_snapshot,
        include_rebuild_counts=True,
        buff_runtime_rebuild_counts={
            "legacy": {
                "buff_load_loop": 5,
                "scheduled_event": 2,
            },
            "candidate": {
                "scheduled_event": 4,
                "scheduled_event_runtime_ports": 7,
            },
        },
    )

    assert report["buff_runtime_rebuild_counts"] == {
        "legacy": {
            "buff_load_loop": 5,
            "scheduled_event": 2,
        },
        "candidate": {
            "scheduled_event": 4,
            "scheduled_event_runtime_ports": 7,
        },
    }
    assert report["comparisons"]["buff_runtime_rebuild_counts"] == {
        "buff_load_loop": -5,
        "scheduled_event": 2,
        "scheduled_event_runtime_ports": 7,
    }


def test_build_parser_accepts_required_cli_flags():
    parser = build_parser()

    args = parser.parse_args(
        [
            "--team",
            "team-a",
            "--apl",
            "./zsim/data/APLData/example.toml",
            "--stop-tick",
            "240",
            "--legacy-runtime",
            "legacy-a",
            "--candidate-runtime",
            "candidate-b",
            "--json",
            "--include-rebuild-counts",
        ]
    )

    assert args.team == "team-a"
    assert args.apl == "./zsim/data/APLData/example.toml"
    assert args.stop_tick == 240
    assert args.legacy_runtime == "legacy-a"
    assert args.candidate_runtime == "candidate-b"
    assert args.json is True
    assert args.include_rebuild_counts is True


def test_run_runtime_benchmark_uses_runtime_labels_and_cleanup(monkeypatch: pytest.MonkeyPatch):
    snapshots_by_session: dict[str, RuntimeBenchmarkSnapshot] = {
        "101": RuntimeBenchmarkSnapshot(
            runtime_label="legacy-label",
            session_id="101",
            total_runtime_ms=100.0,
            hotspots={
                "simulator_run_ms": 80.0,
                "damage_report_ms": 15.0,
                "buff_report_ms": 5.0,
            },
        ),
        "102": RuntimeBenchmarkSnapshot(
            runtime_label="candidate-label",
            session_id="102",
            total_runtime_ms=99.0,
            hotspots={
                "simulator_run_ms": 78.0,
                "damage_report_ms": 16.0,
                "buff_report_ms": 5.0,
            },
        ),
    }
    rebuild_counts_by_session = {
        "101": {"buff_load_loop": 1},
        "102": {"buff_load_loop": 3, "scheduled_event": 2},
    }
    created_session_ids: list[str] = []
    submitted_payloads: list[tuple[dict[str, Any], int, bool]] = []
    snapshot_loads: list[tuple[str, str, float, dict[str, int] | None]] = []
    cleaned_sessions: list[str] = []

    monkeypatch.setattr(
        rb,
        "_prepare_common_cfg",
        lambda team, apl: rb.CommonCfg.model_validate(
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

    monkeypatch.setattr(rb, "_build_session_id", fake_build_session_id)

    class FakeFuture:
        def __init__(self, session_id: str, include_rebuild_counts: bool):
            self._session_id = session_id
            self._include_rebuild_counts = include_rebuild_counts

        def result(self) -> tuple[str, float, dict[str, int] | None]:
            rebuild_counts = None
            if self._include_rebuild_counts:
                rebuild_counts = dict(rebuild_counts_by_session[self._session_id])
            return self._session_id, 88.8, rebuild_counts

    class FakeExecutor:
        def __init__(self, max_workers: int):
            self.max_workers = max_workers

        def __enter__(self) -> "FakeExecutor":
            return self

        def __exit__(self, exc_type, exc, tb) -> Literal[False]:
            return False

        def submit(self, func, common_cfg_data, stop_tick, include_rebuild_counts=False):
            submitted_payloads.append((common_cfg_data, stop_tick, include_rebuild_counts))
            return FakeFuture(common_cfg_data["session_id"], include_rebuild_counts)

    monkeypatch.setattr(rb, "ProcessPoolExecutor", FakeExecutor)

    def fake_load_runtime_benchmark_snapshot(
        label: str,
        sid: str,
        simulator_runtime_ms: float,
        rebuild_counts: dict[str, int] | None = None,
    ) -> RuntimeBenchmarkSnapshot:
        snapshot_loads.append((label, sid, simulator_runtime_ms, rebuild_counts))
        base_snapshot = snapshots_by_session[sid]
        return RuntimeBenchmarkSnapshot(
            runtime_label=label,
            session_id=sid,
            total_runtime_ms=base_snapshot.total_runtime_ms,
            hotspots=base_snapshot.hotspots,
            rebuild_counts=rebuild_counts,
        )

    monkeypatch.setattr(rb, "_load_runtime_benchmark_snapshot", fake_load_runtime_benchmark_snapshot)
    monkeypatch.setattr(rb, "_cleanup_result_artifacts", cleaned_sessions.append)

    report = run_runtime_benchmark(
        team="fake-team",
        apl="./override.toml",
        stop_tick=77,
        legacy_runtime="legacy-label",
        candidate_runtime="candidate-label",
        cleanup=True,
        include_rebuild_counts=True,
    )

    assert created_session_ids == ["101", "102"]
    assert [payload["session_id"] for payload, _, _ in submitted_payloads] == ["101", "102"]
    assert all(stop_tick == 77 for _, stop_tick, _ in submitted_payloads)
    assert [include_counts for _, _, include_counts in submitted_payloads] == [True, True]
    assert snapshot_loads == [
        ("legacy-label", "101", 88.8, {"buff_load_loop": 1}),
        ("candidate-label", "102", 88.8, {"buff_load_loop": 3, "scheduled_event": 2}),
    ]
    assert report["legacy_runtime"] == "legacy-label"
    assert report["candidate_runtime"] == "candidate-label"
    assert report["runtime_selection"]["mode"] == "label-only-current-runtime"
    assert report["apl"] == "./override.toml"
    assert report["buff_runtime_rebuild_counts"] == {
        "legacy": {"buff_load_loop": 1},
        "candidate": {"buff_load_loop": 3, "scheduled_event": 2},
    }
    assert report["comparisons"]["buff_runtime_rebuild_counts"] == {
        "buff_load_loop": 2,
        "scheduled_event": 2,
    }
    assert cleaned_sessions == ["101", "102"]


def test_single_runtime_benchmark_process_collects_opt_in_rebuild_counts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeCommonCfg:
        @classmethod
        def model_validate(cls, data: dict[str, Any]) -> Any:
            return SimpleNamespace(session_id=data["session_id"])

    class FakeSimulator:
        instances: list["FakeSimulator"] = []

        def __init__(self) -> None:
            self.rebuild_counts: dict[str, int] | None = None
            FakeSimulator.instances.append(self)

        def enable_buff_runtime_rebuild_counting(self) -> None:
            self.rebuild_counts = {}

        def api_run_simulator(self, common_cfg: Any, sim_cfg: Any, stop_tick: int) -> Any:
            if self.rebuild_counts is not None:
                self.rebuild_counts["legacy_buff_runtime_facade"] = 1
                self.rebuild_counts["buff_load_loop"] = stop_tick
            return SimpleNamespace(session_id=common_cfg.session_id)

        def get_buff_runtime_rebuild_counts(self) -> dict[str, int] | None:
            if self.rebuild_counts is None:
                return None
            return dict(self.rebuild_counts)

    perf_counter_values = iter([1.0, 1.125, 2.0, 2.25])
    monkeypatch.setattr(rb.os, "chdir", lambda _: None)
    monkeypatch.setattr(rb.time, "perf_counter", lambda: next(perf_counter_values))
    monkeypatch.setattr(rb, "CommonCfg", FakeCommonCfg)
    monkeypatch.setattr(rb, "Simulator", FakeSimulator)

    default_result = rb._run_single_runtime_benchmark_process(
        {"session_id": "default-session"},
        stop_tick=3,
    )
    opt_in_result = rb._run_single_runtime_benchmark_process(
        {"session_id": "counted-session"},
        stop_tick=4,
        include_rebuild_counts=True,
    )

    assert default_result == ("default-session", 125.0, None)
    assert opt_in_result == (
        "counted-session",
        250.0,
        {
            "legacy_buff_runtime_facade": 1,
            "buff_load_loop": 4,
        },
    )
    assert FakeSimulator.instances[0].rebuild_counts is None


def test_format_human_report_only_prints_rebuild_counts_when_present():
    base_report = {
        "team": "fake-team",
        "apl": "./fake.toml",
        "stop_tick": 20,
        "legacy_runtime": "legacy",
        "candidate_runtime": "candidate",
        "total_runtime_ms": {"legacy": 1.0, "candidate": 1.0},
        "hotspots": {"legacy": [], "candidate": []},
        "comparisons": {
            "total_runtime_ms": 0.0,
            "hotspots": {},
            "faster_runtime": "tie",
            "candidate_vs_legacy_ratio": 1.0,
        },
    }

    default_output = rb._format_human_report(base_report)

    assert "buff_runtime_rebuild_counts" not in default_output

    opt_in_report = dict(base_report)
    opt_in_report["buff_runtime_rebuild_counts"] = {
        "legacy": {"scheduled_event": 1},
        "candidate": {"scheduled_event": 3},
    }
    opt_in_report["comparisons"] = dict(base_report["comparisons"])
    opt_in_report["comparisons"]["buff_runtime_rebuild_counts"] = {"scheduled_event": 2}

    opt_in_output = rb._format_human_report(opt_in_report)

    assert "buff_runtime_rebuild_counts:" in opt_in_output
    assert "buff_runtime_rebuild_count_deltas:" in opt_in_output


def test_load_runtime_benchmark_snapshot_falls_back_for_blank_anomaly_column(
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
    monkeypatch.setattr(rb, "prepare_buff_data_and_cache", fake_prepare_buff_data_and_cache)

    snapshot = rb._load_runtime_benchmark_snapshot("facade", "101", 12.5)

    assert snapshot.runtime_label == "facade"
    assert snapshot.hotspots["simulator_run_ms"] == 12.5
    assert snapshot.hotspots["damage_report_ms"] >= 0
    assert snapshot.hotspots["buff_report_ms"] >= 0


def test_script_entrypoint_runs_with_json_output(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    script_path = Path("scripts/run_buff_runtime_benchmark.py").resolve()
    captured_kwargs: dict[str, Any] = {}

    def fake_run_runtime_benchmark(**kwargs: Any) -> dict[str, Any]:
        captured_kwargs.update(kwargs)
        report = {
            "team": "fake-team",
            "apl": "./fake.toml",
            "stop_tick": 20,
            "legacy_runtime": "legacy",
            "candidate_runtime": "candidate",
            "total_runtime_ms": {"legacy": 1.0, "candidate": 1.0},
            "hotspots": {"legacy": [], "candidate": []},
            "comparisons": {
                "total_runtime_ms": 0.0,
                "hotspots": {},
                "faster_runtime": "tie",
                "candidate_vs_legacy_ratio": 1.0,
            },
        }
        if kwargs["include_rebuild_counts"]:
            report["buff_runtime_rebuild_counts"] = {"legacy": {}, "candidate": {}}
            report["comparisons"]["buff_runtime_rebuild_counts"] = {}
        return report

    monkeypatch.setattr(rb, "run_runtime_benchmark", fake_run_runtime_benchmark)

    namespace: dict[str, Any] = {"__name__": "__main__", "__file__": str(script_path)}
    argv_before = list(rb.sys.argv)
    try:
        rb.sys.argv = [
            str(script_path),
            "--team",
            "fake-team",
            "--json",
            "--include-rebuild-counts",
        ]
        with pytest.raises(SystemExit) as excinfo:
            exec(script_path.read_text(encoding="utf-8"), namespace)
        assert excinfo.value.code == 0
        output = capsys.readouterr().out
        assert '"team": "fake-team"' in output
        assert '"faster_runtime": "tie"' in output
        assert '"buff_runtime_rebuild_counts"' in output
        assert captured_kwargs["include_rebuild_counts"] is True
    finally:
        rb.sys.argv = argv_before


def test_script_entrypoint_importable_from_scripts_directory():
    script_path = Path("scripts/run_buff_runtime_benchmark.py").resolve()
    content = script_path.read_text(encoding="utf-8")

    assert "sys.path.insert(0, str(PROJECT_ROOT))" in content
    assert "from zsim.utils.runtime_benchmark import main" in content
