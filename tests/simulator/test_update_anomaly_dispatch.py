from __future__ import annotations

import inspect
from types import SimpleNamespace

import numpy as np
import pytest

import zsim.sim_progress.anomaly_bar.CopyAnomalyForOutput as copied_output_module
from zsim.models.event_enums import ListenerBroadcastSignal as LBS
from zsim.sim_progress.Dot.BaseDot import Dot
from zsim.sim_progress.Dot.runtime_state import DotRuntimeStateAdapter
from zsim.sim_progress.Update import UpdateAnomaly as update_anomaly_module
from zsim.sim_progress.Update.UpdateAnomaly import (
    anomaly_effect_active,
    remove_dots_cause_disorder,
    spawn_output,
    update_anomaly,
)
from zsim.sim_progress.anomaly_bar import AnomalyBar
from zsim.sim_progress.anomaly_bar.CopyAnomalyForOutput import (
    Disorder,
    NewAnomaly,
    PolarityDisorder,
)
from zsim.sim_progress.data_struct.schedule_dispatch import create_schedule_dispatch_port


class _FailFastEventList(list):
    def append(self, item):
        raise AssertionError("UpdateAnomaly should publish scheduled events via dispatch port")


class _RecordingEventList(list):
    def __init__(self, call_order: list[tuple[str, object]] | None = None) -> None:
        super().__init__()
        self._call_order = call_order

    def append(self, item):
        if self._call_order is not None:
            self._call_order.append(("publish", item))
        super().append(item)


class _RecordingDotRuntimeList(list):
    def __init__(
        self,
        call_order: list[tuple[str, object]],
        items: list[object] | None = None,
    ) -> None:
        super().__init__(items or [])
        self._call_order = call_order

    def append(self, item):
        self._call_order.append(("dot_append", item.ft.index))
        super().append(item)

    def remove(self, item):
        self._call_order.append(("dot_remove", item.ft.index))
        super().remove(item)


class _FailFastDotRuntimeList(list):
    def append(self, item):
        raise AssertionError("debuff-only anomaly effects should not register runtime dots")

    def remove(self, item):
        raise AssertionError("debuff-only anomaly effects should not remove runtime dots")


class _FailFastPendingBuffQueue(list):
    def append(self, item):
        raise AssertionError("anomaly effects should not write pending Buff queues")

    def extend(self, items):
        raise AssertionError("anomaly effects should not write pending Buff queues")

    def insert(self, index, item):
        raise AssertionError("anomaly effects should not write pending Buff queues")

    def clear(self):
        raise AssertionError("anomaly effects should not write pending Buff queues")


class _RecordingDotRuntimeStateAdapter(DotRuntimeStateAdapter):
    def __init__(
        self,
        dynamic_state,
        helper_calls: list[tuple[str, object]],
    ) -> None:
        super().__init__(dynamic_state)
        self._helper_calls = helper_calls

    def replace_by_index(self, dot: Dot, timenow: int) -> tuple[Dot, ...]:
        self._helper_calls.append(("replace_by_index", dot, timenow))
        return super().replace_by_index(dot, timenow)

    def remove_all(self, dots) -> tuple[Dot, ...]:
        dots_tuple = tuple(dots)
        self._helper_calls.append(("remove_all", dots_tuple))
        return super().remove_all(dots_tuple)


def _record_dot_runtime_state_adapter(monkeypatch, helper_calls):
    def recording_from_enemy(cls, enemy):
        helper_calls.append(("from_enemy", enemy))
        return _RecordingDotRuntimeStateAdapter(enemy.dynamic, helper_calls)

    monkeypatch.setattr(
        update_anomaly_module.DotRuntimeStateAdapter,
        "from_enemy",
        classmethod(recording_from_enemy),
    )


class _RecordingDotDynamicState:
    def __init__(
        self,
        call_order: list[tuple[str, object]],
        *,
        effect_times: int = 0,
        ready: bool | None = True,
    ) -> None:
        object.__setattr__(self, "_call_order", call_order)
        object.__setattr__(self, "_recording_enabled", False)
        self.active = True
        self.count = 0
        self.start_ticks = 0
        self.last_effect_ticks = 0
        self.ready = ready
        self.effect_times = effect_times
        object.__setattr__(self, "_recording_enabled", True)

    def __setattr__(self, name: str, value: object) -> None:
        if getattr(self, "_recording_enabled", False) and name in {
            "ready",
            "last_effect_ticks",
            "effect_times",
        }:
            self._call_order.append((f"dy_{name}", value))
        object.__setattr__(self, name, value)


