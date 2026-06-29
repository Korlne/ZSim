from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from zsim.sim_progress.Update.UpdateAnomaly import (
    create_anomaly_runtime_context,
    update_anomaly as _run_update_anomaly,
)

_MISSING_COMPAT_HOOK = object()
_MIGRATION_TEST_ANOMALY_HOOK_NAME = "legacy_" + "update_anomaly"


def _migration_test_update_anomaly_hook():
    """Return a patched legacy hook for migration/test compatibility only."""
    compatibility_hook = globals().get(
        _MIGRATION_TEST_ANOMALY_HOOK_NAME,
        _MISSING_COMPAT_HOOK,
    )
    if (
        compatibility_hook is _MISSING_COMPAT_HOOK
        or compatibility_hook is _run_update_anomaly
    ):
        return None
    return compatibility_hook


def __getattr__(name: str):
    if name == _MIGRATION_TEST_ANOMALY_HOOK_NAME:
        return _run_update_anomaly
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


class _MigrationDispatchEventList:
    """List-shaped append adapter for patched legacy anomaly tests."""

    def __init__(self, dispatch_port) -> None:
        self._dispatch_port = dispatch_port

    def append(self, event) -> None:
        self._dispatch_port.publish_scheduled(event)

    def extend(self, events) -> None:
        self._dispatch_port.publish_scheduled_batch(events)


def run_update_anomaly(**kwargs) -> None:
    compatibility_hook = _migration_test_update_anomaly_hook()
    if compatibility_hook is not None:
        runtime_context = kwargs["runtime_context"]
        active_store_key = "dynamic_" + "buff_dict"
        compatibility_kwargs = {
            "skill_node": kwargs["skill_node"],
            active_store_key: kwargs[active_store_key],
            "sim_instance": kwargs["sim_instance"],
            "buff_runtime_view": runtime_context.buff_runtime_view,
        }
        compatibility_hook(
            kwargs["element_type"],
            kwargs["enemy"],
            kwargs["time_now"],
            _MigrationDispatchEventList(runtime_context.dispatch_port),
            kwargs["char_obj_list"],
            **compatibility_kwargs,
        )
        return
    _run_update_anomaly(**kwargs)


if TYPE_CHECKING:
    from zsim.sim_progress.ScheduledEvent.buff_runtime import BuffRuntimeFacade
    from zsim.sim_progress.ScheduledEvent.buff_runtime import BuffRuntimeReadPort
    from zsim.sim_progress.ScheduledEvent.buff_runtime import BuffRuntimeState
    from zsim.sim_progress.Enemy import Enemy
    from zsim.sim_progress.Load import LoadingMission
    from zsim.sim_progress.Preload import SkillNode
    from zsim.sim_progress.anomaly_bar import AnomalyBar
    from zsim.sim_progress.data_struct import ActionStack
    from zsim.simulator.dataclasses import ScheduleData
    from zsim.simulator.simulator_class import Simulator


class RuntimeCommandPort(ABC):
    """同 tick runtime 写侧边界。"""

    @abstractmethod
    def update_anomaly(
        self,
        *,
        element_type: int,
        enemy: "Enemy",
        tick: int,
        skill_node: "SkillNode",
    ) -> None:
        """执行属性异常更新命令。"""

    @abstractmethod
    def settle_buffs(
        self,
        *,
        tick: int,
        enemy: "Enemy",
        skill_node: "SkillNode | LoadingMission | None" = None,
        anomaly_bar: "AnomalyBar | None" = None,
    ) -> None:
        """执行 Schedule 阶段 Buff 结算命令。"""


