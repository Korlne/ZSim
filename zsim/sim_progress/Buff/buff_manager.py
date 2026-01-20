from typing import Optional, TYPE_CHECKING
from .buff_model import Buff

from zsim.sim_progress.zsim_event_system.zsim_events.buff_event import (
    PeriodicBuffTickEvent, 
    BuffEventMessage
)

if TYPE_CHECKING:
    from zsim.sim_progress.Character.character import Character


class BuffManager:
    """
    角色 Buff 管理器
    职责：
    1. 维护角色当前激活的 Buff 列表 (active_buff_list)。
    2. 提供 CRUD 接口。
    3. 负责同步 BonusPool。
    """
    def __init__(self, owner: "Character"):
        self.owner = owner
        # 动态 Buff 列表：BuffID -> Buff Instance
        self._active_buffs: dict[int, Buff] = {}

    def get_active_buffs(self) -> list[Buff]:
        return list(self._active_buffs.values())

    def has_buff(self, buff_id: int) -> bool:
        return buff_id in self._active_buffs

    def get_buff(self, buff_id: int) -> Optional[Buff]:
        return self._active_buffs.get(buff_id)

    def add_buff(
        self, buff: Buff, timestamp: int, duration: Optional[int] = None, stacks: int = 0
    ) -> None:
        """
        向角色添加或刷新 Buff。
        :param buff: 必须是一个全新的、独占的 Buff 实例 (通过 Factory 创建)
        """
        buff_id = buff.ft.buff_id

        # 场景 A: Buff 已存在 -> 刷新现有实例
        if buff_id in self._active_buffs:
            existing_buff = self._active_buffs[buff_id]
            existing_buff.refresh(timestamp, duration, stacks)
            self._sync_bonus_pool(existing_buff)
            return

        # 场景 B: 新 Buff -> 激活传入的新实例
        buff.start(timestamp, duration, stacks)
        
        if buff.dy.is_active:
            self._active_buffs[buff_id] = buff
            self._on_buff_added(buff)
            
            # 检查并注册周期性事件
            self._register_periodic_events(buff, timestamp)

    def remove_buff(self, buff_id: int, timestamp: int) -> None:
        """移除指定 Buff"""
        if buff_id not in self._active_buffs:
            return

        buff = self._active_buffs[buff_id]
        buff.end(timestamp)
        
        del self._active_buffs[buff_id]
        self._on_buff_removed(buff)

    def _register_periodic_events(self, buff: Buff, current_tick: int) -> None:
        """检查 Buff 是否包含周期性 TriggerEffect，并注册首个 Tick 事件"""
        # 假设 buff.effects 包含了该 Buff 的所有 Effect 对象
        # 需要确保 Buff Model 中有 effects 属性，或者通过 buff_feature 获取
        effects = getattr(buff, "effects", []) 
        
        for effect in effects:
            # 判断是否为 TriggerEffect 且包含定时器配置
            if hasattr(effect, "timer_config") and effect.timer_config:
                self._schedule_next_tick(buff, effect, current_tick, is_first=True)

    def _schedule_next_tick(self, buff: Buff, effect, current_tick: int, is_first: bool = False):
            """向调度器注册下一个 Tick 事件"""
            # [ZSim 架构规范] Character 必定持有 sim_instance 引用
            # 且 Simulator 必定持有 data (ScheduleData)
            if self.owner.sim_instance is None:
                # 仅在非仿真环境（如单元测试未mock simulator）时可能发生，视情况保留或移除
                return

            interval_seconds = effect.timer_config.interval
            # 1秒 = 60 ticks
            interval_ticks = int(interval_seconds * 60)
            
            # 如果配置了立即触发且是第一次
            if is_first and effect.timer_config.immediate:
                execute_tick = current_tick
            else:
                execute_tick = current_tick + interval_ticks

            # 构造事件
            event_msg = BuffEventMessage(
                buff_id=str(buff.ft.buff_id),
                lifecycle_type="periodic_tick",
                current_stacks=buff.dy.current_stacks,
                duration_remaining=buff.dy.end_tick - execute_tick
            )
            
            event = PeriodicBuffTickEvent(
                event_message=event_msg,
                event_origin=buff,
                execute_tick=execute_tick
            )

            self.owner.sim_instance.data.event_list.append(event)

    def tick(self, current_time: int) -> None:
        """[生命周期] 负责清理过期 Buff"""
        expired_ids = []
        
        for buff_id, buff in self._active_buffs.items():
            if buff.ft.independent_stacks:
                buff.cleanup_expired_stacks(current_time)
            
            if not buff.ft.independent_stacks:
                buff.cleanup_expired_stacks(current_time)

            if not buff.dy.is_active:
                expired_ids.append(buff_id)

        for bid in expired_ids:
            # 清理引用并通知
            if bid in self._active_buffs:
                del self._active_buffs[bid]
                self._sync_bonus_pool_remove(bid)

    def _on_buff_added(self, buff: Buff) -> None:
        self._sync_bonus_pool(buff)

    def _on_buff_removed(self, buff: Buff) -> None:
        self._sync_bonus_pool_remove(buff.ft.buff_id)

    def _sync_bonus_pool(self, buff: Buff) -> None:
        """通知 Character 的 BonusPool 更新该 Buff 的效果"""
        # if hasattr(self.owner, "bonus_pool"):
        #     self.owner.bonus_pool.update_effects(buff)
        pass

    def _sync_bonus_pool_remove(self, buff_id: int) -> None:
        """通知 Character 的 BonusPool 移除该 Buff 的效果"""
        # if hasattr(self.owner, "bonus_pool"):
        #     self.owner.bonus_pool.remove_effects(buff_id)
        pass