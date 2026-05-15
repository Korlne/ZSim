def find_char(found_char_dict: dict, game_state: dict, CID: int):
    """
    根据提供的CID，找到对应的char，并且返回、保存在self.found_char_dict中。
    每次调用时，会先检查是否在self.found_char_dict中。如果找不到，再扔出去。
    """
    if CID in found_char_dict.keys():
        return found_char_dict[CID]
    for char in game_state["char_data"].char_obj_list:
        if char.CID == int(CID):
            found_char_dict[char.CID] = char
            return char
    else:
        raise ValueError(f"未找到CID为{CID}的角色！")
