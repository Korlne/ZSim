from typing import TYPE_CHECKING

from zsim.define import ASTRAYAO_REPORT
from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

# 逻辑ID
LOGIC_ID = "Astra_Yao_Core_Passive_Atk_Bonus"


@BuffCallbackRepository.register(LOGIC_ID)
def astra_yao_core_passive_atk_bonus(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    耀嘉音 - 核心被动攻击力加成
    逻辑：
        在 Buff 激活或刷新时(BuffStart)，根据持有者(owner)的实时攻击力计算层数。
        转化比例：0.35 * ATK。
        包含特殊的持续时间延长机制：若处于活跃状态且刚更新过，则延长持续时间。
    """
    sim = buff.sim_instance
    char = buff.owner  # Buff 的持有者即为受益人

    if not char:
        return

    # 1. 基础参数
    core_passive_ratio = 0.35
    duration_added_per_active = 1200

    # 2. 计算层数 (Count)
    # 基于当前属性快照
    static_atk = getattr(char.statement, "ATK", 0)
    target_count = min(int(static_atk * core_passive_ratio), buff.config.max_stacks)

    buff.dy.count = target_count

    # 3. 持续时间更新逻辑
    # 获取记录 (Stored in custom_data)
    # 结构: {"last_start_tick": int, "last_end_tick": int}
    record_data = buff.dy.custom_data.get("update_info", {})

    current_tick = sim.tick
    last_end_tick = record_data.get("last_end_tick", -1)

    # 判定是"刷新延长"还是"全新启动"
    # 如果 Buff 之前是激活状态，且未完全过期（允许少量容差，或逻辑上的连续性）
    is_refresh = buff.dy.active and last_end_tick >= current_tick

    if is_refresh:
        # 延长逻辑
        # 原逻辑：min(last_update_end_tick + 1200, maxduration + tick)
        # 这里简化为直接修改 buff.dy.end_tick
        new_end_tick = min(
            last_end_tick + duration_added_per_active, current_tick + buff.config.duration
        )
        buff.dy.end_tick = new_end_tick

        # 此时 BuffStart 事件可能已经重置了 start_tick，这里通常不需要手动改 start_tick
    else:
        # 全新启动
        # Buff 系统默认会设置 duration，这里我们确保它是我们期望的值
        buff.dy.end_tick = current_tick + duration_added_per_active

    # 4. 更新记录
    buff.dy.custom_data["update_info"] = {
        "last_start_tick": current_tick,
        "last_end_tick": buff.dy.end_tick,
    }

    if ASTRAYAO_REPORT:
        sim.schedule_data.change_process_state()
        print(
            f"核心被动触发器激活！为{char.NAME}添加攻击力Buff（{target_count}点）！"
            f"持续时间: {current_tick} -> {buff.dy.end_tick}"
        )
