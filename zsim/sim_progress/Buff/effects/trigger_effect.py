from dataclasses import dataclass, field
from typing import Iterable, Optional, Protocol, TYPE_CHECKING

from .base_effect import EffectBase


class TriggerCondition(Protocol):
    """触发条件协议"""

    def evaluate(self, profile: "EventProfile") -> bool:
        """判断事件画像是否满足条件"""
        ...


class TriggerAction(Protocol):
    """触发行为协议"""

    def execute(self, profile: "EventProfile") -> Iterable[object]:
        """执行触发行为并返回产生的事件或结果"""
        ...


@dataclass
class PeriodicTimerConfig:
    """周期性触发器的配置"""
    interval: float  # 触发间隔（秒）
    immediate: bool = False  # 是否在 Buff 施加时立即触发一次


@dataclass
class TriggerEffect(EffectBase):
    """
    机制型触发效果
    仅负责承载触发条件与执行行为，不直接处理事件路由。
    """

    trigger_event_type: str
    conditions: list[TriggerCondition] = field(default_factory=list)
    actions: list[TriggerAction] = field(default_factory=list)
    source_buff_id: str = 0
    effect_config: Optional[dict] = None
    timer_config: Optional[PeriodicTimerConfig] = None  # 新增：周期性定时器配置

    def __post_init__(self) -> None:
        super().__init__(source_buff_id=self.source_buff_id, effect_config=self.effect_config)

    def apply(self, target: object) -> None:
        """触发型效果不直接作用于目标对象"""
        return None

    def should_trigger(self, profile: "EventProfile") -> bool:
        """判断是否满足所有触发条件"""
        return all(condition.evaluate(profile) for condition in self.conditions)

    def execute(self, profile: "EventProfile") -> list[object]:
        """执行触发行为并返回产物"""
        results: list[object] = []
        for action in self.actions:
            results.extend(list(action.execute(profile)))
        return results


if TYPE_CHECKING:
    from zsim.sim_progress.zsim_event_system.zsim_events.event_profile import EventProfile