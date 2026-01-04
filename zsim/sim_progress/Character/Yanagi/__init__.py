from typing import TYPE_CHECKING

from zsim.sim_progress.anomaly_bar.CopyAnomalyForOutput import NewAnomaly
from zsim.sim_progress.Preload import SkillNode

from ..character import Character
from ..utils.filters import (
    _anomaly_filter,
    _skill_node_filter,
)
from .StanceManager import StanceManager

if TYPE_CHECKING:
    pass


class Yanagi(Character):
    """柳的特殊资源系统"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stance_manager = StanceManager(self)
        self.cinme_1_buff_index = "Buff-角色-柳-1画-洞悉"
        self.cinema_4_buff_index = "Buff-角色-柳-4画-识破"

        # 定义架势 Buff 的 ID
        self._stance_buffs_initialized = False
        self.stance_buff_jougen = "Buff-角色-柳-架势-上弦"
        self.stance_buff_kagen = "Buff-角色-柳-架势-下弦"

    def special_resources(self, *args, **kwargs) -> None:
        # 在第一帧或初始化时，将架势 Buff 注册到 BuffManager
        # 这些 Buff 用于 APL 检测当前架势，必须长期存在
        if not self._stance_buffs_initialized and self.sim_instance is not None:
            tick = self.sim_instance.tick

            # 1. 添加“上弦” Buff
            # StanceManager 默认初始状态为上弦 (stance_jougen=True)
            buff_j = self.buff_manager.add_buff(self.stance_buff_jougen, tick)
            if buff_j:
                buff_j.dy.end_tick = -1  # 设置为无限时长
                buff_j.dy.active = self.stance_manager.stance_jougen  # 同步初始状态

            # 2. 添加“下弦” Buff
            # 默认初始状态下弦为 False
            buff_k = self.buff_manager.add_buff(self.stance_buff_kagen, tick)
            if buff_k:
                buff_k.dy.end_tick = -1  # 设置为无限时长
                buff_k.dy.active = self.stance_manager.stance_kagen  # 同步初始状态

            self._stance_buffs_initialized = True

        skill_nodes: list["SkillNode"] = _skill_node_filter(*args, **kwargs)
        anomalies: list[NewAnomaly] = _anomaly_filter(*args, **kwargs)
        # tick = kwargs.get('tick', 0)
        for nodes in skill_nodes:
            self.stance_manager.update_myself(nodes)

        if self.cinema >= 1 and anomalies:
            if self.sim_instance is not None:
                # 使用 self.buff_manager.add_buff 替代 buff_add_strategy
                self.buff_manager.add_buff(self.cinme_1_buff_index, self.sim_instance.tick)

            if self.cinema >= 4:
                for _anomaly in anomalies:
                    if isinstance(_anomaly.activate_by, SkillNode):
                        if str(self.CID) in _anomaly.activate_by.skill_tag:
                            if self.sim_instance is not None:
                                # 使用 self.buff_manager.add_buff 替代 buff_add_strategy
                                self.buff_manager.add_buff(
                                    self.cinema_4_buff_index, self.sim_instance.tick
                                )
                            break

    def update_sp_and_decibel(self, *args, **kwargs):
        """自然更新能量和喧响的方法"""
        # Preload Skill
        skill_nodes = _skill_node_filter(*args, **kwargs)
        for node in skill_nodes:
            # SP
            if node.char_name == self.NAME:
                if node.skill_tag == "1221_E_EX_1" and self.cinema == 6:
                    sp_consume = node.skill.sp_consume / 2
                else:
                    sp_consume = node.skill.sp_consume
                sp_threshold = node.skill.sp_threshold
                sp_recovery = node.skill.sp_recovery
                if self.sp < sp_threshold:
                    print(
                        f"{node.skill_tag}需要{sp_threshold:.2f}点能量，目前{self.NAME}仅有{self.sp:.2f}点，需求无法满足，请检查技能树"
                    )
                sp_change = sp_recovery - sp_consume
                self.update_sp(sp_change)
            # Decibel
            self.process_single_node_decibel(node)
        # SP recovery over time
        self.update_sp_overtime(args, kwargs)

    def get_resources(self) -> tuple[str | None, int | float | bool | None]:
        """柳的get_resource不返回内容！因为柳没有特殊资源，只有特殊状态"""
        return None, None

    def get_special_stats(self, *args, **kwargs) -> dict[str | None, object | None]:
        return {
            "当前架势": self.stance_manager.stance_now,
            "森罗万象状态": self.stance_manager.shinrabanshou.active,
        }
