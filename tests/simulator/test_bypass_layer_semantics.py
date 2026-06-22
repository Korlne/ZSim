from __future__ import annotations

import inspect
from types import SimpleNamespace
from typing import Any, Mapping, Sequence, cast

import pytest

import zsim.sim_progress.Buff.BuffXLogic.SeedCinema6Trigger as seed_cinema6_module
import zsim.sim_progress.Buff.BuffXLogic.YuzuhaCinema6SheelTrigger as yuzuha_cinema6_module
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
from zsim.sim_progress.Buff.JudgeTools import build_preparation_context_from_sim_instance
from zsim.sim_progress.Buff.buff_class import Buff
from zsim.sim_progress.Buff.BuffAddStrategy import buff_add_strategy
from zsim.sim_progress.data_struct.BattleEventListener import ListenerManger
from zsim.sim_progress.data_struct.BattleEventListener.AliceDotTriggerListener import (
    AliceDotTriggerListener,
)
from zsim.sim_progress.data_struct.SchedulePreload import SchedulePreload
from zsim.sim_progress.data_struct.schedule_dispatch import (
    ScheduleDispatchPort,
    ScheduledEventEmitterProvider,
    create_schedule_dispatch_port,
)
from zsim.sim_progress.Dot.BaseDot import Dot
from zsim.sim_progress.ScheduledEvent import buff_runtime as buff_runtime_module
from zsim.sim_progress.ScheduledEvent import runtime_command as runtime_command_module
from zsim.sim_progress.ScheduledEvent.buff_runtime import BuffRuntimeReadPort
from zsim.sim_progress.ScheduledEvent.event_handlers.context import EventContext
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers.polarized_assault import (
    PolarizedAssaultEventHandler,
)
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers.preload import (
    PreloadEventHandler,
)
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers.quick_assist import (
    QuickAssistEventHandler,
)
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers.stun_forced_termination import (
    StunForcedTerminationEventHandler,
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


class _FutureRetainedEvent:
    execute_tick = 11

    def execute_myself(self) -> None:
        raise AssertionError("future retained event should be requeued without executing")

    def execute_update(self, tick: int) -> None:
        raise AssertionError("future retained event should be requeued without executing")

    def execute(self) -> None:
        raise AssertionError("future retained event should be requeued without executing")


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

    def create_recording_state_facade(
        self: buff_runtime_module.BuffRuntimeState,
    ) -> buff_runtime_module.BuffRuntimeFacade:
        facade_calls.append(
            ("create_buff_runtime_state_facade", "runtime", "BuffRuntimeState")
        )
        return _RecordingLegacyBuffRuntimeFacade(runtime_state=self)

    def fail_schedule_dispatch_port(*args: object, **kwargs: object) -> None:
        raise AssertionError("buff_add_strategy must not create ScheduleDispatchPort")

    def fail_runtime_command_port(*args: object, **kwargs: object) -> None:
        raise AssertionError("buff_add_strategy must not create RuntimeCommandPort")

    def fail_runtime_read_port(*args: object, **kwargs: object) -> None:
        raise AssertionError("buff_add_strategy must not create BuffRuntimeReadPort")

    monkeypatch.setattr(
        buff_runtime_module.BuffRuntimeState,
        "create_facade",
        create_recording_state_facade,
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


@pytest.mark.parametrize(
    "handler_cls",
    [
        PreloadEventHandler,
        QuickAssistEventHandler,
        PolarizedAssaultEventHandler,
        StunForcedTerminationEventHandler,
    ],
)
def test_handler_requeue_uses_current_schedule_queue_not_dispatch_port(
    handler_cls: type[Any],
) -> None:
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
    event = _FutureRetainedEvent()

    schedule_data.event_list = current_event_list

    handler_cls().handle(cast(Any, event), context)

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
    listener = AliceDotTriggerListener(
        listener_id="Alice_5",
        sim_instance=cast(Any, sim_instance),
        scheduled_event_emitter_provider=ScheduledEventEmitterProvider(
            lambda: cast(ScheduleDispatchPort, dispatch_port)
        ),
    )
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
        "zsim.sim_progress.Update.UpdateAnomaly.spawn_normal_dot",
        fake_spawn_normal_dot,
    )

    listener.listening_event(event=None, signal=LBS.ASSAULT_STATE_ON)

    assert call_order == ["dot_start", "register_dot", "publish"]
    assert dynamic_dot_list == [replacement_dot]
    assert dispatch_port.events == [anomaly_payload]
    assert schedule_data.event_list == []
    assert replacement_dot.started_at == 17


def test_preparation_context_preload_commands_publish_only_scheduled_events() -> None:
    event_list: list[object] = []
    listener_calls: list[object] = []
    runtime_calls: list[object] = []
    preload_data = SimpleNamespace(marker="preload-data")
    sim_instance = SimpleNamespace(
        tick=23,
        load_data=SimpleNamespace(
            exist_buff_dict={},
            action_stack=SimpleNamespace(),
        ),
        init_data=SimpleNamespace(Judge_list_set=[]),
        char_data=SimpleNamespace(char_obj_list=[]),
        global_stats=SimpleNamespace(DYNAMIC_BUFF_DICT={}),
        schedule_data=SimpleNamespace(
            event_list=event_list,
            enemy=SimpleNamespace(),
        ),
        preload=SimpleNamespace(preload_data=preload_data),
        listener_manager=SimpleNamespace(
            broadcast_event=lambda **kwargs: listener_calls.append(kwargs)
        ),
        runtime_command_port=SimpleNamespace(
            update_anomaly=lambda **kwargs: runtime_calls.append(kwargs)
        ),
    )
    preparation_context = build_preparation_context_from_sim_instance(
        cast(Any, sim_instance)
    )

    preparation_context.preload_commands.schedule_preload_events(
        preload_tick_list=[23, 24],
        skill_tag_list=["1461_Cinema_6", "1461_Cinema_6"],
        apl_priority_list=[0, 1],
        active_generation_list=[False, True],
    )

    assert [type(event) for event in event_list] == [SchedulePreload, SchedulePreload]
    assert [cast(SchedulePreload, event).execute_tick for event in event_list] == [
        23,
        24,
    ]
    assert [cast(SchedulePreload, event).skill_tag for event in event_list] == [
        "1461_Cinema_6",
        "1461_Cinema_6",
    ]
    assert [cast(SchedulePreload, event).apl_priority for event in event_list] == [0, 1]
    assert [cast(SchedulePreload, event).active_generation for event in event_list] == [
        False,
        True,
    ]
    assert all(cast(SchedulePreload, event).preload_data is preload_data for event in event_list)
    assert listener_calls == []
    assert runtime_calls == []


def test_seed_cinema6_preload_spawn_uses_context_command_surface_guardrail() -> None:
    source = inspect.getsource(seed_cinema6_module.SeedCinema6Trigger)

    assert "preload_commands.schedule_preload_events(" in source
    assert "schedule_preload_event_factory(" not in source
    assert "create_schedule_dispatch_port" not in source
    assert "publish_scheduled" not in source
    assert "RuntimeCommandPort" not in source
    assert "listener_manager" not in source
    assert "broadcast_event" not in source


def test_yuzuha_cinema6_preload_spawn_uses_context_command_surface_guardrail() -> None:
    source = inspect.getsource(yuzuha_cinema6_module.YuzuhaCinema6SheelTrigger)

    assert "preload_commands.schedule_preload_events(" in source
    assert "schedule_preload_event_factory(" not in source
    assert "create_schedule_dispatch_port" not in source
    assert "publish_scheduled" not in source
    assert "RuntimeCommandPort" not in source
    assert "listener_manager" not in source
    assert "broadcast_event" not in source


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

    sim_instance = SimpleNamespace(
        schedule_data=schedule_data,
        listener_manager=SimpleNamespace(broadcast_event=fail_broadcast),
    )
    captured: list[tuple[str, object]] = []

    def fake_update_anomaly(
        *,
        element_type: int,
        enemy: object,
        time_now: int,
        char_obj_list: list[object],
        sim_instance: object,
        skill_node: object,
        dynamic_buff_dict: dict[str, list[object]],
        runtime_context: object,
        **kwargs: object,
    ) -> None:
        captured.append(("update_time", time_now))
        captured.append(("update_char_obj_list", char_obj_list))
        captured.append(("update_dynamic_buff", dynamic_buff_dict))
        captured.append(("update_runtime_context", runtime_context))

    def fake_settle_schedule_buffs(
        self: Any,
        *,
        tick: int,
        enemy: object,
        sim_instance: object,
        skill_node: object | None = None,
        anomaly_bar: object | None = None,
    ) -> None:
        dynamic_buff_arg = self._runtime_state.active_store_for_compat()
        dynamic_buff_arg["enemy"].append("same-tick-settle")
        captured.append(("settle_dynamic_buff", dynamic_buff_arg))

    monkeypatch.setattr(runtime_command_module, "run_update_anomaly", fake_update_anomaly)
    monkeypatch.setattr(
        buff_runtime_module.DefaultBuffRuntimeFacade,
        "settle_schedule_buffs",
        fake_settle_schedule_buffs,
    )
    port = create_runtime_command_port(
        data=cast(Any, schedule_data),
        exist_buff_dict=cast(Any, exist_buff_dict),
        action_stack=cast(Any, SimpleNamespace()),
        sim_instance=cast(Any, sim_instance),
    )
    enemy = SimpleNamespace(dynamic=SimpleNamespace(dynamic_dot_list=[]))
    skill_node = SimpleNamespace(skill_tag="1001_TEST")

    schedule_data.event_list = current_event_list

    port.update_anomaly(
        element_type=1,
        enemy=cast(Any, enemy),
        tick=18,
        skill_node=cast(Any, skill_node),
    )
    port.settle_buffs(tick=18, enemy=cast(Any, enemy), skill_node=cast(Any, skill_node))

    runtime_context = cast(Any, captured[3][1])
    assert captured == [
        ("update_time", 18),
        ("update_char_obj_list", schedule_data.char_obj_list),
        ("update_dynamic_buff", dynamic_buff),
        ("update_runtime_context", runtime_context),
        ("settle_dynamic_buff", dynamic_buff),
    ]
    assert runtime_context.sim_instance is sim_instance
    assert runtime_context.buff_runtime_view is None
    assert runtime_context.dot_runtime_state.snapshot() == ()
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
            "create_buff_runtime_state_facade",
            "runtime",
            "BuffRuntimeState",
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
    runtime_enemy_store = enemy_sim.global_stats.DYNAMIC_BUFF_DICT["enemy"]
    assert runtime_enemy_store is enemy_mirror

    buff_add_strategy(
        "enemy-boundary",
        benifit_list=["enemy"],
        sim_instance=enemy_sim,
    )

    enemy_calls = facade_calls[enemy_start:]
    _assert_pending_queues_untouched(enemy_sim, enemy_pending)
    assert enemy_sim.schedule_data.event_list == []
    assert enemy_store == [old_enemy_buff]
    assert len(runtime_enemy_store) == 1
    new_enemy_buff = runtime_enemy_store[0]
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
