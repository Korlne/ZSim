from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from itertools import count
from pathlib import Path
from typing import Any

import polars as pl

from zsim.define import config, results_dir
from zsim.models.session.session_run import CommonCfg
from zsim.simulator import Simulator
from zsim.utils.process_buff_result import prepare_buff_data_and_cache
from zsim.utils.process_dmg_result import prepare_dmg_data_and_cache, sort_df_by_UUID

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_BUFF_TIMELINE_SAMPLE_LIMIT = 20
_SESSION_ID_COUNTER = count(1)


@dataclass(frozen=True)
class RuntimeSnapshot:
    runtime_label: str
    session_id: str
    total_damage: float
    event_counts: dict[str, Any]
    buff_timeline: dict[str, list[dict[str, Any]]]


def _build_session_id() -> str:
    """生成与现有结果处理链兼容的纯数字 session_id。"""
    return f"{time.time_ns()}{next(_SESSION_ID_COUNTER):03d}"


def _load_team_config(team_name: str) -> CommonCfg:
    from tests.teams import auto_register_teams

    registry = auto_register_teams()
    team_config = registry.get_team(team_name)
    if team_config is None:
        available = ", ".join(sorted(registry.list_team_names()))
        raise ValueError(f"unknown team '{team_name}'. available teams: {available}")
    return team_config.create_config()


def _prepare_common_cfg(team: str, apl: str | None) -> CommonCfg:
    common_cfg = _load_team_config(team)
    if apl is None:
        return common_cfg
    return common_cfg.model_copy(update={"apl_path": apl}, deep=True)


def _run_single_runtime_process(common_cfg_data: dict[str, Any], stop_tick: int) -> str:
    os.chdir(PROJECT_ROOT)
    common_cfg = CommonCfg.model_validate(common_cfg_data)
    simulator = Simulator()
    confirmation = simulator.api_run_simulator(common_cfg, sim_cfg=None, stop_tick=stop_tick)
    return confirmation.session_id


def _summarize_event_counts(
    dmg_result_df: pl.DataFrame,
    uuid_df: pl.DataFrame,
) -> dict[str, Any]:
    def count_by(df: pl.DataFrame, column: str) -> dict[str, int]:
        if column not in df.columns:
            return {}
        grouped = df.filter(pl.col(column).is_not_null()).group_by(column).len().sort(column)
        return {str(row[column]): int(row["len"]) for row in grouped.iter_rows(named=True)}

    anomaly_total = 0
    if "is_anomaly" in uuid_df.columns:
        anomaly_total = int(uuid_df.filter(pl.col("is_anomaly") == True).height)  # noqa: E712

    disorder_total = 0
    if "is_disorder" in dmg_result_df.columns:
        disorder_total = int(
            dmg_result_df.filter(pl.col("is_disorder").fill_null(False) == True).height  # noqa: E712
        )

    return {
        "total": int(uuid_df.height),
        "anomaly_total": anomaly_total,
        "disorder_total": disorder_total,
        "by_skill_tag": count_by(uuid_df, "skill_tag"),
        "by_skill_name": count_by(uuid_df, "skill_cn_name"),
        "by_element_type": count_by(uuid_df, "element_type"),
    }


def _load_damage_result_df(session_id: str) -> pl.DataFrame:
    csv_file_path = Path(results_dir) / session_id / "damage.csv"
    lf = pl.scan_csv(csv_file_path)
    schema_names = lf.collect_schema().names()
    lf = lf.rename({col: col.replace("\r", "").replace("\n", "").strip() for col in schema_names})
    return lf.collect()


def _normalize_consistency_damage_df(dmg_result_df: pl.DataFrame) -> pl.DataFrame:
    if "is_anomaly" not in dmg_result_df.columns:
        return dmg_result_df.with_columns(pl.lit(False).alias("is_anomaly"))
    if dmg_result_df["is_anomaly"].is_null().all():
        return dmg_result_df.with_columns(pl.lit(False).alias("is_anomaly"))
    return dmg_result_df.with_columns(pl.col("is_anomaly").fill_null(False))


