from typing import Any, Iterable

from .zsim_event import ZSimEvent


class EventProfile:
    """事件画像，封装事件组并提供统一查询接口"""

    def __init__(self, event_group: Iterable[ZSimEvent]):
        self._event_group: list[ZSimEvent] = list(event_group)

    @property
    def event_group(self) -> list[ZSimEvent]:
        """返回事件组快照"""
        return list(self._event_group)

    def primary_event(self) -> ZSimEvent | None:
        """获取事件组中的主事件（默认第一个）"""
        return self._event_group[0] if self._event_group else None

    def has_event_type(self, event_type: str) -> bool:
        """检查事件组中是否存在指定类型的事件"""
        return any(str(event.event_type) == event_type for event in self._event_group)

    def get_attr(self, name: str, default: Any = None) -> Any:
        """从事件对象中获取指定属性，找不到则返回默认值"""
        for event in self._event_group:
            if hasattr(event.event_obj, name):
                return getattr(event.event_obj, name)
        return default
