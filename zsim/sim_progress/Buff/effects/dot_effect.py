"""
Dot Effect Implementation
负责处理异常状态的持续伤害逻辑
"""
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING, Dict, Any

from zsim.sim_progress.Buff.effects.base_effect import EffectBase
from zsim.sim_progress.Report import report_to_log

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_model import Buff
    from zsim.sim_progress.zsim_event_system.event_profile import EventProfile
    from zsim.sim_progress.zsim_event_system.zsim_events.anomaly_event import AnomalyEvent

@dataclass
class AnomalySnapshot:
    """
    异常快照：存储由于触发异常时的面板计算出的固定伤害值
    """
    damage_base: float      # 计算后的基准伤害 (CalAnomaly result)
    element_type: str       # 属性类型 (fire, electric, etc.)
    attribute_data: Dict[str, float]  # 触发时的关键属性快照 (穿透率等，用于二次计算)
    source_id: str          # 来源角色ID

class DotTriggerEffect(EffectBase):
    """
    DoT 触发器效果
    根据间隔或事件触发异常伤害
    """
    def __init__(self, 
                 snapshot: AnomalySnapshot, 
                 interval: float = 0,       # 触发间隔 (ms)，0表示非时间触发
                 trigger_on_hit: bool = False, # 是否受击触发 (如感电)
                 damage_rate: float = 1.0,  # 每次触发的伤害倍率
                 **kwargs):
        super().__init__(**kwargs)
        self.snapshot = snapshot
        self.interval = interval
        self.trigger_on_hit = trigger_on_hit
        self.damage_rate = damage_rate
        self._last_trigger_time = 0.0

    def on_attach(self, owner, buff_instance: 'Buff'):
        """Buff 生效时初始化"""
        self._last_trigger_time = 0 # 或者是当前时间，取决于是否立即生效

    def on_tick(self, owner, buff_instance: 'Buff', context):
        """
        时间触发逻辑 (适用于 灼烧/中毒/物理裂伤)
        由 GlobalBuffController 或 Timer 调用
        """
        if self.trigger_on_hit or self.interval <= 0:
            return

        current_time = context.timestamp
        # 简单的间隔判断
        if current_time - self._last_trigger_time >= self.interval:
            self._execute_dot_damage(context, trigger_type="tick")
            self._last_trigger_time = current_time

    def on_event(self, owner, buff_instance: 'Buff', event: 'EventProfile'):
        """
        事件触发逻辑 (适用于 感电)
        由 EventRouter 分发
        """
        if not self.trigger_on_hit:
            return

        # 仅响应受击事件
        if event.event_type == "EnemyHit":
            # 检查内置CD (感电通常有 1s 内置CD)
            if event.timestamp - self._last_trigger_time >= self.interval:
                self._execute_dot_damage(event, trigger_type="hit")
                self._last_trigger_time = event.timestamp

    def _execute_dot_damage(self, context, trigger_type: str):
        """执行最终伤害计算与上报"""
        final_damage = self.snapshot.damage_base * self.damage_rate
        
        # 调用报告系统
        # 注意：这里需要适配你现有的 Report 接口参数
        process_dmg_result(
            tick=getattr(context, 'timestamp', 0),
            attacker_id=self.snapshot.source_id,
            target_id="enemy", # 暂定
            damage=final_damage,
            damage_type="Anomaly",
            element=self.snapshot.element_type,
            comment=f"{trigger_type}_trigger"
        )