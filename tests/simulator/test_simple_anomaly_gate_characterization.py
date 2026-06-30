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
from zsim.sim_progress.Buff.BuffXLogic.ElectroLipGlossAtkAndDmgBonus import (
    ElectroLipGlossAtkAndDmgBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.JaneAdditionalAbilityPhyBuildupBonus import (
    JaneAdditionalAbilityPhyBuildupBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.MarcatoDesireAtkBonus import (
    MarcatoDesireAtkBonus,
)
from zsim.sim_progress.Buff.BuffXLogic.TimeweaverApBonus import TimeweaverApBonus
from zsim.sim_progress.Load import LoadingMission
from zsim.sim_progress.Preload import SkillNode


class _FailFastEventList(list[object]):
    def append(self, item: object) -> None:
        raise AssertionError("simple anomaly gate tests must not publish events")


class _FailFastRuntimeCommandPort:
    def __getattr__(self, name: str) -> Callable[..., None]:
        def _fail(*args: object, **kwargs: object) -> None:
            raise AssertionError(
                f"simple anomaly gate tests must not touch runtime writes: {name}"
            )

        return _fail


class _FailFastListenerManager:
    def broadcast_event(self, *args: object, **kwargs: object) -> None:
        raise AssertionError("simple anomaly gate tests must not broadcast listeners")


class _CurrentBuffDynamicState:
    @property
    def count(self) -> float:
        return 0.0

    @count.setter
    def count(self, value: float) -> None:
        raise AssertionError("simple anomaly gates must not mutate current dy.count")


class _BuffTemplate:
    def __init__(self, *, index: str) -> None:
        self.ft = SimpleNamespace(index=index)
        self.dy = SimpleNamespace(count=0.0)
        self.history = SimpleNamespace(record=None)


class _CurrentBuffProbe:
    def __init__(self, *, index: str, tick: int = 100) -> None:
        runtime_command_port = _FailFastRuntimeCommandPort()
        self.ft = SimpleNamespace(index=index)
        self.dy: Any = _CurrentBuffDynamicState()
        self.sim_instance = SimpleNamespace(
            tick=tick,
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
        raise AssertionError("simple anomaly gates must not call simple_start")

    def simple_exit(self, *args: object, **kwargs: object) -> None:
        raise AssertionError("simple anomaly gates must not call simple_exit")

    def update_to_buff_0(self, *args: object, **kwargs: object) -> None:
        raise AssertionError("simple anomaly gates must not call update_to_buff_0")


class _AnomalyDynamicProbe:
    def __init__(self, *, under_anomaly: bool) -> None:
        self.under_anomaly = under_anomaly
        self.calls: list[str] = []
        self.dynamic_debuff_list: list[object] = []
        self.dynamic_dot_list: list[object] = []

    def is_under_anomaly(self) -> bool:
        self.calls.append("is_under_anomaly")
        return self.under_anomaly


@dataclass(frozen=True)
class _SimpleGateFixture:
    logic: Any
    current_buff: _CurrentBuffProbe
    current_template: _BuffTemplate
    enemy_dynamic: _AnomalyDynamicProbe
    exist_buff_dict: dict[str, dict[str, _BuffTemplate]]


class _PreparationContextProbe:
    def __init__(
        self,
        *,
        exist_buff_dict: dict[str, dict[str, _BuffTemplate]],
        equipper_name: str,
        enemy: object | None,
    ) -> None:
        self._exist_buff_dict = exist_buff_dict
        self._equipper_name = equipper_name
        self._enemy = enemy

    def find_sub_exist_buff_dict(self, owner_name: str) -> dict[str, _BuffTemplate]:
        return self._exist_buff_dict[owner_name]

    def find_equipper(self, item_name: str) -> str:
        return self._equipper_name

    def find_char_from_cid(self, cid: int) -> SimpleNamespace:
        return SimpleNamespace(NAME=self._equipper_name, CID=cid)

    def find_char_from_name(self, name: str) -> SimpleNamespace:
        return SimpleNamespace(NAME=name)

    def find_enemy(self) -> object:
        assert self._enemy is not None
        return self._enemy


def _install_lookup_fakes(
    monkeypatch: pytest.MonkeyPatch,
    *,
    logic_type: type[Any] | None = None,
    exist_buff_dict: dict[str, dict[str, _BuffTemplate]],
    equipper_name: str = "测试装备者",
    enemy: object | None = None,
) -> None:
    if logic_type is not None:
        module = importlib.import_module(logic_type.__module__)
        if hasattr(module, "build_preparation_context_from_buff"):
            preparation_context = _PreparationContextProbe(
                exist_buff_dict=exist_buff_dict,
                equipper_name=equipper_name,
                enemy=enemy,
            )
            monkeypatch.setattr(
                module,
                "build_preparation_context_from_buff",
                lambda buff_instance: preparation_context,
            )

            def fake_check_preparation(
                *,
                buff_instance: object,
                buff_0: _BuffTemplate,
                preparation_context: object | None = None,
                **kwargs: object,
            ) -> None:
                record = buff_0.history.record
                if "char_CID" in kwargs:
                    record.char = SimpleNamespace(
                        NAME=equipper_name,
                        CID=kwargs["char_CID"],
                    )
                if "enemy" in kwargs:
                    record.enemy = enemy
                if "equipper" in kwargs:
                    record.equipper = equipper_name

            monkeypatch.setattr(module, "check_preparation", fake_check_preparation)
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
        "find_char_from_name",
        lambda NAME, sim_instance=None: SimpleNamespace(NAME=NAME),
    )
    monkeypatch.setattr(
        JudgeTools,
        "find_char_from_CID",
        lambda char_CID, sim_instance=None: SimpleNamespace(NAME=equipper_name, CID=char_CID),
    )
    if enemy is not None:
        monkeypatch.setattr(
            JudgeTools,
            "find_enemy",
            lambda sim_instance=None: enemy,
        )


def _make_gate_fixture(
    monkeypatch: pytest.MonkeyPatch,
    *,
    logic_type: type[Any],
    current_index: str,
    owner_name: str,
    under_anomaly: bool,
    tick: int = 100,
) -> _SimpleGateFixture:
    current_buff = _CurrentBuffProbe(index=current_index, tick=tick)
    current_template = _BuffTemplate(index=current_index)
    exist_buff_dict = {owner_name: {current_index: current_template}}
    current_buff.sim_instance.load_data.exist_buff_dict = exist_buff_dict
    logic = logic_type(current_buff)
    enemy_dynamic = _AnomalyDynamicProbe(under_anomaly=under_anomaly)
    enemy = SimpleNamespace(dynamic=enemy_dynamic)
    _install_lookup_fakes(
        monkeypatch,
        logic_type=logic_type,
        exist_buff_dict=exist_buff_dict,
        equipper_name=owner_name,
        enemy=enemy,
    )

    return _SimpleGateFixture(
        logic=logic,
        current_buff=current_buff,
        current_template=current_template,
        enemy_dynamic=enemy_dynamic,
        exist_buff_dict=exist_buff_dict,
    )


def _make_skill_node(
    *,
    char_name: str,
    trigger_buff_level: int,
    hit_now: bool,
    tick: int = 100,
) -> SkillNode:
    skill = SimpleNamespace(
        skill_tag=f"{char_name}_simple_anomaly_gate",
        char_name=char_name,
        hit_times=1,
        labels=None,
        ticks=2,
        tick_list=[1] if hit_now else [3],
        trigger_buff_level=trigger_buff_level,
        element_type=0,
        heavy_attack=False,
    )
    skill_node = SkillNode(skill, preload_tick=tick - 1)
    loading_mission = LoadingMission(skill_node)
    loading_mission.mission_start(timenow=tick - 1, report=False)
    return skill_node


def _assert_no_side_effects(fixture: _SimpleGateFixture) -> None:
    assert fixture.current_buff.dy.count == 0.0
    assert fixture.current_template.dy.count == 0.0
    assert fixture.current_buff.sim_instance.schedule_data.event_list == []
    assert fixture.enemy_dynamic.dynamic_dot_list == []
    assert fixture.enemy_dynamic.dynamic_debuff_list == []


@pytest.mark.parametrize(
    ("under_anomaly", "expected_judge", "expected_exit"),
    [
        pytest.param(False, False, True, id="no-anomaly"),
        pytest.param(True, True, False, id="active-anomaly"),
    ],
)
def test_electro_lip_gloss_simple_anomaly_gate_is_read_only(
    monkeypatch: pytest.MonkeyPatch,
    *,
    under_anomaly: bool,
    expected_judge: bool,
    expected_exit: bool,
) -> None:
    fixture = _make_gate_fixture(
        monkeypatch,
        logic_type=ElectroLipGlossAtkAndDmgBonus,
        current_index="Buff-音擎-触电唇彩-攻击力与伤害提高",
        owner_name="测试装备者",
        under_anomaly=under_anomaly,
    )

    assert fixture.logic.special_judge_logic() is expected_judge
    assert fixture.logic.special_exit_logic() is expected_exit

    assert fixture.logic.buff_0 is fixture.current_template
    assert fixture.logic.record is fixture.current_template.history.record
    assert fixture.enemy_dynamic.calls == ["is_under_anomaly", "is_under_anomaly"]
    _assert_no_side_effects(fixture)


@pytest.mark.parametrize(
    ("under_anomaly", "expected_judge", "expected_exit"),
    [
        pytest.param(False, False, True, id="no-anomaly"),
        pytest.param(True, True, False, id="active-anomaly"),
    ],
)
def test_jane_additional_ability_simple_anomaly_gate_is_read_only(
    monkeypatch: pytest.MonkeyPatch,
    *,
    under_anomaly: bool,
    expected_judge: bool,
    expected_exit: bool,
) -> None:
    fixture = _make_gate_fixture(
        monkeypatch,
        logic_type=JaneAdditionalAbilityPhyBuildupBonus,
        current_index="Buff-角色-简-组队被动-物理积蓄效率提高",
        owner_name="简",
        under_anomaly=under_anomaly,
    )

    assert fixture.logic.special_judge_logic() is expected_judge
    assert fixture.logic.special_exit_logic() is expected_exit

    assert fixture.logic.buff_0 is fixture.current_template
    assert fixture.logic.record is fixture.current_template.history.record
    assert fixture.enemy_dynamic.calls == ["is_under_anomaly", "is_under_anomaly"]
    _assert_no_side_effects(fixture)


@pytest.mark.parametrize(
    ("under_anomaly", "expected"),
    [
        pytest.param(False, False, id="no-anomaly"),
        pytest.param(True, True, id="active-anomaly"),
    ],
)
def test_marcato_desire_simple_anomaly_hit_gate_is_read_only(
    monkeypatch: pytest.MonkeyPatch,
    *,
    under_anomaly: bool,
    expected: bool,
) -> None:
    fixture = _make_gate_fixture(
        monkeypatch,
        logic_type=MarcatoDesireAtkBonus,
        current_index="Buff-音擎-强音热望-攻击力提高",
        owner_name="测试装备者",
        under_anomaly=under_anomaly,
    )
    skill_node = _make_skill_node(
        char_name="测试装备者",
        trigger_buff_level=2,
        hit_now=True,
    )

    assert fixture.logic.special_judge_logic(skill_node=skill_node) is expected

    assert fixture.logic.buff_0 is fixture.current_template
    assert fixture.logic.record is fixture.current_template.history.record
    assert fixture.enemy_dynamic.calls == ["is_under_anomaly"]
    _assert_no_side_effects(fixture)


def test_marcato_desire_skips_anomaly_read_when_hit_prerequisites_fail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _make_gate_fixture(
        monkeypatch,
        logic_type=MarcatoDesireAtkBonus,
        current_index="Buff-音擎-强音热望-攻击力提高",
        owner_name="测试装备者",
        under_anomaly=True,
    )
    skill_node = _make_skill_node(
        char_name="测试装备者",
        trigger_buff_level=1,
        hit_now=True,
    )

    assert fixture.logic.special_judge_logic(skill_node=skill_node) is False

    assert fixture.enemy_dynamic.calls == []
    _assert_no_side_effects(fixture)


@pytest.mark.parametrize(
    ("under_anomaly", "expected"),
    [
        pytest.param(False, False, id="no-anomaly"),
        pytest.param(True, True, id="active-anomaly"),
    ],
)
def test_timeweaver_simple_anomaly_hit_gate_is_read_only(
    monkeypatch: pytest.MonkeyPatch,
    *,
    under_anomaly: bool,
    expected: bool,
) -> None:
    fixture = _make_gate_fixture(
        monkeypatch,
        logic_type=TimeweaverApBonus,
        current_index="Buff-音擎-时流贤者-电属性积蓄效率提高",
        owner_name="测试装备者",
        under_anomaly=under_anomaly,
    )
    skill_node = _make_skill_node(
        char_name="测试装备者",
        trigger_buff_level=1,
        hit_now=True,
    )

    assert fixture.logic.special_judge_logic(skill_node=skill_node) is expected

    assert fixture.logic.buff_0 is fixture.current_template
    assert fixture.logic.record is fixture.current_template.history.record
    assert fixture.enemy_dynamic.calls == ["is_under_anomaly"]
    _assert_no_side_effects(fixture)


def test_timeweaver_skips_anomaly_read_when_hit_prerequisites_fail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _make_gate_fixture(
        monkeypatch,
        logic_type=TimeweaverApBonus,
        current_index="Buff-音擎-时流贤者-电属性积蓄效率提高",
        owner_name="测试装备者",
        under_anomaly=True,
    )
    skill_node = _make_skill_node(
        char_name="测试装备者",
        trigger_buff_level=3,
        hit_now=True,
    )

    assert fixture.logic.special_judge_logic(skill_node=skill_node) is False

    assert fixture.enemy_dynamic.calls == []
    _assert_no_side_effects(fixture)
