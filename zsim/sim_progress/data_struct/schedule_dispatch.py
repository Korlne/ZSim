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


class _ScheduleQueueOwner(ABC):
    """Owns the low-level queue mutation behind schedule dispatch ports."""

    @abstractmethod
    def enqueue(self, event: Any) -> None:
        """Append one scheduled event to the owned queue."""


class _MutableScheduleQueueOwner(_ScheduleQueueOwner):
    def __init__(self, event_queue: MutableSequence[Any]) -> None:
        self._event_queue = event_queue

    def enqueue(self, event: Any) -> None:
        # Keep the raw append contained inside the queue owner.
        self._event_queue.append(event)


class _ScheduleDataQueueOwner(_ScheduleQueueOwner):
    def __init__(self, schedule_data: "ScheduleData") -> None:
        self._schedule_data = schedule_data

    @property
    def _event_queue(self) -> MutableSequence[Any]:
        return self._schedule_data.event_list

    def enqueue(self, event: Any) -> None:
        # Resolve the queue at publish time so rebinding ScheduleData.event_list is safe.
        self._event_queue.append(event)


class _QueueBackedScheduleDispatchPort(ScheduleDispatchPort):
    def __init__(self, queue_owner: _ScheduleQueueOwner) -> None:
        self._queue_owner = queue_owner

    def publish_scheduled(self, event: Any) -> None:
        self._queue_owner.enqueue(event)


class LegacyEventListScheduleDispatchAdapter(_QueueBackedScheduleDispatchPort):
    """Compatibility wrapper for legacy callers that still pass raw `event_list`.

    New production code should use `create_schedule_dispatch_port(...)`, which
    binds dispatch to `ScheduleData` and keeps queue mutation inside the queue
    owner instead of depending on a raw list append contract.
    """

    def __init__(self, event_queue: MutableSequence[Any]) -> None:
        super().__init__(_MutableScheduleQueueOwner(event_queue))


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
    return _QueueBackedScheduleDispatchPort(_ScheduleDataQueueOwner(schedule_data))


__all__ = [
    "LegacyEventListScheduleDispatchAdapter",
    "ScheduleDispatchPort",
    "create_schedule_dispatch_port",
]
