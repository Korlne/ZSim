from __future__ import annotations

from dataclasses import dataclass
import inspect
from types import SimpleNamespace
from typing import Any, Iterator, Sequence, cast

import numpy as np
import pytest

import zsim.sim_progress.ScheduledEvent.CalAnomaly as cal_anomaly_module
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
from zsim.sim_progress.anomaly_bar import AnomalyBar
from zsim.sim_progress.anomaly_bar.CopyAnomalyForOutput import (
    DirgeOfDestinyAnomaly,
    NewAnomaly,
)

_AggregationCall = tuple[tuple[object, ...], object | None, object, str | None]


@dataclass(frozen=True)
class _AttributeReadFixture:
    context: BuffAttributeReadContext
    active_buff_view: dict[str, list[object]]
    enemy: SimpleNamespace
    char: SimpleNamespace
    expected_enabled_buff: tuple[object, ...]
    expected_enemy_dot_buff: tuple[object, ...] = ()


@dataclass(frozen=True)
class _AnomalyFormulaFixture:
    sim_instance: SimpleNamespace
    character: SimpleNamespace
    activation: SimpleNamespace
    enemy: SimpleNamespace
    active_buff_view: dict[str, list[object]]
    source_snapshot: np.ndarray
    anomaly_bar: AnomalyBar


@pytest.fixture(autouse=True)
def _reset_formula_fixture_state() -> Iterator[None]:
    MultiplierData.mul_data_cache.clear()
    MultiplierData.StaticStatement._instance_cache.clear()
    yield
    MultiplierData.mul_data_cache.clear()
    MultiplierData.StaticStatement._instance_cache.clear()


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


def _make_enemy(
    enemy_debuffs: Sequence[object] = (),
    enemy_dots: Sequence[object] = (),
) -> SimpleNamespace:
    return SimpleNamespace(
        dynamic=SimpleNamespace(
            dynamic_debuff_list=list(enemy_debuffs),
            dynamic_dot_list=list(enemy_dots),
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
    enemy_dot_count: int = 0,
) -> _AttributeReadFixture:
    char_buffs = tuple(object() for _ in range(char_buff_count))
    enemy_debuffs = tuple(object() for _ in range(enemy_debuff_count))
    enemy_dots = tuple(object() for _ in range(enemy_dot_count))
    char = _make_character(
        name=name,
        am=am,
        ap=ap,
        imp=imp,
        crit_rate=crit_rate,
        crit_damage=crit_damage,
    )
    enemy = _make_enemy(enemy_debuffs, enemy_dots)
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
        expected_enemy_dot_buff=enemy_dots,
    )


def _make_anomaly_snapshot(values: Sequence[float] | None = None) -> np.ndarray:
    if values is None:
        values = (
            100.0,
            1.10,
            2.0,
            60.0,
            1.30,
            999.0,
            0.05,
            8.0,
            0.10,
            1.20,
            1.40,
        )
    return np.array([list(values)], dtype=np.float64)


