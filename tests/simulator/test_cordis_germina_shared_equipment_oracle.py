from types import SimpleNamespace
from typing import Any, cast

import pytest

import zsim.sim_progress.Buff.BuffXLogic.CordisGerminaCritRateBonus as crit_module
import zsim.sim_progress.Buff.BuffXLogic.CordisGerminaEleDmgBonus as ele_module
from zsim.sim_progress.Preload import SkillNode


def _buff_0() -> SimpleNamespace:
    return SimpleNamespace(history=SimpleNamespace(record=None))


def _logic_harness(logic_cls: type[object], *, index: str, tick: int = 120) -> SimpleNamespace:
    sim_instance = SimpleNamespace(tick=tick)
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index=index),
    )
    logic = logic_cls(cast(Any, buff_instance))
    return SimpleNamespace(
        logic=logic,
        buff_instance=buff_instance,
        sim_instance=sim_instance,
    )


def _skill_node(
    *,
    char_name: str,
    trigger_buff_level: int,
    tick: int,
    hits_now: bool,
) -> SkillNode:
    node = SkillNode.__new__(SkillNode)
    node.char_name = char_name
    node.skill = SimpleNamespace(trigger_buff_level=trigger_buff_level)
    node.tick_list = [tick - 0.5] if hits_now else [tick - 2.0]
    return node


def test_cordis_germina_shared_owner_keeps_distinct_templates_and_records(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    owner = "仪玄"
    crit = _logic_harness(
        crit_module.CordisGerminaCritRateBonus,
        index="cordis-crit-rate-index",
    )
    ele = _logic_harness(
        ele_module.CordisGerminaEleDmgBonus,
        index="cordis-ele-dmg-index",
    )
    crit_buff_0 = _buff_0()
    ele_buff_0 = _buff_0()
    find_equipper_calls: list[tuple[str, object]] = []
    find_exist_calls: list[object] = []

    def fake_find_equipper(item_name: str, *, sim_instance: object) -> str:
        find_equipper_calls.append((item_name, sim_instance))
        return owner

    def fake_find_exist_buff_dict(
        *, sim_instance: object
    ) -> dict[str, dict[str, object]]:
        find_exist_calls.append(sim_instance)
        return {
            owner: {
                crit.buff_instance.ft.index: crit_buff_0,
                ele.buff_instance.ft.index: ele_buff_0,
            }
        }

    monkeypatch.setattr(
        crit_module.JudgeTools,
        "find_equipper",
        fake_find_equipper,
    )
    monkeypatch.setattr(
        crit_module.JudgeTools,
        "find_exist_buff_dict",
        fake_find_exist_buff_dict,
    )

    crit.logic.check_record_module()
    ele.logic.check_record_module()

    assert find_equipper_calls == [
        ("机巧心种", crit.sim_instance),
        ("机巧心种", ele.sim_instance),
    ]
    assert find_exist_calls == [crit.sim_instance, ele.sim_instance]
    assert crit.logic.equipper == owner
    assert ele.logic.equipper == owner
    assert crit.logic.buff_0 is crit_buff_0
    assert ele.logic.buff_0 is ele_buff_0
    assert crit.logic.record is crit_buff_0.history.record
    assert ele.logic.record is ele_buff_0.history.record
    assert crit.logic.record is not ele.logic.record
    assert isinstance(crit.logic.record, crit_module.CordisGerminaCritRateBonusRecord)
    assert isinstance(ele.logic.record, ele_module.CordisGerminaEleDmgBonusRecord)

    crit_existing_record = crit.logic.record
    ele_existing_record = ele.logic.record
    crit.logic.check_record_module()
    ele.logic.check_record_module()

    assert find_equipper_calls == [
        ("机巧心种", crit.sim_instance),
        ("机巧心种", ele.sim_instance),
    ]
    assert find_exist_calls == [crit.sim_instance, ele.sim_instance]
    assert crit.logic.record is crit_existing_record
    assert ele.logic.record is ele_existing_record


@pytest.mark.parametrize(
    ("char_name", "trigger_buff_level", "hits_now", "expected"),
    [
        ("仪玄", 0, True, True),
        ("仪玄", 2, True, True),
        ("青衣", 0, True, False),
        ("仪玄", 1, True, False),
        ("仪玄", 0, False, False),
    ],
)
def test_cordis_germina_ele_dmg_skill_node_timing_oracle(
    monkeypatch: pytest.MonkeyPatch,
    char_name: str,
    trigger_buff_level: int,
    hits_now: bool,
    expected: bool,
) -> None:
    owner = "仪玄"
    harness = _logic_harness(
        ele_module.CordisGerminaEleDmgBonus,
        index="cordis-ele-dmg-index",
        tick=120,
    )
    ele_buff_0 = _buff_0()
    preparation_calls: list[dict[str, object]] = []

    def fake_find_equipper(item_name: str, *, sim_instance: object) -> str:
        assert item_name == "机巧心种"
        assert sim_instance is harness.sim_instance
        return owner

    def fake_find_exist_buff_dict(
        *, sim_instance: object
    ) -> dict[str, dict[str, object]]:
        assert sim_instance is harness.sim_instance
        return {owner: {harness.buff_instance.ft.index: ele_buff_0}}

    def fake_check_preparation(
        *,
        buff_instance: object,
        buff_0: object,
        **kwargs: object,
    ) -> None:
        assert buff_instance is harness.buff_instance
        assert buff_0 is ele_buff_0
        preparation_calls.append(dict(kwargs))
        record = cast(Any, ele_buff_0.history.record)
        record.equipper = owner
        record.char = SimpleNamespace(NAME=owner)

    monkeypatch.setattr(
        ele_module.JudgeTools,
        "find_equipper",
        fake_find_equipper,
    )
    monkeypatch.setattr(
        ele_module.JudgeTools,
        "find_exist_buff_dict",
        fake_find_exist_buff_dict,
    )
    monkeypatch.setattr(
        ele_module,
        "check_preparation",
        fake_check_preparation,
    )

    result = harness.logic.special_judge_logic(
        skill_node=_skill_node(
            char_name=char_name,
            trigger_buff_level=trigger_buff_level,
            tick=harness.sim_instance.tick,
            hits_now=hits_now,
        )
    )

    assert result is expected
    assert preparation_calls == [{"equipper": "机巧心种"}]
    assert harness.logic.buff_0 is ele_buff_0
    assert harness.logic.record is ele_buff_0.history.record
