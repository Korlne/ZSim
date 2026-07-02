from zsim.sim_progress.BuffGraph.adapters.condition_adapters import (
    build_prepared_context_condition_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.effect_adapters import (
    build_prepared_context_effect_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.read_adapters import (
    build_prepared_context_read_adapters,
)
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.runtime.compiler import compile_buff_graph_spec
from zsim.sim_progress.BuffGraph.runtime.executor import execute_compiled_buff_graph
from zsim.sim_progress.BuffGraph.runtime.trace import validate_buff_graph_trace
from zsim.sim_progress.BuffGraph.spec import BuffGraphEdge, BuffGraphSpec, OwnerKind


def test_prepared_context_blocks_are_registered_and_compile() -> None:
    registry = build_default_block_registry()

    block_ids = {block.block_id for block in registry.all()}

    assert {
        "read.prepared_owner",
        "read.prepared_equipper",
        "read.prepared_template_buff",
        "read.trigger_buff_state",
        "read.foreground_character",
        "condition.equipper_identity",
        "condition.trigger_buff_active",
        "condition.trigger_buff_box_size_equals",
        "condition.equipper_is_background",
        "condition.equipper_is_foreground",
        "effect.update_template_buff",
        "effect.bind_prepared_record",
    } <= block_ids

    spec = _prepared_context_spec()
    result = compile_buff_graph_spec(spec, block_registry=registry)

    assert result.passed is True
    assert result.compiled is not None


def test_prepared_context_graph_reads_trigger_state_and_requests_template_update() -> None:
    registry = build_default_block_registry()
    compiled = compile_buff_graph_spec(
        _prepared_context_spec(),
        block_registry=registry,
    ).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(
        compiled,
        adapters=_prepared_context_adapters(),
        tick=240,
        prepared_context={
            "prepared_owner": "OwnerA",
            "prepared_equipper": "EquipperA",
            "foreground_character": "ForegroundA",
            "name_box": ["ForegroundA", "EquipperA", "SupportA"],
            "trigger_buff_states": {
                "trigger-a": {
                    "active": True,
                    "count": 2,
                    "built_in_buff_box": ["buff-a", "buff-b"],
                }
            },
            "template_buffs": {
                "template-a": {
                    "buff_index": "template-a",
                    "count": 0,
                }
            },
        },
    )

    assert result.passed is True
    assert result.node_outputs["equipper"] == {"equipper": "EquipperA"}
    assert result.node_outputs["foreground"] == {"character": "ForegroundA"}
    assert result.node_outputs["trigger-state"]["active"] is True
    assert result.node_outputs["trigger-state"]["built_in_buff_box_size"] == 2
    assert result.node_outputs["box-size"] == {
        "passed": True,
        "actual_size": 2,
        "expected_size": 2,
    }
    assert result.node_outputs["background"] == {"passed": True}
    assert result.outputs == {
        "command": {
            "type": "update_template_buff",
            "template_buff_index": "template-a",
            "mode": "set_count",
            "count": 1,
            "delta": None,
        }
    }
    assert validate_buff_graph_trace(result.trace) == ()


def test_prepared_context_foreground_and_identity_conditions_are_context_only() -> None:
    registry = build_default_block_registry()
    equipper = registry.get("read.prepared_equipper").create_node(node_id="equipper")
    foreground = registry.get("read.foreground_character").create_node(node_id="foreground")
    identity = registry.get("condition.equipper_identity").create_node(
        node_id="identity",
        params={"equipper": "EquipperA"},
    )
    foreground_condition = registry.get("condition.equipper_is_foreground").create_node(
        node_id="is-foreground"
    )
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="prepared-context-foreground",
        display_name="Prepared Context Foreground",
        owner_kind=OwnerKind.W_ENGINE,
        owner_name="EquipperA",
        source_buff_index="template-a",
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/HellfireGearsSpRBonus.py",
        nodes=(equipper, foreground, identity, foreground_condition),
        edges=(
            BuffGraphEdge(edge_id="edge-1", source_node_id="equipper", target_node_id="identity"),
            BuffGraphEdge(
                edge_id="edge-2",
                source_node_id="equipper",
                target_node_id="is-foreground",
            ),
            BuffGraphEdge(
                edge_id="edge-3",
                source_node_id="foreground",
                target_node_id="is-foreground",
            ),
        ),
    )
    compiled = compile_buff_graph_spec(spec, block_registry=registry).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(
        compiled,
        adapters=_prepared_context_adapters(),
        tick=1,
        prepared_context={
            "prepared_equipper": "EquipperA",
            "foreground_character": "EquipperA",
        },
    )

    assert result.passed is True
    assert result.node_outputs["identity"] == {"passed": True}
    assert result.outputs == {"passed": True}


def test_bind_prepared_record_effect_outputs_binding_not_runtime_command() -> None:
    registry = build_default_block_registry()
    bind_record = registry.get("effect.bind_prepared_record").create_node(
        node_id="bind",
        params={"record_key": "sp_bonus_seen", "value": True},
    )
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="prepared-record-binding",
        display_name="Prepared Record Binding",
        owner_kind=OwnerKind.W_ENGINE,
        owner_name="EquipperA",
        source_buff_index="template-a",
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/HellfireGearsSpRBonus.py",
        nodes=(bind_record,),
    )
    compiled = compile_buff_graph_spec(spec, block_registry=registry).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(
        compiled,
        adapters=_prepared_context_adapters(),
        tick=1,
        prepared_context={"prepared_owner": "OwnerA", "prepared_equipper": "EquipperA"},
    )

    assert result.passed is True
    assert "command" not in result.outputs
    assert result.outputs == {
        "binding": {
            "record_key": "sp_bonus_seen",
            "owner": "OwnerA",
            "equipper": "EquipperA",
            "value": True,
        }
    }


