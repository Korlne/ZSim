from __future__ import annotations

import argparse
import asyncio
import json
import math
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
from zsim.models.session.session_result import (
    BUFF_TIMELINE_PUBLIC_FIELDS,
    normalize_buff_timeline_entry as normalize_result_buff_timeline_entry,
    normalize_buff_timeline_payload as normalize_result_buff_timeline_payload,
    normalize_buff_timeline_value as normalize_result_buff_timeline_value,
)
from zsim.models.session.session_run import CommonCfg
from zsim.simulator import Simulator
from zsim.utils.process_buff_result import _prepare_buff_timeline_data, prepare_buff_data_and_cache
from zsim.utils.process_dmg_result import (
    _normalize_damage_schema,
    prepare_dmg_data_and_cache,
    sort_df_by_UUID,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_BUFF_TIMELINE_SAMPLE_LIMIT = 20
_DAMAGE_DIFF_SAMPLE_LIMIT = 5
_DAMAGE_UUID_COMPARE_FIELDS = (
    "dmg_expect_sum",
    "stun_sum",
    "buildup_sum",
    "skill_tag",
    "skill_cn_name",
    "element_type",
    "is_anomaly",
)
_SESSION_ID_COUNTER = count(1)
MULTI_TEAM_CONSISTENCY_SCHEMA = "zsim-buffload-opt-in-multi-team-consistency.v1"
EXTERNAL_GOLDEN_PARITY_SCHEMA = "zsim-external-golden-parity.v1"
RUNTIME_LABEL_CONTRACT = {
    "mode": "label-only-current-runtime",
    "description": (
        "baseline_runtime and candidate_runtime are report labels only; "
        "both executions use the Simulator default Buff runtime."
    ),
    "compatibility_aliases": {
        "legacy_runtime": "report compatibility alias for baseline_runtime",
    },
}


@dataclass(frozen=True)
class RuntimeSnapshot:
    runtime_label: str
    session_id: str
    total_damage: float
    event_counts: dict[str, Any]
    buff_timeline: dict[str, list[dict[str, Any]]]


@dataclass(frozen=True)
class BuffTimelineParityData:
    present: bool
    source_type: str
    source_paths: list[Path]
    timeline: dict[str, list[dict[str, Any]]]
    summary: dict[str, Any]
    records: list[dict[str, Any]]


def _build_session_id() -> str:
    """生成与现有结果处理链兼容的纯数字 session_id。"""
    return f"{time.time_ns()}{next(_SESSION_ID_COUNTER):03d}"


def _runtime_selection_contract(
    *,
    candidate_use_indexed_buff_load_loop: bool = False,
) -> dict[str, Any]:
    if not candidate_use_indexed_buff_load_loop:
        return dict(RUNTIME_LABEL_CONTRACT)
    return {
        **RUNTIME_LABEL_CONTRACT,
        "mode": "candidate-explicit-opt-in-indexed-buff-load-loop",
        "candidate_use_indexed_buff_load_loop": True,
        "default_off": True,
        "default_indexed_execution": "blocked",
    }


def _resolve_baseline_runtime_label(
    *,
    baseline_runtime: str | None,
    legacy_runtime: str | None,
    default: str,
) -> str:
    if baseline_runtime is not None:
        return baseline_runtime
    if legacy_runtime is not None:
        return legacy_runtime
    return default


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


def _run_single_runtime_process(
    common_cfg_data: dict[str, Any],
    stop_tick: int,
    use_indexed_buff_load_loop: bool = False,
) -> str:
    os.chdir(PROJECT_ROOT)
    common_cfg = CommonCfg.model_validate(common_cfg_data)
    simulator = Simulator(use_indexed_buff_load_loop=use_indexed_buff_load_loop)
    confirmation = simulator.api_run_simulator(
        common_cfg,
        sim_cfg=None,
        stop_tick=stop_tick,
        use_indexed_buff_load_loop=use_indexed_buff_load_loop,
    )
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
    return _normalize_damage_schema(dmg_result_df)


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
    candidate_use_indexed_buff_load_loop: bool = False,
) -> dict[str, Any]:
    event_count_differences = _event_count_differences(
        legacy_snapshot.event_counts, candidate_snapshot.event_counts
    )
    buff_timeline_differences = _summarize_buff_timeline_differences(
        legacy_snapshot.buff_timeline,
        candidate_snapshot.buff_timeline,
    )
    total_damage_delta = round(candidate_snapshot.total_damage - legacy_snapshot.total_damage, 4)

    has_event_differences = any(bool(value) for value in event_count_differences.values())
    baseline_label = legacy_snapshot.runtime_label

    return {
        "team": team,
        "apl": apl,
        "stop_tick": stop_tick,
        "baseline_runtime": baseline_label,
        "legacy_runtime": baseline_label,
        "candidate_runtime": candidate_snapshot.runtime_label,
        "runtime_selection": _runtime_selection_contract(
            candidate_use_indexed_buff_load_loop=candidate_use_indexed_buff_load_loop,
        ),
        "total_damage": {
            "baseline": legacy_snapshot.total_damage,
            "legacy": legacy_snapshot.total_damage,
            "candidate": candidate_snapshot.total_damage,
        },
        "event_counts": {
            "baseline": legacy_snapshot.event_counts,
            "legacy": legacy_snapshot.event_counts,
            "candidate": candidate_snapshot.event_counts,
        },
        "buff_timeline": {
            "baseline": legacy_snapshot.buff_timeline,
            "legacy": legacy_snapshot.buff_timeline,
            "candidate": candidate_snapshot.buff_timeline,
        },
        "report_compatibility": {
            "legacy_runtime": "alias for baseline_runtime",
            "legacy": "alias bucket for baseline",
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


def _event_count_differences_match(event_count_differences: dict[str, Any]) -> bool:
    return not any(bool(value) for value in event_count_differences.values())


def _buff_timeline_differences_match(buff_timeline_differences: dict[str, Any]) -> bool:
    return (
        int(buff_timeline_differences.get("legacy_only_count", 0)) == 0
        and int(buff_timeline_differences.get("candidate_only_count", 0)) == 0
    )


def _team_consistency_summary(report: dict[str, Any]) -> dict[str, Any]:
    differences = report["differences"]
    event_count_differences = differences["event_counts"]
    buff_timeline_differences = differences["buff_timeline"]
    runtime_selection = dict(report.get("runtime_selection", {}))
    candidate_opt_in = bool(runtime_selection.get("candidate_use_indexed_buff_load_loop", False))
    matches = bool(differences["matches"])

    return {
        "team": report["team"],
        "apl": report["apl"],
        "stop_tick": int(report["stop_tick"]),
        "runtime_labels": {
            "default_path": report.get("baseline_runtime", report["legacy_runtime"]),
            "opt_in_indexed_path": report["candidate_runtime"],
        },
        "runtime_selection": runtime_selection,
        "candidate_use_indexed_buff_load_loop": candidate_opt_in,
        "opt_in_flag_status": (
            "candidate_explicit_opt_in" if candidate_opt_in else "default_off_label_only"
        ),
        "damage_parity": {
            "default_path": report["total_damage"].get(
                "baseline",
                report["total_damage"]["legacy"],
            ),
            "opt_in_indexed_path": report["total_damage"]["candidate"],
            "delta": differences["total_damage"],
            "matches": differences["total_damage"] == 0,
        },
        "event_count_parity": {
            "matches": _event_count_differences_match(event_count_differences),
            "differences": event_count_differences,
        },
        "buff_timeline_parity": {
            "matches": _buff_timeline_differences_match(buff_timeline_differences),
            "legacy_only_count": buff_timeline_differences["legacy_only_count"],
            "candidate_only_count": buff_timeline_differences["candidate_only_count"],
            "sample_legacy_only": buff_timeline_differences["sample_legacy_only"],
            "sample_candidate_only": buff_timeline_differences["sample_candidate_only"],
        },
        "mismatch_count": 0 if matches else 1,
        "matches": matches,
    }


def build_multi_team_consistency_summary(
    *,
    reports: list[dict[str, Any]],
    generated_at: str | None = None,
) -> dict[str, Any]:
    if not reports:
        raise ValueError("multi-team consistency summary requires at least one report")

    matrix_results = [_team_consistency_summary(report) for report in reports]
    teams = list(dict.fromkeys(result["team"] for result in matrix_results))
    mismatch_results = [result for result in matrix_results if not result["matches"]]
    mismatch_teams = list(dict.fromkeys(result["team"] for result in mismatch_results))
    stop_ticks = sorted({int(result["stop_tick"]) for result in matrix_results})
    mismatch_count = sum(int(result["mismatch_count"]) for result in matrix_results)

    return {
        "schema": MULTI_TEAM_CONSISTENCY_SCHEMA,
        "generated_at": generated_at or time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "team_count": len(teams),
        "teams": teams,
        "stop_ticks": stop_ticks,
        "stop_tick_count": len(stop_ticks),
        "matrix_row_count": len(matrix_results),
        "required_minimum_stop_tick": 120,
        "minimum_stop_tick_met": all(stop_tick >= 120 for stop_tick in stop_ticks),
        "runtime_paths": {
            "default_path": "default current BuffLoadLoop execution",
            "opt_in_indexed_path": "candidate explicit opt-in indexed BuffLoadLoop execution",
        },
        "candidate_use_indexed_buff_load_loop": all(
            bool(
                report.get("runtime_selection", {}).get(
                    "candidate_use_indexed_buff_load_loop", False
                )
            )
            for report in reports
        ),
        "default_indexed_execution": "blocked",
        "mismatch_count": mismatch_count,
        "mismatch_teams": mismatch_teams,
        "mismatch_matrix_keys": [
            {"team": result["team"], "stop_tick": result["stop_tick"]}
            for result in mismatch_results
        ],
        "all_match": not mismatch_teams,
        "matrix_results": matrix_results,
        "team_results": matrix_results,
        "reports": reports,
    }


def _write_json_artifact(output_path: str | Path, payload: dict[str, Any]) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def run_multi_team_main_loop_consistency(
    *,
    teams: list[str],
    stop_tick: int,
    stop_ticks: list[int] | None = None,
    baseline_runtime: str | None = None,
    candidate_runtime: str = "opt-in-indexed-path",
    legacy_runtime: str | None = None,
    cleanup: bool = True,
    candidate_use_indexed_buff_load_loop: bool = True,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    if not teams:
        raise ValueError("at least one team is required")
    matrix_stop_ticks = list(stop_ticks or [stop_tick])
    if not matrix_stop_ticks:
        raise ValueError("at least one stop tick is required")
    baseline_label = _resolve_baseline_runtime_label(
        baseline_runtime=baseline_runtime,
        legacy_runtime=legacy_runtime,
        default="default-current-path",
    )

    reports = [
        run_main_loop_consistency(
            team=team,
            apl=None,
            stop_tick=matrix_stop_tick,
            baseline_runtime=baseline_label,
            candidate_runtime=candidate_runtime,
            cleanup=cleanup,
            candidate_use_indexed_buff_load_loop=candidate_use_indexed_buff_load_loop,
        )
        for team in teams
        for matrix_stop_tick in matrix_stop_ticks
    ]
    summary = build_multi_team_consistency_summary(reports=reports)
    if output_path is not None:
        _write_json_artifact(output_path, summary)
    return summary


def _cleanup_result_artifacts(session_id: str) -> None:
    result_path = Path(results_dir) / session_id
    if result_path.exists():
        shutil.rmtree(result_path, ignore_errors=True)


def run_main_loop_consistency(
    *,
    team: str,
    apl: str | None,
    stop_tick: int,
    baseline_runtime: str | None = None,
    candidate_runtime: str = "candidate-current",
    legacy_runtime: str | None = None,
    cleanup: bool = True,
    candidate_use_indexed_buff_load_loop: bool = False,
) -> dict[str, Any]:
    os.chdir(PROJECT_ROOT)
    base_cfg = _prepare_common_cfg(team, apl)
    apl_path = base_cfg.apl_path
    snapshots: list[RuntimeSnapshot] = []
    baseline_label = _resolve_baseline_runtime_label(
        baseline_runtime=baseline_runtime,
        legacy_runtime=legacy_runtime,
        default="default-current",
    )

    runtime_flags = (False, candidate_use_indexed_buff_load_loop)
    for runtime_label, use_indexed_buff_load_loop in zip(
        (baseline_label, candidate_runtime),
        runtime_flags,
        strict=True,
    ):
        session_id = _build_session_id()
        runtime_cfg = base_cfg.model_copy(update={"session_id": session_id}, deep=True)
        runtime_cfg_data = runtime_cfg.model_dump(mode="json")

        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                _run_single_runtime_process,
                runtime_cfg_data,
                stop_tick,
                use_indexed_buff_load_loop,
            )
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
        candidate_use_indexed_buff_load_loop=candidate_use_indexed_buff_load_loop,
    )


def _resolve_existing_directory(path: str | Path, label: str) -> Path:
    resolved = Path(path).expanduser()
    if not resolved.exists():
        raise FileNotFoundError(f"{label} does not exist: {resolved}")
    if not resolved.is_dir():
        raise NotADirectoryError(f"{label} is not a directory: {resolved}")
    return resolved.resolve()


def _load_common_cfg_from_file(common_cfg_path: str | Path) -> CommonCfg:
    path = Path(common_cfg_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"common cfg file does not exist: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("common_config"), dict):
        payload = payload["common_config"]
    return CommonCfg.model_validate(payload)


def _prepare_external_golden_common_cfg(
    *,
    team: str | None,
    common_cfg: str | Path | None,
    apl: str | None,
) -> tuple[CommonCfg, dict[str, Any]]:
    has_team = team is not None
    has_common_cfg = common_cfg is not None
    if has_team == has_common_cfg:
        raise ValueError("provide exactly one run config input: --team or --common-cfg")

    if team is not None:
        prepared_cfg = _prepare_common_cfg(team, apl)
        return prepared_cfg, {
            "kind": "team",
            "team": team,
            "common_cfg_path": None,
            "source_session_id": prepared_cfg.session_id,
        }

    assert common_cfg is not None
    cfg_path = Path(common_cfg).expanduser()
    prepared_cfg = _load_common_cfg_from_file(cfg_path)
    if apl is not None:
        prepared_cfg = prepared_cfg.model_copy(update={"apl_path": apl}, deep=True)
    return prepared_cfg, {
        "kind": "common_cfg",
        "team": None,
        "common_cfg_path": str(cfg_path.resolve()),
        "source_session_id": prepared_cfg.session_id,
    }


@dataclass(frozen=True)
class DamageParityData:
    present: bool
    path: Path
    raw_df: pl.DataFrame | None
    uuid_df: pl.DataFrame
    summary: dict[str, Any]
    uuid_records: list[dict[str, Any]]


def _stable_json_scalar(value: Any) -> Any:
    if hasattr(value, "item"):
        try:
            value = value.item()
        except (AttributeError, ValueError):
            pass
    if value is None:
        return None
    if isinstance(value, bool):
        return bool(value)
    if isinstance(value, int):
        return int(value)
    if isinstance(value, float):
        if math.isnan(value):
            return None
        return round(float(value), 6)
    if isinstance(value, str):
        return value
    return str(value)


def _normalize_json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): _normalize_json_value(value[key])
            for key in sorted(value, key=lambda item: str(item))
        }
    if isinstance(value, list):
        return [_normalize_json_value(item) for item in value]
    return _stable_json_scalar(value)


