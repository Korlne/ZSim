from __future__ import annotations

from types import SimpleNamespace

import pytest
import zsim.sim_progress.data_struct.BattleEventListener.AliceDotTriggerListener as listener_module

from zsim.models.event_enums import ListenerBroadcastSignal as LBS
from zsim.sim_progress.Dot.BaseDot import Dot
from zsim.sim_progress.data_struct.BattleEventListener.AliceDotTriggerListener import (
    AliceDotTriggerListener,
)


class _FailFastEventList(list):
    def append(self, item):
        raise AssertionError("AliceDotTriggerListener should publish via dispatch port")


class _RecordingDispatchPort:
    def __init__(self) -> None:
        self.events: list[object] = []

    def publish_scheduled(self, event: object) -> None:
        self.events.append(event)


class _FakeAnomalyBar:
    def __init__(self) -> None:
        self.settled = False

    def anomaly_settled(self) -> None:
        self.settled = True


class _FakeDot(Dot):
    def __init__(self, *, index: str, anomaly_data: object) -> None:
        super().__init__(bar=None, sim_instance=None)
        self.ft.index = index
        self.ft.max_duration = 60
        self.anomaly_data = anomaly_data
        self.started_at: int | None = None
        self.ended_at: int | None = None

    def start(self, timenow: int):
        self.started_at = timenow
        super().start(timenow)

    def end(self, timenow: int):
        self.ended_at = timenow
        super().end(timenow)


def _build_listener(*, event_list):
    enemy = SimpleNamespace(
        dynamic=SimpleNamespace(
            assault=True,
            dynamic_dot_list=[],
        ),
        anomaly_bars_dict={0: _FakeAnomalyBar()},
    )
    sim_instance = SimpleNamespace(
        tick=10,
        schedule_data=SimpleNamespace(
            enemy=enemy,
            event_list=event_list,
            change_process_state=lambda: None,
        ),
        char_data=SimpleNamespace(find_char_obj=lambda CID: SimpleNamespace(CID=CID, NAME="Alice")),
    )
    return AliceDotTriggerListener(listener_id="Alice_5", sim_instance=sim_instance), sim_instance, enemy


def test_alice_dot_trigger_listener_publishes_dot_anomaly_via_dispatch_port(
    monkeypatch: pytest.MonkeyPatch,
):
    dispatch_port = _RecordingDispatchPort()
    listener, sim_instance, enemy = _build_listener(event_list=_FailFastEventList())
    previous_dot = _FakeDot(index="AliceCoreSkillAssaultDot", anomaly_data=SimpleNamespace(tag="old"))
    enemy.dynamic.dynamic_dot_list.append(previous_dot)
    published_bar = SimpleNamespace(tag="new")
    replacement_dot = _FakeDot(index="AliceCoreSkillAssaultDot", anomaly_data=published_bar)
    received_bar: dict[str, _FakeAnomalyBar] = {}

    def fake_create_dispatch_port(*, sim_instance):
        assert sim_instance is listener.sim_instance
        return dispatch_port

    def fake_spawn_normal_dot(*, dot_index, sim_instance, bar: _FakeAnomalyBar):
        assert dot_index == "AliceCoreSkillAssaultDot"
        assert sim_instance is listener.sim_instance
        received_bar["value"] = bar
        return replacement_dot

    monkeypatch.setattr(listener_module, "create_schedule_dispatch_port", fake_create_dispatch_port)
    monkeypatch.setattr(
        "zsim.sim_progress.Update.UpdateAnomaly.spawn_normal_dot",
        fake_spawn_normal_dot,
    )

    listener.listening_event(event=None, signal=LBS.ASSAULT_STATE_ON)

    assert listener.char is not None
    assert previous_dot.ended_at == sim_instance.tick
    assert replacement_dot.started_at == sim_instance.tick
    assert enemy.dynamic.dynamic_dot_list == [replacement_dot]
    assert dispatch_port.events == [published_bar]
    assert sim_instance.schedule_data.event_list == []
    assert received_bar["value"] is not enemy.anomaly_bars_dict[0]
    assert received_bar["value"].settled is True
