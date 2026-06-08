from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class TriggerBuffState:
    """触发器 Buff 的只读状态快照。"""

    active: bool
    count: int | float
    built_in_buff_box: tuple[object, ...]


def read_trigger_buff_state(record: object) -> TriggerBuffState:
    """
    从 `check_preparation(..., trigger_buff_0=...)` 已保存的旧模板 Buff 读取状态。

    该 helper 不使用 `BuffRuntimeReadPort`：P2-C 读取的是 `history.record`
    持有的旧模板 Buff 身份，和 ScheduledEvent runtime view 的 active Buff 读口分离。
    """
    trigger_buff_0 = getattr(record, "trigger_buff_0", None)
    if trigger_buff_0 is None:
        raise ValueError("record.trigger_buff_0 尚未初始化，无法读取触发器 Buff 状态")

    dynamic_state: Any = getattr(trigger_buff_0, "dy", None)
    if dynamic_state is None:
        raise ValueError("record.trigger_buff_0 缺少 dy 状态，无法读取触发器 Buff 状态")

    return TriggerBuffState(
        active=bool(dynamic_state.active),
        count=dynamic_state.count,
        built_in_buff_box=tuple(dynamic_state.built_in_buff_box),
    )
