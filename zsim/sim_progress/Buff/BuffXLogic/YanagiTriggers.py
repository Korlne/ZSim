from typing import TYPE_CHECKING

from zsim.define import YANAGI_REPORT
from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.Preload import SkillNode

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

# ==============================================================================
# 逻辑ID定义 (需与 buff_effect.csv 中的 logic_id 保持一致)
# ==============================================================================
LOGIC_POLARITY_DISORDER = "Yanagi_Polarity_Disorder_Trigger"
LOGIC_STANCE_JOUGEN = "Yanagi_Stance_Jougen"
LOGIC_STANCE_KAGEN = "Yanagi_Stance_Kagen"
LOGIC_CINEMA1_INSIGHT_MONITOR = "Yanagi_Cinema1_Insight_Monitor"
LOGIC_CINEMA6_SHINRA_MONITOR = "Yanagi_Cinema6_Shinra_Monitor"


# ==============================================================================
# 极性紊乱触发器
# ==============================================================================
@BuffCallbackRepository.register(LOGIC_POLARITY_DISORDER)
def yanagi_polarity_disorder_trigger(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    柳-极性紊乱触发器
    逻辑：
        监听技能命中，若满足条件（如强化特殊技最后一击），则触发极性紊乱判定。
        这里主要负责调用 Character 内部的极性紊乱处理逻辑。
    """
    sim = buff.sim_instance
    yanagi = buff.owner

    # 1. 验证事件
    if not hasattr(event, "event_origin") or not isinstance(event.event_origin, SkillNode):
        return
    skill_node = event.event_origin

    # 2. 验证是否为柳的技能
    if skill_node.char_name != "柳":
        return

    # 3. 验证是否为 Last Hit (防止多段伤害重复触发)
    # SkillExecutionEvent 携带 hit_times (总段数), Context 携带 hitted_count (当前段数)
    if hasattr(context, "hitted_count") and hasattr(event, "hit_times"):
        if context.hitted_count != event.hit_times:
            return

    # 4. 筛选触发技能 (强化E下落攻击 或 Q)
    # 假设标签为 1221_E_EX_SLAM 或 1221_Q，需根据实际 Skill Tag 调整
    trigger_tags = ["1221_E_EX_SLAM", "1221_Q"]
    # 注意：实际项目中需确认柳的技能标签，这里做宽泛匹配示例
    is_trigger_skill = any(tag in skill_node.skill_tag for tag in trigger_tags)

    # 也可以检查 trigger_buff_level 或其他标识
    if not is_trigger_skill:
        return

    # 5. 执行触发 (委托给 Character 内部逻辑)
    # 假设柳有 handle_polarity_disorder 方法
    if hasattr(yanagi, "handle_polarity_disorder"):
        yanagi.handle_polarity_disorder(sim.tick, skill_node)
        if YANAGI_REPORT:
            sim.schedule_data.change_process_state()
            print(f"【柳】触发极性紊乱判定 - 来源: {skill_node.skill_tag}")


# ==============================================================================
# 架势判定：上弦 (Jougen)
# ==============================================================================
@BuffCallbackRepository.register(LOGIC_STANCE_JOUGEN)
def yanagi_stance_jougen_monitor(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    柳-上弦架势判定
    逻辑：
        检测柳当前的架势状态。若为上弦(True)，激活Buff；否则关闭。
    """
    yanagi = buff.owner
    if not hasattr(yanagi, "stance_manager"):
        return

    # stance_now: True 为上弦, False 为下弦
    is_jougen = yanagi.stance_manager.stance_now

    if is_jougen:
        if not buff.dy.active:
            buff.start(current_tick=buff.sim_instance.tick)
    else:
        if buff.dy.active:
            buff.end(current_tick=buff.sim_instance.tick)


# ==============================================================================
# 架势判定：下弦 (Kagen)
# ==============================================================================
@BuffCallbackRepository.register(LOGIC_STANCE_KAGEN)
def yanagi_stance_kagen_monitor(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    柳-下弦架势判定
    逻辑：
        检测柳当前的架势状态。若为下弦(False)，激活Buff；否则关闭。
    """
    yanagi = buff.owner
    if not hasattr(yanagi, "stance_manager"):
        return

    is_jougen = yanagi.stance_manager.stance_now
    is_kagen = not is_jougen

    if is_kagen:
        if not buff.dy.active:
            buff.start(current_tick=buff.sim_instance.tick)
    else:
        if buff.dy.active:
            buff.end(current_tick=buff.sim_instance.tick)


# ==============================================================================
# 1画：精通增幅 (洞悉状态监测)
# ==============================================================================
@BuffCallbackRepository.register(LOGIC_CINEMA1_INSIGHT_MONITOR)
def yanagi_cinema1_insight_monitor(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    柳-1画精通增幅
    逻辑：
        检测【洞悉】Buff是否存在且层数 >= 1。
        洞悉Buff ID: "Buff-角色-柳-1画-洞悉"
    """
    yanagi = buff.owner
    if not hasattr(yanagi, "buff_manager"):
        return

    insight_buff_id = "Buff-角色-柳-1画-洞悉"
    insight_buff = yanagi.buff_manager.get_buff(insight_buff_id)

    should_active = False
    if insight_buff and insight_buff.dy.active and insight_buff.dy.count >= 1:
        should_active = True

    if should_active:
        if not buff.dy.active:
            buff.start(current_tick=buff.sim_instance.tick)
    else:
        if buff.dy.active:
            buff.end(current_tick=buff.sim_instance.tick)


# ==============================================================================
# 6画：特殊技伤害提升 (森罗万象状态监测)
# ==============================================================================
@BuffCallbackRepository.register(LOGIC_CINEMA6_SHINRA_MONITOR)
def yanagi_cinema6_shinra_monitor(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    柳-6画森罗万象状态监测
    逻辑：
        检测柳的【森罗万象状态】是否开启。
    """
    yanagi = buff.owner

    # 获取特殊状态
    # 假设 get_special_stats 返回字典包含 "森罗万象状态"
    special_stats = yanagi.get_special_stats()
    is_active = special_stats.get("森罗万象状态", False)

    if is_active:
        if not buff.dy.active:
            buff.start(current_tick=buff.sim_instance.tick)
    else:
        if buff.dy.active:
            buff.end(current_tick=buff.sim_instance.tick)
