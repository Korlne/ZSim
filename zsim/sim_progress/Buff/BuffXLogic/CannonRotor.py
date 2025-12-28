from typing import TYPE_CHECKING

from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.Load import LoadingMission
from zsim.sim_progress.Preload import SkillNode
from zsim.sim_progress.Preload.SkillsQueue import spawn_node

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

LOGIC_ID = "Cannon_Rotor"
SKILL_TAG_SUFFIX = "CannonRotorAdditionalDamage"


@BuffCallbackRepository.register(LOGIC_ID)
def cannon_rotor(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    加农转子 - 额外伤害触发
    逻辑：
        监听技能命中(SkillHit)。
        计算暴击率 (CritRate)，进行 RNG 判定。
        若命中，则生成一个额外的伤害事件 (SkillNode)。
    """
    sim = buff.sim_instance
    owner = buff.owner

    if not owner:
        return

    # 1. 验证事件源
    if not hasattr(event, "event_origin") or not isinstance(event.event_origin, SkillNode):
        return
    skill_node = event.event_origin

    # 2. 筛选条件
    if skill_node.char_name != owner.NAME:
        return

    # 必须是命中帧
    if not skill_node.is_hit_now(tick=sim.tick):
        return

    # 3. 暴击判定逻辑
    # 获取实时属性快照
    crit_rate = getattr(owner.statement, "CR", 0)  # 假设 CR 存储在 statement 中

    # RNG 判定
    rng = sim.rng_instance
    rand_val = rng.random_float()

    if rand_val > crit_rate:
        return

    # 4. 触发效果：生成额外伤害
    # 构造完整的 skill_tag
    whole_skill_tag = f"{owner.CID}_{SKILL_TAG_SUFFIX}"

    # 获取 preload 数据 (需确保 buff 只有引用或通过 sim 获取)
    # 这里假设 sim.preload_data 可用，或者从 skill_node 获取
    preload_skills = sim.preload_data.skills

    new_node = spawn_node(whole_skill_tag, sim.tick, preload_skills)

    # 启动任务并挂载
    mission = LoadingMission(new_node)
    mission.mission_start(sim.tick)
    new_node.loading_mission = mission

    # 推入事件队列
    sim.schedule_data.event_list.append(new_node)

    # 激活 Buff (用于标记或记录触发)
    buff.simple_start(current_tick=sim.tick)
