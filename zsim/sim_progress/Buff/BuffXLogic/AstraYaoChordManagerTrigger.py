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

LOGIC_ID = "Buff-角色-耀佳音-震音管理器-触发器"


def get_skill_node(event: "ZSimEventABC"):
    if hasattr(event, "event_origin") and isinstance(event.event_origin, SkillNode):
        return event.event_origin
    return None


@BuffCallbackRepository.register(LOGIC_ID)
def astra_yao_chord_manager_trigger(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    耀嘉音震音管理器触发器。
    筛选特定技能（trigger_buff_level in [5, 7, 8] 且 时间匹配），触发协同攻击。
    """
    if not isinstance(event, SkillExecutionEvent):
        return

    skill_node = get_skill_node(event)
    if not skill_node:
        return

    # 筛选条件
    trigger_level = getattr(skill_node.skill, "trigger_buff_level", -1)
    if trigger_level in [5, 7, 8]:
        # 必须是预设的触发时间点
        current_tick = context.timer.tick
        if current_tick == skill_node.preload_tick:
            char = buff.owner
            if hasattr(char, "chord_manager"):
                # 触发协同攻击
                char.chord_manager.chord_trigger.try_spawn_chord_coattack(
                    current_tick, skill_node=skill_node
                )
