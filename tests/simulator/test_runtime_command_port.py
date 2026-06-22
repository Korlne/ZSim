from types import SimpleNamespace
from typing import Any, cast

import pytest

import zsim.sim_progress.ScheduledEvent as scheduled_event_module
from zsim.sim_progress.Buff.buff_class import Buff
from zsim.sim_progress.ScheduledEvent import buff_runtime as buff_runtime_module
from zsim.sim_progress.ScheduledEvent.buff_runtime import (
    BuffRuntimeState,
    DefaultBuffRuntimeReadAdapter,
    LegacyBuffRuntimeReadAdapter,
)
from zsim.sim_progress.ScheduledEvent import runtime_command as runtime_command_module
from zsim.sim_progress.ScheduledEvent.runtime_command import (
    LegacyRuntimeCommandAdapter,
    create_runtime_command_port,
)


def _runtime_state_for_test(
    *,
    exist_buff_dict: dict,
    dynamic_buff: dict,
    loading_buff: dict | None = None,
    enemy_mirror: list | None = None,
) -> BuffRuntimeState:
    return BuffRuntimeState(
        template_registry=exist_buff_dict,
        pending_queue={} if loading_buff is None else loading_buff,
        active_store=dynamic_buff,
        enemy_mirror=[] if enemy_mirror is None else enemy_mirror,
    )


class _ScheduleLogicProbe:
    def __init__(self, calls: list[tuple[str, dict[str, object]]]) -> None:
        self._calls = calls

    def xjudge(self, **kwargs) -> bool:
        self._calls.append(("xjudge", kwargs))
        return True

    def xeffect(self, **kwargs) -> None:
        self._calls.append(("xeffect", kwargs))


def _make_schedule_buff(
    index: str,
    *,
    logic: object | None = None,
    add_buff_to: int = 1,
    operator: str = "alpha",
    simple_effect_logic: bool = False,
    count: int = 0,
) -> Buff:
    buff = Buff.__new__(Buff)
    buff.ft = SimpleNamespace(
        index=index,
        schedule_judge=True,
        passively_updating=False,
        backend_acitve=True,
        add_buff_to=add_buff_to,
        operator=operator,
        simple_effect_logic=simple_effect_logic,
        individual_settled=False,
        maxduration=10,
        step=1,
        maxcount=99,
    )
    buff.dy = SimpleNamespace(
        active=False,
        ready=True,
        startticks=0,
        endticks=0,
        count=count,
        built_in_buff_box=[],
        is_changed=False,
    )
    buff.history = SimpleNamespace(active_times=0)
    buff.logic = logic if logic is not None else SimpleNamespace(
        xjudge=lambda **kwargs: True,
        xeffect=lambda **kwargs: None,
    )
    return buff


