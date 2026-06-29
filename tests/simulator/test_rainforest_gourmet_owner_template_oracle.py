from types import SimpleNamespace
from typing import Any, cast

import pytest

import zsim.sim_progress.Buff.BuffXLogic.RainforestGourmetATKBonus as rainforest_module
from zsim.sim_progress.Preload import SkillNode


def _buff_0() -> SimpleNamespace:
    return SimpleNamespace(history=SimpleNamespace(record=None))


def _logic_harness(
    *,
    index: str = "rainforest-template-index",
    tick: int = 120,
) -> SimpleNamespace:
    sim_instance = SimpleNamespace(tick=tick)
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index=index),
    )
    logic = rainforest_module.RainforestGourmetATKBonus(cast(Any, buff_instance))
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
) -> SkillNode:
    node = SkillNode.__new__(SkillNode)
    node.char_name = char_name
    node.preload_tick = preload_tick
    node.skill = SimpleNamespace(sp_consume=sp_consume)
    return node


def _install_direct_owner_template(
    monkeypatch: pytest.MonkeyPatch,
    *,
    harness: SimpleNamespace,
    owner: str,
    buff_0: SimpleNamespace,
) -> tuple[list[tuple[str, object]], list[object]]:
    calls: list[tuple[str, object]] = []
    find_exist_calls: list[object] = []

    def fake_find_equipper(item_name: str, *, sim_instance: object) -> str:
        calls.append(("find_equipper", item_name))
        assert sim_instance is harness.sim_instance
        return owner

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        find_exist_calls.append(sim_instance)
        return {owner: {harness.buff_instance.ft.index: buff_0}}

    monkeypatch.setattr(rainforest_module.JudgeTools, "find_equipper", fake_find_equipper)
    monkeypatch.setattr(
        rainforest_module.JudgeTools,
        "find_exist_buff_dict",
        fake_find_exist_buff_dict,
    )
    return calls, find_exist_calls


def _install_preparation(
    monkeypatch: pytest.MonkeyPatch,
    *,
    harness: SimpleNamespace,
    owner: str,
    buff_0: SimpleNamespace,
    sub_exist_buff_dict: dict[str, object] | None = None,
) -> list[dict[str, object]]:
    preparation_calls: list[dict[str, object]] = []

    def fake_check_preparation(
        *,
        buff_instance: object,
        buff_0: object,
        **kwargs: object,
    ) -> None:
        assert buff_instance is harness.buff_instance
        assert buff_0 is buff_0_ref
        preparation_calls.append(dict(kwargs))
        record = cast(Any, buff_0_ref.history.record)
        record.equipper = owner
        record.char = SimpleNamespace(NAME=owner)
        if kwargs.get("sub_exist_buff_dict") == 1:
            record.sub_exist_buff_dict = sub_exist_buff_dict_ref

    buff_0_ref = buff_0
    sub_exist_buff_dict_ref = (
        sub_exist_buff_dict
        if sub_exist_buff_dict is not None
        else {harness.buff_instance.ft.index: buff_0}
    )
    monkeypatch.setattr(rainforest_module, "check_preparation", fake_check_preparation)
    return preparation_calls


def test_rainforest_check_record_module_preserves_owner_template_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _logic_harness()
    owner = "露西"
    buff_0 = _buff_0()
    owner_calls, find_exist_calls = _install_direct_owner_template(
        monkeypatch,
        harness=harness,
        owner=owner,
        buff_0=buff_0,
    )

    harness.logic.check_record_module()

    assert owner_calls == [("find_equipper", "雨林饕客")]
    assert find_exist_calls == [harness.sim_instance]
    assert harness.logic.equipper == owner
    assert harness.logic.buff_0 is buff_0
    assert isinstance(buff_0.history.record, rainforest_module.RainforestGourmetATKBonusRecord)
    assert harness.logic.record is buff_0.history.record
    assert cast(Any, harness.logic.record).equipper is None
    assert cast(Any, harness.logic.record).char is None
    assert cast(Any, harness.logic.record).sub_exist_buff_dict is None
    assert cast(Any, harness.logic.record).last_update_node is None

    existing_record = harness.logic.record
    harness.logic.check_record_module()

    assert owner_calls == [("find_equipper", "雨林饕客")]
    assert find_exist_calls == [harness.sim_instance]
    assert harness.logic.record is existing_record
    assert buff_0.history.record is existing_record


