from types import SimpleNamespace
from typing import Any, cast

import pytest

import zsim.sim_progress.Buff.BuffXLogic.ElegantVanityDmgBonus as elegant_module
from zsim.sim_progress.Preload import SkillNode


def _buff_0() -> SimpleNamespace:
    return SimpleNamespace(history=SimpleNamespace(record=None))


def _logic_harness(*, index: str = "elegant-template-index", tick: int = 120) -> SimpleNamespace:
    sim_instance = SimpleNamespace(tick=tick)
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index=index),
    )
    logic = elegant_module.ElegantVanityDmgBonus(cast(Any, buff_instance))
    return SimpleNamespace(
        logic=logic,
        buff_instance=buff_instance,
        sim_instance=sim_instance,
    )


def _skill_node(
    *,
    char_name: str,
    preload_tick: int,
    sp_consume: int,
    uuid: str = "skill-node-uuid",
) -> SkillNode:
    node = SkillNode.__new__(SkillNode)
    node.char_name = char_name
    node.preload_tick = preload_tick
    node.skill = SimpleNamespace(sp_consume=sp_consume)
    node.UUID = uuid
    return node


class _FakeElegantPreparationContext:
    def __init__(
        self,
        *,
        owner: str,
        index: str,
        buff_0: object,
        calls: list[tuple[str, object]],
    ) -> None:
        self._owner = owner
        self._index = index
        self._buff_0 = buff_0
        self._calls = calls

    def find_equipper(self, item_name: str) -> str:
        self._calls.append(("find_equipper", item_name))
        return self._owner

    def find_sub_exist_buff_dict(self, owner_name: str) -> dict[str, object]:
        self._calls.append(("find_sub_exist_buff_dict", owner_name))
        return {self._index: self._buff_0}


def _install_preparation_context(
    monkeypatch: pytest.MonkeyPatch,
    *,
    harness: SimpleNamespace,
    owner: str,
    buff_0: SimpleNamespace,
) -> tuple[list[object], list[tuple[str, object]]]:
    context_build_calls: list[object] = []
    calls: list[tuple[str, object]] = []

    def fake_build_preparation_context_from_buff(
        buff_instance: object,
    ) -> _FakeElegantPreparationContext:
        context_build_calls.append(buff_instance)
        return _FakeElegantPreparationContext(
            owner=owner,
            index=harness.buff_instance.ft.index,
            buff_0=buff_0,
            calls=calls,
        )

    monkeypatch.setattr(
        elegant_module,
        "build_preparation_context_from_buff",
        fake_build_preparation_context_from_buff,
    )
    return context_build_calls, calls


def _install_preparation(
    monkeypatch: pytest.MonkeyPatch,
    *,
    harness: SimpleNamespace,
    owner: str,
    buff_0: SimpleNamespace,
) -> list[dict[str, object]]:
    preparation_calls: list[dict[str, object]] = []

    def fake_check_preparation(
        *,
        buff_instance: object,
        buff_0: object,
        preparation_context: object,
        **kwargs: object,
    ) -> None:
        assert buff_instance is harness.buff_instance
        assert buff_0 is buff_0_ref
        assert isinstance(preparation_context, _FakeElegantPreparationContext)
        preparation_calls.append({"preparation_context": preparation_context, **kwargs})
        record = cast(Any, buff_0_ref.history.record)
        record.equipper = owner
        record.char = SimpleNamespace(NAME=owner)

    buff_0_ref = buff_0
    monkeypatch.setattr(elegant_module, "check_preparation", fake_check_preparation)
    return preparation_calls


def test_elegant_vanity_check_record_module_preserves_owner_template_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _logic_harness()
    owner = "仪玄"
    buff_0 = _buff_0()
    context_build_calls, context_calls = _install_preparation_context(
        monkeypatch,
        harness=harness,
        owner=owner,
        buff_0=buff_0,
    )

    harness.logic.check_record_module()

    assert context_build_calls == [harness.buff_instance]
    assert context_calls == [
        ("find_equipper", "玲珑妆匣"),
        ("find_sub_exist_buff_dict", owner),
    ]
    assert harness.logic.equipper == owner
    assert harness.logic.buff_0 is buff_0
    assert isinstance(buff_0.history.record, elegant_module.ElegantVanityDmgBonusRecord)
    assert harness.logic.record is buff_0.history.record
    assert cast(Any, harness.logic.record).last_update_tick_node is None

    existing_record = harness.logic.record
    harness.logic.check_record_module()

    assert context_build_calls == [harness.buff_instance]
    assert context_calls == [
        ("find_equipper", "玲珑妆匣"),
        ("find_sub_exist_buff_dict", owner),
    ]
    assert harness.logic.record is existing_record
    assert buff_0.history.record is existing_record


