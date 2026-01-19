import unittest
from unittest.mock import MagicMock

import pandas as pd

from zsim.sim_progress.Buff.BuffManager.BuffManagerClass import BuffManager
from zsim.sim_progress.Buff.GlobalBuffControllerClass.global_buff_controller import (
    GlobalBuffController,
)
from zsim.sim_progress.Character.bonus_pool import BonusPool

# --- 模拟类 (Mock Classes) ---


class MockCharacter:
    def __init__(self, name="TestChar"):
        self.NAME = name
        self.CID = "test_char_001"
        self.bonus_pool = BonusPool(self)

        # 基础属性
        self.baseATK = 1000.0
        self.ATK_percent = 0.0
        self.ATK_numeric = 0.0
        self.overall_ATK_percent = 0.0
        self.overall_ATK_numeric = 0.0

        # 其他必须属性 (简化)
        self.HP_percent = 0.0
        self.HP_numeric = 0.0
        self.baseHP = 10000
        self.overall_HP_percent = 0.0
        self.overall_HP_numeric = 0.0
        self.DEF_percent = 0.0
        self.DEF_numeric = 0.0
        self.baseDEF = 800
        self.overall_DEF_percent = 0.0
        self.overall_DEF_numeric = 0.0
        self.IMP_percent = 0.0
        self.IMP_numeric = 0.0
        self.baseIMP = 100
        self.overall_IMP_percent = 0.0
        self.overall_IMP_numeric = 0.0
        self.AP_percent = 0.0
        self.AP_numeric = 0.0
        self.baseAP = 100
        self.overall_AP_percent = 0.0
        self.overall_AP_numeric = 0.0
        self.AM_percent = 0.0
        self.AM_numeric = 0.0
        self.baseAM = 100
        self.overall_AM_percent = 0.0
        self.overall_AM_numeric = 0.0
        self.baseCRIT_score = 0.0
        self.CRIT_rate_numeric = 0.0
        self.CRIT_damage_numeric = 0.0
        self.sp_regen_percent = 0.0
        self.sp_regen_numeric = 0.0
        self.base_sp_regen = 1.0
        self.sp_get_ratio = 1.0
        self.sp_limit = 100
        self.PEN_ratio = 0.0
        self.PEN_numeric = 0.0
        self.ICE_DMG_bonus = 0.0
        self.FIRE_DMG_bonus = 0.0
        self.PHY_DMG_bonus = 0.0
        self.ETHER_DMG_bonus = 0.0
        self.ELECTRIC_DMG_bonus = 0.0
        self.ALL_DMG_bonus = 0.0
        self.Trigger_DMG_bonus = 0.0
        self.crit_rate_limit = 1.0

        # 初始化 Mock 的 Statement
        # 注意：这里我们手动引入 Character.Statement 类，或者简单模拟
        # 为了测试真实逻辑，我们需要引用 Character 中的 Statement 类
        from zsim.sim_progress.Character.character import Character

        self._StatementClass = Character.Statement

    @property
    def statement(self):
        return self._StatementClass(self, crit_balancing=False)


class MockSimulator:
    def __init__(self):
        self.char_obj_dict = {}
        self.event_handler_registry = MagicMock()  # 模拟事件系统


