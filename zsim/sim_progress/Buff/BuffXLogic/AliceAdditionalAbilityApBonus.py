from typing import TYPE_CHECKING

from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

# 定义逻辑ID，需与 buff_effect.csv 中的 logic_id 保持一致
LOGIC_ID = "Alice_Additional_Ability_Ap_Bonus"


@BuffCallbackRepository.register(LOGIC_ID)
def alice_additional_ability_ap_bonus(
    buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
):
    """
    爱丽丝额外能力：异常掌控转精通
    逻辑：
        读取爱丽丝实时异常掌控(AM)，根据公式 (AM - 140) * 1.6 计算Buff层数。
        直接从 Character.statement 对象中获取维护好的实时属性。

    触发建议：
        建议在 SkillStart, SkillHit 或 BuffStart 时触发，以保证属性随战斗变化实时更新。
    """
    sim = buff.sim_instance

    # 1. 获取爱丽丝对象 (通过CID查找)
    alice_char = sim.char_data.find_char_obj(CID=1401)
    if not alice_char:
        return

    # 2. 获取实时异常掌控 (AM)
    # 依据 Character 类结构，statement 对象维护了属性快照
    # 如果 Character 尚未实现自动更新 statement，则此处获取的是初始化时的值
    current_am = getattr(alice_char.statement, "AM", 0)

    # 3. 计算转化层数
    if current_am < 140:
        target_count = 0
    else:
        trans_ratio = 1.6
        target_count = int((current_am - 140) * trans_ratio)

    # 4. 同步 Buff 状态
    # 如果计算出的层数 > 0，确保 Buff 处于激活状态
    if target_count > 0:
        if not buff.dy.active:
            buff.start(current_tick=sim.tick)

        # 更新层数 (避免重复赋值)
        if buff.dy.count != target_count:
            buff.dy.count = target_count
            # print(f"[Alice AP Bonus] AM:{current_am} -> Stacks updated to {target_count}")

    else:
        # 如果层数为 0，结束 Buff
        if buff.dy.active:
            buff.end(current_tick=sim.tick)
            buff.dy.count = 0
