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
    """

    def __init__(self, owner: "Character"):
        self.owner = owner
        # 存储结构: { "攻击力%": [Effect1, Effect2], "火属性伤害提升": [...] }
        self._effects: Dict[str, List[BonusEffect]] = defaultdict(list)

    def add_effect(self, effect: BonusEffect):
        """注册一个效果"""
        self._effects[effect.target_attribute].append(effect)

    def remove_effect(self, effect: BonusEffect):
        """移除一个效果"""
        attr = effect.target_attribute
        if attr in self._effects:
            try:
                self._effects[attr].remove(effect)
                # 如果列表为空，清理 key，保持字典整洁
                if not self._effects[attr]:
                    del self._effects[attr]
            except ValueError:
                pass

    def query_total_add(self, attribute_name: str) -> float:
        """
        查询指定属性的【加算】总和 (calc_mode='add')。
        例如：查询 '攻击力%' 的所有 Buff 加成总和。
        """
        total = 0.0
        if attribute_name in self._effects:
            for effect in self._effects[attribute_name]:
                if effect.enable and effect.calc_mode == "add":
                    total += effect.value
        return total

    def query_total_mul(self, attribute_name: str) -> float:
        """
        查询指定属性的【乘算】总和 (calc_mode='mul')。
        通常用于‘伤害提升’区间，公式为 (1 + sum(mul_effects))。
        注意：ZSim 的定义中，'区间乘算'通常也是加在区间内的，所以也是累加。
        如果遇到真正的‘独立乘算’，请使用 query_final_multipliers。
        """
        # 在 ZZZ 模型中，大多数 "乘区" (如增伤区) 内部是加算的
        # 所以这里我们返回累加值，由调用者决定是否 +1
        total = 0.0
        if attribute_name in self._effects:
            for effect in self._effects[attribute_name]:
                if effect.enable and effect.calc_mode == "mul":
                    total += effect.value
        return total

    def query_final_multipliers(self, attribute_name: str) -> float:
        """
        查询指定属性的【最终独立乘算】总倍率 (calc_mode='final_mul')。
        公式：Product(1 + value)
        """
        multiplier = 1.0
        if attribute_name in self._effects:
            for effect in self._effects[attribute_name]:
                if effect.enable and effect.calc_mode == "final_mul":
                    multiplier *= 1.0 + effect.value
        return multiplier

    def get_all_modifiers(self) -> Dict[str, float]:
        """
        (Debug用) 获取当前所有生效属性的汇总值 (简化视图)。
        仅做简单累加，不区分乘区逻辑。
        """
        result = defaultdict(float)
        for attr, effects in self._effects.items():
            for effect in effects:
                if effect.enable:
                    result[attr] += effect.value
        return dict(result)
