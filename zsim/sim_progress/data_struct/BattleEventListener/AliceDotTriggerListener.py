from typing import TYPE_CHECKING

from zsim.define import ALICE_REPORT
from zsim.models.event_enums import ListenerBroadcastSignal as LBS

from .BaseListenerClass import BaseListener

if TYPE_CHECKING:
    from zsim.sim_progress.Character.Alice import Alice
    from zsim.sim_progress.Character.character import Character
    from zsim.simulator.simulator_class import Simulator


class AliceDotTriggerListener(BaseListener):
    """这个监听器的作用是监听畏缩的激活与刷新"""

    def __init__(self, listener_id: str | None = None, sim_instance: "Simulator | None" = None):
        super().__init__(listener_id, sim_instance=sim_instance)
        self.char: "Character | None | Alice" = None

    def listening_event(self, event, signal: LBS, **kwargs):
        """监听到紊乱信号时，激活"""
        if self.char is None:
            char_obj = self.sim_instance.char_data.find_char_obj(CID=1401)
            self.char = char_obj
        if signal not in [LBS.ASSAULT_STATE_ON]:
            return
        self.listener_active()

    def listener_active(self, **kwargs):
        """核心被动激活，给敌人添加Dot"""
        enemy = self.sim_instance.schedule_data.enemy
        # 验证
        if not enemy.dynamic.assault:
            raise ValueError(
                "【爱丽丝核心被动Dot监听器警告】敌人当前的状态不符合核心被动激活条件，请检查！"
            )

        from copy import deepcopy

        # [New Architecture] 移除 spawn_normal_dot 和 Dot 类
        # from zsim.sim_progress.Update.UpdateAnomaly import spawn_normal_dot
        # from zsim.sim_progress.Dot.BaseDot import Dot

        """
        获取快照逻辑保留
        """
        phy_anomaly_bar = deepcopy(enemy.anomaly_bars_dict[0])
        phy_anomaly_bar.anomaly_settled()

        # [Refactor] 使用 BuffManager 添加 Dot
        dot_buff_id = "AliceCoreSkillAssaultDot"
        if hasattr(enemy, "buff_manager"):
            # 添加 Buff
            new_buff = enemy.buff_manager.add_buff(dot_buff_id, current_tick=self.sim_instance.tick)

            # 如果 add_buff 不直接返回实例（假设根据 BuffManagerClass 源码它可能返回 None 或 Buff）
            # 我们尝试获取它来注入快照
            if new_buff is None:
                new_buff = enemy.buff_manager.get_buff(dot_buff_id)

            if new_buff:
                # 注入快照数据到 custom_data，供 Effect 使用
                new_buff.dy.custom_data["anomaly_snapshot"] = phy_anomaly_bar

                # 为了日志和事件记录，可能需要手动添加到 event_list，
                # 但通常 Buff 激活应该由 BuffManager 处理日志。
                # 如果仍需向 ScheduleData.event_list 汇报异常数据（用于统计面板等）：
                # event_list.append(phy_anomaly_bar) # 可选，视具体需求
        else:
            print("Error: Enemy missing buff_manager.")

        # 添加事件到列表供前端显示或日志记录
        event_list = self.sim_instance.schedule_data.event_list
        event_list.append(phy_anomaly_bar)

        if ALICE_REPORT:
            self.sim_instance.schedule_data.change_process_state()
            print("【爱丽丝事件】检测到畏缩状态更新，核心被动Dot激活！")
