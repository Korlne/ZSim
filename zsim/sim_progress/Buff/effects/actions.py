from abc import ABC, abstractmethod
from typing import Any, Dict, List
from .trigger_context import TriggerContext

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable, Any, Dict, List, Optional

from zsim.sim_progress.zsim_event_system.zsim_events.anomaly_event import (
    DotDamageEvent, 
    DotDamageEventMessage
)
from zsim.sim_progress.zsim_event_system.zsim_events.buff_event import PeriodicBuffTickEvent

if TYPE_CHECKING:
    from zsim.sim_progress.zsim_event_system.event_profile import EventProfile
    from zsim.sim_progress.Buff.effects.dot_effect import AnomalySnapshot

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
    """修改属性 (触发式修改)"""
    def __init__(self, target_key: str, value: float, mode: str = "add"):
        self.target_key = target_key
        self.value = value
        self.mode = mode 

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
        print(f"[Action] 触发额外伤害: 倍率 {self.multiplier}, 类型 {self.dmg_type}")

@dataclass
class DealDotDamageAction:
    """
    [Action] 执行 Dot 伤害
    职责：读取异常快照 (Snapshot)，构造并发出 DotDamageEvent。
    """
    snapshot: "AnomalySnapshot"
    dot_type: str
    damage_multiplier: float = 1.0
    source_buff_id: int = 0  # 用于校验 Tick 是否属于当前 Buff

    def execute(self, profile: "EventProfile") -> Iterable[object]:
        """
        执行行为：生成 Dot 伤害事件
        """
        trigger_reason = "passive_trigger"
        
        # 1. 校验触发源
        # 如果是周期性 Tick 事件，必须确保事件源是同一个 Buff 实例
        if isinstance(profile.event_origin, PeriodicBuffTickEvent):
            tick_event: PeriodicBuffTickEvent = profile.event_origin
            if str(tick_event.buff_instance.ft.buff_id) == str(self.source_buff_id):
                trigger_reason = "periodic_tick"
            else:
                # 不是本 Buff 的 Tick，不产生伤害 (例如：其他 Buff 的 Tick 触发了某种全局监听，但不应触发此伤害)
                return []
        
        # 2. 构造事件载荷
        # 使用初始化时注入的 snapshot 数据
        event_msg = DotDamageEventMessage(
            dot_type=self.dot_type,
            damage_base=self.snapshot.damage_base * self.damage_multiplier,
            element_type=self.snapshot.element_type,
            source_character_id=self.snapshot.source_character_id,
            attribute_snapshot=self.snapshot.attribute_snapshot.copy(),
            trigger_reason=trigger_reason,
            extra_params=self.snapshot.extra_params.copy()
        )

        # 3. 确定事件发起者 (Origin)
        # 尽量回溯到 Buff 实例
        origin = None
        if hasattr(profile.event_origin, "buff_instance"):
            origin = profile.event_origin.buff_instance
        elif hasattr(profile, "event_origin"):
            origin = profile.event_origin

        dot_event = DotDamageEvent(
            event_message=event_msg,
            event_origin=origin
        )

        return [dot_event]

# --- 工厂类 ---
class ActionFactory:
    """将配置列表转换为行为对象列表"""
    
    _FUNC_MAP = {
        "add_stack": AddStackAction,
        "refresh": RefreshDurationAction,
        "modify_attr": ModifyAttributeAction,
        "trigger_damage": TriggerDamageAction,
        "deal_anomaly_damage": DealDotDamageAction, # 注册新行为
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
                        actions.append(action_cls())
                except TypeError as e:
                    print(f"[ActionFactory] ❌ 创建行为 {func_name} 失败，参数错误: {e}")
            else:
                print(f"[ActionFactory] ⚠️ 未知行为 func: {func_name}")
        
        return actions