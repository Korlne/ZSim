from typing import Dict, List, Optional, TYPE_CHECKING
from .buff_model import Buff

if TYPE_CHECKING:
    from zsim.sim_progress.Character.character import Character

class BuffManager:
    """
    角色 Buff 管理器
    职责：
    1. 维护角色当前激活的 Buff 列表 (active_buff_list)。
    2. 提供 add_buff, remove_buff, has_buff 等 CRUD 接口。
    3. 负责 Buff 状态变更时通知属性计算系统 (Sync with BonusPool)。
    """
    def __init__(self, owner: "Character"):
        self.owner = owner
        # 动态 Buff 列表：BuffID -> Buff Instance
        self._active_buffs: Dict[str, Buff] = {}

    def get_active_buffs(self) -> List[Buff]:
        """获取当前所有激活的 Buff"""
        return list(self._active_buffs.values())

    def has_buff(self, buff_id: str) -> bool:
        """检查角色是否持有指定 Buff"""
        return buff_id in self._active_buffs

    def get_buff(self, buff_id: str) -> Optional[Buff]:
        """获取指定的激活 Buff"""
        return self._active_buffs.get(buff_id)

    def add_buff(self, buff: Buff, timestamp: int, duration: Optional[int] = None, stacks: int = 0) -> None:
        """
        向角色添加或刷新 Buff。
        :param buff: 要添加的 Buff 对象 (通常来自 GlobalBuffController)
        :param timestamp: 当前时间戳
        :param duration: 持续时间 (None 则使用 Buff 默认配置)
        :param stacks: 叠加层数 (0 则使用 Buff 默认配置)
        """
        buff_id = buff.ft.buff_id

        # 场景 A: Buff 已存在 -> 刷新
        if buff_id in self._active_buffs:
            existing_buff = self._active_buffs[buff_id]
            existing_buff.refresh(timestamp, duration, stacks)
            # 刷新可能改变层数，需要同步效果
            self._sync_bonus_pool(existing_buff)
            return

        # 场景 B: 新 Buff -> 激活并添加
        # 注意：此处直接操作传入的 Buff 对象。
        # 如果 Buff 是全局唯一的（如设计文档所述），这没问题。
        # 如果 Buff 可能是通用的，则需考虑是否 clone。目前遵循“Buff对象唯一”原则。
        buff.start(timestamp, duration, stacks)
        
        if buff.dy.is_active:
            self._active_buffs[buff_id] = buff
            self._on_buff_added(buff)

    def remove_buff(self, buff_id: str, timestamp: int) -> None:
        """
        移除指定 Buff。
        :param buff_id: Buff ID
        :param timestamp: 移除发生的时间戳
        """
        if buff_id not in self._active_buffs:
            return

        buff = self._active_buffs[buff_id]
        buff.end(timestamp) # 执行 Buff 自身的结束逻辑 (统计数据等)
        
        del self._active_buffs[buff_id]
        self._on_buff_removed(buff)

    def tick(self, current_time: int) -> None:
        """
        [生命周期] 模拟器每个 Tick 调用一次。
        负责清理过期 Buff。
        """
        # 收集需要移除的 Buff ID (避免遍历时修改字典)
        expired_ids = []
        
        for buff_id, buff in self._active_buffs.items():
            # 1. 检查独立堆叠的过期情况
            if buff.ft.independent_stacks:
                buff.cleanup_expired_stacks(current_time)
            
            # 2. 检查 Buff 是否整体过期 (Buff.end() 会将 is_active 置为 False)
            # 如果非独立堆叠，cleanup_expired_stacks 也会处理 end_time 检查
            if not buff.ft.independent_stacks:
                 buff.cleanup_expired_stacks(current_time)

            if not buff.dy.is_active:
                expired_ids.append(buff_id)

        # 执行移除
        for bid in expired_ids:
            # 这里调用 internal remove，不再重复调用 buff.end() 因为它已经 inactive 了
            # 但为了触发 removed 回调，我们需要手动处理
            del self._active_buffs[bid]
            # 获取 Buff 对象引用稍显困难，但在 active 列表中肯定是存在的
            # 由于上面已经 inactive，我们假设它已经完成了 end 逻辑，这里只需处理移除回调
            # 但我们需要 Effect 对象来清理 BonusPool
            # 优化：在 remove_buff 中处理，或者在这里
            # 简单起见，从 GlobalController 获取引用或在遍历前暂存
            # 这里简化处理：通知 BonusPool 移除该 ID 对应的效果
            self._sync_bonus_pool_remove(bid)

    # --- 内部同步方法 (将在后续接入 BonusPool 时具体实现) ---

    def _on_buff_added(self, buff: Buff):
        """Buff 添加时的回调"""
        self._sync_bonus_pool(buff)

    def _on_buff_removed(self, buff: Buff):
        """Buff 移除时的回调"""
        self._sync_bonus_pool_remove(buff.ft.buff_id)

    def _sync_bonus_pool(self, buff: Buff):
        """
        通知 Character 的 BonusPool 更新该 Buff 的效果。
        (等待 BonusPool 重构完成后接入)
        """
        if hasattr(self.owner, "bonus_pool") and self.owner.bonus_pool:
            # self.owner.bonus_pool.update_effects(buff)
            pass

    def _sync_bonus_pool_remove(self, buff_id: str):
        """
        通知 Character 的 BonusPool 移除该 Buff 的效果。
        """
        if hasattr(self.owner, "bonus_pool") and self.owner.bonus_pool:
            # self.owner.bonus_pool.remove_effects(buff_id)
            pass