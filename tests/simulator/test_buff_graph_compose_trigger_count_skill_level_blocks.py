from zsim.sim_progress.BuffGraph.adapters.compose_adapters import build_low_risk_compose_adapters
from zsim.sim_progress.BuffGraph.adapters.condition_adapters import (
    build_prepared_context_condition_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.read_adapters import (
    build_prepared_context_read_adapters,
)
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.runtime.compiler import compile_buff_graph_spec
from zsim.sim_progress.BuffGraph.runtime.executor import execute_compiled_buff_graph
from zsim.sim_progress.BuffGraph.runtime.trace import validate_buff_graph_trace
from zsim.sim_progress.BuffGraph.spec import BuffGraphEdge, BuffGraphSpec, OwnerKind


def test_compose_trigger_count_and_skill_level_blocks_are_registered_and_compile() -> None:
    registry = build_default_block_registry()

    assert registry.get("compose.not").adapter_id == "compose.not.v1"
    assert (
        registry.get("condition.trigger_buff_count_compare").adapter_id
        == "condition.trigger_buff_count_compare.v1"
    )
    assert registry.get("condition.skill_trigger_level").adapter_id == (
        "condition.skill_trigger_level.v1"
    )

    result = compile_buff_graph_spec(_trigger_count_skill_level_spec(), block_registry=registry)

    assert result.passed is True
    assert result.compiled is not None


def test_trigger_count_compare_and_not_compose_execute_from_prepared_context() -> None:
    registry = build_default_block_registry()
    compiled = compile_buff_graph_spec(_trigger_count_skill_level_spec(), block_registry=registry)
    assert compiled.compiled is not None

    result = execute_compiled_buff_graph(
        compiled.compiled,
        adapters=_adapters(),
        tick=10,
        prepared_context={
            "trigger_buff_states": {
                "trigger-a": {
                    "active": True,
                    "count": 3,
                }
            },
            "event": {
                "trigger_level": 2,
            },
        },
    )

    assert result.passed is True
    assert result.node_outputs["count-compare"] == {
        "passed": True,
        "actual_count": 3,
        "expected_count": 2,
        "operator": "at_least",
    }
    assert result.node_outputs["skill-level"] == {
        "passed": True,
        "actual_level": 2,
        "expected_level": 2,
        "operator": "equals",
    }
    assert result.outputs == {"passed": False}
    assert validate_buff_graph_trace(result.trace) == ()


def test_trigger_count_compare_supports_comparison_operators() -> None:
    registry = build_default_block_registry()
    read_state = registry.get("read.trigger_buff_state").create_node(
        node_id="trigger-state",
        params={"trigger_buff_index": "trigger-a"},
    )
    compare = registry.get("condition.trigger_buff_count_compare").create_node(
        node_id="count-compare",
        params={"trigger_buff_index": "trigger-a", "expected_count": 4, "operator": "less_than"},
    )
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="trigger-count-compare",
        display_name="Trigger Count Compare",
        owner_kind=OwnerKind.W_ENGINE,
        owner_name="OwnerA",
        source_buff_index="template-a",
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/FlamemakerShakerApBonus.py",
        nodes=(read_state, compare),
        edges=(
            BuffGraphEdge(
                edge_id="edge-1",
                source_node_id="trigger-state",
                target_node_id="count-compare",
            ),
        ),
    )
    compiled = compile_buff_graph_spec(spec, block_registry=registry).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(
        compiled,
        adapters=_adapters(),
        tick=1,
        prepared_context={"trigger_buff_states": {"trigger-a": {"count": 3}}},
    )

    assert result.passed is True
    assert result.outputs == {
        "passed": True,
        "actual_count": 3,
        "expected_count": 4,
        "operator": "less_than",
    }


def _trigger_count_skill_level_spec() -> BuffGraphSpec:
    registry = build_default_block_registry()
    read_state = registry.get("read.trigger_buff_state").create_node(
        node_id="trigger-state",
        params={"trigger_buff_index": "trigger-a"},
    )
    count_compare = registry.get("condition.trigger_buff_count_compare").create_node(
        node_id="count-compare",
        params={"trigger_buff_index": "trigger-a", "expected_count": 2, "operator": "at_least"},
    )
    skill_level = registry.get("condition.skill_trigger_level").create_node(
        node_id="skill-level",
        params={"expected_level": 2, "operator": "equals"},
    )
    not_node = registry.get("compose.not").create_node(node_id="not-count")
    return BuffGraphSpec.draft_from_xlogic(
        graph_id="compose-trigger-count-skill-level",
        display_name="Compose Trigger Count Skill Level",
        owner_kind=OwnerKind.W_ENGINE,
        owner_name="OwnerA",
        source_buff_index="template-a",
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/CordisGerminaSNAAndQIgnoreDefense.py",
        nodes=(read_state, count_compare, skill_level, not_node),
        edges=(
            BuffGraphEdge(
                edge_id="edge-1",
                source_node_id="trigger-state",
                target_node_id="count-compare",
            ),
            BuffGraphEdge(
                edge_id="edge-2",
                source_node_id="count-compare",
                target_node_id="not-count",
            ),
        ),
    )


def _adapters() -> dict[str, object]:
    adapters: dict[str, object] = {}
    for group in (
        build_prepared_context_read_adapters(),
        build_prepared_context_condition_adapters(),
        build_low_risk_compose_adapters(),
    ):
        adapters.update(group)
    return adapters
