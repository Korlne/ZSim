from typing import TYPE_CHECKING

from zsim.define import VIVIAN_REPORT
from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.Load import LoadingMission
from zsim.sim_progress.Preload import SkillNode
from zsim.sim_progress.zsim_event_system.zsim_events.skill_event import SkillExecutionEvent

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events.base_zsim_event import (
        BaseZSimEventContext,
        ZSimEventABC,
    )

LOGIC_ID = "Buff-角色-薇薇安-落雨生花触发器"


@BuffCallbackRepository.register(LOGIC_ID)
def vivian_coattack_trigger(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    薇薇安的协同攻击（落雨生花）触发器。
    检测到队友释放强化E并且第一跳命中时触发。
    """
    if not isinstance(event, SkillExecutionEvent):
        return

    skill_node = event.event_origin
    # 兼容性处理：如果origin是SkillNode或LoadingMission
    if isinstance(skill_node, LoadingMission):
        skill_node = skill_node.mission_node

    if not isinstance(skill_node, SkillNode):
        return

    # 1. 过滤：非强化E技能 (trigger_buff_level != 2)
    # 注意：此处假设队友的强化E trigger_buff_level 为 2
    if getattr(skill_node.skill, "trigger_buff_level", -1) != 2:
        return

    # 2. 过滤：非第一跳
    tick = context.timer.tick
    if not skill_node.loading_mission.is_first_hit(tick):
        return

    # 3. 状态管理：防止同一技能重复触发
    state = buff.dy.custom_data
    last_uuid = state.get("last_update_node_uuid", None)

    should_trigger = False

    # 判定逻辑
    if last_uuid is None:
        should_trigger = True
    elif skill_node.UUID != last_uuid:
        # 不同技能，进入特殊判定 (JUDGE_MAP逻辑)
        # 1221_E_EX_1 (柳的招式): 需要判断前一个节点的结束时间
        # 但在新系统中，难以直接获取"上一个节点对象"，这里简化逻辑：
        # 如果 UUID 不同且是强化E第一跳，通常视为新动作

        # 还原原逻辑中的特殊映射判断
        if skill_node.skill_tag == "1221_E_EX_1":
            # 检查上一个记录的结束时间
            last_end_tick = state.get("last_update_node_end_tick", 0)
            if last_end_tick >= tick:
                should_trigger = True
            else:
                should_trigger = False
        elif skill_node.skill_tag == "1221_E_EX_2":
            should_trigger = False
        else:
            should_trigger = True
    else:
        # 同一技能，不触发
        return

    if should_trigger:
        # 更新状态
        state["last_update_node_uuid"] = skill_node.UUID
        state["last_update_node_end_tick"] = getattr(skill_node, "end_tick", tick)
        state["last_update_skill_tag"] = skill_node.skill_tag

        # 执行效果：生成落雨生花
        char = buff.owner
        if not hasattr(char, "feather_manager"):
            return

        coattack_skill_tag = char.feather_manager.spawn_coattack()

        if coattack_skill_tag is None:
            if VIVIAN_REPORT:
                print(f"【落雨生花】触发器：豆子不够，无法触发。队友技能：{skill_node.skill_tag}")
            return

        # 添加协同攻击到队列
        preload_data = getattr(buff.sim_instance, "preload_data", None)
        if preload_data:
            input_tuple = (coattack_skill_tag, False, 0)
            preload_data.external_add_skill(input_tuple)

            if VIVIAN_REPORT:
                print(f"【落雨生花】触发器：成功触发！响应队友技能：{skill_node.skill_tag}")
