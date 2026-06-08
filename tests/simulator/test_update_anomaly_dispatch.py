from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from zsim.models.event_enums import ListenerBroadcastSignal as LBS
from zsim.sim_progress.Dot.BaseDot import Dot
from zsim.sim_progress.Update import UpdateAnomaly as update_anomaly_module
from zsim.sim_progress.Update.UpdateAnomaly import (
    anomaly_effect_active,
    remove_dots_cause_disorder,
    update_anomaly,
)
from zsim.sim_progress.anomaly_bar import AnomalyBar
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


def _build_skill_node(*, element_type: int, char_name: str = "alpha", skill_tag: str = "1001_TEST"):
    return SimpleNamespace(
        element_type=element_type,
        char_name=char_name,
        skill_tag=skill_tag,
        skill=SimpleNamespace(char_obj=SimpleNamespace(CID=1001)),
    )


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


def test_anomaly_effect_active_replaces_same_index_dot_without_scheduled_publish(
    monkeypatch,
):
    call_order: list[tuple[str, object]] = []
    sim_instance = _build_sim_instance(_FailFastEventList())
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

    anomaly_effect_active(
        SimpleNamespace(accompany_debuff=None, accompany_dot="Shock"),
        77,
        enemy,
        new_anomaly,
        3,
        sim_instance,
    )

    assert spawn_calls == [(3, 77, new_anomaly, sim_instance)]
    assert old_dot.ended_at == 77
    assert enemy.dynamic.dynamic_dot_list == [unrelated_dot, new_dot]
    assert enemy.dynamic.dynamic_dot_list.count(new_dot) == 1
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


def test_remove_dots_cause_disorder_publishes_freeze_follow_up_via_dispatch_port():
    call_order: list[tuple[str, object]] = []
    legacy_event_list = _FailFastEventList()
    sim_instance = _build_sim_instance(legacy_event_list)
    enemy = _build_enemy(sim_instance)
    anomaly_event = SimpleNamespace(marker="freeze-follow-up")
    freeze_dot = _FakeDot(
        index="Freez",
        anomaly_data=anomaly_event,
        call_order=call_order,
    )
    freeze_dot.dy.effect_times = 1
    enemy.dynamic.dynamic_dot_list.append(freeze_dot)

    recording_queue = _RecordingEventList(call_order)
    sim_instance.schedule_data.event_list = recording_queue
    disorder = SimpleNamespace(accompany_dot="Shock")

    remove_dots_cause_disorder(
        disorder,
        enemy,
        create_schedule_dispatch_port(sim_instance=sim_instance),
        10,
    )

    assert recording_queue == [anomaly_event]
    assert call_order == [("publish", anomaly_event), ("dot_end", "Freez")]
    assert freeze_dot.ended_at == 10
    assert enemy.dynamic.dynamic_dot_list == []
    assert enemy.dynamic.frozen is False
    assert enemy.dynamic.frostbite is False
