from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Callable

import pytest
import zsim.define as define_module

sys.modules.setdefault("define", define_module)

from zsim.sim_progress.Buff import JudgeTools

lina_module = importlib.import_module(
    "zsim.sim_progress.Buff.BuffXLogic.LinaAdditionalSkillEleDMGBonus"
)
soldier11_module = importlib.import_module(
    "zsim.sim_progress.Buff.BuffXLogic.Soldier11AdditionalSkillExtraFireDMGBonus"
)

LinaAdditionalSkillEleDMGBonus = lina_module.LinaAdditionalSkillEleDMGBonus
Soldier11AdditionalSkillExtraFireDMGBonus = (
    soldier11_module.Soldier11AdditionalSkillExtraFireDMGBonus
)


class _FailFastEventList(list[object]):
    def append(self, item: object) -> None:
        raise AssertionError("simple enemy-state gates must not publish events")


class _FailFastRuntimeCommandPort:
    def __getattr__(self, name: str) -> Callable[..., None]:
        def _fail(*args: object, **kwargs: object) -> None:
            raise AssertionError(
                f"simple enemy-state gates must not touch runtime writes: {name}"
            )

        return _fail


class _FailFastListenerManager:
    def broadcast_event(self, *args: object, **kwargs: object) -> None:
        raise AssertionError("simple enemy-state gates must not broadcast listeners")


class _CurrentBuffDynamicState:
    @property
    def count(self) -> float:
        return 0.0

    @count.setter
    def count(self, value: float) -> None:
        raise AssertionError("simple enemy-state gates must not mutate current dy.count")


class _BuffTemplate:
    def __init__(self, *, index: str) -> None:
        self.ft = SimpleNamespace(index=index)
        self.dy = SimpleNamespace(count=0.0)
        self.history = SimpleNamespace(record=None)


class _CurrentBuffProbe:
    def __init__(self, *, index: str) -> None:
        runtime_command_port = _FailFastRuntimeCommandPort()
        self.ft = SimpleNamespace(index=index)
        self.dy: Any = _CurrentBuffDynamicState()
        self.sim_instance = SimpleNamespace(
            listener_manager=_FailFastListenerManager(),
            load_data=SimpleNamespace(
                exist_buff_dict={},
                action_stack=[],
                runtime_command_port=runtime_command_port,
            ),
            schedule_data=SimpleNamespace(
                event_list=_FailFastEventList(),
                runtime_command_port=runtime_command_port,
            ),
            runtime_command_port=runtime_command_port,
        )

    def simple_start(self, *args: object, **kwargs: object) -> None:
        raise AssertionError("simple enemy-state gates must not call simple_start")

    def simple_exit(self, *args: object, **kwargs: object) -> None:
        raise AssertionError("simple enemy-state gates must not call simple_exit")

    def update_to_buff_0(self, *args: object, **kwargs: object) -> None:
        raise AssertionError("simple enemy-state gates must not call update_to_buff_0")


class _EnemyDynamicStateProbe:
    def __init__(self, *, shock: bool, stun: bool) -> None:
        self._shock = shock
        self._stun = stun
        self.shock_reads = 0
        self.stun_reads = 0
        self.dynamic_debuff_list: list[object] = []
        self.dynamic_dot_list: list[object] = []

    @property
    def shock(self) -> bool:
        self.shock_reads += 1
        return self._shock

    @property
    def stun(self) -> bool:
        self.stun_reads += 1
        return self._stun


@dataclass(frozen=True)
class _PreparationCall:
    buff_instance: object
    buff_0: object
    kwargs: dict[str, object]
    record_at_call: object


@dataclass(frozen=True)
class _StateGateFixture:
    logic: Any
    current_buff: _CurrentBuffProbe
    current_template: _BuffTemplate
    enemy_dynamic: _EnemyDynamicStateProbe
    preparation_calls: list[_PreparationCall]


def _install_lookup_and_preparation_fakes(
    monkeypatch: pytest.MonkeyPatch,
    *,
    logic_module: Any,
    current_buff: _CurrentBuffProbe,
    current_template: _BuffTemplate,
    exist_buff_dict: dict[str, dict[str, _BuffTemplate]],
    enemy: object,
    preparation_calls: list[_PreparationCall],
) -> None:
    monkeypatch.setattr(
        JudgeTools,
        "find_exist_buff_dict",
        lambda sim_instance=None: exist_buff_dict,
    )

    def _check_preparation(*, buff_instance: object, buff_0: Any, **kwargs: object) -> None:
        if buff_instance is not current_buff:
            raise AssertionError("preparation used the wrong current buff")
        if buff_0 is not current_template:
            raise AssertionError("preparation used the wrong buff template")
        record = buff_0.history.record
        if record is None:
            raise AssertionError("check_record_module must run before get_prepared")
        record.enemy = enemy
        preparation_calls.append(
            _PreparationCall(
                buff_instance=buff_instance,
                buff_0=buff_0,
                kwargs=dict(kwargs),
                record_at_call=record,
            )
        )

    monkeypatch.setattr(logic_module, "check_preparation", _check_preparation)


