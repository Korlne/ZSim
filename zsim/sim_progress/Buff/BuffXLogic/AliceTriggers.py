from copy import deepcopy
from typing import TYPE_CHECKING

from zsim.define import ALICE_REPORT
from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.data_struct import PolarizedAssaultEvent
from zsim.sim_progress.Preload import SkillNode

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

# =============================================================================
# 逻辑ID定义 (需与 buff_effect.csv 中的 logic_id 保持一致)
# =============================================================================
LOGIC_ID_AP_BONUS = "Alice_Additional_Ability_Ap_Bonus"
LOGIC_ID_C6_TRIGGER = "Alice_Cinema6_Trigger"
LOGIC_ID_PA_TRIGGER = "Alice_Polarized_Assault_Trigger"


# =============================================================================
# 额外能力：异常掌控转精通
# =============================================================================
@BuffCallbackRepository.register(LOGIC_ID_AP_BONUS)
def alice_additional_ability_ap_bonus(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    爱丽丝额外能力：异常掌控转精通
    逻辑：
        读取爱丽丝实时异常掌控(AM)，根据公式 (AM - 140) * 1.6 计算Buff层数。
    """
    sim = buff.sim_instance

    # 1. 获取爱丽丝对象
    alice_char = sim.char_data.find_char_obj(CID=1401)
    if not alice_char:
        return

    # 2. 获取实时异常掌控 (AM)
    current_am = getattr(alice_char.statement, "AM", 0)

    # 3. 计算转化层数
    if current_am < 140:
        target_count = 0
    else:
        trans_ratio = 1.6
        target_count = int((current_am - 140) * trans_ratio)

    # 4. 同步 Buff 状态
    if target_count > 0:
        if not buff.dy.active:
            buff.start(current_tick=sim.tick)

        if buff.dy.count != target_count:
            buff.dy.count = target_count
    else:
        if buff.dy.active:
            buff.end(current_tick=sim.tick)
            buff.dy.count = 0


# =============================================================================
# 6画：额外攻击触发
# =============================================================================
@BuffCallbackRepository.register(LOGIC_ID_C6_TRIGGER)
def alice_c6_trigger(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    爱丽丝6画额外攻击逻辑：
    在【决胜】状态下，队友的攻击命中会触发爱丽丝的额外攻击。
    """
    sim = buff.sim_instance

    # 1. 确保事件类型是技能命中
    if not hasattr(event, "event_origin") or not event.event_origin:
        return

    skill_node = event.event_origin  # event_origin 是 SkillNode

    # 2. 获取爱丽丝对象
    alice_char = sim.char_data.find_char_obj(CID=1401)
    if not alice_char:
        return

    # 3. 过滤条件
    # 3.1 过滤掉爱丽丝自己的技能
    if skill_node.char_name == alice_char.NAME:
        return

    # 3.2 检查爱丽丝是否处于决胜状态 (victory_state)
    if not getattr(alice_char, "victory_state", False):
        return

    # 3.3 过滤掉非命中帧
    if not skill_node.is_hit_now(tick=sim.tick):
        return

    # 4. CD 检查 (内置 60tick CD)
    last_trigger = buff.dy.custom_data.get("last_c6_trigger", -9999)
    cd_limit = 60

    if sim.tick - last_trigger < cd_limit:
        return

    # 5. 执行逻辑：触发额外攻击
    if hasattr(alice_char, "spawn_extra_attack"):
        alice_char.spawn_extra_attack()
        # 更新 CD
        buff.dy.custom_data["last_c6_trigger"] = sim.tick


# =============================================================================
# 极性强击触发器 (Polarized Assault)
# =============================================================================
# 合法的触发技能标签
PA_ALLOWED_SKILL_TAGS = ["1401_SNA_3", "1401_Q"]


@BuffCallbackRepository.register(LOGIC_ID_PA_TRIGGER)
def alice_polarized_assault_trigger(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    爱丽丝 - 极性强击触发器
    逻辑：
        监听技能命中(SkillHit)，若为合法的触发源（SNA3或Q）且为LastHit，
        则构造一个 PolarizedAssaultEvent 并推入系统事件队列。
    """
    sim = buff.sim_instance

    # 1. 验证事件类型和来源
    if not hasattr(event, "event_origin") or not isinstance(event.event_origin, SkillNode):
        return

    skill_node = event.event_origin

    # 2. 基础条件筛选
    if skill_node.skill_tag not in PA_ALLOWED_SKILL_TAGS:
        return

    # 3. LastHit 判定
    if not skill_node.is_last_hit(tick=sim.tick):
        return

    # 4. 获取角色对象
    alice_char = sim.char_data.find_char_obj(CID=1401)
    if not alice_char:
        return

    # 5. 特殊判定：2画以下大招不触发
    if skill_node.skill_tag == "1401_Q" and alice_char.cinema < 2:
        return

    # 6. 执行触发逻辑
    enemy = sim.ctx.current_enemy
    if not enemy:
        return

    if 0 not in enemy.anomaly_bars_dict:
        return

    copyed_anomaly_bar = deepcopy(enemy.anomaly_bars_dict[0])
    copyed_anomaly_bar.activated_by = skill_node

    # 构造事件
    pa_event = PolarizedAssaultEvent(
        execute_tick=sim.tick,
        anomlay_bar=copyed_anomaly_bar,
        char_instance=alice_char,
        skill_node=skill_node,
    )

    # 推入事件队列
    sim.schedule_data.event_list.append(pa_event)

    if ALICE_REPORT:
        sim.schedule_data.change_process_state()
        print(
            f"【爱丽丝事件】{skill_node.skill.skill_text} 最后一Hit命中，创建了一个极性强击事件！"
        )
