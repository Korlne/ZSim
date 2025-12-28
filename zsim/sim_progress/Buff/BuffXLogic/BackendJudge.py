from typing import TYPE_CHECKING

from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

# 逻辑ID
LOGIC_ID = "Backend_Judge"


@BuffCallbackRepository.register(LOGIC_ID)
def backend_judge(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    通用后台判定逻辑
    逻辑：
        检查 Buff 持有者是否为当前场上角色。
        如果持有者 != 场上角色 (即在后台)，则激活 Buff。
        否则 (在前台)，结束 Buff。
    """
    sim = buff.sim_instance
    owner = buff.owner  # Buff 的持有者/装备者

    if not owner:
        return

    # 1. 获取当前场上角色
    # 假设 sim.ctx 维护了上下文信息
    current_on_field_char = getattr(sim.ctx, "on_field_character", None)

    # 备用方案：如果 ctx 未直接提供对象，可能提供了 CID 或 Name
    if current_on_field_char is None:
        # 尝试从 name_box 获取 (原逻辑方式)
        # 假设 sim.init_data.name_box[0] 是当前角色名
        if hasattr(sim, "init_data") and hasattr(sim.init_data, "name_box"):
            current_name = sim.init_data.name_box[0]
            # 这里需要判断 owner.name 或 owner.id 是否匹配
            is_on_field = owner.name == current_name
        else:
            # 无法判定时默认不处理
            return
    else:
        is_on_field = owner == current_on_field_char

    # 2. 执行判定
    if not is_on_field:
        # 在后台 -> 激活
        if not buff.dy.active:
            buff.start(current_tick=sim.tick)
    else:
        # 在前台 -> 关闭
        if buff.dy.active:
            buff.end(current_tick=sim.tick)
