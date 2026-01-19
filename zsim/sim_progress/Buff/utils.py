from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zsim.sim_progress.Character.character import Character
    from zsim.simulator.simulator_class import Simulator


def change_name_box(name_box: list[str]) -> dict:
    """
    辅助函数：将 name_box 转换为包含 enemy 的字典或其他结构
    (请根据你原本的逻辑确认，通常是给每个人加个索引，并加上 enemy)
    """
    # 这是一个常见的模拟器实现逻辑，如果你的逻辑不同，请从旧文件复制过来
    new_box = {name: i for i, name in enumerate(name_box)}
    new_box["enemy"] = len(name_box)
    return new_box


def find_char_list(sim_instance: "Simulator") -> list["Character"]:
    """
    辅助函数：从模拟器实例中查找角色列表
    用于 DecibelManager 等需要获取角色对象的场景
    """
    if hasattr(sim_instance, "char_data") and hasattr(sim_instance.char_data, "char_obj_list"):
        return sim_instance.char_data.char_obj_list
    elif hasattr(sim_instance, "schedule_data") and hasattr(
        sim_instance.schedule_data, "char_obj_list"
    ):
        return sim_instance.schedule_data.char_obj_list
    else:
        # 尝试从 game_state 获取
        if (
            hasattr(sim_instance, "game_state")
            and sim_instance.game_state
            and "char_data" in sim_instance.game_state
        ):
            return sim_instance.game_state["char_data"].char_obj_list
    return []
