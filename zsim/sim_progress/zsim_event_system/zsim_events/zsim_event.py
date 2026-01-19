from dataclasses import dataclass
from typing import Any

from ....define import ZSimEventTypes


@dataclass(frozen=True)
class ZSimEvent:
    """
    统一事件包装器
    用于将外部复杂对象封装为统一事件类型，屏蔽底层对象差异。
    """

    event_type: ZSimEventTypes | str
    event_obj: Any
