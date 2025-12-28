from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List

from zsim.sim_progress.Buff.Effect.definitions import BonusEffect

if TYPE_CHECKING:
    from zsim.sim_progress.Character.character import Character


class BonusPool:
    """
    属性加成池。
    管理角色身上的所有数值类增益 (BonusEffect)。

    职责：
    1. 存储来自各个 Buff 的 BonusEffect。
    2. 提供按属性名查询汇总数值的接口。
    3. [新增] 支持按来源 ID (Source ID) 批量添加/移除效果。
    """

    def __init__(self, owner: "Character"):
        self.owner = owner
        # 核心存储: { "攻击力%": [Effect1, Effect2], ... }
        self._effects: Dict[str, List[BonusEffect]] = defaultdict(list)

        # [新增] 来源索引: { "Buff-1001": [Effect1, Effect2], ... }
        # 用于快速查找并移除指定 Buff 带来的所有效果
        self._source_index: Dict[str, List[BonusEffect]] = defaultdict(list)

    def add_effect(self, effect: BonusEffect):
        """(底层接口) 注册单个效果"""
        self._effects[effect.target_attribute].append(effect)

    def remove_effect(self, effect: BonusEffect):
        """(底层接口) 移除单个效果"""
        attr = effect.target_attribute
        if attr in self._effects:
            try:
                self._effects[attr].remove(effect)
                if not self._effects[attr]:
                    del self._effects[attr]
            except ValueError:
                pass

    # -------------------------------------------------------------------------
    # 新架构适配接口
    # -------------------------------------------------------------------------

    def add_modifier(self, source_id: str, effects: List[BonusEffect]):
        """
        [新接口] 注册来自特定来源（如 Buff ID）的一组效果。
        Args:
            source_id: 来源标识（如 BuffName）
            effects: 效果列表
        """
        # 记录到来源索引
        self._source_index[source_id].extend(effects)

        # 注册到核心存储
        for effect in effects:
            self.add_effect(effect)

    def remove_modifier(self, source_id: str):
        """
        [新接口] 移除指定来源的所有效果。
        """
        if source_id not in self._source_index:
            return

        # 获取该来源的所有效果
        effects_to_remove = self._source_index[source_id]

        # 从核心存储中移除
        for effect in effects_to_remove:
            self.remove_effect(effect)

        # 清理来源索引
        del self._source_index[source_id]

    # -------------------------------------------------------------------------
    # 查询接口 (保持不变)
    # -------------------------------------------------------------------------

    def query_total_add(self, attribute_name: str) -> float:
        """查询指定属性的【加算】总和"""
        total = 0.0
        if attribute_name in self._effects:
            for effect in self._effects[attribute_name]:
                if effect.enable and effect.calc_mode == "add":
                    total += effect.value
        return total

    def query_total_mul(self, attribute_name: str) -> float:
        """查询指定属性的【乘算】总和"""
        total = 0.0
        if attribute_name in self._effects:
            for effect in self._effects[attribute_name]:
                if effect.enable and effect.calc_mode == "mul":
                    total += effect.value
        return total

    def query_final_multipliers(self, attribute_name: str) -> float:
        """查询指定属性的【最终独立乘算】总倍率"""
        multiplier = 1.0
        if attribute_name in self._effects:
            for effect in self._effects[attribute_name]:
                if effect.enable and effect.calc_mode == "final_mul":
                    multiplier *= 1.0 + effect.value
        return multiplier

    def get_all_modifiers(self) -> Dict[str, float]:
        """(Debug用) 获取当前所有生效属性的汇总值"""
        result = defaultdict(float)
        for attr, effects in self._effects.items():
            for effect in effects:
                if effect.enable:
                    result[attr] += effect.value
        return dict(result)
