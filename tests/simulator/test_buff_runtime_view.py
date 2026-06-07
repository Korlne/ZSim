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
        self.active_buff_calls = 0
        self.active_view_calls = 0
        self.snapshot_calls = 0
        self.snapshot_view_calls = 0
        self.dynamic_calls = 0
        self.exist_calls = 0

    def get_active_buffs(self, beneficiary: str):
        self.active_buff_calls += 1
        return tuple(self.dynamic_buff.get(beneficiary, []))

    def get_active_buff_view(self):
        self.active_view_calls += 1
        return {beneficiary: tuple(buffs) for beneficiary, buffs in self.dynamic_buff.items()}

    def get_exist_buff_snapshot(self, beneficiary: str):
        self.snapshot_calls += 1
        return dict(self.exist_buff_dict.get(beneficiary, {}))

    def get_exist_buff_snapshot_view(self):
        self.snapshot_view_calls += 1
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

    def read_legacy_dynamic_buff(self, context):
        return self._get_context_legacy_dynamic_buff(context)

    def read_legacy_exist_buff_dict(self, context):
        return self._get_context_legacy_exist_buff_dict(context)

    def read_runtime_active_buffs(self, context, beneficiary):
        return self._get_context_runtime_active_buffs(context, beneficiary)

    def read_runtime_active_buff_view(self, context):
        return self._get_context_runtime_active_buff_view(context)

    def read_runtime_exist_buff_snapshot(self, context, beneficiary):
        return self._get_context_runtime_exist_buff_snapshot(context, beneficiary)

    def read_runtime_exist_buff_snapshot_view(self, context):
        return self._get_context_runtime_exist_buff_snapshot_view(context)


def _build_context(runtime_view: BuffRuntimeReadPort) -> EventContext:
    return EventContext(
        data=SimpleNamespace(),
        tick=10,
        enemy=SimpleNamespace(),
        buff_runtime_view=runtime_view,
        runtime_command_port=SimpleNamespace(),
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
    assert context.get_legacy_dynamic_buff_dict() is dynamic_buff
    assert context.get_legacy_exist_buff_dict() is exist_buff_dict
    assert runtime_view.dynamic_calls == 1
    assert runtime_view.exist_calls == 1

    assert context.get_dynamic_buff() is dynamic_buff
    assert context.get_exist_buff_dict() is exist_buff_dict
    assert runtime_view.dynamic_calls == 2
    assert runtime_view.exist_calls == 2


def test_event_context_runtime_read_accessors_delegate_without_legacy_container_access():
    alpha_buff = object()
    dynamic_buff = {"alpha": [alpha_buff]}
    exist_buff_dict = {"alpha": {"buff": alpha_buff}}
    runtime_view = _FakeRuntimeView(dynamic_buff, exist_buff_dict)
    context = _build_context(runtime_view)

    assert context.get_runtime_active_buffs("alpha") == (alpha_buff,)
    assert context.get_runtime_active_buff_view()["alpha"] == (alpha_buff,)
    assert context.get_runtime_exist_buff_snapshot("alpha") == {"buff": alpha_buff}
    assert context.get_runtime_exist_buff_snapshot_view()["alpha"] == {"buff": alpha_buff}
    assert runtime_view.active_buff_calls == 1
    assert runtime_view.active_view_calls == 1
    assert runtime_view.snapshot_calls == 1
    assert runtime_view.snapshot_view_calls == 1
    assert runtime_view.dynamic_calls == 0
    assert runtime_view.exist_calls == 0


def test_base_event_handler_compatibility_accessors_delegate_via_runtime_view():
    dynamic_buff = {"enemy": [object()]}
    exist_buff_dict = {"enemy": {"buff": object()}}
    runtime_view = _FakeRuntimeView(dynamic_buff, exist_buff_dict)
    context = _build_context(runtime_view)
    handler = _AccessorProbeHandler()

    assert handler.read_legacy_dynamic_buff(context) is dynamic_buff
    assert handler.read_legacy_exist_buff_dict(context) is exist_buff_dict
    assert runtime_view.dynamic_calls == 1
    assert runtime_view.exist_calls == 1

    assert handler.read_dynamic_buff(context) is dynamic_buff
    assert handler.read_exist_buff_dict(context) is exist_buff_dict
    assert runtime_view.dynamic_calls == 2
    assert runtime_view.exist_calls == 2


def test_base_event_handler_runtime_read_accessors_delegate_without_legacy_access():
    buff = object()
    dynamic_buff = {"enemy": [buff]}
    exist_buff_dict = {"enemy": {"buff": buff}}
    runtime_view = _FakeRuntimeView(dynamic_buff, exist_buff_dict)
    context = _build_context(runtime_view)
    handler = _AccessorProbeHandler()

    assert handler.read_runtime_active_buffs(context, "enemy") == (buff,)
    assert handler.read_runtime_active_buff_view(context)["enemy"] == (buff,)
    assert handler.read_runtime_exist_buff_snapshot(context, "enemy") == {"buff": buff}
    assert handler.read_runtime_exist_buff_snapshot_view(context)["enemy"] == {"buff": buff}
    assert runtime_view.active_buff_calls == 1
    assert runtime_view.active_view_calls == 1
    assert runtime_view.snapshot_calls == 1
    assert runtime_view.snapshot_view_calls == 1
    assert runtime_view.dynamic_calls == 0
    assert runtime_view.exist_calls == 0
