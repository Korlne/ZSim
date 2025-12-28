import ast
import json
from typing import TYPE_CHECKING, Any, List, Optional, Tuple

import pandas as pd

from zsim.define import EXIST_FILE_PATH, config_path

# 引入新定义的 Effect 类
from zsim.sim_progress.Buff.Effect.definitions import EffectBase
from zsim.sim_progress.Report import report_to_log

if TYPE_CHECKING:
    from zsim.simulator.simulator_class import Simulator


# 加载全局配置
with open(config_path, "r", encoding="utf-8") as file:
    config = json.load(file)
debug = config.get("debug")


class Buff:
    """
    Buff 实体类 (重构版)

    职责遵循 SRP (单一职责原则)：
    1. 状态容器：维护 Buff 的层数、持续时间、冷却等运行时状态 (BuffDynamic)。
    2. 配置载体：持有 Buff 的静态属性 (BuffFeature)。
    3. 效果持有者：携带 Effect 列表，但不包含 Effect 的具体执行逻辑。

    不再包含：
    - 复杂的触发判定逻辑 (移交 EventRegistry)。
    - 属性修正计算逻辑 (移交 BonusPool)。
    """

    def __init__(self, config: pd.Series, sim_instance: "Simulator", owner: Optional[Any] = None):
        """
        初始化 Buff 实例。

        Args:
            config: 来自 `触发判断.csv` 的单行配置数据。
            sim_instance: 模拟器实例引用。
            owner: Buff 的持有者 (通常是 Character 实例或 Enemy 实例)。
        """
        # 初始化静态特征
        self.ft = self.BuffFeature(config)
        # 初始化动态状态
        self.dy = self.BuffDynamic()
        # 初始化历史记录
        self.history = self.BuffHistory()

        self.sim_instance = sim_instance

        # Buff 持有者
        # 用于在逻辑回调中快速访问属性（如 buff.owner.statement.AM）
        self.owner = owner

        # 效果列表
        # 由 GlobalBuffController 在实例化时通过 `_create_effects_for_buff` 填充
        self.effects: List[EffectBase] = []

    # -------------------------------------------------------------------------
    # 状态管理方法 (State Mutation Methods)
    # 这些方法只负责更新 self.dy 的数据，不进行任何业务逻辑判定或事件分发。
    # -------------------------------------------------------------------------

    def start(self, current_tick: int, duration: int = -1):
        """
        激活 Buff。

        Args:
            current_tick: 当前时间 tick。
            duration: 指定持续时间。如果为 -1，则使用 config 中的默认 maxduration。
        """
        self.dy.active = True
        self.dy.start_tick = current_tick

        # 处理持续时间
        real_duration = duration if duration > 0 else self.ft.maxduration
        if real_duration > 0:
            self.dy.end_tick = current_tick + real_duration
        else:
            # 0 或负数通常代表瞬时或无限，具体语义由上层 Manager 决定，这里暂定为无限(-1)或瞬时(0)
            self.dy.end_tick = current_tick + real_duration if real_duration == 0 else -1

        self.history.active_times += 1
        # 初始层数逻辑由 add_stack 处理，start 默认不给层数，或由调用者显式调用 add_stack

    def end(self, current_tick: int):
        """
        结束 Buff。
        """
        if not self.dy.active:
            return

        self.dy.active = False
        self.dy.count = 0
        self.dy.built_in_buff_box.clear()

        # 注意：通常不在此处自动清除 custom_data，因为某些逻辑可能需要跨激活周期保存状态（如内置CD）
        # 如果需要重置，应显式调用 reset_myself()

        # 更新历史记录
        self.history.last_end_tick = current_tick
        self.history.end_times += 1

        # 计算本次持续时间
        duration = max(0, current_tick - self.dy.start_tick)
        self.history.last_duration = duration

    def refresh(self, current_tick: int):
        """
        刷新 Buff 的持续时间。
        """
        if self.ft.maxduration > 0:
            self.dy.start_tick = current_tick
            self.dy.end_tick = current_tick + self.ft.maxduration

    def add_stack(self, count: int = 1):
        """
        增加层数。
        """
        self.dy.count = min(self.dy.count + count, self.ft.maxcount)

    def remove_stack(self, count: int = 1):
        """
        减少层数。
        """
        self.dy.count = max(0, self.dy.count - count)
        if self.dy.count == 0:
            # 注意：层数归零是否导致 Buff 结束，应由 Manager 层判断并调用 end()，
            # 这里只负责数值变更。
            pass

    def check_expiry(self, current_tick: int) -> bool:
        """
        检查 Buff 是否过期。
        返回 True 表示已过期。
        """
        if not self.dy.active:
            return False
        if self.dy.end_tick == -1:  # 无限持续
            return False
        return current_tick >= self.dy.end_tick

    def reset_myself(self):
        """重置 Buff 所有状态至初始值"""
        self.dy.reset()
        self.history.reset()

    def __str__(self) -> str:
        status = "Active" if self.dy.active else "Inactive"
        return f"Buff<{self.ft.index}> [{status}] Stacks:{self.dy.count}"

    # -------------------------------------------------------------------------
    # 内部类定义 (Inner Classes)
    # -------------------------------------------------------------------------

    class BuffFeature:
        """
        Buff 的静态配置信息 (Read-Only)。
        存储从 CSV 读取的不可变数据。
        """

        # 简单的缓存机制，避免重复解析相同的配置
        bf_instance_cache = {}
        max_cache_size = 256

        def __new__(cls, config):
            # 将 config 转换为可哈希的 tuple 作为 key
            config_items = (
                tuple(sorted(config.items()))
                if isinstance(config, dict)
                else tuple(sorted(config.to_dict().items()))
            )
            cache_key = hash(config_items)

            if cache_key in cls.bf_instance_cache:
                return cls.bf_instance_cache[cache_key]

            instance = super(Buff.BuffFeature, cls).__new__(cls)
            if len(cls.bf_instance_cache) >= cls.max_cache_size:
                cls.bf_instance_cache.popitem()
            cls.bf_instance_cache[cache_key] = instance
            return instance

        def __init__(self, meta_config: pd.Series):
            if hasattr(self, "index"):  # 防止缓存实例重复初始化
                return

            try:
                data: dict = dict(meta_config)
            except TypeError:
                raise TypeError(f"{meta_config} is not a mapping")

            # 基础标识
            self.index = data.get("BuffName", "Unknown")  # Buff 的唯一标识 ID
            self.description = data.get("description", "")

            # 数值属性
            self.maxduration = int(data.get("maxduration", 0))
            self.maxcount = int(data.get("maxcount", 1))
            self.step = int(data.get("incrementalstep", 1))  # 默认叠层步长
            self.cd = int(data.get("increaseCD", 0))  # 内置冷却时间

            # 类型标识
            self.is_debuff = bool(data.get("is_debuff", False))
            self.is_weapon = bool(data.get("is_weapon", False))

            # 机制标识
            self.individual_settled = bool(data.get("individual_settled", False))  # 层数独立结算
            self.hitincrease = bool(data.get("hitincrease", False))  # 是否命中叠层

            # 标签解析
            self.label: Optional[dict] = self.__process_label_str(data)
            self.label_effect_rule: Optional[int] = self.__process_label_rule(data)

        def __process_label_rule(self, config_dict: dict) -> int | None:
            label_rule = config_dict.get("label_effect_rule", 0)
            return (
                int(label_rule)
                if not (pd.isna(label_rule) or label_rule is None)
                else (0 if self.label else None)
            )

        def __process_label_str(self, config_dict: dict):
            label_str = config_dict.get("label", None)
            if label_str is None or pd.isna(label_str) or str(label_str).strip() == "":
                return None
            try:
                return ast.literal_eval(str(label_str).strip())
            except (ValueError, SyntaxError):
                report_to_log(
                    f"[Warning] Buff {config_dict.get('BuffName')} label parse failed: {label_str}",
                    level=4,
                )
                return None

    class BuffDynamic:
        """
        Buff 的运行时动态状态。
        """

        def __init__(self):
            self.active: bool = False  # 当前是否激活
            self.count: int = 0  # 当前层数

            self.start_tick: int = 0  # 开始时间 (tick)
            self.end_tick: int = 0  # 预计结束时间 (tick)，-1 表示无限

            self.last_trigger_tick: int = 0  # 上次触发时间 (用于计算内置 CD)

            # [Added] 通用自定义数据字典
            # 用于存储特定逻辑需要的私有状态，替代旧的 BuffRecord 类
            # 例如: {"last_c6_trigger": 1024, "accumulated_damage": 5000}
            self.custom_data: dict = {}

            # 独立结算层数容器: List[Tuple[start_tick, end_tick]]
            self.built_in_buff_box: List[Tuple[int, int]] = []

        def reset(self):
            """重置为初始状态"""
            self.__init__()

        @property
        def is_ready(self) -> bool:
            """(辅助属性) 检查是否处于 CD 就绪状态"""
            return True

    class BuffHistory:
        """
        Buff 的统计历史记录。
        """

        def __init__(self):
            self.active_times: int = 0  # 激活次数
            self.end_times: int = 0  # 结束次数
            self.last_end_tick: int = 0  # 上次结束时间
            self.last_duration: int = 0  # 上次持续时间

        def reset(self):
            self.__init__()


def spawn_buff_from_index(
    index: str, sim_instance: "Simulator", owner: Optional[Any] = None
) -> Buff:
    """
    [Factory] 根据 Index 创建 Buff 实例。
    主要用于测试环境。
    """
    try:
        df = pd.read_csv(EXIST_FILE_PATH)
        # 查找匹配行
        matched = df[df["BuffName"] == index]
        if matched.empty:
            raise ValueError(f"Buff index '{index}' not found in database.")

        trigger_config = matched.iloc[0].copy()

        # 创建 Buff 实例
        # 传递 owner
        return Buff(trigger_config, sim_instance=sim_instance, owner=owner)

    except FileNotFoundError:
        raise FileNotFoundError(f"CSV Database file not found: {EXIST_FILE_PATH}")
    except Exception as e:
        raise RuntimeError(f"Failed to spawn buff '{index}': {e}")
