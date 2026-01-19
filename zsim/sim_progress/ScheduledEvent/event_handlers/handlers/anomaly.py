"""异常事件处理器"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from zsim.sim_progress import Report
from zsim.sim_progress.anomaly_bar import AnomalyBar as AnB
from zsim.sim_progress.anomaly_bar.CopyAnomalyForOutput import (
    NewAnomaly,
)

# [Refactor] 移除旧 Buff 系统依赖
# from zsim.sim_progress.Buff import ScheduleBuffSettle
from ...CalAnomaly import CalAnomaly
from ..base import BaseEventHandler
from ..context import EventContext

if TYPE_CHECKING:
    from zsim.simulator.simulator_class import Simulator


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
        - [New] 广播异常事件以触发相关Buff或角色机制 (替代旧的 ScheduleBuffSettle)
        """
        # 验证输入
        self._validate_event(event, (AnB, NewAnomaly))
        self._validate_context(context)

        enemy = self._get_context_enemy(context)
        # [Refactor] 移除旧接口相关变量，仅保留 BuffManager 所需数据
        sim_instance = self._get_context_sim_instance(context)
        tick = self._get_context_tick(context)

        # 计算异常伤害
        calculator = CalAnomaly(
            anomaly_obj=event,
            enemy_obj=enemy,
            # [Refactor] CalAnomaly 接口已更新，不再需要 dynamic_buff
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

        # [Refactor] 使用事件广播替代 ScheduleBuffSettle
        # 旧逻辑：ScheduleBuffSettle 负责触发“造成异常时”的 Buff 或逻辑
        # 新逻辑：通过广播事件，让角色或 BuffManager 自行监听处理
        self._broadcast_anomaly_event(event, sim_instance)

    def _broadcast_anomaly_event(self, event: AnB | NewAnomaly, sim_instance: Simulator) -> None:
        """广播异常事件到所有角色

        Args:
            event: 异常事件对象
            sim_instance: 模拟器实例
        """
        # 通知所有角色（例如：柳需要根据异常事件更新特殊资源/架势）
        for char_obj in sim_instance.char_data.char_obj_list:
            if hasattr(char_obj, "update_special_resource"):
                char_obj.update_special_resource(event)
