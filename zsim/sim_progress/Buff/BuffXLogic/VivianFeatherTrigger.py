from typing import TYPE_CHECKING

from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.Preload import SkillNode
from zsim.sim_progress.zsim_event_system.zsim_events.skill_event import SkillExecutionEvent

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events.base_zsim_event import (
        BaseZSimEventContext,
        ZSimEventABC,
    )

LOGIC_ID = "Buff-角色-薇薇安-羽毛获取"


@BuffCallbackRepository.register(LOGIC_ID)
def vivian_feather_trigger(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    薇薇安羽毛更新触发器。
    在薇薇安技能最后一跳时更新羽毛。
    """
    if not isinstance(event, SkillExecutionEvent):
        return

    skill_node = getattr(event, "event_origin", None)
    if not isinstance(skill_node, SkillNode):
        return

    # 1. 必须是薇薇安的技能
    if "1331" not in skill_node.skill_tag:
        return

    # 2. 必须是最后一跳
    tick = context.timer.tick
    if not skill_node.loading_mission.is_last_hit(tick):
        return

    # 3. 更新羽毛
    char = buff.owner
    if hasattr(char, "feather_manager"):
        char.feather_manager.update_myself(skill_node=skill_node)
