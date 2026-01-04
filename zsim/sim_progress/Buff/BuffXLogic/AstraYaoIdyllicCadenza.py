from typing import TYPE_CHECKING

from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.zsim_event_system.zsim_events.skill_event import SkillExecutionEvent

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events.base_zsim_event import (
        BaseZSimEventContext,
        ZSimEventABC,
    )

LOGIC_ID = "Buff-角色-耀佳音-咏叹华彩"


@BuffCallbackRepository.register(LOGIC_ID)
def astra_yao_idyllic_cadenza(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    耀嘉音咏叹华彩状态监控。
    监听技能事件，同步 Character 实例中的 idyllic_cadenza 状态。
    """
    if not isinstance(event, SkillExecutionEvent):
        return

    char = buff.owner
    # 耀嘉音的 idyllic_cadenza 属性在 Character 类中维护
    if hasattr(char, "idyllic_cadenza"):
        is_active = char.idyllic_cadenza
        if buff.dy.active != is_active:
            buff.dy.active = is_active
