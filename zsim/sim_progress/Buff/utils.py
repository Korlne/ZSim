def change_name_box(name_box: list[str]) -> dict:
    """
    辅助函数：将 name_box 转换为包含 enemy 的字典或其他结构
    (请根据你原本的逻辑确认，通常是给每个人加个索引，并加上 enemy)
    """
    # 这是一个常见的模拟器实现逻辑，如果你的逻辑不同，请从旧文件复制过来
    new_box = {name: i for i, name in enumerate(name_box)}
    new_box["enemy"] = len(name_box)
    return new_box