def _prepare_damage_data_for_consistency(session_id: str) -> tuple[pl.DataFrame, pl.DataFrame]:
    try:
        dmg_data = prepare_dmg_data_and_cache(session_id)
    except ValueError as exc:
        if "is_anomaly" not in str(exc):
            raise
        dmg_data = None

    if dmg_data is not None:
        dmg_result_df = dmg_data["dmg_result_df"]
        uuid_df = dmg_data["uuid_df"]
        if not isinstance(dmg_result_df, pl.DataFrame) or not isinstance(uuid_df, pl.DataFrame):
            raise RuntimeError(f"unexpected damage payload for session '{session_id}'")
        return dmg_result_df, uuid_df

    dmg_result_df = _normalize_consistency_damage_df(_load_damage_result_df(session_id))
    uuid_df = sort_df_by_UUID(dmg_result_df)
    return dmg_result_df, uuid_df


def _load_runtime_snapshot(runtime_label: str, session_id: str) -> RuntimeSnapshot:
    dmg_result_df, uuid_df = _prepare_damage_data_for_consistency(session_id)
    buff_timeline = asyncio.run(prepare_buff_data_and_cache(session_id)) or {}
    total_damage = round(float(uuid_df["dmg_expect_sum"].fill_null(0).sum()), 4)
    event_counts = _summarize_event_counts(dmg_result_df, uuid_df)

    return RuntimeSnapshot(
        runtime_label=runtime_label,
        session_id=session_id,
        total_damage=total_damage,
        event_counts=event_counts,
        buff_timeline=buff_timeline,
    )


def _event_count_differences(
    legacy_counts: dict[str, Any],
    candidate_counts: dict[str, Any],
) -> dict[str, Any]:
    def diff_scalar(key: str) -> int:
        return int(candidate_counts.get(key, 0)) - int(legacy_counts.get(key, 0))

    def diff_map(key: str) -> dict[str, int]:
        legacy_map = legacy_counts.get(key, {})
        candidate_map = candidate_counts.get(key, {})
        keys = sorted(set(legacy_map) | set(candidate_map))
        return {
            item_key: int(candidate_map.get(item_key, 0)) - int(legacy_map.get(item_key, 0))
            for item_key in keys
            if int(candidate_map.get(item_key, 0)) != int(legacy_map.get(item_key, 0))
        }

    return {
        "total": diff_scalar("total"),
        "anomaly_total": diff_scalar("anomaly_total"),
        "disorder_total": diff_scalar("disorder_total"),
        "by_skill_tag": diff_map("by_skill_tag"),
        "by_skill_name": diff_map("by_skill_name"),
        "by_element_type": diff_map("by_element_type"),
    }


