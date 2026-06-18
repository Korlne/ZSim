from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Callable, Iterable, cast

import pytest

import zsim.sim_progress.Buff.BuffXLogic.AnomalyDebuffExitJudge as anomaly_module
import zsim.sim_progress.Buff.BuffXLogic.HailstormShrineIceBonus as hailstorm_module
import zsim.sim_progress.Buff.BuffXLogic.MiyabiAdditionalAbility_IgnoreIceRes as miyabi_ignore_module
from zsim.sim_progress.Buff.BuffXLogic.enemy_anomaly_map_read import (
    read_enemy_anomaly_state,
    snapshot_enemy_anomaly_states,
)


SUPPORTED_ANOMALY_INDEXES = tuple(
    anomaly_module.anomaly_statement_dict.items()
)
SUPPORTED_ANOMALY_NAMES = tuple(anomaly_module.anomaly_statement_dict.values())
SNAPSHOT_ANOMALY_NAMES = tuple(hailstorm_module.anomaly_name_list)
assert SNAPSHOT_ANOMALY_NAMES == tuple(miyabi_ignore_module.anomaly_name_list)


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
        self.logic: Any | None = None


class _SnapshotDynamicProbe:
    def __init__(self, **values: bool) -> None:
        self._values = {
            name: values.get(name, False) for name in SNAPSHOT_ANOMALY_NAMES
        }
        self.reads: list[str] = []

    def __getattribute__(self, name: str) -> Any:
        if name in SNAPSHOT_ANOMALY_NAMES:
            reads = object.__getattribute__(self, "reads")
            values = object.__getattribute__(self, "_values")
            reads.append(name)
            return values[name]
        return object.__getattribute__(self, name)


class _SnapshotEnemyProbe:
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
            "old_container",
        }
    )

    def __init__(self, dynamic: _SnapshotDynamicProbe) -> None:
        self.dynamic = dynamic

    def __getattribute__(self, name: str) -> Any:
        if name in object.__getattribute__(self, "_FORBIDDEN_SURFACES"):
            raise AssertionError(f"unexpected helper surface read: {name}")
        return object.__getattribute__(self, name)


class _ActionStackProbe:
    def __init__(self, action: object) -> None:
        self.action = action
        self.peek_calls = 0

    def peek(self) -> object:
        self.peek_calls += 1
        return self.action


class _Buff0Probe:
    def __init__(self, record: object | None) -> None:
        self.history = SimpleNamespace(record=record)


class _TracingAnomalyState(dict[str, bool]):
    def __init__(self, values: dict[str, bool], events: list[str]) -> None:
        super().__init__(values)
        self._events = events

    def values(self) -> Any:
        self._events.append("values")
        return super().values()

    def __getitem__(self, name: str) -> bool:
        self._events.append(f"get:{name}")
        return super().__getitem__(name)

    def update(self, *args: Any, **kwargs: bool) -> None:
        self._events.append("update")
        super().update(*args, **kwargs)


class _MiyabiAdditionalRecordProbe:
    def __init__(
        self,
        *,
        previous_anomalies: dict[str, bool],
        effect_count: int,
        events: list[str],
    ) -> None:
        object.__setattr__(self, "events", events)
        object.__setattr__(self, "_recording", False)
        self.anomaly_state = _TracingAnomalyState(previous_anomalies, events)
        self.disorder = False
        self.effect_count = effect_count
        self.action_stack = None
        self.enemy = None
        object.__setattr__(self, "_recording", True)

    def __setattr__(self, name: str, value: object) -> None:
        if (
            object.__getattribute__(self, "_recording")
            and name in {"disorder", "effect_count"}
        ):
            object.__getattribute__(self, "events").append(f"set:{name}:{value}")
        object.__setattr__(self, name, value)


def _anomaly_map(**active: bool) -> dict[str, bool]:
    return {name: active.get(name, False) for name in SNAPSHOT_ANOMALY_NAMES}


def _action(*, trigger_buff_level: int = 1, mission_tag: str = "") -> object:
    return SimpleNamespace(
        mission_node=SimpleNamespace(
            skill=SimpleNamespace(trigger_buff_level=trigger_buff_level)
        ),
        mission_tag=mission_tag,
    )


