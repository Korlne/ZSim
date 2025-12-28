from typing import TYPE_CHECKING

from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

# 逻辑ID
LOGIC_ID = "Astra_Yao_Idyllic_Cadenza"


@BuffCallbackRepository.register(LOGIC_ID)
def astra_yao_idyllic_cadenza(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    耀嘉音 - 咏叹华彩加成判定
    逻辑：
        实时检测耀嘉音的资源状态（资源[1]）。
        如果资源[1]存在/为真，则激活Buff，否则关闭。
    """
    sim = buff.sim_instance

    # 1. 获取角色对象 (耀嘉音)
    # 假设 buff.owner 就是耀嘉音，或者通过 CID 查找
    char = sim.char_data.find_char_obj(CID=1311)
    if not char:
        return

    # 2. 获取资源状态
    # 对应原逻辑: self.record.char.get_resources()[1]
    resources = char.get_resources()
    # 确保索引安全
    is_active = bool(resources[1]) if len(resources) > 1 else False

    # 3. 同步 Buff 状态
    if is_active:
        if not buff.dy.active:
            buff.start(current_tick=sim.tick)
    else:
        if buff.dy.active:
            buff.end(current_tick=sim.tick)
