import json
from pathlib import Path

from zsim.sim_progress.BuffGraph.adapters.compose_adapters import build_low_risk_compose_adapters
from zsim.sim_progress.BuffGraph.adapters.condition_adapters import build_low_risk_condition_adapters
from zsim.sim_progress.BuffGraph.adapters.effect_adapters import build_low_risk_effect_adapters
from zsim.sim_progress.BuffGraph.adapters.read_adapters import build_low_risk_read_adapters
from zsim.sim_progress.BuffGraph.adapters.state_adapters import build_low_risk_state_adapters
from zsim.sim_progress.BuffGraph.adapters.trigger_adapters import build_low_risk_trigger_adapters
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.migration import import_xlogic_to_graph
from zsim.sim_progress.BuffGraph.runtime.compiler import compile_buff_graph_spec
from zsim.sim_progress.BuffGraph.runtime.executor import execute_compiled_buff_graph
from zsim.sim_progress.BuffGraph.runtime.trace import validate_buff_graph_trace
from zsim.sim_progress.BuffGraph.spec import OwnerKind


FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "buff_graph" / "low-risk-xlogic-parity"


def test_imported_low_risk_xlogic_matches_trace_and_output_fixture() -> None:
    fixture = json.loads((FIXTURE_ROOT / "alice-cinema6-hit-start-buff.json").read_text(encoding="utf-8"))
    registry = build_default_block_registry()
    import_result = import_xlogic_to_graph(
        xlogic_path=fixture["xlogic_path"],
        source=fixture["source"],
        owner_kind=OwnerKind(fixture["owner_kind"]),
        owner_name=fixture["owner_name"],
        source_buff_index=fixture["source_buff_index"],
        block_registry=registry,
    )
    assert import_result.imported is True
    assert import_result.spec is not None
    compiled = compile_buff_graph_spec(import_result.spec, block_registry=registry).compiled
    assert compiled is not None

    result = execute_compiled_buff_graph(
        compiled,
        adapters=_low_risk_adapters(),
        tick=600,
        prepared_context=fixture["prepared_context"],
    )

    assert result.passed is True
    assert result.outputs == fixture["expected_final_output"]
    assert validate_buff_graph_trace(result.trace) == ()
    assert [(event.kind.value, event.checkpoint) for event in result.trace.events] == [
        tuple(item) for item in fixture["expected_trace_kind_checkpoint"]
    ]


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
