import math
from typing import TYPE_CHECKING

from zsim.define import VIVIAN_REPORT
from zsim.sim_progress.anomaly_bar import AnomalyBar
from zsim.sim_progress.anomaly_bar.CopyAnomalyForOutput import DirgeOfDestinyAnomaly
from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.Preload import SkillNode
from zsim.sim_progress.ScheduledEvent.Calculator import Calculator as Cal
from zsim.sim_progress.ScheduledEvent.Calculator import MultiplierData as Mul
from zsim.sim_progress.zsim_event_system.zsim_events.skill_event import SkillExecutionEvent

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events.base_zsim_event import (
        BaseZSimEventContext,
        ZSimEventABC,
    )

LOGIC_ID = "Buff-角色-薇薇安-6画-核心被动强化"

ANOMALY_RATIO_MUL = {
    0: 0.0075,
    1: 0.08,
    2: 0.0108,
    3: 0.032,
    4: 0.0615,
    5: 0.0108,
}


@BuffCallbackRepository.register(LOGIC_ID)
def vivian_cinema6_trigger(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    薇薇安6画：使用【悬落】(1331_SNA_2) 时消耗护羽，强化异放伤害。
    """
    if not isinstance(event, SkillExecutionEvent):
        return

    skill_node = getattr(event, "event_origin", None)
    if not isinstance(skill_node, SkillNode):
        return

    if skill_node.skill_tag != "1331_SNA_2":
        return

    state = buff.dy.custom_data

    # 1. 消耗逻辑 (Pre-Active)
    # 防止同一技能重复消耗
    if state.get("last_consumed_uuid") != skill_node.UUID:
        char = buff.owner
        if hasattr(char, "feather_manager"):
            guard_feather = char.feather_manager.guard_feather
            cost = min(guard_feather, 5)

            # 记录消耗量供后续伤害计算
            state["current_cost"] = cost
            state["last_consumed_uuid"] = skill_node.UUID

            # 扣除资源 & 1画联动
            char.feather_manager.guard_feather = 0
            char.feather_manager.c1_counter += cost
            while char.feather_manager.c1_counter >= 4:
                char.feather_manager.c1_counter -= 4
                char.feather_manager.flight_feather = min(
                    char.feather_manager.flight_feather + 1, 5
                )

            if VIVIAN_REPORT:
                print(f"6画触发器：【悬落】消耗护羽 {cost}。")

    # 2. 伤害计算逻辑 (Effect)
    target = getattr(event, "target", None) or buff.sim_instance.enemy_group[1]

    # 检查异常状态
    active_anomalies = target.dynamic.get_active_anomaly()
    if not active_anomalies:
        # 无异常，只触发羽毛转化 (C6 signal)
        char = buff.owner
        if hasattr(char, "feather_manager"):
            # 这里复用 FeatherManager update_myself 的副作用(转化羽毛)
            # 但注意 update_myself 会调用 trans_feather，
            # 该函数可能会在此时机被触发两次 (trigger itself + logic)，需留意 FeatherTrigger 实现
            # 在本逻辑中显式调用 c6_signal
            char.feather_manager.update_myself(c6_signal=True)
        return

    # 防止同一技能重复造成伤害
    if state.get("last_dmg_uuid") == skill_node.UUID:
        return
    state["last_dmg_uuid"] = skill_node.UUID

    # 计算额外伤害
    active_bar = active_anomalies[0]
    copied_anomaly = AnomalyBar.create_new_from_existing(active_bar)
    if not copied_anomaly.settled:
        copied_anomaly.anomaly_settled()

    enemy_buffs = getattr(target.dynamic, "buff_list", [])
    mul_data = Mul(target, enemy_buffs, buff.owner)
    ap = Cal.AnomalyMul.cal_ap(mul_data)

    ratio = ANOMALY_RATIO_MUL.get(copied_anomaly.element_type, 0.01)
    cinema_ratio = 1 if buff.owner.cinema < 2 else 1.3
    c6_ratio_bonus = state.get("current_cost", 0) * 0.8

    final_ratio = math.floor(ap / 10) * ratio * cinema_ratio * c6_ratio_bonus

    dirge_event = DirgeOfDestinyAnomaly(
        copied_anomaly, active_by="1331", sim_instance=buff.sim_instance
    )
    dirge_event.anomaly_dmg_ratio = final_ratio

    if hasattr(buff.sim_instance, "event_list"):
        buff.sim_instance.event_list.append(dirge_event)

    if VIVIAN_REPORT:
        print(f"6画触发器：触发额外异放！倍率加成: {c6_ratio_bonus}")

    # 伤害触发后，再次确保羽毛转化逻辑执行
    char = buff.owner
    if hasattr(char, "feather_manager"):
        char.feather_manager.update_myself(c6_signal=True)
