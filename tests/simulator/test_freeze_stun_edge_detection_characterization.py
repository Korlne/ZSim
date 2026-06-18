from __future__ import annotations

import sys
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Callable

import pytest
import zsim.define as define_module

sys.modules.setdefault("define", define_module)

from zsim.sim_progress.Buff.BuffXLogic import (  # noqa: E402
    BranchBladeSongCritRateBonus as branch_module,
)
from zsim.sim_progress.Buff.BuffXLogic import WeepingGeminiApBonus as weeping_module  # noqa: E402
from zsim.sim_progress.Buff.BuffXLogic import (  # noqa: E402
    LighterUniqueSkillStunTimeLimitBonus as lighter_module,
)
from zsim.sim_progress.Buff.BuffXLogic import PolarMetalFreezeBonus as polar_module  # noqa: E402
from zsim.sim_progress.Buff.BuffXLogic.BranchBladeSongCritRateBonus import (  # noqa: E402
    BranchBladeSongCritRateBonus,
    BranchBladeSongCritRateBonusRecord,
)
from zsim.sim_progress.Buff.BuffXLogic.LighterUniqueSkillStunTimeLimitBonus import (  # noqa: E402
    LighterUniqueSkillStunTimeLimitBonus,
    LighterUniqueSkillStunTimeRecord,
)
from zsim.sim_progress.Buff.BuffXLogic.PolarMetalFreezeBonus import (  # noqa: E402
    PolarMetalFreezeBonus,
    PolarMetalRecord,
)
from zsim.sim_progress.Buff.BuffXLogic.WeepingGeminiApBonus import (  # noqa: E402
    WeepingGeminiApBonus,
    WeepingGeminiApBonusRecord,
)
from zsim.sim_progress.anomaly_bar import AnomalyBar  # noqa: E402


class _FailFastRuntimeCommandPort:
    def __getattr__(self, name: str) -> Callable[..., None]:
        def _fail(*args: object, **kwargs: object) -> None:
            raise AssertionError(
                f"edge-detection characterization must not touch runtime writes: {name}"
            )

        return _fail


class _FailFastListenerManager:
    def broadcast_event(self, *args: object, **kwargs: object) -> None:
        raise AssertionError("edge-detection characterization must not broadcast listeners")


class _FailFastEventList(list[object]):
    def append(self, item: object) -> None:
        raise AssertionError("edge-detection characterization must not publish events")


class _BuffTemplate:
    def __init__(self, *, index: str) -> None:
        self.ft = SimpleNamespace(index=index)
        self.dy = SimpleNamespace(count=0.0)
        self.history = SimpleNamespace(record=None)


class _CurrentBuffProbe:
    def __init__(self, *, index: str, tick: int) -> None:
        runtime_command_port = _FailFastRuntimeCommandPort()
        self.ft = SimpleNamespace(index=index)
        self.dy = SimpleNamespace(count=0.0)
        self.simple_start_calls: list[tuple[int, dict[str, object]]] = []
        self.simple_exit_calls: list[tuple[object, ...]] = []
        self.update_to_buff_0_calls: list[object] = []
        self.sim_instance = SimpleNamespace(
            tick=tick,
            listener_manager=_FailFastListenerManager(),
            load_data=SimpleNamespace(runtime_command_port=runtime_command_port),
            schedule_data=SimpleNamespace(
                event_list=_FailFastEventList(),
                runtime_command_port=runtime_command_port,
            ),
            runtime_command_port=runtime_command_port,
        )

    def simple_start(
        self,
        timenow: int,
        sub_exist_buff_dict: dict[str, object],
        **kwargs: object,
    ) -> None:
        self.simple_start_calls.append((timenow, sub_exist_buff_dict))

    def simple_exit(self, *args: object, **kwargs: object) -> None:
        self.simple_exit_calls.append(args)

    def update_to_buff_0(self, buff_0: object) -> None:
        self.update_to_buff_0_calls.append(buff_0)


@dataclass(frozen=True)
class _EdgeFixture:
    logic: Any
    active_buff: _CurrentBuffProbe
    buff_0: _BuffTemplate
    enemy: Any
    prepared_calls: list[dict[str, object]]


