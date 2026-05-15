def check_number_type(text):
    """
    将文本的整型、浮点数、布尔值、元组转化为正常格式，纯文本不变、若是类型不是文本则直接输出。
    :param text: 输入的参数，可能是文本或已经正确的类型
    :return: 转换后的值
    """
    if isinstance(text, str):
        # 尝试转换为整型
        try:
            return int(text)
        except ValueError:
            pass
        # 尝试转换为浮点数
        try:
            return float(text)
        except ValueError:
            pass
        # 尝试转化None
        if text.lower() == "none":
            return None
        # 尝试转换为布尔值
        if text.lower() in ["true", "false"]:
            return text.lower() == "true"
        # 尝试转换为元组
        if text.startswith("(") and text.endswith(")"):
            try:
                # 去除括号并分割元素
                elements = text[1:-1].split(",")
                # 递归处理每个元素
                return tuple(check_number_type(elem.strip()) for elem in elements)[1]
            except ValueError:
                pass
        # 如果以上转换都失败，返回原文本
        return text
    elif isinstance(text, tuple):
        # 如果是元组，递归处理每个元素
        return tuple(check_number_type(elem) for elem in text)[1]
    else:
        # 如果不是文本类型，直接返回
        return text