def test_runtime_command_port_preserves_legacy_container_identity_for_same_tick_writes(
    monkeypatch: pytest.MonkeyPatch,
):
    stale_event_list = ["stale"]
    current_event_list: list[object] = []
    char_obj_list = [SimpleNamespace(NAME="alpha")]
    dynamic_buff = {"alpha": [object()], "enemy": [object()]}
    exist_buff_dict = {"alpha": {"buff": object()}, "enemy": {}}
    action_stack = SimpleNamespace()
    runtime_state = _runtime_state_for_test(
        exist_buff_dict=exist_buff_dict,
        dynamic_buff=dynamic_buff,
    )
    runtime_view = LegacyBuffRuntimeReadAdapter(runtime_state=runtime_state)
    schedule_data = SimpleNamespace(
        event_list=stale_event_list,
        char_obj_list=char_obj_list,
        dynamic_buff=dynamic_buff,
    )
    sim_instance = cast(
        Any,
        SimpleNamespace(
            schedule_data=schedule_data,
            listener_manager=SimpleNamespace(broadcast_event=lambda **kwargs: None),
        ),
    )
    port = create_runtime_command_port(
        data=schedule_data,
        exist_buff_dict=exist_buff_dict,
        action_stack=action_stack,
        sim_instance=sim_instance,
        buff_runtime_view=runtime_view,
    )
    enemy = SimpleNamespace(dynamic=SimpleNamespace(dynamic_dot_list=[]))
    skill_node = SimpleNamespace(skill_tag="1001_TEST")
    captured: dict[str, Any] = {}

    def _fake_update_anomaly(
        *,
        element_type,
        enemy,
        time_now,
        char_obj_list,
        sim_instance,
        skill_node,
        dynamic_buff_dict,
        runtime_context,
        **kwargs,
    ) -> None:
        captured["element_type"] = element_type
        captured["enemy"] = enemy
        captured["tick"] = time_now
        captured["char_obj_list"] = char_obj_list
        captured["skill_node"] = skill_node
        captured["dynamic_buff_dict"] = dynamic_buff_dict
        captured["sim_instance"] = sim_instance
        captured["runtime_context"] = runtime_context

    def _fake_settle_schedule_buffs(
        self,
        *,
        tick,
        enemy,
        sim_instance,
        skill_node=None,
        anomaly_bar=None,
    ) -> None:
        captured["settle_tick"] = tick
        captured[
            "settle_exist_buff_dict"
        ] = self._runtime_state.template_registry_for_compat()
        captured["settle_enemy"] = enemy
        captured["settle_dynamic_buff"] = self._runtime_state.active_store_for_compat()
        captured["settle_sim_instance"] = sim_instance
        captured["settle_skill_node"] = skill_node
        captured["settle_anomaly_bar"] = anomaly_bar

    monkeypatch.setattr(runtime_command_module, "run_update_anomaly", _fake_update_anomaly)
    monkeypatch.setattr(
        buff_runtime_module.DefaultBuffRuntimeFacade,
        "settle_schedule_buffs",
        _fake_settle_schedule_buffs,
    )

    schedule_data.event_list = current_event_list

    assert isinstance(port, LegacyRuntimeCommandAdapter)

    port.update_anomaly(
        element_type=1,
        enemy=enemy,
        tick=10,
        skill_node=skill_node,
    )
    port.settle_buffs(
        tick=10,
        enemy=enemy,
        skill_node=skill_node,
    )

    assert captured["element_type"] == 1
    assert captured["enemy"] is enemy
    assert captured["tick"] == 10
    assert captured["char_obj_list"] is char_obj_list
    assert captured["skill_node"] is skill_node
    assert captured["dynamic_buff_dict"] is dynamic_buff
    assert captured["sim_instance"] is sim_instance
    runtime_context = captured["runtime_context"]
    assert runtime_context.sim_instance is sim_instance
    assert runtime_context.buff_runtime_view is runtime_view
    assert runtime_context.dot_runtime_state.snapshot() == ()
    runtime_context.dispatch_port.publish_scheduled("scheduled")
    assert current_event_list == ["scheduled"]
    assert stale_event_list == ["stale"]
    assert captured["settle_tick"] == 10
    assert captured["settle_exist_buff_dict"] is exist_buff_dict
    assert captured["settle_enemy"] is enemy
    assert captured["settle_dynamic_buff"] is dynamic_buff
    assert captured["settle_sim_instance"] is sim_instance
    assert captured["settle_skill_node"] is skill_node
    assert captured["settle_anomaly_bar"] is None


