from typing import TYPE_CHECKING, Literal, Dict, Any
from pydantic import Field

from ....define import ZSimEventTypes
from .base_zsim_event import EventMessage, ZSimBaseEvent

if TYPE_CHECKING:
    from ...anomaly_bar import AnomalyBar
    from ...Buff.buff_model import Buff 


class AnomalyEventMessage(EventMessage):
    """异常积蓄/状态相关事件的数据载荷"""
    attribute_type: str
    trigger_type: Literal["buildup", "trigger", "end"]
    value: float


class AnomalyEvent(ZSimBaseEvent[AnomalyEventMessage]):
    """异常事件（积蓄变化、状态触发）"""
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


# ================= Dot 结算相关事件 =================

class DotDamageEventMessage(EventMessage):
    """
    Dot 伤害结算事件载荷。
    包含了计算一次 Dot 伤害所需的所有“快照”信息。
    """
    dot_type: str             # 类型标识: "burn", "shock", "corruption", etc.
    damage_base: float        # 施加时的基准伤害值 (Snapshot)
    element_type: str         # 伤害属性: "fire", "electric", etc.
    source_character_id: str  # 来源角色 ID
    
    trigger_reason: Literal["periodic_tick", "passive_trigger", "disorder"] # 触发原因
    
    # 属性快照：记录施加时的穿透率、属性伤加成等关键属性
    attribute_snapshot: Dict[str, float] = Field(default_factory=dict)
    
    # 额外参数：用于传递特殊的乘区修正或机制标记
    extra_params: Dict[str, Any] = Field(default_factory=dict)


class DotDamageEvent(ZSimBaseEvent[DotDamageEventMessage]):
    """
    Dot 伤害事件。
    当 DotEffect 执行（周期性 Tick 或被动触发）时产生此事件。
    随后由 Schedule 系统中的 Handler 捕获并进行最终伤害计算与 Report。
    """
    def __init__(
        self,
        event_message: DotDamageEventMessage,
        event_origin: Any, # 通常为对应的 Buff 实例
    ):
        # 仍然归类为 ANOMALY_EVENT，或者可以在 define.py 定义新的 DOT_EVENT
        super().__init__(
            event_type=ZSimEventTypes.ANOMALY_EVENT, 
            event_message=event_message,
            event_origin=event_origin,
        )