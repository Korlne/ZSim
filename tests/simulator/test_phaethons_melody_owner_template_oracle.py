from types import SimpleNamespace
from typing import Any, cast

import pytest

import zsim.sim_progress.Buff.BuffXLogic.PhaethonsMelody as phaethons_module
from zsim.sim_progress.Preload import SkillNode


def _buff_0() -> SimpleNamespace:
    return SimpleNamespace(history=SimpleNamespace(record=None))


def _logic_harness(*, index: str = "phaethons-template-index", tick: int = 120) -> SimpleNamespace:
    sim_instance = SimpleNamespace(tick=tick)
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index=index),
    )
    logic = phaethons_module.PhaethonsMelody(cast(Any, buff_instance))
    return SimpleNamespace(
        logic=logic,
        buff_instance=buff_instance,
        sim_instance=sim_instance,
    )


def _skill_node(
    *,
    char_name: str,
    preload_tick: int,
    trigger_buff_level: int,
) -> SkillNode:
    node = SkillNode.__new__(SkillNode)
    node.char_name = char_name
    node.preload_tick = preload_tick
    node.skill = SimpleNamespace(trigger_buff_level=trigger_buff_level)
    return node


def _install_direct_owner_template_lookup(
    monkeypatch: pytest.MonkeyPatch,
    *,
    harness: SimpleNamespace,
    owner: str,
    buff_0: SimpleNamespace,
) -> tuple[list[tuple[str, object]], list[object]]:
    owner_calls: list[tuple[str, object]] = []
    template_calls: list[object] = []

    def fake_find_equipper(item_name: str, *, sim_instance: object) -> str:
        owner_calls.append((item_name, sim_instance))
        return owner

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        template_calls.append(sim_instance)
        return {owner: {harness.buff_instance.ft.index: buff_0}}

    monkeypatch.setattr(phaethons_module.JudgeTools, "find_equipper", fake_find_equipper)
    monkeypatch.setattr(
        phaethons_module.JudgeTools,
        "find_exist_buff_dict",
        fake_find_exist_buff_dict,
    )
    return owner_calls, template_calls


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
        **kwargs: object,
    ) -> None:
        assert buff_instance is harness.buff_instance
        assert buff_0 is buff_0_ref
        preparation_calls.append(dict(kwargs))
        record = cast(Any, buff_0_ref.history.record)
        record.equipper = owner
        record.char = SimpleNamespace(NAME=owner)

    buff_0_ref = buff_0
    monkeypatch.setattr(phaethons_module, "check_preparation", fake_check_preparation)
    return preparation_calls


def test_phaethons_check_record_module_preserves_direct_owner_template_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _logic_harness()
    owner = "妮可"
    buff_0 = _buff_0()
    owner_calls, template_calls = _install_direct_owner_template_lookup(
        monkeypatch,
        harness=harness,
        owner=owner,
        buff_0=buff_0,
    )

    harness.logic.check_record_module()

    assert owner_calls == [("法厄同之歌", harness.sim_instance)]
    assert template_calls == [harness.sim_instance]
    assert harness.logic.equipper == owner
    assert harness.logic.buff_0 is buff_0
    assert isinstance(buff_0.history.record, phaethons_module.PhaethonsMelodyRecord)
    assert harness.logic.record is buff_0.history.record
    assert cast(Any, harness.logic.record).equipper is None
    assert cast(Any, harness.logic.record).char is None

    existing_record = harness.logic.record
    harness.logic.check_record_module()

    assert owner_calls == [("法厄同之歌", harness.sim_instance)]
    assert template_calls == [harness.sim_instance]
    assert harness.logic.record is existing_record
    assert buff_0.history.record is existing_record


def test_phaethons_special_judge_logic_pins_missing_and_type_gates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _logic_harness()
    owner = "妮可"
    buff_0 = _buff_0()
    _install_direct_owner_template_lookup(
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
    assert preparation_calls == [{"equipper": "法厄同之歌"}]

    with pytest.raises(TypeError, match="不是SkillNode类"):
        harness.logic.special_judge_logic(skill_node=object())

    assert preparation_calls == [
        {"equipper": "法厄同之歌"},
        {"equipper": "法厄同之歌"},
    ]


@pytest.mark.parametrize(
    ("char_name", "trigger_buff_level", "preload_tick_offset", "expected", "tick_checked"),
    [
        ("安比", 2, 0, True, True),
        ("妮可", 2, 0, False, False),
        ("安比", 1, 0, False, False),
        ("安比", 3, 0, False, False),
        ("安比", 2, -1, False, True),
        ("安比", 2, 1, False, True),
    ],
)
def test_phaethons_special_judge_logic_pins_non_equipper_enhanced_e_and_preload_gates(
    monkeypatch: pytest.MonkeyPatch,
    char_name: str,
    trigger_buff_level: int,
    preload_tick_offset: int,
    expected: bool,
    tick_checked: bool,
) -> None:
    harness = _logic_harness(tick=120)
    owner = "妮可"
    buff_0 = _buff_0()
    owner_calls, template_calls = _install_direct_owner_template_lookup(
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

    monkeypatch.setattr(phaethons_module, "find_tick", fake_find_tick)

    skill_node = _skill_node(
        char_name=char_name,
        preload_tick=harness.sim_instance.tick + preload_tick_offset,
        trigger_buff_level=trigger_buff_level,
    )

    result = harness.logic.special_judge_logic(skill_node=skill_node)

    assert result is expected
    assert owner_calls == [("法厄同之歌", harness.sim_instance)]
    assert template_calls == [harness.sim_instance]
    assert preparation_calls == [{"equipper": "法厄同之歌"}]
    assert harness.logic.equipper == owner
    assert harness.logic.buff_0 is buff_0
    assert harness.logic.record is buff_0.history.record
    assert cast(Any, harness.logic.record).equipper == owner
    assert cast(Any, harness.logic.record).char.NAME == owner
    assert tick_calls == ([harness.sim_instance] if tick_checked else [])
