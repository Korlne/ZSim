from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Sequence, cast

import pytest

import zsim.sim_progress.ScheduledEvent.Calculator as calculator_module
from zsim.sim_progress.Buff.BuffXLogic.AliceAdditionalAbilityApBonus import (
    AliceAdditionalAbilityApBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.YuzuhaAdditionalAbilityAnomalyBuildupBonus import (
    YuzuhaAdditionalAbilityAnomalyBuildupBonus,
)
from zsim.sim_progress.ScheduledEvent.Calculator import Calculator, MultiplierData

_AggregationCall = tuple[tuple[object, ...], object | None, object, str | None]


class _DynamicCountRecorder:
    def __init__(self, calls: list[tuple[Any, ...]], initial_count: float) -> None:
        self._calls = calls
        self._count = initial_count

    @property
    def count(self) -> float:
        return self._count

    @count.setter
    def count(self, value: float) -> None:
        self._calls.append(("dy.count", value))
        self._count = value


class _StateSyncBuffProbe:
    def __init__(
        self,
        *,
        index: str,
        tick: int,
        calls: list[tuple[Any, ...]],
        initial_count: float,
        maxcount: float = 999.0,
    ) -> None:
        self.ft = SimpleNamespace(index=index, maxcount=maxcount)
        self.dy = _DynamicCountRecorder(calls, initial_count)
        self.sim_instance = SimpleNamespace(tick=tick)
        self._calls = calls

    def simple_start(
        self,
        timenow: int,
        sub_exist_buff_dict: dict[str, object],
        **kwargs: object,
    ) -> None:
        no_count = bool(kwargs.get("no_count", False))
        self._calls.append(
            (
                "simple_start",
                timenow,
                no_count,
                self.dy.count,
                sub_exist_buff_dict[self.ft.index],
            )
        )
        if not no_count:
            self.dy.count = self.dy.count + 1

    def update_to_buff_0(self, buff_0: object) -> None:
        self._calls.append(("update_to_buff_0", buff_0, self.dy.count))
        cast(Any, buff_0).dy.count = self.dy.count


@dataclass(frozen=True)
class _AliceStateSyncCase:
    logic: Any
    active_buff: _StateSyncBuffProbe
    buff_0: Any
    calls: list[tuple[Any, ...]]
    get_prepared_calls: list[dict[str, object]]
    aggregation_calls: list[_AggregationCall]
    expected_enabled_buff: tuple[object, ...]
    expected_old_count: float | None


@dataclass(frozen=True)
class _YuzuhaStateSyncCase:
    logic: Any
    active_buff: _StateSyncBuffProbe
    buff_0: Any
    calls: list[tuple[Any, ...]]
    get_prepared_calls: list[dict[str, object]]
    aggregation_calls: list[_AggregationCall]
    expected_enabled_buff: tuple[object, ...]
    expected_old_count: float | None
    expected_cinema_1_ratio: float


def _make_alice_character(*, am: float) -> SimpleNamespace:
    statement = SimpleNamespace(statement={"AM": am}, AM=am)
    return SimpleNamespace(NAME="Alice", CID=1401, level=60, statement=statement)


def _make_yuzuha_character(*, am: float, cinema: int) -> SimpleNamespace:
    statement = SimpleNamespace(statement={"AM": am}, AM=am)
    return SimpleNamespace(NAME="Yuzuha", CID=1411, cinema=cinema, level=60, statement=statement)


def _make_enemy(
    *,
    sim_instance: object,
    enemy_debuffs: Sequence[object],
) -> SimpleNamespace:
    return SimpleNamespace(
        dynamic=SimpleNamespace(
            dynamic_debuff_list=list(enemy_debuffs),
            dynamic_dot_list=[],
        ),
        sim_instance=sim_instance,
    )


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


def _old_alice_count(
    *,
    enemy: SimpleNamespace,
    dynamic_buff_list: dict[str, list[object]],
    char: SimpleNamespace,
    trans_ratio: float,
) -> float | None:
    MultiplierData.mul_data_cache.clear()
    mul_data = MultiplierData(
        cast(Any, enemy),
        dynamic_buff_list,
        cast(Any, char),
    )
    am = Calculator.AnomalyMul.cal_am(mul_data)
    if am < 140:
        return None
    return float((am - 140) * trans_ratio)


def _old_yuzuha_buildup_count(
    *,
    enemy: SimpleNamespace,
    dynamic_buff_list: dict[str, list[object]],
    char: SimpleNamespace,
    cinema_1_ratio: float,
) -> float | None:
    MultiplierData.mul_data_cache.clear()
    mul_data = MultiplierData(
        cast(Any, enemy),
        dynamic_buff_list,
        cast(Any, char),
    )
    am = Calculator.AnomalyMul.cal_am(mul_data)
    if am < 100:
        return None
    return float(min(am - 100, 100) * cinema_1_ratio)


def _make_alice_state_sync_case(
    monkeypatch: pytest.MonkeyPatch,
    *,
    static_am: float,
    field_am: float = 0.0,
    flat_am: float = 0.0,
    initial_count: float = 123.0,
    maxcount: float = 999.0,
) -> _AliceStateSyncCase:
    calls: list[tuple[Any, ...]] = []
    active_buff = _StateSyncBuffProbe(
        index="alice-additional-ability-ap",
        tick=600,
        calls=calls,
        initial_count=initial_count,
        maxcount=maxcount,
    )
    char_buff = object()
    enemy_debuff = object()
    char = _make_alice_character(am=static_am)
    enemy = _make_enemy(
        sim_instance=active_buff.sim_instance,
        enemy_debuffs=(enemy_debuff,),
    )
    dynamic_buff_list = {char.NAME: [char_buff]}
    aggregation_calls = _patch_buff_aggregation(
        monkeypatch,
        {
            "局内异常掌控": field_am,
            "固定异常掌控": flat_am,
        },
    )
    buff_0 = SimpleNamespace(dy=SimpleNamespace(count=initial_count))
    sub_exist_buff_dict = {active_buff.ft.index: buff_0}
    trans_ratio = 1.6

    logic = cast(
        Any,
        AliceAdditionalAbilityApBonus.__new__(AliceAdditionalAbilityApBonus),
    )
    logic.buff_instance = active_buff
    logic.buff_0 = buff_0
    logic.record = SimpleNamespace(
        enemy=enemy,
        dynamic_buff_list=dynamic_buff_list,
        char=char,
        sub_exist_buff_dict=sub_exist_buff_dict,
        trans_ratio=trans_ratio,
    )
    logic.check_record_module = lambda: None

    get_prepared_calls: list[dict[str, object]] = []
    logic.get_prepared = lambda **kwargs: get_prepared_calls.append(kwargs)
    expected_old_count = _old_alice_count(
        enemy=enemy,
        dynamic_buff_list=dynamic_buff_list,
        char=char,
        trans_ratio=trans_ratio,
    )
    return _AliceStateSyncCase(
        logic=logic,
        active_buff=active_buff,
        buff_0=buff_0,
        calls=calls,
        get_prepared_calls=get_prepared_calls,
        aggregation_calls=aggregation_calls,
        expected_enabled_buff=(char_buff, enemy_debuff),
        expected_old_count=expected_old_count,
    )


def _make_yuzuha_state_sync_case(
    monkeypatch: pytest.MonkeyPatch,
    *,
    static_am: float,
    cinema: int,
    field_am: float = 0.0,
    flat_am: float = 0.0,
    initial_count: float = 88.0,
) -> _YuzuhaStateSyncCase:
    calls: list[tuple[Any, ...]] = []
    active_buff = _StateSyncBuffProbe(
        index="yuzuha-additional-ability-anomaly-buildup",
        tick=700,
        calls=calls,
        initial_count=initial_count,
    )
    char_buff = object()
    enemy_debuff = object()
    char = _make_yuzuha_character(am=static_am, cinema=cinema)
    enemy = _make_enemy(
        sim_instance=active_buff.sim_instance,
        enemy_debuffs=(enemy_debuff,),
    )
    dynamic_buff_list = {char.NAME: [char_buff]}
    aggregation_calls = _patch_buff_aggregation(
        monkeypatch,
        {
            "局内异常掌控": field_am,
            "固定异常掌控": flat_am,
        },
    )
    buff_0 = SimpleNamespace(dy=SimpleNamespace(count=initial_count))
    sub_exist_buff_dict = {active_buff.ft.index: buff_0}
    expected_cinema_1_ratio = 1.0 if cinema < 1 else 1.3

    logic = cast(
        Any,
        YuzuhaAdditionalAbilityAnomalyBuildupBonus.__new__(
            YuzuhaAdditionalAbilityAnomalyBuildupBonus
        ),
    )
    logic.buff_instance = active_buff
    logic.buff_0 = buff_0
    logic.record = SimpleNamespace(
        enemy=enemy,
        dynamic_buff_list=dynamic_buff_list,
        char=char,
        sub_exist_buff_dict=sub_exist_buff_dict,
        cinema_1_ratio=None,
    )
    logic.check_record_module = lambda: None

    get_prepared_calls: list[dict[str, object]] = []
    logic.get_prepared = lambda **kwargs: get_prepared_calls.append(kwargs)
    expected_old_count = _old_yuzuha_buildup_count(
        enemy=enemy,
        dynamic_buff_list=dynamic_buff_list,
        char=char,
        cinema_1_ratio=expected_cinema_1_ratio,
    )
    return _YuzuhaStateSyncCase(
        logic=logic,
        active_buff=active_buff,
        buff_0=buff_0,
        calls=calls,
        get_prepared_calls=get_prepared_calls,
        aggregation_calls=aggregation_calls,
        expected_enabled_buff=(char_buff, enemy_debuff),
        expected_old_count=expected_old_count,
        expected_cinema_1_ratio=expected_cinema_1_ratio,
    )


def test_count_state_sync_preserves_simple_start_assignment_update_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _make_alice_state_sync_case(
        monkeypatch,
        static_am=145.0,
    )

    case.logic.special_judge_logic()

    assert case.expected_old_count == pytest.approx(8.0)
    assert case.get_prepared_calls == [
        {"char_CID": 1401, "sub_exist_buff_dict": 1, "enemy": 1, "dynamic_buff_list": 1}
    ]
    assert case.aggregation_calls == [
        (case.expected_enabled_buff, None, case.active_buff.sim_instance, "Alice"),
        (case.expected_enabled_buff, None, case.active_buff.sim_instance, "Alice"),
    ]
    assert case.calls == [
        ("simple_start", 600, True, 123.0, case.buff_0),
        ("dy.count", case.expected_old_count),
        ("update_to_buff_0", case.buff_0, case.expected_old_count),
    ]
    assert case.active_buff.dy.count == pytest.approx(case.expected_old_count)
    assert case.buff_0.dy.count == pytest.approx(case.expected_old_count)


def test_count_state_sync_skips_writeback_below_am_threshold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _make_alice_state_sync_case(
        monkeypatch,
        static_am=139.99,
    )

    result = case.logic.special_judge_logic()

    assert result is None
    assert case.expected_old_count is None
    assert case.get_prepared_calls == [
        {"char_CID": 1401, "sub_exist_buff_dict": 1, "enemy": 1, "dynamic_buff_list": 1}
    ]
    assert case.aggregation_calls == [
        (case.expected_enabled_buff, None, case.active_buff.sim_instance, "Alice"),
        (case.expected_enabled_buff, None, case.active_buff.sim_instance, "Alice"),
    ]
    assert case.calls == []
    assert case.active_buff.dy.count == pytest.approx(123.0)
    assert case.buff_0.dy.count == pytest.approx(123.0)


def test_alice_reader_path_matches_old_count_for_high_am_source_behavior(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _make_alice_state_sync_case(
        monkeypatch,
        static_am=800.0,
        maxcount=999.0,
    )

    case.logic.special_judge_logic()

    assert case.expected_old_count == pytest.approx((800.0 - 140.0) * 1.6)
    assert case.expected_old_count > case.active_buff.ft.maxcount
    assert case.calls == [
        ("simple_start", 600, True, 123.0, case.buff_0),
        ("dy.count", case.expected_old_count),
        ("update_to_buff_0", case.buff_0, case.expected_old_count),
    ]
    assert case.active_buff.dy.count == pytest.approx(case.expected_old_count)
    assert case.buff_0.dy.count == pytest.approx(case.expected_old_count)


def test_yuzuha_buildup_skips_writeback_below_am_threshold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _make_yuzuha_state_sync_case(
        monkeypatch,
        static_am=99.99,
        cinema=0,
    )

    result = case.logic.special_hit_logic()

    assert result is None
    assert case.expected_old_count is None
    assert case.logic.record.cinema_1_ratio == pytest.approx(case.expected_cinema_1_ratio)
    assert case.get_prepared_calls == [
        {"char_CID": 1411, "sub_exist_buff_dict": 1, "enemy": 1, "dynamic_buff_list": 1}
    ]
    assert case.aggregation_calls == [
        (case.expected_enabled_buff, None, case.active_buff.sim_instance, "Yuzuha"),
        (case.expected_enabled_buff, None, case.active_buff.sim_instance, "Yuzuha"),
    ]
    assert case.calls == []
    assert case.active_buff.dy.count == pytest.approx(88.0)
    assert case.buff_0.dy.count == pytest.approx(88.0)


def test_yuzuha_buildup_reader_path_matches_old_count_for_cinema_zero_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _make_yuzuha_state_sync_case(
        monkeypatch,
        static_am=145.0,
        cinema=0,
    )

    case.logic.special_hit_logic()

    assert case.expected_old_count == pytest.approx(45.0)
    assert case.logic.record.cinema_1_ratio == pytest.approx(1.0)
    assert case.get_prepared_calls == [
        {"char_CID": 1411, "sub_exist_buff_dict": 1, "enemy": 1, "dynamic_buff_list": 1}
    ]
    assert case.aggregation_calls == [
        (case.expected_enabled_buff, None, case.active_buff.sim_instance, "Yuzuha"),
        (case.expected_enabled_buff, None, case.active_buff.sim_instance, "Yuzuha"),
    ]
    assert case.calls == [
        ("simple_start", 700, True, 88.0, case.buff_0),
        ("dy.count", case.expected_old_count),
        ("update_to_buff_0", case.buff_0, case.expected_old_count),
    ]
    assert case.active_buff.dy.count == pytest.approx(case.expected_old_count)
    assert case.buff_0.dy.count == pytest.approx(case.expected_old_count)


def test_yuzuha_buildup_reader_path_matches_old_count_for_cinema_one_plus_cap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _make_yuzuha_state_sync_case(
        monkeypatch,
        static_am=250.0,
        cinema=1,
    )

    case.logic.special_hit_logic()

    assert case.expected_old_count == pytest.approx(130.0)
    assert case.logic.record.cinema_1_ratio == pytest.approx(1.3)
    assert case.get_prepared_calls == [
        {"char_CID": 1411, "sub_exist_buff_dict": 1, "enemy": 1, "dynamic_buff_list": 1}
    ]
    assert case.aggregation_calls == [
        (case.expected_enabled_buff, None, case.active_buff.sim_instance, "Yuzuha"),
        (case.expected_enabled_buff, None, case.active_buff.sim_instance, "Yuzuha"),
    ]
    assert case.calls == [
        ("simple_start", 700, True, 88.0, case.buff_0),
        ("dy.count", case.expected_old_count),
        ("update_to_buff_0", case.buff_0, case.expected_old_count),
    ]
    assert case.active_buff.dy.count == pytest.approx(case.expected_old_count)
    assert case.buff_0.dy.count == pytest.approx(case.expected_old_count)


def test_alice_additional_ability_uses_reader_not_multiplier_data() -> None:
    source = Path(
        "zsim/sim_progress/Buff/BuffXLogic/AliceAdditionalAbilityApBonus.py"
    ).read_text(encoding="utf-8")

    assert "MultiplierData" not in source
    assert "Calculator.AnomalyMul.cal_am" not in source
    assert "create_anomaly_attribute_read_context" in source
    assert "read_anomaly_mastery" in source


def test_yuzuha_buildup_uses_reader_not_multiplier_data() -> None:
    source = Path(
        "zsim/sim_progress/Buff/BuffXLogic/YuzuhaAdditionalAbilityAnomalyBuildupBonus.py"
    ).read_text(encoding="utf-8")

    assert "MultiplierData" not in source
    assert "Calculator.AnomalyMul.cal_am" not in source
    assert "create_anomaly_attribute_read_context" in source
    assert "read_anomaly_mastery" in source