def _make_settled_anomaly_formula_fixture(
    *,
    character_name: str = "异常公式角色",
    snapshot: np.ndarray | None = None,
    scaling_factor: float = 1.25,
) -> _AnomalyFormulaFixture:
    source_snapshot = _make_anomaly_snapshot() if snapshot is None else snapshot
    sim_instance = SimpleNamespace(tick=321)
    character = SimpleNamespace(NAME=character_name)
    activation = SimpleNamespace(skill=SimpleNamespace(char_obj=character))
    enemy = _make_enemy()
    active_buff_view: dict[str, list[object]] = {character.NAME: []}
    anomaly_bar = AnomalyBar(sim_instance=cast(Any, sim_instance), element_type=0)
    anomaly_bar.current_ndarray = np.array(source_snapshot, dtype=np.float64, copy=True)
    anomaly_bar.current_effective_anomaly = np.float64(30.0)
    anomaly_bar.current_anomaly = np.float64(129.0)
    anomaly_bar.settled = True
    anomaly_bar.activated_by = cast(Any, activation)
    anomaly_bar.scaling_factor = scaling_factor
    return _AnomalyFormulaFixture(
        sim_instance=sim_instance,
        character=character,
        activation=activation,
        enemy=enemy,
        active_buff_view=active_buff_view,
        source_snapshot=source_snapshot,
        anomaly_bar=anomaly_bar,
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


def test_formula_parity_fixture_builds_independent_calculator_inputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _make_attribute_read_fixture(
        name="公式夹具角色",
        am=100.0,
        ap=300.0,
        imp=80.0,
        crit_rate=0.2,
        crit_damage=0.5,
        char_buff_count=2,
        enemy_debuff_count=1,
        enemy_dot_count=2,
    )
    aggregation_calls = _patch_buff_aggregation(
        monkeypatch,
        {
            "局内异常掌控": 0.2,
            "固定异常精通": 30.0,
            "局内冲击力%": 0.1,
        },
    )

    data = _legacy_multiplier_data(fixture)
    reader_data = _reader_snapshot_data(fixture.context)

    assert fixture.char.statement.AM == pytest.approx(100.0)
    assert fixture.char.statement.AP == pytest.approx(300.0)
    assert len(fixture.active_buff_view[fixture.char.NAME]) == 2
    assert tuple(fixture.enemy.dynamic.dynamic_debuff_list) == (
        fixture.expected_enabled_buff[2:]
    )
    assert (
        tuple(fixture.enemy.dynamic.dynamic_dot_list)
        == fixture.expected_enemy_dot_buff
    )
    assert data.dynamic.field_anomaly_mastery == pytest.approx(0.2)
    assert data.dynamic.anomaly_proficiency == pytest.approx(30.0)
    assert reader_data.dynamic.field_imp_percentage == pytest.approx(0.1)
    _assert_aggregation_calls(aggregation_calls, fixture, times=2)

    data.dynamic.anomaly_proficiency = -999.0
    fixture.active_buff_view[fixture.char.NAME].append(object())
    fixture.enemy.dynamic.dynamic_debuff_list.append(object())
    fixture.enemy.dynamic.dynamic_dot_list.append(object())

    next_fixture = _make_attribute_read_fixture(
        name="公式夹具角色",
        am=100.0,
        ap=300.0,
        imp=80.0,
        crit_rate=0.2,
        crit_damage=0.5,
        char_buff_count=2,
        enemy_debuff_count=1,
        enemy_dot_count=2,
    )
    next_data = _legacy_multiplier_data(next_fixture)

    assert next_data is not data
    assert len(next_fixture.active_buff_view[next_fixture.char.NAME]) == 2
    assert len(next_fixture.enemy.dynamic.dynamic_debuff_list) == 1
    assert len(next_fixture.enemy.dynamic.dynamic_dot_list) == 2
    assert next_data.dynamic.anomaly_proficiency == pytest.approx(30.0)


def test_anomaly_formula_fixture_copies_snapshot_inputs_for_copied_output() -> None:
    source_snapshot = _make_anomaly_snapshot(
        (210.0, 1.20, 3.0, 60.0, 1.50, 999.0, 0.15, 5.0, 0.20, 1.30, 1.70)
    )
    original_snapshot = source_snapshot.copy()
    fixture = _make_settled_anomaly_formula_fixture(snapshot=source_snapshot)

    assert fixture.anomaly_bar.current_ndarray is not source_snapshot
    np.testing.assert_allclose(fixture.anomaly_bar.current_ndarray, original_snapshot)

    copied = NewAnomaly(
        fixture.anomaly_bar,
        active_by=cast(Any, fixture.activation),
        sim_instance=cast(Any, SimpleNamespace(tick=322)),
    )

    source_snapshot[0, 0] = -111.0
    assert fixture.anomaly_bar.current_ndarray[0, 0] == pytest.approx(
        original_snapshot[0, 0]
    )
    fixture.anomaly_bar.current_ndarray[0, 0] = -222.0
    assert copied.current_ndarray[0, 0] == pytest.approx(original_snapshot[0, 0])

    next_fixture = _make_settled_anomaly_formula_fixture()
    assert next_fixture.anomaly_bar.current_ndarray[0, 0] == pytest.approx(100.0)


@pytest.mark.parametrize(
    (
        "char_buff_count",
        "enemy_debuff_count",
        "dynamic_statement",
        "expected_fields",
    ),
    [
        pytest.param(
            0,
            0,
            {},
            {
                "field_anomaly_mastery": 0.0,
                "anomaly_mastery": 0.0,
                "field_anomaly_proficiency": 0.0,
                "anomaly_proficiency": 0.0,
                "crit_rate": 0.0,
            },
            id="no-buff-no-debuff",
        ),
        pytest.param(
            2,
            1,
            {
                "局内异常掌控": 0.25,
                "固定异常掌控": 12.0,
                "局内异常精通": 0.15,
                "固定异常精通": 35.0,
            },
            {
                "field_anomaly_mastery": 0.25,
                "anomaly_mastery": 12.0,
                "field_anomaly_proficiency": 0.15,
                "anomaly_proficiency": 35.0,
                "crit_rate": 0.0,
            },
            id="active-buff-enemy-debuff",
        ),
    ],
)
def test_multiplier_data_get_buff_bonus_builds_dynamic_statement_snapshot(
    monkeypatch: pytest.MonkeyPatch,
    char_buff_count: int,
    enemy_debuff_count: int,
    dynamic_statement: dict[str, float],
    expected_fields: dict[str, float],
) -> None:
    MultiplierData.mul_data_cache.clear()
    fixture = _make_attribute_read_fixture(
        char_buff_count=char_buff_count,
        enemy_debuff_count=enemy_debuff_count,
    )
    aggregation_calls = _patch_buff_aggregation(monkeypatch, dynamic_statement)

    data = _legacy_multiplier_data(fixture)
    raw_statement = data.get_buff_bonus(
        fixture.active_buff_view,
        fixture.context.query_node,
    )

    assert raw_statement == dynamic_statement
    for attr_name, expected_value in expected_fields.items():
        assert getattr(data.dynamic, attr_name) == pytest.approx(expected_value)
    assert data.dynamic.ano_extra_bonus["all"] == pytest.approx(0.0)
    _assert_aggregation_calls(aggregation_calls, fixture, times=2)


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


def test_calculator_attribute_formula_boundaries_remain_retained_compatibility(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    MultiplierData.mul_data_cache.clear()
    fixture = _make_attribute_read_fixture(
        name="公式边界测试",
        am=100.0,
        ap=300.0,
        imp=80.0,
        crit_rate=0.2,
        crit_damage=0.5,
        char_buff_count=1,
        enemy_debuff_count=1,
    )
    aggregation_calls = _patch_buff_aggregation(
        monkeypatch,
        {
            "局内异常掌控": 0.2,
            "固定异常掌控": 15.0,
            "局内异常精通": 0.25,
            "固定异常精通": 40.0,
            "局内冲击力%": 0.1,
            "固定冲击力": 9.0,
            "固定暴击率": 0.1,
            "局内暴击率": 0.05,
            "被暴击几率增加": 0.25,
            "固定暴击伤害": 0.3,
            "局内暴击伤害": 0.2,
            "受暴击伤害增加": 0.4,
        },
    )

    retained_data = _legacy_multiplier_data(fixture)
    formula_boundaries = {
        "cal_am": Calculator.AnomalyMul.cal_am(retained_data),
        "cal_ap": Calculator.AnomalyMul.cal_ap(retained_data),
        "cal_imp": Calculator.StunMul.cal_imp(retained_data),
        "cal_crit_rate": Calculator.RegularMul.cal_crit_rate(retained_data),
        "cal_personal_crit_rate": Calculator.RegularMul.cal_personal_crit_rate(
            retained_data
        ),
        "cal_personal_crit_dmg": Calculator.RegularMul.cal_personal_crit_dmg(
            retained_data
        ),
    }
    expected_boundaries = {
        "cal_am": 135.0,
        "cal_ap": 415.0,
        "cal_imp": 97.0,
        "cal_crit_rate": 0.6,
        "cal_personal_crit_rate": 0.35,
        "cal_personal_crit_dmg": 1.0,
    }

    reader = CalculatorBuffAttributeReader()
    reader_values = {
        "cal_am": reader.read_anomaly_mastery(fixture.context),
        "cal_ap": reader.read_anomaly_proficiency(fixture.context),
        "cal_imp": reader.read_impact(fixture.context),
        "cal_crit_rate": reader.read_full_crit_rate(fixture.context),
        "cal_personal_crit_rate": reader.read_personal_crit_rate(fixture.context),
        "cal_personal_crit_dmg": reader.read_personal_crit_damage(fixture.context),
    }

    assert formula_boundaries == pytest.approx(expected_boundaries)
    # P2-A/P2-B reader parity 只是兼容性证据，不能作为删除 Calculator 公式的依据。
    assert reader_values == pytest.approx(formula_boundaries)
    assert (
        formula_boundaries["cal_crit_rate"]
        - formula_boundaries["cal_personal_crit_rate"]
    ) == pytest.approx(0.25)
    assert cast(Any, retained_data).dynamic.received_crit_dmg_bonus == pytest.approx(
        0.4
    )
    _assert_aggregation_calls(aggregation_calls, fixture, times=7)


def test_anomaly_bar_settlement_and_copied_snapshot_inputs_remain_retained_compatibility() -> None:
    sim_instance = SimpleNamespace(tick=120)
    bar = AnomalyBar(sim_instance=cast(Any, sim_instance), element_type=0)
    first_snapshot = np.array(
        [[100.0, 1.10, 2.0, 60.0, 1.30, 0.0, 0.05, 8.0, 0.10, 1.20, 1.40]],
        dtype=np.float64,
    )
    second_snapshot = np.array(
        [[200.0, 1.40, 3.0, 50.0, 1.60, 0.0, 0.15, 4.0, 0.20, 1.60, 1.80]],
        dtype=np.float64,
    )
    ineffective_snapshot: np.ndarray = np.full((1, 11), 999.0, dtype=np.float64)
    effective_hit = SimpleNamespace(effective_anomlay_buildup=lambda: True)
    ineffective_hit = SimpleNamespace(effective_anomlay_buildup=lambda: False)

    bar.update_snap_shot(
        (0, np.float64(20.0), first_snapshot),
        cast(Any, effective_hit),
    )
    bar.update_snap_shot(
        (0, np.float64(10.0), second_snapshot),
        cast(Any, effective_hit),
    )
    bar.update_snap_shot(
        (0, np.float64(99.0), ineffective_snapshot),
        cast(Any, ineffective_hit),
    )

    assert bar.current_anomaly == pytest.approx(129.0)
    assert len(cast(list[tuple[Any, ...]], bar.ndarray_box)) == 2

    bar.anomaly_settled()

    expected_snapshot = ((first_snapshot * 20.0) + (second_snapshot * 10.0)) / 30.0
    assert bar.settled is True
    assert bar.current_effective_anomaly == pytest.approx(30.0)
    assert bar.ndarray_box == []
    np.testing.assert_allclose(bar.current_ndarray, expected_snapshot)

    activation = SimpleNamespace(
        skill=SimpleNamespace(char_obj=SimpleNamespace(NAME="快照角色"))
    )
    copied = NewAnomaly(
        bar,
        active_by=cast(Any, activation),
        sim_instance=cast(Any, SimpleNamespace(tick=121)),
    )

    assert copied.current_ndarray is not bar.current_ndarray
    np.testing.assert_allclose(copied.current_ndarray, expected_snapshot)
    bar.current_ndarray[0, 0] = -999.0
    assert copied.current_ndarray[0, 0] == pytest.approx(expected_snapshot[0, 0])
    assert copied.activated_by is activation


def test_cal_anomaly_uses_settled_snapshot_mul_data_and_retained_damage_ratios(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created_mul_data: list[Any] = []

    class _MulDataProbe:
        def __init__(
            self,
            *,
            enemy_obj: object,
            dynamic_buff: object,
            judge_node: object,
            character_obj: object,
        ) -> None:
            self.enemy_obj = enemy_obj
            self.dynamic_buff = dynamic_buff
            self.judge_node = judge_node
            self.character_obj = character_obj
            self.dynamic = SimpleNamespace(
                strike_crit_rate_increase=0.25,
                strike_crit_dmg_increase=0.4,
            )
            created_mul_data.append(self)

    monkeypatch.setattr(cal_anomaly_module, "MulData", _MulDataProbe)
    monkeypatch.setattr(
        cal_anomaly_module.CalAnomaly,
        "cal_def_mul",
        lambda self, data, v_char_level: np.float64(0.5),
    )
    monkeypatch.setattr(
        cal_anomaly_module.Cal.RegularMul,
        "cal_res_mul",
        staticmethod(lambda data, *, element_type, snapshot_res_pen: np.float64(0.7)),
    )
    monkeypatch.setattr(
        cal_anomaly_module.Cal.RegularMul,
        "cal_dmg_vulnerability",
        staticmethod(lambda data, *, element_type: np.float64(0.9)),
    )
    monkeypatch.setattr(
        cal_anomaly_module.Cal.RegularMul,
        "cal_stun_vulnerability",
        staticmethod(lambda data: np.float64(0.8)),
    )
    monkeypatch.setattr(
        cal_anomaly_module.Cal.RegularMul,
        "cal_special_mul",
        staticmethod(lambda data: np.float64(1.2)),
    )

    anomaly_fixture = _make_settled_anomaly_formula_fixture()
    sim_instance = anomaly_fixture.sim_instance
    character = anomaly_fixture.character
    activation = anomaly_fixture.activation
    enemy = anomaly_fixture.enemy
    active_buff_view = anomaly_fixture.active_buff_view
    anomaly_bar = anomaly_fixture.anomaly_bar
    settled_snapshot = anomaly_bar.current_ndarray

    calculator = cal_anomaly_module.CalAnomaly(
        anomaly_obj=anomaly_bar,
        enemy_obj=cast(Any, enemy),
        dynamic_buff=active_buff_view,
        sim_instance=cast(Any, sim_instance),
    )

    expected_multipliers = np.array(
        [
            100.0,
            1.10,
            2.0,
            2.0,
            1.30,
            1.10,
            0.5,
            0.7,
            0.9,
            1.20,
            1.40,
            0.8,
            1.2,
        ],
        dtype=np.float64,
    )
    assert len(created_mul_data) == 1
    assert created_mul_data[0].judge_node is anomaly_bar
    assert created_mul_data[0].dynamic_buff is active_buff_view
    assert created_mul_data[0].character_obj is character
    assert calculator.dmg_sp is anomaly_bar.current_ndarray
    np.testing.assert_allclose(calculator.final_multipliers, expected_multipliers)
    assert calculator.cal_anomaly_dmg() == pytest.approx(
        np.prod(expected_multipliers)
        / (settled_snapshot[0, 9] * settled_snapshot[0, 10])
        * anomaly_bar.scaling_factor
    )

    abloom = DirgeOfDestinyAnomaly(
        anomaly_bar,
        active_by=cast(Any, activation),
        sim_instance=cast(Any, sim_instance),
    )
    abloom.anomaly_dmg_ratio = 1.3
    abloom.scaling_factor = 1.0
    created_mul_data.clear()

    abloom_calculator = cal_anomaly_module.CalAbloom(
        abloom_obj=abloom,
        enemy_obj=cast(Any, enemy),
        dynamic_buff=active_buff_view,
        sim_instance=cast(Any, sim_instance),
    )

    expected_abloom_multipliers = expected_multipliers.copy()
    expected_abloom_multipliers[0] *= abloom.anomaly_dmg_ratio
    assert len(created_mul_data) == 1
    assert created_mul_data[0].judge_node is abloom
    assert abloom_calculator.dmg_sp is abloom.current_ndarray
    np.testing.assert_allclose(
        abloom_calculator.final_multipliers,
        expected_abloom_multipliers,
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
