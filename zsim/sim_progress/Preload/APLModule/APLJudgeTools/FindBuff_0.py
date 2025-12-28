def find_buff_0(game_state: dict, char, buff_index):
    """
    根据buff的index来找到buff
    通常用于判断“当前是否有该Buff激活”
    """
    if hasattr(char, "buff_manager"):
        return char.buff_manager.get_buff(buff_index)
    return None
