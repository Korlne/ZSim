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


class _FakeMetanukiPreparationContext:
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


def test_metanuki_check_record_module_preserves_owner_template_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _logic_harness()
    owner = "猫又"
    buff_0 = _buff_0()
    context_build_calls: list[object] = []
    context_calls: list[tuple[str, object]] = []

    def fake_build_preparation_context_from_buff(
        buff_instance: object,
    ) -> _FakeMetanukiPreparationContext:
        context_build_calls.append(buff_instance)
        return _FakeMetanukiPreparationContext(
            owner=owner,
            index=harness.buff_instance.ft.index,
            buff_0=buff_0,
            calls=context_calls,
        )

    monkeypatch.setattr(
        metanuki_module,
        "build_preparation_context_from_buff",
        fake_build_preparation_context_from_buff,
    )

    harness.logic.check_record_module()

    assert context_build_calls == [harness.buff_instance]
    assert context_calls == [
        ("find_equipper", "狸法七变化"),
        ("find_sub_exist_buff_dict", owner),
    ]
    assert harness.logic.equipper == owner
    assert harness.logic.buff_0 is buff_0
    assert isinstance(buff_0.history.record, metanuki_module.MetanukiMorphosisAPBonusRecord)
    assert harness.logic.record is buff_0.history.record

    existing_record = harness.logic.record
    harness.logic.check_record_module()

    assert context_build_calls == [harness.buff_instance]
    assert context_calls == [
        ("find_equipper", "狸法七变化"),
        ("find_sub_exist_buff_dict", owner),
    ]
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
    context_build_calls: list[object] = []
    context_calls: list[tuple[str, object]] = []
    preparation_calls: list[dict[str, object]] = []

    def fake_build_preparation_context_from_buff(
        buff_instance: object,
    ) -> _FakeMetanukiPreparationContext:
        context_build_calls.append(buff_instance)
        return _FakeMetanukiPreparationContext(
            owner=owner,
            index=harness.buff_instance.ft.index,
            buff_0=buff_0,
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
        assert buff_0 is buff_0_ref
        assert isinstance(preparation_context, _FakeMetanukiPreparationContext)
        preparation_calls.append({"preparation_context": preparation_context, **kwargs})
        record = cast(Any, buff_0_ref.history.record)
        record.equipper = owner
        record.char = SimpleNamespace(NAME=owner)

    buff_0_ref = buff_0

    monkeypatch.setattr(
        metanuki_module,
        "build_preparation_context_from_buff",
        fake_build_preparation_context_from_buff,
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
    assert context_build_calls == [harness.buff_instance, harness.buff_instance]
    assert context_calls == [
        ("find_equipper", "狸法七变化"),
        ("find_sub_exist_buff_dict", owner),
    ]
    assert len(preparation_calls) == 1
    assert isinstance(
        preparation_calls[0]["preparation_context"],
        _FakeMetanukiPreparationContext,
    )
    assert preparation_calls[0]["equipper"] == "狸法七变化"
    assert harness.logic.equipper == owner
    assert harness.logic.buff_0 is buff_0
    assert harness.logic.record is buff_0.history.record
    assert cast(Any, harness.logic.record).char.NAME == owner
