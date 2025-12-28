from typing import TYPE_CHECKING, Dict, List, Optional

from zsim.sim_progress.Buff.buff_class import Buff
from zsim.sim_progress.Buff.Effect.definitions import BonusEffect, TriggerEffect
from zsim.sim_progress.Buff.Event.buff_handler import BuffTriggerHandler
from zsim.sim_progress.Buff.GlobalBuffControllerClass.global_buff_controller import (
    GlobalBuffController,
)
from zsim.sim_progress.Report import report_to_log

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
        # 注意：这里假设 owner 是角色。如果是敌人，可能需要从 enemy_group 或 direct reference 获取
        # 为了兼容性，先尝试从 char_obj_dict 获取
        char = self.sim_instance.char_obj_dict.get(self.owner_id)
        if char:
            return char

        # 如果是敌人
        if (
            self.sim_instance.enemy
            and getattr(self.sim_instance.enemy, "name", "") == self.owner_id
        ):
            return self.sim_instance.enemy

        return None

    def add_buff(self, buff_id: str, current_tick: int, stacks: int = 1, duration: int = -1):
        """
        添加或刷新 Buff。
        Args:
            buff_id: Buff 名称/ID.
            current_tick: 当前时间 tick.
            stacks: 施加的层数 (默认为1).
            duration: 持续时间 (tick), -1 表示使用配置的默认值.
        """
        if buff_id in self._active_buffs:
            # --- Case A: Buff 已存在 -> 刷新与叠层 ---
            existing_buff = self._active_buffs[buff_id]

            # 1. 刷新持续时间
            if existing_buff.ft.maxduration > 0:
                existing_buff.refresh(current_tick)
                # 注：如果逻辑需要支持动态改变 duration，可在此扩展

            # 2. 叠加层数
            if existing_buff.ft.maxcount > 1:
                existing_buff.add_stack(stacks)

            report_to_log(
                f"[{self.owner_id}] Buff刷新: {buff_id}, 层数: {existing_buff.dy.count}", level=1
            )

        else:
            # --- Case B: Buff 不存在 -> 新建实例 ---
            try:
                # 1. 工厂创建
                new_buff = self._controller.instantiate_buff(buff_id, self.sim_instance)

                # 2. 初始化状态
                initial_stack = min(stacks, new_buff.ft.maxcount) if stacks > 0 else 1
                new_buff.dy.count = initial_stack
                new_buff.start(current_tick, duration)

                self._active_buffs[buff_id] = new_buff

                # 3. 注册触发器 (Event System)
                self._register_buff_triggers(new_buff)

                # 4. 注册属性加成 (Bonus Pool)
                self._register_buff_bonuses(new_buff)

                report_to_log(f"[{self.owner_id}] Buff获得: {buff_id}", level=2)

            except Exception as e:
                import traceback

                traceback.print_exc()
                report_to_log(f"[{self.owner_id}] 添加Buff失败 '{buff_id}': {e}", level=4)

    def remove_buff(self, buff_id: str, current_tick: int):
        """主动移除 Buff"""
        if buff_id in self._active_buffs:
            buff = self._active_buffs[buff_id]

            # 1. 标记结束
            buff.end(current_tick)

            # 2. 注销触发器 (清理 Handler 引用)
            self._unregister_buff_triggers(buff_id)

            # 3. 注销属性加成 (从 BonusPool 移除)
            self._unregister_buff_bonuses(buff)

            # 4. 从容器移除
            del self._active_buffs[buff_id]

            report_to_log(f"[{self.owner_id}] Buff移除: {buff_id}", level=2)

    def get_buff(self, buff_id: str) -> Optional[Buff]:
        """查询 Buff"""
        return self._active_buffs.get(buff_id)

    def has_buff(self, buff_id: str) -> bool:
        """检查是否持有且激活"""
        buff = self._active_buffs.get(buff_id)
        return buff is not None and buff.dy.active

    def tick(self, current_tick: int):
        """
        [生命周期维护]
        在 Simulator 主循环中调用，检查自然过期的 Buff。
        """
        # 使用 list(keys) 避免遍历时删除报错
        for buff_id in list(self._active_buffs.keys()):
            buff = self._active_buffs[buff_id]

            if buff.check_expiry(current_tick):
                report_to_log(f"[{self.owner_id}] Buff自然过期: {buff_id}", level=1)
                self.remove_buff(buff_id, current_tick)

    # -------------------------------------------------------------------------
    # 内部集成方法
    # -------------------------------------------------------------------------

    def _register_buff_triggers(self, buff: Buff):
        """解析 TriggerEffect 并注册 Handler 到全局事件系统"""
        registry = getattr(self.sim_instance, "event_handler_registry", None)
        if not registry:
            # 如果模拟器尚未集成新事件注册表，则跳过
            return

        handlers = []
        for effect in buff.effects:
            if isinstance(effect, TriggerEffect):
                # 创建 Handler
                handler = BuffTriggerHandler(self.owner_id, buff, effect)

                # 注册到事件系统
                # 注意：事件类型通常在 definitions.py 或 TriggerEffect 中定义
                registry.register(effect.trigger_event_type, handler)

                handlers.append(handler)

        if handlers:
            self._buff_handlers[buff.ft.index] = handlers

    def _unregister_buff_triggers(self, buff_id: str):
        """清理本地 Handler 引用"""
        # 注意：ZSimEventHandlerRegistry 目前没有 unregister 接口。
        # 机制上依赖 Buff.dy.active = False 来让 Handler.supports() 返回 False，从而停止响应。
        if buff_id in self._buff_handlers:
            del self._buff_handlers[buff_id]

    def _register_buff_bonuses(self, buff: Buff):
        """将 BonusEffect 注入角色的 BonusPool"""
        owner = self.owner
        if owner and hasattr(owner, "bonus_pool"):
            # 筛选出所有的 BonusEffect
            bonus_effects = [e for e in buff.effects if isinstance(e, BonusEffect)]

            if not bonus_effects:
                return

            # 优先使用新版批量接口 add_modifier
            if hasattr(owner.bonus_pool, "add_modifier"):
                owner.bonus_pool.add_modifier(buff.ft.index, bonus_effects)
            else:
                # 兼容旧版逐个添加
                for effect in bonus_effects:
                    owner.bonus_pool.add_effect(effect)

    def _unregister_buff_bonuses(self, buff: Buff):
        """从角色的 BonusPool 移除 BonusEffect"""
        owner = self.owner
        if owner and hasattr(owner, "bonus_pool"):
            # 优先使用新版批量接口 remove_modifier
            if hasattr(owner.bonus_pool, "remove_modifier"):
                owner.bonus_pool.remove_modifier(buff.ft.index)
            else:
                # 兼容旧版逐个移除
                for effect in buff.effects:
                    if isinstance(effect, BonusEffect):
                        owner.bonus_pool.remove_effect(effect)
