from copy import deepcopy
from typing import TYPE_CHECKING

from zsim.define import ELEMENT_TYPE_MAPPING
from zsim.models.event_enums import ListenerBroadcastSignal as LBS
from zsim.sim_progress.anomaly_bar import AnomalyBar
from zsim.sim_progress.anomaly_bar.CopyAnomalyForOutput import (
    Disorder,
    NewAnomaly,
    PolarityDisorder,
)

# [New Architecture] 移除旧的策略和Dot基类
# from zsim.sim_progress.Buff.BuffAddStrategy import buff_add_strategy
# from zsim.sim_progress.Dot.BaseDot import Dot

if TYPE_CHECKING:
    from zsim.sim_progress.Buff import Buff
    from zsim.sim_progress.Preload import SkillNode
    from zsim.simulator.simulator_class import Simulator


def spawn_output(anomaly_bar, mode_number, sim_instance: "Simulator", **kwargs):
    """
    该函数用于抛出一个新的属性异常类 (Event Object, 并非Buff)
    """
    if not isinstance(anomaly_bar, AnomalyBar):
        raise TypeError(f"{anomaly_bar}不是AnomalyBar类！")
    skill_node = kwargs.get("skill_node", None)

    # 先处理快照，使其除以总权值。
    anomaly_bar.anomaly_settled() if mode_number in [0] else None

    output: "AnomalyBar | None" = None
    if mode_number == 0:
        output = NewAnomaly(anomaly_bar, active_by=skill_node, sim_instance=sim_instance)
    elif mode_number == 1:
        output = Disorder(anomaly_bar, active_by=skill_node, sim_instance=sim_instance)
    elif mode_number == 2:
        polarity_ratio = kwargs.get("polarity_ratio", None)
        if polarity_ratio is None:
            raise ValueError(
                "在调用spawn_output函数的模式二（mode_number=2）、企图生成一个极性紊乱对象时，并未传入必须的参数polarity_ratio！"
            )
        output = PolarityDisorder(
            anomaly_bar, polarity_ratio, active_by=skill_node, sim_instance=sim_instance
        )
    if output is None:
        raise ValueError("在调用spawn_output函数时，未正确生成一个AnomalyBar实例！")
    # 广播事件
    if mode_number in [1, 2]:
        sim_instance.listener_manager.broadcast_event(event=output, signal=LBS.DISORDER_SPAWN)
    return output


def anomaly_effect_active(
    bar: AnomalyBar,
    timenow: int,
    enemy,
    new_anomaly,
    element_type,
    sim_instance: "Simulator",
):
    """
    创建属性异常附带的 debuff 和 dot (现统一为 Buff)。
    使用 BuffManager 进行管理。
    """
    # 1. 添加伴随 Debuff
    if bar.accompany_debuff:
        for debuff_id in bar.accompany_debuff:
            # [Refactor] 使用 BuffManager
            if hasattr(enemy, "buff_manager"):
                enemy.buff_manager.add_buff(debuff_id, current_tick=timenow)

    # 2. 添加伴随 Dot (异常状态 Buff)
    if bar.accompany_dot:
        # [Refactor] Dot 现在是 Buff。bar.accompany_dot 应该是 BuffID。
        # 旧逻辑是删除同名 Dot，新 BuffManager.add_buff 会自动处理刷新/叠层。
        # 如果异常状态是“单例且刷新”机制，BuffManager 默认支持。
        if hasattr(enemy, "buff_manager"):
            dot_buff_id = bar.accompany_dot
            enemy.buff_manager.add_buff(dot_buff_id, current_tick=timenow)

            # [Refactor] 注入异常快照数据
            # 由于 add_buff 不直接返回对象（视实现而定，假设遵循提供的 BuffManager 代码），
            # 我们需要获取它并注入数据。
            # 注意：如果 BuffManager 尚未实例化该 Buff (例如被抵抗)，get_buff 可能返回 None
            dot_buff = enemy.buff_manager.get_buff(dot_buff_id)
            if dot_buff:
                # 将快照信息注入 custom_data，供 Effect 计算使用
                dot_buff.dy.custom_data["anomaly_snapshot"] = new_anomaly
                # 标记该 Buff 属于异常类 (用于紊乱清除)
                dot_buff.dy.custom_data["is_anomaly_dot"] = True


