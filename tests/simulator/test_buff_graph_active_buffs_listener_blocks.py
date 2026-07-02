from zsim.sim_progress.BuffGraph.adapters.condition_adapters import (
    build_prepared_context_condition_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.effect_adapters import (
    build_active_buffs_listener_effect_adapters,
    build_prepared_context_effect_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.read_adapters import (
    build_active_buffs_listener_read_adapters,
    build_prepared_context_read_adapters,
)
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.runtime.compiler import compile_buff_graph_spec
from zsim.sim_progress.BuffGraph.runtime.executor import execute_compiled_buff_graph
from zsim.sim_progress.BuffGraph.runtime.trace import validate_buff_graph_trace
from zsim.sim_progress.BuffGraph.spec import BuffGraphEdge, BuffGraphSpec, OwnerKind


def test_active_buffs_listener_blocks_are_registered_and_compile() -> None:
    registry = build_default_block_registry()

    block_ids = {block.block_id for block in registry.all()}

    assert {
        "read.active_buffs_for_equipper",
        "read.listener_signal",
        "effect.register_listener",
        "effect.consume_listener_signal",
    } <= block_ids

    for spec in (_active_buffs_spec(), _listener_signal_spec()):
        result = compile_buff_graph_spec(spec, block_registry=registry)

        assert result.passed is True
        assert result.compiled is not None


def test_active_buffs_graph_reads_context_for_prepared_equipper() -> None:
    registry = build_default_block_registry()
    compiled = compile_buff_graph_spec(
        _active_buffs_spec(),
        block_registry=registry,
    ).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(
        compiled,
        adapters=_active_buffs_listener_adapters(),
        tick=120,
        prepared_context={
            "prepared_equipper": "EquipperA",
            "active_buffs_by_equipper": {
                "EquipperA": [
                    {"buff_index": "buff-a", "active": True},
                    {"buff_index": "buff-b", "active": True},
                    {"buff_index": "buff-expired", "active": False},
                ],
                "EquipperB": [{"buff_index": "other-buff", "active": True}],
            },
        },
    )

    assert result.passed is True
    assert result.node_outputs["equipper"] == {"equipper": "EquipperA"}
    assert result.outputs["equipper"] == "EquipperA"
    assert result.outputs["active_buff_count"] == 2
    assert [buff["buff_index"] for buff in result.outputs["active_buffs"]] == [
        "buff-a",
        "buff-b",
    ]
    assert validate_buff_graph_trace(result.trace) == ()


def test_active_buffs_graph_can_filter_flat_active_buff_collection() -> None:
    registry = build_default_block_registry()
    active_buffs = registry.get("read.active_buffs_for_equipper").create_node(
        node_id="active-buffs"
    )
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="active-buffs-flat",
        display_name="Active Buffs Flat Collection",
        owner_kind=OwnerKind.W_ENGINE,
        owner_name="EquipperA",
        source_buff_index="template-a",
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/IceJadeTeaPotExtraDMGBonus.py",
        nodes=(active_buffs,),
    )
    compiled = compile_buff_graph_spec(spec, block_registry=registry).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(
        compiled,
        adapters=_active_buffs_listener_adapters(),
        tick=1,
        prepared_context={
            "prepared_equipper": "EquipperA",
            "active_buffs": {
                "buff-a": {"buff_index": "buff-a", "equipper": "EquipperA", "active": True},
                "buff-b": {"buff_index": "buff-b", "owner": "EquipperA", "active": True},
                "buff-c": {"buff_index": "buff-c", "equipper": "EquipperB", "active": True},
            },
        },
    )

    assert result.passed is True
    assert result.outputs["active_buff_count"] == 2
    assert {buff["buff_index"] for buff in result.outputs["active_buffs"]} == {
        "buff-a",
        "buff-b",
    }


def test_listener_graph_registers_and_consumes_signal_without_runtime_command() -> None:
    registry = build_default_block_registry()
    compiled = compile_buff_graph_spec(
        _listener_signal_spec(),
        block_registry=registry,
    ).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(
        compiled,
        adapters=_active_buffs_listener_adapters(),
        tick=240,
        prepared_context={
            "prepared_owner": "OwnerA",
            "prepared_equipper": "EquipperA",
            "source_buff_index": "listener-source-a",
            "listener_signals": {
                "buff-refresh": {
                    "listener_key": "buff-refresh",
                    "trigger_buff_index": "trigger-a",
                    "count": 2,
                }
            },
        },
    )

    assert result.passed is True
    assert result.node_outputs["listener-signal"] == {
        "listener_signal": {
            "listener_key": "buff-refresh",
            "trigger_buff_index": "trigger-a",
            "count": 2,
        },
        "matched": True,
        "listener_key": "buff-refresh",
    }
    assert result.node_outputs["register"] == {
        "listener_registration": {
            "listener_key": "buff-refresh",
            "source_buff_index": "listener-source-a",
            "owner": "OwnerA",
            "equipper": "EquipperA",
        }
    }
    assert result.outputs == {
        "listener_consumption": {
            "listener_key": "buff-refresh",
            "consumed": True,
            "signal": {
                "listener_key": "buff-refresh",
                "trigger_buff_index": "trigger-a",
                "count": 2,
            },
        }
    }
    assert "command" not in result.node_outputs["register"]
    assert "command" not in result.outputs
    assert validate_buff_graph_trace(result.trace) == ()


def _active_buffs_spec() -> BuffGraphSpec:
    registry = build_default_block_registry()
    equipper = registry.get("read.prepared_equipper").create_node(node_id="equipper")
    active_buffs = registry.get("read.active_buffs_for_equipper").create_node(
        node_id="active-buffs"
    )
    return BuffGraphSpec.draft_from_xlogic(
        graph_id="active-buffs-for-equipper",
        display_name="Active Buffs For Equipper",
        owner_kind=OwnerKind.W_ENGINE,
        owner_name="EquipperA",
        source_buff_index="template-a",
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/IceJadeTeaPotExtraDMGBonus.py",
        nodes=(equipper, active_buffs),
        edges=(
            BuffGraphEdge(
                edge_id="edge-1",
                source_node_id="equipper",
                target_node_id="active-buffs",
            ),
        ),
    )


def _listener_signal_spec() -> BuffGraphSpec:
    registry = build_default_block_registry()
    listener_signal = registry.get("read.listener_signal").create_node(
        node_id="listener-signal",
        params={"listener_key": "buff-refresh"},
    )
    register = registry.get("effect.register_listener").create_node(
        node_id="register",
        params={"listener_key": "buff-refresh"},
    )
    consume = registry.get("effect.consume_listener_signal").create_node(
        node_id="consume",
        params={"listener_key": "buff-refresh"},
    )
    return BuffGraphSpec.draft_from_xlogic(
        graph_id="listener-signal-context",
        display_name="Listener Signal Context",
        owner_kind=OwnerKind.W_ENGINE,
        owner_name="EquipperA",
        source_buff_index="listener-source-a",
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/ZanshinHerbCase.py",
        nodes=(listener_signal, register, consume),
        edges=(
            BuffGraphEdge(
                edge_id="edge-1",
                source_node_id="listener-signal",
                target_node_id="consume",
            ),
        ),
    )


def _active_buffs_listener_adapters() -> dict[str, object]:
    adapters: dict[str, object] = {}
    for group in (
        build_prepared_context_read_adapters(),
        build_active_buffs_listener_read_adapters(),
        build_prepared_context_condition_adapters(),
        build_prepared_context_effect_adapters(),
        build_active_buffs_listener_effect_adapters(),
    ):
        adapters.update(group)
    return adapters
