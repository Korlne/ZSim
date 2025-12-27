# [Refactor] Phase 2: Exposed New Classes
# 新系统入口
from .buff_class import Buff
from .BuffManager.BuffManagerClass import BuffManager
from .GlobalBuffControllerClass.global_buff_controller import GlobalBuffController

# [Legacy] 标记为废弃 (Deprecated)
# 下面的模块在重构完成前保留引用，但 Buff0Manager 已经因接口变更而不可用。
# from .Buff0Manager import Buff0Manager
# from .BuffAdd import buff_add
# from .BuffLoad import BuffInitialize, BuffLoadLoop
# from .ScheduleBuffSettle import ScheduleBuffSettle