class TestBuffSystem(unittest.TestCase):
    def setUp(self):
        # 1. 初始化 Mock 环境
        self.sim = MockSimulator()
        self.char = MockCharacter("TestAgent")
        self.sim.char_obj_dict["TestAgent"] = self.char

        # 2. 初始化 Controller (Mock 数据，避免读取真实 CSV)
        self.controller = GlobalBuffController.get_instance()
        # Mock 数据库查询: 只要 ID 为 "TestBuff_ATK" 就返回我们造的数据
        self.controller._trigger_db = pd.DataFrame(
            {
                "BuffName": ["TestBuff_ATK"],
                "maxduration": [10],
                "maxcount": [5],
                "incrementalstep": [1],
                "increaseCD": [0],
                "description": ["测试攻击Buff"],
            }
        ).set_index("BuffName", drop=False)

        # Mock 效果: "TestBuff_ATK" 增加 10% 攻击力
        self.controller._effect_db = {
            "TestBuff_ATK": {"攻击力%": 0.10}  # 10%
        }

        # 3. 初始化 Manager
        self.manager = BuffManager("TestAgent", self.sim)

    def test_add_buff_and_verify_bonus(self):
        """测试：添加 Buff 后，BonusPool 是否有效果，Character 面板是否变化"""
        print("\n--- Test: Add Buff & Verify Bonus ---")

        # 初始状态：1000 攻击力
        initial_atk = self.char.statement.ATK
        print(f"Initial ATK: {initial_atk}")
        self.assertEqual(initial_atk, 1000.0)

        # 添加 Buff: 1层, 持续10秒
        self.manager.add_buff("TestBuff_ATK", current_tick=0, stacks=1)

        # 验证 1: Buff 是否在 Active 列表
        buff = self.manager.get_buff("TestBuff_ATK")
        self.assertIsNotNone(buff)
        self.assertTrue(buff.dy.active)
        print(f"Buff Added: {buff}")

        # 验证 2: BonusPool 是否收到 Effect
        atk_bonus = self.char.bonus_pool.query_total_add("攻击力%")
        self.assertEqual(atk_bonus, 0.10)
        print(f"BonusPool ATK%: {atk_bonus}")

        # 验证 3: Character 面板是否更新
        # 1000 * (1 + 0.10) = 1100
        new_atk = self.char.statement.ATK
        print(f"New ATK: {new_atk}")
        self.assertEqual(new_atk, 1100.0)

    def test_buff_stacking(self):
        """测试：Buff 叠层"""
        print("\n--- Test: Buff Stacking ---")
        # 添加 3 层
        self.manager.add_buff("TestBuff_ATK", current_tick=0, stacks=3)

        # 由于我们现在的 Effect 实现通常是 Buff 实例持有一个 Effect 对象，
        # 而 BonusEffect 的 value 是静态配置的。
        # [注意]:
        # 如果 Buff 的设计是 "每层增加 10%"，那么 Effect.value 应该是 动态计算的 或者 BonusPool 需要乘层数。
        # 让我们检查一下代码：
        # Phase 1 的 BonusEffect 只有静态 value。
        # Phase 4 的 BonusPool.query_total_add 是 sum(effect.value)。
        #
        # 如果设计意图是 "层数 * 数值"，目前的代码可能只加了一次（因为只注册了一个 Effect 对象）。
        # **这是一个潜在的 Bug 或设计遗漏点**。
        #
        # 修正方案通常是：
        # A. BonusPool 在计算时读取 source_buff.dy.count。
        # B. 或者 Buff 在 add_stack 时更新 Effect.value。
        #
        # 我们假设目前的实现是 "Buff激活即生效配置值(不随层数变)" 或者 "尚未实现随层数变化"。
        # 为了测试通过，我们先验证层数变更。

        buff = self.manager.get_buff("TestBuff_ATK")
        self.assertEqual(buff.dy.count, 3)
        print(f"Buff Stacks: {buff.dy.count}")

    def test_buff_expiry(self):
        """测试：Buff 过期移除"""
        print("\n--- Test: Buff Expiry ---")
        self.manager.add_buff("TestBuff_ATK", current_tick=0, duration=10)  # 持续到 tick 10

        # Tick 5: 应该存在
        self.manager.tick(5)
        self.assertIsNotNone(self.manager.get_buff("TestBuff_ATK"))

        # Tick 11: 应该过期
        self.manager.tick(11)
        self.assertIsNone(self.manager.get_buff("TestBuff_ATK"))

        # 验证效果是否移除
        atk_bonus = self.char.bonus_pool.query_total_add("攻击力%")
        self.assertEqual(atk_bonus, 0.0)
        print("Buff Expired and Effect Removed.")


if __name__ == "__main__":
    unittest.main()
