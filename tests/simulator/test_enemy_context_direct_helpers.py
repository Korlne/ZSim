from __future__ import annotations

import inspect
from types import SimpleNamespace
from typing import Any, cast

import pytest

import zsim.sim_progress.Buff.BuffXLogic.HugoCorePassiveEXStunBonus as hugo_ex_module
import zsim.sim_progress.Buff.BuffXLogic.YixuanCinema2StunTimeLimitBonus as yixuan_c2_module
import zsim.sim_progress.Buff.BuffXLogic.YixuanAdditionalAbilityDmgBonus as yixuan_module
from zsim.sim_progress.Buff.BuffXLogic.HugoCorePassiveEXStunBonus import (
    HugoCorePassiveEXStunBonus,
    HugoCorePassiveEXStunBonusRecord,
)
from zsim.sim_progress.Buff.BuffXLogic.YixuanCinema2StunTimeLimitBonus import (
    YixuanCinema2StunTimeLimitBonus,
    YixuanCinema2StunTimeLimitBonusRecord,
)
from zsim.sim_progress.Buff.BuffXLogic.YixuanAdditionalAbilityDmgBonus import (
    YixuanAdditionalAbilityDmgBonus,
    YixuanAdditionalAbilityDmgBonusRecord,
)
from zsim.sim_progress.Buff.JudgeTools.PreparationContext import (
    build_preparation_context_from_sim_instance,
)
from zsim.sim_progress.Preload import SkillNode
from zsim.sim_progress.ScheduledEvent.buff_runtime import BuffRuntimeState


class _FailFastEventList(list[object]):
    def append(self, item: object) -> None:
        raise AssertionError("enemy context helper should not write raw event_list")


class _ForbiddenLayer:
    def __init__(self, label: str) -> None:
        self.label = label

    def __getattr__(self, name: str) -> Any:
        raise AssertionError(f"{self.label} should not be touched: {name}")

    def __call__(self, *args: object, **kwargs: object) -> None:
        raise AssertionError(f"{self.label} should not be called")


class _EnemyDynamicProbe:
    def __init__(self, *, stunned: bool) -> None:
        self._stunned = stunned
        self.stun_reads = 0

    @property
    def stun(self) -> bool:
        self.stun_reads += 1
        return self._stunned


class _ScheduleDataProbe:
    def __init__(self, *, stunned: bool) -> None:
        self.enemy_dynamic = _EnemyDynamicProbe(stunned=stunned)
        self.enemy = SimpleNamespace(dynamic=self.enemy_dynamic)
        self.event_list = _FailFastEventList()
        self.change_process_calls = 0

    def change_process_state(self) -> None:
        self.change_process_calls += 1
        raise AssertionError("enemy context branch should not report-state in this slice")


class _BuffInstanceProbe:
    def __init__(self, *, sim_instance: SimpleNamespace) -> None:
        self.sim_instance = sim_instance
        self.ft = SimpleNamespace(
            index="Buff-\u89d2\u8272-\u4eea\u7384-\u7ec4\u961f\u88ab\u52a8\u589e\u4f24"
        )


def _buff_template(index: str) -> SimpleNamespace:
    return SimpleNamespace(
        ft=SimpleNamespace(index=index),
        dy=SimpleNamespace(count=0.0),
        history=SimpleNamespace(record=None),
    )


def _build_preparation_sim_instance(
    *,
    runtime_registry: dict[str, dict[str, object]],
    fallback_registry: dict[str, dict[str, object]],
) -> SimpleNamespace:
    runtime_state = BuffRuntimeState(
        template_registry=runtime_registry,
        pending_queue={},
        active_store={},
        enemy_mirror=[],
    )
    return SimpleNamespace(
        buff_runtime_state=runtime_state,
        char_data=SimpleNamespace(char_obj_list=[]),
        init_data=SimpleNamespace(Judge_list_set=[]),
        schedule_data=SimpleNamespace(enemy=object(), event_list=[]),
        load_data=SimpleNamespace(
            exist_buff_dict=fallback_registry,
            action_stack=object(),
        ),
        preload=SimpleNamespace(preload_data=object()),
        global_stats=SimpleNamespace(DYNAMIC_BUFF_DICT={}),
    )


