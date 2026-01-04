from copy import deepcopy
from typing import TYPE_CHECKING, Optional

from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.Preload import SkillNode
from zsim.sim_progress.Update import spawn_output
from zsim.sim_progress.zsim_event_system.zsim_events.skill_event import SkillExecutionEvent

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events.base_zsim_event import (
        BaseZSimEventContext,
        ZSimEventABC,
    )

LOGIC_ID = "Buff-角色-柳-极性紊乱触发器"


def get_skill_node(event: "ZSimEventABC") -> Optional["SkillNode"]:
    """从事件中提取 SkillNode 的辅助函数"""
    if not hasattr(event, "event_origin"):
        return None
    origin = event.event_origin
    if isinstance(origin, SkillNode):
        return origin
    if hasattr(origin, "event_origin") and isinstance(origin.event_origin, SkillNode):
        return origin.event_origin
    return None


@BuffCallbackRepository.register(LOGIC_ID)
def yanagi_polarity_disorder_trigger(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    柳的极性紊乱触发器。
    在强化E和Q的最后一击，如果敌人处于属性异常状态，则触发极性紊乱伤害。
    """
    if not isinstance(event, SkillExecutionEvent):
        return

    skill_node = get_skill_node(event)
    if not skill_node:
        return

    # 1. 筛选相关技能
    # 1221_E_EX_1: 强化E 穿刺攻击 (用于叠层)
    # 1221_E_EX_2: 强化E 下落攻击 (用于触发)
    # 1221_Q: 终结技 (用于触发)
    target_tags = ["1221_E_EX_1", "1221_E_EX_2", "1221_Q"]
    if skill_node.skill_tag not in target_tags:
        return

    # 2. 初始化 custom_data 状态
    state = buff.dy.custom_data
    if "e_counter" not in state:
        state["e_counter"] = {"update_from": "", "count": 0}
        # 2命以上最大计数为4，否则为2
        state["e_max_count"] = 4 if buff.owner.cinema >= 2 else 2

    # 3. 分支：穿刺攻击 (计数逻辑)
    if skill_node.skill_tag == "1221_E_EX_1":
        # 避免同一技能的多次 Hit 重复计数 (通过 UUID 判断)
        current_uuid = getattr(skill_node, "UUID", "")
        if state["e_counter"]["update_from"] == current_uuid:
            return

        # 2命以上才启用计数逻辑
        if buff.owner.cinema >= 2:
            state["e_counter"]["count"] = min(state["e_counter"]["count"] + 1, state["e_max_count"])
            state["e_counter"]["update_from"] = current_uuid
        return

    # 4. 分支：下落攻击或终结技 (触发逻辑)
    # 必须是该技能的最后一击
    last_hit_tick = skill_node.loading_mission.get_last_hit()
    current_tick = context.timer.tick

    # 判断是否为最后一跳 (当前时间是否刚好覆盖最后一跳时间点)
    is_last_hit = current_tick - 1 < last_hit_tick <= current_tick
    if not is_last_hit:
        return

    # 获取目标敌人
    target = getattr(event, "target", None)
    # 兼容性处理：如果事件没有 target，尝试从 sim_instance 获取
    if target is None and hasattr(buff.sim_instance, "enemy_group"):
        target = buff.sim_instance.enemy_group[1]  # 默认主目标

    if not target:
        return

    # 检查敌人是否处于属性异常状态
    if hasattr(target, "dynamic") and target.dynamic.is_under_anomaly():
        # 执行极性紊乱逻辑
        _execute_polarity_disorder(buff, event, context, state, target, skill_node)

        # 触发后重置计数器
        state["e_counter"] = {"update_from": "", "count": 0}


def _execute_polarity_disorder(buff, event, context, state, target, skill_node):
    """执行极性紊乱伤害生成与分发"""
    # 计算倍率
    basic_ratio = 0.15 if buff.owner.cinema < 2 else 0.2
    count = state["e_counter"]["count"]
    final_ratio = basic_ratio + 0.15 * count

    # 获取当前激活的异常条
    active_anomaly_bar = target.get_active_anomaly_bar()
    if not active_anomaly_bar:
        return

    # 复制异常条用于结算
    active_bar_deep_copy = deepcopy(active_anomaly_bar)
    if not active_bar_deep_copy.settled:
        active_bar_deep_copy.anomaly_settled()

    # 生成极性紊乱事件/输出
    polarity_disorder_output = spawn_output(
        active_bar_deep_copy,
        mode_number=2,  # 模式2代表极性紊乱
        polarity_ratio=final_ratio,
        skill_node=skill_node,
        sim_instance=buff.sim_instance,
    )

    # 将事件推送到系统中
    if hasattr(context, "push_event"):
        context.push_event(polarity_disorder_output)
    elif hasattr(buff.sim_instance, "event_list"):
        # 兼容旧式直接追加到列表
        buff.sim_instance.event_list.append(polarity_disorder_output)
