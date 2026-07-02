from copy import deepcopy

from zsim.sim_progress.BuffGraph.adapters.condition_adapters import (
    build_yuzuha_cinema2_qte_signal_condition_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.effect_adapters import (
    build_yuzuha_cinema2_qte_signal_effect_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.read_adapters import (
    build_low_risk_read_adapters,
    build_yuzuha_cinema2_qte_signal_read_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.state_adapters import (
    build_yuzuha_cinema2_qte_signal_state_adapters,
)
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.runtime.compiler import compile_buff_graph_spec
from zsim.sim_progress.BuffGraph.runtime.executor import execute_compiled_buff_graph
from zsim.sim_progress.BuffGraph.runtime.trace import BuffGraphTraceKind, validate_buff_graph_trace
from zsim.sim_progress.BuffGraph.spec import BuffGraphEdge, BuffGraphSpec, OwnerKind


YUZUHA_CINEMA2_BLOCK_IDS = {
    "read.enemy_stun_state",
    "condition.enemy_stun_active",
    "state.pending_skill_node_signal",
    "effect.set_skill_node_force_qte_trigger",
    "effect.notify_schedule_process_state",
    "state.commit_cooldown_tick",
}


def test_yuzuha_cinema2_qte_signal_blocks_are_registered_and_compile() -> None:
    registry = build_default_block_registry()

    assert YUZUHA_CINEMA2_BLOCK_IDS <= {block.block_id for block in registry.all()}

    result = compile_buff_graph_spec(_yuzuha_cinema2_spec(), block_registry=registry)

    assert result.passed is True
    assert result.compiled is not None


def test_yuzuha_cinema2_qte_signal_graph_produces_intents_only() -> None:
    registry = build_default_block_registry()
    compiled = compile_buff_graph_spec(_yuzuha_cinema2_spec(), block_registry=registry).compiled
    assert compiled is not None

    skill_node = {
        "skill_tag": "1411_E_EX_A",
        "hit_index": 3,
        "is_last_hit": True,
        "force_qte_trigger": False,
    }
    original_skill_node = deepcopy(skill_node)
    result = execute_compiled_buff_graph(
        compiled,
        adapters=_yuzuha_cinema2_adapters(),
        tick=1500,
        prepared_context={
            "tick": 1500,
            "source_buff_index": "Buff-Yuzuha-Cinema2",
            "enemy_context": {"dynamic": {"stun": False}},
            "skill_node": skill_node,
            "state": {"yuzuha-c2-cooldown": 299},
            "YUZUHA_REPORT": True,
        },
    )

    assert result.passed is True
    assert result.node_outputs["read-stun"] == {
        "enemy_stun_state": {"active": False, "source": "prepared_enemy_context"},
        "active": False,
    }
    assert result.node_outputs["stun-gate"] == {
        "passed": True,
        "active": False,
        "expected_active": False,
    }
    assert result.node_outputs["skill-tag"]["passed"] is True
    assert result.node_outputs["hit-frame"]["passed"] is True
    assert result.node_outputs["cooldown-ready"]["passed"] is True
    assert result.node_outputs["cooldown-ready"]["elapsed"] == 1201
    assert result.node_outputs["capture-signal"]["pending_skill_node_signal"] == {
        "signal_key": "yuzuha-c2",
        "operation": "capture",
        "skill_node": original_skill_node,
        "pending": True,
    }
    assert result.node_outputs["force-qte"]["skill_node_mutation_intent"] == {
        "intent_type": "skill_node_mutation",
        "mutation": "set_force_qte_trigger",
        "field": "force_qte_trigger",
        "value": True,
        "skill_node": original_skill_node,
        "enabled": True,
        "payload": {},
        "source_buff_index": "Buff-Yuzuha-Cinema2",
    }
    assert result.node_outputs["process-state"]["process_state_notification_intent"] == {
        "intent_type": "process_state_notification",
        "action": "change_process_state",
        "reason": "yuzuha-cinema2-force-qte",
        "payload": {},
        "enabled": True,
        "source_buff_index": "Buff-Yuzuha-Cinema2",
    }
    assert result.outputs["cooldown_commit_intent"] == {
        "intent_type": "cooldown_commit",
        "cooldown_key": "yuzuha-c2-cooldown",
        "tick": 1500,
        "previous_tick": 299,
        "enabled": True,
        "source_buff_index": "Buff-Yuzuha-Cinema2",
    }
    assert skill_node == original_skill_node
    assert "RuntimeCommandPort" not in str(result.node_outputs)
    assert "ScheduleDispatchPort" not in str(result.node_outputs)
    assert "ScheduledEventEmitter" not in str(result.node_outputs)
    assert validate_buff_graph_trace(result.trace) == ()
    assert any(event.kind is BuffGraphTraceKind.EFFECT_REQUESTED for event in result.trace.events)


def test_yuzuha_cinema2_strict_cooldown_gate_preserves_legacy_greater_than() -> None:
    registry = build_default_block_registry()
    tick = registry.get("read.current_tick").create_node(node_id="tick")
    cooldown = registry.get("condition.cooldown_ready").create_node(
        node_id="cooldown-ready",
        params={
            "cooldown_key": "yuzuha-c2-cooldown",
            "cooldown_ticks": 1200,
            "operator": ">",
        },
    )
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="yuzuha-cinema2-strict-cooldown",
        display_name="Yuzuha Cinema2 Strict Cooldown",
        owner_kind=OwnerKind.CHARACTER,
        owner_name="Yuzuha",
        source_buff_index="Buff-Yuzuha-Cinema2",
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/YuzuhaCinema2Trigger.py",
        nodes=(tick, cooldown),
        edges=(BuffGraphEdge(edge_id="edge-1", source_node_id="tick", target_node_id="cooldown-ready"),),
    )
    compiled = compile_buff_graph_spec(spec, block_registry=registry).compiled
    assert compiled is not None

    blocked = execute_compiled_buff_graph(
        compiled,
        adapters=_yuzuha_cinema2_adapters(),
        tick=1500,
        prepared_context={"tick": 1500, "state": {"yuzuha-c2-cooldown": 300}},
    )
    ready = execute_compiled_buff_graph(
        compiled,
        adapters=_yuzuha_cinema2_adapters(),
        tick=1500,
        prepared_context={"tick": 1500, "state": {"yuzuha-c2-cooldown": 299}},
    )

    assert blocked.outputs["passed"] is False
    assert blocked.outputs["elapsed"] == 1200
    assert ready.outputs["passed"] is True
    assert ready.outputs["elapsed"] == 1201


def test_pending_skill_node_signal_records_overwrite_and_missing_signal_guards() -> None:
    registry = build_default_block_registry()
    capture = registry.get("state.pending_skill_node_signal").create_node(
        node_id="capture-signal",
        params={"signal_key": "yuzuha-c2", "operation": "capture", "require_empty": True},
    )
    consume = registry.get("state.pending_skill_node_signal").create_node(
        node_id="consume-signal",
        params={"signal_key": "yuzuha-c2", "operation": "consume", "require_pending": True},
    )
    capture_spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="yuzuha-cinema2-capture-signal",
        display_name="Yuzuha Cinema2 Capture Signal",
        owner_kind=OwnerKind.CHARACTER,
        owner_name="Yuzuha",
        source_buff_index="Buff-Yuzuha-Cinema2",
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/YuzuhaCinema2Trigger.py",
        nodes=(capture,),
        edges=(),
    )
    consume_spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="yuzuha-cinema2-consume-signal",
        display_name="Yuzuha Cinema2 Consume Signal",
        owner_kind=OwnerKind.CHARACTER,
        owner_name="Yuzuha",
        source_buff_index="Buff-Yuzuha-Cinema2",
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/YuzuhaCinema2Trigger.py",
        nodes=(consume,),
        edges=(),
    )
    capture_compiled = compile_buff_graph_spec(capture_spec, block_registry=registry).compiled
    consume_compiled = compile_buff_graph_spec(consume_spec, block_registry=registry).compiled
    assert capture_compiled is not None
    assert consume_compiled is not None

    overwrite = execute_compiled_buff_graph(
        capture_compiled,
        adapters=_yuzuha_cinema2_adapters(),
        tick=1,
        prepared_context={
            "skill_node": {"skill_tag": "1411_Q"},
            "pending_skill_node_signals": {
                "yuzuha-c2": {"skill_node": {"skill_tag": "1411_E_EX_A"}},
            },
        },
    )
    missing = execute_compiled_buff_graph(
        consume_compiled,
        adapters=_yuzuha_cinema2_adapters(),
        tick=1,
        prepared_context={},
    )

    assert overwrite.outputs["passed"] is False
    assert overwrite.outputs["pending_skill_node_signal"]["error_code"] == "pending_signal_exists"
    assert missing.outputs["passed"] is False
    assert missing.outputs["pending_skill_node_signal"]["error_code"] == "missing_pending_signal"