class _ForbiddenListenerManager:
    def broadcast_event(self, **kwargs):
        raise AssertionError("dot replacement should not use listener broadcast")


class _ForbiddenRuntimeCommandPort:
    def update_anomaly(self, **kwargs):
        raise AssertionError("scheduled-publish parity tests should not issue runtime commands")


class _FakeDot(Dot):
    def __init__(
        self,
        *,
        index: str,
        anomaly_data=None,
        call_order: list[tuple[str, object]] | None = None,
    ):
        super().__init__(bar=None, sim_instance=None)
        self.ft.index = index
        self.ft.max_effect_times = 30
        self.anomaly_data = anomaly_data
        self.ended_at: int | None = None
        self._call_order = call_order

    def end(self, timenow: int):
        if self._call_order is not None:
            self._call_order.append(("dot_end", self.ft.index))
        self.ended_at = timenow
        super().end(timenow)


def _build_sim_instance(
    event_list,
    call_order: list[tuple[str, object]] | None = None,
):
    def broadcast_event(**kwargs):
        if call_order is not None:
            call_order.append(("broadcast", kwargs["signal"]))

    return SimpleNamespace(
        tick=10,
        schedule_data=SimpleNamespace(
            event_list=event_list,
            change_process_state=lambda: None,
        ),
        listener_manager=SimpleNamespace(broadcast_event=broadcast_event),
        decibel_manager=SimpleNamespace(update=lambda **kwargs: None),
        runtime_command_port=_ForbiddenRuntimeCommandPort(),
    )


def _build_enemy(sim_instance):
    state_attr_map = {index: f"anomaly_state_{index}" for index in range(7)}
    dynamic = SimpleNamespace(
        active_anomaly_bar_dict={index: None for index in range(7)},
        frozen=False,
        frostbite=False,
        dynamic_dot_list=[],
    )
    for attr_name in state_attr_map.values():
        setattr(dynamic, attr_name, False)
    return SimpleNamespace(
        sim_instance=sim_instance,
        dynamic=dynamic,
        anomaly_bars_dict={},
        trans_element_number_to_str={
            0: "physical",
            1: "fire",
            2: "ice",
            3: "electric",
            4: "ether",
            5: "frost",
            6: "auricink",
        },
        trans_anomaly_effect_to_str=state_attr_map,
        max_anomaly_physical=100,
        max_anomaly_fire=100,
        max_anomaly_ice=100,
        max_anomaly_electric=100,
        max_anomaly_ether=100,
        max_anomaly_frost=100,
        max_anomaly_auricink=100,
        update_max_anomaly=lambda element_type: None,
    )


def _build_anomaly_bar(sim_instance, *, element_type: int) -> AnomalyBar:
    bar = AnomalyBar(sim_instance=sim_instance, element_type=element_type)
    bar.max_anomaly = 100
    bar.current_anomaly = 100
    bar.ready = True
    bar.basic_max_duration = 60
    bar.ndarray_box = [(element_type, np.float64(100), np.ones((1, 1), dtype=np.float64))]
    return bar


def _build_spawn_output_source_bar(
    sim_instance,
    *,
    element_type: int,
    settled: bool,
) -> AnomalyBar:
    bar = _build_anomaly_bar(sim_instance, element_type=element_type)
    snapshot = np.array([[1.25, 2.5, 3.75]], dtype=np.float64)
    bar.current_anomaly = np.float64(100)
    bar.current_effective_anomaly = np.float64(100 if settled else 0)
    bar.current_ndarray = snapshot.copy()
    bar.ndarray_box = [] if settled else [(element_type, np.float64(100), snapshot)]
    bar.settled = settled
    bar.active = True
    bar.anomaly_dmg_ratio = 2.25
    bar.scaling_factor = 1.5
    bar.max_duration = 420
    bar.last_active = 120
    bar.accompany_dot = "Shock"
    bar.rename_tag = f"spawn-output-mode-{element_type}"
    return bar


def _build_skill_node(*, element_type: int, char_name: str = "alpha", skill_tag: str = "1001_TEST"):
    return SimpleNamespace(
        element_type=element_type,
        char_name=char_name,
        skill_tag=skill_tag,
        skill=SimpleNamespace(char_obj=SimpleNamespace(CID=1001)),
    )


