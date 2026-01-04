import importlib
import os
import pkgutil
from typing import TYPE_CHECKING, Any, Callable, Dict

from zsim.sim_progress.Report import report_to_log

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.zsim_event_system.zsim_events import BaseZSimEventContext, ZSimEventABC

# 定义回调函数签名
BuffCallback = Callable[["Buff", "ZSimEventABC", "BaseZSimEventContext"], Any]


class BuffCallbackRepository:
    _registry: Dict[str, BuffCallback] = {}
    _is_loaded = False

    @classmethod
    def register(cls, logic_id: str):
        """装饰器：注册一个回调函数"""

        def decorator(func: BuffCallback):
            if logic_id in cls._registry:
                report_to_log(
                    f"[BuffSystem] Warning: logic_id '{logic_id}' is being overwritten.", level=3
                )
            cls._registry[logic_id] = func
            return func

        return decorator

    @classmethod
    def get_callback(cls, logic_id: str) -> BuffCallback | None:
        """获取回调函数"""
        # 确保在使用前加载了所有外部逻辑
        if not cls._is_loaded:
            cls.load_external_logics()

        return cls._registry.get(logic_id)

    @classmethod
    def load_external_logics(cls):
        """
        动态加载 zsim/sim_progress/Buff/BuffXLogic 下的所有 Python 模块。
        这样模块内的 @register 装饰器就会执行，将逻辑注册进来。
        """
        if cls._is_loaded:
            return

        # 定位 BuffXLogic 包的路径
        # 假设当前文件在 zsim/sim_progress/Buff/Event/
        # 我们需要指向 zsim/sim_progress/Buff/BuffXLogic/
        base_package = "zsim.sim_progress.Buff.BuffXLogic"

        # 获取相对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logic_dir = os.path.join(os.path.dirname(current_dir), "BuffXLogic")

        if not os.path.exists(logic_dir):
            report_to_log(f"[BuffSystem] Logic directory not found: {logic_dir}", level=3)
            return

        # 遍历目录加载模块
        for _, name, _ in pkgutil.iter_modules([logic_dir]):
            if name.startswith("_") or name == "BasicComplexBuffClass":
                continue  # 跳过私有模块和旧基类
            try:
                importlib.import_module(f"{base_package}.{name}")
                # report_to_log(f"[BuffSystem] Loaded logic module: {name}", level=1)
            except Exception as e:
                report_to_log(f"[BuffSystem] Failed to load logic {name}: {e}", level=4)

        cls._is_loaded = True


# --- 通用基础逻辑 ---


@BuffCallbackRepository.register("stack_add_self")
def cb_stack_add_self(buff: "Buff", event: "ZSimEventABC", context: "BaseZSimEventContext"):
    buff.add_stack(1)
    buff.refresh(event.timestamp if hasattr(event, "timestamp") else 0)
