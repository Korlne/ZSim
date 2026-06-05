from __future__ import annotations

from types import SimpleNamespace

import pytest

from zsim.sim_progress.ScheduledEvent.buff_runtime import BuffRuntimeReadPort
from zsim.sim_progress.ScheduledEvent.event_handlers.context import EventContext
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers import skill as skill_module
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers.skill import SkillEventHandler


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


def _build_skill_event_context(runtime_view: BuffRuntimeReadPort) -> tuple[EventContext, SimpleNamespace]:
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
    sim_instance = SimpleNamespace(
        tick=10,
        char_data=SimpleNamespace(char_obj_list=[character]),
        listener_manager=SimpleNamespace(broadcast_event=lambda **kwargs: None),
    )
    context = EventContext(
        data=schedule_data,
        tick=10,
        enemy=enemy,
        buff_runtime_view=runtime_view,
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


def test_skill_handler_reads_runtime_view_and_limits_legacy_access_to_write_boundary(
    monkeypatch: pytest.MonkeyPatch,
):
    legacy_dynamic_buff = {"alpha": [object()], "enemy": [object()]}
    legacy_exist_buff_dict = {"alpha": {"alpha-buff": object()}, "enemy": {}}
    runtime_view = _RuntimeViewProbe(
        legacy_dynamic_buff,
        legacy_exist_buff_dict,
        allow_legacy=True,
    )
    context, _ = _build_skill_event_context(runtime_view)
    captured: dict[str, object] = {}

    class _FakeCalculator:
        def __init__(self, *, dynamic_buff, **kwargs) -> None:
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
        captured["anomaly_dynamic_buff"] = dynamic_buff_dict

    def _fake_schedule_settle(
        tick,
        exist_buff_dict,
        enemy,
        dynamic_buff,
        action_stack,
        *,
        skill_node,
        sim_instance,
        **kwargs,
    ) -> None:
        captured["settle_exist_buff_dict"] = exist_buff_dict
        captured["settle_dynamic_buff"] = dynamic_buff

    monkeypatch.setattr(skill_module, "Calculator", _FakeCalculator)
    monkeypatch.setattr(skill_module, "update_anomaly", _fake_update_anomaly)
    monkeypatch.setattr(skill_module, "ScheduleBuffSettle", _fake_schedule_settle)
    monkeypatch.setattr(skill_module, "ProcessHitUpdateDots", lambda *args, **kwargs: None)
    monkeypatch.setattr(skill_module, "ProcessFreezLikeDots", lambda *args, **kwargs: None)
    monkeypatch.setattr(skill_module.Report, "report_dmg_result", lambda **kwargs: None)

    handler = SkillEventHandler()
    monkeypatch.setattr(handler, "_validate_event", lambda *args, **kwargs: None)
    monkeypatch.setattr(handler, "_get_execute_tick", lambda *args, **kwargs: 10)
    event = _build_skill_node()

    handler.handle(event, context)

    assert captured["calculator_dynamic_buff"] is runtime_view.active_buff_view
    assert captured["anomaly_dynamic_buff"] is runtime_view.active_buff_view
    assert captured["settle_exist_buff_dict"] is legacy_exist_buff_dict
    assert captured["settle_dynamic_buff"] is legacy_dynamic_buff
    assert runtime_view.active_view_calls == 1
    assert runtime_view.legacy_dynamic_calls == 1
    assert runtime_view.legacy_exist_calls == 1
