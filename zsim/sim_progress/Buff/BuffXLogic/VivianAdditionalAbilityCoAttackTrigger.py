from typing import TYPE_CHECKING

from zsim.define import VIVIAN_REPORT
from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository

# 假设存在此事件，如不存在需根据实际事件系统调整，或监听 Update 阶段
from zsim.sim_progress.zsim_event_system.zsim_events.anomaly_event import AnomalyActivatedEvent

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events.base_zsim_event import (
        BaseZSimEventContext,
        ZSimEventABC,
    )

LOGIC_ID = "Buff-角色-薇薇安-组队被动-协同攻击"


@BuffCallbackRepository.register(LOGIC_ID)
def vivian_additional_ability_coattack_trigger(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    薇薇安组队被动：队友触发异常时，触发落雨生花。
    内置CD 0.5秒 (30 ticks)。
    """
    if not isinstance(event, AnomalyActivatedEvent):
        return

    anomaly_bar = event.anomaly_bar
    if not anomaly_bar:
        return

    # 1. 过滤薇薇安自己触发的异常
    if anomaly_bar.activated_by and "1331" in getattr(anomaly_bar.activated_by, "skill_tag", ""):
        return

    # 2. CD 和 重复触发检查
    state = buff.dy.custom_data
    current_tick = context.timer.tick
    last_update_tick = state.get("last_update_tick", 0)
    last_anomaly_id = state.get("last_anomaly_id", None)

    # CD 检查 (30 ticks)
    if current_tick - last_update_tick < 30:
        return

    # 同一异常不重复触发
    if id(anomaly_bar) == last_anomaly_id:
        return

    # 3. 更新状态
    state["last_update_tick"] = current_tick
    state["last_anomaly_id"] = id(anomaly_bar)

    # 4. 执行效果
    char = buff.owner
    if hasattr(char, "feather_manager"):
        coattack_skill_tag = char.feather_manager.spawn_coattack()

        if coattack_skill_tag is None:
            if VIVIAN_REPORT:
                print(f"组队被动：豆子不够，无法触发。新异常类型：{anomaly_bar.element_type}")
            return

        # 添加技能
        preload_data = getattr(buff.sim_instance, "preload_data", None)
        if preload_data:
            input_tuple = (coattack_skill_tag, False, 0)
            preload_data.external_add_skill(input_tuple)

            if VIVIAN_REPORT:
                print("组队被动：队友触发异常，薇薇安触发落雨生花！")