def _install_owner_lookup(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    owner: str,
    index: str,
    buff_0: _BuffTemplate,
    equipper: str | None = None,
) -> list[object]:
    lookup_calls: list[object] = []

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        lookup_calls.append(sim_instance)
        return {owner: {index: buff_0}}

    monkeypatch.setattr(module.JudgeTools, "find_exist_buff_dict", fake_find_exist_buff_dict)
    if equipper is not None:
        monkeypatch.setattr(
            module.JudgeTools,
            "find_equipper",
            lambda equipper_name, sim_instance=None: equipper,
        )
    return lookup_calls


def _make_branch_fixture(
    monkeypatch: pytest.MonkeyPatch,
    *,
    frozen: bool | None,
    tick: int = 321,
) -> _EdgeFixture:
    index = "Buff-驱动盘-折枝剑歌-暴击率提高"
    active_buff = _CurrentBuffProbe(index=index, tick=tick)
    buff_0 = _BuffTemplate(index=index)
    _install_owner_lookup(
        monkeypatch,
        module=branch_module,
        owner="测试装备者",
        index=index,
        buff_0=buff_0,
        equipper="测试装备者",
    )
    monkeypatch.setattr(
        branch_module.JudgeTools,
        "find_tick",
        lambda sim_instance=None: tick,
    )
    enemy = SimpleNamespace(dynamic=SimpleNamespace(frozen=frozen))
    logic = BranchBladeSongCritRateBonus(active_buff)
    prepared_calls: list[dict[str, object]] = []

    def fake_get_prepared(**kwargs: object) -> None:
        prepared_calls.append(kwargs)
        logic.record.enemy = enemy

    monkeypatch.setattr(logic, "get_prepared", fake_get_prepared)
    return _EdgeFixture(logic, active_buff, buff_0, enemy, prepared_calls)


def _make_polar_fixture(
    monkeypatch: pytest.MonkeyPatch,
    *,
    frozen: bool | None,
    tick: int = 421,
) -> _EdgeFixture:
    index = "Buff-驱动盘-极地重金属-冰属性伤害提高"
    active_buff = _CurrentBuffProbe(index=index, tick=tick)
    buff_0 = _BuffTemplate(index=index)
    _install_owner_lookup(
        monkeypatch,
        module=polar_module,
        owner="测试装备者",
        index=index,
        buff_0=buff_0,
        equipper="测试装备者",
    )
    monkeypatch.setattr(
        polar_module.JudgeTools,
        "find_tick",
        lambda sim_instance=None: tick,
    )
    enemy = SimpleNamespace(dynamic=SimpleNamespace(frozen=frozen))
    logic = PolarMetalFreezeBonus(active_buff)
    prepared_calls: list[dict[str, object]] = []

    def fake_get_prepared(**kwargs: object) -> None:
        prepared_calls.append(kwargs)
        logic.record.enemy = enemy

    monkeypatch.setattr(logic, "get_prepared", fake_get_prepared)
    return _EdgeFixture(logic, active_buff, buff_0, enemy, prepared_calls)


def _make_weeping_fixture(
    monkeypatch: pytest.MonkeyPatch,
    *,
    stun: bool,
    tick: int = 456,
) -> _EdgeFixture:
    index = "Buff-音擎-双生泣星-异常精通提高"
    active_buff = _CurrentBuffProbe(index=index, tick=tick)
    buff_0 = _BuffTemplate(index=index)
    _install_owner_lookup(
        monkeypatch,
        module=weeping_module,
        owner="测试装备者",
        index=index,
        buff_0=buff_0,
        equipper="测试装备者",
    )
    monkeypatch.setattr(weeping_module, "find_tick", lambda sim_instance=None: tick)
    enemy = SimpleNamespace(dynamic=SimpleNamespace(stun=stun))
    logic = WeepingGeminiApBonus(active_buff)
    prepared_calls: list[dict[str, object]] = []
    sub_exist_buff_dict = {index: buff_0}

    def fake_get_prepared(**kwargs: object) -> None:
        prepared_calls.append(kwargs)
        logic.record.equipper = "测试装备者"
        logic.record.enemy = enemy
        logic.record.sub_exist_buff_dict = sub_exist_buff_dict

    monkeypatch.setattr(logic, "get_prepared", fake_get_prepared)
    return _EdgeFixture(logic, active_buff, buff_0, enemy, prepared_calls)


