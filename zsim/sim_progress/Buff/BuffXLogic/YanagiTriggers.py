from copy import deepcopy
from typing import TYPE_CHECKING, Any

from zsim.sim_progress import JudgeTools
from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.Update import spawn_output
from zsim.sim_progress.zsim_event_system.zsim_events.skill_event import SkillExecutionEvent

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

# ==============================================================================
# 逻辑ID定义
# ==============================================================================
LOGIC_POLARITY_DISORDER = "Yanagi_Polarity_Disorder_Trigger"


# ==============================================================================
# 辅助函数
# ==============================================================================
def _get_target(buff: "Buff", event: "ZSimEventABC") -> Any:
    """获取目标对象（优先从事件获取，否则默认取1号位敌人）"""
    if hasattr(event, "target") and event.target:
        return event.target
    if hasattr(buff.sim_instance, "enemy_group"):
        return buff.sim_instance.enemy_group[1]
    return None


def _is_last_hit(event: "SkillExecutionEvent", context: "BaseZSimEventContext") -> bool:
    """判断当前是否为技能的最后一击"""
    # SkillExecutionEvent 携带 hit_times (总段数)
    # Context 携带 hitted_count (当前已命中段数)
    if hasattr(context, "hitted_count") and hasattr(event, "hit_times"):
        return context.hitted_count == event.hit_times
    return False


# ==============================================================================
# 核心逻辑实现
# ==============================================================================


@BuffCallbackRepository.register(LOGIC_POLARITY_DISORDER)
def yanagi_polarity_disorder_trigger(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    柳-极性紊乱触发器
    对应原 YanagiPolarityDisorderTrigger.py

    监听: SkillHit (SkillExecutionEvent)
    逻辑:
    1. 1221_E_EX_1 (突刺): 命中时更新连击计数 (需2命+)。
    2. 1221_E_EX_2 (下落) / 1221_Q: Last Hit 命中且敌人处于异常状态时，触发极性紊乱。
    """
    if not isinstance(event, SkillExecutionEvent):
        return

    skill_tag = event.event_message.skill_tag

    # 筛选关注的技能标签
    if skill_tag not in ["1221_E_EX_1", "1221_E_EX_2", "1221_Q"]:
        return

    # 初始化状态数据 (替代原 Record 类)
    state = buff.dy.custom_data.setdefault(
        "yanagi_pd_state",
        {
            "e_counter": {"update_from": "", "count": 0},  # 计数器
            "e_max_count": None,  # 最大层数缓存
            "basic_ratio": None,  # 基础倍率缓存
        },
    )

    # 获取角色命座
    cinema = buff.owner.cinema if hasattr(buff.owner, "cinema") else 0

    # === 分支 A: 突刺攻击 (更新计数) ===
    if skill_tag == "1221_E_EX_1":
        # 命座 < 2 不参与计数
        if cinema < 2:
            return

        # 检查是否为同一技能的重复Hit (避免多段伤害重复计数)
        current_uuid = event.event_message.event_id
        if state["e_counter"]["update_from"] == current_uuid:
            return

        # 初始化最大层数
        if state["e_max_count"] is None:
            state["e_max_count"] = 2 if cinema < 6 else 4

        # 更新计数
        state["e_counter"]["count"] += 1
        if state["e_counter"]["count"] >= state["e_max_count"]:
            state["e_counter"]["count"] = state["e_max_count"]

        # 记录本次更新来源
        state["e_counter"]["update_from"] = current_uuid
        return

    # === 分支 B: 触发攻击 (结算极性紊乱) ===
    # 仅在 Last Hit 触发
    if not _is_last_hit(event, context):
        return

    # 检查敌人状态
    target = _get_target(buff, event)
    if not target or not hasattr(target, "dynamic"):
        return

    if not target.dynamic.is_under_anomaly():
        # 触发攻击打中但无异常，清空计数
        state["e_counter"] = {"update_from": "", "count": 0}
        return

    # === 执行结算 ===

    # 1. 计算倍率
    if state["basic_ratio"] is None:
        state["basic_ratio"] = 0.15 if cinema < 2 else 0.2

    final_ratio = state["basic_ratio"] + 0.15 * state["e_counter"]["count"]

    # 2. 获取异常条快照
    active_anomaly_bar = target.dynamic.get_active_anomaly_bar()
    if not active_anomaly_bar:
        return

    active_bar_copy = deepcopy(active_anomaly_bar)
    if not active_bar_copy.settled:
        active_bar_copy.anomaly_settled()

    # 3. 生成输出对象
    # 使用 spawn_output (mode_number=2 代表极性紊乱)
    # 注意: skill_node 参数在 spawn_output 中可能被使用，传入 event_origin (即 SkillNode)
    skill_node = event.event_origin
    sim = buff.sim_instance

    polarity_disorder_output = spawn_output(
        active_bar_copy,
        mode_number=2,
        polarity_ratio=final_ratio,
        skill_node=skill_node,
        sim_instance=sim,
    )

    # 4. 推送事件
    if hasattr(context, "push_event"):
        context.push_event(polarity_disorder_output)
    else:
        # 兼容性回退
        event_list = JudgeTools.find_event_list(sim_instance=sim)
        event_list.append(polarity_disorder_output)

    # 5. 结算后重置计数
    state["e_counter"] = {"update_from": "", "count": 0}
