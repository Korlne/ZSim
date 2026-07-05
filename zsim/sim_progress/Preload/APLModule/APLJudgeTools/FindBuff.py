def find_buff(game_state: dict, char, buff_index):
    """
    根据buff的index来找到buff
    通常用于判断“当前是否有该Buff激活”
    """
    for buffs in game_state["global_stats"].DYNAMIC_BUFF_DICT[char.NAME]:
        if buffs.ft.index == buff_index:
            return buffs
    else:
        return None

    # elif hasattr(data, key):  # 处理类对象
    #     return get_nested_value(getattr(data, key), key_list[1:])
    # else:
    #     raise ValueError(f'无法解析的数据类型！{data, type(data)}')
