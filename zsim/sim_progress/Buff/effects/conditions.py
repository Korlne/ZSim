from abc import ABC, abstractmethod
from typing import Any, Dict, List
from .trigger_context import TriggerContext

# --- 抽象基类 ---
class BaseCondition(ABC):
    @abstractmethod
    def check(self, context: TriggerContext) -> bool:
        """返回 True 表示条件满足"""
        pass

# --- 具体实现 ---

class MinStackCondition(BaseCondition):
    """检测 Buff 层数是否 >= X"""
    def __init__(self, min_stacks: int):
        self.min_stacks = min_stacks

    def check(self, context: TriggerContext) -> bool:
        if not context.buff_instance:
            return False
        return context.buff_instance.current_stacks >= self.min_stacks

class SkillTypeCondition(BaseCondition):
    """检测触发事件的技能类型 (如 NormalAttack, Dodge)"""
    def __init__(self, skill_type: str):
        self.skill_type = skill_type.lower()

    def check(self, context: TriggerContext) -> bool:
        if not context.event:
            return False
        # 假设事件对象有 skill_type 属性
        event_type = getattr(context.event, "skill_type", "").lower()
        return event_type == self.skill_type

class ElementTypeCondition(BaseCondition):
    """检测触发事件的元素类型"""
    def __init__(self, element: str):
        self.element = element.lower()

    def check(self, context: TriggerContext) -> bool:
        if not context.event:
            return False
        event_elem = getattr(context.event, "element_type", "").lower()
        return event_elem == self.element

class ProbabilityCondition(BaseCondition):
    """概率触发 (0.0 - 1.0)"""
    def __init__(self, probability: float):
        self.p = probability

    def check(self, context: TriggerContext) -> bool:
        import random
        return random.random() < self.p

# --- 工厂类 ---
class ConditionFactory:
    """将配置字典转换为条件对象列表 (Implicit AND)"""
    
    # 映射表: JSON Key -> Condition Class
    _KEY_MAP = {
        "min_stacks": MinStackCondition,
        "skill_type": SkillTypeCondition,
        "element": ElementTypeCondition,
        "probability": ProbabilityCondition,
        "chance": ProbabilityCondition, # 别名
    }

    @classmethod
    def create_conditions(cls, config: Dict[str, Any]) -> List[BaseCondition]:
        conditions = []
        if not config:
            return conditions

        for key, value in config.items():
            if key in cls._KEY_MAP:
                condition_cls = cls._KEY_MAP[key]
                conditions.append(condition_cls(value))
            # 处理自定义复杂逻辑 (Task 2.1 提到的 custom_id)
            elif key == "custom_id":
                # TODO: 从 CustomRegistry 获取
                pass
            else:
                print(f"[ConditionFactory] ⚠️ 未知条件 Key: {key}")
        
        return conditions