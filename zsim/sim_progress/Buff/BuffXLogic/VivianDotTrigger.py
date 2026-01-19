from typing import TYPE_CHECKING

from zsim.define import VIVIAN_REPORT
from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository
from zsim.sim_progress.Load import LoadingMission
from zsim.sim_progress.Preload import SkillNode
from zsim.sim_progress.Update.UpdateAnomaly import spawn_normal_dot
from zsim.sim_progress.zsim_event_system.zsim_events.skill_event import SkillExecutionEvent

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events.base_zsim_event import (
        BaseZSimEventContext,
        ZSimEventABC,
    )

LOGIC_ID = "Buff-角色-薇薇安-DOT赋予"


@BuffCallbackRepository.register(LOGIC_ID)
def vivian_dot_trigger(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """
    薇薇安的预言Dot触发器。
    SNA_2 或 协同攻击 命中异常敌人时施加。
    """
    if not isinstance(event, SkillExecutionEvent):
        return

    skill_node = getattr(event, "event_origin", None)
    if not isinstance(skill_node, SkillNode):
        return

    # 1. 筛选技能
    if skill_node.skill_tag not in ["1331_SNA_2", "1331_CoAttack_A"]:
        return

    # 2. 必须命中
    tick = context.timer.tick
    if not skill_node.loading_mission.is_hit_now(tick):
        return

    # 3. 敌人必须处于异常状态
    target = getattr(event, "target", None) or buff.sim_instance.enemy_group[1]
    if not target.dynamic.is_under_anomaly():
        return

    # 4. 避免重复添加 (检测是否已有 Dot)
    if target.find_dot("ViviansProphecy") is not None:
        return

    # 5. 生成并施加 Dot
    dot = spawn_normal_dot("ViviansProphecy", sim_instance=buff.sim_instance)
    dot.start(tick)

    # 初始化 Dot 的 LoadingMission (用于伤害结算)
    dot.skill_node_data.loading_mission = LoadingMission(dot.skill_node_data)
    dot.skill_node_data.loading_mission.mission_start(tick)

    # 添加到敌人 Dot 列表和事件队列
    target.dynamic.dynamic_dot_list.append(dot)
    if hasattr(buff.sim_instance, "event_list"):
        buff.sim_instance.event_list.append(dot.skill_node_data)

    if VIVIAN_REPORT:
        print("核心被动：薇薇安对敌人施加Dot——薇薇安的预言")
