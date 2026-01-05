import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np

from zsim.define import ElementType

if TYPE_CHECKING:
    from zsim.sim_progress.Buff import Buff
    from zsim.sim_progress.data_struct.single_hit import SingleHit
    from zsim.sim_progress.Preload import SkillNode
    from zsim.simulator.simulator_class import Simulator


@dataclass
class AnomalyBar:
    """
    这是属性异常类的基类。其中包含了属性异常的基本属性，以及几个基本方法。
    """

    sim_instance: "Simulator"
    element_type: ElementType = 0  # 属性种类编号(1~5)
    is_disorder: bool = False  # 是否是紊乱实例
    current_ndarray: np.ndarray = field(
        default_factory=lambda: np.zeros((1, 1), dtype=np.float64)
    )  # 当前快照总和
    current_anomaly: np.float64 = field(
        default_factory=lambda: np.float64(0)
    )  # 当前已经累计的积蓄值
    current_effective_anomaly: np.float64 = field(
        default_factory=lambda: np.float64(0)
    )  # 有效积蓄值（参与快照的）
    anomaly_times: int = 0  # 迄今为止触发过的异常次数
    cd: int = 180  # 属性异常的内置CD，
    last_active: int = 0  # 上一次属性异常的时间
    max_anomaly: int | None = None  # 最大积蓄值
    ready: bool = True  # 内置CD状态
    accompany_debuff: list | None = None  # 是否在激活时伴生debuff的index
    accompany_dot: str | None = None  # 是否在激活时伴生dot的index
    active: bool | None = None  # 当前异常条是否激活，这一属性和enemy下面的异常开关同步。
    max_duration: int | None = None
    duration_buff_list: list | None = None  # 影响当前异常状态最大时长的buff名
    duration_buff_key_list: list | None = None  # 影响当前异常状态最大时长的buff效果关键字
    basic_max_duration: int = 0  # 基础最大时间
    UUID: uuid.UUID | None = None
    activated_by: "SkillNode | None" = None
    ndarray_box: list[tuple] | None = None
    scaling_factor: float = 1.0  # 缩放比例，在计算伤害时会乘以该比例
    settled: bool = False  # 快照是否被结算过
    rename_tag: str | None = None  # 重命名标签
    schedule_priority: int = 999  # 默认情况下，异常条的处理优先级为999，位于当前tick的最后。

    @property
    def rename(self) -> bool:
        return self.rename_tag is not None

    def __post_init__(self):
        self.UUID = uuid.uuid4()

    def __hash__(self):
        return hash(self.UUID)

    @property
    def is_full(self):
        assert self.max_anomaly is not None
        return self.current_anomaly >= self.max_anomaly

    def remaining_tick(self):
        timetick = self.sim_instance.tick
        assert self.max_duration is not None
        remaining_tick = max(self.max_duration - self.duration(timetick), 0)
        return remaining_tick

    def duration(self, timetick: int):
        duration = timetick - self.last_active
        if self.max_duration is None:
            raise AssertionError("该异常的max_duration为None，无法判断是否过期！")

        # [Refractor] 移除异常判定断言。
        # 即使 duration > max_duration（即异常已结束），remaining_tick() 中的 max(..., 0) 也会正确处理。
        # 这里强制报错会导致紊乱计算时，对于刚结束的异常处理失败。
        # if self.max_duration is not None:
        #     assert duration <= self.max_duration, "该异常早就结束了！不应该触发紊乱！"
        return duration

    def update_snap_shot(self, new_snap_shot: tuple, single_hit: "SingleHit"):
        """
        该函数是更新快照的核心函数。
        """
        if not isinstance(new_snap_shot[2], np.ndarray):
            raise TypeError("所传入的快照元组的第3个元素应该是np.ndarray！")

        build_up_value = new_snap_shot[1]  # 获取积蓄值
        self.current_anomaly += build_up_value

        if single_hit.effective_anomlay_buildup():
            # 只有有效积蓄才会累计快照
            if self.ndarray_box is None:
                self.ndarray_box = []
            self.ndarray_box.append(new_snap_shot)

    def ready_judge(self, timenow):
        if timenow - self.last_active >= self.cd:
            self.ready = True

    def check_myself(self, timenow: int):
        assert self.max_duration is not None, "该异常的max_duration为None，无法判断是否过期！"
        if self.active and (self.last_active + self.max_duration < timenow):
            self.active = False
            return True
        return False

    def change_info_cause_active(
        self,
        timenow: int,
        skill_node: "SkillNode",
    ):
        """
        属性异常激活时，必要的信息更新
        """
        char_cid = int(skill_node.skill_tag.strip().split("_")[0])
        self.ready = False
        self.anomaly_times += 1
        self.last_active = timenow
        self.active = True
        self.activated_by = skill_node
        # [新架构] 直接从 BuffManager 获取影响持续时间的 Buff
        self.__get_max_duration(char_cid)

    def reset_current_info_cause_output(self):
        """
        重置和属性积蓄条以及快照相关的信息。
        """
        self.current_effective_anomaly = np.float64(0)
        self.current_anomaly = np.float64(0)
        self.current_ndarray = np.zeros((1, self.current_ndarray.shape[0]), dtype=np.float64)
        self.ndarray_box = []
        self.settled = False

    def get_buildup_pct(self):
        if self.max_anomaly is None:
            return 0
        if self.is_full:
            return 1
        pct = self.current_anomaly / self.max_anomaly
        return pct

    def reset_myself(self):
        self.current_ndarray = np.zeros((1, 1), dtype=np.float64)
        self.current_anomaly = np.float64(0)
        self.anomaly_times = 0
        self.last_active = 0
        self.ready = True
        self.active = False
        self.max_anomaly = None
        self.ndarray_box = []

    def __get_max_duration(self, anomaly_from: int | str) -> None:
        """通过 BuffManager 计算当前异常的最大持续时间"""
        if self.duration_buff_list is None:
            self.max_duration = self.basic_max_duration
            return

        # [Refactor] 引入 BonusEffect
        from zsim.sim_progress.Buff.Effect.definitions import BonusEffect

        max_duration_delta_fix = 0
        max_duration_delta_pct = 0
        enemy = getattr(self.sim_instance, "enemy", None)
        if enemy is None or not hasattr(enemy, "buff_manager"):
            self.max_duration = self.basic_max_duration
            return

        enemy_buff_list = [
            buff for buff in enemy.buff_manager._active_buffs.values() if buff.dy.active
        ]
        for _buff_index in self.duration_buff_list:
            for buffs in enemy_buff_list:
                if _buff_index == buffs.ft.index:
                    # [Refactor] 直接使用 effects 列表
                    for effect in buffs.effects:
                        if isinstance(effect, BonusEffect) and effect.enable:
                            if effect.target_attribute in self.duration_buff_key_list:
                                keys = effect.target_attribute
                                if "百分比" in keys:
                                    max_duration_delta_pct += buffs.dy.count * effect.value
                                else:
                                    max_duration_delta_fix += buffs.dy.count * effect.value

        self.max_duration = max(
            self.basic_max_duration * (1 + max_duration_delta_pct) + max_duration_delta_fix,
            0,
        )

    @staticmethod
    def create_new_from_existing(existing_instance):
        new_instance = AnomalyBar.__new__(AnomalyBar)
        new_instance.__dict__ = existing_instance.__dict__.copy()
        return new_instance

    def __deepcopy__(self, memo):
        import copy

        cls = self.__class__
        new_anomaly_bar = cls.__new__(cls)
        memo[id(self)] = new_anomaly_bar
        for key, value in self.__dict__.items():
            if key == "sim_instance":
                setattr(new_anomaly_bar, key, value)
            elif key == "activated_by" and hasattr(value, "skill"):
                new_skill_node = copy.copy(value)
                setattr(new_anomaly_bar, key, new_skill_node)
            elif key == "current_ndarray" and value is not None:
                setattr(new_anomaly_bar, key, value.copy())
            elif key == "current_anomaly" and value is not None:
                setattr(new_anomaly_bar, key, copy.copy(value))
            elif key == "UUID":
                setattr(new_anomaly_bar, key, uuid.uuid4())
            else:
                try:
                    setattr(new_anomaly_bar, key, copy.deepcopy(value, memo))
                except TypeError:
                    setattr(new_anomaly_bar, key, value)

        return new_anomaly_bar

    def anomaly_settled(self):
        """结算快照！"""
        if self.settled:
            raise RuntimeError(
                "【异常条结算警告】当前异常条快照已经被结算过一次了，请检查业务逻辑，找出重复结算的时间点！"
            )
        total_array = np.zeros((1, 1), dtype=np.float64)
        effective_buildup: np.float64 = np.float64(0)
        while self.ndarray_box:
            _tuples = self.ndarray_box.pop()
            _array = _tuples[2].reshape(1, -1)
            _build_up = _tuples[1]
            if total_array.shape[1] != _array.shape[1]:
                if total_array.shape[1] < _array.shape[1]:
                    new_shape = (1, _array.shape[1])
                    extended_ndarray = np.zeros(new_shape, dtype=np.float64)
                    extended_ndarray[:, : total_array.shape[1]] = total_array
                    total_array = extended_ndarray
                else:
                    raise ValueError(f"传入的快照数组列数为{_array.shape[1]}，小于快照缓存的列数！")
            total_array += _array * _build_up
            effective_buildup += _build_up
        self.current_effective_anomaly = effective_buildup
        self.current_ndarray = total_array / self.current_effective_anomaly
        self.settled = True
