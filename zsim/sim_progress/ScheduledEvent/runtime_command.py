from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from zsim.sim_progress.Buff.ScheduleBuffSettle import (
    ScheduleBuffSettle as legacy_schedule_buff_settle,
)
from zsim.sim_progress.Update import update_anomaly as legacy_update_anomaly

if TYPE_CHECKING:
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


class LegacyRuntimeCommandAdapter(RuntimeCommandPort):
    """基于旧容器的 runtime command 兼容适配器。"""

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
        # 通过 ScheduleData 取当前 event_list，避免列表被重绑后持有过期引用。
        legacy_update_anomaly(
            element_type,
            enemy,
            tick,
            self._data.event_list,
            self._data.char_obj_list,
            skill_node=skill_node,
            dynamic_buff_dict=self._active_store_for_compat(),
            buff_runtime_view=self._buff_runtime_view,
            sim_instance=self._sim_instance,
        )

    def settle_buffs(
        self,
        *,
        tick: int,
        enemy: "Enemy",
        skill_node: "SkillNode | LoadingMission | None" = None,
        anomaly_bar: "AnomalyBar | None" = None,
    ) -> None:
        legacy_kwargs: dict[str, object] = {}
        if skill_node is not None:
            legacy_kwargs["skill_node"] = skill_node
        if anomaly_bar is not None:
            legacy_kwargs["anomaly_bar"] = anomaly_bar

        legacy_schedule_buff_settle(
            tick,
            self._template_registry_for_compat(),
            enemy,
            self._active_store_for_compat(),
            self._action_stack,
            sim_instance=self._sim_instance,
            **legacy_kwargs,
        )

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
    "LegacyRuntimeCommandAdapter",
    "create_runtime_command_port",
]
