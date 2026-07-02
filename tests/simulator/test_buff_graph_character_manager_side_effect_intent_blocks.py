from zsim.sim_progress.BuffGraph.adapters.condition_adapters import (
    build_character_manager_side_effect_condition_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.effect_adapters import (
    build_character_manager_side_effect_effect_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.read_adapters import (
    build_character_manager_side_effect_read_adapters,
    build_low_risk_read_adapters,
    build_runtime_command_scheduled_signal_read_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.state_adapters import (
    build_character_manager_side_effect_state_adapters,
)
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.runtime.compiler import compile_buff_graph_spec
from zsim.sim_progress.BuffGraph.runtime.executor import execute_compiled_buff_graph
from zsim.sim_progress.BuffGraph.runtime.trace import BuffGraphTraceKind, validate_buff_graph_trace
from zsim.sim_progress.BuffGraph.spec import BuffGraphEdge, BuffGraphSpec, OwnerKind


CHARACTER_MANAGER_BLOCK_IDS = {
    "condition.hit_frame",
    "condition.skill_tag_in",
    "condition.skill_owner_not_self",
    "condition.operating_character",
    "condition.skill_owner",
    "condition.character_state",
    "condition.cooldown_ready",
    "condition.preload_tick",
    "read.next_team_member",
    "state.last_observed_skill",
    "effect.update_character_manager",
    "effect.force_quick_assist",
    "effect.spawn_coattack",
    "effect.spawn_extra_attack",
    "effect.spawn_planned_skill_node",
    "effect.update_character_resource",
    "effect.external_add_skill",
}


def test_character_manager_side_effect_blocks_are_registered_and_compile() -> None:
    registry = build_default_block_registry()

    assert CHARACTER_MANAGER_BLOCK_IDS <= {block.block_id for block in registry.all()}

    result = compile_buff_graph_spec(_character_manager_spec(), block_registry=registry)

    assert result.passed is True
    assert result.compiled is not None


def test_character_manager_side_effect_graph_produces_intents_only() -> None:
    registry = build_default_block_registry()
    compiled = compile_buff_graph_spec(
        _character_manager_spec(),
        block_registry=registry,
    ).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(
        compiled,
        adapters=_character_manager_adapters(),
        tick=42,
        prepared_context={
            "tick": 42,
            "source_buff_index": "Buff-Test-Character-Intent",
            "name_box": ["Alice", "Yuzuha", "Nicole"],
            "foreground_character": "Alice",
            "prepared_owner": "Alice",
            "skill_node": {
                "skill_tag": "EX",
                "trigger_level": 2,
                "hit_index": 3,
                "is_last_hit": True,
                "owner": "Yuzuha",
            },
            "character_states": {"Yuzuha": {"victory_state": True}},
            "cooldowns": {"assist-window": 10},
            "state": {"last-skill": {"skill_tag": "NA"}},
        },
    )

    assert result.passed is True
    assert result.node_outputs["hit-frame"]["passed"] is True
    assert result.node_outputs["skill-tag"]["passed"] is True
    assert result.node_outputs["owner-not-self"]["passed"] is True
    assert result.node_outputs["operating-character"]["passed"] is True
    assert result.node_outputs["skill-owner"]["passed"] is True
    assert result.node_outputs["character-state"]["passed"] is True
    assert result.node_outputs["cooldown-ready"]["passed"] is True
    assert result.node_outputs["preload-tick"]["passed"] is True
    assert result.node_outputs["last-observed-skill"]["changed"] is True
    assert result.node_outputs["next-team-member"] == {
        "character": "Yuzuha",
        "team_index": 1,
    }
    assert result.node_outputs["spawn-coattack"]["character_side_effect_intent"] == {
        "intent_type": "character_side_effect",
        "action": "spawn_coattack",
        "target": "Yuzuha",
        "skill_tag": "EX-Coattack",
        "payload": {"source": "unit-test"},
        "enabled": True,
        "source_buff_index": "Buff-Test-Character-Intent",
    }
    assert result.node_outputs["external-add-skill"]["character_side_effect_intent"] == {
        "intent_type": "character_side_effect",
        "action": "external_add_skill",
        "skill_tag": "EX-Coattack",
        "payload": {},
        "enabled": True,
        "source_buff_index": "Buff-Test-Character-Intent",
    }
    assert "RuntimeCommandPort" not in str(result.node_outputs)
    assert "ScheduleDispatchPort" not in str(result.node_outputs)
    assert "ScheduledEventEmitter" not in str(result.node_outputs)
    assert validate_buff_graph_trace(result.trace) == ()
    assert any(event.kind is BuffGraphTraceKind.EFFECT_REQUESTED for event in result.trace.events)


def test_character_side_effect_intent_can_be_disabled_by_condition() -> None:
    registry = build_default_block_registry()
    skill = registry.get("read.skill_node").create_node(node_id="read-skill")
    hit = registry.get("condition.hit_frame").create_node(
        node_id="hit-frame",
        params={"expected_hit_index": 99},
    )
    extra_attack = registry.get("effect.spawn_extra_attack").create_node(
        node_id="spawn-extra-attack",
        params={"skill_tag": "EX-Extra"},
    )
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="disabled-character-side-effect-intent",
        display_name="Disabled Character Side Effect Intent",
        owner_kind=OwnerKind.UNKNOWN,
        owner_name="unknown:disabled-character-side-effect-intent",
        source_buff_index=None,
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/AliceCinema6Trigger.py",
        nodes=(skill, hit, extra_attack),
        edges=(
            BuffGraphEdge(edge_id="edge-1", source_node_id="read-skill", target_node_id="hit-frame"),
            BuffGraphEdge(edge_id="edge-2", source_node_id="hit-frame", target_node_id="spawn-extra-attack"),
        ),
    )
    compiled = compile_buff_graph_spec(spec, block_registry=registry).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(
        compiled,
        adapters=_character_manager_adapters(),
        tick=7,
        prepared_context={"skill_node": {"skill_tag": "EX", "hit_index": 3}},
    )

    assert result.passed is True
    assert result.node_outputs["hit-frame"]["passed"] is False
    assert result.outputs["character_side_effect_intent"]["enabled"] is False


def _character_manager_spec() -> BuffGraphSpec:
    registry = build_default_block_registry()
    tick = registry.get("read.current_tick").create_node(node_id="read-tick")
    skill = registry.get("read.skill_node").create_node(node_id="read-skill")
    next_member = registry.get("read.next_team_member").create_node(node_id="next-team-member")
    hit = registry.get("condition.hit_frame").create_node(
        node_id="hit-frame",
        params={"expected_hit_index": 3, "require_last_hit": True},
    )
    tag = registry.get("condition.skill_tag_in").create_node(
        node_id="skill-tag",
        params={"skill_tags": ["EX", "EX-A"]},
    )
    owner_not_self = registry.get("condition.skill_owner_not_self").create_node(
        node_id="owner-not-self"
    )
    operating = registry.get("condition.operating_character").create_node(
        node_id="operating-character",
        params={"character": "Yuzuha"},
    )
    skill_owner = registry.get("condition.skill_owner").create_node(
        node_id="skill-owner",
        params={"owner": "Yuzuha"},
    )
    character_state = registry.get("condition.character_state").create_node(
        node_id="character-state",
        params={"character": "Yuzuha", "state_key": "victory_state", "expected_value": True},
    )
    cooldown = registry.get("condition.cooldown_ready").create_node(
        node_id="cooldown-ready",
        params={"cooldown_key": "assist-window", "cooldown_ticks": 20},
    )
    preload = registry.get("condition.preload_tick").create_node(
        node_id="preload-tick",
        params={"expected_tick": 42},
    )
    last_skill = registry.get("state.last_observed_skill").create_node(
        node_id="last-observed-skill",
        params={"state_key": "last-skill"},
    )
    update_manager = registry.get("effect.update_character_manager").create_node(
        node_id="update-manager",
        params={"manager": "quick_assist_trigger", "operation": "update_myself"},
    )
    quick_assist = registry.get("effect.force_quick_assist").create_node(
        node_id="force-quick-assist",
        params={"target": "Yuzuha"},
    )
    coattack = registry.get("effect.spawn_coattack").create_node(
        node_id="spawn-coattack",
        params={"target": "Yuzuha", "skill_tag": "EX-Coattack", "payload": {"source": "unit-test"}},
    )
    extra_attack = registry.get("effect.spawn_extra_attack").create_node(
        node_id="spawn-extra-attack",
        params={"target": "Yuzuha", "skill_tag": "EX-Extra"},
    )
    planned_skill = registry.get("effect.spawn_planned_skill_node").create_node(
        node_id="spawn-planned-skill",
        params={"skill_tag": "EX-Planned", "scheduled_tick": 43},
    )
    character_resource = registry.get("effect.update_character_resource").create_node(
        node_id="update-character-resource",
        params={"resource": "adrenaline", "mode": "add", "payload": {"value": 1}},
    )
    external_add_skill = registry.get("effect.external_add_skill").create_node(
        node_id="external-add-skill",
        params={"skill_tag": "EX-Coattack"},
    )
    return BuffGraphSpec.draft_from_xlogic(
        graph_id="character-manager-side-effect-intents",
        display_name="Character Manager Side Effect Intents",
        owner_kind=OwnerKind.UNKNOWN,
        owner_name="unknown:character-manager-side-effect-intents",
        source_buff_index=None,
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/VivianCoattackTrigger.py",
        nodes=(
            tick,
            skill,
            next_member,
            hit,
            tag,
            owner_not_self,
            operating,
            skill_owner,
            character_state,
            cooldown,
            preload,
            last_skill,
            update_manager,
            quick_assist,
            coattack,
            extra_attack,
            planned_skill,
            character_resource,
            external_add_skill,
        ),
        edges=(
            BuffGraphEdge(edge_id="edge-1", source_node_id="read-tick", target_node_id="cooldown-ready"),
            BuffGraphEdge(edge_id="edge-2", source_node_id="read-tick", target_node_id="preload-tick"),
            BuffGraphEdge(edge_id="edge-3", source_node_id="read-skill", target_node_id="hit-frame"),
            BuffGraphEdge(edge_id="edge-4", source_node_id="read-skill", target_node_id="skill-tag"),
            BuffGraphEdge(edge_id="edge-5", source_node_id="read-skill", target_node_id="owner-not-self"),
            BuffGraphEdge(edge_id="edge-6", source_node_id="read-skill", target_node_id="skill-owner"),
            BuffGraphEdge(edge_id="edge-7", source_node_id="read-skill", target_node_id="last-observed-skill"),
            BuffGraphEdge(edge_id="edge-8", source_node_id="next-team-member", target_node_id="operating-character"),
            BuffGraphEdge(edge_id="edge-9", source_node_id="skill-tag", target_node_id="update-manager"),
            BuffGraphEdge(edge_id="edge-10", source_node_id="owner-not-self", target_node_id="force-quick-assist"),
            BuffGraphEdge(edge_id="edge-11", source_node_id="hit-frame", target_node_id="spawn-coattack"),
            BuffGraphEdge(edge_id="edge-12", source_node_id="character-state", target_node_id="spawn-extra-attack"),
            BuffGraphEdge(edge_id="edge-13", source_node_id="cooldown-ready", target_node_id="spawn-planned-skill"),
            BuffGraphEdge(edge_id="edge-14", source_node_id="preload-tick", target_node_id="update-character-resource"),
            BuffGraphEdge(edge_id="edge-15", source_node_id="skill-owner", target_node_id="external-add-skill"),
        ),
    )


def _character_manager_adapters() -> dict[str, object]:
    adapters: dict[str, object] = {}
    for group in (
        build_low_risk_read_adapters(),
        build_runtime_command_scheduled_signal_read_adapters(),
        build_character_manager_side_effect_read_adapters(),
        build_character_manager_side_effect_condition_adapters(),
        build_character_manager_side_effect_state_adapters(),
        build_character_manager_side_effect_effect_adapters(),
    ):
        adapters.update(group)
    return adapters
