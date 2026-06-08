from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Sequence, cast

import pytest
import zsim.define as define_module

sys.modules.setdefault("define", define_module)

from zsim.sim_progress.Buff import JudgeTools
from zsim.sim_progress.Buff.JudgeTools import read_trigger_buff_state
from zsim.sim_progress.Buff.BuffXLogic.AstralVoice import AstralVoice
from zsim.sim_progress.Buff.BuffXLogic.CordisGerminaSNAAndQIgnoreDefense import (
    CordisGerminaSNAAndQIgnoreDefense,
)
from zsim.sim_progress.Buff.BuffXLogic.FlamemakerShakerApBonus import (
    FlamemakerShakerApBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.SharpenedStingerAnomalyBuildupBonus import (
    SharpenedStingerAnomalyBuildupBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.SpectralGazeImpactBonus import (
    SpectralGazeImpactBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.YangiCinema1ApBonus import (
    YangiCinema1ApBonus,
)
from zsim.sim_progress.Load import LoadingMission
from zsim.sim_progress.Preload import SkillNode

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_BUFF_XLOGIC_ROOT = _PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffXLogic"


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
    current_operator: str = "operator",
) -> _GateFixture:
    current_buff = _CurrentBuffProbe(index=current_index, operator=current_operator)
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


def _make_astral_voice_gate(
    monkeypatch: pytest.MonkeyPatch,
    *,
    active: bool,
) -> _GateFixture:
    return _make_equipment_gate(
        monkeypatch,
        logic_type=AstralVoice,
        current_index="Buff-驱动盘-静听嘉音-全队增伤",
        trigger_index="Buff-驱动盘-静听嘉音-嘉音",
        active=active,
        count=7,
        equipper_name="静听嘉音",
        current_operator="静听嘉音",
    )


def _make_astral_voice_skill_node(
    *,
    trigger_buff_level: int,
    mission_state: str | None,
) -> SkillNode:
    skill = cast(
        Any,
        SimpleNamespace(
            skill_tag="test_astral_voice_support",
            char_name="静听嘉音",
            hit_times=1,
            labels=None,
            ticks=1,
            tick_list=[],
            trigger_buff_level=trigger_buff_level,
        ),
    )
    skill_node = SkillNode(skill, preload_tick=100)
    loading_mission = LoadingMission(skill_node)
    loading_mission.mission_dict = {}
    if mission_state is not None:
        loading_mission.mission_dict[100] = mission_state
    return skill_node


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
    trigger_state = read_trigger_buff_state(logic.record)
    assert trigger_state.active is fixture.trigger_template.dy.active
    assert trigger_state.count == fixture.trigger_template.dy.count
    assert trigger_state.built_in_buff_box == tuple(
        fixture.trigger_template.dy.built_in_buff_box
    )


def _assert_astral_voice_judge_no_writes(fixture: _GateFixture) -> None:
    _assert_lazy_record_and_trigger_identity(fixture)
    assert (
        fixture.logic.record.action_stack
        is fixture.current_buff.sim_instance.load_data.action_stack
    )
    assert fixture.current_buff.dy.count == 0.0
    assert fixture.current_buff.sim_instance.schedule_data.event_list == []


def test_trigger_state_helper_public_api_is_read_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _make_equipment_gate(
        monkeypatch,
        logic_type=FlamemakerShakerApBonus,
        current_index="Buff-驱动盘-灼心摇壶-异常精通提高",
        trigger_index="Buff-驱动盘-灼心摇壶-增伤",
        active=True,
        count=5,
        built_in_buff_box=(("start", "end"),),
    )
    fixture.logic.check_record_module()
    fixture.logic.get_prepared(
        equipper="灼心摇壶",
        trigger_buff_0=("equipper", "灼心摇壶-增伤"),
    )

    trigger_state = read_trigger_buff_state(fixture.logic.record)

    assert trigger_state.active is True
    assert trigger_state.count == 5
    assert trigger_state.built_in_buff_box == (("start", "end"),)
    for mutating_name in (
        "simple_start",
        "update_to_buff_0",
        "publish",
        "runtime_command_port",
        "schedule_dispatch_port",
    ):
        assert not hasattr(trigger_state, mutating_name)
    with pytest.raises(AttributeError):
        trigger_state.count = 6  # type: ignore[misc]
    assert fixture.logic.record.trigger_buff_0 is fixture.trigger_template


def test_trigger_state_helper_requires_prepared_trigger_record() -> None:
    with pytest.raises(ValueError, match="trigger_buff_0"):
        read_trigger_buff_state(SimpleNamespace(trigger_buff_0=None))


@pytest.mark.parametrize(
    ("file_name", "forbidden_chains"),
    [
        pytest.param(
            "FlamemakerShakerApBonus.py",
            ("record.trigger_buff_0.dy.active", "record.trigger_buff_0.dy.count"),
            id="flamemaker",
        ),
        pytest.param(
            "SpectralGazeImpactBonus.py",
            ("record.trigger_buff_0.dy.active", "record.trigger_buff_0.dy.count"),
            id="spectral-gaze",
        ),
        pytest.param(
            "SharpenedStingerAnomalyBuildupBonus.py",
            ("record.trigger_buff_0.dy.count",),
            id="sharpened-stinger",
        ),
        pytest.param(
            "CordisGerminaSNAAndQIgnoreDefense.py",
            ("record.trigger_buff_0.dy.built_in_buff_box",),
            id="cordis-germina",
        ),
        pytest.param(
            "AstralVoice.py",
            ("record.trigger_buff_0.dy.active",),
            id="astral-voice",
        ),
    ],
)
def test_migrated_trigger_state_gate_sources_use_trigger_state_helper(
    *,
    file_name: str,
    forbidden_chains: Sequence[str],
) -> None:
    source = (_BUFF_XLOGIC_ROOT / file_name).read_text(encoding="utf-8")

    assert "read_trigger_buff_state" in source
    for chain in forbidden_chains:
        assert chain not in source


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
    ("count", "expected"),
    [
        pytest.param(0, False, id="zero"),
        pytest.param(2, False, id="below-threshold"),
        pytest.param(3, True, id="equals-threshold"),
        pytest.param(4, False, id="above-threshold"),
    ],
)
def test_sharpened_stinger_count_gate_is_read_only(
    monkeypatch: pytest.MonkeyPatch,
    *,
    count: float,
    expected: bool,
) -> None:
    fixture = _make_equipment_gate(
        monkeypatch,
        logic_type=SharpenedStingerAnomalyBuildupBonus,
        current_index="Buff-武器-精1淬锋钳刺-属性异常积蓄效率提升",
        trigger_index="Buff-武器-精1淬锋钳刺-猎意",
        equipper_name="淬锋钳刺",
        active=True,
        count=count,
    )

    assert fixture.logic.special_judge_logic() is expected
    assert fixture.logic.special_exit_logic() is (not expected)
    _assert_lazy_record_and_trigger_identity(fixture)
    assert (
        fixture.logic.record.preload_data
        is fixture.current_buff.sim_instance.preload.preload_data
    )
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
    trigger_box = tuple(object() for _ in range(box_length))
    fixture = _make_equipment_gate(
        monkeypatch,
        logic_type=CordisGerminaSNAAndQIgnoreDefense,
        current_index="Buff-音擎-机巧心种-普攻大招无视防御",
        trigger_index="Buff-音擎-机巧心种-电属性增伤",
        active=True,
        count=0,
        built_in_buff_box=trigger_box,
    )

    assert fixture.logic.special_judge_logic() is expected
    assert fixture.logic.special_exit_logic() is (not expected)
    _assert_lazy_record_and_trigger_identity(fixture)
    assert fixture.current_buff.dy.count == 0.0
    assert fixture.current_template.dy.built_in_buff_box == ()
    assert fixture.current_template.dy.count == 0.0
    assert fixture.trigger_template.dy.built_in_buff_box == trigger_box
    assert len(fixture.trigger_template.dy.built_in_buff_box) == box_length


def test_astral_voice_judge_returns_false_without_skill_node(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _make_astral_voice_gate(monkeypatch, active=True)

    assert fixture.logic.special_judge_logic() is False
    _assert_astral_voice_judge_no_writes(fixture)


@pytest.mark.parametrize(
    "input_kind",
    [
        pytest.param("skill-node", id="skill-node"),
        pytest.param("loading-mission", id="loading-mission"),
    ],
)
def test_astral_voice_judge_normalizes_skill_node_inputs_without_writes(
    monkeypatch: pytest.MonkeyPatch,
    *,
    input_kind: str,
) -> None:
    fixture = _make_astral_voice_gate(monkeypatch, active=True)
    skill_node = _make_astral_voice_skill_node(
        trigger_buff_level=7,
        mission_state="start",
    )
    judge_input: SkillNode | LoadingMission
    if input_kind == "loading-mission":
        assert skill_node.loading_mission is not None
        judge_input = skill_node.loading_mission
    else:
        judge_input = skill_node

    assert fixture.logic.special_judge_logic(skill_node=judge_input) is True
    _assert_astral_voice_judge_no_writes(fixture)


@pytest.mark.parametrize(
    ("active", "trigger_buff_level", "mission_state", "expected"),
    [
        pytest.param(False, 7, "start", False, id="inactive-trigger"),
        pytest.param(True, 6, "start", False, id="wrong-trigger-level"),
        pytest.param(True, 7, "hit", False, id="mission-not-start"),
        pytest.param(True, 7, None, False, id="missing-tick-state"),
        pytest.param(True, 7, "start", True, id="active-level-seven-start"),
    ],
)
def test_astral_voice_judge_gate_branches_are_read_only(
    monkeypatch: pytest.MonkeyPatch,
    *,
    active: bool,
    trigger_buff_level: int,
    mission_state: str | None,
    expected: bool,
) -> None:
    fixture = _make_astral_voice_gate(monkeypatch, active=active)
    skill_node = _make_astral_voice_skill_node(
        trigger_buff_level=trigger_buff_level,
        mission_state=mission_state,
    )

    assert fixture.logic.special_judge_logic(skill_node=skill_node) is expected
    _assert_astral_voice_judge_no_writes(fixture)


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
