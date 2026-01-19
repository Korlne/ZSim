from typing import Optional, TYPE_CHECKING
from .buff_model import Buff, BuffFeature

if TYPE_CHECKING:
    from zsim.simulator.config_classes import SimConfig



class GlobalBuffController:
    """
    全局 Buff 控制器 (Factory & Registry)
    职责：
    1. 存储 Buff 的静态配置配方 (BuffFeature)。
    2. 提供工厂方法 create_buff_instance，生产全新的 Buff 实例。
    3. 管理数据初始化加载。
    """
    def __init__(self):
        # 核心仓库：BuffID -> BuffFeature (Recipe)
        self._feature_registry: dict[str, BuffFeature] = {}

    def register_buff_feature(self, feature: BuffFeature) -> None:
        """
        注册一个 Buff 配方。
        :param feature: Buff 静态配置对象
        """
        if feature.buff_id in self._feature_registry:
            raise ValueError(f"Duplicate Buff ID registration attempted: {feature.buff_id}")
        
        self._feature_registry[feature.buff_id] = feature

    def create_buff_instance(self, buff_id: str) -> Optional[Buff]:
        """
        [工厂方法] 根据 ID 创建一个新的 Buff 实例。
        如果 ID 不存在，返回 None。
        """
        feature = self._feature_registry.get(buff_id)
        if not feature:
            return None
        
        # 创建全新实例，状态互不干扰
        new_buff = Buff(feature)
        
        # TODO: 在此处装载 Buff 的 Effect 对象 (Phase 2)
        # new_buff.effects = self._load_effects_for_buff(buff_id)
        
        return new_buff

    def buff_initiate_factory(self, sim_config: "SimConfig") -> None:
        """
        [初始化阶段] 读取配置，注册所有涉及的 BuffFeature。
        """
        # TODO: 接入新的数据加载模块
        # 1. features = load_buff_features(sim_config)
        # 2. for ft in features:
        # 3.     self.register_buff_feature(ft)
        pass

    def reset(self) -> None:
        """重置控制器状态"""
        self._feature_registry.clear()
