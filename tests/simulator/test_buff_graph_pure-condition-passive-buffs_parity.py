import json
from pathlib import Path

import pytest

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


FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "buff_graph" / "pure-condition-passive-buffs"


@pytest.mark.parametrize(
    "fixture_name",
    [
        "cordis-germina-crit-rate-bonus.json",
        "moonlight-lullaby-all-team-dmg-bonus.json",
    ],
)
def test_pure_condition_passive_xlogic_imports_to_graph_trace_and_output_fixture(
    fixture_name: str,
) -> None:
    fixture = json.loads((FIXTURE_ROOT / fixture_name).read_text(encoding="utf-8"))
    xlogic_path = Path(fixture["xlogic_path"])
    source = xlogic_path.read_text(encoding="utf-8")
    registry = build_default_block_registry()

    import_result = import_xlogic_to_graph(
        xlogic_path=fixture["xlogic_path"],
        source=source,
        owner_kind=OwnerKind(fixture["owner_kind"]),
        owner_name=fixture["owner_name"],
        source_buff_index=fixture["source_buff_index"],
        graph_id=fixture["case_id"],
        display_name=fixture["case_id"],
        block_registry=registry,
    )

    assert import_result.imported is True
    assert import_result.spec is not None
    assert import_result.unsupported_patterns == ()
    assert [node.block_id for node in import_result.spec.nodes] == fixture["expected_node_block_ids"]

    compile_result = compile_buff_graph_spec(import_result.spec, block_registry=registry)
    assert compile_result.passed is True
    assert compile_result.compiled is not None

    result = execute_compiled_buff_graph(
        compile_result.compiled,
        adapters=_low_risk_adapters(),
        tick=fixture["prepared_context"]["tick"],
        prepared_context=fixture["prepared_context"],
    )

    assert result.passed is True
    assert result.outputs == fixture["expected_final_output"]
    assert validate_buff_graph_trace(result.trace) == ()
    assert [(event.kind.value, event.checkpoint) for event in result.trace.events] == [
        tuple(item) for item in fixture["expected_trace_kind_checkpoint"]
    ]


def test_pure_condition_passive_wave_keeps_boundary_gaps_for_later_waves() -> None:
    fixture = json.loads((FIXTURE_ROOT / "wave-boundary-gaps.json").read_text(encoding="utf-8"))

    assert fixture["gaps"]
    assert {gap["next_wave"] for gap in fixture["gaps"]} == {"record-cooldown-stack-buffs"}
    assert all("custom" not in gap["reason"].lower() for gap in fixture["gaps"])


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