def test_build_preparation_context_uses_runtime_template_registry_owner() -> None:
    runtime_buff = _buff_template("Runtime-Buff-Template")
    fallback_buff = _buff_template("Fallback-Buff-Template")
    runtime_registry = {"runtime-owner": {"runtime-buff": runtime_buff}}
    fallback_registry = {"fallback-owner": {"fallback-buff": fallback_buff}}
    sim_instance = _build_preparation_sim_instance(
        runtime_registry=runtime_registry,
        fallback_registry=fallback_registry,
    )

    context = build_preparation_context_from_sim_instance(sim_instance)

    assert context.find_sub_exist_buff_dict("runtime-owner") is runtime_registry[
        "runtime-owner"
    ]
    assert context.find_trigger_buff("runtime-owner", "Template") is runtime_buff
    runtime_late_buff = _buff_template("Runtime-Buff-Late")
    runtime_registry["runtime-owner"]["runtime-late-buff"] = runtime_late_buff
    assert (
        context.find_sub_exist_buff_dict("runtime-owner")["runtime-late-buff"]
        is runtime_late_buff
    )
    with pytest.raises(KeyError):
        context.find_sub_exist_buff_dict("fallback-owner")


def test_build_preparation_context_falls_back_for_runtime_state_without_registry_owner() -> None:
    fallback_buff = _buff_template("Fallback-Buff-Template")
    fallback_registry = {"fallback-owner": {"fallback-buff": fallback_buff}}
    sim_instance = _build_preparation_sim_instance(
        runtime_registry={"runtime-owner": {"runtime-buff": object()}},
        fallback_registry=fallback_registry,
    )
    sim_instance.buff_runtime_state = SimpleNamespace(create_read_port=lambda: object())

    context = build_preparation_context_from_sim_instance(sim_instance)

    assert context.find_sub_exist_buff_dict("fallback-owner") is fallback_registry[
        "fallback-owner"
    ]
    assert context.find_trigger_buff("fallback-owner", "Template") is fallback_buff


def test_build_preparation_context_keeps_template_registry_run_scoped() -> None:
    first_buff = _buff_template("Runtime-One-Template")
    second_buff = _buff_template("Runtime-Two-Template")
    first_registry = {"same-owner": {"same-key": first_buff}}
    second_registry = {"same-owner": {"same-key": second_buff}}

    first_context = build_preparation_context_from_sim_instance(
        _build_preparation_sim_instance(
            runtime_registry=first_registry,
            fallback_registry={"fallback": {}},
        )
    )
    second_context = build_preparation_context_from_sim_instance(
        _build_preparation_sim_instance(
            runtime_registry=second_registry,
            fallback_registry={"fallback": {}},
        )
    )

    assert first_context.find_sub_exist_buff_dict("same-owner") is first_registry[
        "same-owner"
    ]
    assert second_context.find_sub_exist_buff_dict("same-owner") is second_registry[
        "same-owner"
    ]
    assert first_context.find_trigger_buff("same-owner", "One-Template") is first_buff
    assert second_context.find_trigger_buff("same-owner", "Two-Template") is second_buff
    second_registry["same-owner"]["second-only"] = _buff_template(
        "Runtime-Two-Second"
    )
    assert "second-only" not in first_context.find_sub_exist_buff_dict("same-owner")
    assert "second-only" in second_context.find_sub_exist_buff_dict("same-owner")