def test_spawn_output_mode_zero_settles_without_listener_or_scheduled_publish():
    call_order: list[tuple[str, object]] = []
    broadcast_events: list[tuple[object, object]] = []
    recording_queue = _RecordingEventList(call_order)
    sim_instance = _build_sim_instance(recording_queue)
    sim_instance.load_data = SimpleNamespace(
        LOADING_BUFF_DICT={"enemy": _FailFastPendingBuffQueue()}
    )

    def record_broadcast(*, event: object, signal: object) -> None:
        call_order.append(("broadcast", signal))
        broadcast_events.append((event, signal))

    sim_instance.listener_manager = SimpleNamespace(broadcast_event=record_broadcast)
    source_bar = _build_spawn_output_source_bar(
        sim_instance,
        element_type=4,
        settled=False,
    )
    skill_node = _build_skill_node(element_type=4)

    output = spawn_output(
        source_bar,
        0,
        sim_instance=sim_instance,
        skill_node=skill_node,
    )

    assert type(output) is NewAnomaly
    assert output is not source_bar
    assert output.sim_instance is sim_instance
    assert output.activated_by is skill_node
    assert output.activate_by is skill_node
    assert output.is_disorder is False
    assert output.element_type == 4
    assert output.accompany_dot == "Shock"
    assert output.rename_tag == "spawn-output-mode-4"
    assert output.anomaly_dmg_ratio == pytest.approx(2.25)
    assert output.scaling_factor == pytest.approx(1.5)
    assert output.max_duration == 420
    assert output.last_active == 120
    assert output.current_effective_anomaly == pytest.approx(100)
    assert source_bar.settled is True
    assert output.current_ndarray is not source_bar.current_ndarray
    np.testing.assert_allclose(
        output.current_ndarray,
        np.array([[1.25, 2.5, 3.75]], dtype=np.float64),
    )
    assert output.schedule_priority == 999
    assert not hasattr(output, "execute_tick")
    assert recording_queue == []
    assert broadcast_events == []
    assert call_order == []


@pytest.mark.parametrize(
    ("mode_number", "expected_type", "kwargs", "expected_polarity_ratio"),
    [
        pytest.param(1, Disorder, {}, None, id="disorder"),
        pytest.param(
            2,
            PolarityDisorder,
            {"polarity_ratio": 1.6},
            1.6,
            id="polarity-disorder",
        ),
    ],
)
def test_spawn_output_disorder_modes_broadcast_listener_payload_without_publish(
    mode_number,
    expected_type,
    kwargs,
    expected_polarity_ratio,
):
    call_order: list[tuple[str, object]] = []
    broadcast_events: list[tuple[object, object]] = []
    recording_queue = _RecordingEventList(call_order)
    sim_instance = _build_sim_instance(recording_queue)
    sim_instance.load_data = SimpleNamespace(
        LOADING_BUFF_DICT={"enemy": _FailFastPendingBuffQueue()}
    )

    def record_broadcast(*, event: object, signal: object) -> None:
        call_order.append(("broadcast", signal))
        broadcast_events.append((event, signal))

    sim_instance.listener_manager = SimpleNamespace(broadcast_event=record_broadcast)
    source_bar = _build_spawn_output_source_bar(
        sim_instance,
        element_type=3,
        settled=True,
    )
    skill_node = _build_skill_node(element_type=3)

    output = spawn_output(
        source_bar,
        mode_number,
        sim_instance=sim_instance,
        skill_node=skill_node,
        **kwargs,
    )

    assert type(output) is expected_type
    assert output is not source_bar
    assert output.sim_instance is sim_instance
    assert output.activated_by is skill_node
    assert output.activate_by is skill_node
    assert output.is_disorder is True
    assert output.settled is True
    assert output.element_type == 3
    assert output.accompany_dot == "Shock"
    assert output.rename_tag == "spawn-output-mode-3"
    assert output.anomaly_dmg_ratio == pytest.approx(2.25)
    assert output.scaling_factor == pytest.approx(1.5)
    assert output.max_duration == 420
    assert output.last_active == 120
    assert output.current_effective_anomaly == pytest.approx(100)
    assert output.current_ndarray is not source_bar.current_ndarray
    np.testing.assert_allclose(
        output.current_ndarray,
        np.array([[1.25, 2.5, 3.75]], dtype=np.float64),
    )
    if expected_polarity_ratio is None:
        assert not hasattr(output, "polarity_disorder_ratio")
        assert not hasattr(output, "additional_dmg_ap_ratio")
    else:
        assert output.polarity_disorder_ratio == pytest.approx(expected_polarity_ratio)
        assert output.additional_dmg_ap_ratio == 32
    assert output.schedule_priority == 999
    assert not hasattr(output, "execute_tick")
    assert recording_queue == []
    assert broadcast_events == [(output, LBS.DISORDER_SPAWN)]
    assert call_order == [("broadcast", LBS.DISORDER_SPAWN)]