def test_runtime_command_settle_buffs_uses_runtime_owner_for_schedule_active_writes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, dict[str, object]]] = []
    schedule_buff = _make_schedule_buff(
        "enemy-schedule-buff",
        logic=_ScheduleLogicProbe(calls),
    )
    old_enemy_buff = _make_schedule_buff("enemy-schedule-buff")
    enemy_mirror = [old_enemy_buff]
    dynamic_buff = {
        "alpha": [],
        "beta": [],
        "gamma": [],
        "enemy": [old_enemy_buff],
    }
    exist_buff_dict = {
        "alpha": {"enemy-schedule-buff": schedule_buff},
        "beta": {},
        "gamma": {},
        "enemy": {},
    }
    schedule_data = SimpleNamespace(
        event_list=[],
        char_obj_list=[],
        dynamic_buff=dynamic_buff,
        loading_buff={},
    )
    enemy = SimpleNamespace(dynamic=SimpleNamespace(dynamic_debuff_list=enemy_mirror))
    sim_instance = SimpleNamespace()
    runtime_state = BuffRuntimeState(
        template_registry=exist_buff_dict,
        pending_queue=schedule_data.loading_buff,
        active_store=dynamic_buff,
        enemy_mirror=enemy_mirror,
    )
    active_owner = runtime_state.active_store_owner()
    active_owner_calls: list[tuple[str, str, str]] = []
    original_find_by_index = active_owner.find_by_index
    original_remove = active_owner.remove
    original_append = active_owner.append

    def recording_find_by_index(beneficiary: str, buff_index: str) -> Buff | None:
        active_owner_calls.append(("find", beneficiary, buff_index))
        return original_find_by_index(beneficiary, buff_index)

    def recording_remove(beneficiary: str, buff: Buff) -> None:
        active_owner_calls.append(("remove", beneficiary, buff.ft.index))
        original_remove(beneficiary, buff)

    def recording_append(beneficiary: str, buff: Buff) -> None:
        active_owner_calls.append(("append", beneficiary, buff.ft.index))
        original_append(beneficiary, buff)

    monkeypatch.setattr(active_owner, "find_by_index", recording_find_by_index)
    monkeypatch.setattr(active_owner, "remove", recording_remove)
    monkeypatch.setattr(active_owner, "append", recording_append)

    monkeypatch.setattr(
        "zsim.sim_progress.Buff.JudgeTools.find_preload_data",
        lambda sim_instance: SimpleNamespace(
            get_on_field_node=lambda tick: SimpleNamespace(char_name="alpha")
        ),
    )
    monkeypatch.setattr(
        "zsim.sim_progress.Buff.JudgeTools.find_all_name_order_box",
        lambda sim_instance: {
            "alpha": ["alpha", "beta", "gamma", "enemy"],
            "beta": ["beta", "alpha", "gamma", "enemy"],
            "gamma": ["gamma", "alpha", "beta", "enemy"],
        },
    )

    port = create_runtime_command_port(
        data=cast(Any, schedule_data),
        action_stack=cast(Any, SimpleNamespace()),
        sim_instance=cast(Any, sim_instance),
        buff_runtime_state=runtime_state,
    )

    port.settle_buffs(tick=18, enemy=cast(Any, enemy))

    assert calls == [("xjudge", {}), ("xeffect", {})]
    assert len(dynamic_buff["enemy"]) == 1
    new_enemy_buff = dynamic_buff["enemy"][0]
    assert new_enemy_buff is not old_enemy_buff
    assert new_enemy_buff is not schedule_buff
    assert new_enemy_buff.ft.index == "enemy-schedule-buff"
    assert enemy_mirror == [new_enemy_buff]
    assert active_owner_calls == [
        ("find", "enemy", "enemy-schedule-buff"),
        ("remove", "enemy", "enemy-schedule-buff"),
        ("append", "enemy", "enemy-schedule-buff"),
    ]


