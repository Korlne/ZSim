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
    *,
    name: str = "折枝剑歌",
    am: float = 0.0,
    ap: float = 0.0,
    imp: float = 0.0,
    crit_rate: float = 0.0,
    crit_damage: float = 0.0,
) -> SimpleNamespace:
    statement_values = {
        "AM": am,
        "AP": ap,
        "IMP": imp,
        "CRIT_rate": crit_rate,
        "CRIT_damage": crit_damage,
    }
    statement = SimpleNamespace(statement=statement_values)
    for attr_name, value in statement_values.items():
        setattr(statement, attr_name, value)
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
    imp: float = 0.0,
    crit_rate: float = 0.0,
    crit_damage: float = 0.0,
    char_buff_count: int = 1,
    enemy_debuff_count: int = 1,
) -> _AttributeReadFixture:
    char_buffs = tuple(object() for _ in range(char_buff_count))
    enemy_debuffs = tuple(object() for _ in range(enemy_debuff_count))
    char = _make_character(
        name=name,
        am=am,
        ap=ap,
        imp=imp,
        crit_rate=crit_rate,
        crit_damage=crit_damage,
    )
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


def _reader_snapshot_data(context: BuffAttributeReadContext) -> MultiplierData:
    return CalculatorBuffAttributeReader._build_formula_snapshot(context)


def _legacy_multiplier_data(fixture: _AttributeReadFixture) -> MultiplierData:
    return MultiplierData(
        cast(Any, fixture.enemy),
        fixture.active_buff_view,
        cast(Any, fixture.char),
        cast(Any, fixture.context.query_node),
    )


def _legacy_impact_oracle(fixture: _AttributeReadFixture) -> float:
    return Calculator.StunMul.cal_imp(_legacy_multiplier_data(fixture))


def _legacy_full_crit_rate_oracle(fixture: _AttributeReadFixture) -> float:
    return Calculator.RegularMul.cal_crit_rate(_legacy_multiplier_data(fixture))


def _legacy_personal_crit_rate_oracle(fixture: _AttributeReadFixture) -> float:
    return Calculator.RegularMul.cal_personal_crit_rate(
        _legacy_multiplier_data(fixture)
    )


def _legacy_personal_crit_damage_oracle(fixture: _AttributeReadFixture) -> float:
    return Calculator.RegularMul.cal_personal_crit_dmg(
        _legacy_multiplier_data(fixture)
    )


def _assert_aggregation_calls(
    aggregation_calls: list[_AggregationCall],
    fixture: _AttributeReadFixture,
    *,
    times: int = 2,
) -> None:
    assert aggregation_calls == [
        (
            fixture.expected_enabled_buff,
            None,
            fixture.enemy.sim_instance,
            fixture.char.NAME,
        )
    ] * times


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
    (
        "static_imp",
        "field_imp",
        "flat_imp",
        "char_buff_count",
        "enemy_debuff_count",
        "expected",
    ),
    [
        pytest.param(100.0, 0.0, 0.0, 1, 1, 100.0, id="baseline"),
        pytest.param(100.0, 0.2, 0.0, 1, 1, 120.0, id="percentage-buff"),
        pytest.param(100.0, 0.0, 12.0, 1, 1, 112.0, id="flat-buff"),
        pytest.param(90.0, 0.1, 9.0, 0, 1, 108.0, id="enemy-debuff"),
        pytest.param(123.0, 0.0, 0.0, 0, 0, 123.0, id="no-buff"),
    ],
)
def test_p2b_parity_fixture_matches_old_impact_helper(
    monkeypatch: pytest.MonkeyPatch,
    static_imp: float,
    field_imp: float,
    flat_imp: float,
    char_buff_count: int,
    enemy_debuff_count: int,
    expected: float,
) -> None:
    MultiplierData.mul_data_cache.clear()
    fixture = _make_attribute_read_fixture(
        name="冲击测试",
        imp=static_imp,
        char_buff_count=char_buff_count,
        enemy_debuff_count=enemy_debuff_count,
    )
    aggregation_calls = _patch_buff_aggregation(
        monkeypatch,
        {
            "局内冲击力%": field_imp,
            "固定冲击力": flat_imp,
        },
    )

    reader_value = CalculatorBuffAttributeReader().read_impact(fixture.context)
    old_value = _legacy_impact_oracle(fixture)

    assert reader_value == pytest.approx(old_value)
    assert reader_value == pytest.approx(expected)
    _assert_aggregation_calls(aggregation_calls, fixture)


