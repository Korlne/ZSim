from typing import TYPE_CHECKING, Any, Callable, Dict

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_events import BaseZSimEventContext, ZSimEventABC

# 定义回调函数签名: (Buff实例, 事件对象, 上下文) -> 产生的新事件或None
BuffCallback = Callable[["Buff", "ZSimEventABC", "BaseZSimEventContext"], Any]


class BuffCallbackRepository:
    """
    Buff 回调逻辑仓库。
    存储所有 TriggerEffect 中 callback_logic_id 对应的具体函数。
    """

    _registry: Dict[str, BuffCallback] = {}

    @classmethod
    def register(cls, logic_id: str):
        """装饰器：注册一个回调函数"""

        def decorator(func: BuffCallback):
            cls._registry[logic_id] = func
            return func

        return decorator

    @classmethod
    def get_callback(cls, logic_id: str) -> BuffCallback:
        """获取回调函数"""
        return cls._registry.get(logic_id)

    @classmethod
    def execute(
        cls, logic_id: str, buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"
    ):
        """执行回调"""
        func = cls.get_callback(logic_id)
        if func:
            # 可以在这里加通用的错误处理或日志
            return func(buff, event, context)
        # else:
        #     print(f"[Warning] Unknown callback logic_id: {logic_id}")


# --- 下面定义具体的通用逻辑 (Standard Callbacks) ---


@BuffCallbackRepository.register("stack_add_self")
def cb_stack_add_self(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """通用逻辑：给自己叠层"""
    buff.add_stack(1)
    buff.refresh(event.timestamp if hasattr(event, "timestamp") else 0)


@BuffCallbackRepository.register("refresh_duration")
def cb_refresh_duration(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """通用逻辑：仅刷新持续时间"""
    buff.refresh(event.timestamp if hasattr(event, "timestamp") else 0)


# 示例：针对特定角色的特殊逻辑 (迁移旧代码时会大量增加此类)
@BuffCallbackRepository.register("trigger_counter_attack")
def cb_trigger_counter_attack(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    """示例：触发反击 (Placeholder)"""
    pass