def update_anomaly(
    element_type: int,
    enemy,
    time_now: int,
    event_list: list,
    char_obj_list: list,
    sim_instance: "Simulator",
    skill_node: "SkillNode",
    dynamic_buff_dict: dict[str, list["Buff"]],
    **kwargs,
):
    """
    Schedule阶段的SkillEvent分支内运行。
    判断异常触发：新建、替换或紊乱。
    """
    bar: AnomalyBar = enemy.anomaly_bars_dict[skill_node.element_type]
    if not isinstance(bar, AnomalyBar):
        raise TypeError(f"{type(bar)}不是Anomaly类！")

    active_anomaly_check, active_anomaly_list, last_anomaly_element_type = check_anomaly_bar(enemy)

    # 获取当前最大值
    bar.max_anomaly = getattr(
        enemy, f"max_anomaly_{enemy.trans_element_number_to_str[element_type]}"
    )

    if bar.current_anomaly >= bar.max_anomaly:
        bar.ready_judge(time_now)
        if bar.ready:
            # 触发异常
            sim_instance.decibel_manager.update(skill_node=skill_node, key="anomaly")
            bar.change_info_cause_active(
                time_now, dynamic_buff_dict=dynamic_buff_dict, skill_node=skill_node
            )
            enemy.update_max_anomaly(element_type)

            active_bar = deepcopy(bar)
            enemy.dynamic.active_anomaly_bar_dict[element_type] = active_bar

            # 广播
            sim_instance.listener_manager.broadcast_event(event=active_bar, signal=LBS.ANOMALY)
            if active_bar.element_type in [0]:
                sim_instance.listener_manager.broadcast_event(
                    event=active_bar, signal=LBS.ASSAULT_SPAWN
                )

            # --- 分支判断 ---
            if element_type in active_anomaly_list or active_anomaly_check == 0:
                # 触发同类异常或新异常 (非紊乱)
                mode_number = 0
                new_anomaly = spawn_output(
                    active_bar, mode_number, skill_node=skill_node, sim_instance=sim_instance
                )
                for _char in char_obj_list:
                    _char.special_resources(new_anomaly)

                # 应用效果 (Buff/Dot)
                anomaly_effect_active(
                    active_bar,
                    time_now,
                    enemy,
                    new_anomaly,
                    element_type,
                    sim_instance=sim_instance,
                )

                if element_type in [2, 5]:  # 冰/烈霜
                    if enemy.dynamic.frozen:
                        event_list.append(new_anomaly)
                    enemy.dynamic.frozen = True
                else:
                    event_list.append(new_anomaly)

                setattr(enemy.dynamic, enemy.trans_anomaly_effect_to_str[element_type], True)
                enemy.dynamic.active_anomaly_bar_dict[element_type] = active_bar

            elif element_type not in active_anomaly_list and len(active_anomaly_list) > 0:
                # 触发紊乱 (Disorder)
                mode_number = 1
                last_anomaly_bar = enemy.dynamic.active_anomaly_bar_dict[last_anomaly_element_type]

                # 更新状态标志
                setattr(
                    enemy.dynamic,
                    enemy.trans_anomaly_effect_to_str[last_anomaly_element_type],
                    False,
                )
                setattr(enemy.dynamic, enemy.trans_anomaly_effect_to_str[element_type], True)

                if element_type in [2, 5]:
                    enemy.dynamic.frozen = True

                # 1. 结算旧异常 (紊乱伤害)
                disorder = spawn_output(
                    last_anomaly_bar,
                    mode_number,
                    skill_node=skill_node,
                    sim_instance=sim_instance,
                )
                enemy.dynamic.active_anomaly_bar_dict[last_anomaly_element_type] = None
                enemy.anomaly_bars_dict[last_anomaly_element_type].active = False

                # 2. 移除旧异常对应的 Dot/Buff
                remove_dots_cause_disorder(disorder, enemy, event_list, time_now)

                # 3. 应用新异常
                new_anomaly = spawn_output(
                    active_bar, 0, skill_node=skill_node, sim_instance=sim_instance
                )
                anomaly_effect_active(
                    active_bar,
                    time_now,
                    enemy,
                    new_anomaly,
                    element_type,
                    sim_instance=sim_instance,
                )
                enemy.dynamic.active_anomaly_bar_dict[element_type] = active_bar

                if element_type not in [2, 5]:
                    event_list.append(new_anomaly)
                for obj in char_obj_list:
                    obj.special_resources(disorder)
                event_list.append(disorder)

                sim_instance.decibel_manager.update(skill_node=skill_node, key="disorder")
                enemy.sim_instance.schedule_data.change_process_state()
                if disorder.activated_by:
                    print(
                        f"由【{disorder.activated_by.char_name}】的【{disorder.activated_by.skill_tag}】技能触发了紊乱！【{ELEMENT_TYPE_MAPPING[last_anomaly_bar.element_type]}】属性的异常状态提前结束！"
                    )
            else:
                raise ValueError("无法解析的异常/紊乱分支")

            bar.reset_current_info_cause_output()


