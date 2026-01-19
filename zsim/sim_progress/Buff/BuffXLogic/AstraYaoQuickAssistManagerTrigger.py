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

LOGIC_ID = "Buff-角色-耀佳音-快支管理器-触发器"


def get_skill_node(event: "ZSimEventABC"):
    """辅助函数：提取 SkillNode"""
    if hasattr(event, "event_origin") and isinstance(event.event_origin, SkillNode):
        return event.event_origin
    # 部分事件结构可能不同，需根据实际情况适配
    return getattr(event, "event_origin", None)


@BuffCallbackRepository.register(LOGIC_ID)
def astra_yao_quick_assist_manager_trigger(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    耀嘉音快支管理器触发器。
    监听到技能执行后，将事件转发给 chord_manager 进行处理。
    """
    if not isinstance(event, SkillExecutionEvent):
        return

    skill_node = get_skill_node(event)
    if not skill_node:
        return

    char = buff.owner
    if hasattr(char, "chord_manager"):
        # 调用 Manager 的 update_myself 方法
        # 注意：Manager 方法签名可能需要适配 context.timer.tick
        char.chord_manager.quick_assist_trigger_manager.update_myself(
            context.timer.tick, skill_node
        )
