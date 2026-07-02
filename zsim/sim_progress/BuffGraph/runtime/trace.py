from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping


class BuffGraphTraceKind(StrEnum):
    GRAPH_STARTED = "graph_started"
    NODE_EVALUATED = "node_evaluated"
    ADAPTER_EXECUTED = "adapter_executed"
    EFFECT_REQUESTED = "effect_requested"
    PARITY_CHECKPOINT = "parity_checkpoint"
    GRAPH_FINISHED = "graph_finished"


NON_BEHAVIORAL_TRACE_KEYS = {
    "debug_repr",
    "elapsed_ms",
    "file",
    "object_address",
    "object_id",
    "path",
    "session_id",
    "timing_ms",
    "wall_time",
}


@dataclass(frozen=True, slots=True)
class BuffGraphTraceError:
    code: str
    message: str
    path: str


@dataclass(frozen=True, slots=True)
class BuffGraphTraceEvent:
    tick: int
    sequence: int
    kind: BuffGraphTraceKind
    graph_id: str
    node_id: str | None = None
    block_id: str | None = None
    adapter_id: str | None = None
    checkpoint: str = ""
    payload: Mapping[str, Any] = field(default_factory=dict)
    diagnostic: Mapping[str, Any] = field(default_factory=dict)

    def normalized(self) -> Mapping[str, Any]:
        return {
            "tick": self.tick,
            "sequence": self.sequence,
            "kind": self.kind.value,
            "graph_id": self.graph_id,
            "node_id": self.node_id,
            "block_id": self.block_id,
            "adapter_id": self.adapter_id,
            "checkpoint": self.checkpoint,
            "payload": _normalize_behavior_value(self.payload),
        }


@dataclass(frozen=True, slots=True)
class BuffGraphTrace:
    graph_id: str
    events: tuple[BuffGraphTraceEvent, ...] = ()

    def append(self, event: BuffGraphTraceEvent) -> "BuffGraphTrace":
        return BuffGraphTrace(graph_id=self.graph_id, events=(*self.events, event))

    def normalized_events(self) -> tuple[Mapping[str, Any], ...]:
        return tuple(event.normalized() for event in self.events)


@dataclass(frozen=True, slots=True)
class BuffGraphTraceComparison:
    passed: bool
    first_difference: str | None
    expected: tuple[Mapping[str, Any], ...]
    actual: tuple[Mapping[str, Any], ...]


def validate_buff_graph_trace(trace: BuffGraphTrace) -> tuple[BuffGraphTraceError, ...]:
    errors: list[BuffGraphTraceError] = []
    if not trace.graph_id.strip():
        errors.append(BuffGraphTraceError("required_text", "graph_id must be non-empty", "graph_id"))

    previous_key: tuple[int, int] | None = None
    for index, event in enumerate(trace.events):
        path = f"events[{index}]"
        if event.tick < 0:
            errors.append(BuffGraphTraceError("negative_tick", "tick must be >= 0", f"{path}.tick"))
        if event.sequence < 0:
            errors.append(
                BuffGraphTraceError("negative_sequence", "sequence must be >= 0", f"{path}.sequence")
            )
        if event.graph_id != trace.graph_id:
            errors.append(
                BuffGraphTraceError(
                    "graph_id_mismatch",
                    f"event graph_id {event.graph_id!r} does not match trace graph_id {trace.graph_id!r}",
                    f"{path}.graph_id",
                )
            )
        if event.kind != BuffGraphTraceKind.GRAPH_STARTED and not event.checkpoint.strip():
            errors.append(
                BuffGraphTraceError(
                    "required_checkpoint",
                    "non-start trace events require a behavior checkpoint",
                    f"{path}.checkpoint",
                )
            )

        key = (event.tick, event.sequence)
        if previous_key is not None and key < previous_key:
            errors.append(
                BuffGraphTraceError(
                    "trace_order",
                    "trace events must be ordered by tick then sequence",
                    path,
                )
            )
        previous_key = key

    return tuple(errors)


def compare_normalized_traces(
    *,
    expected: BuffGraphTrace,
    actual: BuffGraphTrace,
) -> BuffGraphTraceComparison:
    expected_events = expected.normalized_events()
    actual_events = actual.normalized_events()
    if expected_events == actual_events:
        return BuffGraphTraceComparison(
            passed=True,
            first_difference=None,
            expected=expected_events,
            actual=actual_events,
        )

    max_len = max(len(expected_events), len(actual_events))
    for index in range(max_len):
        if index >= len(expected_events):
            difference = f"actual has extra event at index {index}"
            break
        if index >= len(actual_events):
            difference = f"actual is missing event at index {index}"
            break
        if expected_events[index] != actual_events[index]:
            difference = f"first trace difference at index {index}"
            break
    else:
        difference = "trace length or content differs"

    return BuffGraphTraceComparison(
        passed=False,
        first_difference=difference,
        expected=expected_events,
        actual=actual_events,
    )


def _normalize_behavior_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: _normalize_behavior_value(value[key])
            for key in sorted(value)
            if str(key) not in NON_BEHAVIORAL_TRACE_KEYS
        }
    if isinstance(value, tuple | list):
        return tuple(_normalize_behavior_value(item) for item in value)
    return value
