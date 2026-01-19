from abc import ABC, abstractmethod
from typing import Any, Dict, List
from .trigger_context import TriggerContext

# --- 抽象基类 ---
class BaseAction(ABC):
    @abstractmethod
    def execute(self, context: TriggerContext) -> None:
        pass

# --- 具体实现 ---

class AddStackAction(BaseAction):
    """增加 Buff 层数"""
    def __init__(self, stacks: int = 1):
        self.add_count = stacks

    def execute(self, context: TriggerContext) -> None:
        if context.buff_instance:
            context.buff_instance.add_stack(self.add_count)
            print(f"[Action] Buff {context.buff_instance.feature.name} 层数增加 {self.add_count}")

class RefreshDurationAction(BaseAction):
    """刷新 Buff 持续时间"""
    def execute(self, context: TriggerContext) -> None:
        if context.buff_instance:
            context.buff_instance.refresh()
            print(f"[Action] Buff {context.buff_instance.feature.name} 时间已刷新")

class ModifyAttributeAction(BaseAction):
    """
    修改属性 (非 Bonus 系统的临时修改，或永久叠加)
    注意：Buff 系统的常驻加成通常由 BonusEffect 处理，这里处理的是"触发式"修改
    """
    def __init__(self, target_key: str, value: float, mode: str = "add"):
        self.target_key = target_key
        self.value = value
        self.mode = mode # add / mult / set

    def execute(self, context: TriggerContext) -> None:
        char = context.source
        if not hasattr(char, self.target_key):
            return
        
        old_val = getattr(char, self.target_key)
        new_val = old_val
        
        if self.mode == "add":
            new_val += self.value
        elif self.mode == "mult":
            new_val *= self.value
        
        setattr(char, self.target_key, new_val)
        print(f"[Action] 修改属性 {self.target_key}: {old_val} -> {new_val}")

class TriggerDamageAction(BaseAction):
    """触发一次额外伤害 (如: 强击)"""
    def __init__(self, multiplier: float, dmg_type: str = "Physical"):
        self.multiplier = multiplier
        self.dmg_type = dmg_type

    def execute(self, context: TriggerContext) -> None:
        # 这里需要调用伤害计算模块，暂时打印
        print(f"[Action] 触发额外伤害: 倍率 {self.multiplier}, 类型 {self.dmg_type}")

# --- 工厂类 ---
class ActionFactory:
    """将配置列表转换为行为对象列表"""
    
    _FUNC_MAP = {
        "add_stack": AddStackAction,
        "refresh": RefreshDurationAction,
        "modify_attr": ModifyAttributeAction,
        "trigger_damage": TriggerDamageAction
    }

    @classmethod
    def create_actions(cls, actions_data: List[Dict[str, Any]]) -> List[BaseAction]:
        actions = []
        if not actions_data:
            return actions

        for item in actions_data:
            func_name = item.get("func")
            args = item.get("args", {})
            
            if func_name in cls._FUNC_MAP:
                action_cls = cls._FUNC_MAP[func_name]
                try:
                    if isinstance(args, dict):
                        actions.append(action_cls(**args))
                    else:
                        #无参情况
                        actions.append(action_cls())
                except TypeError as e:
                    print(f"[ActionFactory] ❌ 创建行为 {func_name} 失败，参数错误: {e}")
            else:
                print(f"[ActionFactory] ⚠️ 未知行为 func: {func_name}")
        
        return actions