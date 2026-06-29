from types import SimpleNamespace
from typing import Any, cast

import pytest

import zsim.sim_progress.Buff.BuffXLogic.RiotSuppressorMarkVI as riot_module
from zsim.sim_progress.Preload import SkillNode


def _buff_0(*, active: bool = False) -> SimpleNamespace:
    return SimpleNamespace(
        history=SimpleNamespace(record=None),
        dy=SimpleNamespace(active=active),
    )


def _logic_harness(
    *,
    index: str = "riot-template-index",
    tick: int = 240,
) -> SimpleNamespace:
    sim_instance = SimpleNamespace(tick=tick)
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index=index),
    )
    logic = riot_module.RiotSuppressorMarkVI(cast(Any, buff_instance))
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


def _install_direct_owner_template(
    monkeypatch: pytest.MonkeyPatch,
    *,
    harness: SimpleNamespace,
    owner: str,
    buff_0: SimpleNamespace,
) -> tuple[list[tuple[str, object]], list[object]]:
    owner_calls: list[tuple[str, object]] = []
    find_exist_calls: list[object] = []

    def fake_find_equipper(item_name: str, *, sim_instance: object) -> str:
        owner_calls.append(("find_equipper", item_name))
        assert sim_instance is harness.sim_instance
        return owner

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        find_exist_calls.append(sim_instance)
        return {owner: {harness.buff_instance.ft.index: buff_0}}

    monkeypatch.setattr(riot_module.JudgeTools, "find_equipper", fake_find_equipper)
    monkeypatch.setattr(
        riot_module.JudgeTools,
        "find_exist_buff_dict",
        fake_find_exist_buff_dict,
    )
    return owner_calls, find_exist_calls


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
    monkeypatch.setattr(riot_module, "check_preparation", fake_check_preparation)
    return preparation_calls


def _install_tick(monkeypatch: pytest.MonkeyPatch, *, harness: SimpleNamespace) -> list[object]:
    tick_calls: list[object] = []

    def fake_find_tick(*, sim_instance: object) -> int:
        tick_calls.append(sim_instance)
        return harness.sim_instance.tick

    monkeypatch.setattr(riot_module, "find_tick", fake_find_tick)
    return tick_calls


def _prepared_logic(
    monkeypatch: pytest.MonkeyPatch,
    *,
    active: bool = False,
    tick: int = 240,
    owner: str = "朱鸢",
) -> tuple[SimpleNamespace, SimpleNamespace, list[dict[str, object]]]:
    harness = _logic_harness(tick=tick)
    buff_0 = _buff_0(active=active)
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
    return harness, buff_0, preparation_calls


def test_riot_check_record_module_preserves_owner_template_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _logic_harness()
    owner = "朱鸢"
    buff_0 = _buff_0()
    owner_calls, find_exist_calls = _install_direct_owner_template(
        monkeypatch,
        harness=harness,
        owner=owner,
        buff_0=buff_0,
    )

    harness.logic.check_record_module()

    assert owner_calls == [("find_equipper", "防暴者Ⅵ型")]
    assert find_exist_calls == [harness.sim_instance]
    assert harness.logic.equipper == owner
    assert harness.logic.buff_0 is buff_0
    assert isinstance(buff_0.history.record, riot_module.RiotSuppressorMarkVIRecord)
    assert harness.logic.record is buff_0.history.record
    assert cast(Any, harness.logic.record).equipper is None
    assert cast(Any, harness.logic.record).char is None
    assert cast(Any, harness.logic.record).max_effect_times == 8
    assert cast(Any, harness.logic.record).available_effect_times == 0
    assert cast(Any, harness.logic.record).active_signal is None
    assert cast(Any, harness.logic.record).sub_exist_buff_dict is None

    existing_record = harness.logic.record
    harness.logic.check_record_module()

    assert owner_calls == [("find_equipper", "防暴者Ⅵ型")]
    assert find_exist_calls == [harness.sim_instance]
    assert harness.logic.record is existing_record
    assert buff_0.history.record is existing_record


def test_riot_special_judge_logic_pins_missing_type_and_active_zero_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness, buff_0, preparation_calls = _prepared_logic(monkeypatch)

    assert harness.logic.special_judge_logic() is False
    assert preparation_calls == [{"equipper": "防暴者Ⅵ型"}]

    with pytest.raises(ValueError):
        harness.logic.special_judge_logic(skill_node=object())

    buff_0.dy.active = True
    cast(Any, buff_0.history.record).available_effect_times = 0
    with pytest.raises(ValueError):
        harness.logic.special_judge_logic(
            skill_node=_skill_node(
                char_name="朱鸢",
                preload_tick=harness.sim_instance.tick,
                trigger_buff_level=2,
            )
        )


