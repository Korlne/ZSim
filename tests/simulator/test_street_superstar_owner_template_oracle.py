from types import SimpleNamespace
from typing import Any, cast

import pytest

import zsim.sim_progress.Buff.BuffXLogic.StreetSuperstar as street_module
from zsim.sim_progress.Preload import SkillNode


def _buff_0() -> SimpleNamespace:
    return SimpleNamespace(history=SimpleNamespace(record=None))


def _logic_harness(
    *,
    index: str = "street-template-index",
    tick: int = 660,
) -> SimpleNamespace:
    sim_instance = SimpleNamespace(tick=tick)
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index=index),
        dy=SimpleNamespace(endticks="stale-endticks"),
    )
    logic = street_module.StreetSuperstar(cast(Any, buff_instance))
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
    ticks: int = 72,
) -> SkillNode:
    node = SkillNode.__new__(SkillNode)
    node.char_name = char_name
    node.preload_tick = preload_tick
    node.skill = SimpleNamespace(trigger_buff_level=trigger_buff_level, ticks=ticks)
    return node


def _install_preparation_context(
    monkeypatch: pytest.MonkeyPatch,
    *,
    harness: SimpleNamespace,
    owner: str,
    buff_0: SimpleNamespace,
) -> tuple[SimpleNamespace, list[object], list[tuple[str, object]]]:
    build_calls: list[object] = []
    context_calls: list[tuple[str, object]] = []

    def fake_find_equipper(item_name: str) -> str:
        context_calls.append(("find_equipper", item_name))
        return owner

    def fake_find_sub_exist_buff_dict(owner_name: str) -> dict[str, object]:
        context_calls.append(("find_sub_exist_buff_dict", owner_name))
        assert owner_name == owner
        return {harness.buff_instance.ft.index: buff_0}

    preparation_context = SimpleNamespace(
        find_equipper=fake_find_equipper,
        find_sub_exist_buff_dict=fake_find_sub_exist_buff_dict,
    )

    def fake_build_preparation_context(buff_instance: object) -> SimpleNamespace:
        build_calls.append(buff_instance)
        assert buff_instance is harness.buff_instance
        return preparation_context

    if hasattr(street_module, "JudgeTools"):
        monkeypatch.setattr(
            street_module.JudgeTools,
            "find_equipper",
            lambda *args, **kwargs: pytest.fail("Street must use PreparationContext"),
        )
        monkeypatch.setattr(
            street_module.JudgeTools,
            "find_exist_buff_dict",
            lambda *args, **kwargs: pytest.fail("Street must use PreparationContext"),
        )
    monkeypatch.setattr(
        street_module,
        "build_preparation_context_from_buff",
        fake_build_preparation_context,
    )
    return preparation_context, build_calls, context_calls