def _count_truthy_values(df: pl.DataFrame, column: str) -> int:
    if column not in df.columns or df.height == 0 or df[column].is_null().all():
        return 0
    if df[column].dtype == pl.Boolean:
        return int(df[column].fill_null(False).sum())
    return int(
        df.select(
            pl.col(column)
            .cast(pl.Utf8)
            .str.to_lowercase()
            .is_in(["true", "1"])
            .fill_null(False)
            .sum()
            .alias("truthy_count")
        ).item()
    )


def _count_by_string_value(df: pl.DataFrame, column: str) -> dict[str, int]:
    if column not in df.columns or df.height == 0:
        return {}
    grouped = (
        df.filter(pl.col(column).is_not_null())
        .with_columns(pl.col(column).cast(pl.Utf8).alias("__count_key"))
        .group_by("__count_key")
        .len()
        .sort("__count_key")
    )
    return {
        str(row["__count_key"]): int(row["len"])
        for row in grouped.iter_rows(named=True)
    }


def _diff_count_maps(golden: dict[str, int], candidate: dict[str, int]) -> dict[str, int]:
    diff: dict[str, int] = {}
    for key in sorted(set(golden) | set(candidate)):
        delta = int(candidate.get(key, 0)) - int(golden.get(key, 0))
        if delta != 0:
            diff[key] = delta
    return diff


