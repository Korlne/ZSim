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
from zsim.sim_progress.Buff.JudgeTools import (
    BuffTemplateRegistryReadPort,
    TriggerBuffLookup,
    TriggerBuffRef,
    read_trigger_buff_state,
    read_trigger_buff_state_active,
)
from zsim.sim_progress.Buff.BuffXLogic.AstralVoice import AstralVoice
from zsim.sim_progress.Buff.BuffXLogic.CordisGerminaSNAAndQIgnoreDefense import (
    CordisGerminaSNAAndQIgnoreDefense,
)
from zsim.sim_progress.Buff.BuffXLogic.FlamemakerShakerApBonus import (
    FlamemakerShakerApBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.JaneCinema1APTransToDmgBonus import (
    JaneCinema1APTransToDmgBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.JaneCoreSkillStrikeCritDmgBonus import (
    JaneCoreSkillStrikeCritDmgBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.JaneCoreSkillStrikeCritRateBonus import (
    JaneCoreSkillStrikeCritRateBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.JanePassionStateAPTransToATK import (
    JanePassionStateAPTransToATK,
)
from zsim.sim_progress.Buff.BuffXLogic.JanePassionStatePhyBuildupBonus import (
    JanePassionStatePhyBuildupBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.SeveredInnocencELEDMGBonus import (
    SeveredInnocencELEDMGBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.SharpenedStingerAnomalyBuildupBonus import (
    SharpenedStingerAnomalyBuildupBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.Soldier0AnbyAdditionalSkillDMGBonus import (
    Soldier0AnbyAdditionalSkillDMGBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.Soldier0AnbyCinema4EleResReduce import (
    Soldier0AnbyCinema4EleResReduce,
)
from zsim.sim_progress.Buff.BuffXLogic.Soldier0AnbyCoreSkillCritDMGBonus import (
    Soldier0AnbyCoreSkillCritDMGBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.SpectralGazeImpactBonus import (
    SpectralGazeImpactBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.WeepingCradleDMGBonusIncrease import (
    WeepingCradleDMGBonusIncrease,
)
from zsim.sim_progress.Buff.BuffXLogic.YangiCinema1ApBonus import (
    YangiCinema1ApBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.YunkuiTalesSheerAtkBonus import (
    YunkuiTalesSheerAtkBonus,
)
from zsim.sim_progress.Load import LoadingMission
from zsim.sim_progress.Preload import SkillNode
from zsim.sim_progress.ScheduledEvent.Calculator import CalculatorBuffAttributeReader

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
        startticks: int = 0,
        endticks: int = 0,
    ) -> None:
        self.active = active
        self.count = count
        self.built_in_buff_box = tuple(built_in_buff_box)
        self.startticks = startticks
        self.endticks = endticks


class _BuffTemplate:
    def __init__(
        self,
        *,
        index: str,
        active: bool = False,
        count: float = 0.0,
        built_in_buff_box: Sequence[object] = (),
        startticks: int = 0,
        endticks: int = 0,
    ) -> None:
        self.ft = SimpleNamespace(index=index)
        self.dy = _TriggerBuffDynamicState(
            active=active,
            count=count,
            built_in_buff_box=built_in_buff_box,
            startticks=startticks,
            endticks=endticks,
        )
        self.history = SimpleNamespace(record=None)


class _CurrentBuffProbe:
    def __init__(self, *, index: str, operator: str = "operator") -> None:
        self.ft = SimpleNamespace(index=index, operator=operator)
        self.dy: Any = _CurrentBuffDynamicState()
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


class _EffectCurrentBuffDynamicState:
    def __init__(self, events: list[tuple[str, tuple[object, ...]]]) -> None:
        self._count = 0.0
        self._startticks = 0
        self._endticks = 0
        self._events = events

    @property
    def count(self) -> float:
        return self._count

    @count.setter
    def count(self, value: float) -> None:
        self._count = value
        self._events.append(("set_count", (value,)))

    @property
    def startticks(self) -> int:
        return self._startticks

    @startticks.setter
    def startticks(self, value: int) -> None:
        self._startticks = value
        self._events.append(("set_startticks", (value,)))

    @property
    def endticks(self) -> int:
        return self._endticks

    @endticks.setter
    def endticks(self, value: int) -> None:
        self._endticks = value
        self._events.append(("set_endticks", (value,)))


class _AstralVoiceEffectBuffProbe(_CurrentBuffProbe):
    def __init__(self, *, index: str, operator: str = "operator") -> None:
        self.effect_events: list[tuple[str, tuple[object, ...]]] = []
        super().__init__(index=index, operator=operator)
        self.dy = _EffectCurrentBuffDynamicState(self.effect_events)

    def simple_start(self, *args: object, **kwargs: object) -> None:
        self.effect_events.append(("simple_start", args))

    def update_to_buff_0(self, *args: object, **kwargs: object) -> None:
        self.effect_events.append(("update_to_buff_0", args))


class _JaneHitBuffProbe(_AstralVoiceEffectBuffProbe):
    def __init__(
        self,
        *,
        index: str,
        operator: str = "operator",
        maxcount: float = 999.0,
    ) -> None:
        super().__init__(index=index, operator=operator)
        self.ft.maxcount = maxcount


class _Soldier0AnbyHitBuffProbe(_AstralVoiceEffectBuffProbe):
    pass


class _WeepingCradleEffectBuffProbe(_AstralVoiceEffectBuffProbe):
    def simple_start(self, *args: object, **kwargs: object) -> None:
        payload = args if not kwargs else args + (kwargs,)
        self.effect_events.append(("simple_start", payload))


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
    char_name: str = "柳",
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
        lambda char_CID, sim_instance=None: SimpleNamespace(NAME=char_name, CID=char_CID),
    )
    monkeypatch.setattr(
        JudgeTools,
        "find_char_from_name",
        lambda NAME, sim_instance=None: SimpleNamespace(NAME=NAME),
    )
    monkeypatch.setattr(
        JudgeTools,
        "find_enemy",
        lambda sim_instance=None: SimpleNamespace(NAME="enemy"),
    )
    monkeypatch.setattr(
        JudgeTools,
        "find_dynamic_buff_list",
        lambda sim_instance=None: [],
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


def _make_astral_voice_effect_gate(
    monkeypatch: pytest.MonkeyPatch,
    *,
    count: float,
) -> _GateFixture:
    current_index = "Buff-驱动盘-静听嘉音-全队增伤"
    trigger_index = "Buff-驱动盘-静听嘉音-嘉音"
    current_buff = _AstralVoiceEffectBuffProbe(
        index=current_index,
        operator="静听嘉音",
    )
    current_template = _BuffTemplate(index=current_index)
    trigger_template = _BuffTemplate(
        index=trigger_index,
        active=True,
        count=count,
    )
    exist_buff_dict = {
        "静听嘉音": {
            current_index: current_template,
            trigger_index: trigger_template,
        }
    }
    current_buff.sim_instance.load_data.exist_buff_dict = exist_buff_dict
    _install_lookup_fakes(
        monkeypatch,
        exist_buff_dict=exist_buff_dict,
        equipper_name="静听嘉音",
    )

    return _GateFixture(
        logic=AstralVoice(current_buff),
        current_buff=current_buff,
        current_template=current_template,
        trigger_template=trigger_template,
        exist_buff_dict=exist_buff_dict,
    )


def _make_weeping_cradle_gate(
    monkeypatch: pytest.MonkeyPatch,
    *,
    active: bool,
    current_active: bool = False,
    trigger_startticks: int = 25,
    trigger_endticks: int = 85,
    tick: int = 100,
    cd: int = 10,
) -> _GateFixture:
    current_index = "Buff-武器-精1啜泣摇篮-全队增伤自增长"
    trigger_index = "Buff-武器-精1啜泣摇篮-全队增伤"
    current_buff = _WeepingCradleEffectBuffProbe(
        index=current_index,
        operator="啜泣摇篮",
    )
    current_buff.ft.refinement = 1
    current_buff.ft.cd = cd
    current_buff.sim_instance.tick = tick
    current_template = _BuffTemplate(index=current_index, active=current_active)
    trigger_template = _BuffTemplate(
        index=trigger_index,
        active=active,
        count=0,
        startticks=trigger_startticks,
        endticks=trigger_endticks,
    )
    exist_buff_dict = {
        "啜泣摇篮": {
            current_index: current_template,
            trigger_index: trigger_template,
        }
    }
    current_buff.sim_instance.load_data.exist_buff_dict = exist_buff_dict
    _install_lookup_fakes(
        monkeypatch,
        exist_buff_dict=exist_buff_dict,
        equipper_name="啜泣摇篮",
    )

    return _GateFixture(
        logic=WeepingCradleDMGBonusIncrease(current_buff),
        current_buff=current_buff,
        current_template=current_template,
        trigger_template=trigger_template,
        exist_buff_dict=exist_buff_dict,
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


def _make_jane_fixture(
    monkeypatch: pytest.MonkeyPatch,
    *,
    logic_type: type[Any],
    current_buff: _CurrentBuffProbe,
    current_index: str,
    trigger_index: str,
    active: bool,
    count: float,
) -> _GateFixture:
    current_template = _BuffTemplate(index=current_index)
    trigger_template = _BuffTemplate(
        index=trigger_index,
        active=active,
        count=count,
    )
    exist_buff_dict = {
        "简": {
            current_index: current_template,
            trigger_index: trigger_template,
        }
    }
    current_buff.sim_instance.load_data.exist_buff_dict = exist_buff_dict
    _install_lookup_fakes(
        monkeypatch,
        exist_buff_dict=exist_buff_dict,
        char_name="简",
    )

    return _GateFixture(
        logic=logic_type(current_buff),
        current_buff=current_buff,
        current_template=current_template,
        trigger_template=trigger_template,
        exist_buff_dict=exist_buff_dict,
    )


def _make_jane_gate(
    monkeypatch: pytest.MonkeyPatch,
    *,
    logic_type: type[Any],
    current_index: str,
    trigger_index: str,
    active: bool,
    count: float = 3.0,
) -> _GateFixture:
    current_buff = _CurrentBuffProbe(index=current_index, operator="简")
    return _make_jane_fixture(
        monkeypatch,
        logic_type=logic_type,
        current_buff=current_buff,
        current_index=current_index,
        trigger_index=trigger_index,
        active=active,
        count=count,
    )


def _make_jane_hit_gate(
    monkeypatch: pytest.MonkeyPatch,
    *,
    logic_type: type[Any],
    current_index: str,
    trigger_index: str,
    active: bool,
    count: float,
    maxcount: float = 999.0,
) -> _GateFixture:
    current_buff = _JaneHitBuffProbe(
        index=current_index,
        operator="简",
        maxcount=maxcount,
    )
    return _make_jane_fixture(
        monkeypatch,
        logic_type=logic_type,
        current_buff=current_buff,
        current_index=current_index,
        trigger_index=trigger_index,
        active=active,
        count=count,
    )


def _make_soldier0_anby_fixture(
    monkeypatch: pytest.MonkeyPatch,
    *,
    logic_type: type[Any],
    current_buff: _CurrentBuffProbe,
    current_index: str,
    active: bool,
    count: float = 3.0,
    operating_now: int = 1381,
) -> _GateFixture:
    trigger_index = "Buff-角色-零号·安比-银星触发器"
    current_template = _BuffTemplate(index=current_index)
    trigger_template = _BuffTemplate(
        index=trigger_index,
        active=active,
        count=count,
    )
    exist_buff_dict = {
        "零号·安比": {
            current_index: current_template,
            trigger_index: trigger_template,
        }
    }
    current_buff.sim_instance.load_data.exist_buff_dict = exist_buff_dict
    current_buff.sim_instance.preload.preload_data = SimpleNamespace(
        operating_now=operating_now
    )
    _install_lookup_fakes(
        monkeypatch,
        exist_buff_dict=exist_buff_dict,
        char_name="零号·安比",
    )

    return _GateFixture(
        logic=logic_type(current_buff),
        current_buff=current_buff,
        current_template=current_template,
        trigger_template=trigger_template,
        exist_buff_dict=exist_buff_dict,
    )


def _make_soldier0_anby_gate(
    monkeypatch: pytest.MonkeyPatch,
    *,
    logic_type: type[Any],
    current_index: str,
    active: bool,
    operating_now: int = 1381,
) -> _GateFixture:
    current_buff = _CurrentBuffProbe(index=current_index, operator="零号·安比")
    return _make_soldier0_anby_fixture(
        monkeypatch,
        logic_type=logic_type,
        current_buff=current_buff,
        current_index=current_index,
        active=active,
        operating_now=operating_now,
    )


def _make_soldier0_anby_hit_gate(
    monkeypatch: pytest.MonkeyPatch,
    *,
    active: bool,
    count: float = 3.0,
) -> _GateFixture:
    current_index = "Buff-角色-零号·安比-核心被动-暴击伤害"
    current_buff = _Soldier0AnbyHitBuffProbe(
        index=current_index,
        operator="零号·安比",
    )
    return _make_soldier0_anby_fixture(
        monkeypatch,
        logic_type=Soldier0AnbyCoreSkillCritDMGBonus,
        current_buff=current_buff,
        current_index=current_index,
        active=active,
        count=count,
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
        "startticks",
        "endticks",
    ):
        assert not hasattr(trigger_state, mutating_name)
    with pytest.raises(AttributeError):
        trigger_state.count = 6  # type: ignore[misc]
    assert fixture.logic.record.trigger_buff_0 is fixture.trigger_template


def test_trigger_state_active_helper_does_not_require_full_snapshot_fields() -> None:
    record = SimpleNamespace(
        trigger_buff_0=SimpleNamespace(dy=SimpleNamespace(active=True))
    )

    assert read_trigger_buff_state_active(record) is True
    with pytest.raises(AttributeError):
        read_trigger_buff_state(record)


def test_trigger_state_helper_requires_prepared_trigger_record() -> None:
    with pytest.raises(ValueError, match="trigger_buff_0"):
        read_trigger_buff_state(SimpleNamespace(trigger_buff_0=None))
    with pytest.raises(ValueError, match="trigger_buff_0"):
        read_trigger_buff_state_active(SimpleNamespace(trigger_buff_0=None))


def test_trigger_buff_ref_lookup_preserves_old_template_identity() -> None:
    trigger_template = _BuffTemplate(
        index="Buff-角色-简-核心被动-啮咬触发器",
        active=True,
        count=1,
    )
    lookup = TriggerBuffLookup(
        BuffTemplateRegistryReadPort(
            {"简": {"Buff-角色-简-核心被动-啮咬触发器": trigger_template}}
        )
    )

    result = lookup.find_by_ref(
        TriggerBuffRef.owner("简", "Buff-角色-简-核心被动-啮咬触发器")
    )

    assert result is trigger_template


def test_trigger_buff_ref_lookup_preserves_suffix_collision_behavior() -> None:
    trigger_template = _BuffTemplate(
        index="Buff-驱动盘-灼心摇壶-增伤",
        active=True,
        count=5,
    )
    prefix_match = _BuffTemplate(
        index="Buff-驱动盘-灼心摇壶-增伤-历史副本",
        active=True,
        count=99,
    )
    lookup = TriggerBuffLookup(
        BuffTemplateRegistryReadPort(
            {
                "测试装备者": {
                    "Buff-驱动盘-灼心摇壶-增伤": trigger_template,
                    "Buff-驱动盘-灼心摇壶-增伤-历史副本": prefix_match,
                }
            }
        )
    )

    result = lookup.find_by_ref(TriggerBuffRef.owner("测试装备者", "灼心摇壶-增伤"))

    assert result is trigger_template


def test_trigger_buff_ref_lookup_preserves_duplicate_name_error() -> None:
    duplicate_a = _BuffTemplate(index="Buff-角色-简-重复触发器")
    duplicate_b = _BuffTemplate(index="Buff-角色-简-重复触发器")
    lookup = TriggerBuffLookup(
        BuffTemplateRegistryReadPort(
            {"简": {"a": duplicate_a, "b": duplicate_b}}
        )
    )

    with pytest.raises(ValueError, match="同名buff"):
        lookup.find_by_ref(TriggerBuffRef.owner("简", "重复触发器"))


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
            ("record.trigger_buff_0.dy.active", "record.trigger_buff_0.dy.count"),
            id="astral-voice",
        ),
        pytest.param(
            "JaneCinema1APTransToDmgBonus.py",
            ("record.trigger_buff_0.dy.active",),
            id="jane-cinema1-ap-dmg",
        ),
        pytest.param(
            "JaneCoreSkillStrikeCritDmgBonus.py",
            ("record.trigger_buff_0.dy.active",),
            id="jane-core-crit-dmg",
        ),
        pytest.param(
            "JaneCoreSkillStrikeCritRateBonus.py",
            ("record.trigger_buff_0.dy.active",),
            id="jane-core-crit-rate",
        ),
        pytest.param(
            "JanePassionStateAPTransToATK.py",
            ("record.trigger_buff_0.dy.active",),
            id="jane-passion-ap-atk",
        ),
        pytest.param(
            "JanePassionStatePhyBuildupBonus.py",
            ("record.trigger_buff_0.dy.active",),
            id="jane-passion-buildup",
        ),
        pytest.param(
            "Soldier0AnbyAdditionalSkillDMGBonus.py",
            ("record.trigger_buff_0.dy.active",),
            id="soldier0-additional-skill",
        ),
        pytest.param(
            "Soldier0AnbyCinema4EleResReduce.py",
            ("record.trigger_buff_0.dy.active",),
            id="soldier0-cinema4-ele-res",
        ),
        pytest.param(
            "Soldier0AnbyCoreSkillCritDMGBonus.py",
            ("record.trigger_buff_0.dy.active",),
            id="soldier0-core-crit-dmg",
        ),
        pytest.param(
            "SeveredInnocencELEDMGBonus.py",
            ("record.trigger_buff_0.dy.active", "record.trigger_buff_0.dy.count"),
            id="severed-innocence",
        ),
        pytest.param(
            "YangiCinema1ApBonus.py",
            ("record.trigger_buff_0.dy.active", "record.trigger_buff_0.dy.count"),
            id="yanagi-cinema1-ap",
        ),
        pytest.param(
            "YunkuiTalesSheerAtkBonus.py",
            ("trigger_buff_0.dy.active", "trigger_buff_0.dy.count"),
            id="yunkui-tales",
        ),
        pytest.param(
            "WeepingCradleDMGBonusIncrease.py",
            ("record.trigger_buff_0.dy.active",),
            id="weeping-cradle-active-only",
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


def test_jane_core_skill_crit_rate_uses_typed_trigger_ref_contract() -> None:
    source = (_BUFF_XLOGIC_ROOT / "JaneCoreSkillStrikeCritRateBonus.py").read_text(
        encoding="utf-8"
    )
    compact_source = "".join(source.split())

    assert "TriggerBuffRef.enemy(" in source
    assert 'trigger_buff_0=("enemy",' not in compact_source


_JANE_ACTIVE_GATE_CASES: tuple[tuple[type[Any], str, str], ...] = (
    (
        JaneCinema1APTransToDmgBonus,
        "Buff-角色-简-1画-狂热状态精通转增伤",
        "Buff-角色-简-狂热状态触发器",
    ),
    (
        JaneCoreSkillStrikeCritDmgBonus,
        "Buff-角色-简-核心被动-强击暴击伤害",
        "Buff-角色-简-核心被动-啮咬触发器",
    ),
    (
        JaneCoreSkillStrikeCritRateBonus,
        "Buff-角色-简-核心被动-强击暴击率",
        "Buff-角色-简-核心被动-啮咬触发器",
    ),
    (
        JanePassionStateAPTransToATK,
        "Buff-角色-简-狂热状态精通转攻击力",
        "Buff-角色-简-狂热状态触发器",
    ),
    (
        JanePassionStatePhyBuildupBonus,
        "Buff-角色-简-狂热状态物理积蓄效率",
        "Buff-角色-简-狂热状态触发器",
    ),
)


@pytest.mark.parametrize(
    ("logic_type", "current_index", "trigger_index"),
    _JANE_ACTIVE_GATE_CASES,
)
@pytest.mark.parametrize(
    ("active", "expected"),
    [
        pytest.param(False, False, id="inactive"),
        pytest.param(True, True, id="active"),
    ],
)
def test_jane_owner_family_trigger_active_gates_are_read_only(
    monkeypatch: pytest.MonkeyPatch,
    *,
    logic_type: type[Any],
    current_index: str,
    trigger_index: str,
    active: bool,
    expected: bool,
) -> None:
    fixture = _make_jane_gate(
        monkeypatch,
        logic_type=logic_type,
        current_index=current_index,
        trigger_index=trigger_index,
        active=active,
    )

    assert fixture.logic.special_judge_logic() is expected
    assert fixture.logic.special_exit_logic() is (not expected)
    _assert_lazy_record_and_trigger_identity(fixture)
    assert fixture.current_buff.dy.count == 0.0
    assert fixture.current_buff.sim_instance.schedule_data.event_list == []


@pytest.mark.parametrize(
    ("logic_type", "current_index", "trigger_index", "ap", "maxcount", "expected"),
    [
        pytest.param(
            JaneCinema1APTransToDmgBonus,
            "Buff-角色-简-1画-狂热状态精通转增伤",
            "Buff-角色-简-狂热状态触发器",
            900.0,
            70.0,
            70.0,
            id="cinema1-ap-to-dmg-cap",
        ),
        pytest.param(
            JaneCoreSkillStrikeCritRateBonus,
            "Buff-角色-简-核心被动-强击暴击率",
            "Buff-角色-简-核心被动-啮咬触发器",
            250.0,
            999.0,
            80.0,
            id="core-crit-rate-ap-formula",
        ),
        pytest.param(
            JanePassionStateAPTransToATK,
            "Buff-角色-简-狂热状态精通转攻击力",
            "Buff-角色-简-狂热状态触发器",
            155.8,
            999.0,
            35.0,
            id="passion-ap-to-atk-floor",
        ),
    ],
)
def test_jane_ap_hit_paths_remain_formula_owned(
    monkeypatch: pytest.MonkeyPatch,
    *,
    logic_type: type[Any],
    current_index: str,
    trigger_index: str,
    ap: float,
    maxcount: float,
    expected: float,
) -> None:
    formula_contexts: list[object] = []

    def _read_anomaly_proficiency(
        self: CalculatorBuffAttributeReader,
        context: object,
    ) -> float:
        formula_contexts.append(context)
        return ap

    monkeypatch.setattr(
        CalculatorBuffAttributeReader,
        "read_anomaly_proficiency",
        _read_anomaly_proficiency,
    )
    fixture = _make_jane_hit_gate(
        monkeypatch,
        logic_type=logic_type,
        current_index=current_index,
        trigger_index=trigger_index,
        active=False,
        count=99.0,
        maxcount=maxcount,
    )
    hit_buff = cast(_JaneHitBuffProbe, fixture.current_buff)

    fixture.logic.special_hit_logic()

    assert len(formula_contexts) == 1
    assert hit_buff.dy.count == pytest.approx(expected)
    assert [event[0] for event in hit_buff.effect_events] == [
        "simple_start",
        "set_count",
        "update_to_buff_0",
    ]
    _assert_lazy_record_and_trigger_identity(fixture)
    assert fixture.trigger_template.dy.active is False
    assert fixture.current_buff.sim_instance.schedule_data.event_list == []


_SOLDIER0_ANBY_ACTIVE_GATE_CASES: tuple[tuple[type[Any], str], ...] = (
    (
        Soldier0AnbyCinema4EleResReduce,
        "Buff-角色-零号·安比-4画-电抗降低",
    ),
    (
        Soldier0AnbyCoreSkillCritDMGBonus,
        "Buff-角色-零号·安比-核心被动-暴击伤害",
    ),
)


@pytest.mark.parametrize(
    ("logic_type", "current_index"),
    _SOLDIER0_ANBY_ACTIVE_GATE_CASES,
)
@pytest.mark.parametrize(
    ("active", "expected"),
    [
        pytest.param(False, False, id="inactive"),
        pytest.param(True, True, id="active"),
    ],
)
def test_soldier0_anby_trigger_active_gates_are_read_only(
    monkeypatch: pytest.MonkeyPatch,
    *,
    logic_type: type[Any],
    current_index: str,
    active: bool,
    expected: bool,
) -> None:
    fixture = _make_soldier0_anby_gate(
        monkeypatch,
        logic_type=logic_type,
        current_index=current_index,
        active=active,
    )

    assert fixture.logic.special_judge_logic() is expected
    _assert_lazy_record_and_trigger_identity(fixture)
    assert fixture.logic.record.char.CID == 1381
    assert fixture.current_buff.dy.count == 0.0
    assert fixture.current_buff.sim_instance.schedule_data.event_list == []


@pytest.mark.parametrize(
    ("active", "operating_now", "expected"),
    [
        pytest.param(False, 1381, False, id="inactive-correct-operator"),
        pytest.param(True, 1381, True, id="active-correct-operator"),
        pytest.param(True, 1261, False, id="active-wrong-operator"),
    ],
)
def test_soldier0_anby_additional_skill_preserves_operating_character_gate(
    monkeypatch: pytest.MonkeyPatch,
    *,
    active: bool,
    operating_now: int,
    expected: bool,
) -> None:
    fixture = _make_soldier0_anby_gate(
        monkeypatch,
        logic_type=Soldier0AnbyAdditionalSkillDMGBonus,
        current_index="Buff-角色-零号·安比-额外能力-全队增伤",
        active=active,
        operating_now=operating_now,
    )

    assert fixture.logic.special_judge_logic() is expected
    _assert_lazy_record_and_trigger_identity(fixture)
    assert (
        fixture.logic.record.preload_data
        is fixture.current_buff.sim_instance.preload.preload_data
    )
    assert fixture.logic.record.preload_data.operating_now == operating_now
    assert fixture.current_buff.dy.count == 0.0
    assert fixture.current_buff.sim_instance.schedule_data.event_list == []


def test_soldier0_anby_core_crit_damage_hit_path_remains_formula_owned(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    formula_contexts: list[object] = []

    def _read_personal_crit_damage(
        self: CalculatorBuffAttributeReader,
        context: object,
    ) -> float:
        formula_contexts.append(context)
        return 2.5

    monkeypatch.setattr(
        CalculatorBuffAttributeReader,
        "read_personal_crit_damage",
        _read_personal_crit_damage,
    )
    fixture = _make_soldier0_anby_hit_gate(monkeypatch, active=True, count=5.0)
    hit_buff = cast(_Soldier0AnbyHitBuffProbe, fixture.current_buff)

    assert fixture.logic.special_judge_logic() is True
    fixture.logic.special_hit_logic()

    assert len(formula_contexts) == 1
    assert hit_buff.dy.count == pytest.approx(75.0)
    assert [event[0] for event in hit_buff.effect_events] == [
        "simple_start",
        "set_count",
        "update_to_buff_0",
    ]
    assert hit_buff.effect_events[0] == (
        "simple_start",
        (100, fixture.exist_buff_dict["零号·安比"]),
    )
    assert hit_buff.effect_events[2] == (
        "update_to_buff_0",
        (fixture.current_template,),
    )
    _assert_lazy_record_and_trigger_identity(fixture)
    assert cast(float, fixture.logic.record.trigger_buff_0.dy.count) == 5.0
    assert fixture.current_buff.sim_instance.schedule_data.event_list == []


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


@pytest.mark.parametrize(
    ("active", "count", "expected"),
    [
        pytest.param(False, 2, False, id="inactive-below-required-count"),
        pytest.param(False, 4, False, id="inactive-above-required-count"),
        pytest.param(True, 2, False, id="below-required-count"),
        pytest.param(True, 3, True, id="required-count"),
        pytest.param(True, 4, False, id="above-required-count"),
    ],
)
def test_severed_innocence_count_gate_thresholds_are_read_only(
    monkeypatch: pytest.MonkeyPatch,
    *,
    active: bool,
    count: float,
    expected: bool,
) -> None:
    fixture = _make_equipment_gate(
        monkeypatch,
        logic_type=SeveredInnocencELEDMGBonus,
        current_index="Buff-音擎-牺牲洁纯-电属性伤害提高",
        trigger_index="Buff-音擎-牺牲洁纯-触发暴伤",
        equipper_name="牺牲洁纯",
        active=active,
        count=count,
    )

    assert fixture.logic.special_judge_logic() is expected
    _assert_lazy_record_and_trigger_identity(fixture)
    assert fixture.current_buff.dy.count == 0.0
    assert fixture.current_buff.sim_instance.schedule_data.event_list == []


def test_severed_innocence_count_three_inactive_trigger_still_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _make_equipment_gate(
        monkeypatch,
        logic_type=SeveredInnocencELEDMGBonus,
        current_index="Buff-音擎-牺牲洁纯-电属性伤害提高",
        trigger_index="Buff-音擎-牺牲洁纯-触发暴伤",
        equipper_name="牺牲洁纯",
        active=False,
        count=3,
    )

    with pytest.raises(ValueError, match="有层数但是未激活"):
        fixture.logic.special_judge_logic()

    _assert_lazy_record_and_trigger_identity(fixture)
    assert fixture.current_buff.dy.count == 0.0
    assert fixture.current_buff.sim_instance.schedule_data.event_list == []


@pytest.mark.parametrize(
    ("active", "count", "expected"),
    [
        pytest.param(False, 3, False, id="inactive-required-count"),
        pytest.param(True, 2, False, id="below-required-count"),
        pytest.param(True, 3, True, id="required-count"),
        pytest.param(True, 4, False, id="above-required-count"),
    ],
)
def test_yunkui_tales_local_trigger_alias_gate_is_read_only(
    monkeypatch: pytest.MonkeyPatch,
    *,
    active: bool,
    count: float,
    expected: bool,
) -> None:
    fixture = _make_equipment_gate(
        monkeypatch,
        logic_type=YunkuiTalesSheerAtkBonus,
        current_index="Buff-驱动盘-云岿如我-四件套-贯穿力提升",
        trigger_index="Buff-驱动盘-云岿如我-四件套-暴击率提升",
        equipper_name="云岿如我",
        active=active,
        count=count,
    )

    assert fixture.logic.special_judge_logic() is expected
    _assert_lazy_record_and_trigger_identity(fixture)
    assert fixture.logic.record.trigger_buff_0 is fixture.trigger_template
    assert fixture.current_buff.dy.count == 0.0
    assert fixture.current_buff.sim_instance.schedule_data.event_list == []


def test_yunkui_tales_source_keeps_local_alias_without_direct_state_reads() -> None:
    source = (_BUFF_XLOGIC_ROOT / "YunkuiTalesSheerAtkBonus.py").read_text(
        encoding="utf-8"
    )

    assert "trigger_buff_0: Buff = self.record.trigger_buff_0" in source
    assert "read_trigger_buff_state(self.record)" in source
    assert "trigger_buff_0.dy.active" not in source
    assert "trigger_buff_0.dy.count" not in source


@pytest.mark.parametrize(
    ("active", "expected", "expected_last_update_tick"),
    [
        pytest.param(False, False, 0, id="inactive-trigger"),
        pytest.param(True, True, 100, id="active-trigger-cooldown-ready"),
    ],
)
def test_weeping_cradle_active_gate_uses_helper_and_preserves_cooldown(
    monkeypatch: pytest.MonkeyPatch,
    *,
    active: bool,
    expected: bool,
    expected_last_update_tick: int,
) -> None:
    fixture = _make_weeping_cradle_gate(monkeypatch, active=active)

    assert fixture.logic.special_judge_logic() is expected
    _assert_lazy_record_and_trigger_identity(fixture)
    assert fixture.logic.record.last_update_tick == expected_last_update_tick
    assert fixture.current_buff.sim_instance.schedule_data.event_list == []
    current_buff = cast(_WeepingCradleEffectBuffProbe, fixture.current_buff)
    assert current_buff.effect_events == []

    if active:
        assert fixture.logic.special_judge_logic() is False
        assert fixture.logic.record.last_update_tick == expected_last_update_tick
        assert current_buff.effect_events == []


def test_weeping_cradle_effect_mirrors_trigger_time_window_after_start(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _make_weeping_cradle_gate(
        monkeypatch,
        active=True,
        current_active=False,
        trigger_startticks=25,
        trigger_endticks=85,
    )

    assert fixture.logic.special_judge_logic() is True
    fixture.logic.special_effect_logic()

    _assert_lazy_record_and_trigger_identity(fixture)
    assert fixture.logic.record.sub_exist_buff_dict is fixture.exist_buff_dict["啜泣摇篮"]
    current_buff = cast(_WeepingCradleEffectBuffProbe, fixture.current_buff)
    assert current_buff.dy.startticks == 25
    assert current_buff.dy.endticks == 85
    assert current_buff.effect_events == [
        ("simple_start", (100, fixture.exist_buff_dict["啜泣摇篮"])),
        ("set_startticks", (25,)),
        ("set_endticks", (85,)),
        ("update_to_buff_0", (fixture.current_template,)),
    ]
    assert fixture.current_buff.sim_instance.schedule_data.event_list == []


def test_weeping_cradle_active_current_buff_self_stack_keeps_time_window(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _make_weeping_cradle_gate(
        monkeypatch,
        active=True,
        current_active=True,
        trigger_startticks=25,
        trigger_endticks=85,
    )

    assert fixture.logic.special_judge_logic() is True
    fixture.logic.special_effect_logic()

    _assert_lazy_record_and_trigger_identity(fixture)
    current_buff = cast(_WeepingCradleEffectBuffProbe, fixture.current_buff)
    assert current_buff.dy.startticks == 0
    assert current_buff.dy.endticks == 0
    assert current_buff.effect_events == [
        (
            "simple_start",
            (
                100,
                fixture.exist_buff_dict["啜泣摇篮"],
                {"no_start": True, "no_end": True},
            ),
        ),
    ]
    assert fixture.current_buff.sim_instance.schedule_data.event_list == []


def test_weeping_cradle_source_keeps_time_window_mirror_outside_snapshot() -> None:
    source = (_BUFF_XLOGIC_ROOT / "WeepingCradleDMGBonusIncrease.py").read_text(
        encoding="utf-8"
    )

    assert "read_trigger_buff_state(self.record)" in source
    assert "self.record.trigger_buff_0.dy.active" not in source
    assert "self.record.trigger_buff_0.dy.startticks" in source
    assert "self.record.trigger_buff_0.dy.endticks" in source
    assert "read_trigger_buff_state(self.record).startticks" not in source
    assert "read_trigger_buff_state(self.record).endticks" not in source


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
    "count",
    [
        pytest.param(0, id="zero-count"),
        pytest.param(5, id="normal-count"),
        pytest.param(99, id="high-count"),
    ],
)
def test_astral_voice_effect_count_mirror_uses_trigger_state_helper(
    monkeypatch: pytest.MonkeyPatch,
    *,
    count: float,
) -> None:
    fixture = _make_astral_voice_effect_gate(monkeypatch, count=count)

    fixture.logic.special_effect_logic()

    _assert_lazy_record_and_trigger_identity(fixture)
    assert fixture.logic.record.sub_exist_buff_dict is fixture.exist_buff_dict["静听嘉音"]
    assert fixture.current_buff.dy.count == count
    assert fixture.current_buff.sim_instance.schedule_data.event_list == []
    current_buff = cast(_AstralVoiceEffectBuffProbe, fixture.current_buff)
    assert current_buff.effect_events == [
        ("simple_start", (100, fixture.exist_buff_dict["静听嘉音"])),
        ("set_count", (count,)),
        ("update_to_buff_0", (fixture.current_template,)),
    ]


def test_astral_voice_effect_count_mirror_keeps_runtime_boundaries_out_of_scope() -> None:
    source = (_BUFF_XLOGIC_ROOT / "AstralVoice.py").read_text(encoding="utf-8")

    assert "BuffRuntimeReadPort" not in source
    assert "RuntimeCommandPort" not in source
    assert "ScheduleDispatchPort" not in source
    assert "publish_scheduled" not in source
    assert "listener_manager.broadcast_event" not in source


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
    assert fixture.current_buff.sim_instance.schedule_data.event_list == []


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
