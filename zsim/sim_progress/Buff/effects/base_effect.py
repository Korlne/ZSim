from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class EffectBase(ABC):
    """
    Buff 效果基类 (Abstract Base Class)
    对应设计文档中的 effect_base_class
    """
    def __init__(self, source_buff_id: str, effect_config: Optional[Dict[str, Any]] = None):
        """
        :param source_buff_id: 来源 Buff 的 ID
        :param effect_config: 效果的原始配置数据 (来自 JSON/CSV)
        """
        self.source_buff_id = source_buff_id
        self.config = effect_config if effect_config else {}

    @abstractmethod
    def apply(self, target: Any) -> None:
        """
        应用效果的接口
        :param target: 效果作用的目标 (通常是 Character 或 Modifier 上下文)
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} from {self.source_buff_id}>"