@pytest.mark.parametrize(
    (
        "static_crit_rate",
        "field_crit_rate",
        "flat_crit_rate",
        "received_crit_rate",
        "char_buff_count",
        "enemy_debuff_count",
        "expected_full",
        "expected_personal",
    ),
    [
        pytest.param(0.05, 0.0, 0.0, 0.0, 1, 1, 0.05, 0.05, id="baseline"),
        pytest.param(0.1, 0.2, 0.0, 0.0, 1, 1, 0.3, 0.3, id="field-buff"),
        pytest.param(0.1, 0.0, 0.12, 0.0, 1, 1, 0.22, 0.22, id="flat-buff"),
        pytest.param(
            0.1,
            0.0,
            0.0,
            0.15,
            0,
            1,
            0.25,
            0.1,
            id="received-enemy-debuff",
        ),
        pytest.param(0.2, 0.0, 0.0, 0.0, 0, 0, 0.2, 0.2, id="no-buff"),
    ],
)
def test_p2b_parity_fixture_matches_old_full_and_personal_crit_rate_helpers(
    monkeypatch: pytest.MonkeyPatch,
    static_crit_rate: float,
    field_crit_rate: float,
    flat_crit_rate: float,
    received_crit_rate: float,
    char_buff_count: int,
    enemy_debuff_count: int,
    expected_full: float,
    expected_personal: float,
) -> None:
    MultiplierData.mul_data_cache.clear()
    fixture = _make_attribute_read_fixture(
        name="双暴测试",
        crit_rate=static_crit_rate,
        char_buff_count=char_buff_count,
        enemy_debuff_count=enemy_debuff_count,
    )
    aggregation_calls = _patch_buff_aggregation(
        monkeypatch,
        {
            "局内暴击率": field_crit_rate,
            "固定暴击率": flat_crit_rate,
            "被暴击几率增加": received_crit_rate,
        },
    )

    reader = CalculatorBuffAttributeReader()
    reader_full = reader.read_full_crit_rate(fixture.context)
    reader_personal = reader.read_personal_crit_rate(fixture.context)
    old_full = _legacy_full_crit_rate_oracle(fixture)
    old_personal = _legacy_personal_crit_rate_oracle(fixture)

    assert reader_full == pytest.approx(old_full)
    assert reader_personal == pytest.approx(old_personal)
    assert reader_full == pytest.approx(expected_full)
    assert reader_personal == pytest.approx(expected_personal)
    assert reader_full - reader_personal == pytest.approx(received_crit_rate)
    _assert_aggregation_calls(aggregation_calls, fixture, times=3)


def test_p2b_full_crit_rate_includes_received_bonus_but_personal_excludes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    MultiplierData.mul_data_cache.clear()
    fixture = _make_attribute_read_fixture(
        name="受暴击测试",
        crit_rate=0.2,
        enemy_debuff_count=1,
    )
    aggregation_calls = _patch_buff_aggregation(
        monkeypatch,
        {
            "固定暴击率": 0.1,
            "局内暴击率": 0.05,
            "被暴击几率增加": 0.25,
        },
    )

    reader = CalculatorBuffAttributeReader()
    full_crit_rate = reader.read_full_crit_rate(fixture.context)
    personal_crit_rate = reader.read_personal_crit_rate(fixture.context)

    assert full_crit_rate == pytest.approx(0.6)
    assert personal_crit_rate == pytest.approx(0.35)
    assert full_crit_rate - personal_crit_rate == pytest.approx(0.25)
    _assert_aggregation_calls(aggregation_calls, fixture, times=2)


@pytest.mark.parametrize(
    (
        "static_crit_damage",
        "field_crit_damage",
        "flat_crit_damage",
        "received_crit_damage",
        "char_buff_count",
        "enemy_debuff_count",
        "expected_personal",
    ),
    [
        pytest.param(0.5, 0.0, 0.0, 0.0, 1, 1, 0.5, id="baseline"),
        pytest.param(0.5, 0.4, 0.0, 0.0, 1, 1, 0.9, id="field-buff"),
        pytest.param(0.5, 0.0, 0.3, 0.0, 1, 1, 0.8, id="flat-buff"),
        pytest.param(
            0.5,
            0.0,
            0.0,
            0.2,
            0,
            1,
            0.5,
            id="received-enemy-debuff-excluded",
        ),
        pytest.param(0.75, 0.0, 0.0, 0.0, 0, 0, 0.75, id="no-buff"),
    ],
)
def test_p2b_parity_fixture_matches_old_personal_crit_damage_helper(
    monkeypatch: pytest.MonkeyPatch,
    static_crit_damage: float,
    field_crit_damage: float,
    flat_crit_damage: float,
    received_crit_damage: float,
    char_buff_count: int,
    enemy_debuff_count: int,
    expected_personal: float,
) -> None:
    MultiplierData.mul_data_cache.clear()
    fixture = _make_attribute_read_fixture(
        name="暴伤测试",
        crit_damage=static_crit_damage,
        char_buff_count=char_buff_count,
        enemy_debuff_count=enemy_debuff_count,
    )
    aggregation_calls = _patch_buff_aggregation(
        monkeypatch,
        {
            "局内暴击伤害": field_crit_damage,
            "固定暴击伤害": flat_crit_damage,
            "受暴击伤害增加": received_crit_damage,
        },
    )

    reader_value = CalculatorBuffAttributeReader().read_personal_crit_damage(
        fixture.context
    )
    reader_data = _reader_snapshot_data(fixture.context)
    old_value = _legacy_personal_crit_damage_oracle(fixture)

    assert reader_value == pytest.approx(old_value)
    assert reader_value == pytest.approx(expected_personal)
    assert cast(Any, reader_data).dynamic.received_crit_dmg_bonus == pytest.approx(
        received_crit_damage
    )
    _assert_aggregation_calls(aggregation_calls, fixture, times=3)


def test_p2b_personal_crit_damage_excludes_received_crit_damage_bonus(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    MultiplierData.mul_data_cache.clear()
    fixture = _make_attribute_read_fixture(
        name="受暴伤测试",
        crit_damage=0.5,
        enemy_debuff_count=1,
    )
    aggregation_calls = _patch_buff_aggregation(
        monkeypatch,
        {
            "固定暴击伤害": 0.3,
            "局内暴击伤害": 0.2,
            "受暴击伤害增加": 0.4,
        },
    )

    personal_crit_damage = CalculatorBuffAttributeReader().read_personal_crit_damage(
        fixture.context
    )
    reader_data = _reader_snapshot_data(fixture.context)

    assert personal_crit_damage == pytest.approx(1.0)
    assert cast(Any, reader_data).dynamic.received_crit_dmg_bonus == pytest.approx(0.4)
    _assert_aggregation_calls(aggregation_calls, fixture, times=2)


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