def test_runtime_command_settle_buffs_uses_template_owner_for_schedule_templates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, dict[str, object]]] = []
    owner_schedule_buff = _make_schedule_buff(
        "owner-schedule-buff",
        logic=_ScheduleLogicProbe(calls),
        simple_effect_logic=True,
    )
    shadow_schedule_buff = _make_schedule_buff(
        "owner-schedule-buff",
        simple_effect_logic=True,
        count=40,
    )
    dynamic_buff: dict[str, list[Buff]] = {
        "alpha": [],
        "beta": [],
        "gamma": [],
        "enemy": [],
    }
    runtime_registry: dict[str, dict[str, Buff]] = {
        "alpha": {"owner-schedule-buff": owner_schedule_buff},
        "beta": {},
        "gamma": {},
        "enemy": {},
    }
    runtime_state = BuffRuntimeState(
        template_registry=runtime_registry,
        pending_queue={},
        active_store=dynamic_buff,
        enemy_mirror=dynamic_buff["enemy"],
    )
    template_owner = runtime_state.template_registry_owner()
    owner_calls: list[str] = []
    original_for_owner = template_owner.for_owner

    def recording_for_owner(owner: str) -> dict[str, Buff]:
        owner_calls.append(owner)
        return original_for_owner(owner)

    def fail_compat_access() -> dict[str, dict[str, Buff]]:
        raise AssertionError("schedule settlement must use BuffTemplateRegistry owner")

    monkeypatch.setattr(template_owner, "for_owner", recording_for_owner)
    monkeypatch.setattr(runtime_state, "template_registry_for_compat", fail_compat_access)
    monkeypatch.setattr(
        "zsim.sim_progress.Buff.JudgeTools.find_preload_data",
        lambda sim_instance: SimpleNamespace(
            get_on_field_node=lambda tick: SimpleNamespace(char_name="alpha")
        ),
    )
    monkeypatch.setattr(
        "zsim.sim_progress.Buff.JudgeTools.find_all_name_order_box",
        lambda sim_instance: {
            "alpha": ["alpha", "beta", "gamma", "enemy"],
            "beta": ["beta", "alpha", "gamma", "enemy"],
            "gamma": ["gamma", "alpha", "beta", "enemy"],
        },
    )

    port = create_runtime_command_port(
        data=cast(
            Any,
            SimpleNamespace(
                event_list=[],
                char_obj_list=[],
                dynamic_buff=dynamic_buff,
                loading_buff={},
            ),
        ),
        action_stack=cast(Any, SimpleNamespace()),
        sim_instance=cast(Any, SimpleNamespace()),
        exist_buff_dict={"alpha": {"owner-schedule-buff": shadow_schedule_buff}},
        buff_runtime_state=runtime_state,
    )

    port.settle_buffs(tick=24, enemy=cast(Any, SimpleNamespace(dynamic=SimpleNamespace())))

    assert owner_calls == ["alpha", "beta", "gamma"]
    assert calls == [("xjudge", {})]
    assert len(dynamic_buff["enemy"]) == 1
    new_enemy_buff = dynamic_buff["enemy"][0]
    assert new_enemy_buff is not owner_schedule_buff
    assert new_enemy_buff.ft.index == "owner-schedule-buff"
    assert new_enemy_buff.dy.startticks == 24
    assert new_enemy_buff.dy.endticks == 34
    assert new_enemy_buff.dy.count == 1
    assert owner_schedule_buff.dy.count == 1
    assert owner_schedule_buff.history.active_times == 1
    assert shadow_schedule_buff.dy.count == 40
    assert shadow_schedule_buff.history.active_times == 0


class _FakeSkillNode:
    skill: SimpleNamespace
    element_type: int
    loading_mission: Any


class _RuntimeCommandProbe:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def update_anomaly(self, **kwargs) -> None:
        self.calls.append(("update_anomaly", kwargs))

    def settle_buffs(self, **kwargs) -> None:
        self.calls.append(("settle_buffs", kwargs))


def _build_scheduled_event_for_runtime_probe(
    runtime_command_port: _RuntimeCommandProbe,
) -> tuple[Any, SimpleNamespace]:
    enemy = SimpleNamespace(name="enemy")
    scheduled_event = cast(
        Any,
        scheduled_event_module.ScheduledEvent.__new__(scheduled_event_module.ScheduledEvent),
    )
    scheduled_event.runtime_command_port = runtime_command_port
    scheduled_event.enemy = enemy
    scheduled_event.tick = 10
    scheduled_event.sim_instance = SimpleNamespace(tick=10)
    return scheduled_event, enemy


