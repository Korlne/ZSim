from zsim.sim_progress.BuffGraph.adapters.compose_adapters import (
    build_calculator_runtime_formula_compose_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.condition_adapters import (
    build_calculator_runtime_formula_condition_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.effect_adapters import (
    build_calculator_runtime_formula_effect_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.read_adapters import (
    build_calculator_runtime_formula_read_adapters,
)
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.runtime.compiler import compile_buff_graph_spec
from zsim.sim_progress.BuffGraph.runtime.executor import execute_compiled_buff_graph
from zsim.sim_progress.BuffGraph.runtime.trace import BuffGraphTraceKind, validate_buff_graph_trace
from zsim.sim_progress.BuffGraph.spec import BuffGraphEdge, BuffGraphSpec, OwnerKind


CALCULATOR_FORMULA_BLOCK_IDS = {
    "read.calculator_attribute",
    "condition.numeric_compare",
    "compose.numeric_formula",
    "read.refinement",
    "read.current_action",
    "effect.publish_resource_refresh",
}


def test_calculator_runtime_formula_blocks_are_registered_and_compile() -> None:
    registry = build_default_block_registry()

    assert CALCULATOR_FORMULA_BLOCK_IDS <= {block.block_id for block in registry.all()}

    result = compile_buff_graph_spec(_calculator_formula_spec(), block_registry=registry)

    assert result.passed is True
    assert result.compiled is not None


def test_calculator_runtime_formula_graph_reads_values_and_produces_resource_intent_only() -> None:
    registry = build_default_block_registry()
    compiled = compile_buff_graph_spec(_calculator_formula_spec(), block_registry=registry).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(
        compiled,
        adapters=_calculator_formula_adapters(),
        tick=88,
        prepared_context={
            "source_buff_index": "Buff-Test-Calculator-Formula",
            "calculator_attributes": {"Alice": {"anomaly_mastery": 155}},
            "refinements": {"SliceOfTime": 5},
            "current_action": {"action_name": "EX", "trigger_level": 2},
        },
    )

    assert result.passed is True
    assert result.node_outputs["calculator-attribute"] == {
        "value": 155.0,
        "attribute": "anomaly_mastery",
        "source": "Alice",
    }
    assert result.node_outputs["numeric-compare"]["passed"] is True
    assert result.node_outputs["numeric-formula"]["value"] == 6.0
    assert result.node_outputs["refinement"]["refinement"] == 5.0
    assert result.node_outputs["resource-formula"]["value"] == 18.0
    assert result.node_outputs["current-action"] == {
        "action": {"action_name": "EX", "trigger_level": 2},
        "action_name": "EX",
        "trigger_level": 2,
    }
    assert result.outputs["resource_refresh_intent"] == {
        "intent_type": "resource_refresh",
        "resource": "energy",
        "amount": 18.0,
        "payload": {"source": "unit-test"},
        "enabled": True,
        "source_buff_index": "Buff-Test-Calculator-Formula",
    }
    assert "RuntimeCommandPort" not in str(result.node_outputs)
    assert "ScheduleDispatchPort" not in str(result.node_outputs)
    assert "ScheduledEventEmitter" not in str(result.node_outputs)
    assert validate_buff_graph_trace(result.trace) == ()
    assert any(event.kind is BuffGraphTraceKind.EFFECT_REQUESTED for event in result.trace.events)


def test_resource_refresh_intent_can_be_disabled_by_numeric_compare() -> None:
    registry = build_default_block_registry()
    calculator = registry.get("read.calculator_attribute").create_node(
        node_id="calculator-attribute",
        params={"attribute": "anomaly_mastery", "source": "Alice"},
    )
    compare = registry.get("condition.numeric_compare").create_node(
        node_id="numeric-compare",
        params={"operator": ">=", "expected": 200},
    )
    refresh = registry.get("effect.publish_resource_refresh").create_node(
        node_id="publish-resource-refresh",
        params={"resource": "energy", "amount": 12},
    )
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="disabled-resource-refresh-intent",
        display_name="Disabled Resource Refresh Intent",
        owner_kind=OwnerKind.UNKNOWN,
        owner_name="unknown:disabled-resource-refresh-intent",
        source_buff_index=None,
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/SeedAdditionalAbilityTrigger.py",
        nodes=(calculator, compare, refresh),
        edges=(
            BuffGraphEdge(
                edge_id="edge-1",
                source_node_id="calculator-attribute",
                target_node_id="numeric-compare",
            ),
            BuffGraphEdge(
                edge_id="edge-2",
                source_node_id="numeric-compare",
                target_node_id="publish-resource-refresh",
            ),
        ),
    )
    compiled = compile_buff_graph_spec(spec, block_registry=registry).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(
        compiled,
        adapters=_calculator_formula_adapters(),
        tick=9,
        prepared_context={"calculator_attributes": {"Alice": {"anomaly_mastery": 100}}},
    )

    assert result.passed is True
    assert result.node_outputs["numeric-compare"]["passed"] is False
    assert result.outputs["resource_refresh_intent"]["enabled"] is False


def _calculator_formula_spec() -> BuffGraphSpec:
    registry = build_default_block_registry()
    calculator = registry.get("read.calculator_attribute").create_node(
        node_id="calculator-attribute",
        params={"attribute": "anomaly_mastery", "source": "Alice"},
    )
    compare = registry.get("condition.numeric_compare").create_node(
        node_id="numeric-compare",
        params={"operator": ">=", "expected": 140},
    )
    formula = registry.get("compose.numeric_formula").create_node(
        node_id="numeric-formula",
        params={"operation": "linear", "subtract": 140, "multiplier": 0.4, "max_value": 20},
    )
    refinement = registry.get("read.refinement").create_node(
        node_id="refinement",
        params={"source": "SliceOfTime"},
    )
    resource_formula = registry.get("compose.numeric_formula").create_node(
        node_id="resource-formula",
        params={"operation": "linear", "subtract": 1, "multiplier": 2, "offset": 10},
    )
    current_action = registry.get("read.current_action").create_node(node_id="current-action")
    refresh = registry.get("effect.publish_resource_refresh").create_node(
        node_id="publish-resource-refresh",
        params={"resource": "energy", "payload": {"source": "unit-test"}},
    )
    return BuffGraphSpec.draft_from_xlogic(
        graph_id="calculator-runtime-formula-blocks",
        display_name="Calculator Runtime Formula Blocks",
        owner_kind=OwnerKind.UNKNOWN,
        owner_name="unknown:calculator-runtime-formula-blocks",
        source_buff_index=None,
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/AliceAdditionalAbilityApBonus.py",
        nodes=(calculator, compare, formula, refinement, resource_formula, current_action, refresh),
        edges=(
            BuffGraphEdge(
                edge_id="edge-1",
                source_node_id="calculator-attribute",
                target_node_id="numeric-compare",
            ),
            BuffGraphEdge(
                edge_id="edge-2",
                source_node_id="calculator-attribute",
                target_node_id="numeric-formula",
            ),
            BuffGraphEdge(
                edge_id="edge-3",
                source_node_id="refinement",
                target_node_id="resource-formula",
            ),
            BuffGraphEdge(
                edge_id="edge-4",
                source_node_id="resource-formula",
                target_node_id="publish-resource-refresh",
            ),
        ),
    )


def _calculator_formula_adapters() -> dict[str, object]:
    adapters: dict[str, object] = {}
    for group in (
        build_calculator_runtime_formula_read_adapters(),
        build_calculator_runtime_formula_condition_adapters(),
        build_calculator_runtime_formula_compose_adapters(),
        build_calculator_runtime_formula_effect_adapters(),
    ):
        adapters.update(group)
    return adapters