def _make_state_gate_fixture(
    monkeypatch: pytest.MonkeyPatch,
    *,
    logic_module: Any,
    logic_type: type[Any],
    current_index: str,
    owner_name: str,
    shock: bool,
    stun: bool,
) -> _StateGateFixture:
    current_buff = _CurrentBuffProbe(index=current_index)
    current_template = _BuffTemplate(index=current_index)
    exist_buff_dict = {owner_name: {current_index: current_template}}
    current_buff.sim_instance.load_data.exist_buff_dict = exist_buff_dict
    logic = logic_type(current_buff)
    enemy_dynamic = _EnemyDynamicStateProbe(shock=shock, stun=stun)
    enemy = SimpleNamespace(dynamic=enemy_dynamic)
    preparation_calls: list[_PreparationCall] = []
    _install_lookup_and_preparation_fakes(
        monkeypatch,
        logic_module=logic_module,
        current_buff=current_buff,
        current_template=current_template,
        exist_buff_dict=exist_buff_dict,
        enemy=enemy,
        preparation_calls=preparation_calls,
    )

    return _StateGateFixture(
        logic=logic,
        current_buff=current_buff,
        current_template=current_template,
        enemy_dynamic=enemy_dynamic,
        preparation_calls=preparation_calls,
    )


def _assert_preparation_calls(
    fixture: _StateGateFixture,
    *,
    expected_count: int,
) -> None:
    assert len(fixture.preparation_calls) == expected_count
    for call in fixture.preparation_calls:
        assert call.buff_instance is fixture.current_buff
        assert call.buff_0 is fixture.current_template
        assert call.kwargs == {"enemy": 1}
        assert call.record_at_call is fixture.current_template.history.record


def _assert_identity_and_no_side_effects(fixture: _StateGateFixture) -> None:
    assert fixture.logic.buff_0 is fixture.current_template
    assert fixture.logic.record is fixture.current_template.history.record
    assert fixture.current_buff.dy.count == 0.0
    assert fixture.current_template.dy.count == 0.0
    assert fixture.current_buff.sim_instance.schedule_data.event_list == []
    assert fixture.enemy_dynamic.dynamic_dot_list == []
    assert fixture.enemy_dynamic.dynamic_debuff_list == []


@pytest.mark.parametrize(
    ("shock", "expected_judge", "expected_exit"),
    [
        pytest.param(False, False, True, id="not-shocked"),
        pytest.param(True, True, False, id="shocked"),
    ],
)
def test_lina_additional_skill_shock_gate_delegates_read_only(
    monkeypatch: pytest.MonkeyPatch,
    *,
    shock: bool,
    expected_judge: bool,
    expected_exit: bool,
) -> None:
    fixture = _make_state_gate_fixture(
        monkeypatch,
        logic_module=lina_module,
        logic_type=LinaAdditionalSkillEleDMGBonus,
        current_index="Buff-角色-丽娜-组队被动-电属性伤害提高",
        owner_name="丽娜",
        shock=shock,
        stun=not shock,
    )

    assert fixture.logic.special_judge_logic() is expected_judge
    assert fixture.logic.special_exit_logic() is expected_exit

    _assert_preparation_calls(fixture, expected_count=2)
    assert fixture.enemy_dynamic.shock_reads == 2
    assert fixture.enemy_dynamic.stun_reads == 0
    _assert_identity_and_no_side_effects(fixture)


@pytest.mark.parametrize(
    ("stun", "expected"),
    [
        pytest.param(False, False, id="not-stunned"),
        pytest.param(True, True, id="stunned"),
    ],
)
def test_soldier11_additional_skill_stun_gate_delegates_read_only(
    monkeypatch: pytest.MonkeyPatch,
    *,
    stun: bool,
    expected: bool,
) -> None:
    fixture = _make_state_gate_fixture(
        monkeypatch,
        logic_module=soldier11_module,
        logic_type=Soldier11AdditionalSkillExtraFireDMGBonus,
        current_index="Buff-角色-11号-组队被动-额外火伤",
        owner_name="11号",
        shock=not stun,
        stun=stun,
    )

    assert fixture.logic.special_judge_logic() is expected

    _assert_preparation_calls(fixture, expected_count=1)
    assert fixture.enemy_dynamic.stun_reads == 1
    assert fixture.enemy_dynamic.shock_reads == 0
    _assert_identity_and_no_side_effects(fixture)
