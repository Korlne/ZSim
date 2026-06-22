from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any

from zsim.define import config
from zsim.models.session.session_run import CommonCfg
from zsim.simulator import Simulator
from zsim.utils.main_loop_consistency import (
    PROJECT_ROOT,
    RUNTIME_LABEL_CONTRACT,
    _build_session_id,
    _cleanup_result_artifacts,
    _prepare_damage_data_for_consistency,
    _prepare_common_cfg,
    _runtime_selection_contract,
)
from zsim.utils.process_buff_result import prepare_buff_data_and_cache


REPEAT_BENCHMARK_SUMMARY_SCHEMA = "zsim-buff-runtime-repeat-benchmark.v1"
FUTURE_THRESHOLD_MIN_REPEAT_SAMPLES = 5
NO_DEFAULT_ENABLEMENT_STATEMENT = (
    "No default enablement or speedup target is authorized by this PRD."
)


@dataclass(frozen=True)
class RuntimeBenchmarkSnapshot:
    runtime_label: str
    session_id: str
    total_runtime_ms: float
    hotspots: dict[str, float]
    rebuild_counts: dict[str, int] | None = None
    buff_load_loop_scan_metrics: dict[str, int] | None = None


def _run_single_runtime_benchmark_process(
    common_cfg_data: dict[str, Any],
    stop_tick: int,
    include_rebuild_counts: bool = False,
    use_indexed_buff_load_loop: bool = False,
) -> tuple[str, float, dict[str, int] | None, dict[str, int] | None]:
    os.chdir(PROJECT_ROOT)
    common_cfg = CommonCfg.model_validate(common_cfg_data)
    simulator = Simulator(use_indexed_buff_load_loop=use_indexed_buff_load_loop)
    if include_rebuild_counts:
        simulator.enable_buff_runtime_rebuild_counting()
    started_at = time.perf_counter()
    confirmation = simulator.api_run_simulator(
        common_cfg,
        sim_cfg=None,
        stop_tick=stop_tick,
        use_indexed_buff_load_loop=use_indexed_buff_load_loop,
    )
    simulator_runtime_ms = round((time.perf_counter() - started_at) * 1000, 4)
    rebuild_counts = simulator.get_buff_runtime_rebuild_counts() if include_rebuild_counts else None
    scan_metrics = (
        dict(getattr(simulator, "_buff_load_loop_scan_metrics", {}))
        if include_rebuild_counts
        else None
    )
    return confirmation.session_id, simulator_runtime_ms, rebuild_counts, scan_metrics


def _load_runtime_benchmark_snapshot(
    runtime_label: str,
    session_id: str,
    simulator_runtime_ms: float,
    rebuild_counts: dict[str, int] | None = None,
    buff_load_loop_scan_metrics: dict[str, int] | None = None,
) -> RuntimeBenchmarkSnapshot:
    damage_started_at = time.perf_counter()
    _prepare_damage_data_for_consistency(session_id)
    damage_report_ms = round((time.perf_counter() - damage_started_at) * 1000, 4)

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
        rebuild_counts=rebuild_counts,
        buff_load_loop_scan_metrics=buff_load_loop_scan_metrics,
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


def _rebuild_count_buckets(
    buff_runtime_rebuild_counts: dict[str, dict[str, int]] | None,
) -> dict[str, dict[str, int]]:
    source = buff_runtime_rebuild_counts or {}
    return {
        "legacy": dict(source.get("legacy", {})),
        "candidate": dict(source.get("candidate", {})),
    }


def _rebuild_count_comparisons(
    legacy_counts: dict[str, int],
    candidate_counts: dict[str, int],
) -> dict[str, int]:
    counter_names = sorted(set(legacy_counts) | set(candidate_counts))
    return {
        counter_name: int(candidate_counts.get(counter_name, 0))
        - int(legacy_counts.get(counter_name, 0))
        for counter_name in counter_names
    }