def _make_lighter_fixture(
    monkeypatch: pytest.MonkeyPatch,
    *,
    stun: bool,
) -> _EdgeFixture:
    index = "Buff-角色-莱特-核心被动-失衡时间延长"
    active_buff = _CurrentBuffProbe(index=index, tick=654)
    buff_0 = _BuffTemplate(index=index)
    _install_owner_lookup(
        monkeypatch,
        module=lighter_module,
        owner="莱特",
        index=index,
        buff_0=buff_0,
    )
    enemy = SimpleNamespace(dynamic=SimpleNamespace(stun=stun))
    logic = LighterUniqueSkillStunTimeLimitBonus(active_buff)
    prepared_calls: list[dict[str, object]] = []

    def fake_get_prepared(**kwargs: object) -> None:
        prepared_calls.append(kwargs)
        logic.record.enemy = enemy

    monkeypatch.setattr(logic, "get_prepared", fake_get_prepared)
    return _EdgeFixture(logic, active_buff, buff_0, enemy, prepared_calls)


def _assert_no_runtime_boundaries_touched(active_buff: _CurrentBuffProbe) -> None:
    assert active_buff.sim_instance.schedule_data.event_list == []
    assert active_buff.simple_exit_calls == []
    assert active_buff.update_to_buff_0_calls == []