def _build_yixuan_trigger_harness(
    *,
    stunned: bool,
    tick: int = 720,
) -> SimpleNamespace:
    schedule_data = _ScheduleDataProbe(stunned=stunned)
    sim_instance = SimpleNamespace(
        tick=tick,
        schedule_data=schedule_data,
        listener_manager=_ForbiddenLayer("listener broadcast"),
        runtime_command_port=_ForbiddenLayer("RuntimeCommandPort"),
        legacy_runtime_facade=_ForbiddenLayer("LegacyBuffRuntimeFacade"),
        buff_runtime_read_port=_ForbiddenLayer("BuffRuntimeReadPort"),
    )
    buff_instance = _BuffInstanceProbe(sim_instance=sim_instance)
    trigger = YixuanAdditionalAbilityDmgBonus(buff_instance)

    record = YixuanAdditionalAbilityDmgBonusRecord()
    record.char = SimpleNamespace(NAME="\u4eea\u7384", CID=1371)
    trigger.buff_0 = SimpleNamespace(history=SimpleNamespace(record=record))

    prepared_calls: list[dict[str, object]] = []

    def record_prepared_call(**kwargs: object) -> None:
        prepared_calls.append(kwargs)

    trigger_any: Any = trigger
    trigger_any.get_prepared = record_prepared_call

    return SimpleNamespace(
        trigger=trigger,
        sim_instance=sim_instance,
        schedule_data=schedule_data,
        record=record,
        prepared_calls=prepared_calls,
    )


def _build_yixuan_cinema2_harness(
    *,
    stunned: bool,
    tick: int = 720,
) -> SimpleNamespace:
    schedule_data = _ScheduleDataProbe(stunned=stunned)
    sim_instance = SimpleNamespace(
        tick=tick,
        schedule_data=schedule_data,
        listener_manager=_ForbiddenLayer("listener broadcast"),
        runtime_command_port=_ForbiddenLayer("RuntimeCommandPort"),
        legacy_runtime_facade=_ForbiddenLayer("LegacyBuffRuntimeFacade"),
        buff_runtime_read_port=_ForbiddenLayer("BuffRuntimeReadPort"),
    )
    buff_instance = _BuffInstanceProbe(sim_instance=sim_instance)
    trigger = YixuanCinema2StunTimeLimitBonus(buff_instance)

    record = YixuanCinema2StunTimeLimitBonusRecord()
    record.char = SimpleNamespace(NAME="\u4eea\u7384", CID=1371)
    record.enemy = schedule_data.enemy
    trigger.buff_0 = SimpleNamespace(history=SimpleNamespace(record=record))

    prepared_calls: list[dict[str, object]] = []

    def record_prepared_call(**kwargs: object) -> None:
        prepared_calls.append(kwargs)

    trigger_any: Any = trigger
    trigger_any.get_prepared = record_prepared_call

    return SimpleNamespace(
        trigger=trigger,
        sim_instance=sim_instance,
        schedule_data=schedule_data,
        record=record,
        prepared_calls=prepared_calls,
    )


def _matching_yixuan_skill_node(*, preload_tick: int = 719) -> SimpleNamespace:
    return SimpleNamespace(
        skill_tag="1371_E_EX_B_1",
        preload_tick=preload_tick,
        skill=SimpleNamespace(skill_text="\u51dd\u4e91\u672f"),
    )


def _matching_yixuan_cinema2_skill_node(
    *,
    preload_tick: int = 720,
    skill_tag: str = "1371_Q",
) -> SimpleNamespace:
    return SimpleNamespace(
        skill_tag=skill_tag,
        preload_tick=preload_tick,
        skill=SimpleNamespace(skill_text="\u5587\u54cd\u503c\u5927\u62db"),
    )


def _matching_hugo_ex_skill_node(
    *,
    trigger_buff_level: int = 2,
    skill_tag: str = "1291_E_EX_A",
) -> SkillNode:
    skill = SimpleNamespace(
        skill_tag=skill_tag,
        char_name="雨果",
        hit_times=1,
        labels=None,
        ticks=1,
        tick_list=[],
        trigger_buff_level=trigger_buff_level,
    )
    return SkillNode(skill=skill, preload_tick=720)