def test_scheduled_event_compat_helper_routes_update_anomaly_through_runtime_command(
    monkeypatch: pytest.MonkeyPatch,
):
    call_order: list[object] = []
    runtime_command_port = _RuntimeCommandProbe()

    original_update_anomaly = runtime_command_port.update_anomaly

    def _record_update_anomaly(**kwargs) -> None:
        call_order.append("update_anomaly")
        original_update_anomaly(**kwargs)

    class _FakeLoadingMission:
        def __init__(self, mission_node: object) -> None:
            self.mission_node = mission_node
            self.hitted_count = 1

        def mission_start(self, *, timenow: int) -> None:
            call_order.append(("mission_start", timenow))

        def get_last_hit(self) -> int:
            call_order.append("get_last_hit")
            return 10

    monkeypatch.setattr(scheduled_event_module, "SkillNode", _FakeSkillNode)
    monkeypatch.setattr(scheduled_event_module, "LoadingMission", _FakeLoadingMission)
    monkeypatch.setattr(runtime_command_port, "update_anomaly", _record_update_anomaly)

    scheduled_event, enemy = _build_scheduled_event_for_runtime_probe(runtime_command_port)
    event = _FakeSkillNode()
    event.skill = SimpleNamespace(anomaly_update_rule=None)
    event.element_type = 3
    event.loading_mission = None

    scheduled_event.update_anomaly_bar_after_skill_event(event)

    assert call_order == [("mission_start", 10), "get_last_hit", "update_anomaly"]
    assert event.loading_mission is not None
    assert len(runtime_command_port.calls) == 1
    call_name, call_kwargs = runtime_command_port.calls[0]
    assert call_name == "update_anomaly"
    assert call_kwargs["element_type"] == 3
    assert call_kwargs["enemy"] is enemy
    assert call_kwargs["tick"] == 10
    assert call_kwargs["skill_node"] is event


def test_scheduled_event_compat_helper_skips_runtime_command_when_not_triggered(
    monkeypatch: pytest.MonkeyPatch,
):
    runtime_command_port = _RuntimeCommandProbe()
    monkeypatch.setattr(scheduled_event_module, "SkillNode", _FakeSkillNode)

    scheduled_event, _ = _build_scheduled_event_for_runtime_probe(runtime_command_port)
    event = _FakeSkillNode()
    event.skill = SimpleNamespace(anomaly_update_rule=[2])
    event.element_type = 3
    event.loading_mission = SimpleNamespace(hitted_count=1)

    scheduled_event.update_anomaly_bar_after_skill_event(event)

    assert runtime_command_port.calls == []