@pytest.mark.parametrize(
    (
        "char_name",
        "trigger_buff_level",
        "preload_tick_offset",
        "active",
        "available_effect_times",
        "expected",
        "expected_signal",
    ),
    [
        ("朱鸢", 2, 0, False, 0, True, 2),
        ("朱鸢", 0, 0, True, 3, True, 0),
        ("朱鸢", 0, 0, False, 0, False, None),
        ("安比", 2, 0, False, 0, False, None),
        ("朱鸢", 1, 0, False, 0, False, None),
        ("朱鸢", 2, -1, False, 0, False, None),
        ("朱鸢", 2, 1, False, 0, False, None),
    ],
)
def test_riot_special_judge_logic_pins_signal_gates(
    monkeypatch: pytest.MonkeyPatch,
    char_name: str,
    trigger_buff_level: int,
    preload_tick_offset: int,
    active: bool,
    available_effect_times: int,
    expected: bool,
    expected_signal: int | None,
) -> None:
    harness, buff_0, preparation_calls = _prepared_logic(monkeypatch, active=active)
    tick_calls = _install_tick(monkeypatch, harness=harness)
    skill_node = _skill_node(
        char_name=char_name,
        preload_tick=harness.sim_instance.tick + preload_tick_offset,
        trigger_buff_level=trigger_buff_level,
    )
    harness.logic.check_record_module()
    cast(Any, buff_0.history.record).available_effect_times = available_effect_times

    result = harness.logic.special_judge_logic(skill_node=skill_node)

    assert result is expected
    assert preparation_calls == [{"equipper": "防暴者Ⅵ型"}]
    assert tick_calls == (
        [harness.sim_instance]
        if char_name == "朱鸢" and trigger_buff_level in [2, 0]
        else []
    )
    assert cast(Any, harness.logic.record).active_signal == expected_signal


def test_riot_special_judge_logic_pins_pending_signal_guard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness, buff_0, _ = _prepared_logic(monkeypatch)
    _install_tick(monkeypatch, harness=harness)
    harness.logic.check_record_module()
    cast(Any, buff_0.history.record).active_signal = 2

    with pytest.raises(ValueError):
        harness.logic.special_judge_logic(
            skill_node=_skill_node(
                char_name="朱鸢",
                preload_tick=harness.sim_instance.tick,
                trigger_buff_level=2,
            )
        )

    assert cast(Any, buff_0.history.record).active_signal == 2


@pytest.mark.parametrize(
    ("before_available", "expected_available"),
    [
        (0, 8),
        (5, 8),
        (8, 8),
    ],
)
def test_riot_special_effect_logic_pins_refresh_simple_start_and_signal_cleanup(
    monkeypatch: pytest.MonkeyPatch,
    before_available: int,
    expected_available: int,
) -> None:
    harness = _logic_harness(tick=345)
    owner = "朱鸢"
    buff_0 = _buff_0()
    sub_exist_buff_dict = {harness.buff_instance.ft.index: buff_0, "neighbor": object()}
    simple_start_calls: list[dict[str, object]] = []
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
    tick_calls = _install_tick(monkeypatch, harness=harness)

    def fake_simple_start(timenow: int, exist_buff_dict: dict[str, object]) -> None:
        simple_start_calls.append(
            {"timenow": timenow, "exist_buff_dict": exist_buff_dict}
        )

    harness.buff_instance.simple_start = fake_simple_start
    harness.logic.check_record_module()
    record = cast(Any, harness.logic.record)
    record.active_signal = 2
    record.available_effect_times = before_available

    harness.logic.special_effect_logic()

    assert preparation_calls == [{"equipper": "防暴者Ⅵ型", "sub_exist_buff_dict": 1}]
    assert tick_calls == [harness.sim_instance]
    assert simple_start_calls == [
        {"timenow": harness.sim_instance.tick, "exist_buff_dict": sub_exist_buff_dict}
    ]
    assert record.available_effect_times == expected_available
    assert record.active_signal is None


def test_riot_special_effect_logic_pins_consume_decrement_without_simple_start(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness, buff_0, preparation_calls = _prepared_logic(monkeypatch)
    harness.buff_instance.simple_start = lambda *args, **kwargs: pytest.fail(
        "consume must not call simple_start"
    )
    harness.logic.check_record_module()
    record = cast(Any, buff_0.history.record)
    record.active_signal = 0
    record.available_effect_times = 3

    harness.logic.special_effect_logic()

    assert preparation_calls == [{"equipper": "防暴者Ⅵ型", "sub_exist_buff_dict": 1}]
    assert record.available_effect_times == 2
    assert record.active_signal is None


@pytest.mark.parametrize(
    ("active_signal", "available_effect_times"),
    [
        (0, 0),
        (9, 3),
    ],
)
def test_riot_special_effect_logic_pins_error_signals_without_cleanup(
    monkeypatch: pytest.MonkeyPatch,
    active_signal: int,
    available_effect_times: int,
) -> None:
    harness, buff_0, _ = _prepared_logic(monkeypatch)
    harness.logic.check_record_module()
    record = cast(Any, buff_0.history.record)
    record.active_signal = active_signal
    record.available_effect_times = available_effect_times

    with pytest.raises(ValueError):
        harness.logic.special_effect_logic()

    assert record.active_signal == active_signal


@pytest.mark.parametrize(
    ("available_effect_times", "expected"),
    [
        (0, True),
        (1, False),
        (8, False),
    ],
)
def test_riot_special_exit_logic_pins_available_effect_gate(
    monkeypatch: pytest.MonkeyPatch,
    available_effect_times: int,
    expected: bool,
) -> None:
    harness, buff_0, preparation_calls = _prepared_logic(monkeypatch)
    harness.logic.check_record_module()
    cast(Any, buff_0.history.record).available_effect_times = available_effect_times

    assert harness.logic.special_exit_logic() is expected
    assert preparation_calls == [{"equipper": "防暴者Ⅵ型"}]