def _build_hugo_ex_harness(
    monkeypatch: pytest.MonkeyPatch,
    *,
    stunned: bool,
) -> SimpleNamespace:
    enemy_dynamic = _EnemyDynamicProbe(stunned=stunned)
    enemy = SimpleNamespace(dynamic=enemy_dynamic)
    sim_instance = SimpleNamespace(
        listener_manager=_ForbiddenLayer("listener broadcast"),
        runtime_command_port=_ForbiddenLayer("RuntimeCommandPort"),
        legacy_runtime_facade=_ForbiddenLayer("LegacyBuffRuntimeFacade"),
        buff_runtime_read_port=_ForbiddenLayer("BuffRuntimeReadPort"),
    )
    buff_index = "Buff-角色-雨果-核心被动-强化特殊技失衡值"
    buff_instance = SimpleNamespace(
        ft=SimpleNamespace(index=buff_index),
        sim_instance=sim_instance,
    )
    record = HugoCorePassiveEXStunBonusRecord()
    buff_0 = SimpleNamespace(history=SimpleNamespace(record=record))
    preparation_calls: list[dict[str, object]] = []

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        assert sim_instance is buff_instance.sim_instance
        return {"雨果": {buff_index: buff_0}}

    def fake_check_preparation(
        *,
        buff_instance: object,
        buff_0: object,
        **kwargs: object,
    ) -> None:
        preparation_calls.append(dict(kwargs))
        prepared_record = cast(Any, cast(Any, buff_0).history.record)
        if kwargs.get("enemy"):
            prepared_record.enemy = enemy
        if kwargs.get("char_CID"):
            prepared_record.char = SimpleNamespace(CID=kwargs["char_CID"], NAME="雨果")

    monkeypatch.setattr(
        hugo_ex_module.JudgeTools,
        "find_exist_buff_dict",
        fake_find_exist_buff_dict,
    )
    monkeypatch.setattr(hugo_ex_module, "check_preparation", fake_check_preparation)

    logic = HugoCorePassiveEXStunBonus(cast(Any, buff_instance))
    return SimpleNamespace(
        logic=logic,
        record=record,
        enemy_dynamic=enemy_dynamic,
        preparation_calls=preparation_calls,
    )


def _block_legacy_buff_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_find_exist_buff_dict(**kwargs: object) -> object:
        raise AssertionError("enemy context test should not query old Buff containers")

    for module in (yixuan_module, yixuan_c2_module):
        monkeypatch.setattr(
            module.JudgeTools,
            "find_exist_buff_dict",
            fail_find_exist_buff_dict,
        )


def test_yixuan_enemy_context_stun_branch_returns_true_without_runtime_writes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _block_legacy_buff_lookup(monkeypatch)
    harness = _build_yixuan_trigger_harness(stunned=True)

    result = harness.trigger.special_judge_logic(
        skill_node=_matching_yixuan_skill_node(
            preload_tick=harness.sim_instance.tick - 1,
        )
    )

    assert result is True
    assert harness.prepared_calls == [{"char_CID": 1371}]
    assert harness.schedule_data.enemy_dynamic.stun_reads == 1
    assert harness.schedule_data.change_process_calls == 0
    assert harness.schedule_data.event_list == []
    assert harness.trigger.record is harness.record


def test_yixuan_enemy_context_no_stun_blocks_without_runtime_writes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _block_legacy_buff_lookup(monkeypatch)
    harness = _build_yixuan_trigger_harness(stunned=False)

    result = harness.trigger.special_judge_logic(
        skill_node=_matching_yixuan_skill_node(
            preload_tick=harness.sim_instance.tick - 1,
        )
    )

    assert result is False
    assert harness.prepared_calls == [{"char_CID": 1371}]
    assert harness.schedule_data.enemy_dynamic.stun_reads == 1
    assert harness.schedule_data.change_process_calls == 0
    assert harness.schedule_data.event_list == []


def test_yixuan_enemy_context_missing_skill_node_skips_stun_helper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _block_legacy_buff_lookup(monkeypatch)
    harness = _build_yixuan_trigger_harness(stunned=True)

    result = harness.trigger.special_judge_logic()

    assert result is False
    assert harness.prepared_calls == [{"char_CID": 1371}]
    assert harness.schedule_data.enemy_dynamic.stun_reads == 0
    assert harness.schedule_data.change_process_calls == 0
    assert harness.schedule_data.event_list == []


