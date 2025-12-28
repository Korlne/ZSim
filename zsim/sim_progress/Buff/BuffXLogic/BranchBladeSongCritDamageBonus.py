from typing import TYPE_CHECKING

from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.Preload import SkillNode

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

# Logic ID
LOGIC_ID = "Branch_Blade_Song_Crit_Damage_Bonus"


@BuffCallbackRepository.register(LOGIC_ID)
def branch_blade_song_crit_damage_bonus(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    折枝剑歌 - 爆伤加成 (新冰套)
    逻辑：
        检测角色实时异常掌控(AM)。
        如果 AM >= 115，则激活 Buff。
        由于无法实现"AM>=115时永久激活"，因此在每次技能开始时(SkillStart)进行检测。
    """
    sim = buff.sim_instance
    owner = buff.owner

    if not owner:
        return

    # 1. 仅在技能开始或Buff刷新时检测
    # 这里选择 SkillStart 以确保战斗中实时性
    is_check_timing = False
    if hasattr(event, "event_origin") and isinstance(event.event_origin, SkillNode):
        is_check_timing = True
    # 也可以在 BuffStart 时做一次初始检测
    if event.event_type == "BuffStart":
        is_check_timing = True

    if not is_check_timing:
        return

    # 2. 获取实时属性 (AM)
    current_am = getattr(owner.statement, "AM", 0)

    # 3. 判定与状态同步
    if current_am >= 115:
        if not buff.dy.active:
            buff.start(current_tick=sim.tick)
    else:
        if buff.dy.active:
            buff.end(current_tick=sim.tick)
