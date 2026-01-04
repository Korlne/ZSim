from typing import List, Optional, Set, Type, TypeVar

from .zsim_events.base_zsim_event import ZSimEventABC

# 定义泛型 T，必须是 ZSimEventABC 的子类
T = TypeVar("T", bound=ZSimEventABC)


class EventProfile:
    """
    事件配置/上下文快照 (Event Profile)。

    它封装了在特定时刻或特定动作中发生的一组事件。
    Handler 接收此对象，而不是单个原始事件，以便查询当前上下文中是否存在特定类型的事件。
    """

    def __init__(self, events: List[ZSimEventABC] = None):
        self._events: List[ZSimEventABC] = events or []
        # 缓存字典，用于按类型快速查找事件
        self._event_type_map: dict[Type[ZSimEventABC], List[ZSimEventABC]] = {}
        self._tags: Set[str] = set()

    def add_event(self, event: ZSimEventABC) -> None:
        """向 Profile 中添加一个事件。"""
        self._events.append(event)
        # 更新类型缓存
        event_cls = type(event)
        if event_cls not in self._event_type_map:
            self._event_type_map[event_cls] = []
        self._event_type_map[event_cls].append(event)
        # TODO: 这里可以根据 event 的属性更新 self._tags

    def get_events_by_type(self, event_type: Type[T]) -> List[T]:
        """
        获取指定类型（或其子类）的所有事件。
        """
        # 简单实现：遍历所有事件（由于事件数量通常很少，性能影响可控）
        # 优化实现：如果需要极致性能，可以利用 _event_type_map
        result = []
        for e in self._events:
            if isinstance(e, event_type):
                result.append(e)
        return result

    def get_first_event_by_type(self, event_type: Type[T]) -> Optional[T]:
        """
        获取指定类型的第一个事件。
        通常用于我们知道上下文中只有一个主事件（如：主要技能事件）的情况。
        """
        for e in self._events:
            if isinstance(e, event_type):
                return e
        return None

    @property
    def all_events(self) -> List[ZSimEventABC]:
        """返回所有事件的列表"""
        return self._events

    def __repr__(self) -> str:
        return f"<EventProfile events={len(self._events)} types={[type(e).__name__ for e in self._events]}>"
