from dataclasses import FrozenInstanceError

import pytest

from zsim.sim_progress.BuffGraph.spec import (
    BuffGraphEdge,
    BuffGraphNode,
    BuffGraphNodeViewState,
    BuffGraphSpec,
    BuffGraphViewState,
    BuffGraphViewport,
    OwnerKind,
    RuntimeStatus,
    validate_buff_graph_spec,
)
from zsim.sim_progress.BuffGraph.spec.schema import NodeFamily


def test_buff_graph_spec_keeps_required_business_fields() -> None:
    node = BuffGraphNode(
        node_id="trigger-hit",
        family=NodeFamily.TRIGGER,
        block_id="trigger.skill_hit",
        adapter_id="trigger.skill_hit.v1",
        params={"skill_tag": "basic"},
    )
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="alice-cinema6",
        display_name="Alice Cinema 6",
        owner_kind=OwnerKind.CHARACTER,
        owner_name="Alice",
        source_buff_index="Buff-角色-爱丽丝-影画6",
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/AliceCinema6Trigger.py",
        nodes=(node,),
    )

    assert spec.schema_version
    assert spec.node_library_version
    assert spec.adapter_contract_version
    assert spec.created_from_xlogic.endswith("AliceCinema6Trigger.py")
    assert spec.runtime_status is RuntimeStatus.LEGACY_PYTHON
    assert validate_buff_graph_spec(spec) == ()


def test_buff_graph_view_state_is_editor_state_not_behavior_source() -> None:
    view_state = BuffGraphViewState(
        graph_id="alice-cinema6",
        viewport=BuffGraphViewport(x=10, y=20, zoom=0.75),
        nodes=(BuffGraphNodeViewState(node_id="trigger-hit", x=100, y=240),),
        layout_hints={"group": "trigger"},
    )

    assert view_state.graph_id == "alice-cinema6"
    assert not hasattr(view_state, "runtime_status")
    assert not hasattr(view_state, "params")
    assert not hasattr(view_state, "edges")


def test_buff_graph_spec_rejects_custom_python_or_code_nodes() -> None:
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="bad-code-node",
        display_name="Bad Code Node",
        owner_kind=OwnerKind.CHARACTER,
        owner_name="Alice",
        source_buff_index=None,
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/AliceCinema6Trigger.py",
        nodes=(
            BuffGraphNode(
                node_id="custom",
                family=NodeFamily.EFFECT,
                block_id="custom_python.eval",
                adapter_id="python.exec",
            ),
        ),
    )

    errors = validate_buff_graph_spec(spec)

    assert [error.code for error in errors] == ["custom_python_node_forbidden"]


def test_visual_graph_default_requires_parity_timestamp() -> None:
    spec = BuffGraphSpec(
        schema_version="buff-graph-spec.v1",
        node_library_version="buff-graph-node-library.v1",
        adapter_contract_version="buff-graph-adapter-contract.v1",
        graph_id="alice-cinema6",
        display_name="Alice Cinema 6",
        owner_kind=OwnerKind.CHARACTER,
        owner_name="Alice",
        source_buff_index=None,
        created_from_xlogic=None,
        runtime_status=RuntimeStatus.VISUAL_GRAPH_DEFAULT,
        nodes=(),
        edges=(),
    )

    errors = validate_buff_graph_spec(spec)

    assert [error.code for error in errors] == ["default_requires_verification"]


def test_spec_is_frozen_and_edges_must_reference_known_nodes() -> None:
    node = BuffGraphNode(
        node_id="condition",
        family=NodeFamily.CONDITION,
        block_id="condition.buff_active",
        adapter_id="condition.buff_active.v1",
    )
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="edge-check",
        display_name="Edge Check",
        owner_kind=OwnerKind.W_ENGINE,
        owner_name="Cannon Rotor",
        source_buff_index=None,
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/CannonRotor.py",
        nodes=(node,),
        edges=(BuffGraphEdge(edge_id="edge-1", source_node_id="missing", target_node_id="condition"),),
    )

    with pytest.raises(FrozenInstanceError):
        spec.graph_id = "mutated"  # type: ignore[misc]

    assert [error.code for error in validate_buff_graph_spec(spec)] == ["unknown_source_node"]