def _flatten_buff_timeline(
    buff_timeline: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    for source, entries in sorted(buff_timeline.items()):
        for entry in entries:
            flattened.append(
                {
                    "source": source,
                    "task": str(entry.get("Task", "")),
                    "start": int(entry.get("Start", 0)),
                    "finish": int(entry.get("Finish", 0)),
                    "value": float(entry.get("Value", 0.0)),
                }
            )
    flattened.sort(
        key=lambda item: (
            item["source"],
            item["task"],
            item["start"],
            item["finish"],
            item["value"],
        )
    )
    return flattened


def _summarize_buff_timeline_differences(
    legacy_timeline: dict[str, list[dict[str, Any]]],
    candidate_timeline: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    legacy_flat = _flatten_buff_timeline(legacy_timeline)
    candidate_flat = _flatten_buff_timeline(candidate_timeline)
    legacy_counter = Counter(tuple(item.items()) for item in legacy_flat)
    candidate_counter = Counter(tuple(item.items()) for item in candidate_flat)

    def expand(counter: Counter[tuple[tuple[str, Any], ...]]) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for flattened_item, item_count in sorted(counter.items()):
            item = dict(flattened_item)
            for _ in range(item_count):
                items.append(item)
        return items

    legacy_only = expand(legacy_counter - candidate_counter)
    candidate_only = expand(candidate_counter - legacy_counter)

    return {
        "legacy_only_count": len(legacy_only),
        "candidate_only_count": len(candidate_only),
        "sample_legacy_only": legacy_only[:_BUFF_TIMELINE_SAMPLE_LIMIT],
        "sample_candidate_only": candidate_only[:_BUFF_TIMELINE_SAMPLE_LIMIT],
    }


def build_consistency_report(
    *,
    team: str,
    apl: str,
    stop_tick: int,
    legacy_snapshot: RuntimeSnapshot,
    candidate_snapshot: RuntimeSnapshot,
) -> dict[str, Any]:
    event_count_differences = _event_count_differences(
        legacy_snapshot.event_counts, candidate_snapshot.event_counts
    )
    buff_timeline_differences = _summarize_buff_timeline_differences(
        legacy_snapshot.buff_timeline,
        candidate_snapshot.buff_timeline,
    )
    total_damage_delta = round(candidate_snapshot.total_damage - legacy_snapshot.total_damage, 4)

    has_event_differences = any(
        bool(value) for value in event_count_differences.values()
    )

    return {
        "team": team,
        "apl": apl,
        "stop_tick": stop_tick,
        "legacy_runtime": legacy_snapshot.runtime_label,
        "candidate_runtime": candidate_snapshot.runtime_label,
        "total_damage": {
            "legacy": legacy_snapshot.total_damage,
            "candidate": candidate_snapshot.total_damage,
        },
        "event_counts": {
            "legacy": legacy_snapshot.event_counts,
            "candidate": candidate_snapshot.event_counts,
        },
        "buff_timeline": {
            "legacy": legacy_snapshot.buff_timeline,
            "candidate": candidate_snapshot.buff_timeline,
        },
        "differences": {
            "matches": total_damage_delta == 0
            and not has_event_differences
            and buff_timeline_differences["legacy_only_count"] == 0
            and buff_timeline_differences["candidate_only_count"] == 0,
            "total_damage": total_damage_delta,
            "event_counts": event_count_differences,
            "buff_timeline": buff_timeline_differences,
        },
    }


def _cleanup_result_artifacts(session_id: str) -> None:
    result_path = Path(results_dir) / session_id
    if result_path.exists():
        shutil.rmtree(result_path, ignore_errors=True)


def run_main_loop_consistency(
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
    snapshots: list[RuntimeSnapshot] = []

    for runtime_label in (legacy_runtime, candidate_runtime):
        session_id = _build_session_id()
        runtime_cfg = base_cfg.model_copy(update={"session_id": session_id}, deep=True)
        runtime_cfg_data = runtime_cfg.model_dump(mode="json")

        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_run_single_runtime_process, runtime_cfg_data, stop_tick)
            finished_session_id = future.result()

        try:
            snapshots.append(_load_runtime_snapshot(runtime_label, finished_session_id))
        finally:
            if cleanup:
                _cleanup_result_artifacts(finished_session_id)

    return build_consistency_report(
        team=team,
        apl=apl_path,
        stop_tick=stop_tick,
        legacy_snapshot=snapshots[0],
        candidate_snapshot=snapshots[1],
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a Buff main-loop consistency comparison")
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
        help="Stop tick for each runtime run.",
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
            "total_damage: "
            f"{report['legacy_runtime']}={report['total_damage']['legacy']}, "
            f"{report['candidate_runtime']}={report['total_damage']['candidate']}"
        ),
        f"matches: {report['differences']['matches']}",
        "event_count_differences: "
        + json.dumps(report["differences"]["event_counts"], ensure_ascii=False, sort_keys=True),
        "buff_timeline_differences: "
        + json.dumps(report["differences"]["buff_timeline"], ensure_ascii=False, sort_keys=True),
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    report = run_main_loop_consistency(
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
    "RuntimeSnapshot",
    "build_consistency_report",
    "build_parser",
    "main",
    "run_main_loop_consistency",
]


if __name__ == "__main__":
    sys.exit(main())