def _scan_metric_buckets(
    buff_load_loop_scan_metrics: dict[str, dict[str, int]] | None,
) -> dict[str, dict[str, int]]:
    source = buff_load_loop_scan_metrics or {}
    return {
        "legacy": dict(source.get("legacy", {})),
        "candidate": dict(source.get("candidate", {})),
    }


def _scan_metric_comparisons(
    legacy_metrics: dict[str, int],
    candidate_metrics: dict[str, int],
) -> dict[str, int]:
    metric_names = sorted(set(legacy_metrics) | set(candidate_metrics))
    return {
        metric_name: int(candidate_metrics.get(metric_name, 0))
        - int(legacy_metrics.get(metric_name, 0))
        for metric_name in metric_names
    }


def _numeric_summary(values: Sequence[float | int]) -> dict[str, float]:
    if not values:
        return {"median": 0.0, "min": 0.0, "max": 0.0, "range": 0.0}
    minimum = float(min(values))
    maximum = float(max(values))
    return {
        "median": round(float(median(values)), 4),
        "min": round(minimum, 4),
        "max": round(maximum, 4),
        "range": round(maximum - minimum, 4),
    }


def _summary_with_samples(values: list[float]) -> dict[str, Any]:
    return {
        **_numeric_summary(values),
        "samples": [round(float(value), 4) for value in values],
    }


def _simulator_runtime_ms(report: dict[str, Any], bucket: str) -> float:
    for hotspot in report.get("hotspots", {}).get(bucket, []):
        if hotspot.get("name") == "simulator_run_ms":
            return float(hotspot["runtime_ms"])
    raise KeyError(f"missing simulator_run_ms hotspot for {bucket}")


def _report_rebuild_count_buckets(report: dict[str, Any]) -> dict[str, dict[str, int]]:
    buckets = report.get("buff_runtime_rebuild_counts") or {}
    return {
        "legacy": dict(buckets.get("legacy", {})),
        "candidate": dict(buckets.get("candidate", {})),
    }


def _report_scan_metric_buckets(report: dict[str, Any]) -> dict[str, dict[str, int]]:
    buckets = report.get("buff_load_loop_scan_metrics") or {}
    return {
        "legacy": dict(buckets.get("legacy", {})),
        "candidate": dict(buckets.get("candidate", {})),
    }


def _aggregate_rebuild_count_bucket(
    samples: list[dict[str, dict[str, int]]],
    bucket: str,
) -> dict[str, dict[str, Any]]:
    counter_names = sorted(
        {counter_name for sample in samples for counter_name in sample.get(bucket, {})}
    )
    return {
        counter_name: {
            **_numeric_summary(
                [int(sample.get(bucket, {}).get(counter_name, 0)) for sample in samples]
            ),
            "samples": [int(sample.get(bucket, {}).get(counter_name, 0)) for sample in samples],
        }
        for counter_name in counter_names
    }


def _aggregate_scan_metric_bucket(
    samples: list[dict[str, dict[str, int]]],
    bucket: str,
) -> dict[str, dict[str, Any]]:
    metric_names = sorted(
        {metric_name for sample in samples for metric_name in sample.get(bucket, {})}
    )
    return {
        metric_name: {
            **_numeric_summary(
                [int(sample.get(bucket, {}).get(metric_name, 0)) for sample in samples]
            ),
            "samples": [int(sample.get(bucket, {}).get(metric_name, 0)) for sample in samples],
        }
        for metric_name in metric_names
    }


def _aggregate_scan_metric_value(
    samples: list[dict[str, dict[str, int]]],
    bucket: str,
    metric_name: str,
) -> dict[str, Any]:
    values = [int(sample.get(bucket, {}).get(metric_name, 0)) for sample in samples]
    return {
        **_numeric_summary(values),
        "samples": values,
    }