def _load_damage_csv_from_result_dir(result_dir: Path) -> pl.DataFrame | None:
    csv_path = result_dir / "damage.csv"
    if not csv_path.exists():
        return None
    lf = pl.scan_csv(csv_path)
    schema_names = lf.collect_schema().names()
    lf = lf.rename({col: col.replace("\r", "").replace("\n", "").strip() for col in schema_names})
    return _normalize_damage_schema(lf.collect())


def _damage_summary(
    *,
    present: bool,
    path: Path,
    raw_df: pl.DataFrame | None,
    uuid_df: pl.DataFrame,
) -> dict[str, Any]:
    total_damage = 0.0
    if "dmg_expect_sum" in uuid_df.columns and uuid_df.height > 0:
        total_damage = round(float(uuid_df["dmg_expect_sum"].fill_null(0).sum()), 4)

    return {
        "present": present,
        "path": str(path),
        "row_count": 0 if raw_df is None else int(raw_df.height),
        "uuid_count": int(uuid_df.height),
        "total_damage": total_damage,
        "anomaly_total": _count_truthy_values(uuid_df, "is_anomaly"),
        "disorder_total": 0 if raw_df is None else _count_truthy_values(raw_df, "is_disorder"),
        "by_skill_tag": _count_by_string_value(uuid_df, "skill_tag"),
        "by_skill_cn_name": _count_by_string_value(uuid_df, "skill_cn_name"),
        "by_element_type": _count_by_string_value(uuid_df, "element_type"),
    }


