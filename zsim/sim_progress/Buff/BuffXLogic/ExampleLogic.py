from typing import TYPE_CHECKING, Optional

from zsim.define import ALICE_REPORT, HUGO_REPORT

# ==============================================================================
# 1. 标准导入 (Standard Imports)
# ==============================================================================
# 核心注册器
from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository

# 数据结构与工具
from zsim.sim_progress.Preload import SkillNode
from zsim.sim_progress.ScheduledEvent.Calculator import Calculator, MultiplierData
from zsim.sim_progress.zsim_event_system.zsim_events.base_zsim_event import (
    BaseZSimEventContext,
    ZSimEventABC,
)

# 事件定义
from zsim.sim_progress.zsim_event_system.zsim_events.skill_event import SkillExecutionEvent

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff

# ==============================================================================
# 2. 逻辑 ID 定义
# ==============================================================================
LOGIC_MANAGER_DELEGATE = "Example_Manager_Delegate"  # 场景1: 代理给Manager
LOGIC_RNG_TRIGGER = "Example_RNG_Trigger"  # 场景2: 概率触发
LOGIC_CUSTOM_EVENT = "Example_Custom_Event"  # 场景3: 构造自定义事件
LOGIC_COMPLEX_FOLLOWUP = "Example_Complex_FollowUp"  # 场景4: 复杂计算与追击
LOGIC_RESOURCE_EXIT = "Example_Resource_Exit"  # 场景5: 资源耗尽退出


# ==============================================================================
# 3. 辅助函数
# ==============================================================================
def get_skill_node(event: ZSimEventABC) -> Optional[SkillNode]:
    """安全地从事件中提取 SkillNode"""
    if not hasattr(event, "event_origin"):
        return None
    origin = event.event_origin
    # 情况A: event_origin 直接是 SkillNode
    if isinstance(origin, SkillNode):
        return origin
    # 情况B: event_origin 是 SkillEvent (SkillExecutionEvent的情况), 再下一层是 SkillNode
    if hasattr(origin, "event_origin") and isinstance(origin.event_origin, SkillNode):
        return origin.event_origin
    return None


