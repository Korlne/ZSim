from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import polars as pl

from zsim.define import (
    CHARACTER_DATA_PATH,
    EQUIP_2PC_DATA_PATH,
    SUB_STATS_MAPPING,
    WEAPON_DATA_PATH,
)
from zsim.models.session.session_run import CharConfig, ExecAttrCurveCfg, ExecWeaponCfg

# 引入 BonusPool
from zsim.sim_progress.Character.bonus_pool import BonusPool
from zsim.sim_progress.Character.skill_class import Skill, lookup_name_or_cid
from zsim.sim_progress.Character.utils.filters import _skill_node_filter, _sp_update_data_filter
from zsim.sim_progress.Report import report_to_log

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff
    from zsim.sim_progress.data_struct.sp_update_data import SPUpdateData
    from zsim.sim_progress.Preload.SkillsQueue import SkillNode
    from zsim.simulator.simulator_class import Simulator


class Character:
    def __init__(
        self,
        *,
        char_config: CharConfig,
        sim_cfg: ExecAttrCurveCfg | ExecWeaponCfg | None = None,
    ):
        """
        调用时，会生成包含全部角色基础信息的对象，自动从数据库中查找全部信息

        参数：
        - char_config: CharConfig对象，包含角色的所有配置信息
        - sim_cfg: 模拟配置对象，可选参数，用于特殊模拟模式

        自生成参数：
        -self.level = 60 默认角色等级，传给防御区用
        -记录每个基础属性来源的各参数，主要来自查表
        -包含角色全部技能信息的 Skill 对象，以及来自 Skill 的 action_list, skills_dict

        暴击非配平逻辑（直接读取）：
        scCRIT: 暴击率副词条
        scCRIT_DMG: 暴击伤害副词条

        是否配平由传入参数 char_config.crit_balancing 控制
        配平逻辑下，暴伤与暴击率词条将会被重新分配，且没有基于整数词条数量的自动重整

        """
        # 从CharConfig对象中提取参数
        name = char_config.name
        CID = char_config.CID
        weapon = char_config.weapon
        weapon_level = char_config.weapon_level
        equip_style = char_config.equip_style
        equip_set4 = char_config.equip_set4
        equip_set2_a = char_config.equip_set2_a
        equip_set2_b = char_config.equip_set2_b
        equip_set2_c = char_config.equip_set2_c
        drive4 = char_config.drive4
        drive5 = char_config.drive5
        drive6 = char_config.drive6
        scATK_percent = char_config.scATK_percent
        scATK = char_config.scATK
        scHP_percent = char_config.scHP_percent
        scHP = char_config.scHP
        scDEF_percent = char_config.scDEF_percent
        scDEF = char_config.scDEF
        scAnomalyProficiency = char_config.scAnomalyProficiency
        scPEN = char_config.scPEN
        scCRIT = char_config.scCRIT
        scCRIT_DMG = char_config.scCRIT_DMG
        sp_limit = char_config.sp_limit
        cinema = char_config.cinema
        crit_balancing = char_config.crit_balancing
        crit_rate_limit = char_config.crit_rate_limit

        # 从数据库中查找角色信息，并核对必填项
        self.NAME, self.CID = lookup_name_or_cid(name, CID)

        # 必须在 self.statement 初始化之前完成
        self.bonus_pool = BonusPool(self)

        # 初始化为0的各属性
        self.baseATK = 0.0
        self.ATK_percent = 0.0
        self.ATK_numeric = 0.0
        self.overall_ATK_percent = 0.0
        self.overall_ATK_numeric = 0.0

        self.baseHP = 0.0
        self.HP_percent = 0.0
        self.HP_numeric = 0.0
        self.overall_HP_percent = 0.0
        self.overall_HP_numeric = 0.0

        self.baseDEF = 0.0
        self.DEF_percent = 0.0
        self.DEF_numeric = 0.0
        self.overall_DEF_percent = 0.0
        self.overall_DEF_numeric = 0.0

        self.baseIMP = 0.0
        self.IMP_percent = 0.0
        self.IMP_numeric = 0.0
        self.overall_IMP_percent = 0.0
        self.overall_IMP_numeric = 0.0

        self.baseAP = 0.0
        self.AP_percent = 0.0
        self.AP_numeric = 0.0
        self.overall_AP_percent = 0.0
        self.overall_AP_numeric = 0.0

        self.baseAM = 0.0
        self.AM_percent = 0.0
        self.AM_numeric = 0.0
        self.overall_AM_percent = 0.0
        self.overall_AM_numeric = 0.0

        self.CRIT_rate_numeric = 0.0  # 暴击率（非配平逻辑使用）
        self.CRIT_damage_numeric = 0.0  # 暴击伤害（非配平逻辑使用）

        self.base_sp_regen = 0.0
        self.sp_regen_percent = 0.0
        self.sp_regen_numeric = 0.0

        self.ICE_DMG_bonus = 0.0
        self.FIRE_DMG_bonus = 0.0
        self.PHY_DMG_bonus = 0.0
        self.ETHER_DMG_bonus = 0.0
        self.ELECTRIC_DMG_bonus = 0.0
        self.ALL_DMG_bonus = 0.0
        self.Trigger_DMG_bonus = 0.0

        self.PEN_ratio = 0.0
        self.PEN_numeric = 0.0

        # 单独初始化的各组件
        self.level: int = 60
        self.weapon_ID: str | None = weapon
        self.weapon_level: int = weapon_level
        self.cinema: int = cinema
        self.baseCRIT_score: float = 60
        self.sp_get_ratio: float = 1  # 能量获得效率
        self.sp_limit: int = int(sp_limit)
        self.sp: float = 40.0

        self.decibel: float = 1000.0

        self.specialty: str | None
        self.element_type: int

        self.crit_balancing: bool = crit_balancing
        self.crit_rate_limit: float = crit_rate_limit
        self.sheer_attack_conversion_rate: dict[int, float] | None = None

        # 初始化角色基础属性    .\data\character.csv
        self._init_base_attribute(name)
        # fmt: off
        # 如果并行配置没有移除套装，就初始化套装效果和主副词条
        if sim_cfg is not None:
            if isinstance(sim_cfg, ExecAttrCurveCfg):
                if not sim_cfg.remove_equip:
                    self.__init_all_equip_static(drive4, drive5, drive6,
                                                equip_set2_a, equip_set2_b, equip_set2_c, equip_set4, equip_style,
                                                scATK, scATK_percent, scAnomalyProficiency, scCRIT,
                                                scCRIT_DMG, scDEF, scDEF_percent, scHP, scHP_percent, scPEN)
                self.__init_attr_curve_config(sim_cfg)
                self._init_weapon_primitive(weapon, weapon_level)
            elif isinstance(sim_cfg, ExecWeaponCfg):
                self.__init_all_equip_static(drive4, drive5, drive6,
                                         equip_set2_a, equip_set2_b, equip_set2_c, equip_set4, equip_style,
                                         scATK, scATK_percent, scAnomalyProficiency, scCRIT,
                                         scCRIT_DMG, scDEF, scDEF_percent, scHP, scHP_percent, scPEN)
                self._init_weapon_primitive(sim_cfg.weapon_name, sim_cfg.weapon_level)  # 覆盖武器基础属性
        else:
            self.__init_all_equip_static(drive4, drive5, drive6,
                                         equip_set2_a, equip_set2_b, equip_set2_c, equip_set4, equip_style,
                                         scATK, scATK_percent, scAnomalyProficiency, scCRIT,
                                         scCRIT_DMG, scDEF, scDEF_percent, scHP, scHP_percent, scPEN)
            # 初始化武器基础属性    .\data\weapon.csv
            self._init_weapon_primitive(weapon, weapon_level)

        self.additional_abililty_active: bool | None = None     # 角色是否激活组队被动，该参数将在Buff模块初始化完成后进行赋值

        skill_level_addon = 4 if self.cinema >=5 else (2 if self.cinema >= 3 else 0)
        skills_level: dict[str, int] = {
            "normal_level": 12 + skill_level_addon,
            "special_level": 12 + skill_level_addon,
            "dodge_level": 12 + skill_level_addon,
            "chain_level": 12 + skill_level_addon,
            "assist_level": 12 + skill_level_addon,
        }

        self.statement = Character.Statement(self, crit_balancing=crit_balancing)
        self.skill_object: Skill = Skill(name=self.NAME, CID=self.CID, **skills_level, char_obj=self)
        self.action_list = self.skill_object.action_list
        self.skills_dict = self.skill_object.skills_dict
        self.dynamic = self.Dynamic(self)
        self.sim_instance: "Simulator | None" = None        # 模拟器实例
        self.equip_buff_map: dict[int, "Buff"] = {}     # 来自装备的Buff0的指针

    # fmt: off
    def __init_all_equip_static(self, drive4, drive5, drive6,
                                equip_set2_a, equip_set2_b, equip_set2_c, equip_set4, equip_style,
                                scATK, scATK_percent, scAnomalyProficiency, scCRIT,
                                scCRIT_DMG, scDEF, scDEF_percent, scHP, scHP_percent, scPEN):
        # fmt: on
        # 初始化套装效果        .\data\equip_set_2pc.csv
        self._init_equip_set(
            equip_style, equip_set4, equip_set2_a, equip_set2_b, equip_set2_c
        )
        # 初始化主词条
        self._init_main_stats(drive4, drive5, drive6)
        # 初始化副词条
        self._init_sub_stats(
            scATK_percent, scATK, scHP_percent,scHP, scDEF_percent, scDEF, scAnomalyProficiency, scPEN, scCRIT, scCRIT_DMG,
        )
    # fmt: on

    class Statement:
        def __init__(self, char: "Character", crit_balancing: bool):
            """
            计算角色面板属性 (重构版)。
            集成了 BonusPool 中的 Buff 加成效果。
            """
            bp = char.bonus_pool  # 获取 BonusPool 引用

            self.NAME = char.NAME
            self.CID = char.CID

            # --- 攻击力 ---
            # 基础百分比 = 装备% + Buff(加算)%
            atk_pct_total = (
                char.ATK_percent
                + bp.query_total_add("攻击力%")
                + bp.query_total_add("攻击力百分比")
            )
            # 基础固定值 = 装备固定值 + Buff固定值
            atk_flat_total = (
                char.ATK_numeric + bp.query_total_add("攻击力") + bp.query_total_add("攻击力数值")
            )
            # 局内乘区 (Overall)
            overall_atk_pct = char.overall_ATK_percent + bp.query_total_mul("攻击力")

            self.ATK = (char.baseATK * (1 + atk_pct_total) + atk_flat_total) * (
                1 + overall_atk_pct
            ) + char.overall_ATK_numeric

            # --- 生命值 ---
            hp_pct_total = char.HP_percent + bp.query_total_add("生命值%")
            hp_flat_total = char.HP_numeric + bp.query_total_add("生命值")

            self.HP = (char.baseHP * (1 + hp_pct_total) + hp_flat_total) * (
                1 + char.overall_HP_percent
            ) + char.overall_HP_numeric

            # --- 防御力 ---
            def_pct_total = char.DEF_percent + bp.query_total_add("防御力%")
            def_flat_total = char.DEF_numeric + bp.query_total_add("防御力")

            self.DEF = (char.baseDEF * (1 + def_pct_total) + def_flat_total) * (
                1 + char.overall_DEF_percent
            ) + char.overall_DEF_numeric

            # --- 冲击力 ---
            imp_pct_total = char.IMP_percent + bp.query_total_add("冲击力%")
            imp_flat_total = char.IMP_numeric + bp.query_total_add("冲击力")

            self.IMP = (char.baseIMP * (1 + imp_pct_total) + imp_flat_total) * (
                1 + char.overall_IMP_percent
            ) + char.overall_IMP_numeric

            # --- 异常精通 (AP) ---
            ap_pct_total = char.AP_percent + bp.query_total_add("异常精通%")
            ap_flat_total = char.AP_numeric + bp.query_total_add("异常精通")

            self.AP = (char.baseAP * (1 + ap_pct_total) + ap_flat_total) * (
                1 + char.overall_AP_percent
            ) + char.overall_AP_numeric

            # --- 异常掌控 (AM) ---
            am_pct_total = char.AM_percent + bp.query_total_add("异常掌控%")
            am_flat_total = char.AM_numeric + bp.query_total_add("异常掌控")

            self.AM = (char.baseAM * (1 + am_pct_total) + am_flat_total) * (
                1 + char.overall_AM_percent
            ) + char.overall_AM_numeric

            # --- 双暴 (Critical) ---
            # 获取 Buff 带来的额外暴击/暴伤
            buff_crit_rate = bp.query_total_add("暴击率") + bp.query_total_add("暴击率%")
            buff_crit_dmg = bp.query_total_add("暴击伤害") + bp.query_total_add("暴击伤害%")

            self.CRIT_damage, self.CRIT_rate = self._func_statement_CRIT(
                char.baseCRIT_score,
                char.CRIT_rate_numeric + buff_crit_rate,
                char.CRIT_damage_numeric + buff_crit_dmg,
                char.crit_rate_limit,
                balancing=crit_balancing,
            )

            # --- 能量回复 & 获取效率 ---
            sp_regen_pct = char.sp_regen_percent + bp.query_total_add("能量自动回复%")
            sp_regen_flat = char.sp_regen_numeric + bp.query_total_add("能量自动回复")
            self.sp_regen = char.base_sp_regen * (1 + sp_regen_pct) + sp_regen_flat

            self.sp_get_ratio = char.sp_get_ratio + bp.query_total_add("能量获取效率")
            self.sp_limit = char.sp_limit

            # --- 穿透 (Penetration) ---
            self.PEN_ratio = (
                char.PEN_ratio + bp.query_total_add("穿透率") + bp.query_total_add("穿透率%")
            )
            self.PEN_numeric = char.PEN_numeric + bp.query_total_add("穿透值")

            # --- 属性伤害加成 ---
            self.ICE_DMG_bonus = char.ICE_DMG_bonus + bp.query_total_add("冰属性伤害提升")
            self.FIRE_DMG_bonus = char.FIRE_DMG_bonus + bp.query_total_add("火属性伤害提升")
            self.PHY_DMG_bonus = char.PHY_DMG_bonus + bp.query_total_add("物理属性伤害提升")
            self.ETHER_DMG_bonus = char.ETHER_DMG_bonus + bp.query_total_add("以太属性伤害提升")
            self.ELECTRIC_DMG_bonus = char.ELECTRIC_DMG_bonus + bp.query_total_add("电属性伤害提升")

            self.ALL_DMG_bonus = (
                char.ALL_DMG_bonus
                + bp.query_total_add("全属性伤害提升")
                + bp.query_total_add("造成的伤害提升")
            )
            self.Trigger_DMG_bonus = char.Trigger_DMG_bonus  # 保留原有逻辑

            # 将当前对象 (self) 的所有非可调用属性收集到一个字典中
            self.statement = {
                attr: getattr(self, attr)
                for attr in dir(self)
                if not callable(getattr(self, attr)) and not attr.startswith("__")
            }
            report_to_log(f"[CHAR STATUS]:{self.NAME}:{str(self.statement)}")

        @staticmethod
        def _func_statement_CRIT(
            CRIT_score: float,
            CRIT_rate_numeric: float,
            CRIT_damage_numeric: float,
            CRIT_rate_limit: float,
            balancing: bool,
        ) -> tuple[float, float]:
            """
            双暴状态函数
            balancing : 是否使用配平逻辑
            CRIT_score : 暴击评分
            CRIT_rate_numeric : 暴击率数值
            CRIT_damage_numeric : 暴击伤害数值
            返回：
            CRIT_damage : 暴击伤害
            CRIT_rate : 暴击率

            默认为True，即配平逻辑，会使用暴击评分、暴击暴伤输出，集中计算暴击率与暴击伤害
            若为False，则忽略传入的暴击评分，直接返回给定的数值
            """
            # 参数有效性验证
            if not (0 <= CRIT_score):
                raise ValueError("CRIT_score must be above 0")
            if not (0 <= CRIT_rate_numeric):
                raise ValueError("CRIT_rate_numeric must be above 0")
            if not (0 <= CRIT_damage_numeric):
                raise ValueError("CRIT_damage_numeric must be above 0")
            if not (0 <= CRIT_rate_limit <= 1):
                raise ValueError("CRIT_rate_limit must be between 0 and 1")

            if balancing:
                limit_score: float = CRIT_rate_limit * 400
                if CRIT_score >= limit_score:
                    CRIT_rate = CRIT_rate_limit
                    CRIT_damage = (CRIT_score - CRIT_rate * 200) / 100

                else:
                    CRIT_damage = max(0.5, CRIT_score / 200)
                    CRIT_rate = (CRIT_score / 100 - CRIT_damage) / 2
            else:
                CRIT_damage = CRIT_damage_numeric
                CRIT_rate = CRIT_rate_numeric
            return min(5.0, CRIT_damage), min(1.0, CRIT_rate)

        def __str__(self) -> str:
            return f"角色静态面板：{self.NAME}"

    class Dynamic:
        """用于记录角色各种动态信息的类，主要和APL模块进行互动。"""

        def __init__(self, char_instantce: Character):
            self.character = char_instantce
            self.lasting_node = LastingNode(self.character)
            from zsim.sim_progress.data_struct.QuickAssistSystem.quick_assist_manager import (
                QuickAssistManager,
            )

            self.quick_assist_manager = QuickAssistManager(self.character)
            self._on_field = False  # 角色是否在前台
            self._switching_in_tick = 0  # 角色切到前台状态的时间点
            self._switching_out_tick = 0  # 角色切到后台状态的时间点

        def reset(self):
            self.lasting_node.reset()
            self.on_field = False

        @property
        def on_field(self) -> bool:
            return self._on_field

        @on_field.setter
        def on_field(self, value: bool):
            assert self.character.sim_instance is not None
            tick = self.character.sim_instance.tick
            if self.on_field and not value:
                # 角色on_field状态的下降沿，即角色从前台切换到后台
                self._switching_out_tick = tick
            elif not self.on_field and value:
                # 角色on_field状态的上升沿，即角色从后台切换到前台
                self._switching_in_tick = tick
            self._on_field = value

        def is_off_field_within(self, max_ticks: int) -> bool:
            """判断角色切到后台的时间是否小于等于指定时间"""
            assert self.character.sim_instance is not None
            if self.on_field:
                return False
            current_tick = self.character.sim_instance.tick
            return current_tick - self._switching_out_tick <= max_ticks

        def is_on_field_within(self, max_ticks: int) -> bool:
            """判断角色切到前台的时间是否小于等于指定时间"""
            assert self.character.sim_instance is not None
            if not self.on_field:
                return False
            current_tick = self.character.sim_instance.tick
            return current_tick - self._switching_in_tick <= max_ticks

    def is_available(self, tick: int):
        """查询角色当前tick是否有空"""
        lasting_node = self.dynamic.lasting_node
        if lasting_node is None:
            return ValueError("角色没有LastingNode")
        node = lasting_node.node
        if node is None:
            return True
        if node.end_tick >= tick:
            return False
        return True

    def __mapping_csv_to_attr(self, row: dict):
        self.baseATK += float(row.get("base_ATK", 0))
        self.ATK_percent += float(row.get("ATK%", 0))
        self.DEF_percent += float(row.get("DEF%", 0))
        self.HP_percent += float(row.get("HP%", 0))
        self.IMP_percent += float(row.get("IMP%", 0))
        self.overall_ATK_percent += float(row.get("oATK%", 0))
        self.overall_DEF_percent += float(row.get("oDEF%", 0))
        self.overall_HP_percent += float(row.get("oHP%", 0))
        self.overall_IMP_percent += float(row.get("oIMP%", 0))
        self.AM_percent += float(row.get("Anomaly_Mastery", 0))
        self.AP_numeric += float(row.get("Anomaly_Proficiency", 0))
        self.sp_regen_percent += float(row.get("Regen%", 0))
        self.sp_regen_numeric += float(row.get("Regen", 0))
        self.sp_get_ratio += float(row.get("Get_ratio", 0))
        self.PEN_ratio += float(row.get("pen%", 0))
        self.ICE_DMG_bonus += float(row.get("ICE_DMG_bonus", 0))
        self.FIRE_DMG_bonus += float(row.get("FIRE_DMG_bonus", 0))
        self.ELECTRIC_DMG_bonus += float(row.get("ELECTRIC_DMG_bonus", 0))
        self.PHY_DMG_bonus += float(row.get("PHY_DMG_bonus", 0))
        self.ETHER_DMG_bonus += float(row.get("ETHER_DMG_bonus", 0))
        if self.crit_balancing:
            crit_score_delta = 100 * (
                float(row.get("Crit_Rate", 0)) * 2 + float(row.get("Crit_DMG", 0))
            )
            self.baseCRIT_score += crit_score_delta
        else:
            self.CRIT_rate_numeric += float(row.get("Crit_Rate", 0))
            self.CRIT_damage_numeric += float(row.get("Crit_DMG", 0))

    def _init_base_attribute(self, char_name: str):
        """
        初始化角色基础属性。
        根据角色名称，从CSV文件中读取角色的基础属性数据，并将其赋值给角色对象。
        参数:
        char_name(str): 角色的名称。
        """
        if not isinstance(char_name, str) or not char_name.strip():
            raise ValueError("角色名称必须是非空字符串")
        try:
            row = (
                pl.scan_csv(CHARACTER_DATA_PATH)
                .filter(pl.col("name") == char_name)
                .collect()
                .to_dicts()
            )
            if row:
                # 将对应记录提取出来，并赋值给角色对象
                row_0: dict = row[0]
                self.baseATK = float(row_0.get("基础攻击力", 0))
                self.baseHP = float(row_0.get("基础生命值", 0))
                self.baseDEF = float(row_0.get("基础防御力", 0))
                self.baseIMP = float(row_0.get("基础冲击力", 0))
                self.baseAP = float(row_0.get("基础异常精通", 0))
                self.baseAM = float(row_0.get("基础异常掌控", 0))
                # self.baseCRIT_score = float(row_0.get("基础暴击分数", 60))
                self.CRIT_rate_numeric = float(
                    row_0.get("基础暴击率", 0)
                )  # 此处不需要根据暴击配平区分
                self.CRIT_damage_numeric = float(row_0.get("基础暴击伤害", 1))
                self.baseCRIT_score = 100 * (self.CRIT_rate_numeric * 2 + self.CRIT_damage_numeric)
                # print(f'{self.NAME}的核心被动初始化完成！当前暴击分数为：{self.baseCRIT_score}')

                self.PEN_ratio = float(row_0.get("基础穿透率", 0))
                self.PEN_numeric = float(row_0.get("基础穿透值", 0))
                self.base_sp_regen = float(row_0.get("基础能量自动回复", 0))
                self.base_sp_get_ratio = float(row_0.get("基础能量获取效率", 1))
                self.specialty = row_0.get("角色特性", None)  # 角色特性，强攻、击破等
                self.aid_type = row_0.get("支援类型", None)
                self.element_type = row_0.get("角色属性", 0)
                if self.element_type is None or self.element_type < 0:
                    raise NotImplementedError(f"角色{char_name}的属性类型未定义")
                # CID特殊处理，避免不必要的类型转换
                cid_value: int | None = row_0.get("CID", None)
                self.CID = int(cid_value) if cid_value is not None else -1
            else:
                raise ValueError(f"角色{char_name}不存在")
        except FileNotFoundError:
            logging.error("找不到角色数据文件，请检查路径是否正确。")
            raise
        except Exception as e:
            logging.error(f"初始化角色属性时发生未知错误：{e}")
            raise

    def _init_weapon_primitive(self, weapon: str | None, weapon_level: int) -> None:
        """初始化武器主属性（适配新版 weapon.csv）"""
        if weapon is None:
            return

        df = pl.read_csv(WEAPON_DATA_PATH)
        row = df.filter(pl.col("名称") == weapon)
        if row.height > 0:
            row_0 = row.row(0, named=True)
            base_atk = float(row_0["60级基础攻击力"])
            attr_value = row_0["60级高级属性值"]
            self.baseATK += base_atk
            # 处理高级属性
            attr_type = row_0["高级属性"]
            attr_value = float(attr_value)
            if attr_type in ["攻击力"]:
                self.ATK_percent += attr_value if attr_value < 1 else 0
            elif attr_type in ["暴击率"]:
                if self.crit_balancing:
                    self.baseCRIT_score += attr_value * 200  # 1%暴击率=2分 -> 1暴击率=200分
                else:
                    self.CRIT_rate_numeric += attr_value
            elif attr_type in ["暴击伤害"]:
                if self.crit_balancing:
                    self.baseCRIT_score += attr_value * 100  # 1暴击伤害=100分
                else:
                    self.CRIT_damage_numeric += attr_value
            elif attr_type in ["异常精通"]:
                self.AP_numeric += attr_value
            elif attr_type in ["冲击力"]:
                self.IMP_percent += attr_value
            elif attr_type in ["防御力"]:
                self.DEF_percent += attr_value
            elif attr_type in ["生命值"]:
                self.HP_percent += attr_value
            elif attr_type in ["穿透率"]:
                self.PEN_ratio += attr_value
            elif attr_type in ["能量自动回复"]:
                self.sp_regen_percent += attr_value
            else:
                raise ValueError(f"未知的武器高级属性类型：{attr_type}")
        else:
            raise ValueError(f"请输入正确的武器名称，{weapon} 不存在！")

    def _init_equip_set(
        self,
        equip_style: str,
        equip_set4: str | None,
        equip_set2_a: str | None,
        equip_set2_b: str | None,
        equip_set2_c: str | None,
    ):
        """初始化套装效果, Character类仅计算二件套"""
        if equip_style not in ["4+2", "2+2+2"]:
            raise ValueError("请输入正确的套装格式")
        # 将自身套装效果抄录
        equip_set_all = [equip_set4, equip_set2_a, equip_set2_b, equip_set2_c]
        # 检查四件套与三个二件套是否有相同的套装
        used_sets = []
        if equip_set4:
            used_sets.append(equip_set4)
        two_piece_sets = [equip_set2_a, equip_set2_b, equip_set2_c]
        for set_name in two_piece_sets:
            if set_name:
                if set_name in used_sets:
                    raise ValueError("四件套与二件套中请勿输入重复的套装名称")
        del used_sets, two_piece_sets
        self.equip_set4, self.equip_set2_a, self.equip_set2_b, self.equip_set2_c = equip_set_all
        # 4+2格式则移出2b、2c
        if equip_style == "4+2":  # 非空判断
            if equip_set2_b in equip_set_all:  # 别删这个if，否则输入None会报错
                equip_set_all.remove(equip_set2_b)
            if equip_set2_c in equip_set_all:  # 别删这个if，否则输入None会报错
                equip_set_all.remove(equip_set2_c)
        else:
            if equip_set4 in equip_set_all:  # 别删这个if，否则输入None会报错
                equip_set_all.remove(equip_set4)
        if equip_set_all is not None:  # 全空则跳过
            lf = pl.scan_csv(EQUIP_2PC_DATA_PATH)
            for equip_2pc in equip_set_all:
                if bool(equip_2pc):  # 若二件套非空，则继续
                    row: list[dict] = lf.filter(pl.col("set_ID") == equip_2pc).collect().to_dicts()
                    if row:
                        row_0 = row[0]
                        self.__mapping_csv_to_attr(row_0)
                    else:
                        raise ValueError(f"套装 {equip_2pc} 不存在")

    def _init_main_stats(self, drive4: str | None, drive5: str | None, drive6: str | None):
        """初始化主词条"""
        drive_parts = [drive4, drive5, drive6]
        # 初始化1-3号位
        self.HP_numeric += 2200
        self.ATK_numeric += 316
        self.DEF_numeric += 184
        # 匹配4-6号位
        for drive in drive_parts:
            match drive:
                case "生命值%" | "生命值":
                    self.HP_percent += 0.3
                case "攻击力%" | "攻击力":
                    self.ATK_percent += 0.3
                case "防御力%" | "防御力":
                    self.DEF_percent += 0.48
                case "暴击率%" | "暴击率":
                    if self.crit_balancing:
                        self.baseCRIT_score += 48
                    else:
                        self.CRIT_rate_numeric += 0.24
                case "暴击伤害%" | "暴击伤害":
                    if self.crit_balancing:
                        self.baseCRIT_score += 48
                    else:
                        self.CRIT_damage_numeric += 0.48
                case "异常精通":
                    self.AP_numeric += 92
                case "穿透率%" | "穿透率":
                    self.PEN_ratio += 0.24
                case "冰属性伤害%" | "冰属性伤害":
                    self.ICE_DMG_bonus += 0.3
                case "火属性伤害%" | "火属性伤害":
                    self.FIRE_DMG_bonus += 0.3
                case "电属性伤害%" | "电属性伤害":
                    self.ELECTRIC_DMG_bonus += 0.3
                case "以太属性伤害%" | "以太属性伤害":
                    self.ETHER_DMG_bonus += 0.3
                case "物理属性伤害%" | "物理属性伤害":
                    self.PHY_DMG_bonus += 0.3
                case "异常掌控":
                    self.AM_percent += 0.3
                case "冲击力%" | "冲击力":
                    self.IMP_percent += 0.18
                case "能量自动回复%" | "能量自动回复":
                    self.sp_regen_percent += 0.6
                case None:
                    continue
                case "None" | "-" | "" | "0":
                    continue
                case _:
                    raise ValueError(f"提供的主词条名称 {drive} 不存在")

    def _init_sub_stats(
        self,
        scATK_percent: int | float = 0,
        scATK: int | float = 0,
        scHP_percent: int | float = 0,
        scHP: int | float = 0,
        scDEF_percent: int | float = 0,
        scDEF: int | float = 0,
        scAnomalyProficiency: int | float = 0,
        scPEN: int | float = 0,
        scCRIT: int | float = 0,
        scCRIT_DMG: int | float = 0,
        *,
        DMG_BONUS: int | float = 0,
        PEN_RATIO: int | float = 0,
        ANOMALY_MASTERY: int | float = 0,
        SP_REGEN: int | float = 0,
    ):
        """初始化副词条"""

        self.ATK_percent += scATK_percent * SUB_STATS_MAPPING["scATK_percent"]
        self.ATK_numeric += scATK * SUB_STATS_MAPPING["scATK"]
        self.HP_percent += scHP_percent * SUB_STATS_MAPPING["scHP_percent"]
        self.HP_numeric += scHP * SUB_STATS_MAPPING["scHP"]
        self.DEF_percent += scDEF_percent * SUB_STATS_MAPPING["scDEF_percent"]
        self.DEF_numeric += scDEF * SUB_STATS_MAPPING["scDEF"]
        self.AP_numeric += scAnomalyProficiency * SUB_STATS_MAPPING["scAnomalyProficiency"]
        self.PEN_numeric += scPEN * SUB_STATS_MAPPING["scPEN"]
        if self.crit_balancing:
            self.baseCRIT_score += (
                (scCRIT * SUB_STATS_MAPPING["scCRIT"]) * 2
                + (scCRIT_DMG * SUB_STATS_MAPPING["scCRIT_DMG"])
            ) * 100
        else:
            self.CRIT_rate_numeric += scCRIT * SUB_STATS_MAPPING["scCRIT"]
            self.CRIT_damage_numeric += scCRIT_DMG * SUB_STATS_MAPPING["scCRIT_DMG"]

        # Only for parallel
        element_dmg_mapping = {
            0: self.PHY_DMG_bonus,
            1: self.FIRE_DMG_bonus,
            2: self.ICE_DMG_bonus,
            3: self.ELECTRIC_DMG_bonus,
            4: self.ETHER_DMG_bonus,
            5: self.ICE_DMG_bonus,  # 烈霜也是冰
            6: self.ETHER_DMG_bonus,
        }
        element_dmg_mapping[self.element_type] += DMG_BONUS * SUB_STATS_MAPPING["DMG_BONUS"]

        self.PEN_ratio += PEN_RATIO * SUB_STATS_MAPPING["PEN_RATIO"]
        self.AM_percent += ANOMALY_MASTERY * SUB_STATS_MAPPING["ANOMALY_MASTERY"]
        self.sp_regen_percent += SP_REGEN * SUB_STATS_MAPPING["SP_REGEN"]

    def hardset_sub_stats(
        self,
        scATK_percent: int | float | None = None,
        scATK: int | float | None = None,
        scHP_percent: int | float | None = None,
        scHP: int | float | None = None,
        scDEF_percent: int | float | None = None,
        scDEF: int | float | None = None,
        scAnomalyProficiency: int | float | None = None,
        scPEN: int | float | None = None,
        scCRIT: int | float | None = None,
        scCRIT_DMG: int | float | None = None,
        *,
        DMG_BONUS: int | float | None = None,
        PEN_RATIO: int | float | None = None,
        ANOMALY_MASTERY: int | float | None = None,
        SP_REGEN: int | float | None = None,
    ):
        """硬设置副词条，仅修改传入的参数对应的属性"""

        if scATK_percent is not None:
            self.ATK_percent = scATK_percent * SUB_STATS_MAPPING["scATK_percent"]
        if scATK is not None:
            self.ATK_numeric = scATK * SUB_STATS_MAPPING["scATK"]
        if scHP_percent is not None:
            self.HP_percent = scHP_percent * SUB_STATS_MAPPING["scHP_percent"]
        if scHP is not None:
            self.HP_numeric = scHP * SUB_STATS_MAPPING["scHP"]
        if scDEF_percent is not None:
            self.DEF_percent = scDEF_percent * SUB_STATS_MAPPING["scDEF_percent"]
        if scDEF is not None:
            self.DEF_numeric = scDEF * SUB_STATS_MAPPING["scDEF"]
        if scAnomalyProficiency is not None:
            self.AP_numeric = scAnomalyProficiency * SUB_STATS_MAPPING["scAnomalyProficiency"]
        if scPEN is not None:
            self.PEN_numeric = scPEN * SUB_STATS_MAPPING["scPEN"]
        if self.crit_balancing:
            if scCRIT is not None or scCRIT_DMG is not None:
                current_score = self.baseCRIT_score
                if scCRIT is not None:
                    current_score += scCRIT * SUB_STATS_MAPPING["scCRIT"] * 2 * 100
                if scCRIT_DMG is not None:
                    current_score += scCRIT_DMG * SUB_STATS_MAPPING["scCRIT_DMG"] * 100
                self.baseCRIT_score = current_score
        else:
            if scCRIT is not None:
                self.CRIT_rate_numeric = scCRIT * SUB_STATS_MAPPING["scCRIT"]
            if scCRIT_DMG is not None:
                self.CRIT_damage_numeric = scCRIT_DMG * SUB_STATS_MAPPING["scCRIT_DMG"]

        # Only for parallel
        if DMG_BONUS is not None:
            element_dmg_mapping = {
                0: "PHY_DMG_bonus",
                1: "FIRE_DMG_bonus",
                2: "ICE_DMG_bonus",
                3: "ELECTRIC_DMG_bonus",
                4: "ETHER_DMG_bonus",
                5: "ICE_DMG_bonus",  # 烈霜也是冰
                6: "ETHER_DMG_bonus",  # 玄墨也是以太
            }
            setattr(
                self,
                element_dmg_mapping[self.element_type],
                DMG_BONUS * SUB_STATS_MAPPING["DMG_BONUS"],
            )

        if PEN_RATIO is not None:
            self.PEN_ratio = PEN_RATIO * SUB_STATS_MAPPING["PEN_RATIO"]
        if ANOMALY_MASTERY is not None:
            self.AM_percent = ANOMALY_MASTERY * SUB_STATS_MAPPING["ANOMALY_MASTERY"]
        if SP_REGEN is not None:
            self.sp_regen_percent = SP_REGEN * SUB_STATS_MAPPING["SP_REGEN"]

    def __init_attr_curve_config(self, parallel_config: ExecAttrCurveCfg):
        if not isinstance(parallel_config, ExecAttrCurveCfg):
            return
        ALLOW_SC_LIST: list[str] = list(SUB_STATS_MAPPING.keys())
        sc_name, sc_value = parallel_config.sc_name, parallel_config.sc_value
        if sc_name in ALLOW_SC_LIST:
            adjust_pair = {sc_name: sc_value}
        else:
            raise RuntimeError(f"Parallel Config Segfault: sc_name: {sc_name} do not exist")
        self.hardset_sub_stats(**adjust_pair)

    def update_sp_and_decibel(self, *args, **kwargs):
        """自然更新能量和喧响的方法"""
        # Preload Skill
        skill_nodes: list[SkillNode] = _skill_node_filter(*args, **kwargs)
        for node in skill_nodes:
            # SP
            self.update_single_node_sp(node)
        # SP recovery over time
        self.update_sp_overtime(args, kwargs)

    def update_sp_overtime(self, args, kwargs):
        """处理当前tick的自然回能"""
        sp_regen_data: list[SPUpdateData] = _sp_update_data_filter(*args, **kwargs)
        for mul in sp_regen_data:
            if mul.char_name == self.NAME:
                sp_change_2 = mul.get_sp_regen() / 60  # 每秒回能转化为每帧回能
                self.update_sp(sp_change_2)

    def update_single_node_sp(self, node):
        """处理单个skill_node的回能"""
        if node.char_name == self.NAME:
            sp_consume = node.skill.sp_consume
            sp_threshold = node.skill.sp_threshold
            sp_recovery = node.skill.sp_recovery
            if self.sp < sp_threshold:
                print(
                    f"{node.skill_tag}需要{sp_threshold:.2f}点能量，目前{self.NAME}仅有{self.sp:.2f}点，需求无法满足，请检查技能树"
                )
            sp_change = sp_recovery - sp_consume
            self.update_sp(sp_change)
        # Decibel
        self.process_single_node_decibel(node)

    def process_single_node_decibel(self, node):
        allowed_list = ["1371_Q_A"]
        if (
            self.NAME == node.char_name
            and node.skill_tag.split("_")[1] == "Q"
            and node.skill_tag not in allowed_list
        ):
            if self.decibel - 3000 <= -1e-5:
                print(
                    f"{self.NAME} 释放大招时喧响值不足3000，目前为{self.decibel:.2f}点，请检查技能树"
                )
            self.decibel = 0
        else:
            # 计算喧响变化值
            decibel_change = node.skill.self_fever_re
            # 如果喧响变化值大于0，则更新喧响值
            if decibel_change > 0:
                # 如果不是自身技能，倍率折半
                if node.char_name != self.NAME:
                    decibel_change *= 0.5
                # 更新喧响值
                self.update_decibel(decibel_change)

    def update_sp(self, sp_value: int | float):
        """可全局强制更新能量的方法"""
        self.sp += sp_value
        self.sp = max(0.0, min(self.sp, self.sp_limit))

    def update_decibel(self, decibel_value: int | float):
        """可外部强制更新喧响的方法"""
        # if self.decibel == 3000 and self.NAME == '仪玄':
        #     print(f"{self.NAME} 释放技能时喧响值已满3000点！")
        from zsim.sim_progress.ScheduledEvent.Calculator import cal_buff_total_bonus

        # [Refactor] 使用 BuffManager 获取当前激活的 Buff
        # dynamic_buff = self.sim_instance.global_stats.DYNAMIC_BUFF_DICT # OLD

        enabled_buff = []
        if hasattr(self, "buff_manager"):
            enabled_buff = tuple(self.buff_manager._active_buffs.values())

        # 注意：cal_buff_total_bonus 可能还需要 Enemy 的 Buff (视具体实现而定)。
        # 如果喧响获取效率只看自身的 Buff，则传 self 的即可。
        # 如果 Calculator.cal_buff_total_bonus 内部逻辑需要合并 Enemy Buff，
        # 则这里需要调整调用方式。根据 Calculator.py 的重构，它接受 enabled_buff 元组。
        # 假设这里只关心角色自身的 Buff 对 "喧响获得效率" 的加成。

        buff_bonus_dict = cal_buff_total_bonus(
            enabled_buff=enabled_buff,
            judge_obj=None,
            sim_instance=self.sim_instance,
            char_name=self.NAME,
        )
        decibel_get_ratio = buff_bonus_dict.get("喧响获得效率", 0)
        final_decibel_change_value = decibel_value * (1 + decibel_get_ratio)
        self.decibel += final_decibel_change_value
        # print(final_decibel_change_value, decibel_value, decibel_get_ratio)
        self.decibel = max(0.0, min(self.decibel, 3000))

    def special_resources(self, *args, **kwargs) -> None:
        """父类中不包含默认特殊资源"""
        return None

    def get_resources(self) -> tuple[str | None, int | float | bool | None]:
        """获取特殊资源的属性名称与数量"""
        return None, None

    def get_special_stats(self, *args, **kwargs) -> dict[str | None, object | None]:
        """获取全部特殊属性的名称与数值"""
        result: dict[str | None, object | None] = {}
        return result

    def __str__(self) -> str:
        return f"{self.NAME} {self.level}级，能量{self.sp:.2f}，喧响{self.decibel:.2f}"

    def reset_myself(self):
        # 重置能量、喧响值
        self.sp: float = 40.0
        self.decibel: float = 1000.0
        # 重置动态属性
        self.dynamic.reset()

    def refresh_myself(self):
        """部分角色身上存在每个tick更新一次的数据结构，所以这里提供一个统一的对外调用接口。
        目前这个接口是被Schedule阶段调用的。"""
        return None

    def __deepcopy__(self, memo):
        return self

    def personal_action_replace_strategy(self, action: str):
        return action

    def POST_INIT_DATA(self, sim_instance: "Simulator"):
        self.sim_instance = sim_instance
        # 初始化 BuffManager
        from zsim.sim_progress.Buff.BuffManager.BuffManagerClass import BuffManager

        self.buff_manager = BuffManager(self.NAME, sim_instance)