def test_branch_blade_song_freeze_snapshot_lazy_record_and_unchanged_no_op(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _make_branch_fixture(monkeypatch, frozen=None, tick=321)

    assert fixture.logic.special_judge_logic() is False

    assert fixture.logic.buff_0 is fixture.buff_0
    assert fixture.logic.record is fixture.buff_0.history.record
    assert isinstance(fixture.logic.record, BranchBladeSongCritRateBonusRecord)
    assert fixture.logic.record.last_tick_freez_statement == (321, False)
    assert fixture.prepared_calls == [{"equipper": "折枝剑歌", "enemy": 1}]
    assert fixture.active_buff.simple_start_calls == []
    _assert_no_runtime_boundaries_touched(fixture.active_buff)

    existing_record = fixture.logic.record
    fixture.enemy.dynamic.frozen = False
    assert fixture.logic.special_judge_logic() is False
    assert fixture.logic.record is existing_record
    assert fixture.logic.record.last_tick_freez_statement == (321, False)


def test_branch_blade_song_freeze_state_change_updates_snapshot_before_positive_return(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _make_branch_fixture(monkeypatch, frozen=True, tick=322)

    assert fixture.logic.special_judge_logic() is True

    assert fixture.logic.buff_0 is fixture.buff_0
    assert fixture.logic.record.last_tick_freez_statement == (322, True)
    assert fixture.active_buff.simple_start_calls == []
    _assert_no_runtime_boundaries_touched(fixture.active_buff)


def test_polar_metal_freeze_snapshot_lazy_record_and_unchanged_no_op(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _make_polar_fixture(monkeypatch, frozen=None, tick=421)

    assert fixture.logic.special_judge_logic() is False

    assert fixture.logic.buff_0 is fixture.buff_0
    assert fixture.logic.record is fixture.buff_0.history.record
    assert isinstance(fixture.logic.record, PolarMetalRecord)
    assert fixture.logic.record.last_tick_freez_statement == (421, False)
    assert fixture.prepared_calls == [{"enemy": 1}]
    assert fixture.active_buff.simple_start_calls == []
    _assert_no_runtime_boundaries_touched(fixture.active_buff)

    existing_record = fixture.logic.record
    fixture.enemy.dynamic.frozen = False
    assert fixture.logic.special_judge_logic() is False
    assert fixture.logic.record is existing_record
    assert fixture.logic.record.last_tick_freez_statement == (421, False)


def test_polar_metal_freeze_state_change_updates_snapshot_before_positive_return(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _make_polar_fixture(monkeypatch, frozen=True, tick=422)

    assert fixture.logic.special_judge_logic() is True

    assert fixture.logic.buff_0 is fixture.buff_0
    assert fixture.logic.record.last_tick_freez_statement == (422, True)
    assert fixture.active_buff.simple_start_calls == []
    _assert_no_runtime_boundaries_touched(fixture.active_buff)


def _make_anomaly_bar(active_buff: _CurrentBuffProbe, *, char_name: str) -> AnomalyBar:
    anomaly_bar = AnomalyBar(sim_instance=active_buff.sim_instance)
    anomaly_bar.activated_by = SimpleNamespace(char_name=char_name)
    return anomaly_bar


def test_weeping_gemini_anomaly_bar_identity_edge_and_effect_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _make_weeping_fixture(monkeypatch, stun=False, tick=456)
    first_bar = _make_anomaly_bar(fixture.active_buff, char_name="测试装备者")

    assert fixture.logic.special_judge_logic(anomaly_bar=first_bar) is True
    assert fixture.logic.buff_0 is fixture.buff_0
    assert fixture.logic.record is fixture.buff_0.history.record
    assert isinstance(fixture.logic.record, WeepingGeminiApBonusRecord)
    assert fixture.logic.record.last_update_anomaly is first_bar
    assert fixture.active_buff.simple_start_calls == []

    fixture.logic.special_effect_logic()

    assert fixture.active_buff.simple_start_calls == [(456, {fixture.buff_0.ft.index: fixture.buff_0})]
    assert fixture.logic.record.last_update_anomaly is first_bar
    assert fixture.prepared_calls == [
        {"equipper": "双生泣星"},
        {"equipper": "双生泣星", "enemy": 1, "sub_exist_buff_dict": 1},
    ]
    _assert_no_runtime_boundaries_touched(fixture.active_buff)


def test_weeping_gemini_same_anomaly_no_op_and_new_identity_positive_update(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _make_weeping_fixture(monkeypatch, stun=False)
    first_bar = _make_anomaly_bar(fixture.active_buff, char_name="测试装备者")
    second_bar = _make_anomaly_bar(fixture.active_buff, char_name="测试装备者")

    assert fixture.logic.special_judge_logic(anomaly_bar=first_bar) is True
    assert fixture.logic.special_judge_logic(anomaly_bar=first_bar) is False
    assert fixture.logic.record.last_update_anomaly is first_bar

    assert fixture.logic.special_judge_logic(anomaly_bar=second_bar) is True

    assert fixture.logic.record.last_update_anomaly is second_bar
    assert fixture.active_buff.simple_start_calls == []
    _assert_no_runtime_boundaries_touched(fixture.active_buff)


@pytest.mark.parametrize(
    ("previous_stun", "current_stun", "expected_exit"),
    [
        pytest.param(False, False, False, id="unchanged-not-stunned"),
        pytest.param(True, True, False, id="unchanged-stunned"),
        pytest.param(True, False, True, id="falling-edge"),
    ],
)
def test_lighter_stun_exit_edge_updates_last_statement_before_return(
    monkeypatch: pytest.MonkeyPatch,
    *,
    previous_stun: bool,
    current_stun: bool,
    expected_exit: bool,
) -> None:
    fixture = _make_lighter_fixture(monkeypatch, stun=current_stun)
    fixture.logic.check_record_module()
    assert fixture.logic.buff_0 is fixture.buff_0
    assert fixture.logic.record is fixture.buff_0.history.record
    assert isinstance(fixture.logic.record, LighterUniqueSkillStunTimeRecord)
    fixture.logic.record.last_stun_statement = previous_stun

    assert fixture.logic.special_exit_logic() is expected_exit

    assert fixture.logic.record.last_stun_statement is current_stun
    assert fixture.prepared_calls == [{"enemy": 1}]
    assert fixture.active_buff.simple_start_calls == []
    _assert_no_runtime_boundaries_touched(fixture.active_buff)


def test_lighter_check_record_module_reuses_old_template_and_existing_record(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _make_lighter_fixture(monkeypatch, stun=False)

    fixture.logic.check_record_module()
    existing_record = fixture.logic.record
    existing_record.last_stun_statement = True
    fixture.logic.check_record_module()

    assert fixture.logic.buff_0 is fixture.buff_0
    assert fixture.logic.record is existing_record
    assert fixture.buff_0.history.record is existing_record
    assert fixture.logic.record.last_stun_statement is True
