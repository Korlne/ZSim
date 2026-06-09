from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Mapping, Sequence, cast

import pytest

import zsim.sim_progress.data_struct.BattleEventListener.AliceDotTriggerListener as alice_dot_module
import zsim.sim_progress.data_struct.schedule_dispatch as schedule_dispatch_module
from tests.simulator.test_buff_add_strategy_runtime_facade import (
    _assert_pending_queues_untouched,
    _BuffAddProbe,
    _FailFastPendingQueue,
    _make_sim_instance,
)
from zsim.models.event_enums import ListenerBroadcastSignal as LBS
from zsim.sim_progress.Buff import BuffAddStrategy as buff_add_strategy_module
from zsim.sim_progress.Buff.buff_class import Buff
from zsim.sim_progress.Buff.BuffAddStrategy import buff_add_strategy
from zsim.sim_progress.data_struct.BattleEventListener import ListenerManger
from zsim.sim_progress.data_struct.BattleEventListener.AliceDotTriggerListener import (
    AliceDotTriggerListener,
)
from zsim.sim_progress.data_struct.schedule_dispatch import (
    ScheduleDispatchPort,
    create_schedule_dispatch_port,
)
from zsim.sim_progress.Dot.BaseDot import Dot
from zsim.sim_progress.ScheduledEvent import buff_runtime as buff_runtime_module
from zsim.sim_progress.ScheduledEvent import runtime_command as runtime_command_module
from zsim.sim_progress.ScheduledEvent.buff_runtime import BuffRuntimeReadPort
from zsim.sim_progress.ScheduledEvent.event_handlers.context import EventContext
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers.preload import (
    PreloadEventHandler,
)
from zsim.sim_progress.ScheduledEvent.runtime_command import create_runtime_command_port


class _FailFastEventList(list[object]):
    def append(self, item: object) -> None:
        raise AssertionError("raw schedule queue append is not allowed in this sample")


class _RecordingDispatchPort:
    def __init__(self, call_order: list[str]) -> None:
        self.events: list[object] = []
        self._call_order = call_order

    def publish_scheduled(self, event: object) -> None:
        self._call_order.append("publish")
        self.events.append(event)


class _RecordingDotList(list[object]):
    def __init__(self, call_order: list[str]) -> None:
        super().__init__()
        self._call_order = call_order

    def append(self, item: object) -> None:
        self._call_order.append("register_dot")
        super().append(item)


class _FakeAnomalyBar:
    def __init__(self) -> None:
        self.settled = False

    def anomaly_settled(self) -> None:
        self.settled = True


class _FakeDot(Dot):
    def __init__(self, *, index: str, anomaly_data: object, call_order: list[str]) -> None:
        super().__init__(bar=None, sim_instance=None)
        self.ft.index = index
        self.ft.max_duration = 60
        self.anomaly_data = anomaly_data
        self.started_at: int | None = None
        self._call_order = call_order

    def start(self, timenow: int) -> None:
        self._call_order.append("dot_start")
        self.started_at = timenow
        super().start(timenow)


class _RuntimeViewStub(BuffRuntimeReadPort):
    def get_active_buffs(self, beneficiary: str) -> Sequence[Any]:
        return ()

    def get_active_buff_view(self) -> Mapping[str, Sequence[Any]]:
        return {}

    def get_exist_buff_snapshot(self, beneficiary: str) -> Mapping[str, Any]:
        return {}

    def get_exist_buff_snapshot_view(self) -> Mapping[str, Mapping[str, Any]]:
        return {}

    def get_legacy_dynamic_buff_dict(self) -> dict[str, list[Any]]:
        raise AssertionError("handler requeue should not read legacy dynamic buff")

    def get_legacy_exist_buff_dict(self) -> dict[str, dict[str, Any]]:
        raise AssertionError("handler requeue should not read legacy exist buff")


class _FuturePreloadEvent:
    execute_tick = 11

    def execute_myself(self) -> None:
        raise AssertionError("future preload event should be requeued without executing")


class _RecordingListener:
    def __init__(self, calls: list[tuple[object, LBS, dict[str, object]]]) -> None:
        self.calls = calls

    def listening_event(self, event: object, signal: LBS, **kwargs: object) -> None:
        self.calls.append((event, signal, kwargs))


