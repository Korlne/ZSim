"""
Dot Effect Implementation
负责处理异常状态的持续伤害逻辑与触发机制。
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, TYPE_CHECKING

from zsim.sim_progress.Buff.effects.trigger_effect import TriggerEffect, PeriodicTimerConfig
from zsim.sim_progress.Buff.effects.actions import DealDotDamageAction

if TYPE_CHECKING:
    from zsim.sim_progress.zsim_event_system.event_profile import EventProfile


@dataclass
class AnomalySnapshot:
    """
    异常快照 (Snapshot)
    职责：存储异常状态施加那一刻的面板数据。
    """
    damage_base: float = 0.0
    attribute_snapshot: Dict[str, float] = field(default_factory=dict)
    source_character_id: str = ""
    element_type: str = "physical"
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DotEffect(TriggerEffect):
    """
    Dot (Damage over Time) 效果类
    
    职责：
    1. 持有数据 (Snapshot)。
    2. 配置触发器 (Timer)。
    3. 装配行为 (Action)。
    """
    snapshot: AnomalySnapshot = field(default_factory=AnomalySnapshot)
    dot_type: str = "generic" 
    
    # [配置] 自动触发间隔
    tick_interval: float = 0.0
    
    # [配置] 动态倍率修正
    damage_multiplier: float = 1.0

    def __post_init__(self) -> None:
        """
        初始化：
        1. 配置定时器 (如果是周期性 Dot)。
        2. 自动装配 DealDotDamageAction 到 actions 列表。
        """
        # 配置定时器
        if self.tick_interval > 0:
            self.timer_config = PeriodicTimerConfig(
                interval=self.tick_interval,
                immediate=False 
            )
            # 确保父类监听 Tick 事件
            if not self.trigger_event_type:
                self.trigger_event_type = "PeriodicBuffTickEvent"

        # 将自身的 Snapshot 注入给 Action
        damage_action = DealDotDamageAction(
            snapshot=self.snapshot,
            dot_type=self.dot_type,
            damage_multiplier=self.damage_multiplier,
            source_buff_id=self.source_buff_id
        )
        self.actions.append(damage_action)

        # 调用父类初始化 (处理 effect_config 等)
        super().__post_init__()
