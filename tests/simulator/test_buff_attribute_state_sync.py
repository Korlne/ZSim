from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest

import zsim.sim_progress.ScheduledEvent.Calculator as calculator_module
from zsim.sim_progress.Buff.BuffXLogic.AliceAdditionalAbilityApBonus import (
    AliceAdditionalAbilityApBonus,
)


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
    ) -> None:
        self.ft = SimpleNamespace(index=index, maxcount=999)
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


class _MultiplierDataProbe:
    def __init__(self, **kwargs: object) -> None:
        self.kwargs = kwargs


def _make_alice_state_sync_case(
    monkeypatch: pytest.MonkeyPatch,
    *,
    anomaly_mastery: float,
    initial_count: float = 123.0,
) -> tuple[Any, _StateSyncBuffProbe, Any, list[tuple[Any, ...]], list[dict[str, object]]]:
    monkeypatch.setattr(calculator_module, "MultiplierData", _MultiplierDataProbe)
    monkeypatch.setattr(
        calculator_module.Calculator.AnomalyMul,
        "cal_am",
        staticmethod(lambda data: anomaly_mastery),
    )

    calls: list[tuple[Any, ...]] = []
    active_buff = _StateSyncBuffProbe(
        index="alice-additional-ability-ap",
        tick=600,
        calls=calls,
        initial_count=initial_count,
    )
    buff_0 = SimpleNamespace(dy=SimpleNamespace(count=initial_count))
    sub_exist_buff_dict = {active_buff.ft.index: buff_0}

    logic = cast(
        Any,
        AliceAdditionalAbilityApBonus.__new__(AliceAdditionalAbilityApBonus),
    )
    logic.buff_instance = active_buff
    logic.buff_0 = buff_0
    logic.record = SimpleNamespace(
        enemy=SimpleNamespace(name="enemy"),
        dynamic_buff_list={"Alice": []},
        char=SimpleNamespace(NAME="Alice"),
        sub_exist_buff_dict=sub_exist_buff_dict,
        trans_ratio=1.6,
    )
    logic.check_record_module = lambda: None

    get_prepared_calls: list[dict[str, object]] = []
    logic.get_prepared = lambda **kwargs: get_prepared_calls.append(kwargs)
    return logic, active_buff, buff_0, calls, get_prepared_calls


def test_count_state_sync_preserves_simple_start_assignment_update_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    logic, active_buff, buff_0, calls, get_prepared_calls = _make_alice_state_sync_case(
        monkeypatch,
        anomaly_mastery=145.0,
    )

    logic.special_judge_logic()

    computed_count = (145.0 - 140.0) * 1.6
    assert get_prepared_calls == [
        {"char_CID": 1401, "sub_exist_buff_dict": 1, "enemy": 1, "dynamic_buff_list": 1}
    ]
    assert calls == [
        ("simple_start", 600, True, 123.0, buff_0),
        ("dy.count", computed_count),
        ("update_to_buff_0", buff_0, computed_count),
    ]
    assert active_buff.dy.count == pytest.approx(computed_count)
    assert buff_0.dy.count == pytest.approx(computed_count)


def test_count_state_sync_skips_writeback_below_am_threshold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    logic, active_buff, buff_0, calls, get_prepared_calls = _make_alice_state_sync_case(
        monkeypatch,
        anomaly_mastery=139.99,
    )

    result = logic.special_judge_logic()

    assert result is None
    assert get_prepared_calls == [
        {"char_CID": 1401, "sub_exist_buff_dict": 1, "enemy": 1, "dynamic_buff_list": 1}
    ]
    assert calls == []
    assert active_buff.dy.count == pytest.approx(123.0)
    assert buff_0.dy.count == pytest.approx(123.0)
