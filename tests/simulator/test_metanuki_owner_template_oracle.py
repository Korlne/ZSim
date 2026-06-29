from types import SimpleNamespace
from typing import Any, cast

import pytest

import zsim.sim_progress.Buff.BuffXLogic.MetanukiMorphosisAPBonus as metanuki_module
from zsim.sim_progress.Preload import SkillNode


def _buff_0() -> SimpleNamespace:
    return SimpleNamespace(history=SimpleNamespace(record=None))


def _logic_harness(*, index: str = "metanuki-template-index", tick: int = 120) -> SimpleNamespace:
    sim_instance = SimpleNamespace(tick=tick)
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index=index),
    )
    logic = metanuki_module.MetanukiMorphosisAPBonus(cast(Any, buff_instance))
    return SimpleNamespace(
        logic=logic,
        buff_instance=buff_instance,
        sim_instance=sim_instance,
    )


def _skill_node(
    *,
    char_name: str,
    tick: int,
    labels: dict[str, object] | None,
    hits_now: bool,
) -> SkillNode:
    node = SkillNode.__new__(SkillNode)
    node.char_name = char_name
    node.skill = SimpleNamespace(labels=labels)
    node.labels = labels
    node.tick_list = [tick - 0.5] if hits_now else [tick - 2.0]
    return node


def test_metanuki_check_record_module_preserves_direct_owner_template_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _logic_harness()
    owner = "猫又"
    buff_0 = _buff_0()
    find_equipper_calls: list[tuple[str, object]] = []
    find_exist_calls: list[object] = []
    exist_buff_dict = {owner: {harness.buff_instance.ft.index: buff_0}}

    def fake_find_equipper(item_name: str, *, sim_instance: object) -> str:
        find_equipper_calls.append((item_name, sim_instance))
        return owner

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        find_exist_calls.append(sim_instance)
        return exist_buff_dict

    monkeypatch.setattr(metanuki_module.JudgeTools, "find_equipper", fake_find_equipper)
    monkeypatch.setattr(
        metanuki_module.JudgeTools,
        "find_exist_buff_dict",
        fake_find_exist_buff_dict,
    )

    harness.logic.check_record_module()

    assert find_equipper_calls == [("狸法七变化", harness.sim_instance)]
    assert find_exist_calls == [harness.sim_instance]
    assert harness.logic.equipper == owner
    assert harness.logic.buff_0 is buff_0
    assert isinstance(buff_0.history.record, metanuki_module.MetanukiMorphosisAPBonusRecord)
    assert harness.logic.record is buff_0.history.record

    existing_record = harness.logic.record
    harness.logic.check_record_module()

    assert find_equipper_calls == [("狸法七变化", harness.sim_instance)]
    assert find_exist_calls == [harness.sim_instance]
    assert harness.logic.record is existing_record
    assert buff_0.history.record is existing_record


@pytest.mark.parametrize(
    ("char_name", "labels", "hits_now", "expected"),
    [
        ("猫又", {"aftershock_attack": 1}, True, True),
        ("安比", {"aftershock_attack": 1}, True, False),
        ("猫又", {}, True, False),
        ("猫又", None, True, False),
        ("猫又", {"aftershock_attack": 1}, False, False),
    ],
)
def test_metanuki_special_judge_logic_pins_aftershock_label_and_hit_timing(
    monkeypatch: pytest.MonkeyPatch,
    char_name: str,
    labels: dict[str, object] | None,
    hits_now: bool,
    expected: bool,
) -> None:
    harness = _logic_harness(tick=120)
    owner = "猫又"
    buff_0 = _buff_0()
    find_equipper_calls: list[tuple[str, object]] = []
    find_exist_calls: list[object] = []
    preparation_calls: list[dict[str, object]] = []
    exist_buff_dict = {owner: {harness.buff_instance.ft.index: buff_0}}

    def fake_find_equipper(item_name: str, *, sim_instance: object) -> str:
        find_equipper_calls.append((item_name, sim_instance))
        return owner

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        find_exist_calls.append(sim_instance)
        return exist_buff_dict

    def fake_check_preparation(
        *,
        buff_instance: object,
        buff_0: object,
        **kwargs: object,
    ) -> None:
        assert buff_instance is harness.buff_instance
        assert buff_0 is buff_0_ref
        preparation_calls.append(kwargs)
        record = cast(Any, buff_0_ref.history.record)
        record.equipper = owner
        record.char = SimpleNamespace(NAME=owner)

    buff_0_ref = buff_0

    monkeypatch.setattr(metanuki_module.JudgeTools, "find_equipper", fake_find_equipper)
    monkeypatch.setattr(
        metanuki_module.JudgeTools,
        "find_exist_buff_dict",
        fake_find_exist_buff_dict,
    )
    monkeypatch.setattr(metanuki_module, "check_preparation", fake_check_preparation)

    result = harness.logic.special_judge_logic(
        skill_node=_skill_node(
            char_name=char_name,
            tick=harness.sim_instance.tick,
            labels=labels,
            hits_now=hits_now,
        )
    )

    assert result is expected
    assert find_equipper_calls == [("狸法七变化", harness.sim_instance)]
    assert find_exist_calls == [harness.sim_instance]
    assert preparation_calls == [{"equipper": "狸法七变化"}]
    assert harness.logic.equipper == owner
    assert harness.logic.buff_0 is buff_0
    assert harness.logic.record is buff_0.history.record
    assert cast(Any, harness.logic.record).char.NAME == owner
