from typing import TYPE_CHECKING, Literal

from ....define import ZSimEventTypes
from .base_zsim_event import EventMessage, ZSimBaseEvent

if TYPE_CHECKING:
    from ...anomaly_bar import AnomalyBar


class AnomalyEventMessage(EventMessage):
    """异常积蓄/状态相关事件的数据载荷"""

    attribute_type: str  # 例如: "Fire", "Ice", "Physical"
    trigger_type: Literal[
        "buildup", "trigger", "end"
    ]  # buildup: 积蓄增加, trigger: 异常触发, end: 异常结束
    value: float  # 积蓄值 或 伤害值


class AnomalyEvent(ZSimBaseEvent[AnomalyEventMessage]):
    """
    异常事件。
    当异常槽积蓄变化或异常状态触发时发出。
    """

    def __init__(
        self,
        event_message: AnomalyEventMessage,
        event_origin: "AnomalyBar",
    ):
        super().__init__(
            event_type=ZSimEventTypes.ANOMALY_EVENT,
            event_message=event_message,
            event_origin=event_origin,
        )
