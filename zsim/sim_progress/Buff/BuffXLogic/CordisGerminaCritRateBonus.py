from typing import TYPE_CHECKING

from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.Preload import SkillNode

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

LOGIC_ID = "Cordis_Germina_Ele_Dmg_Bonus"


@BuffCallbackRepository.register(LOGIC_ID)
def cordis_germina_ele_dmg_bonus(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    机巧心种 - 属性伤害/攻击加成触发
    逻辑：
        监听 SkillHit。
        如果技能是 普攻(0) 或 强化特殊技(2)，则触发。
    """
    sim = buff.sim_instance
    owner = buff.owner

    if not owner:
        return

    # 1. 验证事件
    if not hasattr(event, "event_origin") or not isinstance(event.event_origin, SkillNode):
        return
    skill_node = event.event_origin

    if skill_node.char_name != owner.NAME:
        return

    # 2. 筛选技能类型
    # trigger_buff_level: 0=NA, 2=ExSpecial (假设映射关系)
    if skill_node.skill.trigger_buff_level not in [0, 2]:
        return

    # 3. 必须是命中帧
    if not skill_node.is_hit_now(tick=sim.tick):
        return

    # 4. 激活 Buff
    buff.start(current_tick=sim.tick)