def test_spawn_output_mode_two_requires_polarity_ratio_without_side_effects():
    call_order: list[tuple[str, object]] = []
    broadcast_events: list[tuple[object, object]] = []
    recording_queue = _RecordingEventList(call_order)
    sim_instance = _build_sim_instance(recording_queue)
    sim_instance.load_data = SimpleNamespace(
        LOADING_BUFF_DICT={"enemy": _FailFastPendingBuffQueue()}
    )

    def record_broadcast(*, event: object, signal: object) -> None:
        call_order.append(("broadcast", signal))
        broadcast_events.append((event, signal))

    sim_instance.listener_manager = SimpleNamespace(broadcast_event=record_broadcast)
    source_bar = _build_spawn_output_source_bar(
        sim_instance,
        element_type=3,
        settled=False,
    )
    source_snapshot = source_bar.current_ndarray.copy()

    with pytest.raises(ValueError, match="polarity_ratio"):
        spawn_output(
            source_bar,
            2,
            sim_instance=sim_instance,
            skill_node=_build_skill_node(element_type=3),
        )

    assert source_bar.settled is False
    assert source_bar.current_effective_anomaly == np.float64(0)
    np.testing.assert_allclose(source_bar.current_ndarray, source_snapshot)
    assert recording_queue == []
    assert broadcast_events == []
    assert call_order == []


def test_spawn_output_invalid_mode_rejects_without_side_effects(monkeypatch):
    call_order: list[tuple[str, object]] = []
    broadcast_events: list[tuple[object, object]] = []
    recording_queue = _RecordingEventList(call_order)
    sim_instance = _build_sim_instance(recording_queue)
    sim_instance.load_data = SimpleNamespace(
        LOADING_BUFF_DICT={"enemy": _FailFastPendingBuffQueue()}
    )

    def record_broadcast(*, event: object, signal: object) -> None:
        call_order.append(("broadcast", signal))
        broadcast_events.append((event, signal))

    def fail_constructor(*args, **kwargs):
        raise AssertionError("invalid spawn_output mode must not construct copied output")

    monkeypatch.setattr(update_anomaly_module, "NewAnomaly", fail_constructor)
    monkeypatch.setattr(update_anomaly_module, "Disorder", fail_constructor)
    monkeypatch.setattr(update_anomaly_module, "PolarityDisorder", fail_constructor)

    sim_instance.listener_manager = SimpleNamespace(broadcast_event=record_broadcast)
    source_bar = _build_spawn_output_source_bar(
        sim_instance,
        element_type=3,
        settled=False,
    )
    source_snapshot = source_bar.current_ndarray.copy()

    with pytest.raises(ValueError, match="spawn_output"):
        spawn_output(
            source_bar,
            99,
            sim_instance=sim_instance,
            skill_node=_build_skill_node(element_type=3),
        )

    assert source_bar.settled is False
    assert source_bar.current_effective_anomaly == np.float64(0)
    np.testing.assert_allclose(source_bar.current_ndarray, source_snapshot)
    assert recording_queue == []
    assert broadcast_events == []
    assert call_order == []


def test_update_anomaly_publishes_new_anomaly_via_dispatch_port_without_raw_queue_append():
    call_order: list[tuple[str, object]] = []
    legacy_event_list = _FailFastEventList()
    sim_instance = _build_sim_instance(legacy_event_list, call_order)
    enemy = _build_enemy(sim_instance)
    enemy.anomaly_bars_dict[1] = _build_anomaly_bar(sim_instance, element_type=1)
    skill_node = _build_skill_node(element_type=1)
    chars = [SimpleNamespace(special_resources=lambda *args, **kwargs: None)]

    recording_queue = _RecordingEventList(call_order)
    sim_instance.schedule_data.event_list = recording_queue

    update_anomaly(
        1,
        enemy,
        10,
        legacy_event_list,
        chars,
        sim_instance,
        skill_node,
        {"alpha": [], "enemy": []},
    )

    assert len(recording_queue) == 1
    published = recording_queue[0]
    assert call_order == [("broadcast", LBS.ANOMALY), ("publish", published)]
    assert published.element_type == 1
    assert published.activated_by is skill_node
    assert published.is_disorder is False
    assert published.schedule_priority == 999
    assert not hasattr(published, "execute_tick")


