from typing import TYPE_CHECKING

from zsim.define import ASTRAYAO_REPORT
from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.Preload import SkillNode

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

# 逻辑ID
LOGIC_ID = "Astra_Yao_Chord_Manager_Trigger"


@BuffCallbackRepository.register(LOGIC_ID)
def astra_yao_chord_manager_trigger(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    耀嘉音 - 震音管理器触发器
    逻辑：
        监听技能开始(SkillStart)，若技能符合 trigger_buff_level 要求，
        调用 AstraYao.chord_manager.chord_trigger.try_spawn_chord_coattack。
    """
    sim = buff.sim_instance

    # 1. 获取事件源
    if not hasattr(event, "event_origin") or not isinstance(event.event_origin, SkillNode):
        return
    skill_node = event.event_origin

    # 2. 筛选条件
    # 只有特定 trigger_buff_level 的技能可以触发协同
    if skill_node.skill.trigger_buff_level not in [5, 7, 8]:
        return

    # 3. 获取角色对象 (耀嘉音)
    astra_char = sim.char_data.find_char_obj(CID=1311)
    if not astra_char:
        return

    # 4. 执行逻辑
    # 尝试生成震音协同
    # 注意：原逻辑区分了 judge 和 start，这里直接在 Start 事件中执行
    astra_char.chord_manager.chord_trigger.try_spawn_chord_coattack(
        current_tick=sim.tick,
        skill_node=skill_node,
    )

    if ASTRAYAO_REPORT:
        sim.schedule_data.change_process_state()
        print(f"检测到入场动作{skill_node.skill_tag}，尝试调用震音管理器，触发协同攻击！")