def remove_dots_cause_disorder(disorder, enemy, event_list, time_now):
    """
    因紊乱而移除旧的 Dot (Buff)。
    [Refactor] 适配 BuffManager
    """
    if not hasattr(enemy, "buff_manager"):
        return

    # 需要移除的目标 Buff ID
    # disorder.accompany_dot 存储的是旧异常的 Dot Buff ID
    target_buff_id = disorder.accompany_dot

    # 特殊处理：冻结相关的 Buff ID (假设 ID 为 "Freez" 或 "Freezdot")
    # 这里需要根据实际配置的 Buff ID 来匹配
    freeze_ids = ["Freez", "Freezdot", "Buff_Frozen", "Buff_Frostbite"]  # 示例 ID

    # 遍历当前 Buff，找到需要移除的
    # 注意：不能直接遍历删除，需收集后删除
    buffs_to_remove = []

    # 访问 BuffManager 的内部存储或使用查询接口 (如果存在)
    # 假设可以直接访问 _active_buffs 或通过 keys遍历
    active_ids = list(enemy.buff_manager._active_buffs.keys())

    for buff_id in active_ids:
        # 匹配逻辑：ID 匹配 或 是冻结类
        is_target = (buff_id == target_buff_id) or (buff_id in freeze_ids)

        if is_target:
            buff = enemy.buff_manager.get_buff(buff_id)
            if not buff:
                continue

            # 检查是否应该移除 (例如是否过期，虽然 BuffManager tick 会处理，但紊乱是强制结算)
            # 这里主要是强制结算逻辑

            # 如果是冻结类，可能有特殊结算逻辑 (Event List 追加)
            # 旧逻辑中的特殊处理：
            # if dots.ft.index in ["Freez", "Freezdot"]:
            #     event_list.append(_dot.anomaly_data)

            # 快照结算逻辑
            # 检查是否是冻结类 Buff，并且是否携带了快照数据
            if buff_id in freeze_ids and "anomaly_snapshot" in buff.dy.custom_data:
                # 获取之前注入的异常快照 (AnomalyBar 对象)
                snapshot = buff.dy.custom_data["anomaly_snapshot"]

                # 将快照加入事件列表，系统后续会处理这个事件（通常是结算碎冰伤害）
                event_list.append(snapshot)

                # 更新状态
                enemy.dynamic.frozen = False
                enemy.dynamic.frostbite = False

            buffs_to_remove.append(buff_id)

    # 执行移除
    for buff_id in buffs_to_remove:
        enemy.buff_manager.remove_buff(buff_id, current_tick=time_now)
        print(f"因紊乱而强行移除 Buff {buff_id}")
        enemy.sim_instance.schedule_data.change_process_state()


def check_anomaly_bar(enemy):
    """
    自检函数：检查异常状态数量。
    """
    active_anomaly_check = 0
    active_anomaly_list = []
    anomaly_name_list = []
    for (
        element_number,
        element_anomaly_effect,
    ) in enemy.trans_anomaly_effect_to_str.items():
        if getattr(enemy.dynamic, element_anomaly_effect):
            anomaly_name_list.append(element_anomaly_effect)
            # anomaly_name_list_unique = list(set(anomaly_name_list)) # Logic preserved
            active_anomaly_check = len(set(anomaly_name_list))
            active_anomaly_list.append(element_number)
        if active_anomaly_check >= 2:
            raise ValueError("当前同时存在两种以上的异常状态！！！")

    last_anomaly_element_type: int | None = None
    if len(active_anomaly_list) == 1:
        last_anomaly_element_type = active_anomaly_list[0]
    elif len(active_anomaly_list) == 2:
        if active_anomaly_list == [2, 5]:
            for number in [2, 5]:
                if enemy.anomaly_bars_dict[number].active:
                    last_anomaly_element_type = number
                    break
            else:
                raise TypeError(f"当前激活的异常类型列表为{active_anomaly_list}，是预期之外的值。")
    else:
        last_anomaly_element_type = None
    return active_anomaly_check, active_anomaly_list, last_anomaly_element_type


# [Removed] Delete Legacy Factories
# def spawn_anomaly_dot(...)
# def spawn_normal_dot(...)
# def create_dot_instance(...)
