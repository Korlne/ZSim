from zsim.sim_progress.BuffGraph.adapters.condition_adapters import (
    build_enemy_anomaly_state_condition_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.effect_adapters import (
    build_dot_anomaly_output_effect_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.read_adapters import (
    build_enemy_anomaly_state_read_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.state_adapters import (
    build_dot_anomaly_output_state_adapters,
)
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.runtime.compiler import compile_buff_graph_spec
from zsim.sim_progress.BuffGraph.runtime.executor import execute_compiled_buff_graph
from zsim.sim_progress.BuffGraph.runtime.trace import BuffGraphTraceKind, validate_buff_graph_trace
from zsim.sim_progress.BuffGraph.spec import BuffGraphEdge, BuffGraphSpec, OwnerKind


DOT_ANOMALY_OUTPUT_BLOCK_IDS = {
    "effect.spawn_anomaly_output",
    "effect.start_dot",
    "effect.register_dot_runtime",
    "state.counter",
}


def test_dot_anomaly_output_blocks_are_registered_and_compile() -> None:
    registry = build_default_block_registry()

    assert DOT_ANOMALY_OUTPUT_BLOCK_IDS <= {block.block_id for block in registry.all()}

    result = compile_buff_graph_spec(_dot_anomaly_spec(), block_registry=registry)

    assert result.passed is True
    assert result.compiled is not None


def test_dot_anomaly_output_graph_produces_intents_only() -> None:
    registry = build_default_block_registry()
    compiled = compile_buff_graph_spec(_dot_anomaly_spec(), block_registry=registry).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(
        compiled,
        adapters=_dot_anomaly_adapters(),
        tick=64,
        prepared_context={
            "source_buff_index": "Buff-Test-DOT-Anomaly",
            "prepared_owner": "Vivian",
            "enemy_context": {
                "anomaly_states": {"ether": {"state": "corruption", "active": True}},
            },
            "dot_runtime_states": {"vivian-dot": {"active": False}},
            "state": {"polarity-counter": 2},
        },
    )

    assert result.passed is True
    assert result.node_outputs["counter"] == {"count": 3, "active": True}
    assert result.node_outputs["spawn-anomaly-output"]["anomaly_output_intent"] == {
        "intent_type": "anomaly_output",
        "anomaly_key": "ether",
        "output_type": "polarity_disorder",
        "payload": {"source": "unit-test"},
        "enabled": True,
        "source_buff_index": "Buff-Test-DOT-Anomaly",
    }
    assert result.node_outputs["start-dot"]["dot_runtime_intent"] == {
        "intent_type": "dot_runtime",
        "action": "start_dot",
        "dot_key": "vivian-dot",
        "duration_ticks": 120,
        "payload": {},
        "enabled": True,
        "source_buff_index": "Buff-Test-DOT-Anomaly",
    }
    assert result.outputs["dot_runtime_intent"] == {
        "intent_type": "dot_runtime",
        "action": "register_dot_runtime",
        "dot_key": "vivian-dot",
        "payload": {},
        "enabled": True,
        "source_buff_index": "Buff-Test-DOT-Anomaly",
        "owner": "Vivian",
    }
    assert "RuntimeCommandPort" not in str(result.node_outputs)
    assert "ScheduleDispatchPort" not in str(result.node_outputs)
    assert "ScheduledEventEmitter" not in str(result.node_outputs)
    assert "DOTRuntimeMutation" not in str(result.node_outputs)
    assert validate_buff_graph_trace(result.trace) == ()
    assert any(event.kind is BuffGraphTraceKind.EFFECT_REQUESTED for event in result.trace.events)


def _dot_anomaly_spec() -> BuffGraphSpec:
    registry = build_default_block_registry()
    enemy_context = registry.get("read.enemy_context").create_node(node_id="enemy-context")
    anomaly_state = registry.get("read.enemy_anomaly_state").create_node(
        node_id="anomaly-state",
        params={"anomaly_key": "ether"},
    )
    enemy_state = registry.get("condition.enemy_state").create_node(
        node_id="enemy-state",
        params={"expected_state": "corruption", "active": True, "anomaly_key": "ether"},
    )
    counter = registry.get("state.counter").create_node(
        node_id="counter",
        params={"state_key": "polarity-counter", "step": 1},
    )
    dot_state = registry.get("read.dot_runtime_state").create_node(
        node_id="dot-state",
        params={"dot_key": "vivian-dot"},
    )
    anomaly_output = registry.get("effect.spawn_anomaly_output").create_node(
        node_id="spawn-anomaly-output",
        params={
            "anomaly_key": "ether",
            "output_type": "polarity_disorder",
            "payload": {"source": "unit-test"},
        },
    )
    start_dot = registry.get("effect.start_dot").create_node(
        node_id="start-dot",
        params={"dot_key": "vivian-dot", "duration_ticks": 120},
    )
    register_dot = registry.get("effect.register_dot_runtime").create_node(
        node_id="register-dot",
        params={"dot_key": "vivian-dot"},
    )
    return BuffGraphSpec.draft_from_xlogic(
        graph_id="dot-anomaly-output-intents",
        display_name="DOT Anomaly Output Intents",
        owner_kind=OwnerKind.UNKNOWN,
        owner_name="unknown:dot-anomaly-output-intents",
        source_buff_index=None,
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/VivianDotTrigger.py",
        nodes=(
            enemy_context,
            anomaly_state,
            enemy_state,
            counter,
            dot_state,
            anomaly_output,
            start_dot,
            register_dot,
        ),
        edges=(
            BuffGraphEdge(edge_id="edge-1", source_node_id="enemy-context", target_node_id="anomaly-state"),
            BuffGraphEdge(edge_id="edge-2", source_node_id="anomaly-state", target_node_id="enemy-state"),
            BuffGraphEdge(edge_id="edge-3", source_node_id="enemy-state", target_node_id="counter"),
            BuffGraphEdge(edge_id="edge-4", source_node_id="counter", target_node_id="spawn-anomaly-output"),
            BuffGraphEdge(edge_id="edge-5", source_node_id="counter", target_node_id="start-dot"),
            BuffGraphEdge(edge_id="edge-6", source_node_id="counter", target_node_id="register-dot"),
        ),
    )


def _dot_anomaly_adapters() -> dict[str, object]:
    adapters: dict[str, object] = {}
    for group in (
        build_enemy_anomaly_state_read_adapters(),
        build_enemy_anomaly_state_condition_adapters(),
        build_dot_anomaly_output_state_adapters(),
        build_dot_anomaly_output_effect_adapters(),
    ):
        adapters.update(group)
    return adapters