def test_update_anomaly_uses_current_schedule_queue_after_event_list_rebind():
    legacy_event_list = _FailFastEventList()
    first_queue = _RecordingEventList()
    sim_instance = _build_sim_instance(first_queue)
    skill_node = _build_skill_node(element_type=1)
    chars = [SimpleNamespace(special_resources=lambda *args, **kwargs: None)]

    first_enemy = _build_enemy(sim_instance)
    first_enemy.anomaly_bars_dict[1] = _build_anomaly_bar(sim_instance, element_type=1)
    update_anomaly(
        1,
        first_enemy,
        10,
        legacy_event_list,
        chars,
        sim_instance,
        skill_node,
        {"alpha": [], "enemy": []},
    )

    second_queue = _RecordingEventList()
    sim_instance.schedule_data.event_list = second_queue
    second_enemy = _build_enemy(sim_instance)
    second_enemy.anomaly_bars_dict[1] = _build_anomaly_bar(sim_instance, element_type=1)
    update_anomaly(
        1,
        second_enemy,
        20,
        legacy_event_list,
        chars,
        sim_instance,
        skill_node,
        {"alpha": [], "enemy": []},
    )

    assert len(first_queue) == 1
    assert len(second_queue) == 1
    assert first_queue[0] is not second_queue[0]
    assert second_queue[0].sim_instance is sim_instance


def test_update_anomaly_preserves_new_anomaly_then_disorder_order_via_dispatch_port():
    call_order: list[tuple[str, object]] = []
    legacy_event_list = _FailFastEventList()
    sim_instance = _build_sim_instance(legacy_event_list, call_order)
    enemy = _build_enemy(sim_instance)
    current_bar = _build_anomaly_bar(sim_instance, element_type=1)
    previous_bar = _build_anomaly_bar(sim_instance, element_type=3)
    previous_bar.active = True
    enemy.anomaly_bars_dict[1] = current_bar
    enemy.anomaly_bars_dict[3] = previous_bar
    enemy.dynamic.active_anomaly_bar_dict[3] = previous_bar
    setattr(enemy.dynamic, enemy.trans_anomaly_effect_to_str[3], True)
    skill_node = _build_skill_node(element_type=1)
    chars = [
        SimpleNamespace(
            special_resources=lambda anomaly: call_order.append(
                ("special_resources", anomaly)
            )
        )
    ]

    recording_queue = _RecordingEventList(call_order)
    sim_instance.schedule_data.event_list = recording_queue

    update_anomaly(
        1,
        enemy,
        10,
        legacy_event_list,
        chars,
        sim_instance,
        skill_node,
        {"alpha": [], "enemy": []},
    )

    assert len(recording_queue) == 2
    new_anomaly = recording_queue[0]
    disorder = recording_queue[1]
    assert call_order == [
        ("broadcast", LBS.ANOMALY),
        ("broadcast", LBS.DISORDER_SPAWN),
        ("publish", new_anomaly),
        ("special_resources", disorder),
        ("publish", disorder),
    ]
    assert new_anomaly.element_type == 1
    assert new_anomaly.activated_by is skill_node
    assert new_anomaly.is_disorder is False
    assert new_anomaly.schedule_priority == 999
    assert disorder.element_type == 3
    assert disorder.activated_by is skill_node
    assert disorder.is_disorder is True
    assert disorder.schedule_priority == 999