# ==============================================================================
# 场景 1: 管理器代理 (Manager Delegation)
# 逻辑: 监听到事件后，不直接处理业务，而是将数据转发给角色身上的某个 Manager 处理。
# ==============================================================================
@BuffCallbackRepository.register(LOGIC_MANAGER_DELEGATE)
def example_manager_delegate(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    # 1. 必须是技能执行事件
    if not isinstance(event, SkillExecutionEvent):
        return

    # 2. 提取 SkillNode
    skill_node = get_skill_node(event)
    if not skill_node:
        return

    # 3. 获取角色特有的 Manager (需确保角色有此属性)
    char = buff.owner
    # 示例：假设角色有 chord_manager (如耀嘉音)
    if hasattr(char, "chord_manager"):
        # 转发数据
        char.chord_manager.quick_assist_trigger_manager.update_myself(
            current_tick=context.timer.tick, skill_node=skill_node
        )


# ==============================================================================
# 场景 2: 概率触发 (Probabilistic Trigger)
# 逻辑: 基于暴击率或其他属性计算概率，通过 RNG 判定是否触发。
# ==============================================================================
@BuffCallbackRepository.register(LOGIC_RNG_TRIGGER)
def example_rng_trigger(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    if not isinstance(event, SkillExecutionEvent):
        return

    skill_node = get_skill_node(event)
    if not skill_node:
        return

    # 1. 筛选条件 (如：必须是普攻, trigger_buff_level==0)
    if getattr(skill_node.skill, "trigger_buff_level", -1) != 0:
        return

    # 2. 必须是自己的技能
    if str(buff.owner.base_code) not in event.event_message.skill_tag:
        return

    # 3. 准备计算数据
    target = getattr(event, "target", None) or buff.sim_instance.enemy_group[1]
    mul_data = MultiplierData(enemy_obj=target, character_obj=buff.owner)

    # 4. 计算概率 (这里以暴击率为例)
    crit_rate = Calculator.RegularMul.cal_crit_rate(mul_data)

    # 5. RNG 判定
    rng = buff.sim_instance.rng_instance
    if rng.random_float() <= crit_rate:
        # 触发成功：添加层数
        buff.add_stack(1)


# ==============================================================================
# 场景 3: 自定义事件派发 (Custom Event Dispatch)
# 逻辑: 满足条件时，深度复制异常条，构造一个特殊的事件对象并推入队列。
# ==============================================================================
@BuffCallbackRepository.register(LOGIC_CUSTOM_EVENT)
def example_custom_event(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    if not isinstance(event, SkillExecutionEvent):
        return

    skill_node = get_skill_node(event)
    if not skill_node:
        return

    # 1. 筛选特定技能
    if skill_node.skill_tag not in ["1401_SNA_3", "1401_Q"]:
        return

    # 2. Last Hit 判定
    # SkillExecutionEvent 提供了 hit_times，context 提供了 hitted_count
    if hasattr(context, "hitted_count") and hasattr(event, "hit_times"):
        if context.hitted_count != event.hit_times:
            return

    # 3. 构造自定义事件 (以 PolarizedAssaultEvent 为例)
    target = getattr(event, "target", None)
    if not target:
        return

    # 模拟获取异常条并复制
    # if 0 not in getattr(target, "anomaly_bars_dict", {}): return
    # from copy import deepcopy
    # copied_bar = deepcopy(target.anomaly_bars_dict[0])
    # copied_bar.activated_by = skill_node

    # pa_event = PolarizedAssaultEvent(
    #     execute_tick=context.timer.tick,
    #     anomlay_bar=copied_bar,
    #     char_instance=buff.owner,
    #     skill_node=skill_node
    # )

    # 4. 推送事件
    # if hasattr(context, "push_event"):
    #     context.push_event(pa_event)

    if ALICE_REPORT:
        print("示例触发: 自定义事件构造逻辑已执行")


# ==============================================================================
# 场景 4: 复杂计算与追击 (Complex Calculation & Follow-up)
# 逻辑: 敌人失衡时，计算倍率，并生成一个新的技能节点。
# ==============================================================================
@BuffCallbackRepository.register(LOGIC_COMPLEX_FOLLOWUP)
def example_complex_followup(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    if not isinstance(event, SkillExecutionEvent):
        return
    skill_node = get_skill_node(event)
    if not skill_node:
        return

    # 1. 筛选触发源 (强化特殊技)
    if getattr(skill_node.skill, "trigger_buff_level", 0) != 2:
        return

    # 2. 检查敌人失衡状态
    target = getattr(event, "target", None)
    if not target or not getattr(target.dynamic, "stun", False):
        return

    # 3. 防止单次技能多次触发 (使用 custom_data)
    state = buff.dy.custom_data.setdefault("followup_state", {"last_uuid": ""})
    current_uuid = event.event_message.event_id
    if state["last_uuid"] == current_uuid:
        return
    state["last_uuid"] = current_uuid

    # 4. 计算数值
    rest_tick = target.get_stun_rest_tick()
    ratio = 1000 + min(300, rest_tick) / 60 * 280

    # 5. 动态添加数值 Buff
    target_buff_name = "Buff-角色-雨果-决算倍率增幅"

    # 假设是要给自己添加 Buff
    if hasattr(buff.owner, "buff_manager"):
        # 调用 Manager 添加 Buff。具体 API 取决于 BuffManager 的实现
        # 这里假设 add_buff 返回 Buff 对象，或者通过 add_stack 更新层数/数值
        new_buff = buff.owner.buff_manager.add_buff(target_buff_name)

        # 如果该 Buff 是数值堆叠型 (Stackable/Count based)，更新其层数或数值
        # 注意: Buff系统重构后，value 通常由 Effect 定义，但如果是动态数值 Buff，
        # 可能需要通过 update_stack 或修改 custom_data 来实现
        if new_buff:
            # 假设这是一个层数代表数值的 Buff
            # 先清空旧数值（如果设计是不叠加的话）或直接设置
            # 这里简单演示调用 add_stack
            # 实际数值传递可能需要更复杂的 Effect 参数传递机制，视具体 Buff 定义而定
            if hasattr(new_buff, "add_stack"):
                # 如果逻辑是设定为 ratio，可能需要先 reset 再 add，或者 diff
                # 这里仅做示例:
                new_buff.dy.count = int(ratio)  # 强制设定
                # 或者: new_buff.add_stack(int(ratio))
    else:
        if HUGO_REPORT:
            print(f"Error: Owner {buff.owner.name} does not have buff_manager.")

    # 6. 生成并调度追击技能
    # 假设从 sim_instance 获取 preload 数据
    preload_data = getattr(buff.sim_instance, "preload_data", None)
    if not preload_data:
        return

    # 导入技能生成工具
    # from zsim.sim_progress.Preload.SkillsQueue import spawn_node

    # follow_up_node = spawn_node(
    #     "1291_CorePassive_E_EX", # 追击技能 Tag
    #     context.timer.tick,
    #     preload_data.skills
    # )

    # follow_up_node.loading_mission = LoadingMission(follow_up_node)
    # follow_up_node.loading_mission.mission_start(context.timer.tick)

    # if hasattr(context, "push_event"):
    #     context.push_event(follow_up_node)

    if HUGO_REPORT:
        print(f"示例触发: 追击判定通过，倍率 {ratio:.2f}%")


# ==============================================================================
# 场景 5: 资源耗尽退出 (Resource Depletion Exit)
# 逻辑: 由于没有 ResourceChangeEvent，我们在每次技能触发时检查资源。
# ==============================================================================
@BuffCallbackRepository.register(LOGIC_RESOURCE_EXIT)
def example_resource_exit(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    替代方案：监听 SkillExecutionEvent，检查资源状态。
    """
    # 仅在技能执行时检查（频率较高，覆盖面广）
    if not isinstance(event, SkillExecutionEvent):
        return

    # 1. 获取资源
    # 假设 get_resources 返回 [hp, energy, decibel, ...]
    if not hasattr(buff.owner, "get_resources"):
        return

    resources = buff.owner.get_resources()
    if not resources or len(resources) < 2:
        return

    energy = resources[1]  # 假设索引 1 是能量

    # 2. 检查退出条件
    if energy <= 0:
        # 3. 执行退出
        buff.dy.active = False
        buff.dy.count = 0

        # 可选：将持续时间置零以在下一帧清理
        buff.dy.duration = 0

        # print(f"{buff.ft.name} 因能量耗尽失效")
