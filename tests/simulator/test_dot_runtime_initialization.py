from __future__ import annotations

import inspect
from types import SimpleNamespace
from typing import NoReturn

import pytest

from zsim.sim_progress.Dot.Dots.Shock import Shock


class _ForbiddenLayer:
    def __init__(self, label: str) -> None:
        self._label = label

    def _fail(self, action: str) -> NoReturn:
        raise AssertionError(
            f"Shock duration initialization should not touch {self._label}: {action}"
        )

    def __getattr__(self, name: str) -> object:
        self._fail(f"attribute {name}")

    def __call__(self, *args: object, **kwargs: object) -> object:
        self._fail("call")

    def __bool__(self) -> bool:
        self._fail("truthiness")

    def append(self, item: object) -> None:
        self._fail("append")


def _build_sim_instance(name_box, exist_buff_dict):
    return SimpleNamespace(
        init_data=SimpleNamespace(name_box=name_box),
        load_data=SimpleNamespace(exist_buff_dict=exist_buff_dict),
        schedule_data=_ForbiddenLayer("ScheduleDispatchPort / schedule_data"),
        listener_manager=SimpleNamespace(
            broadcast_event=_ForbiddenLayer("listener broadcast"),
        ),
        runtime_command_port=_ForbiddenLayer("RuntimeCommandPort"),
        dynamic_dot_list=_ForbiddenLayer("dynamic_dot_list"),
        calculator=_ForbiddenLayer("Calculator"),
        cal_anomaly=_ForbiddenLayer("CalAnomaly"),
    )


def test_shock_dot_feature_requires_sim_instance():
    with pytest.raises(ValueError, match="sim_instance is None"):
        Shock.DotFeature(sim_instance=None)


def test_shock_dot_duration_defaults_to_600_without_rina():
    sim_instance = _build_sim_instance(
        name_box=["安比", "妮可"],
        exist_buff_dict={},
    )

    feature = Shock.DotFeature(sim_instance=sim_instance)

    assert feature.max_duration == 600
    assert feature.char_name_box == ["安比", "妮可"]
    assert feature.exist_buff_dict == {}


def test_shock_dot_duration_defaults_to_600_when_rina_passive_is_absent():
    sim_instance = _build_sim_instance(
        name_box=["丽娜", "安比"],
        exist_buff_dict={"丽娜": {}},
    )

    feature = Shock.DotFeature(sim_instance=sim_instance)

    assert feature.max_duration == 600
    assert feature.char_name_box == ["丽娜", "安比"]
    assert feature.exist_buff_dict == {"丽娜": {}}


def test_shock_dot_duration_extends_to_780_when_rina_passive_exists():
    passive_index = "Buff-角色-丽娜-组队被动-延长感电"
    passive_marker = object()
    sim_instance = _build_sim_instance(
        name_box=["丽娜", "安比"],
        exist_buff_dict={"丽娜": {passive_index: passive_marker}},
    )

    feature = Shock.DotFeature(sim_instance=sim_instance)

    assert feature.max_duration == 780
    assert feature.char_name_box == ["丽娜", "安比"]
    assert feature.exist_buff_dict == {"丽娜": {passive_index: passive_marker}}


def test_shock_dot_duration_initialization_stays_in_read_only_layer():
    source = inspect.getsource(Shock.DotFeature.__post_init__)

    forbidden_terms = [
        "ScheduleDispatchPort",
        "publish_scheduled",
        "schedule_data",
        "dynamic_dot_list",
        "listener_manager",
        "broadcast_event",
        "RuntimeCommandPort",
        "runtime_command",
        "Calculator",
        "CalAnomaly",
    ]

    for term in forbidden_terms:
        assert term not in source