def _damage_uuid_records(uuid_df: pl.DataFrame) -> list[dict[str, Any]]:
    if uuid_df.height == 0 or "UUID" not in uuid_df.columns:
        return []
    records: list[dict[str, Any]] = []
    for row in uuid_df.sort("UUID").iter_rows(named=True):
        record = {"UUID": str(row["UUID"])}
        for field in _DAMAGE_UUID_COMPARE_FIELDS:
            record[field] = _stable_json_scalar(row.get(field))
        records.append(record)
    return records


def _load_external_damage_data(result_dir: Path) -> DamageParityData:
    csv_path = result_dir / "damage.csv"
    raw_df = _load_damage_csv_from_result_dir(result_dir)
    present = raw_df is not None
    if raw_df is None or raw_df.height == 0:
        uuid_df = pl.DataFrame()
    else:
        uuid_df = sort_df_by_UUID(raw_df)
    summary = _damage_summary(
        present=present,
        path=csv_path,
        raw_df=raw_df,
        uuid_df=uuid_df,
    )
    return DamageParityData(
        present=present,
        path=csv_path,
        raw_df=raw_df,
        uuid_df=uuid_df,
        summary=summary,
        uuid_records=_damage_uuid_records(uuid_df),
    )


def _damage_uuid_differences(
    golden_records: list[dict[str, Any]],
    candidate_records: list[dict[str, Any]],
) -> dict[str, Any]:
    golden_by_uuid = {record["UUID"]: record for record in golden_records}
    candidate_by_uuid = {record["UUID"]: record for record in candidate_records}
    golden_only = [golden_by_uuid[key] for key in sorted(set(golden_by_uuid) - set(candidate_by_uuid))]
    candidate_only = [
        candidate_by_uuid[key] for key in sorted(set(candidate_by_uuid) - set(golden_by_uuid))
    ]

    changed: list[dict[str, Any]] = []
    for uuid in sorted(set(golden_by_uuid) & set(candidate_by_uuid)):
        field_differences: dict[str, dict[str, Any]] = {}
        golden_record = golden_by_uuid[uuid]
        candidate_record = candidate_by_uuid[uuid]
        for field in _DAMAGE_UUID_COMPARE_FIELDS:
            golden_value = golden_record.get(field)
            candidate_value = candidate_record.get(field)
            if golden_value != candidate_value:
                field_differences[field] = {
                    "golden": golden_value,
                    "candidate": candidate_value,
                }
        if field_differences:
            changed.append({"UUID": uuid, "fields": field_differences})

    return {
        "golden_only_count": len(golden_only),
        "candidate_only_count": len(candidate_only),
        "changed_count": len(changed),
        "sample_golden_only": golden_only[:_DAMAGE_DIFF_SAMPLE_LIMIT],
        "sample_candidate_only": candidate_only[:_DAMAGE_DIFF_SAMPLE_LIMIT],
        "sample_changed": changed[:_DAMAGE_DIFF_SAMPLE_LIMIT],
    }


def _build_external_damage_domain(
    *,
    golden_result_dir: Path,
    candidate_result_path: Path,
) -> dict[str, Any]:
    golden = _load_external_damage_data(golden_result_dir)
    candidate = _load_external_damage_data(candidate_result_path)
    scalar_differences = {
        key: round(float(candidate.summary[key]) - float(golden.summary[key]), 4)
        if key == "total_damage"
        else int(candidate.summary[key]) - int(golden.summary[key])
        for key in (
            "total_damage",
            "row_count",
            "uuid_count",
            "anomaly_total",
            "disorder_total",
        )
    }
    field_count_differences = {
        "skill_tag": _diff_count_maps(
            golden.summary["by_skill_tag"],
            candidate.summary["by_skill_tag"],
        ),
        "skill_cn_name": _diff_count_maps(
            golden.summary["by_skill_cn_name"],
            candidate.summary["by_skill_cn_name"],
        ),
        "element_type": _diff_count_maps(
            golden.summary["by_element_type"],
            candidate.summary["by_element_type"],
        ),
    }
    uuid_differences = _damage_uuid_differences(golden.uuid_records, candidate.uuid_records)
    presence_matches = golden.present == candidate.present
    scalar_matches = all(value == 0 for value in scalar_differences.values())
    field_counts_match = not any(bool(value) for value in field_count_differences.values())
    uuid_matches = (
        uuid_differences["golden_only_count"] == 0
        and uuid_differences["candidate_only_count"] == 0
        and uuid_differences["changed_count"] == 0
    )
    matches = presence_matches and scalar_matches and field_counts_match and uuid_matches

    return {
        "implemented": True,
        "matches": matches,
        "status": "match" if matches else "mismatch",
        "sample_limit": _DAMAGE_DIFF_SAMPLE_LIMIT,
        "golden": golden.summary,
        "candidate": candidate.summary,
        "differences": {
            "presence": {
                "golden_damage_csv": golden.present,
                "candidate_damage_csv": candidate.present,
            },
            **scalar_differences,
            "field_counts": field_count_differences,
            "uuid_aggregation": uuid_differences,
        },
    }


def _normalize_buff_timeline_value(value: Any) -> Any:
    return normalize_result_buff_timeline_value(value)


