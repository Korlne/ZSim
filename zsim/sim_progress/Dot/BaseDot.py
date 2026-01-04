from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, List

from zsim.sim_progress.anomaly_bar import AnomalyBar

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.Effect.definitions import EffectBase
    from zsim.sim_progress.Preload import SkillNode
    from zsim.simulator.simulator_class import Simulator


class Dot:
    def __init__(
        self,
        bar: "AnomalyBar | None",
        skill_tag: str | None = None,
        sim_instance: "Simulator | None" = None,
    ):
        self.sim_instance = sim_instance
        self.ft = self.DotFeature(sim_instance=self.sim_instance)
        self.dy = self.DotDynamic()
        self.history = self.DotHistory()

        # [Refactor] 新架构适配：初始化 effects 列表和 owner
        self.effects: List["EffectBase"] = []
        self.owner: Any = None

        # 默认情况下不创建anomlay_data。
        self.anomaly_data = None
        self.skill_node_data: "SkillNode | None" = None
        if bar is not None and skill_tag is not None:
            raise ValueError("Dot的构造函数不可以同时传入bar和skill_tag")
        if bar:
            self.anomaly_data = bar
        if skill_tag:
            from zsim.sim_progress.Buff import JudgeTools
            from zsim.sim_progress.Preload.SkillsQueue import spawn_node

            if self.sim_instance is None:
                raise ValueError("sim_instance is None, but it should not be.")

            preload_data = JudgeTools.find_preload_data(sim_instance=self.sim_instance)
            tick = JudgeTools.find_tick(sim_instance=self.sim_instance)
            self.skill_node_data = spawn_node(skill_tag, tick, preload_data.skills)

    @dataclass
    class DotFeature:
        """
        这里记录了Dot的固定属性。
        """

        sim_instance: "Simulator | None"
        update_cd: int | float = 0
        index: str | None = None
        name: str | None = None
        dot_from: str | None = None
        effect_rules: int | None = None
        max_count: int | None = None
        max_duration: int | None = None
        incremental_step: int | None = None
        max_effect_times: int = 30
        count_as_skill_hit: bool = False  # dot生效时的伤害能否视作技能的一次命中
        complex_exit_logic = False  # 复杂的结束判定

        # [Refactor] 新架构适配：Buff系统必需字段
        label: dict | None = None
        beneficiary: str | None = None

        def __str__(self):
            return str(self.__dict__)

        # [Refactor] 新架构适配：接口属性别名
        @property
        def maxcount(self) -> int:
            return self.max_count if self.max_count is not None else 1

        @property
        def maxduration(self) -> int:
            return self.max_duration if self.max_duration is not None else 0

    @dataclass
    class DotDynamic:
        start_ticks: int = 0
        end_ticks: int = 0
        last_effect_ticks: int = 0
        active: bool | None = None
        count: int = 0
        ready: bool | None = None
        effect_times: int = 0

        # [Refactor] 新架构适配：通用数据存储
        custom_data: dict = field(default_factory=dict)

        @property
        def start_tick(self) -> int:
            return self.start_ticks

        @start_tick.setter
        def start_tick(self, value: int):
            self.start_ticks = value

    @dataclass
    class DotHistory:
        start_times: int = 0
        end_times: int = 0
        last_start_ticks: int = 0
        last_end_ticks: int = 0
        last_duration: int = 0

    def ready_judge(self, timenow: int):
        if not self.dy.ready:
            if timenow - self.dy.last_effect_ticks >= self.ft.update_cd:
                self.dy.ready = True

    def end(self, timenow: int):
        self.dy.active = False
        self.dy.count = 0
        self.history.last_end_ticks = timenow
        self.history.last_duration = timenow - self.dy.start_ticks
        self.history.end_times += 1

    def start(self, timenow: int):
        self.dy.active = True
        self.dy.start_ticks = timenow
        self.dy.last_effect_ticks = timenow
        if self.ft.max_duration is None:
            raise ValueError(f"{self.ft.index}的最大持续时间为None，请检查初始化！")
        self.dy.end_ticks = self.dy.start_ticks + self.ft.max_duration
        self.history.start_times += 1
        self.history.last_start_ticks = timenow
        self.dy.count = 1
        self.dy.effect_times = 1
        self.dy.ready = False

    def exit_judge(self, **kwargs) -> bool:
        pass

    # [Refactor] 新架构适配：过期检查接口
    def check_expiry(self, current_tick: int) -> bool:
        if not self.dy.active:
            return False
        return current_tick >= self.dy.end_ticks