def test_scheduled_event_construction_creates_runtime_ports_from_retained_inputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dynamic_buff = {"alpha": [object()], "enemy": []}
    exist_buff_dict = {"alpha": {"buff": object()}, "enemy": {}}
    loading_buff: dict[str, list[Any]] = {"alpha": []}
    stale_event_list = ["stale"]
    current_event_list: list[object] = []
    char_obj_list = [SimpleNamespace(NAME="alpha")]
    enemy = SimpleNamespace(dynamic=SimpleNamespace(dynamic_dot_list=[]))
    schedule_data = SimpleNamespace(
        enemy=enemy,
        event_list=stale_event_list,
        char_obj_list=char_obj_list,
    )
    action_stack = SimpleNamespace()
    sim_instance = cast(
        Any,
        SimpleNamespace(
            tick=10,
            schedule_data=schedule_data,
            listener_manager=SimpleNamespace(broadcast_event=lambda **kwargs: None),
        ),
    )
    captured: dict[str, Any] = {}

    def _fake_update_anomaly(
        *,
        element_type,
        enemy,
        time_now,
        char_obj_list,
        sim_instance,
        skill_node,
        dynamic_buff_dict,
        runtime_context,
        **kwargs,
    ) -> None:
        captured["element_type"] = element_type
        captured["enemy"] = enemy
        captured["tick"] = time_now
        captured["char_obj_list"] = char_obj_list
        captured["skill_node"] = skill_node
        captured["dynamic_buff_dict"] = dynamic_buff_dict
        captured["sim_instance"] = sim_instance
        captured["runtime_context"] = runtime_context

    monkeypatch.setattr(
        scheduled_event_module.ScheduledEvent,
        "_ensure_handlers_registered",
        lambda self: None,
    )
    monkeypatch.setattr(runtime_command_module, "run_update_anomaly", _fake_update_anomaly)

    scheduled_event = scheduled_event_module.ScheduledEvent(
        dynamic_buff,
        schedule_data,
        10,
        exist_buff_dict,
        action_stack,
        loading_buff=loading_buff,
        sim_instance=sim_instance,
    )
    schedule_data.event_list = current_event_list
    skill_node = SimpleNamespace(skill_tag="1001_TEST")

    assert isinstance(scheduled_event.buff_runtime_view, DefaultBuffRuntimeReadAdapter)
    assert not isinstance(scheduled_event.buff_runtime_view, LegacyBuffRuntimeReadAdapter)
    assert isinstance(scheduled_event.runtime_command_port, LegacyRuntimeCommandAdapter)
    assert tuple(scheduled_event.buff_runtime_view.get_active_buffs("alpha")) == tuple(
        dynamic_buff["alpha"]
    )
    assert dict(scheduled_event.buff_runtime_view.get_exist_buff_snapshot("alpha")) == (
        exist_buff_dict["alpha"]
    )
    assert schedule_data.dynamic_buff is dynamic_buff
    assert schedule_data.loading_buff is loading_buff
    assert {
        "dynamic_buff",
        "loading_buff",
        "_dynamic_buff",
        "_exist_buff_dict",
        "_loading_buff",
    }.isdisjoint(vars(scheduled_event))

    scheduled_event.runtime_command_port.update_anomaly(
        element_type=3,
        enemy=enemy,
        tick=10,
        skill_node=skill_node,
    )

    assert captured["element_type"] == 3
    assert captured["enemy"] is enemy
    assert captured["tick"] == 10
    assert captured["char_obj_list"] is char_obj_list
    assert captured["skill_node"] is skill_node
    assert captured["dynamic_buff_dict"] is dynamic_buff
    assert captured["sim_instance"] is sim_instance
    runtime_context = captured["runtime_context"]
    assert runtime_context.sim_instance is sim_instance
    assert isinstance(runtime_context.buff_runtime_view, DefaultBuffRuntimeReadAdapter)
    assert runtime_context.buff_runtime_view is scheduled_event.buff_runtime_view
    assert runtime_context.dot_runtime_state.snapshot() == ()
    runtime_context.dispatch_port.publish_scheduled("scheduled")
    assert current_event_list == ["scheduled"]
    assert stale_event_list == ["stale"]


def test_scheduled_event_runtime_ports_rebind_read_view_for_each_runtime_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_active = object()
    second_active = object()
    first_state = _runtime_state_for_test(
        exist_buff_dict={"alpha": {"first": object()}, "enemy": {}},
        dynamic_buff={"alpha": [first_active], "enemy": []},
        loading_buff={"alpha": []},
    )
    second_state = _runtime_state_for_test(
        exist_buff_dict={"alpha": {"second": object()}, "enemy": {}},
        dynamic_buff={"alpha": [second_active], "enemy": []},
        loading_buff={"alpha": []},
    )
    first_data = SimpleNamespace(enemy=SimpleNamespace(), event_list=[], char_obj_list=[])
    second_data = SimpleNamespace(enemy=SimpleNamespace(), event_list=[], char_obj_list=[])
    first_stack = SimpleNamespace(marker="first-stack")
    second_stack = SimpleNamespace(marker="second-stack")
    first_sim = SimpleNamespace(marker="first-sim")
    second_sim = SimpleNamespace(marker="second-sim")
    command_ports = [object(), object()]
    captured_calls: list[dict[str, Any]] = []

    def _fake_create_runtime_command_port(**kwargs: Any) -> object:
        captured_calls.append(dict(kwargs))
        return command_ports[len(captured_calls) - 1]

    monkeypatch.setattr(
        scheduled_event_module.ScheduledEvent,
        "_ensure_handlers_registered",
        lambda self: None,
    )
    monkeypatch.setattr(
        scheduled_event_module,
        "create_runtime_command_port",
        _fake_create_runtime_command_port,
    )

    first_event = scheduled_event_module.ScheduledEvent(
        {"alpha": [first_active], "enemy": []},
        first_data,
        1,
        {"alpha": {"first": object()}, "enemy": {}},
        first_stack,
        loading_buff={"alpha": []},
        buff_runtime_state=first_state,
        sim_instance=cast(Any, first_sim),
    )
    second_event = scheduled_event_module.ScheduledEvent(
        {"alpha": [second_active], "enemy": []},
        second_data,
        2,
        {"alpha": {"second": object()}, "enemy": {}},
        second_stack,
        loading_buff={"alpha": []},
        buff_runtime_state=second_state,
        sim_instance=cast(Any, second_sim),
    )

    assert len(captured_calls) == 2
    first_call, second_call = captured_calls
    assert first_call["data"] is first_data
    assert first_call["action_stack"] is first_stack
    assert first_call["buff_runtime_state"] is first_state
    assert first_call["buff_runtime_view"] is first_event.buff_runtime_view
    assert first_call["sim_instance"] is first_sim
    assert second_call["data"] is second_data
    assert second_call["action_stack"] is second_stack
    assert second_call["buff_runtime_state"] is second_state
    assert second_call["buff_runtime_view"] is second_event.buff_runtime_view
    assert second_call["sim_instance"] is second_sim
    assert first_event.runtime_command_port is command_ports[0]
    assert second_event.runtime_command_port is command_ports[1]
    assert first_event.buff_runtime_view is not second_event.buff_runtime_view
    assert tuple(first_event.buff_runtime_view.get_active_buffs("alpha")) == (
        first_active,
    )
    assert tuple(second_event.buff_runtime_view.get_active_buffs("alpha")) == (
        second_active,
    )


