"""异常事件处理器"""

from typing import Any

from zsim.sim_progress import Report
from zsim.sim_progress.anomaly_bar import AnomalyBar as AnB
from zsim.sim_progress.anomaly_bar.CopyAnomalyForOutput import (
    NewAnomaly,
)
from zsim.sim_progress.Buff import ScheduleBuffSettle

from ...CalAnomaly import CalAnomaly
from ..base import BaseEventHandler
from ..context import EventContext


class AnomalyEventHandler(BaseEventHandler):
    """异常事件处理器"""

    def __init__(self):
        super().__init__("anomaly")

    def can_handle(self, event: Any) -> bool:
        return type(event) is AnB or type(event) is NewAnomaly

    def handle(self, event: AnB | NewAnomaly, context: EventContext) -> None:
        """处理异常事件

        处理 AnomalyBar 和 NewAnomaly 两种类型的异常事件，包括：
        - 计算异常伤害
        - 报告伤害结果
        - 处理相关buff结算
        """
        # 验证输入
        self._validate_event(event, (AnB, NewAnomaly))
        self._validate_context(context)

        enemy = self._get_context_enemy(context)
        active_buff_view = self._get_context_active_buff_view(context)
        legacy_dynamic_buff = self._get_context_legacy_dynamic_buff(context)
        legacy_exist_buff_dict = self._get_context_legacy_exist_buff_dict(context)
        action_stack = self._get_context_action_stack(context)
        sim_instance = self._get_context_sim_instance(context)
        tick = self._get_context_tick(context)

        # 计算异常伤害
        calculator = CalAnomaly(
            anomaly_obj=event,
            enemy_obj=enemy,
            dynamic_buff=active_buff_view,
            sim_instance=sim_instance,
        )

        damage_anomaly = calculator.cal_anomaly_dmg()

        Report.report_dmg_result(
            tick=tick,
            skill_tag=event.rename_tag if event.rename else None,
            element_type=event.element_type,
            dmg_expect=round(damage_anomaly, 2),
            is_anomaly=True,
            dmg_crit=round(damage_anomaly, 2),
            stun=0,
            buildup=0,
            **enemy.dynamic.get_status(),
            UUID=event.UUID if event.UUID is not None else "",
        )

        # 处理buff结算
        ScheduleBuffSettle(
            tick,
            legacy_exist_buff_dict,
            enemy,
            legacy_dynamic_buff,
            action_stack,
            anomaly_bar=event,
            sim_instance=sim_instance,
        )
