"""
事件处理上下文模型

该模块定义了事件处理上下文的 dataclass，用于替代字典形式的上下文数据。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Mapping, Sequence

from ..buff_runtime import BuffRuntimeReadPort

if TYPE_CHECKING:
    from zsim.sim_progress.Buff import Buff
    from zsim.sim_progress.data_struct import ActionStack
    from zsim.sim_progress.Enemy import Enemy
    from zsim.sim_progress.Preload.SkillsQueue import SkillNode
    from zsim.simulator.dataclasses import ScheduleData
    from zsim.simulator.simulator_class import Simulator


@dataclass
class EventContext:
    """
    事件处理上下文模型

    包含事件处理所需的全部数据和对象，使用 dataclass 提供类型安全和简洁语法。
    """

    data: ScheduleData
    tick: int
    enemy: Enemy
    buff_runtime_view: BuffRuntimeReadPort
    action_stack: ActionStack[SkillNode]
    sim_instance: Simulator

    def get_data(self) -> ScheduleData:
        """获取调度数据对象"""
        return self.data

    def get_tick(self) -> int:
        """获取当前时间刻"""
        return self.tick

    def get_enemy(self) -> Enemy:
        """获取敌人对象"""
        return self.enemy

    def get_buff_runtime_view(self) -> BuffRuntimeReadPort:
        """获取 Buff runtime 只读视图"""
        return self.buff_runtime_view

    def get_active_buffs(self, beneficiary: str) -> Sequence["Buff"]:
        """获取指定受益者的 active Buff 只读列表"""
        return self.buff_runtime_view.get_active_buffs(beneficiary)

    def get_active_buff_view(self) -> Mapping[str, Sequence["Buff"]]:
        """获取所有受益者的 active Buff 只读视图"""
        return self.buff_runtime_view.get_active_buff_view()

    def get_exist_buff_snapshot(self, beneficiary: str) -> Mapping[str, "Buff"]:
        """获取指定受益者的 snapshot Buff 只读视图"""
        return self.buff_runtime_view.get_exist_buff_snapshot(beneficiary)

    def get_exist_buff_snapshot_view(self) -> Mapping[str, Mapping[str, "Buff"]]:
        """获取所有受益者的 snapshot Buff 只读视图"""
        return self.buff_runtime_view.get_exist_buff_snapshot_view()

    def get_dynamic_buff(self):
        """获取兼容旧接口的动态 Buff 容器"""
        return self.buff_runtime_view.get_legacy_dynamic_buff_dict()

    def get_exist_buff_dict(self):
        """获取兼容旧接口的旧 snapshot Buff 容器"""
        return self.buff_runtime_view.get_legacy_exist_buff_dict()

    def get_action_stack(self) -> ActionStack[SkillNode]:
        """获取动作栈"""
        return self.action_stack

    def get_sim_instance(self) -> Simulator:
        """获取模拟器实例"""
        return self.sim_instance
