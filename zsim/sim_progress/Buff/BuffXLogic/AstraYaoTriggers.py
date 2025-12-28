from typing import TYPE_CHECKING

from zsim.define import ASTRAYAO_REPORT
from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.Preload import SkillNode

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

# =============================================================================
# 逻辑ID定义
# =============================================================================
LOGIC_ID_CHORD_MANAGER = "Astra_Yao_Chord_Manager_Trigger"
LOGIC_ID_CORE_PASSIVE = "Astra_Yao_Core_Passive_Atk_Bonus"
LOGIC_ID_IDYLLIC_CADENZA = "Astra_Yao_Idyllic_Cadenza"
LOGIC_ID_QUICK_ASSIST = "Astra_Yao_Quick_Assist_Manager_Trigger"


# =============================================================================
# 震音管理器触发器
# =============================================================================
@BuffCallbackRepository.register(LOGIC_ID_CHORD_MANAGER)
def astra_yao_chord_manager_trigger(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    耀嘉音 - 震音管理器触发器
    逻辑：
        监听技能开始(SkillStart)，若技能符合 trigger_buff_level 要求，
        调用 AstraYao.chord_manager.chord_trigger.try_spawn_chord_coattack。
    """
    sim = buff.sim_instance

    # 1. 获取事件源
    if not hasattr(event, "event_origin") or not isinstance(event.event_origin, SkillNode):
        return
    skill_node = event.event_origin

    # 2. 筛选条件
    if skill_node.skill.trigger_buff_level not in [5, 7, 8]:
        return

    # 3. 获取角色对象
    astra_char = sim.char_data.find_char_obj(CID=1311)
    if not astra_char:
        return

    # 4. 执行逻辑
    astra_char.chord_manager.chord_trigger.try_spawn_chord_coattack(
        current_tick=sim.tick,
        skill_node=skill_node,
    )

    if ASTRAYAO_REPORT:
        sim.schedule_data.change_process_state()
        print(f"检测到入场动作{skill_node.skill_tag}，尝试调用震音管理器，触发协同攻击！")


# =============================================================================
# 核心被动攻击力加成
# =============================================================================
@BuffCallbackRepository.register(LOGIC_ID_CORE_PASSIVE)
def astra_yao_core_passive_atk_bonus(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    耀嘉音 - 核心被动攻击力加成
    逻辑：
        在 Buff 激活或刷新时，根据持有者(owner)的实时攻击力计算层数 (0.35 * ATK)。
        刷新时延长持续时间。
    """
    sim = buff.sim_instance
    char = buff.owner

    if not char:
        return

    # 1. 基础参数
    core_passive_ratio = 0.35
    duration_added_per_active = 1200

    # 2. 计算层数
    static_atk = getattr(char.statement, "ATK", 0)
    target_count = min(int(static_atk * core_passive_ratio), buff.config.max_stacks)

    buff.dy.count = target_count

    # 3. 持续时间更新逻辑
    record_data = buff.dy.custom_data.get("update_info", {})
    current_tick = sim.tick
    last_end_tick = record_data.get("last_end_tick", -1)

    is_refresh = buff.dy.active and last_end_tick >= current_tick

    if is_refresh:
        new_end_tick = min(
            last_end_tick + duration_added_per_active, current_tick + buff.config.duration
        )
        buff.dy.end_tick = new_end_tick
    else:
        buff.dy.end_tick = current_tick + duration_added_per_active

    # 4. 更新记录
    buff.dy.custom_data["update_info"] = {
        "last_start_tick": current_tick,
        "last_end_tick": buff.dy.end_tick,
    }

    if ASTRAYAO_REPORT:
        sim.schedule_data.change_process_state()
        print(
            f"核心被动触发器激活！为{char.NAME}添加攻击力Buff（{target_count}点）！"
            f"持续时间: {current_tick} -> {buff.dy.end_tick}"
        )


# =============================================================================
# 咏叹华彩加成判定
# =============================================================================
@BuffCallbackRepository.register(LOGIC_ID_IDYLLIC_CADENZA)
def astra_yao_idyllic_cadenza(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    耀嘉音 - 咏叹华彩加成判定
    逻辑：
        实时检测耀嘉音的资源状态。如果资源[1]为真，则激活Buff，否则关闭。
    """
    sim = buff.sim_instance

    # 1. 获取角色对象
    char = sim.char_data.find_char_obj(CID=1311)
    if not char:
        return

    # 2. 获取资源状态
    resources = char.get_resources()
    is_active = bool(resources[1]) if len(resources) > 1 else False

    # 3. 同步 Buff 状态
    if is_active:
        if not buff.dy.active:
            buff.start(current_tick=sim.tick)
    else:
        if buff.dy.active:
            buff.end(current_tick=sim.tick)


# =============================================================================
# 快速支援管理器触发器
# =============================================================================
@BuffCallbackRepository.register(LOGIC_ID_QUICK_ASSIST)
def astra_yao_quick_assist_manager_trigger(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    耀嘉音 - 快支管理器触发器
    逻辑：
        监听技能命中(SkillHit)，将当前的 skill_node 传递给耀嘉音的 quick_assist_trigger_manager。
    """
    sim = buff.sim_instance

    # 1. 获取事件源
    if not hasattr(event, "event_origin") or not isinstance(event.event_origin, SkillNode):
        return
    skill_node = event.event_origin

    # 2. 获取角色对象
    char = sim.char_data.find_char_obj(CID=1311)
    if not char:
        return

    # 3. 执行逻辑
    char.chord_manager.quick_assist_trigger_manager.update_myself(
        current_tick=sim.tick, skill_node=skill_node
    )
