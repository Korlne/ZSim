# [DEPRECATED]
# 此文件属于旧版 Buff 系统 (Class-based Logic)。
# 新版 Buff 系统已迁移至基于回调的架构 (Function-based Callbacks)。
# 请勿在新代码中继承 BasicComplexBuffClass。
#
# 新逻辑编写指南：
# 1. 在 zsim/sim_progress/Buff/BuffXLogic/ 下创建新文件。
# 2. 使用 @BuffCallbackRepository.register("Logic_ID") 装饰函数。
# 3. 函数签名：def logic_func(buff: Buff, event: ZSimEventABC, context: BaseZSimEventContext):
# 4. 直接在函数内操作 buff.dy.count 或调用 buff.start()/buff.end()。


class BasicComplexBuffClass:
    def __init__(self, *args, **kwargs):
        raise DeprecationWarning(
            "BasicComplexBuffClass is deprecated. Please refactor logic using BuffCallbackRepository."
        )
