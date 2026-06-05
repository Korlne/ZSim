from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import Any

from zsim.define import config
from zsim.models.session.session_run import CommonCfg
from zsim.simulator import Simulator
from zsim.utils.main_loop_consistency import (
    PROJECT_ROOT,
    _build_session_id,
    _cleanup_result_artifacts,
    _prepare_common_cfg,
)
from zsim.utils.process_buff_result import prepare_buff_data_and_cache
from zsim.utils.process_dmg_result import prepare_dmg_data_and_cache


@dataclass(frozen=True)
class RuntimeBenchmarkSnapshot:
    runtime_label: str
    session_id: str
    total_runtime_ms: float
    hotspots: dict[str, float]


def _run_single_runtime_benchmark_process(
    common_cfg_data: dict[str, Any],
    stop_tick: int,
) -> tuple[str, float]:
    os.chdir(PROJECT_ROOT)
    common_cfg = CommonCfg.model_validate(common_cfg_data)
    simulator = Simulator()
    started_at = time.perf_counter()
    confirmation = simulator.api_run_simulator(common_cfg, sim_cfg=None, stop_tick=stop_tick)
    simulator_runtime_ms = round((time.perf_counter() - started_at) * 1000, 4)
    return confirmation.session_id, simulator_runtime_ms


def _load_runtime_benchmark_snapshot(
    runtime_label: str,
    session_id: str,
    simulator_runtime_ms: float,
) -> RuntimeBenchmarkSnapshot:
    damage_started_at = time.perf_counter()
    dmg_data = prepare_dmg_data_and_cache(session_id)
    damage_report_ms = round((time.perf_counter() - damage_started_at) * 1000, 4)
    if dmg_data is None:
        raise RuntimeError(f"no damage report was generated for session '{session_id}'")

    buff_started_at = time.perf_counter()
    asyncio.run(prepare_buff_data_and_cache(session_id))
    buff_report_ms = round((time.perf_counter() - buff_started_at) * 1000, 4)

    hotspots = {
        "simulator_run_ms": simulator_runtime_ms,
        "damage_report_ms": damage_report_ms,
        "buff_report_ms": buff_report_ms,
    }

    return RuntimeBenchmarkSnapshot(
        runtime_label=runtime_label,
        session_id=session_id,
        total_runtime_ms=round(sum(hotspots.values()), 4),
        hotspots=hotspots,
    )


def _sorted_hotspots(hotspots: dict[str, float]) -> list[dict[str, float | str]]:
    hotspot_names = sorted(hotspots, key=lambda name: (-hotspots[name], name))
    return [
        {
            "name": hotspot_name,
            "runtime_ms": hotspots[hotspot_name],
        }
        for hotspot_name in hotspot_names
    ]


def _hotspot_comparisons(
    legacy_hotspots: dict[str, float],
    candidate_hotspots: dict[str, float],
) -> dict[str, float]:
    hotspot_names = sorted(set(legacy_hotspots) | set(candidate_hotspots))
    return {
        hotspot_name: round(
            candidate_hotspots.get(hotspot_name, 0.0) - legacy_hotspots.get(hotspot_name, 0.0),
            4,
        )
        for hotspot_name in hotspot_names
    }


def build_runtime_benchmark_report(
    *,
    team: str,
    apl: str,
    stop_tick: int,
    legacy_snapshot: RuntimeBenchmarkSnapshot,
    candidate_snapshot: RuntimeBenchmarkSnapshot,
) -> dict[str, Any]:
    total_runtime_delta = round(
        candidate_snapshot.total_runtime_ms - legacy_snapshot.total_runtime_ms,
        4,
    )
    faster_runtime = "tie"
    if legacy_snapshot.total_runtime_ms < candidate_snapshot.total_runtime_ms:
        faster_runtime = legacy_snapshot.runtime_label
    elif candidate_snapshot.total_runtime_ms < legacy_snapshot.total_runtime_ms:
        faster_runtime = candidate_snapshot.runtime_label

    speedup_ratio = 1.0
    if legacy_snapshot.total_runtime_ms != 0:
        speedup_ratio = round(
            candidate_snapshot.total_runtime_ms / legacy_snapshot.total_runtime_ms,
            4,
        )

    return {
        "team": team,
        "apl": apl,
        "stop_tick": stop_tick,
        "legacy_runtime": legacy_snapshot.runtime_label,
        "candidate_runtime": candidate_snapshot.runtime_label,
        "total_runtime_ms": {
            "legacy": legacy_snapshot.total_runtime_ms,
            "candidate": candidate_snapshot.total_runtime_ms,
        },
        "hotspots": {
            "legacy": _sorted_hotspots(legacy_snapshot.hotspots),
            "candidate": _sorted_hotspots(candidate_snapshot.hotspots),
        },
        "comparisons": {
            "total_runtime_ms": total_runtime_delta,
            "hotspots": _hotspot_comparisons(
                legacy_snapshot.hotspots,
                candidate_snapshot.hotspots,
            ),
            "faster_runtime": faster_runtime,
            "candidate_vs_legacy_ratio": speedup_ratio,
        },
    }