def _normalize_buff_timeline_entry(source: str, entry: Any) -> dict[str, Any]:
    return normalize_result_buff_timeline_entry(source, entry)


def _normalize_buff_timeline_payload(payload: Any) -> dict[str, list[dict[str, Any]]]:
    return normalize_result_buff_timeline_payload(payload)


def _load_buff_timeline_csvs(csv_paths: list[Path]) -> dict[str, list[dict[str, Any]]]:
    timeline: dict[str, list[dict[str, Any]]] = {}
    for csv_path in csv_paths:
        df = pl.read_csv(csv_path)
        source = csv_path.stem
        timeline[source] = _normalize_buff_timeline_payload(
            {source: _prepare_buff_timeline_data(df)}
        )[source]
    return timeline


def _buff_timeline_records(
    timeline: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for source, entries in sorted(timeline.items()):
        for entry in entries:
            records.append(
                {
                    "source": source,
                    "Task": str(entry["Task"]),
                    "Start": int(entry["Start"]),
                    "Finish": int(entry["Finish"]),
                    "Value": _normalize_buff_timeline_value(entry["Value"]),
                }
            )
    records.sort(
        key=lambda item: (
            item["source"],
            item["Task"],
            item["Start"],
            item["Finish"],
            str(item["Value"]),
        )
    )
    return records


def _buff_timeline_summary(
    *,
    present: bool,
    source_type: str,
    source_paths: list[Path],
    timeline: dict[str, list[dict[str, Any]]],
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "present": present,
        "source_type": source_type,
        "source_paths": [str(path) for path in source_paths],
        "source_count": len(timeline),
        "entry_count": len(records),
        "sources": sorted(timeline),
        "public_fields": list(BUFF_TIMELINE_PUBLIC_FIELDS),
    }


def _load_external_buff_timeline_data(result_dir: Path) -> BuffTimelineParityData:
    buff_log_dir = result_dir / "buff_log"
    json_path = buff_log_dir / "buff_timeline_data.json"
    csv_paths = sorted(buff_log_dir.glob("*.csv")) if buff_log_dir.exists() else []

    if json_path.exists():
        timeline = _normalize_buff_timeline_payload(
            json.loads(json_path.read_text(encoding="utf-8"))
        )
        source_type = "json"
        source_paths = [json_path]
    elif csv_paths:
        timeline = _load_buff_timeline_csvs(csv_paths)
        source_type = "csv"
        source_paths = csv_paths
    else:
        timeline = {}
        source_type = "missing"
        source_paths = []

    records = _buff_timeline_records(timeline)
    present = source_type != "missing"
    summary = _buff_timeline_summary(
        present=present,
        source_type=source_type,
        source_paths=source_paths,
        timeline=timeline,
        records=records,
    )
    return BuffTimelineParityData(
        present=present,
        source_type=source_type,
        source_paths=source_paths,
        timeline=timeline,
        summary=summary,
        records=records,
    )


def _buff_timeline_record_key(record: dict[str, Any]) -> tuple[str, str, int, int]:
    return (
        str(record["source"]),
        str(record["Task"]),
        int(record["Start"]),
        int(record["Finish"]),
    )


def _buff_timeline_records_by_key(
    records: list[dict[str, Any]],
) -> dict[tuple[str, str, int, int], list[dict[str, Any]]]:
    by_key: dict[tuple[str, str, int, int], list[dict[str, Any]]] = {}
    for record in records:
        by_key.setdefault(_buff_timeline_record_key(record), []).append(record)
    return by_key


def _expanded_counter_values(counter: Counter[Any]) -> list[Any]:
    values: list[Any] = []
    for value, count_value in sorted(counter.items(), key=lambda item: str(item[0])):
        values.extend([value] * int(count_value))
    return values


def _buff_timeline_entry_differences(
    golden_records: list[dict[str, Any]],
    candidate_records: list[dict[str, Any]],
) -> dict[str, Any]:
    golden_by_key = _buff_timeline_records_by_key(golden_records)
    candidate_by_key = _buff_timeline_records_by_key(candidate_records)
    golden_keys = set(golden_by_key)
    candidate_keys = set(candidate_by_key)

    baseline_only = [
        record
        for key in sorted(golden_keys - candidate_keys)
        for record in golden_by_key[key]
    ]
    candidate_only = [
        record
        for key in sorted(candidate_keys - golden_keys)
        for record in candidate_by_key[key]
    ]
    changed: list[dict[str, Any]] = []
    for key in sorted(golden_keys & candidate_keys):
        golden_values = Counter(record["Value"] for record in golden_by_key[key])
        candidate_values = Counter(record["Value"] for record in candidate_by_key[key])
        if golden_values == candidate_values:
            continue
        changed.append(
            {
                "source": key[0],
                "Task": key[1],
                "Start": key[2],
                "Finish": key[3],
                "golden_values": _expanded_counter_values(golden_values),
                "candidate_values": _expanded_counter_values(candidate_values),
            }
        )

    return {
        "baseline_only_count": len(baseline_only),
        "golden_only_count": len(baseline_only),
        "candidate_only_count": len(candidate_only),
        "changed_entry_count": len(changed),
        "sample_baseline_only": baseline_only[:_BUFF_TIMELINE_SAMPLE_LIMIT],
        "sample_golden_only": baseline_only[:_BUFF_TIMELINE_SAMPLE_LIMIT],
        "sample_candidate_only": candidate_only[:_BUFF_TIMELINE_SAMPLE_LIMIT],
        "sample_changed": changed[:_BUFF_TIMELINE_SAMPLE_LIMIT],
    }


def _build_buff_timeline_domain(
    *,
    golden_result_dir: Path,
    candidate_result_path: Path,
) -> dict[str, Any]:
    golden = _load_external_buff_timeline_data(golden_result_dir)
    candidate = _load_external_buff_timeline_data(candidate_result_path)
    entry_differences = _buff_timeline_entry_differences(golden.records, candidate.records)
    presence_matches = golden.present == candidate.present
    entries_match = (
        entry_differences["baseline_only_count"] == 0
        and entry_differences["candidate_only_count"] == 0
        and entry_differences["changed_entry_count"] == 0
    )
    matches = presence_matches and entries_match
    status = "not_provided"
    if golden.present or candidate.present:
        status = "match" if matches else "mismatch"

    return {
        "implemented": True,
        "matches": matches,
        "status": status,
        "sample_limit": _BUFF_TIMELINE_SAMPLE_LIMIT,
        "source_precedence": "buff_timeline_data.json when present, otherwise buff_log/*.csv",
        "public_fields": list(BUFF_TIMELINE_PUBLIC_FIELDS),
        "golden": golden.summary,
        "candidate": candidate.summary,
        "differences": {
            "presence": {
                "golden_buff_timeline": golden.present,
                "candidate_buff_timeline": candidate.present,
            },
            **entry_differences,
        },
    }


def _load_optional_json(path: Path) -> tuple[bool, Any]:
    if not path.exists():
        return False, None
    return True, json.loads(path.read_text(encoding="utf-8"))


def _json_type_name(value: Any) -> str:
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int | float) and not isinstance(value, bool):
        return "number"
    if value is None:
        return "null"
    return "string"


