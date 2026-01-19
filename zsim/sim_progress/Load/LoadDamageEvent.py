from zsim.sim_progress.Report import report_to_log

# [Removed] import Dot
from .loading_mission import LoadingMission


def SpawnDamageEvent(mission: LoadingMission, event_list: list):
    """
    负责往event_list中添加伤害生成事件，添加的内容是实例：
    目前主要是 SkillNode 的实例 (来自 LoadingMission)。
    """
    if isinstance(mission, LoadingMission):
        if mission.hitted_count > mission.mission_node.hit_times:
            raise ValueError(
                f"{mission.mission_tag}目前是第{mission.hitted_count}，最多{mission.mission_node.hit_times}"
            )
        mission.hitted_count += 1
        event_list.append(mission)

    # [Removed] Legacy Dot handling
    # elif isinstance(mission, Dot.Dot): ...


# [Removed] ProcessTimeUpdateDots
# [Removed] ProcessHitUpdateDots
# [Removed] ProcessFreezLikeDots


def DamageEventJudge(
    timetick: int,
    load_mission_dict: dict,
    enemy,
    event_list: list,
    char_obj_list: list,
    **kwargs,
):
    """
    DamageEvent的Judge函数：轮询load_mission_dict，判断是否应生成Hit事件。
    并且当Hit时间生成时，将对应的实例添加到event_list中。

    注意：Dot类逻辑已移交 Buff 系统管理，不再此处轮询。
    """
    # 处理 Load.Mission 任务
    process_overtime_mission(timetick, load_mission_dict)
    for mission in load_mission_dict.values():
        if not isinstance(mission, LoadingMission):
            raise TypeError(f"{mission}不是LoadingMission类！")
        if mission.is_hit_now(timetick):
            SpawnDamageEvent(mission, event_list)

    # [Refactor] 旧的 Dot 轮询逻辑已移除。
    # 所有的 Dot 现在都是 Buff，应该由 BuffManager 负责在 Tick 时触发相应的 Effect 或 Event。
    # 如果有特定机制需要在 Load 阶段生成 Event，应通过 Buff 的 Handler 注入到 event_list 中，
    # 而不是在这里显式调用 ProcessTimeUpdateDots。


def process_overtime_mission(tick: int, Load_mission_dict: dict):
    """去除过期任务！"""
    to_remove = []
    for key, mission in Load_mission_dict.items():
        if not isinstance(mission, LoadingMission):
            continue
        mission.check_myself(tick)
        if not mission.mission_active_state:
            if key not in to_remove:
                to_remove.append(key)
    for key in to_remove:
        report_to_log(
            f"[Skill LOAD]:{tick}:{Load_mission_dict[key].mission_tag}已经结束,已从Load中移除",
            level=2,
        )
        Load_mission_dict.pop(key)
