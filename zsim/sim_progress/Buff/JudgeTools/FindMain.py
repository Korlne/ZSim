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

    [兼容修复] 新 Buff 系统以 BuffManager 为准，且需过滤 active=False 的 Buff，
    避免旧接口获取到休眠状态的 Buff 导致计算或显示错误。
    """
    # 动态 Buff 字典，直接新建返回即可，不再依赖 GlobalStats
    dynamic_buff_list: dict[str, list] = {}

    if sim_instance.char_data:
        for char in sim_instance.char_data.char_obj_list:
            if hasattr(char, "buff_manager"):
                # 仅返回 active=True 的 Buff
                dynamic_buff_list[char.NAME] = [
                    b for b in char.buff_manager._active_buffs.values() if b.dy.active
                ]

    if sim_instance.enemy and hasattr(sim_instance.enemy, "buff_manager"):
        dynamic_buff_list["enemy"] = [
            b for b in sim_instance.enemy.buff_manager._active_buffs.values() if b.dy.active
        ]

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