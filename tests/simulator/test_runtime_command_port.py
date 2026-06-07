from types import SimpleNamespace
from typing import Any, cast

import pytest

import zsim.sim_progress.ScheduledEvent as scheduled_event_module
from zsim.sim_progress.ScheduledEvent.runtime_command import (
    LegacyRuntimeCommandAdapter,
    create_runtime_command_port,
)
from zsim.sim_progress.ScheduledEvent import runtime_command as runtime_command_module


def test_runtime_command_port_preserves_legacy_container_identity_for_same_tick_writes(
    monkeypatch: pytest.MonkeyPatch,
):
    stale_event_list = ["stale"]
    current_event_list: list[object] = []
    char_obj_list = [SimpleNamespace(NAME="alpha")]
    dynamic_buff = {"alpha": [object()], "enemy": [object()]}
    exist_buff_dict = {"alpha": {"buff": object()}, "enemy": {}}
    action_stack = SimpleNamespace()
    sim_instance = cast(Any, SimpleNamespace())
    schedule_data = SimpleNamespace(
        event_list=stale_event_list,
        char_obj_list=char_obj_list,
        dynamic_buff=dynamic_buff,
    )
    port = create_runtime_command_port(
        data=schedule_data,
        exist_buff_dict=exist_buff_dict,
        action_stack=action_stack,
        sim_instance=sim_instance,
    )
    enemy = SimpleNamespace()
    skill_node = SimpleNamespace(skill_tag="1001_TEST")
    captured: dict[str, Any] = {}

    def _fake_update_anomaly(
        element_type,
        enemy,
        tick,
        event_list,
        char_obj_list,
        *,
        skill_node,
        dynamic_buff_dict,
        sim_instance,
        **kwargs,
    ) -> None:
        captured["element_type"] = element_type
        captured["enemy"] = enemy
        captured["tick"] = tick
        captured["event_list"] = event_list
        captured["char_obj_list"] = char_obj_list
        captured["skill_node"] = skill_node
        captured["dynamic_buff_dict"] = dynamic_buff_dict
        captured["sim_instance"] = sim_instance

    def _fake_schedule_buff_settle(
        tick,
        exist_buff_dict_arg,
        enemy,
        dynamic_buff_arg,
        action_stack_arg,
        *,
        sim_instance,
        **kwargs,
    ) -> None:
        captured["settle_tick"] = tick
        captured["settle_exist_buff_dict"] = exist_buff_dict_arg
        captured["settle_enemy"] = enemy
        captured["settle_dynamic_buff"] = dynamic_buff_arg
        captured["settle_action_stack"] = action_stack_arg
        captured["settle_sim_instance"] = sim_instance
        captured["settle_skill_node"] = kwargs.get("skill_node")
        captured["settle_kwargs"] = kwargs

    monkeypatch.setattr(runtime_command_module, "legacy_update_anomaly", _fake_update_anomaly)
    monkeypatch.setattr(
        runtime_command_module,
        "legacy_schedule_buff_settle",
        _fake_schedule_buff_settle,
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
    assert captured["event_list"] is current_event_list
    assert captured["char_obj_list"] is char_obj_list
    assert captured["skill_node"] is skill_node
    assert captured["dynamic_buff_dict"] is dynamic_buff
    assert captured["sim_instance"] is sim_instance
    assert captured["settle_tick"] == 10
    assert captured["settle_exist_buff_dict"] is exist_buff_dict
    assert captured["settle_enemy"] is enemy
    assert captured["settle_dynamic_buff"] is dynamic_buff
    assert captured["settle_action_stack"] is action_stack
    assert captured["settle_sim_instance"] is sim_instance
    assert captured["settle_skill_node"] is skill_node
    assert "anomaly_bar" not in captured["settle_kwargs"]


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
