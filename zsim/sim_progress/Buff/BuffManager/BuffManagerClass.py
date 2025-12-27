from typing import TYPE_CHECKING, Dict, List, Optional

# 引入核心组件
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
    Buff 管理器 (Final Version).

    职责：
    1. 管理 Buff 实例的生命周期 (创建, 刷新, 叠层, 销毁).
    2. 连接 EventSystem: 为 Buff 注册/注销触发器.
    3. 连接 BonusPool: 为 Character 同步/移除属性加成.
    """

    def __init__(self, owner_id: str, sim_instance: "Simulator"):
        self.owner_id = owner_id
        self.sim_instance = sim_instance

        # 存储当前激活的 Buff: { buff_id: BuffInstance }
        self._active_buffs: Dict[str, Buff] = {}

        # 存储触发器 Handler，用于移除时注销
        # { buff_id: [Handler1, Handler2, ...] }
        self._buff_handlers: Dict[str, List["ZSimEventHandler"]] = {}

        # 获取全局控制器引用 (工厂)
        self._controller = GlobalBuffController.get_instance()

    @property
    def owner(self) -> Optional["Character"]:
        """[Helper] 获取 Buff 持有者的 Character 实例"""
        return self.sim_instance.char_obj_dict.get(self.owner_id)

    def add_buff(self, buff_id: str, current_tick: int, stacks: int = 1, duration: int = -1):
        """
        添加或刷新 Buff。
        Args:
            buff_id: Buff 名称/ID.
            current_tick: 当前时间 tick.
            stacks: 施加的层数 (默认为1).
            duration: 持续时间 (tick), -1 表示使用默认值.
        """
        if buff_id in self._active_buffs:
            # --- Case A: Buff 已存在 -> 刷新与叠层 ---
            existing_buff = self._active_buffs[buff_id]

            # 刷新时间 (如果 Buff 有持续时间)
            if existing_buff.ft.maxduration > 0:
                existing_buff.refresh(current_tick)

            # 叠加层数
            if existing_buff.ft.maxcount > 1:
                existing_buff.add_stack(stacks)

            # (可选) 某些 Buff 即使已存在，重复添加也可能触发特定逻辑，可在此扩展

        else:
            # --- Case B: Buff 不存在 -> 新建实例 ---
            try:
                # 1. 工厂创建
                new_buff = self._controller.instantiate_buff(buff_id, self.sim_instance)

                # 2. 初始化状态
                new_buff.start(current_tick, duration)
                if stacks > 0:
                    new_buff.dy.count = min(stacks, new_buff.ft.maxcount)
                else:
                    new_buff.dy.count = 1

                self._active_buffs[buff_id] = new_buff

                # 3. [Integration] 注册触发器 (Event System)
                self._register_buff_triggers(new_buff)

                # 4. [Integration] 注册属性加成 (Bonus Pool)
                # 这是 Phase 4 核心逻辑：让 Buff 的属性加成生效
                self._register_buff_bonuses(new_buff)

                report_to_log(f"[{self.owner_id}] Buff获得: {buff_id}", level=2)

            except ValueError as e:
                report_to_log(f"[{self.owner_id}] 添加Buff失败 '{buff_id}': {e}", level=4)

    def remove_buff(self, buff_id: str, current_tick: int):
        """主动移除 Buff"""
        if buff_id in self._active_buffs:
            buff = self._active_buffs[buff_id]
            buff.end(current_tick)

            # 1. 注销触发器
            self._unregister_buff_triggers(buff_id)

            # 2. 注销属性加成
            self._unregister_buff_bonuses(buff)

            del self._active_buffs[buff_id]

            report_to_log(f"[{self.owner_id}] Buff移除: {buff_id}", level=2)

    def get_buff(self, buff_id: str) -> Optional[Buff]:
        """查询 Buff"""
        return self._active_buffs.get(buff_id)

    def tick(self, current_tick: int):
        """
        [生命周期维护]
        在 Simulator 主循环中调用，检查自然过期的 Buff。
        """
        # 使用 list() 复制 keys，因为遍历时可能删除字典元素
        for buff_id in list(self._active_buffs.keys()):
            buff = self._active_buffs[buff_id]

            if buff.check_expiry(current_tick):
                # report_to_log(f"[{self.owner_id}] Buff自然过期: {buff_id}", level=3)
                self.remove_buff(buff_id, current_tick)

    # -------------------------------------------------------------------------
    # 内部辅助方法
    # -------------------------------------------------------------------------

    def _register_buff_triggers(self, buff: Buff):
        """解析 TriggerEffect 并注册 Handler"""
        handlers = []
        registry = getattr(self.sim_instance, "event_handler_registry", None)

        if not registry:
            return

        for effect in buff.effects:
            if isinstance(effect, TriggerEffect):
                # 创建 Handler
                handler = BuffTriggerHandler(self.owner_id, buff, effect)

                # 注册到全局事件系统
                # 注意: registry.register 需要支持 (EventType, Handler)
                registry.register(effect.trigger_event_type, handler)

                handlers.append(handler)

        if handlers:
            self._buff_handlers[buff.ft.index] = handlers

    def _unregister_buff_triggers(self, buff_id: str):
        """清理触发器引用"""
        if buff_id in self._buff_handlers:
            del self._buff_handlers[buff_id]

    def _register_buff_bonuses(self, buff: Buff):
        """将 BonusEffect 注入角色的 BonusPool"""
        owner = self.owner
        if owner and hasattr(owner, "bonus_pool"):
            for effect in buff.effects:
                if isinstance(effect, BonusEffect):
                    owner.bonus_pool.add_effect(effect)

    def _unregister_buff_bonuses(self, buff: Buff):
        """从角色的 BonusPool 移除 BonusEffect"""
        owner = self.owner
        if owner and hasattr(owner, "bonus_pool"):
            for effect in buff.effects:
                if isinstance(effect, BonusEffect):
                    owner.bonus_pool.remove_effect(effect)