def _prepared_context_spec() -> BuffGraphSpec:
    registry = build_default_block_registry()
    equipper = registry.get("read.prepared_equipper").create_node(node_id="equipper")
    foreground = registry.get("read.foreground_character").create_node(node_id="foreground")
    trigger_state = registry.get("read.trigger_buff_state").create_node(
        node_id="trigger-state",
        params={"trigger_buff_index": "trigger-a"},
    )
    template_buff = registry.get("read.prepared_template_buff").create_node(
        node_id="template",
        params={"template_buff_index": "template-a"},
    )
    box_size = registry.get("condition.trigger_buff_box_size_equals").create_node(
        node_id="box-size",
        params={"trigger_buff_index": "trigger-a", "expected_size": 2},
    )
    background = registry.get("condition.equipper_is_background").create_node(
        node_id="background"
    )
    update_template = registry.get("effect.update_template_buff").create_node(
        node_id="update-template",
        params={"template_buff_index": "template-a", "mode": "set_count", "count": 1},
    )
    return BuffGraphSpec.draft_from_xlogic(
        graph_id="prepared-context-trigger-state",
        display_name="Prepared Context Trigger State",
        owner_kind=OwnerKind.W_ENGINE,
        owner_name="EquipperA",
        source_buff_index="template-a",
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/HellfireGearsSpRBonus.py",
        nodes=(
            equipper,
            foreground,
            trigger_state,
            template_buff,
            box_size,
            background,
            update_template,
        ),
        edges=(
            BuffGraphEdge(
                edge_id="edge-1",
                source_node_id="trigger-state",
                target_node_id="box-size",
            ),
            BuffGraphEdge(edge_id="edge-2", source_node_id="equipper", target_node_id="background"),
            BuffGraphEdge(
                edge_id="edge-3",
                source_node_id="foreground",
                target_node_id="background",
            ),
            BuffGraphEdge(edge_id="edge-4", source_node_id="template", target_node_id="update-template"),
            BuffGraphEdge(edge_id="edge-5", source_node_id="box-size", target_node_id="update-template"),
            BuffGraphEdge(
                edge_id="edge-6",
                source_node_id="background",
                target_node_id="update-template",
            ),
        ),
    )


def _prepared_context_adapters() -> dict[str, object]:
    adapters: dict[str, object] = {}
    for group in (
        build_prepared_context_read_adapters(),
        build_prepared_context_condition_adapters(),
        build_prepared_context_effect_adapters(),
    ):
        adapters.update(group)
    return adapters