def build_repeat_runtime_benchmark_summary(
    *,
    reports: list[dict[str, Any]],
    include_rebuild_counts: bool = False,
) -> dict[str, Any]:
    if not reports:
        raise ValueError("repeat benchmark summary requires at least one report")

    first_report = reports[0]
    legacy_simulator_runtime_ms = [_simulator_runtime_ms(report, "legacy") for report in reports]
    candidate_simulator_runtime_ms = [
        _simulator_runtime_ms(report, "candidate") for report in reports
    ]
    rebuild_count_samples = (
        [_report_rebuild_count_buckets(report) for report in reports]
        if include_rebuild_counts
        else []
    )
    scan_metric_samples = (
        [_report_scan_metric_buckets(report) for report in reports]
        if include_rebuild_counts
        else []
    )
    runtime_selection = dict(first_report.get("runtime_selection", RUNTIME_LABEL_CONTRACT))

    samples = []
    for index, report in enumerate(reports, start=1):
        sample = {
            "sample_index": index,
            "total_runtime_ms": dict(report["total_runtime_ms"]),
            "simulator_runtime_ms": {
                "legacy": legacy_simulator_runtime_ms[index - 1],
                "candidate": candidate_simulator_runtime_ms[index - 1],
            },
            "rebuild_count_buckets": (
                rebuild_count_samples[index - 1] if include_rebuild_counts else None
            ),
        }
        if include_rebuild_counts:
            sample["scan_metric_buckets"] = scan_metric_samples[index - 1]
        samples.append(sample)

    summary = {
        "schema": REPEAT_BENCHMARK_SUMMARY_SCHEMA,
        "team": first_report["team"],
        "apl": first_report["apl"],
        "stop_tick": int(first_report["stop_tick"]),
        "sample_count": len(reports),
        "repeat_samples": len(reports),
        "runtime_labels": {
            "legacy": first_report["legacy_runtime"],
            "candidate": first_report["candidate_runtime"],
        },
        "runtime_selection": runtime_selection,
        "opt_in_flag_status": {
            "candidate_use_indexed_buff_load_loop": bool(
                runtime_selection.get("candidate_use_indexed_buff_load_loop", False)
            ),
            "default_off": bool(runtime_selection.get("default_off", True)),
            "default_indexed_execution": runtime_selection.get(
                "default_indexed_execution",
                "blocked",
            ),
        },
        "simulator_runtime_ms": {
            "legacy": _summary_with_samples(legacy_simulator_runtime_ms),
            "candidate": _summary_with_samples(candidate_simulator_runtime_ms),
        },
        "rebuild_count_buckets": {
            "included": include_rebuild_counts,
            "samples": rebuild_count_samples,
            "aggregate": {
                "legacy": _aggregate_rebuild_count_bucket(rebuild_count_samples, "legacy"),
                "candidate": _aggregate_rebuild_count_bucket(rebuild_count_samples, "candidate"),
            },
        },
        "future_threshold_use": {
            "speedup_target_defined": False,
            "minimum_repeat_samples": FUTURE_THRESHOLD_MIN_REPEAT_SAMPLES,
            "noise_reporting": (
                "Report sample_count plus median/min/max/range simulator runtime "
                "for each runtime label before any later threshold is evaluated."
            ),
            "rule": (
                "A later PRD may define numeric thresholds only after at least "
                f"{FUTURE_THRESHOLD_MIN_REPEAT_SAMPLES} repeats and explicit noise "
                "reporting; this baseline does not claim a speedup target. "
                + NO_DEFAULT_ENABLEMENT_STATEMENT
            ),
        },
        "enablement_policy": {
            "default_enablement_authorized": False,
            "speedup_target_authorized": False,
            "statement": NO_DEFAULT_ENABLEMENT_STATEMENT,
        },
        "mismatch_counts": {
            "candidate_plan_mismatch_count": {
                "included": include_rebuild_counts,
                "legacy": (
                    _aggregate_scan_metric_value(
                        scan_metric_samples,
                        "legacy",
                        "candidate_plan_mismatch_count",
                    )
                    if include_rebuild_counts
                    else _summary_with_samples([])
                ),
                "candidate": (
                    _aggregate_scan_metric_value(
                        scan_metric_samples,
                        "candidate",
                        "candidate_plan_mismatch_count",
                    )
                    if include_rebuild_counts
                    else _summary_with_samples([])
                ),
            },
        },
        "samples": samples,
    }
    if include_rebuild_counts:
        summary["scan_metric_buckets"] = {
            "included": True,
            "samples": scan_metric_samples,
            "aggregate": {
                "legacy": _aggregate_scan_metric_bucket(scan_metric_samples, "legacy"),
                "candidate": _aggregate_scan_metric_bucket(scan_metric_samples, "candidate"),
            },
        }
    return summary


