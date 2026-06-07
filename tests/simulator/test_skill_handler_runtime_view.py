from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest

from zsim.sim_progress.ScheduledEvent import runtime_command as runtime_command_module
from zsim.sim_progress.ScheduledEvent.buff_runtime import BuffRuntimeReadPort
from zsim.sim_progress.ScheduledEvent.event_handlers.context import EventContext
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers import skill as skill_module
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers.skill import SkillEventHandler
from zsim.sim_progress.ScheduledEvent.runtime_command import create_runtime_command_port


class _RuntimeViewProbe(BuffRuntimeReadPort):
    def __init__(self, dynamic_buff, exist_buff_dict, *, allow_legacy: bool) -> None:
        self.active_buff_view = {
            beneficiary: tuple(buffs) for beneficiary, buffs in dynamic_buff.items()
        }
        self.legacy_dynamic_buff = dynamic_buff
        self.legacy_exist_buff_dict = exist_buff_dict
        self.allow_legacy = allow_legacy
        self.active_view_calls = 0
        self.legacy_dynamic_calls = 0
        self.legacy_exist_calls = 0

    def get_active_buffs(self, beneficiary: str):
        return self.active_buff_view.get(beneficiary, ())

    def get_active_buff_view(self):
        self.active_view_calls += 1
        return self.active_buff_view

    def get_exist_buff_snapshot(self, beneficiary: str):
        return {}

    def get_exist_buff_snapshot_view(self):
        return {}

    def get_legacy_dynamic_buff_dict(self):
        self.legacy_dynamic_calls += 1
        if not self.allow_legacy:
            raise AssertionError("legacy dynamic buff access should not happen on read-only path")
        return self.legacy_dynamic_buff

    def get_legacy_exist_buff_dict(self):
        self.legacy_exist_calls += 1
        if not self.allow_legacy:
            raise AssertionError("legacy exist buff access should not happen on read-only path")
        return self.legacy_exist_buff_dict


class _RuntimeCommandProbe:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def update_anomaly(self, **kwargs) -> None:
        self.calls.append(("update_anomaly", kwargs))

    def settle_buffs(self, **kwargs) -> None:
        self.calls.append(("settle_buffs", kwargs))


def _build_skill_event_context(
    runtime_view: BuffRuntimeReadPort,
    runtime_command_port: _RuntimeCommandProbe,
) -> tuple[EventContext, SimpleNamespace]:
    character = SimpleNamespace(NAME="alpha")
    enemy = SimpleNamespace(
        dynamic=SimpleNamespace(
            dynamic_dot_list=[],
            get_status=lambda: {},
        ),
        hit_received=lambda *args, **kwargs: None,
    )
    schedule_data = SimpleNamespace(
        char_obj_list=[character],
        event_list=[],
    )
    sim_instance = cast(
        Any,
        SimpleNamespace(
            tick=10,
            char_data=SimpleNamespace(char_obj_list=[character]),
            listener_manager=SimpleNamespace(broadcast_event=lambda **kwargs: None),
        ),
    )
    context = EventContext(
        data=schedule_data,
        tick=10,
        enemy=enemy,
        buff_runtime_view=runtime_view,
        runtime_command_port=cast(Any, runtime_command_port),
        action_stack=SimpleNamespace(),
        sim_instance=sim_instance,
    )
    return context, character


def _build_skill_node() -> SimpleNamespace:
    skill = SimpleNamespace(
        char_name="alpha",
        anomaly_update_rule=-1,
        follow_by=False,
        heavy_attack=False,
    )
    return SimpleNamespace(
        preload_tick=10,
        skill=skill,
        skill_tag="1001_TEST",
        char_name="alpha",
        active_generation=False,
        hit_times=1,
        element_type=1,
        UUID="skill-node",
        loading_mission=None,
        mission_node=SimpleNamespace(active_generation=False),
    )


