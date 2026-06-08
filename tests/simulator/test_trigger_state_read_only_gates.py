from __future__ import annotations

import sys
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Callable, Sequence, cast

import pytest
import zsim.define as define_module

sys.modules.setdefault("define", define_module)

from zsim.sim_progress.Buff import JudgeTools
from zsim.sim_progress.Buff.BuffXLogic.CordisGerminaSNAAndQIgnoreDefense import (
    CordisGerminaSNAAndQIgnoreDefense,
)
from zsim.sim_progress.Buff.BuffXLogic.FlamemakerShakerApBonus import (
    FlamemakerShakerApBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.SpectralGazeImpactBonus import (
    SpectralGazeImpactBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.YangiCinema1ApBonus import (
    YangiCinema1ApBonus,
)


class _FailFastEventList(list[object]):
    def append(self, item: object) -> None:
        raise AssertionError("trigger-state read-only gate tests must not publish events")


class _FailFastRuntimeCommandPort:
    def __getattr__(self, name: str) -> Callable[..., None]:
        def _fail(*args: object, **kwargs: object) -> None:
            raise AssertionError(
                f"trigger-state read-only gate tests must not touch runtime command writes: {name}"
            )

        return _fail


class _CurrentBuffDynamicState:
    def __init__(self, count: float = 0.0) -> None:
        self._count = count

    @property
    def count(self) -> float:
        return self._count

    @count.setter
    def count(self, value: float) -> None:
        raise AssertionError("pure trigger-state gates must not mutate current dy.count")


class _TriggerBuffDynamicState:
    def __init__(
        self,
        *,
        active: bool,
        count: float,
        built_in_buff_box: Sequence[object] = (),
    ) -> None:
        self.active = active
        self.count = count
        self.built_in_buff_box = tuple(built_in_buff_box)


class _BuffTemplate:
    def __init__(
        self,
        *,
        index: str,
        active: bool = False,
        count: float = 0.0,
        built_in_buff_box: Sequence[object] = (),
    ) -> None:
        self.ft = SimpleNamespace(index=index)
        self.dy = _TriggerBuffDynamicState(
            active=active,
            count=count,
            built_in_buff_box=built_in_buff_box,
        )
        self.history = SimpleNamespace(record=None)


class _CurrentBuffProbe:
    def __init__(self, *, index: str, operator: str = "operator") -> None:
        self.ft = SimpleNamespace(index=index, operator=operator)
        self.dy = _CurrentBuffDynamicState()
        runtime_command_port = _FailFastRuntimeCommandPort()
        self.sim_instance = SimpleNamespace(
            tick=100,
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
            preload=SimpleNamespace(preload_data=[]),
        )

    def simple_start(self, *args: object, **kwargs: object) -> None:
        raise AssertionError("pure trigger-state gates must not call simple_start")

    def update_to_buff_0(self, *args: object, **kwargs: object) -> None:
        raise AssertionError("pure trigger-state gates must not call update_to_buff_0")


@dataclass(frozen=True)
class _GateFixture:
    logic: Any
    current_buff: _CurrentBuffProbe
    current_template: _BuffTemplate
    trigger_template: _BuffTemplate
    exist_buff_dict: dict[str, dict[str, _BuffTemplate]]


def _install_lookup_fakes(
    monkeypatch: pytest.MonkeyPatch,
    *,
    exist_buff_dict: dict[str, dict[str, _BuffTemplate]],
    equipper_name: str = "测试装备者",
) -> None:
    monkeypatch.setattr(
        JudgeTools,
        "find_exist_buff_dict",
        lambda sim_instance=None: exist_buff_dict,
    )
    monkeypatch.setattr(
        JudgeTools,
        "find_equipper",
        lambda equipper, sim_instance=None: equipper_name,
    )
    monkeypatch.setattr(
        JudgeTools,
        "find_char_from_CID",
        lambda char_CID, sim_instance=None: SimpleNamespace(NAME="柳", CID=char_CID),
    )
    monkeypatch.setattr(
        JudgeTools,
        "find_char_from_name",
        lambda NAME, sim_instance=None: SimpleNamespace(NAME=NAME),
    )


def _make_equipment_gate(
    monkeypatch: pytest.MonkeyPatch,
    *,
    logic_type: type[Any],
    current_index: str,
    trigger_index: str,
    active: bool,
    count: float,
    built_in_buff_box: Sequence[object] = (),
    equipper_name: str = "测试装备者",
) -> _GateFixture:
    current_buff = _CurrentBuffProbe(index=current_index)
    current_template = _BuffTemplate(index=current_index)
    trigger_template = _BuffTemplate(
        index=trigger_index,
        active=active,
        count=count,
        built_in_buff_box=built_in_buff_box,
    )
    exist_buff_dict = {
        equipper_name: {
            current_index: current_template,
            trigger_index: trigger_template,
        }
    }
    current_buff.sim_instance.load_data.exist_buff_dict = exist_buff_dict
    _install_lookup_fakes(
        monkeypatch,
        exist_buff_dict=exist_buff_dict,
        equipper_name=equipper_name,
    )

    return _GateFixture(
        logic=logic_type(current_buff),
        current_buff=current_buff,
        current_template=current_template,
        trigger_template=trigger_template,
        exist_buff_dict=exist_buff_dict,
    )


def _make_yanagi_gate(
    monkeypatch: pytest.MonkeyPatch,
    *,
    active: bool,
    count: float,
) -> _GateFixture:
    current_index = "Buff-角色-柳-1画-异常精通提高"
    trigger_index = "Buff-角色-柳-1画-洞悉"
    current_buff = _CurrentBuffProbe(index=current_index)
    current_template = _BuffTemplate(index=current_index)
    trigger_template = _BuffTemplate(
        index=trigger_index,
        active=active,
        count=count,
    )
    exist_buff_dict = {
        "柳": {
            current_index: current_template,
            trigger_index: trigger_template,
        }
    }
    current_buff.sim_instance.load_data.exist_buff_dict = exist_buff_dict
    _install_lookup_fakes(monkeypatch, exist_buff_dict=exist_buff_dict)

    return _GateFixture(
        logic=YangiCinema1ApBonus(current_buff),
        current_buff=current_buff,
        current_template=current_template,
        trigger_template=trigger_template,
        exist_buff_dict=exist_buff_dict,
    )


def _assert_lazy_record_and_trigger_identity(fixture: _GateFixture) -> None:
    logic = fixture.logic

    assert fixture.current_template.history.record is not None
    assert logic.buff_0 is fixture.current_template
    assert logic.record is fixture.current_template.history.record
    assert logic.record.trigger_buff_0 is fixture.trigger_template


@pytest.mark.parametrize(
    ("active", "count", "expected"),
    [
        pytest.param(False, 5, False, id="inactive"),
        pytest.param(True, 4, False, id="below-threshold"),
        pytest.param(True, 5, True, id="equals-threshold"),
        pytest.param(True, 6, True, id="above-threshold"),
    ],
)
def test_flamemaker_equipment_trigger_count_gate_is_read_only(
    monkeypatch: pytest.MonkeyPatch,
    *,
    active: bool,
    count: float,
    expected: bool,
) -> None:
    fixture = _make_equipment_gate(
        monkeypatch,
        logic_type=FlamemakerShakerApBonus,
        current_index="Buff-驱动盘-灼心摇壶-异常精通提高",
        trigger_index="Buff-驱动盘-灼心摇壶-增伤",
        active=active,
        count=count,
    )

    assert fixture.logic.special_judge_logic() is expected
    _assert_lazy_record_and_trigger_identity(fixture)
    assert fixture.current_buff.dy.count == 0.0


@pytest.mark.parametrize(
    ("active", "count", "expected"),
    [
        pytest.param(False, 3, False, id="inactive"),
        pytest.param(True, 2, False, id="below-required-count"),
        pytest.param(True, 3, True, id="required-count"),
        pytest.param(True, 4, False, id="above-required-count"),
    ],
)
def test_spectral_gaze_equipment_trigger_exact_count_gate_is_read_only(
    monkeypatch: pytest.MonkeyPatch,
    *,
    active: bool,
    count: float,
    expected: bool,
) -> None:
    fixture = _make_equipment_gate(
        monkeypatch,
        logic_type=SpectralGazeImpactBonus,
        current_index="Buff-音擎-索魂影眸-冲击力提高",
        trigger_index="Buff-音擎-索魂影眸-魂锁",
        active=active,
        count=count,
    )

    assert fixture.logic.special_judge_logic() is expected
    _assert_lazy_record_and_trigger_identity(fixture)
    assert fixture.current_buff.dy.count == 0.0


@pytest.mark.parametrize(
    ("box_length", "expected"),
    [
        pytest.param(0, False, id="empty-box"),
        pytest.param(1, False, id="single-entry"),
        pytest.param(2, True, id="two-entries"),
        pytest.param(3, False, id="three-entries"),
    ],
)
def test_cordis_germina_tuple_box_gate_reads_without_tuple_sync(
    monkeypatch: pytest.MonkeyPatch,
    *,
    box_length: int,
    expected: bool,
) -> None:
    fixture = _make_equipment_gate(
        monkeypatch,
        logic_type=CordisGerminaSNAAndQIgnoreDefense,
        current_index="Buff-音擎-机巧心种-普攻大招无视防御",
        trigger_index="Buff-音擎-机巧心种-电属性增伤",
        active=True,
        count=0,
        built_in_buff_box=tuple(object() for _ in range(box_length)),
    )

    assert fixture.logic.special_judge_logic() is expected
    _assert_lazy_record_and_trigger_identity(fixture)
    assert fixture.current_buff.dy.count == 0.0
    assert len(fixture.trigger_template.dy.built_in_buff_box) == box_length


@pytest.mark.parametrize(
    ("active", "count", "expected"),
    [
        pytest.param(False, 1, False, id="inactive"),
        pytest.param(True, 0, False, id="zero-count"),
        pytest.param(True, 1, True, id="one-count"),
        pytest.param(True, 2, True, id="above-threshold"),
    ],
)
def test_yanagi_character_trigger_lookup_preserves_old_identity(
    monkeypatch: pytest.MonkeyPatch,
    *,
    active: bool,
    count: float,
    expected: bool,
) -> None:
    fixture = _make_yanagi_gate(monkeypatch, active=active, count=count)

    assert fixture.logic.special_judge_logic() is expected
    _assert_lazy_record_and_trigger_identity(fixture)
    assert fixture.current_buff.dy.count == 0.0


def test_check_preparation_trigger_lookup_keeps_existing_record_trigger(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _make_equipment_gate(
        monkeypatch,
        logic_type=FlamemakerShakerApBonus,
        current_index="Buff-驱动盘-灼心摇壶-异常精通提高",
        trigger_index="Buff-驱动盘-灼心摇壶-增伤",
        active=True,
        count=5,
    )
    fixture.logic.check_record_module()
    original_trigger = _BuffTemplate(
        index="Buff-驱动盘-灼心摇壶-增伤",
        active=False,
        count=0,
    )
    fixture.logic.record.trigger_buff_0 = original_trigger

    fixture.logic.get_prepared(
        equipper="灼心摇壶",
        trigger_buff_0=("equipper", "灼心摇壶-增伤"),
    )

    assert fixture.logic.record.trigger_buff_0 is original_trigger
    assert fixture.trigger_template is not original_trigger
    assert fixture.current_buff.dy.count == 0.0


def test_trigger_lookup_resolves_suffix_when_multiple_candidates_match(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _make_equipment_gate(
        monkeypatch,
        logic_type=FlamemakerShakerApBonus,
        current_index="Buff-驱动盘-灼心摇壶-异常精通提高",
        trigger_index="Buff-驱动盘-灼心摇壶-增伤",
        active=True,
        count=5,
    )
    prefix_match = _BuffTemplate(
        index="Buff-驱动盘-灼心摇壶-增伤-历史副本",
        active=True,
        count=99,
    )
    fixture.exist_buff_dict["测试装备者"]["Buff-驱动盘-灼心摇壶-增伤-历史副本"] = prefix_match

    assert fixture.logic.special_judge_logic() is True

    _assert_lazy_record_and_trigger_identity(fixture)
    assert fixture.logic.record.trigger_buff_0 is not prefix_match
    assert cast(float, fixture.logic.record.trigger_buff_0.dy.count) == 5