def test_rainforest_special_judge_logic_pins_missing_and_type_gates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _logic_harness()
    owner = "露西"
    buff_0 = _buff_0()
    _install_direct_owner_template(
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

    assert harness.logic.special_judge_logic() is False
    assert preparation_calls == [{"equipper": "雨林饕客"}]

    with pytest.raises(TypeError):
        harness.logic.special_judge_logic(skill_node=object())

    assert preparation_calls == [
        {"equipper": "雨林饕客"},
        {"equipper": "雨林饕客"},
    ]


@pytest.mark.parametrize(
    ("char_name", "preload_tick_offset", "sp_consume", "expected", "tick_checked"),
    [
        ("露西", 0, 28, True, True),
        ("安比", 0, 28, False, False),
        ("露西", -1, 28, False, True),
        ("露西", 1, 28, False, True),
        ("露西", 0, 0, False, True),
    ],
)
def test_rainforest_special_judge_logic_pins_char_tick_sp_and_last_update_node(
    monkeypatch: pytest.MonkeyPatch,
    char_name: str,
    preload_tick_offset: int,
    sp_consume: int,
    expected: bool,
    tick_checked: bool,
) -> None:
    harness = _logic_harness(tick=120)
    owner = "露西"
    buff_0 = _buff_0()
    _install_direct_owner_template(
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

    monkeypatch.setattr(rainforest_module, "find_tick", fake_find_tick)

    skill_node = _skill_node(
        char_name=char_name,
        preload_tick=harness.sim_instance.tick + preload_tick_offset,
        sp_consume=sp_consume,
    )

    result = harness.logic.special_judge_logic(skill_node=skill_node)

    assert result is expected
    assert preparation_calls == [{"equipper": "雨林饕客"}]
    assert tick_calls == ([harness.sim_instance] if tick_checked else [])
    assert harness.logic.equipper == owner
    assert harness.logic.buff_0 is buff_0
    assert harness.logic.record is buff_0.history.record
    assert cast(Any, harness.logic.record).char.NAME == owner
    if expected:
        assert cast(Any, harness.logic.record).last_update_node is skill_node
    else:
        assert cast(Any, harness.logic.record).last_update_node is None


@pytest.mark.parametrize(
    ("sp_consume", "expected_count"),
    [
        (9, 0),
        (10, 1),
        (28, 2),
        (39, 3),
    ],
)
def test_rainforest_special_start_logic_pins_simple_start_count_and_no_update_to_buff_0(
    monkeypatch: pytest.MonkeyPatch,
    sp_consume: int,
    expected_count: int,
) -> None:
    harness = _logic_harness(tick=321)
    owner = "露西"
    buff_0 = _buff_0()
    sub_exist_buff_dict = {harness.buff_instance.ft.index: buff_0, "neighbor": object()}
    simple_start_calls: list[dict[str, object]] = []

    def fake_simple_start(
        timenow: int,
        exist_buff_dict: dict[str, object],
        **kwargs: object,
    ) -> None:
        simple_start_calls.append(
            {
                "timenow": timenow,
                "exist_buff_dict": exist_buff_dict,
                "kwargs": dict(kwargs),
            }
        )

    def fail_update_to_buff_0(*args: object, **kwargs: object) -> None:
        raise AssertionError("Rainforest current behavior must not call update_to_buff_0")

    harness.buff_instance.simple_start = fake_simple_start
    harness.buff_instance.update_to_buff_0 = fail_update_to_buff_0
    _install_direct_owner_template(
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
        sub_exist_buff_dict=sub_exist_buff_dict,
    )
    tick_calls: list[object] = []

    def fake_find_tick(*, sim_instance: object) -> int:
        tick_calls.append(sim_instance)
        return harness.sim_instance.tick

    monkeypatch.setattr(rainforest_module, "find_tick", fake_find_tick)

    harness.logic.check_record_module()
    cast(Any, harness.logic.record).last_update_node = _skill_node(
        char_name=owner,
        preload_tick=harness.sim_instance.tick,
        sp_consume=sp_consume,
    )

    harness.logic.special_start_logic()

    assert preparation_calls == [{"equipper": "雨林饕客", "sub_exist_buff_dict": 1}]
    assert tick_calls == [harness.sim_instance]
    assert simple_start_calls == [
        {
            "timenow": harness.sim_instance.tick,
            "exist_buff_dict": sub_exist_buff_dict,
            "kwargs": {"individule_settled_count": expected_count},
        }
    ]
