from typing import TYPE_CHECKING, Literal

from ....define import ZSimEventTypes
from .base_zsim_event import EventMessage, ZSimBaseEvent

if TYPE_CHECKING:
    from ...Buff import Buff

# 定义 Buff 的生命周期类型
# start: 获得, end: 移除, refresh: 刷新持续时间, stack_change: 层数变化, expire: 自然过期
BuffLifecycleType = Literal["start", "end", "refresh", "stack_change", "expire"]


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
        # 假设 ZSimEventTypes.BUFF_EVENT 已在 define.py 中定义
        # 如果没有，需要在 Phase 1 将其添加到 Enum 中
        super().__init__(
            event_type=ZSimEventTypes.BUFF_EVENT,
            event_message=event_message,
            event_origin=event_origin,
        )

    @property
    def buff_instance(self) -> "Buff":
        return self.event_origin