def build_runtime_benchmark_report(
    *,
    team: str,
    apl: str,
    stop_tick: int,
    legacy_snapshot: RuntimeBenchmarkSnapshot,
    candidate_snapshot: RuntimeBenchmarkSnapshot,
    include_rebuild_counts: bool = False,
    candidate_use_indexed_buff_load_loop: bool = False,
    buff_runtime_rebuild_counts: dict[str, dict[str, int]] | None = None,
    buff_load_loop_scan_metrics: dict[str, dict[str, int]] | None = None,
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

    comparisons: dict[str, Any] = {
        "total_runtime_ms": total_runtime_delta,
        "hotspots": _hotspot_comparisons(
            legacy_snapshot.hotspots,
            candidate_snapshot.hotspots,
        ),
        "faster_runtime": faster_runtime,
        "candidate_vs_legacy_ratio": speedup_ratio,
    }
    report: dict[str, Any] = {
        "team": team,
        "apl": apl,
        "stop_tick": stop_tick,
        "legacy_runtime": legacy_snapshot.runtime_label,
        "candidate_runtime": candidate_snapshot.runtime_label,
        "runtime_selection": _runtime_selection_contract(
            candidate_use_indexed_buff_load_loop=candidate_use_indexed_buff_load_loop,
        ),
        "total_runtime_ms": {
            "legacy": legacy_snapshot.total_runtime_ms,
            "candidate": candidate_snapshot.total_runtime_ms,
        },
        "hotspots": {
            "legacy": _sorted_hotspots(legacy_snapshot.hotspots),
            "candidate": _sorted_hotspots(candidate_snapshot.hotspots),
        },
        "comparisons": comparisons,
    }
    if include_rebuild_counts:
        count_source = buff_runtime_rebuild_counts
        if count_source is None:
            count_source = {
                "legacy": legacy_snapshot.rebuild_counts or {},
                "candidate": candidate_snapshot.rebuild_counts or {},
            }
        rebuild_counts = _rebuild_count_buckets(count_source)
        report["buff_runtime_rebuild_counts"] = rebuild_counts
        comparisons["buff_runtime_rebuild_counts"] = _rebuild_count_comparisons(
            rebuild_counts["legacy"],
            rebuild_counts["candidate"],
        )
        scan_source = buff_load_loop_scan_metrics
        if scan_source is None:
            scan_source = {
                "legacy": legacy_snapshot.buff_load_loop_scan_metrics or {},
                "candidate": candidate_snapshot.buff_load_loop_scan_metrics or {},
            }
        scan_metrics = _scan_metric_buckets(scan_source)
        report["buff_load_loop_scan_metrics"] = scan_metrics
        comparisons["buff_load_loop_scan_metrics"] = _scan_metric_comparisons(
            scan_metrics["legacy"],
            scan_metrics["candidate"],
        )
    return report


def run_runtime_benchmark(
    *,
    team: str,
    apl: str | None,
    stop_tick: int,
    legacy_runtime: str,
    candidate_runtime: str,
    cleanup: bool = True,
    include_rebuild_counts: bool = False,
    candidate_use_indexed_buff_load_loop: bool = False,
) -> dict[str, Any]:
    os.chdir(PROJECT_ROOT)
    base_cfg = _prepare_common_cfg(team, apl)
    apl_path = base_cfg.apl_path
    snapshots: list[RuntimeBenchmarkSnapshot] = []

    runtime_flags = (False, candidate_use_indexed_buff_load_loop)
    for runtime_label, use_indexed_buff_load_loop in zip(
        (legacy_runtime, candidate_runtime),
        runtime_flags,
        strict=True,
    ):
        session_id = _build_session_id()
        runtime_cfg = base_cfg.model_copy(update={"session_id": session_id}, deep=True)
        runtime_cfg_data = runtime_cfg.model_dump(mode="json")

        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                _run_single_runtime_benchmark_process,
                runtime_cfg_data,
                stop_tick,
                include_rebuild_counts,
                use_indexed_buff_load_loop,
            )
            (
                finished_session_id,
                simulator_runtime_ms,
                rebuild_counts,
                scan_metrics,
            ) = future.result()

        try:
            snapshots.append(
                _load_runtime_benchmark_snapshot(
                    runtime_label,
                    finished_session_id,
                    simulator_runtime_ms,
                    rebuild_counts,
                    scan_metrics,
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
        include_rebuild_counts=include_rebuild_counts,
        candidate_use_indexed_buff_load_loop=candidate_use_indexed_buff_load_loop,
    )


def run_repeated_runtime_benchmark(
    *,
    team: str,
    apl: str | None,
    stop_tick: int,
    legacy_runtime: str,
    candidate_runtime: str,
    repeat_samples: int,
    cleanup: bool = True,
    include_rebuild_counts: bool = False,
    candidate_use_indexed_buff_load_loop: bool = False,
) -> dict[str, Any]:
    if repeat_samples < 1:
        raise ValueError("repeat_samples must be at least 1")
    reports = [
        run_runtime_benchmark(
            team=team,
            apl=apl,
            stop_tick=stop_tick,
            legacy_runtime=legacy_runtime,
            candidate_runtime=candidate_runtime,
            cleanup=cleanup,
            include_rebuild_counts=include_rebuild_counts,
            candidate_use_indexed_buff_load_loop=candidate_use_indexed_buff_load_loop,
        )
        for _ in range(repeat_samples)
    ]
    return build_repeat_runtime_benchmark_summary(
        reports=reports,
        include_rebuild_counts=include_rebuild_counts,
    )


def write_repeat_runtime_benchmark_summary(
    path: str | Path,
    summary: dict[str, Any],
) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be at least 1")
    return parsed


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
        help="First run label to record in the report; this does not select a runtime.",
    )
    parser.add_argument(
        "--candidate-runtime",
        default="candidate",
        help="Second run label to record in the report; this does not select a runtime.",
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
    parser.add_argument(
        "--repeat-samples",
        type=_positive_int,
        default=1,
        help="Run this many label-only benchmark samples before summarizing.",
    )
    parser.add_argument(
        "--summary-json",
        default=None,
        help="Write a repeat benchmark JSON summary artifact to this path.",
    )
    parser.add_argument(
        "--include-rebuild-counts",
        action="store_true",
        help="Include Buff runtime rebuild count and BuffLoadLoop scan metric buckets in the report.",
    )
    parser.add_argument(
        "--candidate-use-indexed-buff-load-loop",
        action="store_true",
        help=(
            "Explicitly request indexed BuffLoadLoop for the candidate run only; "
            "omitting this keeps both runs on the default current path."
        ),
    )
    return parser


def _format_human_report(report: dict[str, Any]) -> str:
    lines = [
        f"team: {report['team']}",
        f"apl: {report['apl']}",
        f"stop_tick: {report['stop_tick']}",
        "runtime_selection: "
        + report.get("runtime_selection", {}).get("mode", "label-only-current-runtime"),
        (
            "total_runtime_ms: "
            f"{report['legacy_runtime']}={report['total_runtime_ms']['legacy']}, "
            f"{report['candidate_runtime']}={report['total_runtime_ms']['candidate']}"
        ),
        f"faster_runtime: {report['comparisons']['faster_runtime']}",
        "hotspot_deltas: "
        + json.dumps(report["comparisons"]["hotspots"], ensure_ascii=False, sort_keys=True),
    ]
    if "buff_runtime_rebuild_counts" in report:
        lines.append(
            "buff_runtime_rebuild_counts: "
            + json.dumps(report["buff_runtime_rebuild_counts"], ensure_ascii=False, sort_keys=True)
        )
        if "buff_runtime_rebuild_counts" in report["comparisons"]:
            lines.append(
                "buff_runtime_rebuild_count_deltas: "
                + json.dumps(
                    report["comparisons"]["buff_runtime_rebuild_counts"],
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
    if "buff_load_loop_scan_metrics" in report:
        lines.append(
            "buff_load_loop_scan_metrics: "
            + json.dumps(report["buff_load_loop_scan_metrics"], ensure_ascii=False, sort_keys=True)
        )
        if "buff_load_loop_scan_metrics" in report["comparisons"]:
            lines.append(
                "buff_load_loop_scan_metric_deltas: "
                + json.dumps(
                    report["comparisons"]["buff_load_loop_scan_metrics"],
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
    return "\n".join(lines)


def _format_repeat_summary(summary: dict[str, Any]) -> str:
    labels = summary["runtime_labels"]
    runtimes = summary["simulator_runtime_ms"]
    policy = summary["future_threshold_use"]
    lines = [
        f"team: {summary['team']}",
        f"apl: {summary['apl']}",
        f"stop_tick: {summary['stop_tick']}",
        f"sample_count: {summary['sample_count']}",
        "runtime_selection: "
        + summary.get("runtime_selection", {}).get("mode", "label-only-current-runtime"),
        (
            "simulator_runtime_ms: "
            f"{labels['legacy']} median={runtimes['legacy']['median']} "
            f"min={runtimes['legacy']['min']} max={runtimes['legacy']['max']}; "
            f"{labels['candidate']} median={runtimes['candidate']['median']} "
            f"min={runtimes['candidate']['min']} max={runtimes['candidate']['max']}"
        ),
    ]
    rebuild_counts = summary.get("rebuild_count_buckets", {})
    if rebuild_counts.get("included"):
        lines.append(
            "rebuild_count_buckets: "
            + json.dumps(rebuild_counts["aggregate"], ensure_ascii=False, sort_keys=True)
        )
    scan_metrics = summary.get("scan_metric_buckets", {})
    if scan_metrics.get("included"):
        lines.append(
            "scan_metric_buckets: "
            + json.dumps(scan_metrics["aggregate"], ensure_ascii=False, sort_keys=True)
        )
    lines.append(
        "future_threshold_use: "
        f"speedup_target_defined={policy['speedup_target_defined']}; "
        f"minimum_repeat_samples={policy['minimum_repeat_samples']}; " + policy["noise_reporting"]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repeat_mode = args.repeat_samples > 1 or args.summary_json is not None
    if repeat_mode:
        summary = run_repeated_runtime_benchmark(
            team=args.team,
            apl=args.apl,
            stop_tick=args.stop_tick,
            legacy_runtime=args.legacy_runtime,
            candidate_runtime=args.candidate_runtime,
            repeat_samples=args.repeat_samples,
            cleanup=not args.keep_artifacts,
            include_rebuild_counts=args.include_rebuild_counts,
            candidate_use_indexed_buff_load_loop=args.candidate_use_indexed_buff_load_loop,
        )
        if args.summary_json:
            write_repeat_runtime_benchmark_summary(args.summary_json, summary)
        if args.json:
            print(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2))
        else:
            print(_format_repeat_summary(summary))
        return 0

    report = run_runtime_benchmark(
        team=args.team,
        apl=args.apl,
        stop_tick=args.stop_tick,
        legacy_runtime=args.legacy_runtime,
        candidate_runtime=args.candidate_runtime,
        cleanup=not args.keep_artifacts,
        include_rebuild_counts=args.include_rebuild_counts,
        candidate_use_indexed_buff_load_loop=args.candidate_use_indexed_buff_load_loop,
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
    "build_repeat_runtime_benchmark_summary",
    "build_runtime_benchmark_report",
    "main",
    "run_repeated_runtime_benchmark",
    "run_runtime_benchmark",
    "write_repeat_runtime_benchmark_summary",
]


if __name__ == "__main__":
    sys.exit(main())
