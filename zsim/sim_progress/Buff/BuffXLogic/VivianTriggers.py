from typing import TYPE_CHECKING

from zsim.define import VIVIAN_REPORT
from zsim.sim_progress.anomaly_bar import AnomalyBar
from zsim.sim_progress.anomaly_bar.CopyAnomalyForOutput import DirgeOfDestinyAnomaly
from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.Preload import SkillNode
from zsim.sim_progress.ScheduledEvent.Calculator import Calculator, MultiplierData

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

# =============================================================================
# 逻辑ID定义 (需与 buff_effect.csv 中的 logic_id 保持一致)
# =============================================================================
LOGIC_ID_ADDITIONAL_ABILITY_CO_ATTACK = "Vivian_Additional_Ability_Co_Attack_Trigger"
LOGIC_ID_CINEMA1_DEBUFF = "Vivian_Cinema1_Debuff"
LOGIC_ID_CINEMA6_TRIGGER = "Vivian_Cinema6_Trigger"
LOGIC_ID_COATTACK_TRIGGER = "Vivian_Coattack_Trigger"
LOGIC_ID_CORE_PASSIVE_TRIGGER = "Vivian_Core_Passive_Trigger"
LOGIC_ID_DOT_TRIGGER = "Vivian_Dot_Trigger"
LOGIC_ID_FEATHER_TRIGGER = "Vivian_Feather_Trigger"