def test_yixuan_enemy_context_wrong_tag_still_checks_stun_before_tag_gate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _block_legacy_buff_lookup(monkeypatch)
    harness = _build_yixuan_trigger_harness(stunned=True)
    skill_node = _matching_yixuan_skill_node(
        preload_tick=harness.sim_instance.tick - 1
    )
    skill_node.skill_tag = "1371_Q"

    result = harness.trigger.special_judge_logic(skill_node=skill_node)

    assert result is False
    assert harness.prepared_calls == [{"char_CID": 1371}]
    assert harness.schedule_data.enemy_dynamic.stun_reads == 1
    assert harness.schedule_data.change_process_calls == 0
    assert harness.schedule_data.event_list == []


def test_yixuan_cinema2_stun_branch_returns_true_without_runtime_writes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _block_legacy_buff_lookup(monkeypatch)
    harness = _build_yixuan_cinema2_harness(stunned=True)

    result = harness.trigger.special_judge_logic(
        skill_node=_matching_yixuan_cinema2_skill_node(
            preload_tick=harness.sim_instance.tick,
        )
    )

    assert result is True
    assert harness.prepared_calls == [{"char_CID": 1371, "enemy": 1}]
    assert harness.schedule_data.enemy_dynamic.stun_reads == 1
    assert harness.schedule_data.change_process_calls == 0
    assert harness.schedule_data.event_list == []
    assert harness.trigger.record is harness.record


def test_yixuan_cinema2_no_stun_blocks_after_required_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _block_legacy_buff_lookup(monkeypatch)
    harness = _build_yixuan_cinema2_harness(stunned=False)

    result = harness.trigger.special_judge_logic(
        skill_node=_matching_yixuan_cinema2_skill_node(
            preload_tick=harness.sim_instance.tick,
        )
    )

    assert result is False
    assert harness.prepared_calls == [{"char_CID": 1371, "enemy": 1}]
    assert harness.schedule_data.enemy_dynamic.stun_reads == 1
    assert harness.schedule_data.change_process_calls == 0
    assert harness.schedule_data.event_list == []


def test_yixuan_cinema2_missing_skill_node_skips_stun_helper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _block_legacy_buff_lookup(monkeypatch)
    harness = _build_yixuan_cinema2_harness(stunned=True)

    result = harness.trigger.special_judge_logic()

    assert result is False
    assert harness.prepared_calls == [{"char_CID": 1371, "enemy": 1}]
    assert harness.schedule_data.enemy_dynamic.stun_reads == 0
    assert harness.schedule_data.change_process_calls == 0
    assert harness.schedule_data.event_list == []


def test_yixuan_cinema2_wrong_tag_skips_stun_helper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _block_legacy_buff_lookup(monkeypatch)
    harness = _build_yixuan_cinema2_harness(stunned=True)

    result = harness.trigger.special_judge_logic(
        skill_node=_matching_yixuan_cinema2_skill_node(
            preload_tick=harness.sim_instance.tick,
            skill_tag="1371_E_EX_B_1",
        )
    )

    assert result is False
    assert harness.prepared_calls == [{"char_CID": 1371, "enemy": 1}]
    assert harness.schedule_data.enemy_dynamic.stun_reads == 0
    assert harness.schedule_data.change_process_calls == 0
    assert harness.schedule_data.event_list == []


def test_yixuan_cinema2_preload_mismatch_blocks_after_stun_helper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _block_legacy_buff_lookup(monkeypatch)
    harness = _build_yixuan_cinema2_harness(stunned=True)

    result = harness.trigger.special_judge_logic(
        skill_node=_matching_yixuan_cinema2_skill_node(
            preload_tick=harness.sim_instance.tick - 1,
        )
    )

    assert result is False
    assert harness.prepared_calls == [{"char_CID": 1371, "enemy": 1}]
    assert harness.schedule_data.enemy_dynamic.stun_reads == 1
    assert harness.schedule_data.change_process_calls == 0
    assert harness.schedule_data.event_list == []


@pytest.mark.parametrize(
    ("stunned", "expected"),
    (
        (False, True),
        (True, False),
    ),
)
def test_yixuan_cinema2_exit_preserves_inverse_stun_behavior(
    monkeypatch: pytest.MonkeyPatch,
    *,
    stunned: bool,
    expected: bool,
) -> None:
    _block_legacy_buff_lookup(monkeypatch)
    harness = _build_yixuan_cinema2_harness(stunned=stunned)

    result = harness.trigger.special_exit_logic()

    assert result is expected
    assert harness.prepared_calls == [{"char_CID": 1371, "enemy": 1}]
    assert harness.schedule_data.enemy_dynamic.stun_reads == 1
    assert harness.schedule_data.change_process_calls == 0
    assert harness.schedule_data.event_list == []


