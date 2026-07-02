from zsim.sim_progress.BuffGraph.adapters.compose_adapters import build_low_risk_compose_adapters
from zsim.sim_progress.BuffGraph.adapters.condition_adapters import build_low_risk_condition_adapters
from zsim.sim_progress.BuffGraph.adapters.effect_adapters import build_low_risk_effect_adapters
from zsim.sim_progress.BuffGraph.adapters.read_adapters import build_low_risk_read_adapters
from zsim.sim_progress.BuffGraph.adapters.state_adapters import build_low_risk_state_adapters
from zsim.sim_progress.BuffGraph.adapters.trigger_adapters import build_low_risk_trigger_adapters
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.runtime.compiler import compile_buff_graph_spec
from zsim.sim_progress.BuffGraph.runtime.executor import execute_compiled_buff_graph
from zsim.sim_progress.BuffGraph.runtime.trace import validate_buff_graph_trace
from zsim.sim_progress.BuffGraph.spec import BuffGraphEdge, BuffGraphSpec, OwnerKind


def test_low_risk_adapters_execute_hit_trigger_to_start_buff_command() -> None:
    registry = build_default_block_registry()
    trigger = registry.get("trigger.skill_hit").create_node(
        node_id="trigger",
        params={"skill_tag": "basic"},
    )
    effect = registry.get("effect.start_buff").create_node(
        node_id="effect",
        params={"buff_index": "Buff-角色-爱丽丝-影画6", "count": 1, "duration_ticks": 180},
    )
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="alice-cinema6",
        display_name="Alice Cinema 6",
        owner_kind=OwnerKind.CHARACTER,
        owner_name="Alice",
        source_buff_index="Buff-角色-爱丽丝-影画6",
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/AliceCinema6Trigger.py",
        nodes=(trigger, effect),
        edges=(BuffGraphEdge(edge_id="edge-1", source_node_id="trigger", target_node_id="effect"),),
    )
    compiled = compile_buff_graph_spec(spec, block_registry=registry).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(
        compiled,
        adapters=_low_risk_adapters(),
        tick=600,
        prepared_context={"event": {"kind": "skill_hit", "skill_tag": "basic"}},
    )

    assert result.passed is True
    assert result.node_outputs["trigger"] == {"matched": True}
    assert result.outputs == {
        "command": {
            "type": "start_buff",
            "buff_index": "Buff-角色-爱丽丝-影画6",
            "count": 1,
            "duration_ticks": 180,
        }
    }
    assert validate_buff_graph_trace(result.trace) == ()


def test_low_risk_condition_and_compose_adapters_gate_effects() -> None:
    registry = build_default_block_registry()
    identity = registry.get("condition.character_identity").create_node(
        node_id="identity",
        params={"owner_name": "Alice"},
    )
    active = registry.get("condition.buff_active").create_node(
        node_id="active",
        params={"buff_index": "buff-a"},
    )
    compose = registry.get("compose.all").create_node(node_id="all")
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="condition-compose",
        display_name="Condition Compose",
        owner_kind=OwnerKind.CHARACTER,
        owner_name="Alice",
        source_buff_index=None,
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/CannonRotor.py",
        nodes=(identity, active, compose),
        edges=(
            BuffGraphEdge(edge_id="edge-1", source_node_id="identity", target_node_id="all"),
            BuffGraphEdge(edge_id="edge-2", source_node_id="active", target_node_id="all"),
        ),
    )
    compiled = compile_buff_graph_spec(spec, block_registry=registry).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(
        compiled,
        adapters=_low_risk_adapters(),
        tick=1,
        prepared_context={"owner_name": "Alice", "buffs": {"buff-a": {"active": True, "count": 2}}},
    )

    assert result.passed is True
    assert result.node_outputs["identity"] == {"passed": True}
    assert result.node_outputs["active"]["passed"] is True
    assert result.outputs == {"passed": True}


def test_low_risk_read_and_state_adapters_are_context_only() -> None:
    registry = build_default_block_registry()
    read_tick = registry.get("read.current_tick").create_node(node_id="tick")
    cooldown = registry.get("state.cooldown_gate").create_node(
        node_id="cooldown",
        params={"cooldown_ticks": 120, "state_key": "last-hit"},
    )
    branch = registry.get("compose.branch").create_node(
        node_id="branch",
        params={"true_value": "ready", "false_value": "waiting"},
    )
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="state-read",
        display_name="State Read",
        owner_kind=OwnerKind.CHARACTER,
        owner_name="Alice",
        source_buff_index=None,
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/CannonRotor.py",
        nodes=(read_tick, cooldown, branch),
        edges=(BuffGraphEdge(edge_id="edge-1", source_node_id="cooldown", target_node_id="branch"),),
    )
    compiled = compile_buff_graph_spec(spec, block_registry=registry).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(
        compiled,
        adapters=_low_risk_adapters(),
        tick=300,
        prepared_context={"tick": 300, "state": {"last-hit": 120}},
    )

    assert result.passed is True
    assert result.node_outputs["tick"] == {"tick": 300}
    assert result.node_outputs["cooldown"] == {"ready": True, "last_tick": 120}
    assert result.outputs == {"condition": True, "selected": "ready"}


def _low_risk_adapters() -> dict[str, object]:
    adapters: dict[str, object] = {}
    for group in (
        build_low_risk_trigger_adapters(),
        build_low_risk_condition_adapters(),
        build_low_risk_read_adapters(),
        build_low_risk_effect_adapters(),
        build_low_risk_state_adapters(),
        build_low_risk_compose_adapters(),
    ):
        adapters.update(group)
    return adapters
