import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from zsim.api_src.models.buff_graph import BuffGraphSpecModel
from zsim.sim_progress.Buff.BuffXLogic import YuzuhaCinema2Trigger as legacy_module
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


ROOT = Path(__file__).parents[2]
SPEC_PATH = (
    ROOT
    / "zsim"
    / "sim_progress"
    / "BuffGraph"
    / "generated_specs"
    / "yuzuha-cinema2-qte-signal-cases"
    / "yuzuha-cinema2-trigger.buffgraph.json"
)


def test_yuzuha_cinema2_graph_intents_match_legacy_happy_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(legacy_module, "YUZUHA_REPORT", True)
    legacy = _run_legacy_case(
        skill_tag="1411_E_EX_A",
        enemy_stunned=False,
        last_update_tick=299,
        last_hit=True,
    )
    graph = _run_graph_case(
        skill_tag="1411_E_EX_A",
        enemy_stunned=False,
        last_update_tick=299,
        last_hit=True,
        report_enabled=True,
    )

    assert legacy["judge_result"] is True
    assert legacy["skill_node"].force_qte_trigger is True
    assert legacy["schedule_change_process_calls"] == 1
    assert legacy["last_update_tick"] == 1500
    assert legacy["pending_after_hit"] is None
    assert legacy["prepared_calls"] == [{"char_CID": 1411, "enemy": 1}, {"char_CID": 1411}]

    mutation_intent = graph.node_outputs["effect-set-force-qte-trigger"][
        "skill_node_mutation_intent"
    ]
    process_intent = graph.node_outputs["effect-notify-process-state"][
        "process_state_notification_intent"
    ]
    cooldown_intent = graph.outputs["cooldown_commit_intent"]

    assert graph.node_outputs["condition-enemy-not-stunned"]["passed"] is True
    assert graph.node_outputs["condition-skill-tag-in"]["passed"] is True
    assert graph.node_outputs["condition-hit-frame"]["passed"] is True
    assert graph.node_outputs["condition-cooldown-ready"]["passed"] is True
    assert mutation_intent["mutation"] == "set_force_qte_trigger"
    assert mutation_intent["field"] == "force_qte_trigger"
    assert mutation_intent["value"] is True
    assert mutation_intent["enabled"] is True
    assert mutation_intent["skill_node"]["skill_tag"] == legacy["skill_node"].skill_tag
    assert process_intent["action"] == "change_process_state"
    assert process_intent["enabled"] is True
    assert cooldown_intent == {
        "intent_type": "cooldown_commit",
        "cooldown_key": "yuzuha-cinema2-trigger",
        "tick": 1500,
        "previous_tick": 299,
        "enabled": True,
        "source_buff_index": "Buff-角色-柚叶-2画-连携技触发器",
    }


@pytest.mark.parametrize(
    (
        "skill_tag",
        "enemy_stunned",
        "last_update_tick",
        "last_hit",
        "failed_graph_gate",
    ),
    [
        ("1411_E_EX_A", True, None, True, "condition-enemy-not-stunned"),
        ("1411_OTHER", False, None, True, "condition-skill-tag-in"),
        ("1411_E_EX_A", False, 300, True, "condition-cooldown-ready"),
        ("1411_E_EX_A", False, None, False, "condition-hit-frame"),
    ],
)
def test_yuzuha_cinema2_graph_gate_checkpoints_match_legacy_rejections(
    skill_tag: str,
    enemy_stunned: bool,
    last_update_tick: int | None,
    last_hit: bool,
    failed_graph_gate: str,
) -> None:
    legacy = _run_legacy_case(
        skill_tag=skill_tag,
        enemy_stunned=enemy_stunned,
        last_update_tick=last_update_tick,
        last_hit=last_hit,
        run_hit=False,
    )
    graph = _run_graph_case(
        skill_tag=skill_tag,
        enemy_stunned=enemy_stunned,
        last_update_tick=last_update_tick,
        last_hit=last_hit,
        report_enabled=True,
    )

    assert legacy["judge_result"] is False
    assert graph.node_outputs[failed_graph_gate]["passed"] is False


def _run_legacy_case(
    *,
    skill_tag: str,
    enemy_stunned: bool,
    last_update_tick: int | None,
    last_hit: bool,
    run_hit: bool = True,
) -> dict[str, object]:
    schedule_data = _ScheduleProbe()
    buff_instance = SimpleNamespace(
        sim_instance=SimpleNamespace(tick=1500, schedule_data=schedule_data),
        ft=SimpleNamespace(index="Buff-角色-柚叶-2画-连携技触发器"),
    )
    trigger = legacy_module.YuzuhaCinema2Trigger(buff_instance)
    record = legacy_module.YuzuhaCinema2TriggerRecord()
    record.enemy = SimpleNamespace(dynamic=SimpleNamespace(stun=enemy_stunned))
    record.last_update_tick = last_update_tick
    trigger.record = record
    prepared_calls: list[dict[str, object]] = []
    trigger.check_record_module = lambda: None
    trigger.get_prepared = lambda **kwargs: prepared_calls.append(kwargs)
    skill_node = _SkillNodeProbe(skill_tag=skill_tag, last_hit=last_hit)

    judge_result = trigger.special_judge_logic(skill_node=skill_node)
    if judge_result and run_hit:
        trigger.special_hit_logic()

    return {
        "judge_result": judge_result,
        "skill_node": skill_node,
        "schedule_change_process_calls": schedule_data.change_process_calls,
        "last_update_tick": record.last_update_tick,
        "pending_after_hit": record.skill_node_be_changed,
        "prepared_calls": prepared_calls,
    }


def _run_graph_case(
    *,
    skill_tag: str,
    enemy_stunned: bool,
    last_update_tick: int | None,
    last_hit: bool,
    report_enabled: bool,
):
    spec_payload = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    spec = BuffGraphSpecModel.model_validate(spec_payload["spec"]).to_domain()
    compiled = compile_buff_graph_spec(spec, block_registry=build_default_block_registry()).compiled
    assert compiled is not None
    state = {}
    if last_update_tick is not None:
        state["yuzuha-cinema2-trigger"] = last_update_tick
    return execute_compiled_buff_graph(
        compiled,
        adapters=_graph_adapters(),
        tick=1500,
        prepared_context={
            "tick": 1500,
            "source_buff_index": "Buff-角色-柚叶-2画-连携技触发器",
            "enemy_context": {"dynamic": {"stun": enemy_stunned}},
            "skill_node": {
                "skill_tag": skill_tag,
                "hit_index": 1,
                "is_last_hit": last_hit,
                "force_qte_trigger": False,
            },
            "state": state,
            "YUZUHA_REPORT": report_enabled,
        },
    )


def _graph_adapters() -> dict[str, object]:
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


class _ScheduleProbe:
    def __init__(self) -> None:
        self.change_process_calls = 0
        self.event_list: list[object] = []

    def change_process_state(self) -> None:
        self.change_process_calls += 1


class _SkillNodeProbe:
    def __init__(self, *, skill_tag: str, last_hit: bool) -> None:
        self.skill_tag = skill_tag
        self._last_hit = last_hit
        self.force_qte_trigger = False
        self.last_hit_ticks: list[int] = []

    def is_last_hit(self, *, tick: int) -> bool:
        self.last_hit_ticks.append(tick)
        return self._last_hit
