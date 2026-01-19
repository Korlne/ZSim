from typing import TYPE_CHECKING

from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.zsim_event_system.zsim_events.skill_event import SkillExecutionEvent

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events.base_zsim_event import (
        BaseZSimEventContext,
        ZSimEventABC,
    )

LOGIC_ID = "Buff-角色-柳-架势-上弦"


@BuffCallbackRepository.register(LOGIC_ID)
def yanagi_stance_jougen(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    柳的上弦增幅，检测到上弦状态就激活 Buff。
    """
    if not isinstance(event, SkillExecutionEvent):
        return

    char = buff.owner
    if not hasattr(char, "stance_manager"):
        return

    # stance_now: True 为上弦, False 为下弦
    is_jougen = char.stance_manager.stance_now

    if buff.dy.active != is_jougen:
        buff.dy.active = is_jougen
