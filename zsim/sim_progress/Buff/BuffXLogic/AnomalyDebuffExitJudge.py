from typing import TYPE_CHECKING

from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

# 逻辑ID
LOGIC_ID = "Anomaly_Debuff_Exit_Judge"

# Buff名称到敌人动态属性名的映射
ANOMALY_MAP = {
    "Buff-异常-霜寒": "frostbite",
    "Buff-异常-畏缩": "assault",
    "Buff-异常-烈霜霜寒": "frost_frostbite",
    # 可根据需要补充其他映射
}


@BuffCallbackRepository.register(LOGIC_ID)
def anomaly_debuff_exit_judge(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    通用异常Debuff退出判决
    逻辑：
        每帧检查敌人的异常状态（由Buff名称映射得到）。
        如果检测到异常状态结束（下降沿），则结束此Buff。
    """
    sim = buff.sim_instance
    enemy = sim.ctx.current_enemy
    if not enemy:
        return

    # 1. 确定需要监控的异常属性名
    # 优先从 custom_data 获取，避免重复查表
    target_attr = buff.dy.custom_data.get("target_anomaly_attr")
    if not target_attr:
        # 尝试通过 buff 名称匹配 (原逻辑使用 index，这里建议用 name 或 config key)
        # 假设 buff.config.name 是 "Buff-异常-霜寒" 这种格式
        buff_name = buff.config.name
        target_attr = ANOMALY_MAP.get(buff_name)
        if target_attr:
            buff.dy.custom_data["target_anomaly_attr"] = target_attr
        else:
            # 如果找不到映射，可能不需要此逻辑，直接返回
            return

    # 2. 获取当前状态
    current_state = getattr(enemy.dynamic, target_attr, False)

    # 3. 获取上一帧状态 (默认为当前状态，避免初始化误判)
    last_state = buff.dy.custom_data.get("last_state", current_state)

    # 4. 下降沿检测 (True -> False)
    if last_state is True and current_state is False:
        # 异常状态结束，Buff 也应结束
        if buff.dy.active:
            buff.end(current_tick=sim.tick)

    # 5. 更新状态记录
    buff.dy.custom_data["last_state"] = current_state
