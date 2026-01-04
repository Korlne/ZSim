from typing import TYPE_CHECKING

from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.zsim_event_system.zsim_events.skill_event import SkillExecutionEvent

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events.base_zsim_event import (
        BaseZSimEventContext,
        ZSimEventABC,
    )

LOGIC_ID = "Buff-角色-薇薇安-1画-减防"


@BuffCallbackRepository.register(LOGIC_ID)
def vivian_cinema1_debuff(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    薇薇安1画减防Buff。
    敌人身上存在【薇薇安的预言】Dot时生效。
    """
    # 使用技能执行作为检查时机，足以覆盖战斗过程
    if not isinstance(event, SkillExecutionEvent):
        return

    target = buff.owner  # 注意：此Buff通常挂在敌人身上，owner即敌人
    # 或者如果 buff 是全局/光环，需要 find_enemy。
    # 假设该 logic 挂载在 Enemy Config 中，则 owner 是 Enemy Class 实例。

    # 检查 Dot
    has_dot = False
    if hasattr(target, "find_dot"):
        if target.find_dot("ViviansProphecy"):
            has_dot = True

    # 更新 Buff 状态
    if buff.dy.active != has_dot:
        buff.dy.active = has_dot