def _yuzuha_cinema2_spec() -> BuffGraphSpec:
    registry = build_default_block_registry()
    tick = registry.get("read.current_tick").create_node(node_id="read-tick")
    enemy = registry.get("read.enemy_context").create_node(node_id="read-enemy")
    stun = registry.get("read.enemy_stun_state").create_node(node_id="read-stun")
    stun_gate = registry.get("condition.enemy_stun_active").create_node(
        node_id="stun-gate",
        params={"active": False},
    )
    skill = registry.get("read.skill_node").create_node(node_id="read-skill")
    tag = registry.get("condition.skill_tag_in").create_node(
        node_id="skill-tag",
        params={"skill_tags": ["1411_E_EX_A", "1411_E_EX_B", "1411_Q"]},
    )
    hit = registry.get("condition.hit_frame").create_node(
        node_id="hit-frame",
        params={"require_last_hit": True},
    )
    cooldown = registry.get("condition.cooldown_ready").create_node(
        node_id="cooldown-ready",
        params={
            "cooldown_key": "yuzuha-c2-cooldown",
            "cooldown_ticks": 1200,
            "operator": ">",
        },
    )
    signal = registry.get("state.pending_skill_node_signal").create_node(
        node_id="capture-signal",
        params={"signal_key": "yuzuha-c2", "operation": "capture", "require_empty": True},
    )
    force_qte = registry.get("effect.set_skill_node_force_qte_trigger").create_node(
        node_id="force-qte",
    )
    process_state = registry.get("effect.notify_schedule_process_state").create_node(
        node_id="process-state",
        params={"reason": "yuzuha-cinema2-force-qte", "report_flag": "YUZUHA_REPORT"},
    )
    commit = registry.get("state.commit_cooldown_tick").create_node(
        node_id="commit-cooldown",
        params={"cooldown_key": "yuzuha-c2-cooldown"},
    )
    return BuffGraphSpec.draft_from_xlogic(
        graph_id="yuzuha-cinema2-qte-signal-blocks",
        display_name="Yuzuha Cinema2 QTE Signal Blocks",
        owner_kind=OwnerKind.CHARACTER,
        owner_name="Yuzuha",
        source_buff_index="Buff-Yuzuha-Cinema2",
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/YuzuhaCinema2Trigger.py",
        nodes=(tick, enemy, stun, stun_gate, skill, tag, hit, cooldown, signal, force_qte, process_state, commit),
        edges=(
            BuffGraphEdge(edge_id="edge-1", source_node_id="read-enemy", target_node_id="read-stun"),
            BuffGraphEdge(edge_id="edge-2", source_node_id="read-stun", target_node_id="stun-gate"),
            BuffGraphEdge(edge_id="edge-3", source_node_id="read-skill", target_node_id="skill-tag"),
            BuffGraphEdge(edge_id="edge-4", source_node_id="read-skill", target_node_id="hit-frame"),
            BuffGraphEdge(edge_id="edge-5", source_node_id="read-tick", target_node_id="cooldown-ready"),
            BuffGraphEdge(edge_id="edge-6", source_node_id="read-skill", target_node_id="capture-signal"),
            BuffGraphEdge(edge_id="edge-7", source_node_id="capture-signal", target_node_id="force-qte"),
            BuffGraphEdge(edge_id="edge-8", source_node_id="capture-signal", target_node_id="process-state"),
            BuffGraphEdge(edge_id="edge-9", source_node_id="capture-signal", target_node_id="commit-cooldown"),
        ),
    )


def _yuzuha_cinema2_adapters() -> dict[str, object]:
    adapters: dict[str, object] = {}
    for group in (
        build_low_risk_read_adapters(),
        build_yuzuha_cinema2_qte_signal_read_adapters(),
        build_yuzuha_cinema2_qte_signal_condition_adapters(),
        build_yuzuha_cinema2_qte_signal_state_adapters(),
        build_yuzuha_cinema2_qte_signal_effect_adapters(),
    ):
        adapters.update(group)
    return adapters
