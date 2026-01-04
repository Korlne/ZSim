from typing import TYPE_CHECKING

from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.zsim_event_system.zsim_events.skill_event import SkillExecutionEvent

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events.base_zsim_event import (
        BaseZSimEventContext,
        ZSimEventABC,
    )

# 对应配置文件中的 BuffName
LOGIC_ID = "Buff-角色-柳-6画-特殊技伤害提升"


@BuffCallbackRepository.register(LOGIC_ID)
def yanagi_cinema6_ex_dmg_bonus(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    柳的6画，森罗万象激活时，Buff状态置为Active。
    """
    # 仅在技能执行时检查（足以覆盖伤害计算前的状态判定）
    if not isinstance(event, SkillExecutionEvent):
        return

    char = buff.owner
    # 确保宿主是柳且拥有架势管理器
    if not hasattr(char, "stance_manager"):
        return

    # 访问森罗万象状态 (property，内部依赖 sim_instance.tick)
    # 如果处于森罗万象状态，则 buff 激活
    is_active = char.stance_manager.shinrabanshou.active

    # 更新 Buff 状态
    if buff.dy.active != is_active:
        buff.dy.active = is_active
