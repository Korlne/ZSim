from dataclasses import FrozenInstanceError

import pytest

from zsim.sim_progress.BuffGraph.runtime import (
    BuffGraphTrace,
    BuffGraphTraceEvent,
    BuffGraphTraceKind,
    compare_normalized_traces,
    validate_buff_graph_trace,
)


def test_trace_events_are_frozen_behavior_checkpoints() -> None:
    event = BuffGraphTraceEvent(
        tick=120,
        sequence=2,
        kind=BuffGraphTraceKind.ADAPTER_EXECUTED,
        graph_id="alice-cinema6",
        node_id="trigger-hit",
        block_id="trigger.skill_hit",
        adapter_id="trigger.skill_hit.v1",
        checkpoint="skill_hit_matched",
        payload={"skill_tag": "basic", "hit_count": 1},
        diagnostic={"path": "zsim/sim_progress/Buff/BuffXLogic/AliceCinema6Trigger.py"},
    )

    with pytest.raises(FrozenInstanceError):
        event.tick = 121  # type: ignore[misc]

    assert event.normalized() == {
        "tick": 120,
        "sequence": 2,
        "kind": "adapter_executed",
        "graph_id": "alice-cinema6",
        "node_id": "trigger-hit",
        "block_id": "trigger.skill_hit",
        "adapter_id": "trigger.skill_hit.v1",
        "checkpoint": "skill_hit_matched",
        "payload": {"hit_count": 1, "skill_tag": "basic"},
    }


def test_trace_validation_requires_graph_match_and_tick_sequence_order() -> None:
    trace = BuffGraphTrace(
        graph_id="graph-a",
        events=(
            BuffGraphTraceEvent(
                tick=10,
                sequence=1,
                kind=BuffGraphTraceKind.GRAPH_STARTED,
                graph_id="graph-a",
            ),
            BuffGraphTraceEvent(
                tick=9,
                sequence=0,
                kind=BuffGraphTraceKind.NODE_EVALUATED,
                graph_id="graph-b",
                checkpoint="condition_checked",
            ),
            BuffGraphTraceEvent(
                tick=11,
                sequence=-1,
                kind=BuffGraphTraceKind.EFFECT_REQUESTED,
                graph_id="graph-a",
                checkpoint="",
            ),
        ),
    )

    assert [error.code for error in validate_buff_graph_trace(trace)] == [
        "graph_id_mismatch",
        "trace_order",
        "negative_sequence",
        "required_checkpoint",
    ]


def test_normalized_trace_comparison_ignores_non_behavioral_noise() -> None:
    expected = BuffGraphTrace(
        graph_id="alice-cinema6",
        events=(
            BuffGraphTraceEvent(
                tick=300,
                sequence=0,
                kind=BuffGraphTraceKind.PARITY_CHECKPOINT,
                graph_id="alice-cinema6",
                node_id="effect-start",
                block_id="effect.start_buff",
                adapter_id="effect.start_buff.v1",
                checkpoint="buff_started",
                payload={
                    "buff_index": "Buff-角色-爱丽丝-影画6",
                    "count": 1,
                    "debug_repr": "<Buff object at 0x1>",
                    "nested": {"path": "legacy/run-a", "duration": 180},
                },
            ),
        ),
    )
    actual = BuffGraphTrace(
        graph_id="alice-cinema6",
        events=(
            BuffGraphTraceEvent(
                tick=300,
                sequence=0,
                kind=BuffGraphTraceKind.PARITY_CHECKPOINT,
                graph_id="alice-cinema6",
                node_id="effect-start",
                block_id="effect.start_buff",
                adapter_id="effect.start_buff.v1",
                checkpoint="buff_started",
                payload={
                    "count": 1,
                    "buff_index": "Buff-角色-爱丽丝-影画6",
                    "debug_repr": "<Buff object at 0x9>",
                    "nested": {"path": "graph/run-b", "duration": 180},
                },
            ),
        ),
    )

    comparison = compare_normalized_traces(expected=expected, actual=actual)

    assert comparison.passed is True
    assert comparison.first_difference is None


def test_normalized_trace_comparison_reports_first_behavior_difference() -> None:
    expected = BuffGraphTrace(
        graph_id="graph-a",
        events=(
            BuffGraphTraceEvent(
                tick=1,
                sequence=0,
                kind=BuffGraphTraceKind.NODE_EVALUATED,
                graph_id="graph-a",
                checkpoint="cooldown_ready",
                payload={"ready": True},
            ),
        ),
    )
    actual = BuffGraphTrace(
        graph_id="graph-a",
        events=(
            BuffGraphTraceEvent(
                tick=1,
                sequence=0,
                kind=BuffGraphTraceKind.NODE_EVALUATED,
                graph_id="graph-a",
                checkpoint="cooldown_ready",
                payload={"ready": False},
            ),
        ),
    )

    comparison = compare_normalized_traces(expected=expected, actual=actual)

    assert comparison.passed is False
    assert comparison.first_difference == "first trace difference at index 0"
