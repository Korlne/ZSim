import pytest

from zsim.sim_progress.BuffGraph.adapters.condition_adapters import (
    build_enemy_anomaly_state_condition_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.read_adapters import (
    build_enemy_anomaly_state_read_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.state_adapters import (
    build_enemy_anomaly_state_state_adapters,
)
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.runtime.compiler import compile_buff_graph_spec
from zsim.sim_progress.BuffGraph.runtime.executor import execute_compiled_buff_graph
from zsim.sim_progress.BuffGraph.runtime.trace import validate_buff_graph_trace
from zsim.sim_progress.BuffGraph.spec import BuffGraphEdge, BuffGraphSpec, OwnerKind


def test_enemy_anomaly_state_blocks_are_registered_and_compile() -> None:
    registry = build_default_block_registry()

    block_ids = {block.block_id for block in registry.all()}

    assert {
        "read.enemy_context",
        "read.enemy_anomaly_state",
        "read.enemy_anomaly_bar",
        "read.enemy_edge_state",
        "read.dot_runtime_state",
        "condition.enemy_state",
        "condition.edge_transition",
        "state.last_observed_enemy_state",
        "state.edge_memory",
        "state.anomaly_signal",
    } <= block_ids

    result = compile_buff_graph_spec(_enemy_anomaly_state_spec(), block_registry=registry)

    assert result.passed is True
    assert result.compiled is not None


def test_enemy_anomaly_state_graph_reads_context_and_detects_edges() -> None:
    registry = build_default_block_registry()
    compiled = compile_buff_graph_spec(
        _enemy_anomaly_state_spec(),
        block_registry=registry,
    ).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(
        compiled,
        adapters=_enemy_anomaly_state_adapters(),
        tick=360,
        prepared_context={
            "enemy_context": {
                "anomaly_states": {
                    "ice": {"state": "frost", "active": True},
                },
                "anomaly_bars": {
                    "ice": {"value": 45, "threshold": 90},
                },
            },
            "enemy_edge_states": {
                "frost": {"previous": False, "current": True},
            },
            "dot_runtime_states": {
                "burn": {"active": False, "remaining_ticks": 0},
            },
            "state": {
                "last-frost-state": "none",
                "frost-edge": False,
            },
        },
    )

    assert result.passed is True
    assert result.node_outputs["read-anomaly-state"] == {
        "anomaly_state": {"state": "frost", "active": True},
        "state_value": "frost",
        "active": True,
        "anomaly_key": "ice",
    }
    assert result.node_outputs["read-anomaly-bar"]["anomaly_value"] == 45.0
    assert result.node_outputs["read-anomaly-bar"]["anomaly_threshold"] == 90.0
    assert result.node_outputs["read-anomaly-bar"]["anomaly_ratio"] == pytest.approx(0.5)
    assert result.node_outputs["condition-enemy-state"] == {
        "passed": True,
        "actual_state": "frost",
        "expected_state": "frost",
        "active": True,
    }
    assert result.node_outputs["last-observed"] == {
        "previous_state": "none",
        "current_state": "frost",
        "changed": True,
    }
    assert result.node_outputs["edge-transition"] == {
        "passed": True,
        "previous": False,
        "current": True,
        "transition": "rising",
    }
    assert result.node_outputs["edge-memory"] == {
        "previous": False,
        "current": True,
        "rising_edge": True,
        "falling_edge": False,
        "changed": True,
    }
    assert result.node_outputs["read-dot-state"] == {
        "dot_runtime_state": {"active": False, "remaining_ticks": 0},
        "active": False,
        "dot_key": "burn",
    }
    assert result.outputs["active"] is True
    assert result.outputs["anomaly_signal"]["signal_key"] == "frost-signal"
    assert result.outputs["anomaly_signal"]["anomaly_state"] == {
        "state": "frost",
        "active": True,
    }
    assert "command" not in result.outputs
    assert validate_buff_graph_trace(result.trace) == ()


def test_enemy_anomaly_readers_can_use_direct_prepared_context_snapshots() -> None:
    registry = build_default_block_registry()
    anomaly_state = registry.get("read.enemy_anomaly_state").create_node(
        node_id="read-anomaly-state"
    )
    enemy_state = registry.get("condition.enemy_state").create_node(
        node_id="condition-enemy-state",
        params={"expected_state": "shock"},
    )
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="enemy-anomaly-direct-snapshot",
        display_name="Enemy Anomaly Direct Snapshot",
        owner_kind=OwnerKind.UNKNOWN,
        owner_name="unknown:enemy-anomaly-direct-snapshot",
        source_buff_index=None,
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/enemy_anomaly_read.py",
        nodes=(anomaly_state, enemy_state),
        edges=(
            BuffGraphEdge(
                edge_id="edge-1",
                source_node_id="read-anomaly-state",
                target_node_id="condition-enemy-state",
            ),
        ),
    )
    compiled = compile_buff_graph_spec(spec, block_registry=registry).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(
        compiled,
        adapters=_enemy_anomaly_state_adapters(),
        tick=1,
        prepared_context={"enemy_anomaly_state": {"state": "shock", "active": True}},
    )

    assert result.passed is True
    assert result.outputs == {
        "passed": True,
        "actual_state": "shock",
        "expected_state": "shock",
        "active": True,
    }


def _enemy_anomaly_state_spec() -> BuffGraphSpec:
    registry = build_default_block_registry()
    enemy_context = registry.get("read.enemy_context").create_node(node_id="read-enemy")
    anomaly_state = registry.get("read.enemy_anomaly_state").create_node(
        node_id="read-anomaly-state",
        params={"anomaly_key": "ice"},
    )
    anomaly_bar = registry.get("read.enemy_anomaly_bar").create_node(
        node_id="read-anomaly-bar",
        params={"anomaly_key": "ice"},
    )
    enemy_state = registry.get("condition.enemy_state").create_node(
        node_id="condition-enemy-state",
        params={"expected_state": "frost", "active": True},
    )
    last_observed = registry.get("state.last_observed_enemy_state").create_node(
        node_id="last-observed",
        params={"state_key": "last-frost-state"},
    )
    edge_state = registry.get("read.enemy_edge_state").create_node(
        node_id="read-edge-state",
        params={"edge_key": "frost"},
    )
    edge_transition = registry.get("condition.edge_transition").create_node(
        node_id="edge-transition",
        params={"transition": "rising"},
    )
    edge_memory = registry.get("state.edge_memory").create_node(
        node_id="edge-memory",
        params={"state_key": "frost-edge"},
    )
    dot_state = registry.get("read.dot_runtime_state").create_node(
        node_id="read-dot-state",
        params={"dot_key": "burn"},
    )
    anomaly_signal = registry.get("state.anomaly_signal").create_node(
        node_id="anomaly-signal",
        params={"signal_key": "frost-signal"},
    )
    return BuffGraphSpec.draft_from_xlogic(
        graph_id="enemy-anomaly-state-blocks",
        display_name="Enemy Anomaly State Blocks",
        owner_kind=OwnerKind.UNKNOWN,
        owner_name="unknown:enemy-anomaly-state-blocks",
        source_buff_index=None,
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/enemy_state_read.py",
        nodes=(
            enemy_context,
            anomaly_state,
            anomaly_bar,
            enemy_state,
            last_observed,
            edge_state,
            edge_transition,
            edge_memory,
            dot_state,
            anomaly_signal,
        ),
        edges=(
            BuffGraphEdge(edge_id="edge-1", source_node_id="read-enemy", target_node_id="read-anomaly-state"),
            BuffGraphEdge(edge_id="edge-2", source_node_id="read-enemy", target_node_id="read-anomaly-bar"),
            BuffGraphEdge(
                edge_id="edge-3",
                source_node_id="read-anomaly-state",
                target_node_id="condition-enemy-state",
            ),
            BuffGraphEdge(
                edge_id="edge-4",
                source_node_id="read-anomaly-state",
                target_node_id="last-observed",
            ),
            BuffGraphEdge(
                edge_id="edge-5",
                source_node_id="read-edge-state",
                target_node_id="edge-transition",
            ),
            BuffGraphEdge(
                edge_id="edge-6",
                source_node_id="read-edge-state",
                target_node_id="edge-memory",
            ),
            BuffGraphEdge(
                edge_id="edge-7",
                source_node_id="read-anomaly-state",
                target_node_id="anomaly-signal",
            ),
            BuffGraphEdge(
                edge_id="edge-8",
                source_node_id="read-anomaly-bar",
                target_node_id="anomaly-signal",
            ),
            BuffGraphEdge(
                edge_id="edge-9",
                source_node_id="read-dot-state",
                target_node_id="anomaly-signal",
            ),
        ),
    )


def _enemy_anomaly_state_adapters() -> dict[str, object]:
    adapters: dict[str, object] = {}
    for group in (
        build_enemy_anomaly_state_read_adapters(),
        build_enemy_anomaly_state_condition_adapters(),
        build_enemy_anomaly_state_state_adapters(),
    ):
        adapters.update(group)
    return adapters
