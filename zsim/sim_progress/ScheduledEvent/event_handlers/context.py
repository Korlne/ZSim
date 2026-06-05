"""
事件处理上下文模型

该模块定义了事件处理上下文的dataclass，用于替代字典形式的上下文数据。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..buff_runtime import BuffRuntimeReadPort

if TYPE_CHECKING:
    from zsim.sim_progress.data_struct import ActionStack
    from zsim.sim_progress.Enemy import Enemy
    from zsim.sim_progress.Preload.SkillsQueue import SkillNode
    from zsim.simulator.dataclasses import ScheduleData
    from zsim.simulator.simulator_class import Simulator


@dataclass
class EventContext:
    """
    事件处理上下文模型

    包含事件处理所需的全部数据和对象，使用dataclass提供类型安全和简洁的语法。
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

    def get_dynamic_buff(self):
        """获取兼容旧接口的动态 Buff 容器"""
        return self.buff_runtime_view.get_legacy_dynamic_buff_dict()

    def get_exist_buff_dict(self):
        """获取兼容旧接口的旧快照 Buff 容器"""
        return self.buff_runtime_view.get_legacy_exist_buff_dict()

    def get_action_stack(self) -> ActionStack[SkillNode]:
        """获取动作栈"""
        return self.action_stack

    def get_sim_instance(self) -> Simulator:
        """获取模拟器实例"""
        return self.sim_instance
