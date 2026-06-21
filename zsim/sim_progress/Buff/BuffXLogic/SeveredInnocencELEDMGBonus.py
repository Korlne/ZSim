from .. import Buff, JudgeTools, check_preparation
from ..JudgeTools import (
    TriggerBuffRef,
    build_preparation_context_from_buff,
    read_trigger_buff_state,
)


class SeveredInnocencELEDMGBonusRecord:
    def __init__(self):
        self.char = None
        self.equipper = None
        self.trigger_buff_0 = None


class SeveredInnocencELEDMGBonus(Buff.BuffLogic):
    """
    牺牲洁纯的电伤判定
    """

    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance: Buff = buff_instance
        self.buff_0 = None
        self.equipper = None
        self.record = None
        self.xjudge = self.special_judge_logic
        self.xexit = self.special_exit_logic

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
            self.equipper = preparation_context.find_equipper("牺牲洁纯")
        if self.buff_0 is None:
            if preparation_context is None:
                preparation_context = build_preparation_context_from_buff(
                    self.buff_instance
                )
            self.buff_0 = preparation_context.find_sub_exist_buff_dict(self.equipper)[
                self.buff_instance.ft.index
            ]
        if self.buff_0.history.record is None:
            self.buff_0.history.record = SeveredInnocencELEDMGBonusRecord()
        self.record = self.buff_0.history.record

    def special_judge_logic(self, **kwargs):
        """查装备者身上的触发暴伤的Buff是否为3层"""
        self.check_record_module()
        self.get_prepared(
            char_CID=1381,
            equipper="牺牲洁纯",
            trigger_buff_0=TriggerBuffRef.equipper("牺牲洁纯-触发暴伤"),
        )
        trigger_state = read_trigger_buff_state(self.record)
        if trigger_state.count == 3:
            if not trigger_state.active:
                raise ValueError(f"{self.record.trigger_buff_0.ft.index}有层数但是未激活！")
            return True
        return False

    def special_exit_logic(self, **kwargs):
        """xjudge的反逻辑"""
        if self.xjudge:
            return False
        else:
            return True