def test_update_anomaly_records_new_anomaly_field_matrix_with_runtime_dot(
    monkeypatch,
):
    call_order: list[tuple[str, object]] = []
    helper_calls: list[tuple[str, object]] = []
    legacy_event_list = _FailFastEventList()
    sim_instance = _build_sim_instance(legacy_event_list, call_order)
    enemy = _build_enemy(sim_instance)
    source_bar = _build_anomaly_bar(sim_instance, element_type=3)
    source_bar.accompany_dot = "Shock"
    source_bar.ndarray_box = [
        (3, np.float64(40), np.array([[2.0, 4.0]], dtype=np.float64)),
        (3, np.float64(60), np.array([[6.0, 8.0]], dtype=np.float64)),
    ]
    enemy.anomaly_bars_dict[3] = source_bar
    enemy.dynamic.dynamic_dot_list = _RecordingDotRuntimeList(call_order)
    skill_node = _build_skill_node(element_type=3)
    chars = [
        SimpleNamespace(
            special_resources=lambda anomaly: call_order.append(
                ("special_resources", anomaly)
            )
        )
    ]
    new_dot = _FakeDot(index="Shock", call_order=call_order)
    spawn_calls: list[tuple[object, int, object, object]] = []

    def fake_spawn_anomaly_dot(element_type, timenow, *, bar, sim_instance):
        spawn_calls.append((element_type, timenow, bar, sim_instance))
        return new_dot

    monkeypatch.setattr(
        update_anomaly_module,
        "spawn_anomaly_dot",
        fake_spawn_anomaly_dot,
    )
    _record_dot_runtime_state_adapter(monkeypatch, helper_calls)
    recording_queue = _RecordingEventList(call_order)
    sim_instance.schedule_data.event_list = recording_queue

    update_anomaly(
        3,
        enemy,
        14,
        legacy_event_list,
        chars,
        sim_instance,
        skill_node,
        {"alpha": [], "enemy": []},
    )

    assert len(recording_queue) == 1
    published = recording_queue[0]
    active_bar = enemy.dynamic.active_anomaly_bar_dict[3]
    assert active_bar is not source_bar
    assert enemy.dynamic.anomaly_state_3 is True
    assert active_bar.active is True
    assert active_bar.settled is True
    assert source_bar.current_anomaly == np.float64(0)
    assert source_bar.current_effective_anomaly == np.float64(0)
    assert source_bar.ndarray_box == []
    np.testing.assert_array_equal(
        source_bar.current_ndarray,
        np.zeros((1, 1), dtype=np.float64),
    )

    assert published.element_type == 3
    assert published.activated_by is skill_node
    assert published.is_disorder is False
    assert published.current_effective_anomaly == np.float64(100)
    np.testing.assert_allclose(
        published.current_ndarray,
        np.array([[4.4, 6.4]], dtype=np.float64),
    )
    assert published.schedule_priority == 999
    assert not hasattr(published, "execute_tick")
    assert spawn_calls == [(3, 14, published, sim_instance)]
    assert helper_calls == [
        ("from_enemy", enemy),
        ("replace_by_index", new_dot, 14),
    ]
    assert enemy.dynamic.dynamic_dot_list == [new_dot]
    assert call_order == [
        ("broadcast", LBS.ANOMALY),
        ("special_resources", published),
        ("dot_append", "Shock"),
        ("publish", published),
    ]


def test_anomaly_effect_active_replaces_same_index_dot_without_scheduled_publish(
    monkeypatch,
):
    call_order: list[tuple[str, object]] = []
    helper_calls: list[tuple[str, object]] = []
    sim_instance = _build_sim_instance(_FailFastEventList())
    pending_queue = _FailFastPendingBuffQueue()
    sim_instance.load_data = SimpleNamespace(LOADING_BUFF_DICT={"enemy": pending_queue})
    sim_instance.listener_manager = _ForbiddenListenerManager()
    enemy = _build_enemy(sim_instance)
    old_dot = _FakeDot(index="Shock", call_order=call_order)
    unrelated_dot = _FakeDot(index="Ignite", call_order=call_order)
    new_dot = _FakeDot(index="Shock", call_order=call_order)
    enemy.dynamic.dynamic_dot_list = _RecordingDotRuntimeList(
        call_order,
        [unrelated_dot, old_dot],
    )
    new_anomaly = SimpleNamespace(marker="new-shock-anomaly")
    spawn_calls: list[tuple[object, int, object, object]] = []

    def fake_spawn_anomaly_dot(element_type, timenow, *, bar, sim_instance):
        spawn_calls.append((element_type, timenow, bar, sim_instance))
        return new_dot

    monkeypatch.setattr(
        update_anomaly_module,
        "spawn_anomaly_dot",
        fake_spawn_anomaly_dot,
    )
    monkeypatch.setattr(
        update_anomaly_module,
        "buff_add_strategy",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("dot-only anomaly effects should not call buff_add_strategy")
        ),
    )
    _record_dot_runtime_state_adapter(monkeypatch, helper_calls)

    anomaly_effect_active(
        SimpleNamespace(accompany_debuff=None, accompany_dot="Shock"),
        77,
        enemy,
        new_anomaly,
        3,
        sim_instance,
    )

    assert spawn_calls == [(3, 77, new_anomaly, sim_instance)]
    assert helper_calls == [
        ("from_enemy", enemy),
        ("replace_by_index", new_dot, 77),
    ]
    assert old_dot.ended_at == 77
    assert enemy.dynamic.dynamic_dot_list == [unrelated_dot, new_dot]
    assert enemy.dynamic.dynamic_dot_list.count(new_dot) == 1
    assert pending_queue == []
    assert call_order == [
        ("dot_end", "Shock"),
        ("dot_remove", "Shock"),
        ("dot_append", "Shock"),
    ]


