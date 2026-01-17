from typing import Iterable, Protocol

from .zsim_events import EventProfile, ZSimEvent


class EventHandler(Protocol):
    """事件处理器协议"""

    def execute(self, event: ZSimEvent, profile: EventProfile) -> Iterable[ZSimEvent]:
        """执行事件处理逻辑并返回新事件"""
        ...


class EventTriggerTree(Protocol):
    """事件触发器树协议"""

    def match(self, profile: EventProfile) -> Iterable[str]:
        """根据事件画像返回需要触发的事件类型集合"""
        ...


class EventRouter:
    """事件路由中枢，负责分发事件并驱动处理器"""

    def __init__(
        self,
        handler_map: dict[str, EventHandler] | None = None,
        event_trigger_tree: EventTriggerTree | None = None,
    ) -> None:
        self._handler_map: dict[str, EventHandler] = handler_map or {}
        self._event_trigger_tree = event_trigger_tree
        self._active_event_list: list[ZSimEvent] = []

    @property
    def active_event_list(self) -> list[ZSimEvent]:
        """返回当前动态事件列表"""
        return list(self._active_event_list)

    def register_handler(self, event_type: str, handler: EventHandler) -> None:
        """注册事件处理器"""
        self._handler_map[event_type] = handler

    def publish(self, event: ZSimEvent) -> list[ZSimEvent]:
        """发布事件并驱动所有匹配的处理器"""
        profile = EventProfile([event])
        produced_events: list[ZSimEvent] = []

        for handler_key in self._resolve_handlers(event, profile):
            handler = self._handler_map.get(handler_key)
            if handler is None:
                continue
            produced_events.extend(list(handler.execute(event, profile)))

        return produced_events

    def _resolve_handlers(self, event: ZSimEvent, profile: EventProfile) -> list[str]:
        """根据事件类型和触发器树解析处理器列表"""
        handler_keys = [str(event.event_type)]
        if self._event_trigger_tree is not None:
            handler_keys.extend(list(self._event_trigger_tree.match(profile)))
        return list(dict.fromkeys(handler_keys))
