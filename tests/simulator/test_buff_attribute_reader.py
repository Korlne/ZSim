from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest

import zsim.sim_progress.ScheduledEvent.Calculator as calculator_module
from zsim.sim_progress.Buff.BuffXLogic.BranchBladeSongCritDamageBonus import (
    BranchBladeSongCritDamageBonus,
)
from zsim.sim_progress.ScheduledEvent.Calculator import (
    BuffAttributeReadContext,
    Calculator,
    CalculatorBuffAttributeReader,
    MultiplierData,
)


def _make_character(*, name: str = "折枝剑歌", am: float) -> SimpleNamespace:
    statement = SimpleNamespace(statement={"AM": am}, AM=am)
    return SimpleNamespace(NAME=name, CID=1301, level=60, statement=statement)


def _make_enemy(enemy_debuff: object) -> SimpleNamespace:
    return SimpleNamespace(
        dynamic=SimpleNamespace(
            dynamic_debuff_list=[enemy_debuff],
            dynamic_dot_list=[],
        ),
        sim_instance=SimpleNamespace(marker="sim"),
    )


@pytest.mark.parametrize(
    ("static_am", "field_am", "flat_am", "expected"),
    [
        (100.0, 0.10, 5.0, 115.0),
        (115.0, 0.0, 0.0, 115.0),
        (80.0, 0.25, 10.0, 110.0),
    ],
)
def test_attribute_reader_matches_old_anomaly_mastery_helper(
    monkeypatch: pytest.MonkeyPatch,
    static_am: float,
    field_am: float,
    flat_am: float,
    expected: float,
) -> None:
    MultiplierData.mul_data_cache.clear()
    char_buff = object()
    enemy_debuff = object()
    char = _make_character(am=static_am)
    enemy = _make_enemy(enemy_debuff)
    active_buff_view = {char.NAME: [char_buff]}
    aggregation_calls: list[tuple[tuple[object, ...], object | None, object, str | None]] = []

    def fake_cal_buff_total_bonus(
        *,
        enabled_buff: tuple[object, ...],
        judge_obj: object | None,
        sim_instance: object,
        char_name: str | None,
    ) -> dict[str, float]:
        aggregation_calls.append((enabled_buff, judge_obj, sim_instance, char_name))
        return {
            "局内异常掌控": field_am,
            "固定异常掌控": flat_am,
        }

    monkeypatch.setattr(
        calculator_module,
        "cal_buff_total_bonus",
        fake_cal_buff_total_bonus,
    )

    context = BuffAttributeReadContext(
        enemy=cast(Any, enemy),
        active_buff_view=active_buff_view,
        character=cast(Any, char),
    )
    reader_value = CalculatorBuffAttributeReader().read_anomaly_mastery(context)

    old_data = MultiplierData(
        cast(Any, enemy),
        active_buff_view,
        cast(Any, char),
    )
    old_value = Calculator.AnomalyMul.cal_am(old_data)

    assert reader_value == pytest.approx(old_value)
    assert reader_value == pytest.approx(expected)
    assert aggregation_calls == [
        ((char_buff, enemy_debuff), None, enemy.sim_instance, char.NAME),
        ((char_buff, enemy_debuff), None, enemy.sim_instance, char.NAME),
    ]


def test_attribute_reader_keeps_query_node_optional(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    char = _make_character(am=90.0)
    enemy = _make_enemy(object())

    def fake_cal_buff_total_bonus(**kwargs: object) -> dict[str, float]:
        assert kwargs["judge_obj"] is None
        return {}

    monkeypatch.setattr(
        calculator_module,
        "cal_buff_total_bonus",
        fake_cal_buff_total_bonus,
    )

    context = BuffAttributeReadContext(
        enemy=cast(Any, enemy),
        active_buff_view={},
        character=cast(Any, char),
    )

    assert CalculatorBuffAttributeReader().read_anomaly_mastery(context) == pytest.approx(
        90.0
    )


@pytest.mark.parametrize(
    ("static_am", "field_am", "flat_am", "expected_gate"),
    [
        (80.0, 0.25, 10.0, False),
        (100.0, 0.10, 5.0, True),
        (116.0, 0.0, 0.0, True),
    ],
)
def test_branch_blade_song_gate_uses_attribute_reader_with_old_helper_parity(
    monkeypatch: pytest.MonkeyPatch,
    static_am: float,
    field_am: float,
    flat_am: float,
    expected_gate: bool,
) -> None:
    MultiplierData.mul_data_cache.clear()
    char_buff = object()
    enemy_debuff = object()
    char = _make_character(am=static_am)
    enemy = _make_enemy(enemy_debuff)
    active_buff_view = {char.NAME: [char_buff]}
    aggregation_calls: list[tuple[tuple[object, ...], object | None, object, str | None]] = []

    def fake_cal_buff_total_bonus(
        *,
        enabled_buff: tuple[object, ...],
        judge_obj: object | None,
        sim_instance: object,
        char_name: str | None,
    ) -> dict[str, float]:
        aggregation_calls.append((enabled_buff, judge_obj, sim_instance, char_name))
        return {
            "局内异常掌控": field_am,
            "固定异常掌控": flat_am,
        }

    monkeypatch.setattr(
        calculator_module,
        "cal_buff_total_bonus",
        fake_cal_buff_total_bonus,
    )

    logic = cast(
        Any,
        BranchBladeSongCritDamageBonus.__new__(BranchBladeSongCritDamageBonus),
    )
    logic.record = SimpleNamespace(
        enemy=enemy,
        dynamic_buff_list=active_buff_view,
        char=char,
    )
    get_prepared_calls: list[dict[str, object]] = []
    logic.check_record_module = lambda: None
    logic.get_prepared = lambda **kwargs: get_prepared_calls.append(kwargs)

    reader_gate = logic.special_judge_logic()
    old_data = MultiplierData(
        cast(Any, enemy),
        active_buff_view,
        cast(Any, char),
    )
    old_gate = Calculator.AnomalyMul.cal_am(old_data) >= 115

    assert reader_gate == old_gate
    assert reader_gate is expected_gate
    assert get_prepared_calls == [
        {"equipper": "折枝剑歌", "enemy": 1, "dynamic_buff_list": 1}
    ]
    assert aggregation_calls == [
        ((char_buff, enemy_debuff), None, enemy.sim_instance, char.NAME),
        ((char_buff, enemy_debuff), None, enemy.sim_instance, char.NAME),
    ]
