from types import SimpleNamespace
from typing import Any, cast

import pytest

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
