from typing import TYPE_CHECKING, Any

from zsim.define import VIVIAN_REPORT
from zsim.sim_progress.anomaly_bar.AnomalyBarClass import AnomalyBar
from zsim.sim_progress.anomaly_bar.CopyAnomalyForOutput import DirgeOfDestinyAnomaly
from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.Load import LoadingMission
from zsim.sim_progress.ScheduledEvent.Calculator import Calculator as Cal
from zsim.sim_progress.ScheduledEvent.Calculator import MultiplierData as Mul
from zsim.sim_progress.Update.UpdateAnomaly import spawn_normal_dot
from zsim.sim_progress.zsim_event_system.zsim_events.anomaly_event import AnomalyEvent
from zsim.sim_progress.zsim_event_system.zsim_events.skill_event import SkillExecutionEvent

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

# ==============================================================================
# 逻辑ID定义 (需与 触发判断.csv 中的 logic_id 严格对应)
# ==============================================================================
LOGIC_FEATHER_UPDATE = "Vivian_Feather_Manager"  # 羽毛更新
LOGIC_RAINFALL_COATTACK = "Vivian_Rainfall_CoAttack"  # 协同攻击(队友强化E)
LOGIC_TEAM_PASSIVE = "Vivian_Team_Passive"  # 组队被动(队友异常)
LOGIC_CORE_PASSIVE = "Vivian_Core_Passive"  # 核心被动(生花异放)
LOGIC_PROPHECY_DOT = "Vivian_Prophecy_DoT"  # 预言DoT
LOGIC_CINEMA6_START = "Vivian_Cinema6_Start"  # 6画: 启动消耗
LOGIC_CINEMA6_HIT = "Vivian_Cinema6_Hit"  # 6画: 命中结算

# 核心被动倍率表
ANOMALY_RATIO_MUL = {0: 0.0075, 1: 0.08, 2: 0.0108, 3: 0.032, 4: 0.0615, 5: 0.0108}

# ==============================================================================
# 辅助工具函数
# ==============================================================================


def _is_first_hit(event: "SkillExecutionEvent", context: "BaseZSimEventContext") -> bool:
    """判断当前是否为技能的第一击"""
    # SkillEventContext 维护了 hitted_count
    if hasattr(context, "hitted_count"):
        return context.hitted_count == 1
    return False


def _is_last_hit(event: "SkillExecutionEvent", context: "BaseZSimEventContext") -> bool:
    """判断当前是否为技能的最后一击"""
    if hasattr(context, "hitted_count") and hasattr(event, "hit_times"):
        return context.hitted_count == event.hit_times
    return False


def _get_target(buff: "Buff", event: "ZSimEventABC") -> Any:
    """获取目标对象（优先从事件获取，否则默认取1号位敌人）"""
    if hasattr(event, "target") and event.target:
        return event.target
    if hasattr(buff.sim_instance, "enemy_group"):
        return buff.sim_instance.enemy_group[1]
    return None


def _spawn_coattack(buff: "Buff"):
    """执行生成协同攻击(落雨生花)的动作"""
    owner = buff.owner
    if not hasattr(owner, "feather_manager"):
        return

    # 尝试生成协同攻击 Tag
    coattack_skill_tag = owner.feather_manager.spawn_coattack()

    if coattack_skill_tag is None:
        if VIVIAN_REPORT:
            buff.sim_instance.schedule_data.change_process_state()
            print(f"【落雨生花】触发失败：资源不足。当前资源：{owner.get_special_stats()}")
        return

    # 添加到调度器 (external_add_skill)
    # 假设 sim_instance.scheduler 可用，参数为 (skill_tag, is_insert, delay)
    if hasattr(buff.sim_instance, "scheduler"):
        buff.sim_instance.scheduler.external_add_skill((coattack_skill_tag, False, 0))

    if VIVIAN_REPORT:
        buff.sim_instance.schedule_data.change_process_state()
        print(f"【落雨生花】触发成功！薇薇安释放了 {coattack_skill_tag}")