@pytest.mark.parametrize(
    ("stunned", "expected"),
    (
        (False, True),
        (True, False),
    ),
)
def test_hugo_ex_stun_gate_uses_enemy_state_port(
    monkeypatch: pytest.MonkeyPatch,
    *,
    stunned: bool,
    expected: bool,
) -> None:
    harness = _build_hugo_ex_harness(monkeypatch, stunned=stunned)

    result = harness.logic.special_judge_logic(skill_node=_matching_hugo_ex_skill_node())

    assert result is expected
    assert harness.preparation_calls == [{"char_CID": 1291, "enemy": 1}]
    assert harness.enemy_dynamic.stun_reads == 1
    assert harness.logic.record is harness.record


def test_hugo_ex_wrong_trigger_level_skips_enemy_state_port(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _build_hugo_ex_harness(monkeypatch, stunned=True)

    result = harness.logic.special_judge_logic(
        skill_node=_matching_hugo_ex_skill_node(trigger_buff_level=1)
    )

    assert result is False
    assert harness.preparation_calls == [{"char_CID": 1291, "enemy": 1}]
    assert harness.enemy_dynamic.stun_reads == 0


def test_yixuan_enemy_context_source_stays_out_of_dispatch_runtime_and_formula_boundaries(
) -> None:
    judge_source = inspect.getsource(
        yixuan_module.YixuanAdditionalAbilityDmgBonus.special_judge_logic
    )
    c2_judge_source = inspect.getsource(
        yixuan_c2_module.YixuanCinema2StunTimeLimitBonus.special_judge_logic
    )
    c2_exit_source = inspect.getsource(
        yixuan_c2_module.YixuanCinema2StunTimeLimitBonus.special_exit_logic
    )
    hugo_ex_source = inspect.getsource(
        hugo_ex_module.HugoCorePassiveEXStunBonus.special_judge_logic
    )

    assert "schedule_data.enemy" in judge_source
    assert "read_enemy_stun_active(enemy)" in judge_source
    assert "enemy.dynamic.stun" not in judge_source
    assert "skill_node.preload_tick == self.buff_instance.sim_instance.tick" in judge_source
    assert "change_process_state()" in judge_source
    assert judge_source.index("skill_node is None") < judge_source.index(
        "read_enemy_stun_active(enemy)"
    )
    assert judge_source.index("read_enemy_stun_active(enemy)") < judge_source.index(
        '"1371_E_EX_B_"'
    )
    assert "read_enemy_stun_active(self.record.enemy)" in c2_judge_source
    assert "read_enemy_stun_active(self.record.enemy)" in c2_exit_source
    assert "EnemyStateReadPort(self.record.enemy).stun_active()" in hugo_ex_source
    assert "record.enemy.dynamic.stun" not in hugo_ex_source
    assert c2_judge_source.index("skill_node is None") < c2_judge_source.index(
        "read_enemy_stun_active(self.record.enemy)"
    )
    assert c2_judge_source.index(
        "skill_node.skill_tag != self.record.required_skill_tag"
    ) < c2_judge_source.index("read_enemy_stun_active(self.record.enemy)")

    for forbidden_term in (
        "find_exist_buff_dict",
        "find_event_list",
        "create_schedule_dispatch_port",
        "publish_scheduled",
        "ScheduleDispatchPort",
        "RuntimeCommandPort",
        "LegacyBuffRuntimeFacade",
        "BuffRuntimeReadPort",
        "listener_manager",
        "event_list.append",
        "buff_add(",
        "KickOutBuff",
        "CalAnomaly",
        "anomaly_bars_dict",
        "dot_runtime",
    ):
        assert forbidden_term not in judge_source
        assert forbidden_term not in c2_judge_source
        assert forbidden_term not in c2_exit_source
        assert forbidden_term not in hugo_ex_source