def test_scheduled_event_runtime_port_factory_accepts_current_inputs_per_creation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_active = object()
    second_active = object()
    first_state = _runtime_state_for_test(
        exist_buff_dict={"alpha": {"first": object()}, "enemy": {}},
        dynamic_buff={"alpha": [first_active], "enemy": []},
        loading_buff={"alpha": []},
    )
    second_state = _runtime_state_for_test(
        exist_buff_dict={"alpha": {"second": object()}, "enemy": {}},
        dynamic_buff={"alpha": [second_active], "enemy": []},
        loading_buff={"alpha": []},
    )
    first_view = first_state.create_read_port()
    second_view = second_state.create_read_port()
    first_data = SimpleNamespace(enemy=SimpleNamespace(), event_list=[], char_obj_list=[])
    second_data = SimpleNamespace(enemy=SimpleNamespace(), event_list=[], char_obj_list=[])
    first_stack = SimpleNamespace(marker="first-stack")
    second_stack = SimpleNamespace(marker="second-stack")
    first_sim = SimpleNamespace(marker="first-sim")
    second_sim = SimpleNamespace(marker="second-sim")
    command_ports = [object(), object()]
    captured_calls: list[dict[str, Any]] = []

    def _fake_create_runtime_command_port(**kwargs: Any) -> object:
        captured_calls.append(dict(kwargs))
        return command_ports[len(captured_calls) - 1]

    monkeypatch.setattr(
        scheduled_event_module,
        "create_runtime_command_port",
        _fake_create_runtime_command_port,
    )

    factory = scheduled_event_module.ScheduledEventRuntimePortFactory()

    first_ports = factory.create(
        data=cast(Any, first_data),
        action_stack=cast(Any, first_stack),
        buff_runtime_state=first_state,
        buff_runtime_view=first_view,
        sim_instance=cast(Any, first_sim),
    )
    second_ports = factory.create(
        data=cast(Any, second_data),
        action_stack=cast(Any, second_stack),
        buff_runtime_state=second_state,
        buff_runtime_view=second_view,
        sim_instance=cast(Any, second_sim),
    )

    assert len(captured_calls) == 2
    first_call, second_call = captured_calls
    assert first_call["data"] is first_data
    assert first_call["action_stack"] is first_stack
    assert first_call["buff_runtime_state"] is first_state
    assert first_call["buff_runtime_view"] is first_view
    assert first_call["sim_instance"] is first_sim
    assert second_call["data"] is second_data
    assert second_call["action_stack"] is second_stack
    assert second_call["buff_runtime_state"] is second_state
    assert second_call["buff_runtime_view"] is second_view
    assert second_call["sim_instance"] is second_sim
    assert first_ports.runtime_command_port is command_ports[0]
    assert second_ports.runtime_command_port is command_ports[1]
    assert first_ports.buff_runtime_view is first_view
    assert second_ports.buff_runtime_view is second_view
    assert tuple(first_ports.buff_runtime_view.get_active_buffs("alpha")) == (
        first_active,
    )
    assert tuple(second_ports.buff_runtime_view.get_active_buffs("alpha")) == (
        second_active,
    )