def run_runtime_benchmark(
    *,
    team: str,
    apl: str | None,
    stop_tick: int,
    legacy_runtime: str,
    candidate_runtime: str,
    cleanup: bool = True,
) -> dict[str, Any]:
    os.chdir(PROJECT_ROOT)
    base_cfg = _prepare_common_cfg(team, apl)
    apl_path = base_cfg.apl_path
    snapshots: list[RuntimeBenchmarkSnapshot] = []

    for runtime_label in (legacy_runtime, candidate_runtime):
        session_id = _build_session_id()
        runtime_cfg = base_cfg.model_copy(update={"session_id": session_id}, deep=True)
        runtime_cfg_data = runtime_cfg.model_dump(mode="json")

        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                _run_single_runtime_benchmark_process,
                runtime_cfg_data,
                stop_tick,
            )
            finished_session_id, simulator_runtime_ms = future.result()

        try:
            snapshots.append(
                _load_runtime_benchmark_snapshot(
                    runtime_label,
                    finished_session_id,
                    simulator_runtime_ms,
                )
            )
        finally:
            if cleanup:
                _cleanup_result_artifacts(finished_session_id)

    return build_runtime_benchmark_report(
        team=team,
        apl=apl_path,
        stop_tick=stop_tick,
        legacy_snapshot=snapshots[0],
        candidate_snapshot=snapshots[1],
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a Buff runtime benchmark comparison")
    parser.add_argument("--team", required=True, help="Registered team name to simulate")
    parser.add_argument(
        "--apl",
        default=None,
        help="Optional APL path override. Defaults to the selected team's config.",
    )
    parser.add_argument(
        "--stop-tick",
        type=int,
        default=config.stop_tick,
        help="Stop tick for each benchmarked runtime run.",
    )
    parser.add_argument(
        "--legacy-runtime",
        default="legacy",
        help="Legacy runtime label to record in the report.",
    )
    parser.add_argument(
        "--candidate-runtime",
        default="candidate",
        help="Candidate runtime label to record in the report.",
    )
    parser.add_argument(
        "--keep-artifacts",
        action="store_true",
        help="Keep raw results/<session_id> artifacts after the report is generated.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the full JSON report to stdout.",
    )
    return parser


def _format_human_report(report: dict[str, Any]) -> str:
    lines = [
        f"team: {report['team']}",
        f"apl: {report['apl']}",
        f"stop_tick: {report['stop_tick']}",
        (
            "total_runtime_ms: "
            f"{report['legacy_runtime']}={report['total_runtime_ms']['legacy']}, "
            f"{report['candidate_runtime']}={report['total_runtime_ms']['candidate']}"
        ),
        f"faster_runtime: {report['comparisons']['faster_runtime']}",
        "hotspot_deltas: "
        + json.dumps(report["comparisons"]["hotspots"], ensure_ascii=False, sort_keys=True),
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    report = run_runtime_benchmark(
        team=args.team,
        apl=args.apl,
        stop_tick=args.stop_tick,
        legacy_runtime=args.legacy_runtime,
        candidate_runtime=args.candidate_runtime,
        cleanup=not args.keep_artifacts,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print(_format_human_report(report))
    return 0


__all__ = [
    "PROJECT_ROOT",
    "RuntimeBenchmarkSnapshot",
    "build_parser",
    "build_runtime_benchmark_report",
    "main",
    "run_runtime_benchmark",
]


if __name__ == "__main__":
    sys.exit(main())
