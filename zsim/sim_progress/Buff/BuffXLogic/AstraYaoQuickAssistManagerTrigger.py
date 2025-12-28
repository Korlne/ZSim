from typing import TYPE_CHECKING

from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.Preload import SkillNode

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

# 逻辑ID
LOGIC_ID = "Astra_Yao_Quick_Assist_Manager_Trigger"


@BuffCallbackRepository.register(LOGIC_ID)
def astra_yao_quick_assist_manager_trigger(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    耀嘉音 - 快支管理器触发器
    逻辑：
        监听技能命中(SkillHit)，将当前的 skill_node 传递给耀嘉音的 quick_assist_trigger_manager。
    """
    sim = buff.sim_instance

    # 1. 获取事件源 SkillNode
    if not hasattr(event, "event_origin") or not isinstance(event.event_origin, SkillNode):
        return
    skill_node = event.event_origin

    # 2. 获取角色对象 (耀嘉音)
    char = sim.char_data.find_char_obj(CID=1311)
    if not char:
        return

    # 3. 执行逻辑
    # 调用 update_myself
    char.chord_manager.quick_assist_trigger_manager.update_myself(
        current_tick=sim.tick, skill_node=skill_node
    )

    # 日志输出可根据全局配置决定
    # if ASTRAYAO_REPORT:
    #     print(f'检测到攻击动作命中，尝试调用快支管理器！')
