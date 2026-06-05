from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from zsim.sim_progress.Dot.BaseDot import Dot
from zsim.sim_progress.Update.UpdateAnomaly import (
    remove_dots_cause_disorder,
    update_anomaly,
)
from zsim.sim_progress.anomaly_bar import AnomalyBar
from zsim.sim_progress.data_struct.schedule_dispatch import create_schedule_dispatch_port


class _FailFastEventList(list):
    def append(self, item):
        raise AssertionError("UpdateAnomaly should publish scheduled events via dispatch port")


class _RecordingEventList(list):
    def append(self, item):
        super().append(item)


class _FakeDot(Dot):
    def __init__(self, *, index: str, anomaly_data=None):
        super().__init__(bar=None, sim_instance=None)
        self.ft.index = index
        self.ft.max_effect_times = 30
        self.anomaly_data = anomaly_data
        self.ended_at: int | None = None

    def end(self, timenow: int):
        self.ended_at = timenow
        super().end(timenow)


def _build_sim_instance(event_list):
    return SimpleNamespace(
        tick=10,
        schedule_data=SimpleNamespace(
            event_list=event_list,
            change_process_state=lambda: None,
        ),
        listener_manager=SimpleNamespace(broadcast_event=lambda **kwargs: None),
        decibel_manager=SimpleNamespace(update=lambda **kwargs: None),
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
    legacy_event_list = _FailFastEventList()
    sim_instance = _build_sim_instance(legacy_event_list)
    enemy = _build_enemy(sim_instance)
    enemy.anomaly_bars_dict[1] = _build_anomaly_bar(sim_instance, element_type=1)
    skill_node = _build_skill_node(element_type=1)
    chars = [SimpleNamespace(special_resources=lambda *args, **kwargs: None)]

    recording_queue = _RecordingEventList()
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
    assert recording_queue[0].element_type == 1
    assert recording_queue[0].activated_by is skill_node


def test_update_anomaly_preserves_new_anomaly_then_disorder_order_via_dispatch_port():
    legacy_event_list = _FailFastEventList()
    sim_instance = _build_sim_instance(legacy_event_list)
    enemy = _build_enemy(sim_instance)
    current_bar = _build_anomaly_bar(sim_instance, element_type=1)
    previous_bar = _build_anomaly_bar(sim_instance, element_type=3)
    previous_bar.active = True
    enemy.anomaly_bars_dict[1] = current_bar
    enemy.anomaly_bars_dict[3] = previous_bar
    enemy.dynamic.active_anomaly_bar_dict[3] = previous_bar
    setattr(enemy.dynamic, enemy.trans_anomaly_effect_to_str[3], True)
    skill_node = _build_skill_node(element_type=1)
    chars = [SimpleNamespace(special_resources=lambda *args, **kwargs: None)]

    recording_queue = _RecordingEventList()
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
    assert recording_queue[0].element_type == 1
    assert recording_queue[0].is_disorder is False
    assert recording_queue[1].element_type == 3
    assert recording_queue[1].is_disorder is True


def test_remove_dots_cause_disorder_publishes_freeze_follow_up_via_dispatch_port():
    legacy_event_list = _FailFastEventList()
    sim_instance = _build_sim_instance(legacy_event_list)
    enemy = _build_enemy(sim_instance)
    anomaly_event = SimpleNamespace(marker="freeze-follow-up")
    freeze_dot = _FakeDot(index="Freez", anomaly_data=anomaly_event)
    freeze_dot.dy.effect_times = 1
    enemy.dynamic.dynamic_dot_list.append(freeze_dot)

    recording_queue = _RecordingEventList()
    sim_instance.schedule_data.event_list = recording_queue
    disorder = SimpleNamespace(accompany_dot="Shock")

    remove_dots_cause_disorder(
        disorder,
        enemy,
        create_schedule_dispatch_port(sim_instance=sim_instance),
        10,
    )

    assert recording_queue == [anomaly_event]
    assert freeze_dot.ended_at == 10
    assert enemy.dynamic.dynamic_dot_list == []
    assert enemy.dynamic.frozen is False
    assert enemy.dynamic.frostbite is False
