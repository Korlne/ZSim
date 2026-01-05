from .. import Buff, JudgeTools


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
        # [新架构] 使用 BuffManager 查询装备者身上的激活 Buff
        char_obj = self.buff_instance.sim_instance.char_data.char_obj_dict.get(equipper)
        if char_obj is None or not hasattr(char_obj, "buff_manager"):
            return False

        for buff in char_obj.buff_manager._active_buffs.values():
            if "玉壶青冰-普攻加冲击" not in buff.ft.index:
                continue
            if buff.dy.count >= 15:
                return True
            return False
        return False
