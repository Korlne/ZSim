import re


def check_cid(check_target):
    if len(check_target) != 4 or not bool(re.match(r"^-?\d+$", check_target)):
        """检测self.check_target是否是4位int"""
        raise ValueError(f"子条件中的CID格式不对！{check_target}")

    # TODO: 应该在判断通过的同时输出CID！
