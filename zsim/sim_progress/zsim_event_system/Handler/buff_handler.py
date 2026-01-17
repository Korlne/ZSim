from dataclasses import dataclass
from typing import Iterable

from ....define import ZSimEventTypes
from ...Buff.buff_manager import BuffManager
from ...Buff.buff_model import Buff
from ..event_router import EventHandler
from ..zsim_events import EventProfile, ZSimEvent


@dataclass(frozen=True)
class BuffEventPayload:
    """Buff 事件载荷"""

    buff: Buff
    timestamp: int
    action: str
    duration: int | None = None
    stacks: int = 0


class BuffEventHandler(EventHandler):
    """Buff 事件处理器"""

    def __init__(self, buff_manager: BuffManager) -> None:
        self._buff_manager = buff_manager

    def execute(self, event: ZSimEvent, profile: EventProfile) -> Iterable[ZSimEvent]:
        """执行 Buff 事件逻辑"""
        if str(event.event_type) != str(ZSimEventTypes.BUFF_EVENT):
            return []

        payload = event.event_obj
        if not isinstance(payload, BuffEventPayload):
            return []

        if payload.action == "add":
            self._buff_manager.add_buff(
                payload.buff, payload.timestamp, payload.duration, payload.stacks
            )
        elif payload.action == "remove":
            self._buff_manager.remove_buff(payload.buff.ft.buff_id, payload.timestamp)
        elif payload.action == "refresh":
            self._buff_manager.add_buff(
                payload.buff, payload.timestamp, payload.duration, payload.stacks
            )

        return []