@pytest.mark.parametrize(
    ("char_name", "preload_tick_offset", "sp_consume", "expected"),
    [
        ("仪玄", 0, 25, True),
        ("仪玄", 4, 30, True),
        ("安比", 0, 25, False),
        ("仪玄", -1, 25, False),
        ("仪玄", 0, 24, False),
    ],
)
def test_elegant_vanity_special_judge_logic_pins_char_preload_and_sp_gates(
    monkeypatch: pytest.MonkeyPatch,
    char_name: str,
    preload_tick_offset: int,
    sp_consume: int,
    expected: bool,
) -> None:
    harness = _logic_harness(tick=120)
    owner = "仪玄"
    buff_0 = _buff_0()
    context_build_calls, context_calls = _install_preparation_context(
        monkeypatch,
        harness=harness,
        owner=owner,
        buff_0=buff_0,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        harness=harness,
        owner=owner,
        buff_0=buff_0,
    )
    tick_calls: list[object] = []

    def fake_find_tick(*, sim_instance: object) -> int:
        tick_calls.append(sim_instance)
        return harness.sim_instance.tick

    monkeypatch.setattr(elegant_module.JudgeTools, "find_tick", fake_find_tick)

    skill_node = _skill_node(
        char_name=char_name,
        preload_tick=harness.sim_instance.tick + preload_tick_offset,
        sp_consume=sp_consume,
    )

    result = harness.logic.special_judge_logic(skill_node=skill_node)

    assert result is expected
    assert context_build_calls == [harness.buff_instance, harness.buff_instance]
    assert context_calls == [
        ("find_equipper", "玲珑妆匣"),
        ("find_sub_exist_buff_dict", owner),
    ]
    assert len(preparation_calls) == 1
    assert isinstance(
        preparation_calls[0]["preparation_context"],
        _FakeElegantPreparationContext,
    )
    assert preparation_calls[0]["equipper"] == "玲珑妆匣"
    if char_name == owner:
        assert tick_calls == [harness.sim_instance]
    else:
        assert tick_calls == []
    assert harness.logic.equipper == owner
    assert harness.logic.buff_0 is buff_0
    assert harness.logic.record is buff_0.history.record
    assert cast(Any, harness.logic.record).char.NAME == owner
    if expected:
        assert cast(Any, harness.logic.record).last_update_tick_node is skill_node
    else:
        assert cast(Any, harness.logic.record).last_update_tick_node is None


def test_elegant_vanity_special_judge_logic_pins_uuid_dedupe_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _logic_harness(tick=120)
    owner = "仪玄"
    buff_0 = _buff_0()
    _install_preparation_context(
        monkeypatch,
        harness=harness,
        owner=owner,
        buff_0=buff_0,
    )
    _install_preparation(
        monkeypatch,
        harness=harness,
        owner=owner,
        buff_0=buff_0,
    )
    monkeypatch.setattr(
        elegant_module.JudgeTools,
        "find_tick",
        lambda *, sim_instance: harness.sim_instance.tick,
    )

    first = _skill_node(
        char_name=owner,
        preload_tick=harness.sim_instance.tick,
        sp_consume=25,
        uuid="same-uuid",
    )
    duplicate = _skill_node(
        char_name=owner,
        preload_tick=harness.sim_instance.tick,
        sp_consume=25,
        uuid="same-uuid",
    )
    distinct = _skill_node(
        char_name=owner,
        preload_tick=harness.sim_instance.tick,
        sp_consume=25,
        uuid="distinct-uuid",
    )

    assert harness.logic.special_judge_logic(skill_node=first) is True
    assert cast(Any, harness.logic.record).last_update_tick_node is first

    assert harness.logic.special_judge_logic(skill_node=duplicate) is False
    assert cast(Any, harness.logic.record).last_update_tick_node is first

    assert harness.logic.special_judge_logic(skill_node=distinct) is True
    assert cast(Any, harness.logic.record).last_update_tick_node is distinct