# =============================================================================
# 额外能力：协同攻击触发
# =============================================================================
@BuffCallbackRepository.register(LOGIC_ID_ADDITIONAL_ABILITY_CO_ATTACK)
def vivian_additional_ability_co_attack_trigger(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    薇薇安额外能力：协同攻击触发
    逻辑：
        当队友发动攻击时，满足特定条件（如内置CD、特定技能类型）触发薇薇安的协同攻击。
    """
    sim = buff.sim_instance

    # 1. 验证事件
    if not hasattr(event, "event_origin") or not isinstance(event.event_origin, SkillNode):
        return
    skill_node = event.event_origin

    # 2. 获取薇薇安对象
    vivian = sim.char_data.find_char_obj(name="薇薇安")
    if not vivian:
        return

    # 3. 自身不触发
    if skill_node.char_name == vivian.NAME:
        return

    # 4. 执行触发逻辑 (委托给 Character 内部管理器处理细节)
    if hasattr(vivian, "handle_additional_ability_coattack"):
        vivian.handle_additional_ability_coattack(skill_node, sim.tick)


# =============================================================================
# 1画：Debuff 施加
# =============================================================================
@BuffCallbackRepository.register(LOGIC_ID_CINEMA1_DEBUFF)
def vivian_cinema1_debuff(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    薇薇安1画：Debuff 施加
    逻辑：
        强化特殊技（EX）命中时给敌人施加减抗/易伤 Debuff。
    """
    sim = buff.sim_instance

    if not hasattr(event, "event_origin") or not isinstance(event.event_origin, SkillNode):
        return
    skill_node = event.event_origin

    # 筛选技能标签：强化特殊技 (1221_E_EX 等)
    if "EX" not in skill_node.skill_tag:
        return

    # 获取敌人并添加 Debuff
    enemy = sim.ctx.current_enemy
    if enemy and hasattr(enemy, "buff_manager"):
        # 假设 Buff ID 为 "Buff-角色-薇薇安-影画-1画-减抗"，请根据实际配置调整
        target_buff_id = "Buff-角色-薇薇安-影画-1画-减抗"
        enemy.buff_manager.add_buff(target_buff_id, current_tick=sim.tick)

        if VIVIAN_REPORT:
            print("【薇薇安】1画触发：为敌人添加减抗 Debuff")


# =============================================================================
# 6画：特殊机制触发
# =============================================================================
@BuffCallbackRepository.register(LOGIC_ID_CINEMA6_TRIGGER)
def vivian_cinema6_trigger(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    薇薇安6画触发器
    逻辑：
        全队任意角色触发属性异常的第一跳时，触发特殊效果（如构造新的属性异常伤害）。
        由于逻辑较复杂，建议委托给 Character 内部方法。
    """
    sim = buff.sim_instance
    vivian = buff.owner

    if not vivian or vivian.cinema < 6:
        return

    # 假设此处监听的是某种异常触发事件，或者通用技能事件
    # 如果是监听技能事件：
    if hasattr(event, "event_origin") and isinstance(event.event_origin, SkillNode):
        # 委托给薇薇安实例处理具体的 6 画逻辑判定
        if hasattr(vivian, "handle_cinema6_trigger"):
            vivian.handle_cinema6_trigger(event.event_origin, sim.tick)


# =============================================================================
# 协同攻击通用触发器
# =============================================================================
@BuffCallbackRepository.register(LOGIC_ID_COATTACK_TRIGGER)
def vivian_coattack_trigger(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    薇薇安通用协同攻击逻辑 (落羽生花)
    逻辑：
        监听特定技能（如 1221_E_EX_1），调用协同攻击管理器。
    """
    sim = buff.sim_instance
    if not hasattr(event, "event_origin") or not isinstance(event.event_origin, SkillNode):
        return
    skill_node = event.event_origin

    vivian = sim.char_data.find_char_obj(name="薇薇安")
    if not vivian:
        return

    # 调用协同管理器
    if hasattr(vivian, "coattack_manager"):
        vivian.coattack_manager.check_and_trigger(skill_node, sim.tick)


# =============================================================================
# 核心被动触发器
# =============================================================================
@BuffCallbackRepository.register(LOGIC_ID_CORE_PASSIVE_TRIGGER)
def vivian_core_passive_trigger(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    薇薇安核心被动逻辑：
    触发机制：【落羽生花】(1331_CoAttack_A) 命中处于异常状态的目标时，
    复制目标身上的异常状态，构造一个新的属性异常伤害(DirgeOfDestinyAnomaly)。
    """
    sim = buff.sim_instance
    vivian = buff.owner

    # 1. 验证事件来源
    if not hasattr(event, "event_origin") or not isinstance(event.event_origin, SkillNode):
        return
    skill_node = event.event_origin

    # 2. 筛选技能：必须是 落羽生花 (1331_CoAttack_A)
    if skill_node.skill_tag != "1331_CoAttack_A":
        return

    # 3. 获取敌人
    enemy = sim.ctx.current_enemy
    if not enemy:
        return

    # 4. 检查敌人是否处于异常状态
    if not enemy.dynamic.is_under_anomaly():
        return

    # 5. 获取当前激活的异常条 (Active Anomaly)
    active_anomalies = enemy.dynamic.get_active_anomaly()
    if not active_anomalies:
        return

    # 取第一个激活的异常条（遵循旧逻辑）
    active_anomaly_bar = active_anomalies[0]

    # 6. 构造 DirgeOfDestinyAnomaly (命运之歌异常)
    # 6.1 复制异常条
    copyed_anomaly = AnomalyBar.create_new_from_existing(active_anomaly_bar)
    if not copyed_anomaly.settled:
        copyed_anomaly.anomaly_settled()

    # 6.2 计算属性倍率 (参考旧文件 VivianCorePassiveTrigger.py 中的 ANOMALY_RATIO_MUL)
    # 0:物理, 1:火, 2:冰, 3:电, 4:以太, 5:冰(Frost)
    ANOMALY_RATIO_MUL = {
        0: 0.0075,
        1: 0.08,
        2: 0.0108,
        3: 0.032,
        4: 0.0615,
        5: 0.0108,
    }
    element_ratio = ANOMALY_RATIO_MUL.get(copyed_anomaly.element_type, 0)

    # 6.3 计算影画倍率 (2画提升)
    cinema_ratio = 1.3 if vivian.cinema >= 2 else 1.0

    # 6.4 计算薇薇安的实时异常精通 (AP)
    # 使用新版 Calculator 获取面板，dynamic_buff 传 None (自动从 BuffManager 获取)
    mul_data = MultiplierData(enemy_obj=enemy, dynamic_buff=None, character_obj=vivian)
    ap = Calculator.AnomalyMul.cal_ap(mul_data)

    # 6.5 计算最终倍率
    # 公式：(AP / 10) * 属性系数 * 影画系数
    final_ratio = (ap / 10) * element_ratio * cinema_ratio

    # 7. 创建并推送事件
    dirge_event = DirgeOfDestinyAnomaly(
        copyed_anomaly,
        active_by="1331",  # 薇薇安 ID
        sim_instance=sim,
    )
    dirge_event.anomaly_dmg_ratio = final_ratio

    # 推送到事件队列
    sim.schedule_data.event_list.append(dirge_event)

    if VIVIAN_REPORT:
        sim.schedule_data.change_process_state()
        print(
            f"【薇薇安核心被动】检测到【落羽生花】命中异常状态下的敌人，触发异放！倍率: {final_ratio:.2%}"
        )


# =============================================================================
# Dot 伤害触发器 (预言?)
# =============================================================================
@BuffCallbackRepository.register(LOGIC_ID_DOT_TRIGGER)
def vivian_dot_trigger(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    薇薇安 Dot (薇薇安的预言) 触发逻辑
    逻辑：
        当 1331_SNA_2 或 1331_CoAttack_A 命中处于异常状态的敌人时，
        给敌人施加名为 "ViviansProphecy" 的 Dot。
    """
    sim = buff.sim_instance

    # 1. 验证事件来源
    if not hasattr(event, "event_origin") or not isinstance(event.event_origin, SkillNode):
        return
    skill_node = event.event_origin

    # 2. 筛选技能：SNA_2 或 CoAttack_A
    if skill_node.skill_tag not in ["1331_SNA_2", "1331_CoAttack_A"]:
        return

    # 3. 获取敌人
    enemy = sim.ctx.current_enemy
    if not enemy:
        return

    # 4. 检查敌人是否处于异常状态
    if not enemy.dynamic.is_under_anomaly():
        return

    # 5. 施加 Dot (Buff)
    # 请确保此 ID 在 csv 中已定义
    target_buff_id = "ViviansProphecy"

    if hasattr(enemy, "buff_manager"):
        # Add_buff 会自动处理刷新逻辑（如果配置了 max_stack=1 且刷新策略正确）
        enemy.buff_manager.add_buff(target_buff_id, current_tick=sim.tick)

        if VIVIAN_REPORT:
            sim.schedule_data.change_process_state()
            print("【薇薇安核心被动】对敌人施加/刷新 Dot —— 薇薇安的预言")


# =============================================================================
# 羽毛 (Feather) 管理触发器
# =============================================================================
@BuffCallbackRepository.register(LOGIC_ID_FEATHER_TRIGGER)
def vivian_feather_trigger(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    薇薇安羽毛机制管理
    逻辑：
        监听事件，更新薇薇安的羽毛资源状态。
    """
    sim = buff.sim_instance
    vivian = buff.owner

    if not hasattr(vivian, "feather_manager"):
        return

    # 确保是技能事件
    if not hasattr(event, "event_origin"):
        return

    # 转发给羽毛管理器处理具体逻辑
    vivian.feather_manager.update(event, sim.tick)