def test_scheduled_event_runtime_port_factory_command_uses_rebound_schedule_queue(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    factory = scheduled_event_module.ScheduledEventRuntimePortFactory()
    first_dynamic_buff = {"alpha": [object()], "enemy": []}
    first_state = _runtime_state_for_test(
        exist_buff_dict={"alpha": {"first": object()}, "enemy": {}},
        dynamic_buff=first_dynamic_buff,
    )
    first_stale_event_list = ["first-stale"]
    first_data = SimpleNamespace(
        event_list=first_stale_event_list,
        char_obj_list=[],
        dynamic_buff=first_dynamic_buff,
    )
    first_sim = SimpleNamespace(
        schedule_data=first_data,
        listener_manager=SimpleNamespace(broadcast_event=lambda **kwargs: None),
    )
    factory.create(
        data=cast(Any, first_data),
        action_stack=cast(Any, SimpleNamespace(marker="first-stack")),
        buff_runtime_state=first_state,
        buff_runtime_view=first_state.create_read_port(),
        sim_instance=cast(Any, first_sim),
    )

    second_dynamic_buff = {"alpha": [object()], "enemy": []}
    second_state = _runtime_state_for_test(
        exist_buff_dict={"alpha": {"second": object()}, "enemy": {}},
        dynamic_buff=second_dynamic_buff,
    )
    second_stale_event_list = ["second-stale"]
    second_current_event_list: list[object] = []
    second_data = SimpleNamespace(
        event_list=second_stale_event_list,
        char_obj_list=[],
        dynamic_buff=second_dynamic_buff,
    )
    second_sim = SimpleNamespace(
        schedule_data=second_data,
        listener_manager=SimpleNamespace(broadcast_event=lambda **kwargs: None),
    )
    second_ports = factory.create(
        data=cast(Any, second_data),
        action_stack=cast(Any, SimpleNamespace(marker="second-stack")),
        buff_runtime_state=second_state,
        buff_runtime_view=second_state.create_read_port(),
        sim_instance=cast(Any, second_sim),
    )
    captured: dict[str, Any] = {}

    def _fake_update_anomaly(
        *,
        element_type,
        enemy,
        time_now,
        char_obj_list,
        sim_instance,
        skill_node,
        dynamic_buff_dict,
        runtime_context,
        **kwargs,
    ) -> None:
        captured["sim_instance"] = sim_instance
        captured["dynamic_buff_dict"] = dynamic_buff_dict
        captured["runtime_context"] = runtime_context

    monkeypatch.setattr(runtime_command_module, "run_update_anomaly", _fake_update_anomaly)

    second_data.event_list = second_current_event_list

    second_ports.runtime_command_port.update_anomaly(
        element_type=1,
        enemy=SimpleNamespace(dynamic=SimpleNamespace(dynamic_dot_list=[])),
        tick=10,
        skill_node=SimpleNamespace(skill_tag="1001_TEST"),
    )

    assert captured["sim_instance"] is second_sim
    assert captured["dynamic_buff_dict"] is second_dynamic_buff
    runtime_context = captured["runtime_context"]
    assert runtime_context.sim_instance is second_sim
    runtime_context.dispatch_port.publish_scheduled("scheduled")
    assert second_current_event_list == ["scheduled"]
    assert second_stale_event_list == ["second-stale"]
    assert first_stale_event_list == ["first-stale"]
