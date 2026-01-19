from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Protocol

from .base_effect import EffectBase


class BonusEffectTarget(Protocol):
    """BonusEffect 作用目标协议"""

    def apply_bonus_effect(self, effect: "BonusEffect") -> None:
        """将数值加成效果应用到目标对象"""
        ...


@dataclass
class BonusEffect(EffectBase):
    """
    数值型增益/减益效果
    仅负责描述加成数据与基础应用行为，不承担触发判定逻辑。
    """

    target_attribute: str
    value: float
    correction_type: str
    conditions: list[Callable[[Any], bool]] = field(default_factory=list)
    source_buff_id: int = 0
    effect_config: Optional[dict[str, Any]] = None

    def __post_init__(self) -> None:
        super().__init__(source_buff_id=self.source_buff_id, effect_config=self.effect_config)

    def apply(self, target: BonusEffectTarget) -> None:
        """将数值效果应用到目标对象"""
        if self.conditions and not all(condition(target) for condition in self.conditions):
            return
        target.apply_bonus_effect(self)