def test_skill_handler_reads_runtime_view_and_routes_same_tick_writes_through_runtime_command(
    monkeypatch: pytest.MonkeyPatch,
):
    legacy_dynamic_buff = {"alpha": [object()], "enemy": [object()]}
    legacy_exist_buff_dict = {"alpha": {"alpha-buff": object()}, "enemy": {}}
    runtime_view = _RuntimeViewProbe(
        legacy_dynamic_buff,
        legacy_exist_buff_dict,
        allow_legacy=False,
    )
    runtime_command_port = _RuntimeCommandProbe()
    context, enemy_character = _build_skill_event_context(runtime_view, runtime_command_port)
    call_order: list[str] = []
    captured: dict[str, object] = {}

    class _FakeCalculator:
        def __init__(self, *, dynamic_buff, **kwargs) -> None:
            call_order.append("calculate_damage")
            captured["calculator_dynamic_buff"] = dynamic_buff
            self.regular_multipliers = SimpleNamespace(crit_rate=0.1, crit_dmg=0.5)

        def cal_snapshot(self):
            return (1, 2.5, [1, 2, 3])

        def cal_stun(self):
            return 3.5

        def cal_dmg_expect(self):
            return 4.5

        def cal_dmg_crit(self):
            return 5.5

    original_update_anomaly = runtime_command_port.update_anomaly
    original_settle_buffs = runtime_command_port.settle_buffs

    def _record_update_anomaly(**kwargs) -> None:
        call_order.append("update_anomaly")
        original_update_anomaly(**kwargs)

    def _record_settle_buffs(**kwargs) -> None:
        call_order.append("settle_buffs")
        original_settle_buffs(**kwargs)

    monkeypatch.setattr(skill_module, "Calculator", _FakeCalculator)
    monkeypatch.setattr(handler := SkillEventHandler(), "_update_damage_effects", lambda *args, **kwargs: call_order.append("update_damage_effects"))
    monkeypatch.setattr(skill_module.Report, "report_dmg_result", lambda **kwargs: None)

    monkeypatch.setattr(handler, "_validate_event", lambda *args, **kwargs: None)
    monkeypatch.setattr(handler, "_get_execute_tick", lambda *args, **kwargs: 10)
    monkeypatch.setattr(
        handler,
        "_find_character",
        lambda char_name, char_obj_list: enemy_character,
    )
    monkeypatch.setattr(
        runtime_command_port,
        "update_anomaly",
        _record_update_anomaly,
    )
    monkeypatch.setattr(
        runtime_command_port,
        "settle_buffs",
        _record_settle_buffs,
    )

    event = _build_skill_node()
    handler.handle(event, context)

    assert captured["calculator_dynamic_buff"] is runtime_view.active_buff_view
    assert runtime_view.active_view_calls == 1
    assert runtime_view.legacy_dynamic_calls == 0
    assert runtime_view.legacy_exist_calls == 0

    assert call_order[:3] == ["calculate_damage", "update_anomaly", "settle_buffs"]
    assert "update_damage_effects" in call_order

    assert len(runtime_command_port.calls) == 2
    anomaly_call_name, anomaly_call_kwargs = runtime_command_port.calls[0]
    settle_call_name, settle_call_kwargs = runtime_command_port.calls[1]
    assert anomaly_call_name == "update_anomaly"
    assert anomaly_call_kwargs["element_type"] == event.element_type
    assert anomaly_call_kwargs["enemy"] is context.enemy
    assert anomaly_call_kwargs["tick"] == context.tick
    assert anomaly_call_kwargs["skill_node"] is event
    assert settle_call_name == "settle_buffs"
    assert settle_call_kwargs["tick"] == context.tick
    assert settle_call_kwargs["enemy"] is context.enemy
    assert settle_call_kwargs["skill_node"] is event