def _wrap_snapshot_helper(
    *,
    monkeypatch: pytest.MonkeyPatch,
    module: object,
    events: list[str],
    helper_calls: list[tuple[_SnapshotEnemyProbe, tuple[str, ...]]],
) -> None:
    def fake_snapshot_enemy_anomaly_states(
        enemy: object,
        names: Iterable[str],
    ) -> dict[str, Any]:
        names_tuple = tuple(names)
        helper_calls.append((cast(_SnapshotEnemyProbe, enemy), names_tuple))
        events.append("snapshot")
        return snapshot_enemy_anomaly_states(cast(Any, enemy), names_tuple)

    monkeypatch.setattr(
        module,
        "snapshot_enemy_anomaly_states",
        fake_snapshot_enemy_anomaly_states,
    )


def _make_hailstorm_logic(
    monkeypatch: pytest.MonkeyPatch,
    *,
    previous_anomalies: dict[str, bool],
    current_anomalies: dict[str, bool],
    trigger_buff_level: int = 1,
    mission_tag: str = "",
    lazy_record: bool = False,
) -> SimpleNamespace:
    events: list[str] = []
    helper_calls: list[tuple[_SnapshotEnemyProbe, tuple[str, ...]]] = []
    record = None
    if not lazy_record:
        record = hailstorm_module.HailstormShrineIceBonusRecord()
        record.anomaly_state = _TracingAnomalyState(previous_anomalies, events)
    buff_0 = _Buff0Probe(record)
    buff_instance = _BuffInstanceProbe(index="hailstorm-index", sim_instance=object())
    dynamic = _SnapshotDynamicProbe(**current_anomalies)
    enemy = _SnapshotEnemyProbe(dynamic)
    action_stack = _ActionStackProbe(
        _action(trigger_buff_level=trigger_buff_level, mission_tag=mission_tag)
    )
    char = SimpleNamespace(CID=1091)
    find_equipper_calls: list[tuple[str, object]] = []
    find_exist_calls: list[object] = []
    preparation_calls: list[dict[str, object]] = []

    def fake_find_equipper(equipper: str, *, sim_instance: object) -> str:
        find_equipper_calls.append((equipper, sim_instance))
        return "雅"

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        find_exist_calls.append(sim_instance)
        return {"雅": {"hailstorm-index": buff_0}}

    def fake_check_preparation(
        *,
        buff_instance: object,
        buff_0: object,
        **kwargs: object,
    ) -> None:
        preparation_calls.append(dict(kwargs))
        prepared_record = cast(Any, cast(_Buff0Probe, buff_0).history.record)
        if kwargs.get("enemy"):
            prepared_record.enemy = enemy
        if kwargs.get("action_stack"):
            prepared_record.action_stack = action_stack
        if kwargs.get("equipper"):
            prepared_record.char = char

    _wrap_snapshot_helper(
        monkeypatch=monkeypatch,
        module=hailstorm_module,
        events=events,
        helper_calls=helper_calls,
    )
    monkeypatch.setattr(
        hailstorm_module.JudgeTools,
        "find_equipper",
        fake_find_equipper,
    )
    monkeypatch.setattr(
        hailstorm_module.JudgeTools,
        "find_exist_buff_dict",
        fake_find_exist_buff_dict,
    )
    monkeypatch.setattr(hailstorm_module, "check_preparation", fake_check_preparation)

    logic = hailstorm_module.HailstormShrineIceBonus(cast(Any, buff_instance))
    buff_instance.logic = logic
    return SimpleNamespace(
        logic=logic,
        buff_0=buff_0,
        events=events,
        helper_calls=helper_calls,
        dynamic=dynamic,
        enemy=enemy,
        action_stack=action_stack,
        find_equipper_calls=find_equipper_calls,
        find_exist_calls=find_exist_calls,
        preparation_calls=preparation_calls,
    )


