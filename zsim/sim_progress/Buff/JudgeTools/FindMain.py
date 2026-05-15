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
    dynamic_buff_list = sim_instance.global_stats.DYNAMIC_BUFF_DICT
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
