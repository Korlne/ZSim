from dataclasses import dataclass
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from zsim.sim_progress.Character.character import Character
    # from zsim.sim_progress.zsim_event_system.zsim_events.zsim_event import ZsimEvent

@dataclass
class TriggerContext:
    """
    触发上下文
    封装了 Buff 触发判定和执行所需的所有环境信息。
    """
    source: "Character"          # Buff 的持有者/来源
    target: Optional[Any] = None # 目标 (敌人或其他角色)
    event: Any = None            # 触发该逻辑的具体事件对象 (如 SkillHitEvent)
    state_manager: Any = None    # 全局状态管理器 (可选)
    buff_instance: Any = None    # 当前触发的 Buff 实例 (BuffDynamic)