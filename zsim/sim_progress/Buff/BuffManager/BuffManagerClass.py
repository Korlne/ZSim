from typing import TYPE_CHECKING, Dict, List, Optional

from zsim.sim_progress.Buff.buff_class import Buff
from zsim.sim_progress.Buff.Effect.definitions import BonusEffect, TriggerEffect
from zsim.sim_progress.Buff.Event.buff_handler import BuffTriggerHandler
from zsim.sim_progress.Buff.GlobalBuffControllerClass.global_buff_controller import (
    GlobalBuffController,
)
from zsim.sim_progress.Report import report_to_log
from zsim.sim_progress.Report.buff_handler import report_buff_to_queue

if TYPE_CHECKING:
    from zsim.sim_progress.Character.character import Character
    from zsim.sim_progress.zsim_event_system.Handler.base_handler_class import ZSimEventHandler
    from zsim.simulator.simulator_class import Simulator


class BuffManager:
    """
    Buff 管理器.
    负责管理持有者身上的所有 Buff 实例及其生命周期、效果注册。

    核心职责：
    1. 维护 active_buffs 字典。
    2. 处理 add_buff (创建/刷新/叠层) 和 remove_buff (清理/注销)。
    3. 每一帧 tick() 检查过期 Buff。
    4. 桥接 GlobalBuffController (工厂)、EventSystem (触发器) 和 BonusPool (数值)。
    """

    def __init__(self, owner_id: str, sim_instance: "Simulator"):
        self.owner_id = owner_id
        self.sim_instance = sim_instance

        # 存储当前激活的 Buff: { buff_id: BuffInstance }
        self._active_buffs: Dict[str, Buff] = {}

        # 存储触发器 Handler 引用，用于调试或扩展
        # { buff_id: [Handler1, Handler2, ...] }
        self._buff_handlers: Dict[str, List["ZSimEventHandler"]] = {}

        # 全局控制器 (工厂)
        self._controller = GlobalBuffController.get_instance()

    @property
    def owner(self) -> Optional["Character"]:
        """[Helper] 获取 Buff 持有者的 Character 实例"""
        # [Fix] 适配新 Simulator 结构，通过 char_data 获取 char_obj_dict
        if self.sim_instance.char_data:
            char = self.sim_instance.char_data.char_obj_dict.get(self.owner_id)
            if char:
                return char

        # 如果是敌人
        if (
            self.sim_instance.enemy
            and getattr(self.sim_instance.enemy, "name", "") == self.owner_id
        ):
            return self.sim_instance.enemy

        return None

    def add_buff(self, buff_id: str, current_tick: int) -> Optional[Buff]:
        """
        添加或刷新 Buff。
        [Refactor] 适配 GlobalBuffController 的 instantiate_buff 接口
        """
        existing_buff = self._active_buffs.get(buff_id)

        if existing_buff:
            # 刷新逻辑 (Refresh)
            # 使用 Buff 自身的 start 方法重置持续时间
            existing_buff.start(current_tick)

            if existing_buff.dy.count < existing_buff.ft.maxcount:
                existing_buff.dy.count += 1

            return existing_buff
        else:
            # 创建逻辑 (Create)
            # 使用 instantiate_buff 创建实例
            new_buff = self._controller.instantiate_buff(buff_id, self.sim_instance)

            if not new_buff:
                report_to_log(f"[BuffManager] Failed to create buff: {buff_id}", "warning")
                return None

            # 绑定 Owner
            new_buff.owner = self.owner

            # 初始化/激活 Buff
            new_buff.start(current_tick)
            if new_buff.dy.count == 0:
                new_buff.dy.count = 1

            self._active_buffs[buff_id] = new_buff

            # 注册效果
            self._register_buff_bonuses(new_buff)
            self._register_buff_triggers(new_buff)

            report_to_log(
                f"[BuffManager] {self.owner_id} 获得了 Buff [{buff_id}] (Tick: {current_tick})"
            )
            return new_buff

    def remove_buff(self, buff_id: str, current_tick: int) -> bool:
        buff = self._active_buffs.get(buff_id)
        if not buff:
            return False

        self._unregister_buff_bonuses(buff)
        self._unregister_buff_triggers(buff)
        del self._active_buffs[buff_id]

        report_to_log(
            f"[BuffManager] {self.owner_id} 失去了 Buff [{buff_id}] (Tick: {current_tick})"
        )
        return True

    def tick(self, current_tick: int):
        # [Fix] 增加 Buff 日志上报逻辑
        # 遍历所有激活的 Buff 并记录其层数
        for buff_id, buff in self._active_buffs.items():
            if buff.dy.active:
                report_buff_to_queue(
                    character_name=self.owner_id,
                    time_tick=current_tick + 1,  # 补偿上报函数内部的 -1 偏移
                    buff_name=buff_id,
                    buff_count=buff.dy.count,
                    all_match=True,  # 强制记录
                )

        expired_buffs = []
        for buff_id, buff in self._active_buffs.items():
            if hasattr(buff, "check_expiry"):
                if buff.check_expiry(current_tick):
                    expired_buffs.append(buff_id)
            else:
                if buff.ft.maxduration > 0:
                    if (current_tick - buff.dy.start_tick) >= buff.ft.maxduration:
                        expired_buffs.append(buff_id)

        for buff_id in expired_buffs:
            self.remove_buff(buff_id, current_tick)

    def get_buff(self, buff_id: str) -> Optional[Buff]:
        """查询 Buff"""
        return self._active_buffs.get(buff_id)

    def has_buff(self, buff_id: str) -> bool:
        """检查是否持有且激活"""
        buff = self._active_buffs.get(buff_id)
        return buff is not None and buff.dy.active

    # =========================================================================
    #  内部集成方法
    # =========================================================================

    def _register_buff_bonuses(self, buff: Buff):
        """将 Buff 的数值加成 (BonusEffect) 注册到 Owner 的 BonusPool"""
        owner = self.owner
        if not owner:
            return

        # 使用 BonusPool.add_modifier 批量注册
        # 筛选出所有的 BonusEffect
        bonus_effects = [e for e in buff.effects if isinstance(e, BonusEffect)]

        if bonus_effects and hasattr(owner, "bonus_pool"):
            owner.bonus_pool.add_modifier(buff.ft.index, bonus_effects)

    def _unregister_buff_bonuses(self, buff: Buff):
        """注销数值加成"""
        owner = self.owner
        if not owner:
            return

        # 使用 BonusPool.remove_modifier 批量注销
        if hasattr(owner, "bonus_pool"):
            owner.bonus_pool.remove_modifier(buff.ft.index)

    def _register_buff_triggers(self, buff: Buff):
        """注册事件触发器 (TriggerEffect) 到 EventSystem"""
        if buff.ft.index not in self._buff_handlers:
            self._buff_handlers[buff.ft.index] = []

        for effect in buff.effects:
            if isinstance(effect, TriggerEffect) and effect.enable:
                # 创建专用 Handler
                handler = BuffTriggerHandler(
                    buff_instance=buff,
                    trigger_effect=effect,
                    sim_instance=self.sim_instance,
                )

                from zsim.sim_progress.zsim_event_system.Handler.zsim_event_handler_registry import (
                    ZSimEventHandlerRegistry,
                )

                ZSimEventHandlerRegistry.register(handler)
                self._buff_handlers[buff.ft.index].append(handler)

    def _unregister_buff_triggers(self, buff: Buff):
        """注销事件触发器"""
        handlers = self._buff_handlers.get(buff.ft.index, [])
        from zsim.sim_progress.zsim_event_system.Handler.zsim_event_handler_registry import (
            ZSimEventHandlerRegistry,
        )

        for handler in handlers:
            ZSimEventHandlerRegistry.unregister(handler)

        self._buff_handlers[buff.ft.index] = []
