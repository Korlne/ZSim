from __future__ import annotations

from dataclasses import dataclass
import inspect
from types import SimpleNamespace
from typing import Any, Sequence, cast

import pytest

import zsim.sim_progress.ScheduledEvent.Calculator as calculator_module
from zsim.sim_progress.Buff.BuffXLogic.BranchBladeSongCritDamageBonus import (
    BranchBladeSongCritDamageBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.TimeweaverDisorderDmgMul import (
    TimeweaverDisorderDmgMul,
)
from zsim.sim_progress.ScheduledEvent.Calculator import (
    BuffAttributeReadContext,
    Calculator,
    CalculatorBuffAttributeReader,
    MultiplierData,
    create_anomaly_attribute_read_context,
)

_AggregationCall = tuple[tuple[object, ...], object | None, object, str | None]


@dataclass(frozen=True)
class _AttributeReadFixture:
    context: BuffAttributeReadContext
    active_buff_view: dict[str, list[object]]
    enemy: SimpleNamespace
    char: SimpleNamespace
    expected_enabled_buff: tuple[object, ...]


def _make_character(
    *, name: str = "折枝剑歌", am: float = 0.0, ap: float = 0.0
) -> SimpleNamespace:
    statement = SimpleNamespace(statement={"AM": am, "AP": ap}, AM=am, AP=ap)
    return SimpleNamespace(NAME=name, CID=1301, level=60, statement=statement)


def _make_enemy(enemy_debuffs: Sequence[object] = ()) -> SimpleNamespace:
    return SimpleNamespace(
        dynamic=SimpleNamespace(
            dynamic_debuff_list=list(enemy_debuffs),
            dynamic_dot_list=[],
        ),
        sim_instance=SimpleNamespace(marker="sim"),
    )


def _make_attribute_read_fixture(
    *,
    name: str = "折枝剑歌",
    am: float = 0.0,
    ap: float = 0.0,
    char_buff_count: int = 1,
    enemy_debuff_count: int = 1,
) -> _AttributeReadFixture:
    char_buffs = tuple(object() for _ in range(char_buff_count))
    enemy_debuffs = tuple(object() for _ in range(enemy_debuff_count))
    char = _make_character(name=name, am=am, ap=ap)
    enemy = _make_enemy(enemy_debuffs)
    active_buff_view = {char.NAME: list(char_buffs)}
    return _AttributeReadFixture(
        context=create_anomaly_attribute_read_context(
            enemy=cast(Any, enemy),
            active_buff_view=active_buff_view,
            character=cast(Any, char),
        ),
        active_buff_view=active_buff_view,
        enemy=enemy,
        char=char,
        expected_enabled_buff=char_buffs + enemy_debuffs,
    )


def test_create_anomaly_attribute_read_context_preserves_inputs() -> None:
    char = _make_character(am=115.0, ap=375.0)
    enemy = _make_enemy()
    active_buff_view = {char.NAME: [object()]}
    query_node = SimpleNamespace(marker="node")

    context = create_anomaly_attribute_read_context(
        enemy=cast(Any, enemy),
        active_buff_view=active_buff_view,
        character=cast(Any, char),
        query_node=cast(Any, query_node),
    )

    assert isinstance(context, BuffAttributeReadContext)
    assert context.enemy is enemy
    assert context.active_buff_view is active_buff_view
    assert context.character is char
    assert context.query_node is query_node


def _patch_buff_aggregation(
    monkeypatch: pytest.MonkeyPatch,
    dynamic_statement: dict[str, float],
) -> list[_AggregationCall]:
    aggregation_calls: list[_AggregationCall] = []

    def fake_cal_buff_total_bonus(
        *,
        enabled_buff: tuple[object, ...],
        judge_obj: object | None,
        sim_instance: object,
        char_name: str | None,
    ) -> dict[str, float]:
        aggregation_calls.append((enabled_buff, judge_obj, sim_instance, char_name))
        return dict(dynamic_statement)

    monkeypatch.setattr(
        calculator_module,
        "cal_buff_total_bonus",
        fake_cal_buff_total_bonus,
    )
    return aggregation_calls


@pytest.mark.parametrize(
    (
        "static_am",
        "field_am",
        "flat_am",
        "char_buff_count",
        "enemy_debuff_count",
        "expected",
    ),
    [
        pytest.param(115.0, 0.0, 0.0, 1, 1, 115.0, id="baseline"),
        pytest.param(100.0, 0.15, 0.0, 1, 1, 115.0, id="percentage-buff"),
        pytest.param(100.0, 0.0, 15.0, 1, 1, 115.0, id="flat-buff"),
        pytest.param(115.0, 0.0, 0.0, 0, 0, 115.0, id="no-buff"),
    ],
)
def test_attribute_reader_matches_old_anomaly_mastery_helper(
    monkeypatch: pytest.MonkeyPatch,
    static_am: float,
    field_am: float,
    flat_am: float,
    char_buff_count: int,
    enemy_debuff_count: int,
    expected: float,
) -> None:
    MultiplierData.mul_data_cache.clear()
    fixture = _make_attribute_read_fixture(
        am=static_am,
        char_buff_count=char_buff_count,
        enemy_debuff_count=enemy_debuff_count,
    )
    aggregation_calls = _patch_buff_aggregation(
        monkeypatch,
        {
            "局内异常掌控": field_am,
            "固定异常掌控": flat_am,
        },
    )

    reader_value = CalculatorBuffAttributeReader().read_anomaly_mastery(fixture.context)

    old_data = MultiplierData(
        cast(Any, fixture.enemy),
        fixture.active_buff_view,
        cast(Any, fixture.char),
    )
    old_value = Calculator.AnomalyMul.cal_am(old_data)

    assert reader_value == pytest.approx(old_value)
    assert reader_value == pytest.approx(expected)
    assert aggregation_calls == [
        (
            fixture.expected_enabled_buff,
            None,
            fixture.enemy.sim_instance,
            fixture.char.NAME,
        ),
        (
            fixture.expected_enabled_buff,
            None,
            fixture.enemy.sim_instance,
            fixture.char.NAME,
        ),
    ]


def test_attribute_reader_keeps_query_node_optional(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _make_attribute_read_fixture(am=90.0, enemy_debuff_count=0)

    def fake_cal_buff_total_bonus(**kwargs: object) -> dict[str, float]:
        assert kwargs["judge_obj"] is None
        return {}

    monkeypatch.setattr(
        calculator_module,
        "cal_buff_total_bonus",
        fake_cal_buff_total_bonus,
    )

    assert CalculatorBuffAttributeReader().read_anomaly_mastery(
        fixture.context
    ) == pytest.approx(90.0)


@pytest.mark.parametrize(
    (
        "static_ap",
        "field_ap",
        "flat_ap",
        "char_buff_count",
        "enemy_debuff_count",
        "expected",
    ),
    [
        pytest.param(375.0, 0.0, 0.0, 1, 1, 375.0, id="baseline"),
        pytest.param(300.0, 0.25, 0.0, 1, 1, 375.0, id="percentage-buff"),
        pytest.param(300.0, 0.0, 75.0, 1, 1, 375.0, id="flat-buff"),
        pytest.param(375.0, 0.0, 0.0, 0, 0, 375.0, id="no-buff"),
    ],
)
def test_attribute_reader_matches_old_anomaly_proficiency_helper(
    monkeypatch: pytest.MonkeyPatch,
    static_ap: float,
    field_ap: float,
    flat_ap: float,
    char_buff_count: int,
    enemy_debuff_count: int,
    expected: float,
) -> None:
    MultiplierData.mul_data_cache.clear()
    fixture = _make_attribute_read_fixture(
        name="时流贤者",
        ap=static_ap,
        char_buff_count=char_buff_count,
        enemy_debuff_count=enemy_debuff_count,
    )
    aggregation_calls = _patch_buff_aggregation(
        monkeypatch,
        {
            "局内异常精通": field_ap,
            "固定异常精通": flat_ap,
        },
    )

    reader_value = CalculatorBuffAttributeReader().read_anomaly_proficiency(
        fixture.context
    )

    old_data = MultiplierData(
        cast(Any, fixture.enemy),
        fixture.active_buff_view,
        cast(Any, fixture.char),
    )
    old_value = Calculator.AnomalyMul.cal_ap(old_data)

    assert reader_value == pytest.approx(old_value)
    assert reader_value == pytest.approx(expected)
    assert aggregation_calls == [
        (
            fixture.expected_enabled_buff,
            None,
            fixture.enemy.sim_instance,
            fixture.char.NAME,
        ),
        (
            fixture.expected_enabled_buff,
            None,
            fixture.enemy.sim_instance,
            fixture.char.NAME,
        ),
    ]


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
    fixture = _make_attribute_read_fixture(am=static_am)
    aggregation_calls = _patch_buff_aggregation(
        monkeypatch,
        {
            "局内异常掌控": field_am,
            "固定异常掌控": flat_am,
        },
    )

    logic = cast(
        Any,
        BranchBladeSongCritDamageBonus.__new__(BranchBladeSongCritDamageBonus),
    )
    logic.record = SimpleNamespace(
        enemy=fixture.enemy,
        dynamic_buff_list=fixture.active_buff_view,
        char=fixture.char,
    )
    get_prepared_calls: list[dict[str, object]] = []
    logic.check_record_module = lambda: None
    logic.get_prepared = lambda **kwargs: get_prepared_calls.append(kwargs)

    reader_gate = logic.special_judge_logic()
    old_data = MultiplierData(
        cast(Any, fixture.enemy),
        fixture.active_buff_view,
        cast(Any, fixture.char),
    )
    old_gate = Calculator.AnomalyMul.cal_am(old_data) >= 115

    source = inspect.getsource(BranchBladeSongCritDamageBonus.special_judge_logic)
    assert "MultiplierData" not in source
    assert "Mul(" not in source
    assert "read_anomaly_mastery" in source
    assert reader_gate == old_gate
    assert reader_gate is expected_gate
    assert get_prepared_calls == [
        {"equipper": "折枝剑歌", "enemy": 1, "dynamic_buff_list": 1}
    ]
    assert aggregation_calls == [
        (
            fixture.expected_enabled_buff,
            None,
            fixture.enemy.sim_instance,
            fixture.char.NAME,
        ),
        (
            fixture.expected_enabled_buff,
            None,
            fixture.enemy.sim_instance,
            fixture.char.NAME,
        ),
    ]


@pytest.mark.parametrize(
    ("static_ap", "field_ap", "flat_ap", "expected_gate"),
    [
        (240.0, 0.25, 50.0, False),
        (300.0, 0.20, 15.0, True),
        (376.0, 0.0, 0.0, True),
    ],
)
def test_timeweaver_disorder_gate_uses_attribute_reader_with_old_helper_parity(
    monkeypatch: pytest.MonkeyPatch,
    static_ap: float,
    field_ap: float,
    flat_ap: float,
    expected_gate: bool,
) -> None:
    MultiplierData.mul_data_cache.clear()
    fixture = _make_attribute_read_fixture(name="时流贤者", ap=static_ap)
    aggregation_calls = _patch_buff_aggregation(
        monkeypatch,
        {
            "局内异常精通": field_ap,
            "固定异常精通": flat_ap,
        },
    )

    logic = cast(
        Any,
        TimeweaverDisorderDmgMul.__new__(TimeweaverDisorderDmgMul),
    )
    logic.record = SimpleNamespace(
        enemy=fixture.enemy,
        dynamic_buff_list=fixture.active_buff_view,
        char=fixture.char,
    )
    get_prepared_calls: list[dict[str, object]] = []
    logic.check_record_module = lambda: None
    logic.get_prepared = lambda **kwargs: get_prepared_calls.append(kwargs)

    reader_gate = logic.special_judge_logic()
    old_data = MultiplierData(
        cast(Any, fixture.enemy),
        fixture.active_buff_view,
        cast(Any, fixture.char),
    )
    old_gate = Calculator.AnomalyMul.cal_ap(old_data) >= 375

    source = inspect.getsource(TimeweaverDisorderDmgMul.special_judge_logic)
    assert "MultiplierData" not in source
    assert "Mul(" not in source
    assert "read_anomaly_proficiency" in source
    assert reader_gate == old_gate
    assert bool(reader_gate) is expected_gate
    assert get_prepared_calls == [
        {"equipper": "时流贤者", "preload_data": 1, "dynamic_buff_list": 1, "enemy": 1}
    ]
    assert aggregation_calls == [
        (
            fixture.expected_enabled_buff,
            None,
            fixture.enemy.sim_instance,
            fixture.char.NAME,
        ),
        (
            fixture.expected_enabled_buff,
            None,
            fixture.enemy.sim_instance,
            fixture.char.NAME,
        ),
    ]