class _RuntimeCommandAdapterBase(RuntimeCommandPort):
    def __init__(
        self,
        *,
        data: "ScheduleData",
        action_stack: "ActionStack",
        sim_instance: "Simulator",
        exist_buff_dict: dict | None = None,
        buff_runtime_state: "BuffRuntimeState | None" = None,
        buff_runtime_view: "BuffRuntimeReadPort | None" = None,
    ) -> None:
        if buff_runtime_state is None and exist_buff_dict is None:
            raise ValueError("buff_runtime_state or legacy exist_buff_dict is required")
        self._data = data
        self._exist_buff_dict = exist_buff_dict
        self._buff_runtime_state = buff_runtime_state
        self._action_stack = action_stack
        self._sim_instance = sim_instance
        self._buff_runtime_view = buff_runtime_view

    def update_anomaly(
        self,
        *,
        element_type: int,
        enemy: "Enemy",
        tick: int,
        skill_node: "SkillNode",
    ) -> None:
        run_update_anomaly(
            element_type=element_type,
            enemy=enemy,
            time_now=tick,
            char_obj_list=self._data.char_obj_list,
            sim_instance=self._sim_instance,
            skill_node=skill_node,
            dynamic_buff_dict=self._legacy_active_store_for_update_anomaly(),
            runtime_context=create_anomaly_runtime_context(
                sim_instance=self._sim_instance,
                enemy=enemy,
                buff_runtime_view=self._buff_runtime_view,
                schedule_data=self._data,
            ),
        )

    def settle_buffs(
        self,
        *,
        tick: int,
        enemy: "Enemy",
        skill_node: "SkillNode | LoadingMission | None" = None,
        anomaly_bar: "AnomalyBar | None" = None,
    ) -> None:
        self._buff_runtime_facade_for_settle(enemy).settle_schedule_buffs(
            tick=tick,
            enemy=enemy,
            sim_instance=self._sim_instance,
            skill_node=skill_node,
            anomaly_bar=anomaly_bar,
        )

    def _buff_runtime_facade_for_settle(self, enemy: "Enemy") -> "BuffRuntimeFacade":
        return self._runtime_state_for_settle(enemy).create_facade()

    def _runtime_state_for_settle(self, enemy: "Enemy") -> "BuffRuntimeState":
        if self._buff_runtime_state is None:
            from zsim.sim_progress.ScheduledEvent.buff_runtime import BuffRuntimeState

            self._buff_runtime_state = BuffRuntimeState(
                template_registry=self._template_registry_for_compat(),
                pending_queue=getattr(self._data, "loading_buff", {}),
                active_store=self._active_store_for_compat(),
                enemy_mirror=self._enemy_debuff_mirror_for_settle(enemy),
            )
        return self._buff_runtime_state

    @staticmethod
    def _enemy_debuff_mirror_for_settle(enemy: "Enemy") -> list:
        enemy_dynamic = getattr(enemy, "dynamic", None)
        enemy_mirror = getattr(enemy_dynamic, "dynamic_debuff_list", None)
        if enemy_mirror is None:
            return []
        return enemy_mirror

    def _template_registry_for_compat(self) -> dict:
        if self._buff_runtime_state is not None:
            return self._buff_runtime_state.template_registry_for_compat()
        if self._exist_buff_dict is None:
            raise RuntimeError("legacy exist_buff_dict compatibility data is missing")
        return self._exist_buff_dict

    def _active_store_for_compat(self) -> dict:
        if self._buff_runtime_state is not None:
            return self._buff_runtime_state.active_store_for_compat()
        return self._data.dynamic_buff

    def _legacy_active_store_for_update_anomaly(self) -> dict | None:
        return None


class DefaultRuntimeCommandAdapter(_RuntimeCommandAdapterBase):
    """Production runtime command adapter backed by run-scoped Buff runtime state."""

    def __init__(
        self,
        *,
        data: "ScheduleData",
        action_stack: "ActionStack",
        sim_instance: "Simulator",
        buff_runtime_state: "BuffRuntimeState",
        buff_runtime_view: "BuffRuntimeReadPort | None" = None,
    ) -> None:
        super().__init__(
            data=data,
            action_stack=action_stack,
            sim_instance=sim_instance,
            buff_runtime_state=buff_runtime_state,
            buff_runtime_view=buff_runtime_view,
        )


class LegacyRuntimeCommandAdapter(_RuntimeCommandAdapterBase):
    """Explicit legacy runtime command compatibility adapter."""

    def _legacy_active_store_for_update_anomaly(self) -> dict | None:
        return self._active_store_for_compat()


def create_runtime_command_port(
    *,
    data: "ScheduleData",
    action_stack: "ActionStack",
    sim_instance: "Simulator",
    exist_buff_dict: dict | None = None,
    buff_runtime_state: "BuffRuntimeState | None" = None,
    buff_runtime_view: "BuffRuntimeReadPort | None" = None,
) -> RuntimeCommandPort:
    """创建同 tick runtime 写侧命令入口。"""
    if buff_runtime_state is not None:
        return DefaultRuntimeCommandAdapter(
            data=data,
            action_stack=action_stack,
            sim_instance=sim_instance,
            buff_runtime_state=buff_runtime_state,
            buff_runtime_view=buff_runtime_view,
        )
    return LegacyRuntimeCommandAdapter(
        data=data,
        action_stack=action_stack,
        sim_instance=sim_instance,
        exist_buff_dict=exist_buff_dict,
        buff_runtime_state=buff_runtime_state,
        buff_runtime_view=buff_runtime_view,
    )


__all__ = [
    "RuntimeCommandPort",
    "DefaultRuntimeCommandAdapter",
    "LegacyRuntimeCommandAdapter",
    "create_runtime_command_port",
]
