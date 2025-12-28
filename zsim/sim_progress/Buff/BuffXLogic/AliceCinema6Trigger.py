from typing import TYPE_CHECKING

from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

# 定义逻辑ID，需与 buff_effect.csv 中的 logic_id 对应
LOGIC_ID = "Alice_Cinema6_Trigger"


@BuffCallbackRepository.register(LOGIC_ID)
def alice_c6_trigger(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    爱丽丝6画额外攻击逻辑：
    在【决胜】状态下，队友的攻击命中会触发爱丽丝的额外攻击。
    """
    sim = buff.sim_instance

    # 1. 确保事件类型是技能命中
    # 在新的事件系统中，通常通过 event_type 或 isinstance 判断
    # 这里监听的是 SkillHit 事件
    if not hasattr(event, "event_origin") or not event.event_origin:
        return

    skill_node = event.event_origin  # event_origin 是 SkillNode

    # 2. 获取爱丽丝对象
    # buff 的 owner 或者通过 CID 查找
    alice_char = sim.char_data.find_char_obj(CID=1401)
    if not alice_char:
        return

    # 3. 过滤条件
    # 3.1 过滤掉爱丽丝自己的技能
    if skill_node.char_name == alice_char.NAME:
        return

    # 3.2 检查爱丽丝是否处于决胜状态 (victory_state)
    # 假设 Alice 类有这个属性，或者存储在 char.info 中
    if not getattr(alice_char, "victory_state", False):
        return

    # 3.3 过滤掉非命中帧 (事件系统通常只在命中时分发 SkillHit，这里做二次确认)
    if not skill_node.is_hit_now(tick=sim.tick):
        return

    # 4. CD 检查 (内置 1秒/60tick CD)
    # 假设 CD 为 0.5秒 或 1秒，此处沿用旧逻辑的 check_cd
    # 我们使用 buff.dy.custom_data 来存储上一次触发时间
    last_trigger = buff.dy.custom_data.get("last_c6_trigger", -9999)
    # 假设CD是 60 tick (需确认具体数值)
    cd_limit = 60

    if sim.tick - last_trigger < cd_limit:
        return

    # 5. 执行逻辑：触发额外攻击
    # spawn_extra_attack 是 Alice 角色类的方法
    if hasattr(alice_char, "spawn_extra_attack"):
        alice_char.spawn_extra_attack()
        # 更新 CD
        buff.dy.custom_data["last_c6_trigger"] = sim.tick