# ==============================================================================
# 核心逻辑回调实现
# ==============================================================================


@BuffCallbackRepository.register(LOGIC_FEATHER_UPDATE)
def vivian_feather_update(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    [羽毛管理] 监听 SkillHit (Last Hit)
    当薇薇安自身技能结束时，更新羽毛状态。
    """
    if not isinstance(event, SkillExecutionEvent):
        return

    # 仅处理薇薇安自己的技能
    if str(buff.owner.base_code) not in event.event_message.skill_tag:
        return

    # 仅在最后一击触发更新
    if _is_last_hit(event, context):
        if hasattr(buff.owner, "feather_manager"):
            # FeatherManager.update_myself 需要 SkillNode 信息
            # event.event_origin 即为 SkillNode
            buff.owner.feather_manager.update_myself(event.event_origin)


@BuffCallbackRepository.register(LOGIC_RAINFALL_COATTACK)
def vivian_rainfall_coattack(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    [协同攻击] 监听 队友 SkillHit (First Hit)
    队友释放强化特殊技(TriggerBuffLevel=2)时触发。
    """
    if not isinstance(event, SkillExecutionEvent):
        return

    # 排除自己
    if str(buff.owner.base_code) in event.event_message.skill_tag:
        return

    # 必须是第一击
    if not _is_first_hit(event, context):
        return

    # 检查技能属性：TriggerBuffLevel == 2
    skill_node = event.event_origin
    if not hasattr(skill_node, "skill") or getattr(skill_node.skill, "trigger_buff_level", 0) != 2:
        return

    # 特殊排除：柳的强化E第二段 (兼容旧逻辑)
    if event.event_message.skill_tag == "1221_E_EX_2":
        return

    # 防止同一技能重复触发 (检查 UUID)
    state = buff.dy.custom_data.setdefault("coattack_trigger", {"last_uuid": ""})
    if state["last_uuid"] == event.event_message.event_id:
        return
    state["last_uuid"] = event.event_message.event_id

    _spawn_coattack(buff)


@BuffCallbackRepository.register(LOGIC_TEAM_PASSIVE)
def vivian_team_passive(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    [组队被动] 监听 AnomalyEvent
    队友触发属性异常时，触发协同攻击。
    """
    if not isinstance(event, AnomalyEvent):
        return

    # 仅响应异常触发事件 (trigger)
    # 假设 trigger_type="trigger" 代表异常被触发
    if event.event_message.trigger_type != "trigger":
        return

    anomaly_bar = event.event_origin

    # 排除薇薇安自己触发的异常
    if anomaly_bar.activated_by and str(buff.owner.base_code) in getattr(
        anomaly_bar.activated_by, "skill_tag", ""
    ):
        if VIVIAN_REPORT:
            buff.sim_instance.schedule_data.change_process_state()
            print("组队被动：检测到薇薇安触发的属性异常，不放行！")
        return

    # 内置CD检查 (30 ticks = 0.5秒)
    state = buff.dy.custom_data.setdefault(
        "team_passive", {"last_tick": -999, "last_anomaly_id": None}
    )
    current_tick = context.timer.tick

    if current_tick - state["last_tick"] < 30:
        return

    # 防止同一异常对象重复触发
    if id(anomaly_bar) == state["last_anomaly_id"]:
        return

    # 更新状态并触发
    state["last_tick"] = current_tick
    state["last_anomaly_id"] = id(anomaly_bar)

    if VIVIAN_REPORT:
        buff.sim_instance.schedule_data.change_process_state()
        print(f"组队被动：队友触发异常 {event.event_message.attribute_type}，尝试触发落雨生花。")

    _spawn_coattack(buff)


@BuffCallbackRepository.register(LOGIC_CORE_PASSIVE)
def vivian_core_passive(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    [核心被动] 监听 SkillHit (落雨生花)
    落雨生花命中处于异常状态的敌人时，触发额外异放伤害。
    """
    if not isinstance(event, SkillExecutionEvent):
        return

    # 仅限落雨生花
    if event.event_message.skill_tag != "1331_CoAttack_A":
        return

    # 检查目标是否处于异常状态
    target = _get_target(buff, event)
    if not target or not target.dynamic.is_under_anomaly():
        return

    # 避免同一技能多段重复触发 (虽然生花通常只有一段)
    state = buff.dy.custom_data.setdefault("core_passive", {"last_uuid": ""})
    if state["last_uuid"] == event.event_message.event_id:
        return
    state["last_uuid"] = event.event_message.event_id

    # === 伤害结算逻辑 ===
    active_bars = target.dynamic.get_active_anomaly()
    if not active_bars:
        return

    # 复制异常条进行结算
    active_bar = active_bars[0]
    copy_bar = AnomalyBar.create_new_from_existing(active_bar)
    if not copy_bar.settled:
        copy_bar.anomaly_settled()

    # 计算倍率
    mul_data = Mul(target, target.dynamic.buff_list, buff.owner)
    ap = Cal.AnomalyMul.cal_ap(mul_data)

    ratio = ANOMALY_RATIO_MUL.get(copy_bar.element_type, 0.01)
    # 2命倍率修正
    cinema_ratio = 1.3 if buff.owner.cinema >= 2 else 1.0

    # 公式: (AP / 10) * 基础倍率 * 命座倍率
    final_ratio = (ap / 10.0) * ratio * cinema_ratio

    # 生成伤害事件
    event_obj = DirgeOfDestinyAnomaly(copy_bar, active_by="1331", sim_instance=buff.sim_instance)
    event_obj.anomaly_dmg_ratio = final_ratio

    # 推送事件 (使用 context.push_event 或直接操作 event_list)
    if hasattr(context, "push_event"):
        context.push_event(event_obj)
    else:
        # 回退兼容
        from zsim.sim_progress import JudgeTools

        JudgeTools.find_event_list(sim_instance=buff.sim_instance).append(event_obj)

    if VIVIAN_REPORT:
        buff.sim_instance.schedule_data.change_process_state()
        print("核心被动：【落雨生花】命中异常目标，触发异放伤害！")


@BuffCallbackRepository.register(LOGIC_PROPHECY_DOT)
def vivian_prophecy_dot(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    [预言DoT] 监听 SkillHit (SNA_2 或 CoAttack_A)
    命中处于异常状态的敌人时，施加“薇薇安的预言”DoT。
    """
    if not isinstance(event, SkillExecutionEvent):
        return

    tag = event.event_message.skill_tag
    if tag not in ["1331_SNA_2", "1331_CoAttack_A"]:
        return

    target = _get_target(buff, event)
    if not target or not target.dynamic.is_under_anomaly():
        return

    # 检查 DoT 是否已存在
    if target.find_dot("ViviansProphecy"):
        return

    # 生成 DoT
    dot = spawn_normal_dot("ViviansProphecy", sim_instance=buff.sim_instance)
    dot.start(context.timer.tick)

    # 绑定 loading_mission 以便复用伤害计算逻辑
    dot.skill_node_data.loading_mission = LoadingMission(dot.skill_node_data)
    dot.skill_node_data.loading_mission.mission_start(context.timer.tick)

    target.dynamic.dynamic_dot_list.append(dot)

    # 推送事件
    if hasattr(context, "push_event"):
        context.push_event(dot.skill_node_data)
    else:
        from zsim.sim_progress import JudgeTools

        JudgeTools.find_event_list(sim_instance=buff.sim_instance).append(dot.skill_node_data)

    if VIVIAN_REPORT:
        buff.sim_instance.schedule_data.change_process_state()
        print("核心被动：薇薇安对敌人施加【薇薇安的预言】DoT")


@BuffCallbackRepository.register(LOGIC_CINEMA6_START)
def vivian_cinema6_start(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    [6画·启动] 监听 SkillStart (1331_SNA_2)
    技能开始时：消耗所有护羽，记录消耗量，并尝试联动1画效果。
    """
    # 检查事件类型：必须是 SKILL_START
    if getattr(event, "event_type", None) != "SKILL_START":
        return

    # 检查技能标签
    tag = getattr(event.event_message, "skill_tag", "")
    if tag != "1331_SNA_2":
        return

    # 资源处理
    fm = buff.owner.feather_manager
    guard_feather_cost = min(fm.guard_feather, 5)

    # 记录消耗量到 custom_data，Key 为技能 UUID
    # 这个数据将被 Hit 逻辑读取
    uuid = event.event_message.event_id
    buff.dy.custom_data.setdefault("c6_state", {})[uuid] = guard_feather_cost

    # 扣除护羽
    fm.guard_feather = 0
    fm.c1_counter += guard_feather_cost

    # 1画联动：每消耗4点回复1点飞羽
    while fm.c1_counter >= 4:
        fm.c1_counter -= 4
        fm.flight_feather = min(fm.flight_feather + 1, 5)

    if VIVIAN_REPORT:
        print(f"6画触发：SNA_2启动，消耗护羽 {guard_feather_cost}。")


@BuffCallbackRepository.register(LOGIC_CINEMA6_HIT)
def vivian_cinema6_hit(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    [6画·命中] 监听 SkillHit (1331_SNA_2)
    技能命中时：检查该次技能是否消耗了护羽（读取 custom_data），若消耗则触发额外伤害。
    """
    if not isinstance(event, SkillExecutionEvent):
        return

    if event.event_message.skill_tag != "1331_SNA_2":
        return

    # 读取启动时记录的消耗数据
    c6_data = buff.dy.custom_data.get("c6_state", {})
    uuid = event.event_message.event_id
    cost = c6_data.get(uuid, 0)

    # 若无消耗记录或标记为已结算(-1)，则跳过
    if cost <= 0:
        return

    # 标记为已结算，防止多段 Hit 重复触发
    c6_data[uuid] = -1

    # 检查目标状态
    target = _get_target(buff, event)
    active_bars = target.dynamic.get_active_anomaly() if target else []

    if not active_bars:
        # 无异常，仅更新自身状态标记
        buff.owner.feather_manager.update_myself(c6_signal=True)
        if VIVIAN_REPORT:
            print("6画触发：命中无异常目标，未触发额外伤害。")
        return

    # === 伤害结算 ===
    active_bar = active_bars[0]
    copy_bar = AnomalyBar.create_new_from_existing(active_bar)
    if not copy_bar.settled:
        copy_bar.anomaly_settled()

    # 6画特有倍率
    c6_ratio = cost * 0.8
    cinema_ratio = 1.3 if buff.owner.cinema >= 2 else 1.0

    mul_data = Mul(target, target.dynamic.buff_list, buff.owner)
    ap = Cal.AnomalyMul.cal_ap(mul_data)

    final_ratio = (
        (ap / 10.0) * ANOMALY_RATIO_MUL.get(copy_bar.element_type, 0.01) * cinema_ratio * c6_ratio
    )

    # 生成事件
    event_obj = DirgeOfDestinyAnomaly(copy_bar, active_by="1331", sim_instance=buff.sim_instance)
    event_obj.anomaly_dmg_ratio = final_ratio

    # 推送事件
    if hasattr(context, "push_event"):
        context.push_event(event_obj)
    else:
        from zsim.sim_progress import JudgeTools

        JudgeTools.find_event_list(sim_instance=buff.sim_instance).append(event_obj)

    buff.owner.feather_manager.update_myself(c6_signal=True)

    if VIVIAN_REPORT:
        print(f"6画触发：消耗护羽{cost}，触发额外异放伤害！(倍率: {final_ratio:.2f})")