def _install_preparation(
    monkeypatch: pytest.MonkeyPatch,
    *,
    harness: SimpleNamespace,
    owner: str,
    buff_0: SimpleNamespace,
    preparation_context: SimpleNamespace,
    sub_exist_buff_dict: dict[str, object] | None = None,
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
        assert preparation_context is preparation_context_ref
        preparation_calls.append(dict(kwargs))
        record = cast(Any, buff_0_ref.history.record)
        record.equipper = owner
        record.char = SimpleNamespace(NAME=owner)
        if kwargs.get("sub_exist_buff_dict") == 1:
            record.sub_exist_buff_dict = sub_exist_buff_dict_ref

    buff_0_ref = buff_0
    preparation_context_ref = preparation_context
    sub_exist_buff_dict_ref = (
        sub_exist_buff_dict
        if sub_exist_buff_dict is not None
        else {harness.buff_instance.ft.index: buff_0}
    )
    monkeypatch.setattr(street_module, "check_preparation", fake_check_preparation)
    return preparation_calls


def _install_tick(monkeypatch: pytest.MonkeyPatch, *, harness: SimpleNamespace) -> list[object]:
    tick_calls: list[object] = []

    def fake_find_tick(*, sim_instance: object) -> int:
        tick_calls.append(sim_instance)
        return harness.sim_instance.tick

    monkeypatch.setattr(street_module, "find_tick", fake_find_tick)
    return tick_calls


def _prepared_logic(
    monkeypatch: pytest.MonkeyPatch,
    *,
    tick: int = 660,
    owner: str = "伊芙琳",
    sub_exist_buff_dict: dict[str, object] | None = None,
) -> tuple[SimpleNamespace, SimpleNamespace, list[dict[str, object]]]:
    harness = _logic_harness(tick=tick)
    buff_0 = _buff_0()
    preparation_context, _, _ = _install_preparation_context(
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
        preparation_context=preparation_context,
        sub_exist_buff_dict=sub_exist_buff_dict,
    )
    return harness, buff_0, preparation_calls


def test_street_check_record_module_pins_preparation_context_owner_template_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _logic_harness()
    owner = "伊芙琳"
    buff_0 = _buff_0()
    _, build_calls, context_calls = _install_preparation_context(
        monkeypatch,
        harness=harness,
        owner=owner,
        buff_0=buff_0,
    )

    harness.logic.check_record_module()

    assert build_calls == [harness.buff_instance]
    assert context_calls == [
        ("find_equipper", "街头巨星"),
        ("find_sub_exist_buff_dict", owner),
    ]
    assert harness.logic.equipper == owner
    assert harness.logic.buff_0 is buff_0
    assert isinstance(buff_0.history.record, street_module.StreetSuperstarRecord)
    assert harness.logic.record is buff_0.history.record
    assert cast(Any, harness.logic.record).equipper is None
    assert cast(Any, harness.logic.record).char is None
    assert cast(Any, harness.logic.record).sub_exist_buff_dict is None
    assert cast(Any, harness.logic.record).qte_counter == 0
    assert cast(Any, harness.logic.record).max_qte == 3
    assert cast(Any, harness.logic.record).active_signal is None

    existing_record = harness.logic.record
    harness.logic.check_record_module()

    assert build_calls == [harness.buff_instance]
    assert context_calls == [
        ("find_equipper", "街头巨星"),
        ("find_sub_exist_buff_dict", owner),
    ]
    assert harness.logic.record is existing_record
    assert buff_0.history.record is existing_record


def test_street_special_judge_logic_pins_missing_and_type_gates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness, _, preparation_calls = _prepared_logic(monkeypatch)

    assert harness.logic.special_judge_logic() is False

    with pytest.raises(TypeError, match="SkillNode"):
        harness.logic.special_judge_logic(skill_node=object())

    assert preparation_calls == [
        {"equipper": "街头巨星"},
        {"equipper": "街头巨星"},
    ]


def test_street_special_judge_logic_pins_qte_accumulation_cap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness, buff_0, preparation_calls = _prepared_logic(monkeypatch, tick=700)
    tick_calls = _install_tick(monkeypatch, harness=harness)
    harness.logic.check_record_module()
    record = cast(Any, buff_0.history.record)
    record.qte_counter = 2

    result = harness.logic.special_judge_logic(
        skill_node=_skill_node(
            char_name="任意角色",
            preload_tick=harness.sim_instance.tick,
            trigger_buff_level=5,
        )
    )
    capped_result = harness.logic.special_judge_logic(
        skill_node=_skill_node(
            char_name="任意角色",
            preload_tick=harness.sim_instance.tick,
            trigger_buff_level=5,
        )
    )

    assert result is False
    assert capped_result is False
    assert record.qte_counter == record.max_qte == 3
    assert record.active_signal is None
    assert preparation_calls == [
        {"equipper": "街头巨星"},
        {"equipper": "街头巨星"},
    ]
    assert tick_calls == [harness.sim_instance, harness.sim_instance]


@pytest.mark.parametrize(
    ("preload_tick_offset", "trigger_buff_level"),
    [
        (-1, 5),
        (1, 5),
        (0, 1),
    ],
)
def test_street_special_judge_logic_pins_preload_and_unsupported_level_gates(
    monkeypatch: pytest.MonkeyPatch,
    preload_tick_offset: int,
    trigger_buff_level: int,
) -> None:
    harness, buff_0, preparation_calls = _prepared_logic(monkeypatch, tick=720)
    tick_calls = _install_tick(monkeypatch, harness=harness)

    result = harness.logic.special_judge_logic(
        skill_node=_skill_node(
            char_name="任意角色",
            preload_tick=harness.sim_instance.tick + preload_tick_offset,
            trigger_buff_level=trigger_buff_level,
        )
    )

    assert result is False
    assert cast(Any, buff_0.history.record).qte_counter == 0
    assert cast(Any, buff_0.history.record).active_signal is None
    assert preparation_calls == [{"equipper": "街头巨星"}]
    assert tick_calls == [harness.sim_instance]


def test_street_special_judge_logic_pins_ultimate_owner_gate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness, buff_0, preparation_calls = _prepared_logic(monkeypatch, tick=750)
    tick_calls = _install_tick(monkeypatch, harness=harness)
    owner_signal = _skill_node(
        char_name="伊芙琳",
        preload_tick=harness.sim_instance.tick,
        trigger_buff_level=6,
    )

    assert harness.logic.special_judge_logic(skill_node=owner_signal) is True
    assert cast(Any, buff_0.history.record).active_signal is owner_signal

    cast(Any, buff_0.history.record).active_signal = None
    non_owner_signal = _skill_node(
        char_name="安比",
        preload_tick=harness.sim_instance.tick,
        trigger_buff_level=6,
    )

    assert harness.logic.special_judge_logic(skill_node=non_owner_signal) is False
    assert cast(Any, buff_0.history.record).active_signal is None
    assert preparation_calls == [
        {"equipper": "街头巨星"},
        {"equipper": "街头巨星"},
    ]
    assert tick_calls == [harness.sim_instance, harness.sim_instance]


def test_street_special_start_logic_pins_zero_counter_noop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness, buff_0, preparation_calls = _prepared_logic(monkeypatch, tick=800)
    tick_calls = _install_tick(monkeypatch, harness=harness)
    harness.buff_instance.simple_start = lambda *args, **kwargs: pytest.fail(
        "zero counter must not call simple_start"
    )
    harness.buff_instance.update_to_buff_0 = lambda *args, **kwargs: pytest.fail(
        "zero counter must not call update_to_buff_0"
    )
    harness.logic.check_record_module()
    cast(Any, buff_0.history.record).active_signal = _skill_node(
        char_name="伊芙琳",
        preload_tick=harness.sim_instance.tick,
        trigger_buff_level=6,
    )

    harness.logic.special_start_logic()

    assert preparation_calls == [
        {"equipper": "街头巨星", "sub_exist_buff_dict": 1}
    ]
    assert tick_calls == []
    assert harness.buff_instance.dy.endticks == "stale-endticks"
    assert cast(Any, buff_0.history.record).qte_counter == 0


def test_street_special_start_logic_pins_simple_start_endticks_update_and_cleanup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _logic_harness(tick=840)
    owner = "伊芙琳"
    buff_0 = _buff_0()
    sub_exist_buff_dict = {harness.buff_instance.ft.index: buff_0, "neighbor": object()}
    preparation_context, _, _ = _install_preparation_context(
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
        preparation_context=preparation_context,
        sub_exist_buff_dict=sub_exist_buff_dict,
    )
    tick_calls = _install_tick(monkeypatch, harness=harness)
    events: list[tuple[str, object]] = []

    def fake_simple_start(
        timenow: int,
        exist_buff_dict: dict[str, object],
        **kwargs: object,
    ) -> None:
        events.append(
            (
                "simple_start",
                {
                    "timenow": timenow,
                    "exist_buff_dict": exist_buff_dict,
                    "kwargs": dict(kwargs),
                    "endticks_at_call": harness.buff_instance.dy.endticks,
                },
            )
        )

    def fake_update_to_buff_0(target_buff_0: object) -> None:
        events.append(
            (
                "update_to_buff_0",
                {
                    "target": target_buff_0,
                    "endticks_at_call": harness.buff_instance.dy.endticks,
                },
            )
        )

    harness.buff_instance.simple_start = fake_simple_start
    harness.buff_instance.update_to_buff_0 = fake_update_to_buff_0
    harness.logic.check_record_module()
    record = cast(Any, buff_0.history.record)
    record.qte_counter = 2
    ultimate_signal = _skill_node(
        char_name=owner,
        preload_tick=harness.sim_instance.tick,
        trigger_buff_level=6,
        ticks=90,
    )
    record.active_signal = ultimate_signal
    harness.logic.active_signal = ultimate_signal

    harness.logic.special_start_logic()

    assert preparation_calls == [
        {"equipper": "街头巨星", "sub_exist_buff_dict": 1}
    ]
    assert tick_calls == [harness.sim_instance, harness.sim_instance]
    assert events == [
        (
            "simple_start",
            {
                "timenow": 840,
                "exist_buff_dict": sub_exist_buff_dict,
                "kwargs": {"specified_count": 2, "no_end": 1},
                "endticks_at_call": "stale-endticks",
            },
        ),
        (
            "update_to_buff_0",
            {
                "target": buff_0,
                "endticks_at_call": 930,
            },
        ),
    ]
    assert harness.buff_instance.dy.endticks == 930
    assert record.qte_counter == 0
    assert record.active_signal is ultimate_signal
    assert harness.logic.active_signal is None
