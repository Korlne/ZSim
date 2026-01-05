from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zsim.simulator.simulator_class import Simulator


def find_enemy(sim_instance: "Simulator" = None):
    enemy = sim_instance.schedule_data.enemy
    return enemy


def find_init_data(sim_instance: "Simulator" = None):
    init_data = sim_instance.init_data
    return init_data


def find_char_list(sim_instance: "Simulator" = None):
    char_list = sim_instance.char_data.char_obj_list
    return char_list


def find_dynamic_buff_list(sim_instance: "Simulator" = None):
    """
    获取当前激活的动态 Buff 列表。

    [兼容修复] 新 Buff 系统以 BuffManager 为准，这里需要把活跃 Buff 写回旧接口，
    避免旧 dynamic_buff_list 混入未激活 Buff，导致模拟结果不一致。
    """
    dynamic_buff_list = sim_instance.global_stats.DYNAMIC_BUFF_DICT
    active_buff_map: dict[str, list] = {}

    if sim_instance.char_data:
        for char in sim_instance.char_data.char_obj_list:
            if hasattr(char, "buff_manager"):
                active_buff_map[char.NAME] = [
                    buff
                    for buff in char.buff_manager._active_buffs.values()
                    if buff.dy.active
                ]

    if sim_instance.enemy and hasattr(sim_instance.enemy, "buff_manager"):
        active_buff_map["enemy"] = [
            buff for buff in sim_instance.enemy.buff_manager._active_buffs.values() if buff.dy.active
        ]

    if active_buff_map:
        # 同步写回旧的全局字典，保证旧接口获取到的是新系统激活状态
        for name, buffs in active_buff_map.items():
            dynamic_buff_list[name] = buffs
        return dynamic_buff_list

    return dynamic_buff_list


def find_tick(sim_instance: "Simulator" = None):
    tick = sim_instance.tick
    return tick


def find_exist_buff_dict(sim_instance: "Simulator" = None):
    exist_buff_dict = sim_instance.load_data.exist_buff_dict
    return exist_buff_dict


def find_event_list(sim_instance: "Simulator" = None):
    event_list = sim_instance.schedule_data.event_list
    return event_list


def find_stack(sim_instance: "Simulator" = None):
    stack = sim_instance.load_data.action_stack
    return stack


def find_load_data(sim_instance: "Simulator" = None):
    load_data = sim_instance.load_data
    return load_data


def find_schedule_data(sim_instance: "Simulator" = None):
    schedule_data = sim_instance.schedule_data
    return schedule_data


def find_preload_data(sim_instance: "Simulator" = None):
    preload_data = sim_instance.preload.preload_data
    return preload_data


def find_name_box(sim_instance: "Simulator" = None):
    name_box = sim_instance.load_data.name_box
    return name_box


def find_all_name_order_box(sim_instance: "Simulator" = None):
    all_name_order_box = sim_instance.load_data.all_name_order_box
    return all_name_order_box
