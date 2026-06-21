from .. import Buff, JudgeTools, check_preparation
from ..JudgeTools import (
    TriggerBuffRef,
    build_preparation_context_from_buff,
    read_trigger_buff_state,
)


_SOLDIER0_ANBY_SILVER_STAR_TRIGGER_REF = TriggerBuffRef.owner(
    "零号·安比",
    "Buff-角色-零号·安比-银星触发器",
)


class Soldier0AnbyCinema4EleResReduceRecord:
    def __init__(self):
        self.char = None
        self.trigger_buff_0 = None


class Soldier0AnbyCinema4EleResReduce(Buff.BuffLogic):
    def __init__(self, buff_instance):
        """
        零号·安比的组队被动，操作角色为安比，并且目标有银星时候，全队增伤。
        """
        super().__init__(buff_instance)
        self.buff_instance: Buff = buff_instance
        self.buff_0 = None
        self.record = None
        self.xjudge = self.special_judge_logic

    def get_prepared(self, **kwargs):
        preparation_context = build_preparation_context_from_buff(self.buff_instance)
        return check_preparation(
            buff_instance=self.buff_instance,
            buff_0=self.buff_0,
            preparation_context=preparation_context,
            **kwargs,
        )

    def check_record_module(self):
        if self.buff_0 is None:
            preparation_context = build_preparation_context_from_buff(
                self.buff_instance
            )
            self.buff_0 = preparation_context.find_sub_exist_buff_dict("零号·安比")[
                self.buff_instance.ft.index
            ]
        if self.buff_0.history.record is None:
            self.buff_0.history.record = Soldier0AnbyCinema4EleResReduceRecord()
        self.record = self.buff_0.history.record

    def special_judge_logic(self, **kwargs):
        """
        只要是检测到有银星，就返回True
        """
        self.check_record_module()
        self.get_prepared(
            char_CID=1381,
            trigger_buff_0=_SOLDIER0_ANBY_SILVER_STAR_TRIGGER_REF,
        )
        trigger_state = read_trigger_buff_state(self.record)
        if trigger_state.active:
            return True
        return False