def _make_miyabi_ignore_logic(
    monkeypatch: pytest.MonkeyPatch,
    *,
    previous_anomalies: dict[str, bool],
    current_anomalies: dict[str, bool],
    effect_count: int = 0,
    mission_tag: str = "",
) -> SimpleNamespace:
    events: list[str] = []
    helper_calls: list[tuple[_SnapshotEnemyProbe, tuple[str, ...]]] = []
    record = _MiyabiAdditionalRecordProbe(
        previous_anomalies=previous_anomalies,
        effect_count=effect_count,
        events=events,
    )
    buff_0 = _Buff0Probe(record)
    buff_instance = _BuffInstanceProbe(index="miyabi-ignore-index", sim_instance=object())
    dynamic = _SnapshotDynamicProbe(**current_anomalies)
    enemy = _SnapshotEnemyProbe(dynamic)
    action_stack = _ActionStackProbe(_action(mission_tag=mission_tag))
    find_exist_calls: list[object] = []
    preparation_calls: list[dict[str, object]] = []

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        find_exist_calls.append(sim_instance)
        return {"雅": {"miyabi-ignore-index": buff_0}}

    def fake_check_preparation(
        *,
        buff_instance: object,
        buff_0: object,
        **kwargs: object,
    ) -> None:
        preparation_calls.append(dict(kwargs))
        prepared_record = cast(Any, cast(_Buff0Probe, buff_0).history.record)
        if kwargs.get("enemy"):
            prepared_record.enemy = enemy
        if kwargs.get("action_stack"):
            prepared_record.action_stack = action_stack

    _wrap_snapshot_helper(
        monkeypatch=monkeypatch,
        module=miyabi_ignore_module,
        events=events,
        helper_calls=helper_calls,
    )
    monkeypatch.setattr(
        miyabi_ignore_module.JudgeTools,
        "find_exist_buff_dict",
        fake_find_exist_buff_dict,
    )
    monkeypatch.setattr(
        miyabi_ignore_module,
        "check_preparation",
        fake_check_preparation,
    )

    logic = miyabi_ignore_module.MiyabiAdditionalAbility_IgnoreIceRes(
        cast(Any, buff_instance)
    )
    buff_instance.logic = logic
    return SimpleNamespace(
        logic=logic,
        record=record,
        events=events,
        helper_calls=helper_calls,
        dynamic=dynamic,
        enemy=enemy,
        action_stack=action_stack,
        find_exist_calls=find_exist_calls,
        preparation_calls=preparation_calls,
    )


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


