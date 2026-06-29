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


class _FakeCordisPreparationContext:
    def __init__(
        self,
        *,
        owner: str,
        templates: dict[str, object],
        calls: list[tuple[str, object]],
    ) -> None:
        self._owner = owner
        self._templates = templates
        self._calls = calls

    def find_equipper(self, item_name: str) -> str:
        self._calls.append(("find_equipper", item_name))
        return self._owner

    def find_sub_exist_buff_dict(self, owner_name: str) -> dict[str, object]:
        self._calls.append(("find_sub_exist_buff_dict", owner_name))
        return self._templates


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
    context_build_calls: list[object] = []
    context_calls: list[tuple[str, object]] = []
    templates = {
        crit.buff_instance.ft.index: crit_buff_0,
        ele.buff_instance.ft.index: ele_buff_0,
    }

    def fake_build_preparation_context_from_buff(
        buff_instance: object,
    ) -> _FakeCordisPreparationContext:
        context_build_calls.append(buff_instance)
        return _FakeCordisPreparationContext(
            owner=owner,
            templates=templates,
            calls=context_calls,
        )

    monkeypatch.setattr(
        crit_module,
        "build_preparation_context_from_buff",
        fake_build_preparation_context_from_buff,
    )
    monkeypatch.setattr(
        ele_module,
        "build_preparation_context_from_buff",
        fake_build_preparation_context_from_buff,
    )

    crit.logic.check_record_module()
    ele.logic.check_record_module()

    assert context_build_calls == [crit.buff_instance, ele.buff_instance]
    assert context_calls == [
        ("find_equipper", "机巧心种"),
        ("find_sub_exist_buff_dict", owner),
        ("find_equipper", "机巧心种"),
        ("find_sub_exist_buff_dict", owner),
    ]
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

    assert context_build_calls == [crit.buff_instance, ele.buff_instance]
    assert context_calls == [
        ("find_equipper", "机巧心种"),
        ("find_sub_exist_buff_dict", owner),
        ("find_equipper", "机巧心种"),
        ("find_sub_exist_buff_dict", owner),
    ]
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
    context_build_calls: list[object] = []
    context_calls: list[tuple[str, object]] = []
    templates = {harness.buff_instance.ft.index: ele_buff_0}
    preparation_calls: list[dict[str, object]] = []

    def fake_build_preparation_context_from_buff(
        buff_instance: object,
    ) -> _FakeCordisPreparationContext:
        context_build_calls.append(buff_instance)
        return _FakeCordisPreparationContext(
            owner=owner,
            templates=templates,
            calls=context_calls,
        )

    def fake_check_preparation(
        *,
        buff_instance: object,
        buff_0: object,
        preparation_context: object,
        **kwargs: object,
    ) -> None:
        assert buff_instance is harness.buff_instance
        assert buff_0 is ele_buff_0
        preparation_calls.append({"preparation_context": preparation_context, **kwargs})
        record = cast(Any, ele_buff_0.history.record)
        record.equipper = owner
        record.char = SimpleNamespace(NAME=owner)

    monkeypatch.setattr(
        ele_module,
        "build_preparation_context_from_buff",
        fake_build_preparation_context_from_buff,
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
    assert context_build_calls == [harness.buff_instance, harness.buff_instance]
    assert context_calls == [
        ("find_equipper", "机巧心种"),
        ("find_sub_exist_buff_dict", owner),
    ]
    assert len(preparation_calls) == 1
    assert isinstance(
        preparation_calls[0]["preparation_context"],
        _FakeCordisPreparationContext,
    )
    assert preparation_calls[0]["equipper"] == "机巧心种"
    assert harness.logic.buff_0 is ele_buff_0
    assert harness.logic.record is ele_buff_0.history.record