class LastingNode:
    def __init__(self, char_instance: Character):
        """用于记录和管理角色持续释放技能的状态节点

        该类负责追踪角色的技能释放状态，包括连续释放同一技能的情况和技能被打断的处理。

        属性:
            char_instance (Character): 关联的角色实例
            node (SkillNode): 当前正在执行的技能节点，初始为None
            start_tick (int): 开始释放技能的时间点
            update_tick (int): 最近一次更新状态的时间点
            is_spamming (bool): 是否处于连续释放同一技能的状态
            repeat_times (int): 连续释放同一技能的次数
        """
        self.char_instance = char_instance
        self.node = None
        self.start_tick = 0
        self.update_tick = 0
        self.is_spamming = False  # 是否处于连续释放技能的状态
        self.repeat_times = 0

    def reset(self):
        """重置所有状态参数到初始值

        在需要清除当前技能状态时调用，比如切换角色或战斗结束时
        """
        self.node = None
        self.start_tick = 0
        self.update_tick = 0
        self.is_spamming = False
        self.repeat_times = 0

    def update_node(self, node, tick: int):
        """更新技能节点状态

        处理技能节点的更新逻辑，包括：
        1. 处理与其他角色节点的交互
        2. 处理技能被打断的情况
        3. 处理连续释放同一技能的状态更新
        4. 处理技能切换的逻辑

        参数:
            node (SkillNode): 新的技能节点
            tick (int): 当前时间点

        异常:
            ValueError: 当尝试过早更新节点时抛出
        """
        # 若传入动作不是自己的技能
        # from zsim.sim_progress.Preload import SkillNode
        # assert isinstance(node, SkillNode)
        if node.is_additional_damage and node.skill.ticks == 0:
            # 若传入的动作是0帧的附加伤害，由于这些技能很明显是不需要角色通过某些动画动作来释放的，
            # 所以这里就不更新lasting_node，以保证不会因为0帧技能而导致lasting_node的数据被污染。
            return

        if node.char_name != self.char_instance.NAME:
            if self.node is None:
                # 若此时自己没有技能，则直接返回
                return
            if self.is_spamming and self.node.end_tick <= tick:
                # 若此时自己正在持续释放某技能但是该技能已经结束，则结束技能释放状态、清空技能节点，重置参数；
                self.is_spamming = False
                self.node = None
                self.update_tick = tick
                self.repeat_times = 0
                return
        else:
            # 若传入动作是自己的技能
            if self.node is None:
                # 若此时自己没有登记中的技能，那么就登记当前技能，并且更新参数
                self.node = node
                self.start_tick = tick
                self.update_tick = tick
                self.repeat_times = 1
                return

            # 若此时自己有正在进行中的技能
            if node.skill_tag in ["被打断", "发呆"]:
                # 若此时技能是“被打断”或是“发呆”，则进行参数更新，并且关闭spamming参数；
                self.is_spamming = False
                self.node = node
                self.start_tick = tick
                self.update_tick = tick
                self.repeat_times = 0
                return
            else:
                # 若此时传入技能是其他正常技能，则需要进行判断
                if self.node.end_tick > tick and node.active_generation:
                    # 若已经登记的技能尚未结束，且新传入技能是主动释放，那需要进行验错——理论上，APL不会在角色当前尚还有动作时放行一个新技能。
                    if not self.node.skill.do_immediately and node.skill.do_immediately:
                        # 若已登记技能并非高优先级，而传入技能为高优先级，则说明是发生了技能顶替（比如大招顶替自己的平A），这是一个正常情况，所以不进入报错分支；
                        pass
                    else:
                        if "dodge" in self.node.skill_tag:
                            # 若已经登记技能为闪避，那么此时无论传入什么技能，都不进入报错分支——因为闪避是可以被任意取消的
                            pass
                        else:
                            # 其他的情况则说明APL模块确实出现了错误，报错。
                            raise ValueError(
                                f"过早传入了node{node.skill_tag}，当前node{self.node.skill_tag}为{self.node.preload_tick}开始 {self.node.end_tick}结束,\n"
                                f"但是{node.skill_tag}的企图在{tick}tick进行更新，它预计从{node.preload_tick}开始 {node.end_tick}结束！"
                            )
                # 在验错环节结束后，正式进行技能信息的更新、替换；
                if self.node.skill_tag == node.skill_tag:
                    # 若传入技能和已登记技能一致，则直接更新参数
                    self.is_spamming = True
                    self.repeat_times += 1
                else:
                    # 若传入技能和已登记技能不一致，则关闭spamming参数，并更新技能信息
                    self.is_spamming = False
                    self.start_tick = tick
                    self.repeat_times = 1
                # 无论如何，node以及update_tick参数都会更新
                self.node = node
                self.update_tick = tick

    def spamming_info(self, tick: int):
        """获取当前技能持续释放的状态信息

        参数:
            tick (int): 当前时间点

        返回:
            tuple: (是否连续释放中, 技能标签, 持续时间, 重复次数)
        """
        lasting_tick = tick - self.start_tick
        if self.node is None:
            skill_tag = None
        else:
            skill_tag = self.node.skill_tag
        return self.is_spamming, skill_tag, lasting_tick, self.repeat_times


if __name__ == "__main__":
    pass
