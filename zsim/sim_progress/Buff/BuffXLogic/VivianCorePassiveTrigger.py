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

LOGIC_ID = "Buff-角色-薇薇安-核心被动"

ANOMALY_RATIO_MUL = {
    0: 0.0075,
    1: 0.08,
    2: 0.0108,
    3: 0.032,
    4: 0.0615,
    5: 0.0108,
}


@BuffCallbackRepository.register(LOGIC_ID)
def vivian_core_passive_trigger(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    薇薇安核心被动：落雨生花命中异常状态敌人，触发异放。
    """
    if not isinstance(event, SkillExecutionEvent):
        return

    skill_node = getattr(event, "event_origin", None)
    if not isinstance(skill_node, SkillNode):
        return

    # 1. 筛选技能：落雨生花
    if skill_node.skill_tag != "1331_CoAttack_A":
        return

    # 2. 获取目标及异常状态
    target = getattr(event, "target", None)
    if not target:
        target = buff.sim_instance.enemy_group[1]  # fallback

    if not hasattr(target, "dynamic") or not target.dynamic.is_under_anomaly():
        return

    # 3. 防止单次技能重复触发 (UUID check)
    state = buff.dy.custom_data
    if state.get("last_update_uuid") == skill_node.UUID:
        return
    state["last_update_uuid"] = skill_node.UUID

    # 4. 执行效果：生成额外伤害
    active_anomalies = target.dynamic.get_active_anomaly()
    if not active_anomalies:
        return  # 理论上前面 checks pass 这里不应为空

    active_bar = active_anomalies[0]
    copied_anomaly = AnomalyBar.create_new_from_existing(active_bar)
    if not copied_anomaly.settled:
        copied_anomaly.anomaly_settled()

    # 计算倍率
    enemy_buffs = getattr(target.dynamic, "buff_list", [])
    mul_data = Mul(target, enemy_buffs, buff.owner)
    ap = Cal.AnomalyMul.cal_ap(mul_data)

    ratio = ANOMALY_RATIO_MUL.get(copied_anomaly.element_type, 0.01)
    cinema_ratio = 1 if buff.owner.cinema < 2 else 1.3

    # 伤害公式
    final_ratio = (ap / 10) * ratio * cinema_ratio

    # 构造事件
    dirge_event = DirgeOfDestinyAnomaly(
        copied_anomaly, active_by="1331", sim_instance=buff.sim_instance
    )
    dirge_event.anomaly_dmg_ratio = final_ratio

    # 推送事件
    if hasattr(buff.sim_instance, "event_list"):
        buff.sim_instance.event_list.append(dirge_event)

    if VIVIAN_REPORT:
        print("核心被动：【落雨生花】命中异常敌人，触发异放！")