def test_anomaly_effect_active_spawn_false_leaves_runtime_dot_list_unchanged(
    monkeypatch,
):
    call_order: list[tuple[str, object]] = []
    sim_instance = _build_sim_instance(_FailFastEventList())
    pending_queue = _FailFastPendingBuffQueue()
    sim_instance.load_data = SimpleNamespace(LOADING_BUFF_DICT={"enemy": pending_queue})
    sim_instance.listener_manager = _ForbiddenListenerManager()
    enemy = _build_enemy(sim_instance)
    existing_dot = _FakeDot(index="Shock", call_order=call_order)
    enemy.dynamic.dynamic_dot_list = _RecordingDotRuntimeList(
        call_order,
        [existing_dot],
    )

    monkeypatch.setattr(
        update_anomaly_module,
        "spawn_anomaly_dot",
        lambda *args, **kwargs: False,
    )
    monkeypatch.setattr(
        update_anomaly_module,
        "buff_add_strategy",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("dot-only anomaly effects should not call buff_add_strategy")
        ),
    )
    monkeypatch.setattr(
        update_anomaly_module.DotRuntimeStateAdapter,
        "from_enemy",
        classmethod(
            lambda *args, **kwargs: (_ for _ in ()).throw(
                AssertionError("spawn-false anomaly effects should not create dot helper")
            )
        ),
    )

    anomaly_effect_active(
        SimpleNamespace(accompany_debuff=None, accompany_dot="Shock"),
        88,
        enemy,
        SimpleNamespace(marker="new-shock-anomaly"),
        3,
        sim_instance,
    )

    assert existing_dot.ended_at is None
    assert enemy.dynamic.dynamic_dot_list == [existing_dot]
    assert pending_queue == []
    assert call_order == []


def test_anomaly_effect_active_debuff_branch_uses_existing_buff_add_path(
    monkeypatch,
):
    sim_instance = _build_sim_instance(_FailFastEventList())
    sim_instance.listener_manager = _ForbiddenListenerManager()
    enemy = _build_enemy(sim_instance)
    enemy.dynamic.dynamic_dot_list = _FailFastDotRuntimeList()
    buff_calls: list[tuple[str, object]] = []

    def fake_buff_add_strategy(buff_index, **kwargs):
        buff_calls.append((buff_index, kwargs["sim_instance"]))

    monkeypatch.setattr(
        update_anomaly_module,
        "buff_add_strategy",
        fake_buff_add_strategy,
    )
    monkeypatch.setattr(
        update_anomaly_module,
        "spawn_anomaly_dot",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("debuff-only anomaly effects should not spawn runtime dots")
        ),
    )
    monkeypatch.setattr(
        update_anomaly_module.DotRuntimeStateAdapter,
        "from_enemy",
        classmethod(
            lambda *args, **kwargs: (_ for _ in ()).throw(
                AssertionError("debuff-only anomaly effects should not create dot helper")
            )
        ),
    )

    anomaly_effect_active(
        SimpleNamespace(
            accompany_debuff=["Buff-异常-畏缩", "Buff-异常-霜寒"],
            accompany_dot=None,
        ),
        90,
        enemy,
        SimpleNamespace(marker="new-anomaly"),
        1,
        sim_instance,
    )

    assert buff_calls == [
        ("Buff-异常-畏缩", sim_instance),
        ("Buff-异常-霜寒", sim_instance),
    ]
    assert enemy.dynamic.dynamic_dot_list == []


def test_anomaly_effect_active_does_not_introduce_runtime_write_ports():
    from zsim.sim_progress.ScheduledEvent.buff_runtime import BuffRuntimeReadPort

    source = inspect.getsource(update_anomaly_module.anomaly_effect_active)
    assert "RuntimeCommandPort" not in source
    assert "create_runtime_command_port" not in source
    assert "BuffRuntimeReadPort" not in source
    assert "DotRuntimeStateAdapter.from_enemy" in source

    write_method_names = {
        "append_pending_buff",
        "clear_pending_buffs",
        "remove_active_buff",
        "append_active_buff",
        "sync_enemy_debuff_mirror",
    }
    assert write_method_names.isdisjoint(BuffRuntimeReadPort.__dict__)


def test_copied_output_constructors_keep_publish_dot_and_debuff_layers_external():
    source = inspect.getsource(copied_output_module)
    forbidden_terms = {
        "ScheduleDispatchPort",
        "create_schedule_dispatch_port",
        "publish_scheduled",
        "_publish_scheduled_event",
        "DotRuntimeStateAdapter",
        "spawn_anomaly_dot",
        "buff_add_strategy",
        "RuntimeCommandPort",
        "create_runtime_command_port",
        "settle_buffs",
        "report_dmg_result",
    }

    for term in forbidden_terms:
        assert term not in source
    assert "_copy_source_payload" in source
    assert "_install_copied_payload" in source
    assert "_apply_explicit_overrides" in source


