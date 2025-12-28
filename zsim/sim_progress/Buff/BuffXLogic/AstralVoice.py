from typing import TYPE_CHECKING

from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.Preload import LoadingMission, SkillNode

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

# 逻辑ID
LOGIC_ID = "Astral_Voice"

# 触发器Buff的名称 (需与配置一致)
TRIGGER_BUFF_NAME = "Buff-驱动盘-静听嘉音-嘉音"


@BuffCallbackRepository.register(LOGIC_ID)
def astral_voice(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    静听嘉音 - 套装效果逻辑
    逻辑：
        监听技能开始(SkillStart)。
        如果持有者身上激活了“嘉音”Buff (trigger_buff)，且当前技能 trigger_buff_level == 7，
        则激活本Buff (增伤部分)，并同步层数。
    """
    sim = buff.sim_instance
    owner = buff.owner

    if not owner:
        return

    # 1. 解析事件中的技能节点
    skill_node = None
    if hasattr(event, "event_origin"):
        origin = event.event_origin
        if isinstance(origin, SkillNode):
            skill_node = origin
        elif isinstance(origin, LoadingMission):
            skill_node = origin.mission_node

    if skill_node is None:
        return

    # 2. 查找触发器 Buff (trigger_buff)
    # 假设 owner.buff_manager 提供了按名称查找的方法，或者通过 sim.buff_manager 查找
    # 这里使用通用查找逻辑
    trigger_buff = None
    # 尝试从 owner 的动态 Buff 列表中查找
    # 注意：具体实现需根据 Character 或 BuffManager 的 API 调整
    if hasattr(owner, "buffs"):
        for b in owner.buffs:
            if b.config.name == TRIGGER_BUFF_NAME:
                trigger_buff = b
                break

    # 如果找不到 trigger_buff，说明套装未完整生效
    if not trigger_buff:
        return

    # 3. 判定逻辑
    # 条件1: 触发器Buff必须激活
    # 条件2: 技能的 trigger_buff_level 必须为 7
    if trigger_buff.dy.active and skill_node.skill.trigger_buff_level == 7:
        # 激活本 Buff
        buff.start(current_tick=sim.tick)

        # 同步层数
        buff.dy.count = trigger_buff.dy.count

        # 原逻辑中的 simple_start 和 update_to_buff_0 已被 buff.start() 和直接赋值替代
    else:
        pass
