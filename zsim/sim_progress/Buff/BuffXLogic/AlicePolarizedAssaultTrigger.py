from copy import deepcopy
from typing import TYPE_CHECKING

from zsim.define import ALICE_REPORT
from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.data_struct import PolarizedAssaultEvent
from zsim.sim_progress.Preload import SkillNode

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

# 逻辑ID
LOGIC_ID = "Alice_Polarized_Assault_Trigger"

# 合法的触发技能标签
ALLOWED_SKILL_TAGS = ["1401_SNA_3", "1401_Q"]


@BuffCallbackRepository.register(LOGIC_ID)
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
    # 假设 event.event_origin 存放的是 SkillNode
    if not hasattr(event, "event_origin") or not isinstance(event.event_origin, SkillNode):
        return

    skill_node = event.event_origin

    # 2. 基础条件筛选
    if skill_node.skill_tag not in ALLOWED_SKILL_TAGS:
        return

    # 3. LastHit 判定
    if not skill_node.is_last_hit(tick=sim.tick):
        return

    # 4. 获取角色对象 (爱丽丝)
    alice_char = sim.char_data.find_char_obj(CID=1401)
    if not alice_char:
        return

    # 5. 特殊判定：2画以下大招不触发
    if skill_node.skill_tag == "1401_Q" and alice_char.cinema < 2:
        return

    # 6. 执行触发逻辑
    # 获取敌人对象
    enemy = sim.ctx.current_enemy
    if not enemy:
        return

    # 复制异常条数据 (原逻辑行为)
    # 注意：需确保 enemy.anomaly_bars_dict 结构存在
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
