from .. import Buff, JudgeTools


def _read_ice_jade_dynamic_buff_list(sim_instance):
    return sim_instance.global_stats.DYNAMIC_BUFF_DICT


class IceJadeTeaPotExtraDMGBonus(Buff.BuffLogic):
    """
    青衣专武>=15层时的额外增伤触发判定。
    """

    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance: Buff = buff_instance
        self.xjudge = self.special_judge_logic

    def special_judge_logic(self, **kwargs):
        equipper = JudgeTools.find_equipper(
            "玉壶青冰", sim_instance=self.buff_instance.sim_instance
        )
        dynamic_buff_list = _read_ice_jade_dynamic_buff_list(
            self.buff_instance.sim_instance
        )
        for buffs in dynamic_buff_list[equipper]:
            if "玉壶青冰-普攻加冲击" not in buffs.ft.index:
                continue
            if buffs.dy.count >= 15:
                return True
            else:
                return False
