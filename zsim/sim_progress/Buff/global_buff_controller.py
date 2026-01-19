from typing import Dict, Optional, TYPE_CHECKING
from .buff_model import Buff

if TYPE_CHECKING:
    from zsim.simulator.config_classes import SimulationConfig

class GlobalBuffController:
    """
    全局 Buff 控制器 (Singleton-like Repository)
    职责：
    1. 集中存储本次模拟中涉及的所有 Buff 实例 (_buff_box)。
    2. 提供 Buff 的注册与查询接口。
    3. (工厂职责) 根据 SimConfig 初始化 Buff 对象 (buff_initiate_factory)。
    """
    def __init__(self):
        # 核心仓库：BuffID -> Buff Instance
        self._buff_box: Dict[str, Buff] = {}

    def buff_register(self, buff: Buff) -> None:
        """
        注册一个 Buff 实例到全局仓库。
        :param buff: Buff 对象
        :raises ValueError: 如果 Buff ID 已存在
        """
        if buff.ft.buff_id in self._buff_box:
            raise ValueError(f"Duplicate Buff ID registration attempted: {buff.ft.buff_id}")
        
        self._buff_box[buff.ft.buff_id] = buff

    def get_buff(self, buff_id: str) -> Optional[Buff]:
        """
        根据 ID 获取 Buff 实例。
        """
        return self._buff_box.get(buff_id)

    def buff_initiate_factory(self, sim_config: "SimulationConfig") -> None:
        """
        [工厂方法] 读取配置，初始化并注册所有涉及的 Buff。
        注意：此处为框架代码，具体的数据读取逻辑(select_buff)将在后续数据迁移阶段实现。
        """
        # TODO: 接入新的数据加载模块 (Phase 2 Migration)
        # 1. buff_candidate_list = self.select_buff(sim_config)
        # 2. for config in buff_candidate_list:
        # 3.     feature = BuffFeature(...)
        # 4.     new_buff = Buff(feature)
        # 5.     self.buff_register(new_buff)
        pass

    def reset(self):
        """重置控制器状态 (用于多次模拟之间)"""
        self._buff_box.clear()