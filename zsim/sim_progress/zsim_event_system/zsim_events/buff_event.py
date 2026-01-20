from typing import TYPE_CHECKING, Literal

from ....define import ZSimEventTypes
from .base_zsim_event import EventMessage, ZSimBaseEvent

if TYPE_CHECKING:
    from ...Buff import Buff

# 定义 Buff 的生命周期类型
# start: 获得, end: 移除, refresh: 刷新持续时间, stack_change: 层数变化, expire: 自然过期，periodic_tick：周期性效果
BuffLifecycleType = Literal["start", "end", "refresh", "stack_change", "expire", "periodic_tick"]


class BuffEventMessage(EventMessage):
    """Buff 相关事件的数据载荷"""

    buff_id: str
    lifecycle_type: BuffLifecycleType
    current_stacks: int = 0
    duration_remaining: int = 0
    delta_stacks: int = 0  # 层数变化量 (例如: +1, -1)


class BuffLifecycleEvent(ZSimBaseEvent[BuffEventMessage]):
    """
    Buff 生命周期事件。
    当 Buff 状态发生改变（获得、丢失、层数变化）时发出。
    """

    def __init__(
        self,
        event_message: BuffEventMessage,
        event_origin: "Buff",
    ):
        super().__init__(
            event_type=ZSimEventTypes.BUFF_EVENT,
            event_message=event_message,
            event_origin=event_origin,
        )

    @property
    def buff_instance(self) -> "Buff":
        return self.event_origin


class PeriodicBuffTickEvent(ZSimBaseEvent[BuffEventMessage]):
    """
    Buff 周期性 Tick 事件。
    用于处理如 Dot (Damage over Time) 或周期性回复等效果。
    """

    def __init__(
        self,
        event_message: BuffEventMessage,
        event_origin: "Buff",
        execute_tick: int,
    ):
        self.execute_tick = execute_tick
        super().__init__(
            event_type=ZSimEventTypes.BUFF_EVENT,  # 复用 BUFF_EVENT 类型或定义新的 TICK 类型
            event_message=event_message,
            event_origin=event_origin,
        )

    @property
    def buff_instance(self) -> "Buff":
        return self.event_origin