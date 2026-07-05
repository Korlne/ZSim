from .BreakingLegManager import BreakingLegManager

UNIQUE_MECHANIC_MAP = {
    11411: BreakingLegManager,
    # 11412: BreakingLegManager,
    11413: BreakingLegManager,
    # 11414: BreakingLegManager,
}


def unique_mechanic_factory(enemy_instance):
    """构造特殊敌人事件的工厂函数"""
    mechanic_class = UNIQUE_MECHANIC_MAP.get(enemy_instance.index_ID, None)
    if mechanic_class:
        return mechanic_class(enemy_instance)
    else:
        return None