def test_hailstorm_delegates_snapshot_no_change_and_updates_after_record_reads(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _make_hailstorm_logic(
        monkeypatch,
        previous_anomalies=_anomaly_map(),
        current_anomalies=_anomaly_map(),
        mission_tag="1091_NA",
    )

    assert harness.logic.special_judge_logic() is False

    assert harness.helper_calls == [(harness.enemy, SNAPSHOT_ANOMALY_NAMES)]
    assert harness.dynamic.reads == list(SNAPSHOT_ANOMALY_NAMES)
    assert harness.action_stack.peek_calls == 1
    assert harness.preparation_calls == [
        {"equipper": "霰落星殿", "enemy": 1, "action_stack": 1}
    ]
    assert harness.events == [
        "snapshot",
        "values",
        "get:frostbite",
        "get:assault",
        "get:shock",
        "get:burn",
        "get:corruption",
        "update",
    ]
    assert dict(harness.buff_0.history.record.anomaly_state) == _anomaly_map()


def test_hailstorm_one_anomaly_transition_returns_true_and_updates_record_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _make_hailstorm_logic(
        monkeypatch,
        previous_anomalies=_anomaly_map(),
        current_anomalies=_anomaly_map(frostbite=True),
        mission_tag="1091_NA",
    )

    assert harness.logic.special_judge_logic() is True

    assert harness.helper_calls == [(harness.enemy, SNAPSHOT_ANOMALY_NAMES)]
    assert harness.events == [
        "snapshot",
        "values",
        "get:frostbite",
        "update",
    ]
    assert dict(harness.buff_0.history.record.anomaly_state) == _anomaly_map(
        frostbite=True
    )


def test_hailstorm_two_anomaly_snapshot_raises_before_record_update(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _make_hailstorm_logic(
        monkeypatch,
        previous_anomalies=_anomaly_map(),
        current_anomalies=_anomaly_map(frostbite=True, burn=True),
        mission_tag="1091_NA",
    )

    with pytest.raises(ValueError, match="当前ticks总异常数量为2"):
        harness.logic.special_judge_logic()

    assert harness.helper_calls == [(harness.enemy, SNAPSHOT_ANOMALY_NAMES)]
    assert harness.events == ["snapshot"]
    assert dict(harness.buff_0.history.record.anomaly_state) == _anomaly_map()


def test_hailstorm_trigger_buff_level_gate_uses_action_stack_and_lazy_record(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _make_hailstorm_logic(
        monkeypatch,
        previous_anomalies=_anomaly_map(),
        current_anomalies=_anomaly_map(),
        trigger_buff_level=2,
        mission_tag="tag_1091_EX",
        lazy_record=True,
    )

    assert harness.logic.special_judge_logic() is True

    assert isinstance(
        harness.buff_0.history.record,
        hailstorm_module.HailstormShrineIceBonusRecord,
    )
    assert harness.find_equipper_calls == [
        ("霰落星殿", harness.logic.buff_instance.sim_instance)
    ]
    assert harness.find_exist_calls == [harness.logic.buff_instance.sim_instance]
    assert harness.helper_calls == [(harness.enemy, SNAPSHOT_ANOMALY_NAMES)]
    assert harness.action_stack.peek_calls == 1
    assert dict(harness.buff_0.history.record.anomaly_state) == _anomaly_map()


def test_miyabi_ignore_ice_res_delegates_snapshot_no_disorder_and_updates_record(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _make_miyabi_ignore_logic(
        monkeypatch,
        previous_anomalies=_anomaly_map(),
        current_anomalies=_anomaly_map(frostbite=True),
        mission_tag="1091_NA",
    )

    assert harness.logic.special_judge_logic() is False

    assert harness.helper_calls == [(harness.enemy, SNAPSHOT_ANOMALY_NAMES)]
    assert harness.dynamic.reads == list(SNAPSHOT_ANOMALY_NAMES)
    assert harness.action_stack.peek_calls == 1
    assert harness.preparation_calls == [{"enemy": 1, "action_stack": 1}]
    assert harness.events == [
        "snapshot",
        "values",
        "set:disorder:False",
        "update",
    ]
    assert harness.record.disorder is False
    assert harness.record.effect_count == 0
    assert dict(harness.record.anomaly_state) == _anomaly_map(frostbite=True)


@pytest.mark.parametrize(
    ("starting_effect_count", "expected_effect_count"),
    [
        pytest.param(0, 1, id="increment"),
        pytest.param(1, 1, id="clamp"),
    ],
)
def test_miyabi_ignore_ice_res_disorder_transition_increments_and_clamps_effect_count(
    monkeypatch: pytest.MonkeyPatch,
    *,
    starting_effect_count: int,
    expected_effect_count: int,
) -> None:
    harness = _make_miyabi_ignore_logic(
        monkeypatch,
        previous_anomalies=_anomaly_map(frostbite=True),
        current_anomalies=_anomaly_map(burn=True),
        effect_count=starting_effect_count,
        mission_tag="1091_NA",
    )

    assert harness.logic.special_judge_logic() is False

    assert harness.helper_calls == [(harness.enemy, SNAPSHOT_ANOMALY_NAMES)]
    assert harness.events == [
        "snapshot",
        "values",
        "get:frostbite",
        "set:disorder:True",
        "update",
        f"set:effect_count:{expected_effect_count}",
    ]
    assert harness.record.disorder is True
    assert harness.record.effect_count == expected_effect_count
    assert dict(harness.record.anomaly_state) == _anomaly_map(burn=True)


def test_miyabi_ignore_ice_res_two_anomaly_snapshot_raises_before_record_update(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _make_miyabi_ignore_logic(
        monkeypatch,
        previous_anomalies=_anomaly_map(frostbite=True),
        current_anomalies=_anomaly_map(frostbite=True, burn=True),
        effect_count=0,
        mission_tag="1091_NA",
    )

    with pytest.raises(ValueError, match="当前ticks总异常数量为2"):
        harness.logic.special_judge_logic()

    assert harness.helper_calls == [(harness.enemy, SNAPSHOT_ANOMALY_NAMES)]
    assert harness.events == ["snapshot", "values"]
    assert harness.record.disorder is False
    assert harness.record.effect_count == 0
    assert dict(harness.record.anomaly_state) == _anomaly_map(frostbite=True)


def test_miyabi_ignore_ice_res_action_tag_consumes_effect_after_update(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _make_miyabi_ignore_logic(
        monkeypatch,
        previous_anomalies=_anomaly_map(frostbite=True),
        current_anomalies=_anomaly_map(burn=True),
        effect_count=0,
        mission_tag="1091_SNA_2",
    )

    assert harness.logic.special_judge_logic() is True

    assert harness.helper_calls == [(harness.enemy, SNAPSHOT_ANOMALY_NAMES)]
    assert harness.events == [
        "snapshot",
        "values",
        "get:frostbite",
        "set:disorder:True",
        "update",
        "set:effect_count:1",
        "set:effect_count:0",
    ]
    assert harness.record.disorder is True
    assert harness.record.effect_count == 0
    assert dict(harness.record.anomaly_state) == _anomaly_map(burn=True)
