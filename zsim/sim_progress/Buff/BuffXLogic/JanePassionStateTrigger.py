from typing import TYPE_CHECKING

from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

# 定义逻辑ID
LOGIC_ID = "Jane_Passion_State_Trigger"


@BuffCallbackRepository.register(LOGIC_ID)
def jane_passion_state_trigger(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    简 - 狂热状态触发器
    逻辑：
        监听简的狂热状态(Passion State)，同步控制 Buff 的激活与关闭。
        当狂热状态为 True 时激活 Buff，否则关闭。
    """
    sim = buff.sim_instance

    # 1. 获取简对象
    jane_char = sim.char_data.find_char_obj(CID=1261)
    if not jane_char:
        return

    # 2. 获取狂热状态
    # get_special_stats 返回特定机制的状态字典
    special_stats = jane_char.get_special_stats()
    # 根据 Jane.py 的实现，键名通常为中文或特定标识，此处假设为 "狂热状态"
    is_passion_state = special_stats.get("狂热状态", False)

    # 3. 同步 Buff 状态
    if is_passion_state:
        if not buff.dy.active:
            buff.start(current_tick=sim.tick)
    else:
        if buff.dy.active:
            buff.end(current_tick=sim.tick)