@pytest.mark.parametrize("dot_index", ["Freez", "Freezdot"])
def test_remove_dots_cause_disorder_publishes_freeze_follow_up_via_dispatch_port(
    dot_index,
    monkeypatch,
):
    call_order: list[tuple[str, object]] = []
    helper_calls: list[tuple[str, object]] = []
    recording_queue = _RecordingEventList(call_order)
    sim_instance = _build_sim_instance(recording_queue)
    enemy = _build_enemy(sim_instance)
    anomaly_event = SimpleNamespace(marker="freeze-follow-up")
    freeze_dot = _FakeDot(
        index=dot_index,
        anomaly_data=anomaly_event,
        call_order=call_order,
    )
    freeze_dot.dy = _RecordingDotDynamicState(call_order, effect_times=1)
    enemy.dynamic.dynamic_dot_list = _RecordingDotRuntimeList(call_order, [freeze_dot])
    enemy.dynamic.frozen = True
    enemy.dynamic.frostbite = True
    sim_instance.schedule_data.change_process_state = lambda: call_order.append(
        ("change_process_state", None)
    )
    disorder = SimpleNamespace(accompany_dot="Shock")
    _record_dot_runtime_state_adapter(monkeypatch, helper_calls)

    remove_dots_cause_disorder(
        disorder,
        enemy,
        create_schedule_dispatch_port(sim_instance=sim_instance),
        10,
    )

    assert recording_queue == [anomaly_event]
    assert helper_calls == [
        ("from_enemy", enemy),
        ("remove_all", (freeze_dot,)),
    ]
    assert call_order == [
        ("publish", anomaly_event),
        ("dy_ready", False),
        ("dy_last_effect_ticks", 10),
        ("dy_effect_times", 2),
        ("dot_end", dot_index),
        ("dot_remove", dot_index),
        ("change_process_state", None),
    ]
    assert freeze_dot.dy.ready is False
    assert freeze_dot.dy.last_effect_ticks == 10
    assert freeze_dot.dy.effect_times == 2
    assert freeze_dot.ended_at == 10
    assert enemy.dynamic.dynamic_dot_list == []
    assert enemy.dynamic.frozen is False
    assert enemy.dynamic.frostbite is False


def test_remove_dots_cause_disorder_removes_matching_non_freeze_dot_without_publish(
    monkeypatch,
):
    call_order: list[tuple[str, object]] = []
    helper_calls: list[tuple[str, object]] = []
    sim_instance = _build_sim_instance(_FailFastEventList())
    sim_instance.schedule_data.change_process_state = lambda: call_order.append(
        ("change_process_state", None)
    )
    enemy = _build_enemy(sim_instance)
    unrelated_dot = _FakeDot(index="Ignite", call_order=call_order)
    removed_dot = _FakeDot(index="Shock", call_order=call_order)
    enemy.dynamic.dynamic_dot_list = _RecordingDotRuntimeList(
        call_order,
        [unrelated_dot, removed_dot],
    )
    disorder = SimpleNamespace(accompany_dot="Shock")
    _record_dot_runtime_state_adapter(monkeypatch, helper_calls)

    remove_dots_cause_disorder(
        disorder,
        enemy,
        create_schedule_dispatch_port(sim_instance=sim_instance),
        23,
    )

    assert removed_dot.ended_at == 23
    assert helper_calls == [
        ("from_enemy", enemy),
        ("remove_all", (removed_dot,)),
    ]
    assert unrelated_dot.ended_at is None
    assert enemy.dynamic.dynamic_dot_list == [unrelated_dot]
    assert call_order == [
        ("dot_end", "Shock"),
        ("dot_remove", "Shock"),
        ("change_process_state", None),
    ]


def test_remove_dots_cause_disorder_rejects_invalid_runtime_dot_entry():
    sim_instance = _build_sim_instance(_FailFastEventList())
    sim_instance.schedule_data.change_process_state = lambda: (_ for _ in ()).throw(
        AssertionError("invalid dot entries should not update process state")
    )
    enemy = _build_enemy(sim_instance)
    enemy.dynamic.dynamic_dot_list = [object()]
    disorder = SimpleNamespace(accompany_dot="Shock")

    with pytest.raises(TypeError, match="不是DOT类"):
        remove_dots_cause_disorder(
            disorder,
            enemy,
            create_schedule_dispatch_port(sim_instance=sim_instance),
            23,
        )