def _install_buff_add_cross_layer_guards(
    monkeypatch: pytest.MonkeyPatch,
) -> list[tuple[str, str, object]]:
    facade_calls: list[tuple[str, str, object]] = []

    class _RecordingLegacyBuffRuntimeFacade(buff_runtime_module.LegacyBuffRuntimeFacade):
        def find_active_buff_by_index(self, beneficiary: str, buff_index: str) -> Buff | None:
            facade_calls.append(("find_active_buff_by_index", beneficiary, buff_index))
            return super().find_active_buff_by_index(beneficiary, buff_index)

        def remove_active_buff(self, beneficiary: str, buff: Buff) -> None:
            facade_calls.append(("remove_active_buff", beneficiary, buff))
            super().remove_active_buff(beneficiary, buff)

        def append_active_buff(self, beneficiary: str, buff: Buff) -> None:
            facade_calls.append(("append_active_buff", beneficiary, buff))
            super().append_active_buff(beneficiary, buff)

        def sync_enemy_debuff_mirror(self, buff: Buff) -> None:
            facade_calls.append(("sync_enemy_debuff_mirror", "enemy", buff))
            super().sync_enemy_debuff_mirror(buff)

    def create_recording_legacy_facade(
        **kwargs: Any,
    ) -> buff_runtime_module.BuffRuntimeFacade:
        facade_calls.append(
            ("create_legacy_buff_runtime_facade", "runtime", "LegacyBuffRuntimeFacade")
        )
        return _RecordingLegacyBuffRuntimeFacade(**kwargs)

    def fail_schedule_dispatch_port(*args: object, **kwargs: object) -> None:
        raise AssertionError("buff_add_strategy must not create ScheduleDispatchPort")

    def fail_runtime_command_port(*args: object, **kwargs: object) -> None:
        raise AssertionError("buff_add_strategy must not create RuntimeCommandPort")

    def fail_runtime_read_port(*args: object, **kwargs: object) -> None:
        raise AssertionError("buff_add_strategy must not create BuffRuntimeReadPort")

    monkeypatch.setattr(
        buff_runtime_module,
        "create_legacy_buff_runtime_facade",
        create_recording_legacy_facade,
    )
    monkeypatch.setattr(
        schedule_dispatch_module,
        "create_schedule_dispatch_port",
        fail_schedule_dispatch_port,
    )
    monkeypatch.setattr(
        runtime_command_module,
        "create_runtime_command_port",
        fail_runtime_command_port,
    )
    monkeypatch.setattr(
        buff_runtime_module,
        "create_buff_runtime_read_port",
        fail_runtime_read_port,
    )
    monkeypatch.setattr(
        buff_add_strategy_module,
        "create_schedule_dispatch_port",
        fail_schedule_dispatch_port,
        raising=False,
    )
    monkeypatch.setattr(
        buff_add_strategy_module,
        "create_runtime_command_port",
        fail_runtime_command_port,
        raising=False,
    )
    monkeypatch.setattr(
        buff_add_strategy_module,
        "create_buff_runtime_read_port",
        fail_runtime_read_port,
        raising=False,
    )
    return facade_calls


def test_schedule_dispatch_publish_is_queue_only_not_broadcast_or_runtime_write() -> None:
    event_list: list[object] = []
    schedule_data = SimpleNamespace(event_list=event_list)
    listener_calls: list[object] = []
    runtime_calls: list[object] = []

    dispatch_port = create_schedule_dispatch_port(schedule_data=cast(Any, schedule_data))

    assert isinstance(dispatch_port, ScheduleDispatchPort)

    dispatch_port.publish_scheduled("planned-event")

    assert event_list == ["planned-event"]
    assert listener_calls == []
    assert runtime_calls == []


def test_listener_broadcast_is_synchronous_not_schedule_publish() -> None:
    listener_calls: list[tuple[object, LBS, dict[str, object]]] = []
    schedule_data = SimpleNamespace(event_list=_FailFastEventList())
    manager = ListenerManger(cast(Any, SimpleNamespace(schedule_data=schedule_data)))
    cast(Any, manager)._listeners_group["enemy"]["probe"] = _RecordingListener(listener_calls)

    manager.broadcast_event(event="broadcast-event", signal=LBS.DISORDER_SPAWN, source="test")

    assert listener_calls == [
        ("broadcast-event", LBS.DISORDER_SPAWN, {"source": "test"}),
    ]
    assert schedule_data.event_list == []


