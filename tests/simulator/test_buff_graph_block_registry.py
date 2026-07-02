import pytest

from zsim.sim_progress.BuffGraph.adapters import (
    BuffGraphAdapter,
    BuffGraphAdapterContext,
    BuffGraphAdapterResult,
)
from zsim.sim_progress.BuffGraph.blocks import BuffGraphBlockDefinition, build_default_block_registry
from zsim.sim_progress.BuffGraph.spec.schema import NodeFamily, validate_buff_graph_spec
from zsim.sim_progress.BuffGraph.spec import BuffGraphSpec, OwnerKind


def test_default_registry_contains_controlled_block_families() -> None:
    registry = build_default_block_registry()

    families = {block.family for block in registry.all()}

    assert families == {
        NodeFamily.TRIGGER,
        NodeFamily.CONDITION,
        NodeFamily.READ,
        NodeFamily.EFFECT,
        NodeFamily.STATE,
        NodeFamily.COMPOSE,
    }
    assert registry.get("trigger.skill_hit").adapter_id == "trigger.skill_hit.v1"


def test_registry_creates_spec_nodes_that_validate() -> None:
    registry = build_default_block_registry()
    trigger = registry.get("trigger.skill_hit").create_node(
        node_id="node-trigger",
        params={"skill_tag": "1401_Cinema_6"},
    )
    effect = registry.get("effect.start_buff").create_node(
        node_id="node-effect",
        params={"target_buff_index": "Buff-角色-爱丽丝-影画6"},
    )
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="alice-cinema6",
        display_name="Alice Cinema 6",
        owner_kind=OwnerKind.CHARACTER,
        owner_name="Alice",
        source_buff_index="Buff-角色-爱丽丝-影画6",
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/AliceCinema6Trigger.py",
        nodes=(trigger, effect),
    )

    assert validate_buff_graph_spec(spec) == ()


def test_registry_rejects_code_or_python_blocks() -> None:
    with pytest.raises(ValueError, match="not Python/script/code nodes"):
        BuffGraphBlockDefinition(
            block_id="effect.custom_python",
            family=NodeFamily.EFFECT,
            display_name="Custom Python",
            adapter_id="python.exec",
        ).create_node(node_id="bad")

    with pytest.raises(ValueError, match="not Python/script/code nodes"):
        build_default_block_registry().register(
            BuffGraphBlockDefinition(
                block_id="script.escape_hatch",
                family=NodeFamily.EFFECT,
                display_name="Script",
                adapter_id="effect.script.v1",
            )
        )


def test_registry_rejects_duplicate_block_ids() -> None:
    registry = build_default_block_registry()
    existing = registry.get("trigger.skill_hit")

    with pytest.raises(ValueError, match="duplicate Buff graph block id"):
        registry.register(existing)


def test_adapter_base_contract_is_runtime_agnostic() -> None:
    class EchoAdapter:
        adapter_id = "test.echo.v1"

        def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
            return BuffGraphAdapterResult(
                outputs={"node_id": context.node.node_id},
                trace={"adapter_id": self.adapter_id},
            )

    adapter: BuffGraphAdapter = EchoAdapter()
    node = build_default_block_registry().get("read.current_tick").create_node(node_id="tick")
    result = adapter.execute(BuffGraphAdapterContext(graph_id="graph", node=node))

    assert result.outputs == {"node_id": "tick"}
    assert result.trace == {"adapter_id": "test.echo.v1"}
