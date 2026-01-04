from typing import TYPE_CHECKING

from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.zsim_event_system.zsim_events.skill_event import SkillExecutionEvent

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events.base_zsim_event import (
        BaseZSimEventContext,
        ZSimEventABC,
    )

LOGIC_ID = "Buff-角色-柳-1画-精通增幅"
TRIGGER_BUFF_NAME = "Buff-角色-柳-1画-洞悉"


@BuffCallbackRepository.register(LOGIC_ID)
def yangi_cinema1_ap_bonus(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    柳1画的精通增幅。
    检测“洞悉”Buff的层数，若 >= 1 则激活本Buff。
    """
    if not isinstance(event, SkillExecutionEvent):
        return

    owner = buff.owner
    should_activate = False

    # 尝试获取目标 Buff
    # 假设 owner.buff_manager 提供了 get_buff 方法，或者直接访问 buff 容器
    if hasattr(owner, "buff_manager"):
        trigger_buff = owner.buff_manager.get_buff(TRIGGER_BUFF_NAME)
        if trigger_buff and trigger_buff.dy.active:
            if trigger_buff.dy.count >= 1:
                should_activate = True

    if buff.dy.active != should_activate:
        buff.dy.active = should_activate