def test_handler_requeue_uses_current_schedule_queue_not_dispatch_port() -> None:
    stale_event_list = _FailFastEventList()
    current_event_list: list[object] = []
    schedule_data = SimpleNamespace(event_list=stale_event_list)
    context = EventContext(
        data=cast(Any, schedule_data),
        tick=10,
        enemy=cast(Any, SimpleNamespace()),
        buff_runtime_view=_RuntimeViewStub(),
        runtime_command_port=cast(Any, SimpleNamespace()),
        action_stack=cast(Any, SimpleNamespace()),
        sim_instance=cast(Any, SimpleNamespace()),
    )
    event = _FuturePreloadEvent()

    schedule_data.event_list = current_event_list

    PreloadEventHandler().handle(cast(Any, event), context)

    assert stale_event_list == []
    assert current_event_list == [event]


def test_alice_dot_runtime_registration_precedes_scheduled_publish(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    call_order: list[str] = []
    dispatch_port = _RecordingDispatchPort(call_order)
    dynamic_dot_list = _RecordingDotList(call_order)
    enemy = SimpleNamespace(
        dynamic=SimpleNamespace(
            assault=True,
            dynamic_dot_list=dynamic_dot_list,
        ),
        anomaly_bars_dict={0: _FakeAnomalyBar()},
    )
    schedule_data = SimpleNamespace(
        enemy=enemy,
        event_list=_FailFastEventList(),
        change_process_state=lambda: None,
    )
    sim_instance = SimpleNamespace(
        tick=17,
        schedule_data=schedule_data,
        char_data=SimpleNamespace(find_char_obj=lambda CID: SimpleNamespace(CID=CID)),
    )
    listener = AliceDotTriggerListener(listener_id="Alice_5", sim_instance=cast(Any, sim_instance))
    anomaly_payload = SimpleNamespace(tag="alice-dot-anomaly")
    replacement_dot = _FakeDot(
        index="AliceCoreSkillAssaultDot",
        anomaly_data=anomaly_payload,
        call_order=call_order,
    )

    def fake_spawn_normal_dot(
        *, dot_index: str, sim_instance: object, bar: _FakeAnomalyBar
    ) -> _FakeDot:
        assert dot_index == "AliceCoreSkillAssaultDot"
        assert sim_instance is listener.sim_instance
        assert bar.settled is True
        return replacement_dot

    monkeypatch.setattr(alice_dot_module, "ALICE_REPORT", False)
    monkeypatch.setattr(
        alice_dot_module,
        "create_schedule_dispatch_port",
        lambda *, sim_instance: dispatch_port,
    )
    monkeypatch.setattr(
        "zsim.sim_progress.Update.UpdateAnomaly.spawn_normal_dot",
        fake_spawn_normal_dot,
    )

    listener.listening_event(event=None, signal=LBS.ASSAULT_STATE_ON)

    assert call_order == ["dot_start", "register_dot", "publish"]
    assert dynamic_dot_list == [replacement_dot]
    assert dispatch_port.events == [anomaly_payload]
    assert schedule_data.event_list == []
    assert replacement_dot.started_at == 17


def test_runtime_command_same_tick_write_does_not_publish_or_broadcast(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stale_event_list = _FailFastEventList()
    current_event_list = _FailFastEventList()
    dynamic_buff: dict[str, list[object]] = {"enemy": []}
    schedule_data = SimpleNamespace(
        event_list=stale_event_list,
        char_obj_list=[SimpleNamespace(NAME="Alice")],
        dynamic_buff=dynamic_buff,
    )
    exist_buff_dict: dict[str, dict[str, object]] = {"enemy": {}}

    def fail_broadcast(**kwargs: object) -> None:
        raise AssertionError("runtime command should not broadcast listener events")

    sim_instance = SimpleNamespace(listener_manager=SimpleNamespace(broadcast_event=fail_broadcast))
    captured: list[tuple[str, object]] = []

    def fake_update_anomaly(
        element_type: int,
        enemy: object,
        tick: int,
        event_list: list[object],
        char_obj_list: list[object],
        *,
        skill_node: object,
        dynamic_buff_dict: dict[str, list[object]],
        sim_instance: object,
        **kwargs: object,
    ) -> None:
        captured.append(("update_event_list", event_list))
        captured.append(("update_dynamic_buff", dynamic_buff_dict))

    def fake_schedule_buff_settle(
        tick: int,
        exist_buff_dict_arg: dict[str, dict[str, object]],
        enemy: object,
        dynamic_buff_arg: dict[str, list[object]],
        action_stack_arg: object,
        *,
        sim_instance: object,
        **kwargs: object,
    ) -> None:
        dynamic_buff_arg["enemy"].append("same-tick-settle")
        captured.append(("settle_dynamic_buff", dynamic_buff_arg))

    monkeypatch.setattr(runtime_command_module, "legacy_update_anomaly", fake_update_anomaly)
    monkeypatch.setattr(
        runtime_command_module,
        "legacy_schedule_buff_settle",
        fake_schedule_buff_settle,
    )
    port = create_runtime_command_port(
        data=cast(Any, schedule_data),
        exist_buff_dict=cast(Any, exist_buff_dict),
        action_stack=cast(Any, SimpleNamespace()),
        sim_instance=cast(Any, sim_instance),
    )
    enemy = SimpleNamespace()
    skill_node = SimpleNamespace(skill_tag="1001_TEST")

    schedule_data.event_list = current_event_list

    port.update_anomaly(
        element_type=1,
        enemy=cast(Any, enemy),
        tick=18,
        skill_node=cast(Any, skill_node),
    )
    port.settle_buffs(tick=18, enemy=cast(Any, enemy), skill_node=cast(Any, skill_node))

    assert captured == [
        ("update_event_list", current_event_list),
        ("update_dynamic_buff", dynamic_buff),
        ("settle_dynamic_buff", dynamic_buff),
    ]
    assert dynamic_buff["enemy"] == ["same-tick-settle"]
    assert current_event_list == []


def test_buff_add_strategy_forced_write_stays_out_of_schedule_and_listener_layers() -> None:
    template_buff = _BuffAddProbe("forced-buff", count=1)
    old_active_buff = _BuffAddProbe("forced-buff", count=9)
    active_store: list[Any] = [old_active_buff]
    pending_queue: list[Any] = []
    schedule_event_list = _FailFastEventList()
    listener_calls: list[object] = []
    sim_instance = _make_sim_instance(
        exist_buff_dict={"Alice": {"forced-buff": template_buff}},
        loading_buff_dict={"Alice": pending_queue},
        dynamic_buff_dict={"Alice": active_store},
        enemy_debuff_mirror=[],
    )
    sim_instance.schedule_data.event_list = schedule_event_list
    sim_instance.listener_manager = SimpleNamespace(
        broadcast_event=lambda **kwargs: listener_calls.append(kwargs)
    )

    buff_add_strategy(
        "forced-buff",
        benifit_list=["Alice"],
        specified_count=3,
        sim_instance=cast(Any, sim_instance),
    )

    assert schedule_event_list == []
    assert listener_calls == []
    assert pending_queue == []
    assert len(active_store) == 1
    assert active_store[0] is not old_active_buff
    assert active_store[0].dy.count == 3


def test_buff_add_strategy_cross_layer_boundary_covers_target_shapes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    facade_calls = _install_buff_add_cross_layer_guards(monkeypatch)

    fanout_pending: dict[str, list[Buff]] = {
        "Alice": _FailFastPendingQueue(),
        "Bob": _FailFastPendingQueue(),
        "Corin": _FailFastPendingQueue(),
    }
    alice_store: list[Buff] = [_BuffAddProbe("fanout-boundary", count=8)]
    bob_store: list[Buff] = []
    corin_store: list[Buff] = []
    fanout_sim = _make_sim_instance(
        exist_buff_dict={
            "Alice": {"fanout-boundary": _BuffAddProbe("fanout-boundary", add_buff_to="1100")},
            "Bob": {"fanout-boundary": _BuffAddProbe("fanout-boundary", add_buff_to="1100")},
            "Corin": {"fanout-boundary": _BuffAddProbe("fanout-boundary", add_buff_to="1100")},
        },
        loading_buff_dict=fanout_pending,
        dynamic_buff_dict={
            "Alice": alice_store,
            "Bob": bob_store,
            "Corin": corin_store,
        },
        enemy_debuff_mirror=[],
    )
    fanout_sim.load_data.all_name_order_box = {
        "Alice": ["Alice", "Bob", "Corin", "Daisy"],
        "enemy": ["enemy"],
    }

    buff_add_strategy("fanout-boundary", sim_instance=fanout_sim)

    _assert_pending_queues_untouched(fanout_sim, fanout_pending)
    assert fanout_sim.schedule_data.event_list == []
    assert [call[:2] for call in facade_calls if call[0] == "append_active_buff"] == [
        ("append_active_buff", "Alice"),
        ("append_active_buff", "Bob"),
    ]
    assert any(
        call
        == (
            "create_legacy_buff_runtime_facade",
            "runtime",
            "LegacyBuffRuntimeFacade",
        )
        for call in facade_calls
    )

    explicit_start = len(facade_calls)
    explicit_pending: dict[str, list[Buff]] = {
        "Alice": _FailFastPendingQueue(),
        "Bob": _FailFastPendingQueue(),
        "Corin": _FailFastPendingQueue(),
    }
    explicit_sim = _make_sim_instance(
        exist_buff_dict={
            "Alice": {"explicit-boundary": _BuffAddProbe("explicit-boundary", add_buff_to="1100")},
            "Bob": {"explicit-boundary": _BuffAddProbe("explicit-boundary", add_buff_to="1100")},
            "Corin": {"explicit-boundary": _BuffAddProbe("explicit-boundary", add_buff_to="1100")},
        },
        loading_buff_dict=explicit_pending,
        dynamic_buff_dict={
            "Alice": [],
            "Bob": [],
            "Corin": [],
        },
        enemy_debuff_mirror=[],
    )
    explicit_sim.load_data.all_name_order_box = fanout_sim.load_data.all_name_order_box

    buff_add_strategy(
        "explicit-boundary",
        benifit_list=["Corin"],
        sim_instance=explicit_sim,
    )

    explicit_calls = facade_calls[explicit_start:]
    _assert_pending_queues_untouched(explicit_sim, explicit_pending)
    assert explicit_sim.schedule_data.event_list == []
    assert [call[:2] for call in explicit_calls if call[0] == "append_active_buff"] == [
        ("append_active_buff", "Corin"),
    ]

    enemy_start = len(facade_calls)
    enemy_pending: dict[str, list[Buff]] = {"enemy": _FailFastPendingQueue()}
    old_enemy_buff = _BuffAddProbe("enemy-boundary", operator="enemy")
    old_enemy_mirror = _BuffAddProbe("enemy-boundary", operator="enemy")
    enemy_store: list[Buff] = [old_enemy_buff]
    enemy_mirror: list[Buff] = [old_enemy_mirror]
    enemy_sim = _make_sim_instance(
        exist_buff_dict={
            "enemy": {
                "enemy-boundary": _BuffAddProbe(
                    "enemy-boundary",
                    operator="enemy",
                    add_buff_to="0001",
                )
            }
        },
        loading_buff_dict=enemy_pending,
        dynamic_buff_dict={"enemy": enemy_store},
        enemy_debuff_mirror=enemy_mirror,
    )

    buff_add_strategy(
        "enemy-boundary",
        benifit_list=["enemy"],
        sim_instance=enemy_sim,
    )

    enemy_calls = facade_calls[enemy_start:]
    _assert_pending_queues_untouched(enemy_sim, enemy_pending)
    assert enemy_sim.schedule_data.event_list == []
    assert len(enemy_store) == 1
    new_enemy_buff = enemy_store[0]
    assert new_enemy_buff is not old_enemy_buff
    assert enemy_mirror == [new_enemy_buff]
    assert (
        "sync_enemy_debuff_mirror",
        "enemy",
        new_enemy_buff,
    ) in enemy_calls


def test_buff_runtime_read_port_exposes_no_public_write_methods() -> None:
    write_prefixes = (
        "activate",
        "append",
        "clear",
        "drain",
        "end",
        "enqueue",
        "remove",
        "replace",
        "settle",
        "sync",
        "update",
    )
    public_names = {name for name in BuffRuntimeReadPort.__dict__ if not name.startswith("_")}

    assert {name for name in public_names if name.startswith(write_prefixes)} == set()
