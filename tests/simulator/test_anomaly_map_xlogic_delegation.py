from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Callable, cast

import pytest

import zsim.sim_progress.Buff.BuffXLogic.AnomalyDebuffExitJudge as anomaly_module
from zsim.sim_progress.Buff.BuffXLogic.enemy_anomaly_map_read import (
    read_enemy_anomaly_state,
)


SUPPORTED_ANOMALY_INDEXES = tuple(
    anomaly_module.anomaly_statement_dict.items()
)
SUPPORTED_ANOMALY_NAMES = tuple(anomaly_module.anomaly_statement_dict.values())


class _DynamicProbe:
    def __init__(self, **values: object) -> None:
        self._values = values
        self.reads: list[str] = []

    def set_value(self, name: str, value: object) -> None:
        self._values[name] = value

    def __getattribute__(self, name: str) -> Any:
        if name in SUPPORTED_ANOMALY_NAMES:
            reads = object.__getattribute__(self, "reads")
            values = object.__getattribute__(self, "_values")
            reads.append(name)
            if name not in values:
                raise AssertionError(f"unexpected sibling anomaly read: {name}")
            return values[name]
        return object.__getattribute__(self, name)


class _EnemyProbe:
    _FORBIDDEN_SURFACES = frozenset(
        {
            "history",
            "record",
            "event_list",
            "listener_manager",
            "runtime_command_port",
            "action_stack",
            "effect_count",
            "disorder",
        }
    )

    def __init__(self, dynamic: _DynamicProbe) -> None:
        self.dynamic = dynamic

    def __getattribute__(self, name: str) -> Any:
        if name in object.__getattribute__(self, "_FORBIDDEN_SURFACES"):
            raise AssertionError(f"unexpected runtime or old-container read: {name}")
        return object.__getattribute__(self, name)


class _BuffInstanceProbe:
    def __init__(self, *, index: str, sim_instance: object) -> None:
        self.ft = SimpleNamespace(index=index)
        self.sim_instance = sim_instance
        self.logic: anomaly_module.AnomalyDebuffExitJudge | None = None


def _make_logic(
    *,
    index: str,
    enemy: _EnemyProbe | None,
) -> anomaly_module.AnomalyDebuffExitJudge:
    buff_instance = _BuffInstanceProbe(index=index, sim_instance=object())
    logic = anomaly_module.AnomalyDebuffExitJudge(cast(Any, buff_instance))
    buff_instance.logic = logic
    logic.enemy = enemy
    return logic


@pytest.mark.parametrize(("buff_index", "anomaly_name"), SUPPORTED_ANOMALY_INDEXES)
@pytest.mark.parametrize(
    ("previous_state", "current_state", "expected_exit"),
    [
        pytest.param(True, False, True, id="falling-edge"),
        pytest.param(False, False, False, id="unchanged-inactive"),
        pytest.param(True, True, False, id="unchanged-active"),
    ],
)
def test_anomaly_debuff_exit_judge_delegates_supported_state_read_and_update_order(
    monkeypatch: pytest.MonkeyPatch,
    *,
    buff_index: str,
    anomaly_name: str,
    previous_state: bool,
    current_state: bool,
    expected_exit: bool,
) -> None:
    enemy = _EnemyProbe(_DynamicProbe(**{anomaly_name: current_state}))
    logic = _make_logic(index=buff_index, enemy=enemy)
    setattr(logic, f"last_{anomaly_name}", previous_state)
    helper_calls: list[tuple[_EnemyProbe, str]] = []
    detect_events: list[tuple[str, object, object]] = []

    def fake_read_enemy_anomaly_state(
        read_enemy: object,
        read_name: str,
    ) -> object:
        helper_calls.append((cast(_EnemyProbe, read_enemy), read_name))
        return read_enemy_anomaly_state(cast(Any, read_enemy), read_name)

    def fake_detect_edge(
        pair: list[object],
        mode_func: Callable[[object, object], bool],
    ) -> bool:
        detect_events.append(("detect", tuple(pair), getattr(logic, f"last_{anomaly_name}")))
        result = mode_func(pair[0], pair[1])
        detect_events.append(("result", result, getattr(logic, f"last_{anomaly_name}")))
        return result

    monkeypatch.setattr(
        anomaly_module,
        "read_enemy_anomaly_state",
        fake_read_enemy_anomaly_state,
    )
    monkeypatch.setattr(
        anomaly_module.JudgeTools,
        "find_enemy",
        pytest.fail,
    )
    monkeypatch.setattr(anomaly_module.JudgeTools, "detect_edge", fake_detect_edge)

    assert logic.special_exit_logic() is expected_exit

    assert helper_calls == [(enemy, anomaly_name)]
    assert enemy.dynamic.reads == [anomaly_name]
    assert detect_events == [
        ("detect", (previous_state, current_state), previous_state),
        ("result", expected_exit, previous_state),
    ]
    assert getattr(logic, f"last_{anomaly_name}") is current_state


def test_anomaly_debuff_exit_judge_finds_enemy_once_then_reuses_cached_enemy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    buff_index = "Buff-异常-霜寒"
    anomaly_name = anomaly_module.anomaly_statement_dict[buff_index]
    enemy = _EnemyProbe(_DynamicProbe(frostbite=False))
    logic = _make_logic(index=buff_index, enemy=None)
    logic.last_frostbite = True
    find_calls: list[object] = []

    def fake_find_enemy(*, sim_instance: object) -> _EnemyProbe:
        find_calls.append(sim_instance)
        return enemy

    monkeypatch.setattr(anomaly_module.JudgeTools, "find_enemy", fake_find_enemy)

    assert logic.special_exit_logic() is True
    enemy.dynamic.set_value(anomaly_name, True)
    assert logic.special_exit_logic() is False

    assert find_calls == [logic.buff_instance.sim_instance]
    assert logic.enemy is enemy
    assert enemy.dynamic.reads == [anomaly_name, anomaly_name]
    assert logic.last_frostbite is True


def test_anomaly_debuff_exit_judge_unsupported_index_preserves_key_error_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    enemy = _EnemyProbe(_DynamicProbe(frostbite=False))
    logic = _make_logic(index="Buff-异常-未支持", enemy=None)
    find_calls: list[object] = []

    def fake_find_enemy(*, sim_instance: object) -> _EnemyProbe:
        find_calls.append(sim_instance)
        return enemy

    def fail_if_read(read_enemy: object, read_name: str) -> object:
        raise AssertionError("unsupported indexes must not read anomaly state")

    def fail_if_detected(pair: list[object], mode_func: object) -> bool:
        raise AssertionError("unsupported indexes must not detect edges")

    monkeypatch.setattr(anomaly_module.JudgeTools, "find_enemy", fake_find_enemy)
    monkeypatch.setattr(anomaly_module, "read_enemy_anomaly_state", fail_if_read)
    monkeypatch.setattr(anomaly_module.JudgeTools, "detect_edge", fail_if_detected)

    with pytest.raises(KeyError):
        logic.special_exit_logic()

    assert find_calls == [logic.buff_instance.sim_instance]
    assert logic.enemy is enemy
    assert enemy.dynamic.reads == []