def test_skill_handler_runtime_command_adapter_preserves_legacy_container_identity(
    monkeypatch: pytest.MonkeyPatch,
):
    stale_event_list = ["stale"]
    current_event_list: list[object] = []
    legacy_dynamic_buff = {"alpha": [object()], "enemy": [object()]}
    legacy_exist_buff_dict = {"alpha": {"alpha-buff": object()}, "enemy": {}}
    runtime_view = _RuntimeViewProbe(
        legacy_dynamic_buff,
        legacy_exist_buff_dict,
        allow_legacy=False,
    )
    action_stack = SimpleNamespace()
    character = SimpleNamespace(NAME="alpha")
    enemy = SimpleNamespace(
        dynamic=SimpleNamespace(
            dynamic_dot_list=[],
            get_status=lambda: {},
        ),
        hit_received=lambda *args, **kwargs: None,
    )
    schedule_data = SimpleNamespace(
        char_obj_list=[character],
        event_list=stale_event_list,
        dynamic_buff=legacy_dynamic_buff,
    )
    sim_instance = cast(
        Any,
        SimpleNamespace(
            tick=10,
            char_data=SimpleNamespace(char_obj_list=[character]),
            listener_manager=SimpleNamespace(broadcast_event=lambda **kwargs: None),
        ),
    )
    runtime_command_port = create_runtime_command_port(
        data=schedule_data,
        exist_buff_dict=legacy_exist_buff_dict,
        action_stack=action_stack,
        sim_instance=sim_instance,
        buff_runtime_view=runtime_view,
    )
    schedule_data.event_list = current_event_list
    context = EventContext(
        data=schedule_data,
        tick=10,
        enemy=enemy,
        buff_runtime_view=runtime_view,
        runtime_command_port=runtime_command_port,
        action_stack=action_stack,
        sim_instance=sim_instance,
    )
    call_order: list[str] = []
    captured: dict[str, object] = {}

    class _FakeCalculator:
        def __init__(self, *, dynamic_buff, **kwargs) -> None:
            call_order.append("calculate_damage")
            captured["calculator_dynamic_buff"] = dynamic_buff
            self.regular_multipliers = SimpleNamespace(crit_rate=0.2, crit_dmg=0.6)

        def cal_snapshot(self):
            return (1, 2.5, [1, 2, 3])

        def cal_stun(self):
            return 3.5

        def cal_dmg_expect(self):
            return 4.5

        def cal_dmg_crit(self):
            return 5.5

    def _fake_update_anomaly(
        element_type,
        target_enemy,
        tick,
        event_list,
        char_obj_list,
        *,
        skill_node,
        dynamic_buff_dict,
        sim_instance,
        **kwargs,
    ) -> None:
        call_order.append("update_anomaly")
        captured["update_element_type"] = element_type
        captured["update_enemy"] = target_enemy
        captured["update_tick"] = tick
        captured["update_event_list"] = event_list
        captured["update_char_obj_list"] = char_obj_list
        captured["update_skill_node"] = skill_node
        captured["update_dynamic_buff_dict"] = dynamic_buff_dict
        captured["update_sim_instance"] = sim_instance

    def _fake_schedule_buff_settle(
        tick,
        exist_buff_dict_arg,
        target_enemy,
        dynamic_buff_arg,
        action_stack_arg,
        *,
        sim_instance,
        **kwargs,
    ) -> None:
        call_order.append("settle_buffs")
        captured["settle_tick"] = tick
        captured["settle_exist_buff_dict"] = exist_buff_dict_arg
        captured["settle_enemy"] = target_enemy
        captured["settle_dynamic_buff"] = dynamic_buff_arg
        captured["settle_action_stack"] = action_stack_arg
        captured["settle_sim_instance"] = sim_instance
        captured["settle_skill_node"] = kwargs.get("skill_node")

    monkeypatch.setattr(skill_module, "Calculator", _FakeCalculator)
    monkeypatch.setattr(skill_module.Report, "report_dmg_result", lambda **kwargs: None)
    monkeypatch.setattr(
        runtime_command_module,
        "legacy_update_anomaly",
        _fake_update_anomaly,
    )
    monkeypatch.setattr(
        runtime_command_module,
        "legacy_schedule_buff_settle",
        _fake_schedule_buff_settle,
    )

    handler = SkillEventHandler()
    monkeypatch.setattr(handler, "_validate_event", lambda *args, **kwargs: None)
    monkeypatch.setattr(handler, "_get_execute_tick", lambda *args, **kwargs: 10)
    monkeypatch.setattr(
        handler,
        "_find_character",
        lambda char_name, char_obj_list: character,
    )
    monkeypatch.setattr(
        handler,
        "_update_damage_effects",
        lambda *args, **kwargs: call_order.append("update_damage_effects"),
    )

    event = _build_skill_node()
    handler.handle(event, context)

    assert captured["calculator_dynamic_buff"] is runtime_view.active_buff_view
    assert runtime_view.active_view_calls == 1
    assert runtime_view.legacy_dynamic_calls == 0
    assert runtime_view.legacy_exist_calls == 0

    assert call_order[:3] == ["calculate_damage", "update_anomaly", "settle_buffs"]
    assert "update_damage_effects" in call_order

    assert captured["update_element_type"] == event.element_type
    assert captured["update_enemy"] is enemy
    assert captured["update_tick"] == context.tick
    assert captured["update_event_list"] is current_event_list
    assert captured["update_char_obj_list"] is schedule_data.char_obj_list
    assert captured["update_skill_node"] is event
    assert captured["update_dynamic_buff_dict"] is legacy_dynamic_buff
    assert captured["update_sim_instance"] is sim_instance

    assert captured["settle_tick"] == context.tick
    assert captured["settle_exist_buff_dict"] is legacy_exist_buff_dict
    assert captured["settle_enemy"] is enemy
    assert captured["settle_dynamic_buff"] is legacy_dynamic_buff
    assert captured["settle_action_stack"] is action_stack
    assert captured["settle_sim_instance"] is sim_instance
    assert captured["settle_skill_node"] is event
