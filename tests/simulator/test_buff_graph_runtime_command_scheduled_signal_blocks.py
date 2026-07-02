from zsim.sim_progress.BuffGraph.adapters.condition_adapters import (
    build_runtime_command_scheduled_signal_condition_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.effect_adapters import (
    build_runtime_command_scheduled_signal_effect_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.read_adapters import (
    build_low_risk_read_adapters,
    build_runtime_command_scheduled_signal_read_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.state_adapters import (
    build_runtime_command_scheduled_signal_state_adapters,
)
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.runtime.compiler import compile_buff_graph_spec
from zsim.sim_progress.BuffGraph.runtime.executor import execute_compiled_buff_graph
from zsim.sim_progress.BuffGraph.runtime.trace import BuffGraphTraceKind, validate_buff_graph_trace
from zsim.sim_progress.BuffGraph.spec import BuffGraphEdge, BuffGraphSpec, OwnerKind


def test_runtime_command_scheduled_signal_blocks_are_registered_and_compile() -> None:
    registry = build_default_block_registry()

    assert {
        "read.skill_node",
        "condition.tick_window",
        "state.scheduled_signal",
        "effect.issue_runtime_command",
        "effect.issue_allowed_runtime_command",
        "effect.emit_scheduled_event",
    } <= {block.block_id for block in registry.all()}

    result = compile_buff_graph_spec(_runtime_scheduled_spec(), block_registry=registry)

    assert result.passed is True
    assert result.compiled is not None


def test_runtime_command_scheduled_signal_graph_produces_intents_only() -> None:
    registry = build_default_block_registry()
    compiled = compile_buff_graph_spec(
        _runtime_scheduled_spec(),
        block_registry=registry,
    ).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(
        compiled,
        adapters=_runtime_scheduled_adapters(),
        tick=120,
        prepared_context={
            "tick": 120,
            "source_buff_index": "Buff-Test-Scheduled",
            "skill_node": {
                "skill_tag": "EX",
                "trigger_level": 2,
                "hit_index": 3,
                "is_last_hit": True,
            },
            "scheduled_signals": {
                "test-signal": {
                    "scheduled_tick": 120,
                    "active": True,
                    "payload": {"reason": "unit-test"},
                }
            },
        },
    )

    assert result.passed is True
    assert result.node_outputs["read-skill"]["skill_tag"] == "EX"
    assert result.node_outputs["tick-window"] == {
        "passed": True,
        "tick": 120,
        "start_tick": 100,
        "end_tick": 140,
    }
    assert result.node_outputs["scheduled-signal"]["scheduled_signal"] == {
        "signal_key": "test-signal",
        "scheduled_tick": 120,
        "current_tick": 120,
        "active": True,
        "payload": {"reason": "unit-test"},
    }
    assert result.node_outputs["runtime-command"]["runtime_command_intent"] == {
        "intent_type": "runtime_command",
        "command_scope": "runtime",
        "command_type": "buff_runtime",
        "command_name": "settle_buffs",
        "payload": {"mode": "candidate"},
        "enabled": True,
        "source_buff_index": "Buff-Test-Scheduled",
    }
    assert result.outputs["scheduled_event_intent"] == {
        "intent_type": "scheduled_event",
        "event_type": "skill_node",
        "scheduled_tick": 121,
        "payload": {"kind": "candidate"},
        "enabled": True,
        "source_buff_index": "Buff-Test-Scheduled",
    }
    assert "ScheduleDispatchPort" not in str(result.node_outputs)
    assert "RuntimeCommandPort" not in str(result.node_outputs)
    assert validate_buff_graph_trace(result.trace) == ()
    assert any(event.kind is BuffGraphTraceKind.EFFECT_REQUESTED for event in result.trace.events)


def test_allowed_runtime_command_intent_records_allowed_scope_without_dispatch() -> None:
    registry = build_default_block_registry()
    tick = registry.get("read.current_tick").create_node(node_id="tick")
    allowed = registry.get("effect.issue_allowed_runtime_command").create_node(
        node_id="allowed-runtime-command",
        params={
            "command_type": "resource",
            "command_name": "publish_resource_refresh",
            "payload": {"resource": "energy"},
        },
    )
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="allowed-runtime-command-intent",
        display_name="Allowed Runtime Command Intent",
        owner_kind=OwnerKind.UNKNOWN,
        owner_name="unknown:allowed-runtime-command-intent",
        source_buff_index=None,
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/ElegantVanitySpRecover.py",
        nodes=(tick, allowed),
        edges=(
            BuffGraphEdge(edge_id="edge-1", source_node_id="tick", target_node_id="allowed-runtime-command"),
        ),
    )
    compiled = compile_buff_graph_spec(spec, block_registry=registry).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(
        compiled,
        adapters=_runtime_scheduled_adapters(),
        tick=8,
        prepared_context={},
    )

    assert result.passed is True
    assert result.outputs["runtime_command_intent"]["command_scope"] == "allowed_runtime"
    assert result.outputs["runtime_command_intent"]["enabled"] is True


def _runtime_scheduled_spec() -> BuffGraphSpec:
    registry = build_default_block_registry()
    tick = registry.get("read.current_tick").create_node(node_id="read-tick")
    skill = registry.get("read.skill_node").create_node(node_id="read-skill")
    window = registry.get("condition.tick_window").create_node(
        node_id="tick-window",
        params={"start_tick": 100, "end_tick": 140},
    )
    signal = registry.get("state.scheduled_signal").create_node(
        node_id="scheduled-signal",
        params={"signal_key": "test-signal"},
    )
    runtime_command = registry.get("effect.issue_runtime_command").create_node(
        node_id="runtime-command",
        params={
            "command_type": "buff_runtime",
            "command_name": "settle_buffs",
            "payload": {"mode": "candidate"},
        },
    )
    scheduled_event = registry.get("effect.emit_scheduled_event").create_node(
        node_id="scheduled-event",
        params={
            "event_type": "skill_node",
            "scheduled_tick": 121,
            "payload": {"kind": "candidate"},
        },
    )
    return BuffGraphSpec.draft_from_xlogic(
        graph_id="runtime-command-scheduled-signal-blocks",
        display_name="Runtime Command Scheduled Signal Blocks",
        owner_kind=OwnerKind.UNKNOWN,
        owner_name="unknown:runtime-command-scheduled-signal-blocks",
        source_buff_index=None,
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/runtime_command_scheduled_read.py",
        nodes=(tick, skill, window, signal, runtime_command, scheduled_event),
        edges=(
            BuffGraphEdge(edge_id="edge-1", source_node_id="read-tick", target_node_id="tick-window"),
            BuffGraphEdge(edge_id="edge-2", source_node_id="read-tick", target_node_id="scheduled-signal"),
            BuffGraphEdge(edge_id="edge-3", source_node_id="tick-window", target_node_id="runtime-command"),
            BuffGraphEdge(edge_id="edge-4", source_node_id="scheduled-signal", target_node_id="scheduled-event"),
        ),
    )


def _runtime_scheduled_adapters() -> dict[str, object]:
    adapters: dict[str, object] = {}
    for group in (
        build_low_risk_read_adapters(),
        build_runtime_command_scheduled_signal_read_adapters(),
        build_runtime_command_scheduled_signal_condition_adapters(),
        build_runtime_command_scheduled_signal_state_adapters(),
        build_runtime_command_scheduled_signal_effect_adapters(),
    ):
        adapters.update(group)
    return adapters
