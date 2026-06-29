from .. import Buff, check_preparation
from ..JudgeTools import build_preparation_context_from_buff


class CordisGerminaCritRateBonusRecord:
    def __init__(self):
        self.equipper = None
        self.char = None


class CordisGerminaCritRateBonus(Buff.BuffLogic):
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance: Buff = buff_instance
        self.xjudge = self.special_judge_logic
        self.equipper = None
        self.buff_0 = None
        self.record: CordisGerminaCritRateBonusRecord | None = None

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
            self.equipper = preparation_context.find_equipper("机巧心种")
        if self.buff_0 is None:
            if preparation_context is None:
                preparation_context = build_preparation_context_from_buff(
                    self.buff_instance
                )
            self.buff_0 = preparation_context.find_sub_exist_buff_dict(self.equipper)[
                self.buff_instance.ft.index
            ]
        if self.buff_0.history.record is None:
            self.buff_0.history.record = CordisGerminaCritRateBonusRecord()
        self.record = self.buff_0.history.record

    def special_judge_logic(self, **kwargs):
        self.check_record_module()
        self.get_prepared(equipper="机巧心种")
