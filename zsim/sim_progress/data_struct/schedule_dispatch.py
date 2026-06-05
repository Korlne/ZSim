from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Iterable, MutableSequence

if TYPE_CHECKING:
    from zsim.simulator.dataclasses import ScheduleData
    from zsim.simulator.simulator_class import Simulator


class ScheduleDispatchPort(ABC):
    """计划事件发布接口，只负责计划事件入队。"""

    @abstractmethod
    def publish_scheduled(self, event: Any) -> None:
        """发布单个计划事件。"""

    def publish_scheduled_batch(self, events: Iterable[Any]) -> None:
        """按输入顺序发布多条计划事件。"""
        for event in events:
            self.publish_scheduled(event)


class LegacyEventListScheduleDispatchAdapter(ScheduleDispatchPort):
    """旧 `event_list` 兼容适配器。"""

    def __init__(self, event_queue: MutableSequence[Any]) -> None:
        self._event_queue = event_queue

    def publish_scheduled(self, event: Any) -> None:
        # 保持旧队列的 append 语义，后续仍由调度流程负责排序和消费。
        self._event_queue.append(event)


def create_schedule_dispatch_port(
    *,
    sim_instance: "Simulator | None" = None,
    schedule_data: "ScheduleData | None" = None,
) -> ScheduleDispatchPort:
    """创建计划事件发布入口，但不向生产者暴露 raw `event_list`。"""
    if schedule_data is None:
        if sim_instance is None:
            raise ValueError("sim_instance 和 schedule_data 不能同时为空")
        schedule_data = sim_instance.schedule_data
    return LegacyEventListScheduleDispatchAdapter(schedule_data.event_list)


__all__ = [
    "LegacyEventListScheduleDispatchAdapter",
    "ScheduleDispatchPort",
    "create_schedule_dispatch_port",
]
