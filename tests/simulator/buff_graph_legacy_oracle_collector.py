from __future__ import annotations

import copy
import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal


LegacyXLogicPhase = Literal["judge", "hit", "scheduled_event"]


@dataclass(frozen=True, slots=True)
class LegacyXLogicOracleCase:
    case_id: str
    source_xlogic_path: str
    source_buff_index: str
    tick: int
    phase: LegacyXLogicPhase
    legacy_kwargs: Mapping[str, Any] = field(default_factory=dict)
    prepared_context_fixture: Mapping[str, Any] = field(default_factory=dict)
    record_seed: Mapping[str, Any] = field(default_factory=dict)
    fixture_path: str | None = None
    side_effect_policy: str = "spy_only"


@dataclass(frozen=True, slots=True)
class LegacyXLogicExecutionContext:
    case_id: str
    source_xlogic_path: str
    source_buff_index: str
    tick: int
    phase: LegacyXLogicPhase
    legacy_kwargs: Mapping[str, Any]
    prepared_context_fixture: Mapping[str, Any]
    record_before: Mapping[str, Any]
    side_effect_policy: str


@dataclass(frozen=True, slots=True)
class LegacyXLogicRunResult:
    judge_result: bool | None = None
    hit_result: Any | None = None
    expected_final_output: Mapping[str, Any] = field(default_factory=dict)
    expected_trace_kind_checkpoint: Sequence[Sequence[str]] = field(default_factory=tuple)
    record_after: Mapping[str, Any] = field(default_factory=dict)
    side_effects: Sequence[Mapping[str, Any]] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class LegacyXLogicOracleResult:
    case_id: str
    legacy_oracle: str
    judge_result: bool | None
    hit_result: Any | None
    expected_final_output: Mapping[str, Any]
    expected_trace_kind_checkpoint: tuple[tuple[str, str], ...]
    record_before: Mapping[str, Any]
    record_after: Mapping[str, Any]
    record_delta: Mapping[str, Any]
    side_effects: tuple[Mapping[str, Any], ...]
    blocked_reason: str | None = None

    def to_evidence(self) -> dict[str, Any]:
        return asdict(self)


LegacyXLogicRunner = Callable[[LegacyXLogicExecutionContext], LegacyXLogicRunResult]


def collect_legacy_xlogic_oracle(
    case: LegacyXLogicOracleCase,
    *,
    runner: LegacyXLogicRunner | None,
    project_root: Path | None = None,
) -> LegacyXLogicOracleResult:
    """Collect legacy-oracle evidence without dispatching production runtime effects."""
    fixture = _load_fixture(case.fixture_path, project_root=project_root)
    record_before = _normalize(copy.deepcopy(dict(case.record_seed)))
    if runner is None:
        return LegacyXLogicOracleResult(
            case_id=case.case_id,
            legacy_oracle="legacy_python_collector_blocked",
            judge_result=None,
            hit_result=None,
            expected_final_output={},
            expected_trace_kind_checkpoint=(),
            record_before=record_before,
            record_after=record_before,
            record_delta={},
            side_effects=(),
            blocked_reason="legacy_xlogic_runner_required",
        )

    _validate_case_against_fixture(case, fixture)
    context = LegacyXLogicExecutionContext(
        case_id=case.case_id,
        source_xlogic_path=case.source_xlogic_path,
        source_buff_index=case.source_buff_index,
        tick=case.tick,
        phase=case.phase,
        legacy_kwargs=_normalize(copy.deepcopy(dict(case.legacy_kwargs))),
        prepared_context_fixture=_normalize(
            copy.deepcopy(dict(case.prepared_context_fixture))
        ),
        record_before=record_before,
        side_effect_policy=case.side_effect_policy,
    )
    run = runner(context)
    record_after = _normalize(copy.deepcopy(dict(run.record_after or record_before)))
    return LegacyXLogicOracleResult(
        case_id=case.case_id,
        legacy_oracle="legacy_python_collected",
        judge_result=run.judge_result,
        hit_result=run.hit_result,
        expected_final_output=_normalize(dict(run.expected_final_output)),
        expected_trace_kind_checkpoint=_trace_checkpoint_tuple(
            run.expected_trace_kind_checkpoint
        ),
        record_before=record_before,
        record_after=record_after,
        record_delta=_record_delta(record_before, record_after),
        side_effects=tuple(_normalize(dict(item)) for item in run.side_effects),
        blocked_reason=None,
    )


def fixture_case_from_legacy_parity_fixture(
    fixture_path: str | Path,
    *,
    case_id: str,
    phase: LegacyXLogicPhase,
    tick: int,
    legacy_kwargs: Mapping[str, Any] | None = None,
    record_seed: Mapping[str, Any] | None = None,
) -> LegacyXLogicOracleCase:
    fixture = _load_fixture(str(fixture_path), project_root=None)
    return LegacyXLogicOracleCase(
        case_id=case_id,
        source_xlogic_path=str(fixture["xlogic_path"]),
        source_buff_index=str(fixture["source_buff_index"]),
        tick=tick,
        phase=phase,
        legacy_kwargs=legacy_kwargs or {},
        prepared_context_fixture=dict(fixture.get("prepared_context", {})),
        record_seed=record_seed or {},
        fixture_path=str(fixture_path),
    )


def _load_fixture(
    fixture_path: str | None,
    *,
    project_root: Path | None,
) -> Mapping[str, Any]:
    if fixture_path is None:
        return {}
    path = Path(fixture_path)
    if not path.is_absolute() and project_root is not None:
        path = project_root / path
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_case_against_fixture(
    case: LegacyXLogicOracleCase,
    fixture: Mapping[str, Any],
) -> None:
    if not fixture:
        return
    fixture_xlogic = fixture.get("xlogic_path")
    if fixture_xlogic is not None and fixture_xlogic != case.source_xlogic_path:
        raise ValueError("case source_xlogic_path does not match fixture xlogic_path")
    fixture_buff_index = fixture.get("source_buff_index")
    if fixture_buff_index is not None and fixture_buff_index != case.source_buff_index:
        raise ValueError("case source_buff_index does not match fixture source_buff_index")


def _trace_checkpoint_tuple(
    rows: Sequence[Sequence[str]],
) -> tuple[tuple[str, str], ...]:
    return tuple((str(row[0]), str(row[1])) for row in rows)


def _record_delta(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
) -> dict[str, Any]:
    delta: dict[str, Any] = {}
    keys = set(before) | set(after)
    for key in sorted(keys):
        before_value = before.get(key)
        after_value = after.get(key)
        if before_value != after_value:
            delta[key] = {
                "before": before_value,
                "after": after_value,
            }
    return delta


def _normalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _normalize(value[key]) for key in sorted(value)}
    if isinstance(value, list | tuple):
        return tuple(_normalize(item) for item in value)
    return value