def _flatten_json_types(value: Any, path: str = "$") -> dict[str, str]:
    paths = {path: _json_type_name(value)}
    if isinstance(value, dict):
        for key in sorted(value, key=lambda item: str(item)):
            paths.update(_flatten_json_types(value[key], f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            paths.update(_flatten_json_types(item, f"{path}[{index}]"))
    return paths


def _flatten_json_leaf_values(value: Any, path: str = "$") -> dict[str, Any]:
    if isinstance(value, dict):
        leaves: dict[str, Any] = {}
        for key in sorted(value, key=lambda item: str(item)):
            leaves.update(_flatten_json_leaf_values(value[key], f"{path}.{key}"))
        return leaves
    if isinstance(value, list):
        leaves = {}
        for index, item in enumerate(value):
            leaves.update(_flatten_json_leaf_values(item, f"{path}[{index}]"))
        return leaves
    return {path: _stable_json_scalar(value)}


def _json_path_differences(golden_payload: Any, candidate_payload: Any) -> dict[str, Any]:
    golden_types = _flatten_json_types(golden_payload)
    candidate_types = _flatten_json_types(candidate_payload)
    golden_values = _flatten_json_leaf_values(golden_payload)
    candidate_values = _flatten_json_leaf_values(candidate_payload)
    golden_paths = set(golden_types)
    candidate_paths = set(candidate_types)
    shared_type_paths = sorted(golden_paths & candidate_paths)
    shared_value_paths = sorted(set(golden_values) & set(candidate_values))

    changed_types = [
        {
            "path": path,
            "golden": golden_types[path],
            "candidate": candidate_types[path],
        }
        for path in shared_type_paths
        if golden_types[path] != candidate_types[path]
    ]
    changed_values = [
        {
            "path": path,
            "golden": golden_values[path],
            "candidate": candidate_values[path],
        }
        for path in shared_value_paths
        if golden_values[path] != candidate_values[path]
    ]

    return {
        "golden_only_path_count": len(golden_paths - candidate_paths),
        "candidate_only_path_count": len(candidate_paths - golden_paths),
        "changed_type_count": len(changed_types),
        "changed_value_count": len(changed_values),
        "sample_golden_only_paths": sorted(golden_paths - candidate_paths)[:_DAMAGE_DIFF_SAMPLE_LIMIT],
        "sample_candidate_only_paths": sorted(candidate_paths - golden_paths)[
            :_DAMAGE_DIFF_SAMPLE_LIMIT
        ],
        "sample_changed_types": changed_types[:_DAMAGE_DIFF_SAMPLE_LIMIT],
        "sample_changed_values": changed_values[:_DAMAGE_DIFF_SAMPLE_LIMIT],
    }


def _build_damage_attribution_domain(
    *,
    golden_result_dir: Path,
    candidate_result_path: Path,
) -> dict[str, Any]:
    golden_path = golden_result_dir / "damage_attribution.json"
    candidate_path = candidate_result_path / "damage_attribution.json"
    golden_present, golden_payload = _load_optional_json(golden_path)
    candidate_present, candidate_payload = _load_optional_json(candidate_path)
    both_present = golden_present and candidate_present

    structure_matches = True
    values_match = True
    differences = {
        "presence": {
            "golden_damage_attribution": golden_present,
            "candidate_damage_attribution": candidate_present,
        },
        "structure": {
            "compared": both_present,
            "matches": True,
            "golden_only_path_count": 0,
            "candidate_only_path_count": 0,
            "changed_type_count": 0,
            "sample_golden_only_paths": [],
            "sample_candidate_only_paths": [],
            "sample_changed_types": [],
        },
        "values": {
            "compared": both_present,
            "matches": True,
            "changed_value_count": 0,
            "sample_changed_values": [],
        },
    }

    if both_present:
        path_differences = _json_path_differences(golden_payload, candidate_payload)
        structure_matches = (
            path_differences["golden_only_path_count"] == 0
            and path_differences["candidate_only_path_count"] == 0
            and path_differences["changed_type_count"] == 0
        )
        values_match = path_differences["changed_value_count"] == 0
        differences["structure"] = {
            "compared": True,
            "matches": structure_matches,
            "golden_only_path_count": path_differences["golden_only_path_count"],
            "candidate_only_path_count": path_differences["candidate_only_path_count"],
            "changed_type_count": path_differences["changed_type_count"],
            "sample_golden_only_paths": path_differences["sample_golden_only_paths"],
            "sample_candidate_only_paths": path_differences["sample_candidate_only_paths"],
            "sample_changed_types": path_differences["sample_changed_types"],
        }
        differences["values"] = {
            "compared": True,
            "matches": values_match,
            "changed_value_count": path_differences["changed_value_count"],
            "sample_changed_values": path_differences["sample_changed_values"],
        }

    matches = golden_present == candidate_present and (not both_present or structure_matches and values_match)
    status = "not_provided"
    if golden_present or candidate_present:
        status = "match" if matches else "mismatch"

    return {
        "implemented": True,
        "matches": matches,
        "status": status,
        "sample_limit": _DAMAGE_DIFF_SAMPLE_LIMIT,
        "golden": {"present": golden_present, "path": str(golden_path)},
        "candidate": {"present": candidate_present, "path": str(candidate_path)},
        "differences": differences,
    }


def _external_golden_diff_domains(
    *,
    golden_result_dir: Path,
    candidate_result_path: Path,
) -> dict[str, dict[str, Any]]:
    domains = _external_golden_diff_placeholders()
    domains["damage"] = _build_external_damage_domain(
        golden_result_dir=golden_result_dir,
        candidate_result_path=candidate_result_path,
    )
    domains["damage_attribution"] = _build_damage_attribution_domain(
        golden_result_dir=golden_result_dir,
        candidate_result_path=candidate_result_path,
    )
    domains["buff_timeline"] = _build_buff_timeline_domain(
        golden_result_dir=golden_result_dir,
        candidate_result_path=candidate_result_path,
    )
    return domains


def _external_golden_diff_placeholders() -> dict[str, dict[str, Any]]:
    return {
        "damage": {
            "implemented": False,
            "matches": None,
            "status": "pending",
            "next_story": "US-002",
        },
        "damage_attribution": {
            "implemented": False,
            "matches": None,
            "status": "pending",
            "next_story": "US-002",
        },
        "buff_timeline": {
            "implemented": False,
            "matches": None,
            "status": "pending",
            "next_story": "US-003",
        },
    }


def _implemented_external_golden_diffs_match(domains: dict[str, dict[str, Any]]) -> bool:
    implemented = [domain for domain in domains.values() if domain.get("implemented") is True]
    return all(domain.get("matches") is True for domain in implemented)


def build_external_golden_parity_report(
    *,
    golden_result_dir: Path,
    candidate_session_id: str,
    candidate_result_path: Path,
    run_config_identity: dict[str, Any],
    apl: str,
    stop_tick: int,
) -> dict[str, Any]:
    diff_domains = _external_golden_diff_domains(
        golden_result_dir=golden_result_dir,
        candidate_result_path=candidate_result_path,
    )
    return {
        "schema": EXTERNAL_GOLDEN_PARITY_SCHEMA,
        "schema_version": 1,
        "golden_result_dir": str(golden_result_dir),
        "candidate": {
            "session_id": candidate_session_id,
            "result_path": str(candidate_result_path),
        },
        "run_config": {
            "identity": run_config_identity,
            "team": run_config_identity.get("team"),
            "common_cfg": run_config_identity.get("common_cfg_path"),
            "apl": apl,
            "stop_tick": int(stop_tick),
        },
        "comparison": {
            "mode": "external-golden-result-dir-vs-current-candidate",
            "candidate_run_count": 1,
            "golden_path": str(golden_result_dir),
            "candidate_result_path": str(candidate_result_path),
            "implemented_domains": [
                name for name, domain in diff_domains.items() if domain.get("implemented") is True
            ],
        },
        "diffs": {
            "matches": _implemented_external_golden_diffs_match(diff_domains),
            "domains": diff_domains,
        },
    }


def run_external_golden_parity(
    *,
    golden_result_dir: str | Path,
    team: str | None = None,
    common_cfg: str | Path | None = None,
    apl: str | None = None,
    stop_tick: int,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    os.chdir(PROJECT_ROOT)
    golden_path = _resolve_existing_directory(golden_result_dir, "golden result directory")
    base_cfg, run_config_identity = _prepare_external_golden_common_cfg(
        team=team,
        common_cfg=common_cfg,
        apl=apl,
    )
    candidate_session_id = _build_session_id()
    runtime_cfg = base_cfg.model_copy(update={"session_id": candidate_session_id}, deep=True)

    with ProcessPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            _run_single_runtime_process,
            runtime_cfg.model_dump(mode="json"),
            stop_tick,
            False,
        )
        finished_session_id = future.result()

    candidate_result_path = (Path(results_dir) / finished_session_id).resolve()
    report = build_external_golden_parity_report(
        golden_result_dir=golden_path,
        candidate_session_id=finished_session_id,
        candidate_result_path=candidate_result_path,
        run_config_identity=run_config_identity,
        apl=runtime_cfg.apl_path,
        stop_tick=stop_tick,
    )
    if output_path is not None:
        _write_json_artifact(output_path, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a Buff main-loop consistency comparison")
    parser.add_argument("--team", default=None, help="Registered team name to simulate")
    parser.add_argument(
        "--teams",
        nargs="+",
        default=None,
        help="Registered team names to simulate into one multi-team summary.",
    )
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
        "--stop-ticks",
        nargs="+",
        type=int,
        default=None,
        help=(
            "Optional stop-tick matrix for --teams. When omitted, --teams preserves "
            "the single --stop-tick behavior."
        ),
    )
    parser.add_argument(
        "--baseline-runtime",
        dest="baseline_runtime",
        default="default-current",
        help="First/default current run label to record in the report; this does not select a runtime.",
    )
    parser.add_argument(
        "--legacy-runtime",
        dest="baseline_runtime",
        help="Compatibility alias for --baseline-runtime; report label only, not old runtime selection.",
    )
    parser.add_argument(
        "--candidate-runtime",
        default="candidate-current",
        help="Second run label to record in the report; this does not select a runtime.",
    )
    parser.add_argument(
        "--keep-artifacts",
        action="store_true",
        help="Keep raw results/<session_id> artifacts after the report is generated.",
    )
    parser.add_argument(
        "--candidate-use-indexed-buff-load-loop",
        action="store_true",
        help=(
            "Explicitly request indexed BuffLoadLoop for the candidate run only; "
            "omitting this keeps both runs on the default current path."
        ),
    )
    parser.add_argument(
        "--summary-json",
        default=None,
        help="Optional JSON artifact path for the generated report or multi-team summary.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the full JSON report to stdout.",
    )
    return parser


def build_external_golden_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run one current Buff simulation and compare it with an external golden result directory"
    )
    parser.add_argument(
        "--golden-result-dir",
        required=True,
        help="External golden result directory to compare against.",
    )
    run_config_group = parser.add_mutually_exclusive_group(required=True)
    run_config_group.add_argument("--team", default=None, help="Registered team name to simulate.")
    run_config_group.add_argument(
        "--common-cfg",
        default=None,
        help="Path to a CommonCfg JSON file, or a SessionRun JSON file containing common_config.",
    )
    parser.add_argument(
        "--apl",
        default=None,
        help="Optional APL path override for the selected team or common config.",
    )
    parser.add_argument(
        "--stop-tick",
        type=int,
        default=config.stop_tick,
        help="Stop tick for the single candidate run.",
    )
    parser.add_argument(
        "--output-json",
        required=True,
        help="JSON artifact path for the external golden parity envelope.",
    )
    return parser


def _format_multi_team_human_summary(summary: dict[str, Any]) -> str:
    lines = [
        f"schema: {summary['schema']}",
        "teams: " + ", ".join(summary["teams"]),
        f"stop_ticks: {summary['stop_ticks']}",
        f"matrix_row_count: {summary['matrix_row_count']}",
        f"runtime_selection: indexed_opt_in={summary['candidate_use_indexed_buff_load_loop']}",
        f"all_match: {summary['all_match']}",
        f"mismatch_count: {summary['mismatch_count']}",
    ]
    return "\n".join(lines)


def _format_human_report(report: dict[str, Any]) -> str:
    lines = [
        f"team: {report['team']}",
        f"apl: {report['apl']}",
        f"stop_tick: {report['stop_tick']}",
        "runtime_selection: "
        + report.get("runtime_selection", {}).get("mode", "label-only-current-runtime"),
        (
            "total_damage: "
            f"{report['baseline_runtime']}={report['total_damage']['baseline']}, "
            f"{report['candidate_runtime']}={report['total_damage']['candidate']}"
        ),
        f"matches: {report['differences']['matches']}",
        "event_count_differences: "
        + json.dumps(report["differences"]["event_counts"], ensure_ascii=False, sort_keys=True),
        "buff_timeline_differences: "
        + json.dumps(report["differences"]["buff_timeline"], ensure_ascii=False, sort_keys=True),
    ]
    return "\n".join(lines)


def _format_external_golden_human_summary(report: dict[str, Any]) -> str:
    domains = report["diffs"]["domains"]
    return "\n".join(
        [
            f"schema: {report['schema']}",
            f"golden_result_dir: {report['golden_result_dir']}",
            f"candidate_session_id: {report['candidate']['session_id']}",
            f"candidate_result_path: {report['candidate']['result_path']}",
            f"run_config: {report['run_config']['identity']['kind']}",
            f"apl: {report['run_config']['apl']}",
            f"stop_tick: {report['run_config']['stop_tick']}",
            "implemented_domains: " + ", ".join(report["comparison"]["implemented_domains"]),
            "placeholder_domains: "
            + ", ".join(name for name, domain in domains.items() if not domain["implemented"]),
            f"matches: {report['diffs']['matches']}",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.teams:
        summary = run_multi_team_main_loop_consistency(
            teams=args.teams,
            stop_tick=args.stop_tick,
            stop_ticks=args.stop_ticks,
            baseline_runtime=args.baseline_runtime,
            candidate_runtime=args.candidate_runtime,
            cleanup=not args.keep_artifacts,
            candidate_use_indexed_buff_load_loop=args.candidate_use_indexed_buff_load_loop,
            output_path=args.summary_json,
        )
        if args.json:
            print(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2))
        else:
            print(_format_multi_team_human_summary(summary))
        return 0 if summary["all_match"] else 2

    if args.team is None:
        parser.error("--team is required unless --teams is provided")

    report = run_main_loop_consistency(
        team=args.team,
        apl=args.apl,
        stop_tick=args.stop_tick,
        baseline_runtime=args.baseline_runtime,
        candidate_runtime=args.candidate_runtime,
        cleanup=not args.keep_artifacts,
        candidate_use_indexed_buff_load_loop=args.candidate_use_indexed_buff_load_loop,
    )
    if args.summary_json:
        _write_json_artifact(args.summary_json, report)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print(_format_human_report(report))
    return 0


def external_golden_main(argv: list[str] | None = None) -> int:
    parser = build_external_golden_parser()
    args = parser.parse_args(argv)
    try:
        report = run_external_golden_parity(
            golden_result_dir=args.golden_result_dir,
            team=args.team,
            common_cfg=args.common_cfg,
            apl=args.apl,
            stop_tick=args.stop_tick,
            output_path=args.output_json,
        )
    except (FileNotFoundError, NotADirectoryError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"{parser.prog}: error: {exc}\n")

    print(_format_external_golden_human_summary(report))
    return 0 if report["diffs"]["matches"] else 2


__all__ = [
    "PROJECT_ROOT",
    "EXTERNAL_GOLDEN_PARITY_SCHEMA",
    "MULTI_TEAM_CONSISTENCY_SCHEMA",
    "RUNTIME_LABEL_CONTRACT",
    "RuntimeSnapshot",
    "build_external_golden_parity_report",
    "build_external_golden_parser",
    "build_consistency_report",
    "build_multi_team_consistency_summary",
    "build_parser",
    "external_golden_main",
    "main",
    "run_external_golden_parity",
    "run_main_loop_consistency",
    "run_multi_team_main_loop_consistency",
]


if __name__ == "__main__":
    sys.exit(main())
