from .. import Buff, JudgeTools, check_preparation
from ..JudgeTools import (
    TriggerBuffRef,
    build_preparation_context_from_buff,
    read_trigger_buff_state,
)


class SharpenedStingerAnomalyBuildupBonusRecord:
    def __init__(self):
        self.equipper = None
        self.char = None
        self.update_signal = None
        self.preload_data = None
        self.sub_exist_buff_dict = None
        self.trigger_buff_0 = None


class SharpenedStingerAnomalyBuildupBonus(Buff.BuffLogic):
    """淬锋钳刺第二个特效的判断逻辑"""

    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance: Buff = buff_instance
        self.xjudge = self.special_judge_logic
        self.xexit = self.special_exit_logic
        self.equipper = None
        self.buff_0 = None
        self.record = None

    def get_prepared(self, **kwargs):
        preparation_context = build_preparation_context_from_buff(self.buff_instance)
        return check_preparation(
            buff_instance=self.buff_instance,
            buff_0=self.buff_0,
            preparation_context=preparation_context,
            **kwargs,
        )

    def check_record_module(self):
        preparation_context = None
        if self.equipper is None:
            preparation_context = build_preparation_context_from_buff(self.buff_instance)
            self.equipper = preparation_context.find_equipper("淬锋钳刺")
        if self.buff_0 is None:
            if preparation_context is None:
                preparation_context = build_preparation_context_from_buff(
                    self.buff_instance
                )
            self.buff_0 = preparation_context.find_sub_exist_buff_dict(self.equipper)[
                self.buff_instance.ft.index
            ]
        if self.buff_0.history.record is None:
            self.buff_0.history.record = SharpenedStingerAnomalyBuildupBonusRecord()
        self.record = self.buff_0.history.record

    def special_judge_logic(self, **kwargs):
        """淬锋钳刺的第二特效触发逻辑：触发器Buff为3层时触发。"""
        self.check_record_module()
        self.get_prepared(
            equipper="淬锋钳刺",
            preload_data=1,
            trigger_buff_0=TriggerBuffRef.equipper("淬锋钳刺-猎意"),
        )
        trigger_state = read_trigger_buff_state(self.record)
        if trigger_state.count == 3:
            return True
        else:
            return False

    def special_exit_logic(self, **kwargs):
        return not self.special_judge_logic(**kwargs)
