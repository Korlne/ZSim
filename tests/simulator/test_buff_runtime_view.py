from types import SimpleNamespace

import pytest

from zsim.sim_progress.ScheduledEvent.buff_runtime import (
    BuffRuntimeReadPort,
    LegacyBuffRuntimeReadAdapter,
    create_buff_runtime_read_port,
)
from zsim.sim_progress.ScheduledEvent.event_handlers.base import BaseEventHandler
from zsim.sim_progress.ScheduledEvent.event_handlers.context import EventContext


class _FakeRuntimeView(BuffRuntimeReadPort):
    def __init__(self, dynamic_buff, exist_buff_dict):
        self.dynamic_buff = dynamic_buff
        self.exist_buff_dict = exist_buff_dict
        self.dynamic_calls = 0
        self.exist_calls = 0

    def get_active_buffs(self, beneficiary: str):
        return tuple(self.dynamic_buff.get(beneficiary, []))

    def get_active_buff_view(self):
        return {beneficiary: tuple(buffs) for beneficiary, buffs in self.dynamic_buff.items()}

    def get_exist_buff_snapshot(self, beneficiary: str):
        return dict(self.exist_buff_dict.get(beneficiary, {}))

    def get_exist_buff_snapshot_view(self):
        return {
            beneficiary: dict(buff_dict)
            for beneficiary, buff_dict in self.exist_buff_dict.items()
        }

    def get_legacy_dynamic_buff_dict(self):
        self.dynamic_calls += 1
        return self.dynamic_buff

    def get_legacy_exist_buff_dict(self):
        self.exist_calls += 1
        return self.exist_buff_dict


class _AccessorProbeHandler(BaseEventHandler):
    def __init__(self):
        super().__init__("probe")

    def can_handle(self, event):
        return True

    def handle(self, event, context):
        raise NotImplementedError

    def read_dynamic_buff(self, context):
        return self._get_context_dynamic_buff(context)

    def read_exist_buff_dict(self, context):
        return self._get_context_exist_buff_dict(context)


def _build_context(runtime_view: BuffRuntimeReadPort) -> EventContext:
    return EventContext(
        data=SimpleNamespace(),
        tick=10,
        enemy=SimpleNamespace(),
        buff_runtime_view=runtime_view,
        action_stack=SimpleNamespace(),
        sim_instance=SimpleNamespace(),
    )


def test_create_buff_runtime_read_port_exposes_read_only_views_for_active_and_snapshot_buffs():
    alpha_buff = object()
    enemy_buff = object()
    dynamic_buff = {
        "alpha": [alpha_buff],
        "enemy": [enemy_buff],
    }
    exist_buff_dict = {
        "alpha": {"alpha-buff": alpha_buff},
        "enemy": {"enemy-buff": enemy_buff},
    }

    runtime_view = create_buff_runtime_read_port(
        dynamic_buff=dynamic_buff,
        exist_buff_dict=exist_buff_dict,
    )

    assert isinstance(runtime_view, LegacyBuffRuntimeReadAdapter)
    assert tuple(runtime_view.get_active_buffs("alpha")) == (alpha_buff,)
    assert tuple(runtime_view.get_active_buff_view()["enemy"]) == (enemy_buff,)
    assert dict(runtime_view.get_exist_buff_snapshot("alpha")) == {"alpha-buff": alpha_buff}
    assert dict(runtime_view.get_exist_buff_snapshot_view()["enemy"]) == {
        "enemy-buff": enemy_buff
    }

    with pytest.raises(TypeError):
        runtime_view.get_active_buff_view()["alpha"] = ()

    with pytest.raises(TypeError):
        runtime_view.get_exist_buff_snapshot_view()["alpha"]["extra"] = object()


def test_event_context_compatibility_getters_delegate_to_runtime_view():
    dynamic_buff = {"alpha": [object()]}
    exist_buff_dict = {"alpha": {"buff": object()}}
    runtime_view = _FakeRuntimeView(dynamic_buff, exist_buff_dict)
    context = _build_context(runtime_view)

    assert context.get_buff_runtime_view() is runtime_view
    assert context.get_dynamic_buff() is dynamic_buff
    assert context.get_exist_buff_dict() is exist_buff_dict
    assert runtime_view.dynamic_calls == 1
    assert runtime_view.exist_calls == 1


def test_base_event_handler_compatibility_accessors_delegate_via_runtime_view():
    dynamic_buff = {"enemy": [object()]}
    exist_buff_dict = {"enemy": {"buff": object()}}
    runtime_view = _FakeRuntimeView(dynamic_buff, exist_buff_dict)
    context = _build_context(runtime_view)
    handler = _AccessorProbeHandler()

    assert handler.read_dynamic_buff(context) is dynamic_buff
    assert handler.read_exist_buff_dict(context) is exist_buff_dict
    assert runtime_view.dynamic_calls == 1
    assert runtime_view.exist_calls == 1
