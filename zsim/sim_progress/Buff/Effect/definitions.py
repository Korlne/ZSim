from abc import ABC
from dataclasses import dataclass, field
from typing import List, Literal


@dataclass(kw_only=True)
class EffectBase(ABC):
    """
    Buff 效果的抽象基类。
    所有具体的 Buff 效果（如数值加成、触发器）都应继承此类。
    """

    source_buff_id: str
    """来源 Buff 的 ID（通常是 BuffName 或唯一标识符）"""

    enable: bool = True
    """效果是否处于激活状态"""

    skill_tags: List[str] = field(default_factory=list)
    """
    该效果生效的技能标签限制。
    例如：['1301_SNA_1'] 表示仅在特定招式下生效。为空则无限制。
    """


@dataclass(kw_only=True)
class BonusEffect(EffectBase):
    """
    数值增益类效果。
    负责定义属性数值的修改，不包含计算逻辑，仅承载数据。
    """

    target_attribute: str
    """目标属性名称，例如 '攻击力', '暴击率', '火属性伤害提升'"""

    value: float
    """增益数值"""

    calc_mode: Literal["add", "mul", "final_mul"] = "add"
    """
    计算模式：
    - add: 加算
    - mul: 乘算
    - final_mul: 最终乘算
    """


@dataclass
class TriggerEffect(EffectBase):
    """
    触发器类效果。
    不直接修改数值，而是定义“当发生某事时，执行某逻辑”。
    """

    trigger_event_type: str
    """
    触发该效果的事件类型。
    对应 EventRouter 中的事件名，如 'skill_hit', 'enemy_attack', 'interval_tick'
    """

    callback_logic_id: str
    """
    回调逻辑的 ID。
    EventRouter 触发时，会根据此 ID 查找对应的 Handler 执行具体业务。
    """

    cooldown: float = 0.0
    """触发冷却时间（秒）"""

    trigger_count_limit: int = -1
    """触发次数限制，-1 表示无限制"""
