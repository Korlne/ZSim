from dataclasses import dataclass, field, replace
from typing import Optional, TYPE_CHECKING
import copy

if TYPE_CHECKING:
    from .effects.base_effect import EffectBase


@dataclass(frozen=True)
class BuffFeature:
    """
    Buff 的静态配置 (Immutable Configuration)
    对应原系统中的 Buff.ft (BuffFeature)
    注意：已设置为 frozen=True，禁止在运行时修改
    """
    buff_id: int                    # Buff 唯一标识符 (原 index/BuffName)
    name: str                       # 显示名称 (原 description)
    max_duration: int               # 最大持续时间
    max_stacks: int                 # 最大层数
    stack_increment: int = 1        # 每次激活增加的层数 (原 step)

    # 核心机制开关
    allows_refresh: bool = True     # 是否允许刷新持续时间 (原 fresh)
    independent_stacks: bool = False  # 层数是否独立结算持续时间 (原 individual_settled)

    # 元数据
    source: str = ""                # 来源 (原 bufffrom)
    is_debuff: bool = False         # 是否为负面效果

    # 标签 (用于 EventProfile 筛选)
    tags: list[str] = field(default_factory=list)


@dataclass
class BuffDynamic:
    """
    Buff 的动态状态 (Mutable State)
    对应原系统中的 Buff.dy (BuffDynamic)
    """
    is_active: bool = False         # 是否激活
    current_stacks: int = 0         # 当前层数
    start_time: int = 0             # 最近一次激活/刷新的开始时间
    end_time: int = 0               # 预计结束时间

    # 独立堆叠计时器 [(start_tick, end_tick), ...]
    stack_timers: list[tuple[int, int]] = field(default_factory=list)


@dataclass
class BuffStatistics:
    """
    Buff 的统计数据 (Statistics)
    """
    activate_count: int = 0         # 激活次数
    expire_count: int = 0           # 结束次数
    last_duration: int = 0          # 上一次持续时长
    total_uptime: int = 0           # 总覆盖时间 (Ticks)


class Buff:
    """
    Buff 实体类
    职责：
    1. 维护 Buff 的生命周期状态
    2. 持有 Buff 的效果对象
    3. 记录统计数据
    """
    def __init__(self, feature: BuffFeature):
        self.ft = feature
        self.dy = BuffDynamic()
        self.stats = BuffStatistics()
        self.effects: list["EffectBase"] = []

    def copy(self) -> "Buff":
        """
        创建当前 Buff 的深拷贝副本
        """
        new_buff = Buff(self.ft)  # ft 是 immutable 的，直接引用
        new_buff.dy = replace(self.dy, stack_timers=list(self.dy.stack_timers))
        new_buff.stats = replace(self.stats)
        # 效果对象如果是无状态的配置容器，浅拷贝列表即可；如果效果有状态，需深拷贝
        # 这里假设 EffectBase 子类是无状态的或实现了 copy
        new_buff.effects = [copy.copy(e) for e in self.effects]
        return new_buff

    def start(self, timestamp: int, duration: Optional[int] = None, stacks: int = 0) -> None:
        """激活 Buff (初始化状态)"""
        effective_duration = duration if duration is not None else self.ft.max_duration
        effective_stacks = stacks if stacks > 0 else self.ft.stack_increment

        self.dy.is_active = True
        self.stats.activate_count += 1
        
        if self.ft.independent_stacks:
            self._add_independent_stack(timestamp, effective_duration, count=effective_stacks)
        else:
            self.dy.start_time = timestamp
            if effective_duration > 0:
                self.dy.end_time = timestamp + effective_duration
            else:
                self.dy.end_time = timestamp

            self.dy.current_stacks = min(effective_stacks, self.ft.max_stacks)

    def refresh(
        self, timestamp: int, duration: Optional[int] = None, stacks_to_add: int = 0
    ) -> None:
        """刷新 Buff 状态 (叠层或续时)"""
        if not self.dy.is_active:
            self.start(timestamp, duration, stacks_to_add)
            return

        effective_duration = duration if duration is not None else self.ft.max_duration
        increment = stacks_to_add if stacks_to_add > 0 else self.ft.stack_increment

        self.stats.activate_count += 1

        if self.ft.independent_stacks:
            self._add_independent_stack(timestamp, effective_duration, count=increment)
            self._update_timers_bounds()
        else:
            if self.ft.allows_refresh:
                self.dy.start_time = timestamp
                if effective_duration > 0:
                    self.dy.end_time = timestamp + effective_duration
            
            new_stack = self.dy.current_stacks + increment
            self.dy.current_stacks = min(new_stack, self.ft.max_stacks)

    def end(self, timestamp: int) -> None:
        """强制结束 Buff"""
        if not self.dy.is_active:
            return

        current_duration = max(0, timestamp - self.dy.start_time)
        self.stats.last_duration = current_duration
        self.stats.total_uptime += current_duration
        self.stats.expire_count += 1

        self.dy.is_active = False
        self.dy.current_stacks = 0
        self.dy.stack_timers.clear()

    def cleanup_expired_stacks(self, current_time: int) -> None:
        """清理过期的独立堆叠层数"""
        if not self.ft.independent_stacks:
            if self.dy.end_time > 0 and current_time >= self.dy.end_time:
                self.end(current_time)
            return

        original_count = len(self.dy.stack_timers)
        self.dy.stack_timers = [t for t in self.dy.stack_timers if t[1] > current_time]
        
        self.dy.current_stacks = len(self.dy.stack_timers)
        
        if self.dy.current_stacks == 0 and original_count > 0:
            self.end(current_time)
        elif self.dy.stack_timers:
            self._update_timers_bounds()

    def _add_independent_stack(self, start: int, duration: int, count: int = 1) -> None:
        """内部方法：处理独立堆叠"""
        end = start + duration
        for _ in range(count):
            self.dy.stack_timers.append((start, end))
        
        while len(self.dy.stack_timers) > self.ft.max_stacks:
            self.dy.stack_timers.pop(0)
        
        self.dy.current_stacks = len(self.dy.stack_timers)
        self._update_timers_bounds()

    def _update_timers_bounds(self) -> None:
        """内部方法：更新起止时间显示"""
        if self.dy.stack_timers:
            self.dy.start_time = self.dy.stack_timers[0][0]
            self.dy.end_time = max(t[1] for t in self.dy.stack_timers)
