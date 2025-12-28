from typing import TYPE_CHECKING

from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

LOGIC_ID = "Branch_Blade_Song_Crit_Rate_Bonus"


@BuffCallbackRepository.register(LOGIC_ID)
def branch_blade_song_crit_rate_bonus(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    折枝剑歌 - 暴击率加成
    逻辑：
        检测当前敌人的冻结状态(Frozen)。
        只要处于冻结状态（或碎冰窗口期，具体由 enemy.frozen 定义），则激活 Buff。
    """
    sim = buff.sim_instance

    # 1. 获取当前敌人
    enemy = sim.ctx.current_enemy
    if not enemy:
        return

    # 2. 获取冻结状态
    # 假设 enemy.dynamic.frozen 是一个布尔值或状态对象
    # 根据旧代码：enemy.dynamic.frozen is None -> False
    is_frozen = False
    if hasattr(enemy, "dynamic") and hasattr(enemy.dynamic, "frozen"):
        is_frozen = bool(enemy.dynamic.frozen)

    # 3. 状态同步
    # 优化：仅在状态改变时调用 start/end
    if is_frozen:
        if not buff.dy.active:
            buff.start(current_tick=sim.tick)
    else:
        if buff.dy.active:
            buff.end(current_tick=sim.tick)
