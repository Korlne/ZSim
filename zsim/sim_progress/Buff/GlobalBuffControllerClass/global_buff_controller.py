from collections import defaultdict
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from zsim.define import EFFECT_FILE_PATH, EXIST_FILE_PATH
from zsim.sim_progress.Buff.buff_class import Buff
from zsim.sim_progress.Buff.Effect.definitions import BonusEffect, EffectBase
from zsim.sim_progress.Report import report_to_log


class GlobalBuffController:
    """
    全局 Buff 控制器 (Singleton)。

    职责：
    1. 维护 Buff 数据库的缓存 (Trigger Config & Effect Config)。
    2. 作为工厂 (Factory)，提供 Buff 实例的创建方法。
    3. 解析 Buff 效果数据，将 CSV/JSON 转换为 Effect 对象。
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        接收 *args, **kwargs 是为了兼容 GlobalBuffController(sim_instance=...) 这种调用方式。
        如果不接收参数，Python 会抛出 TypeError。
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, sim_instance=None):
        """
        接收 sim_instance 参数。
        """
        # 单例模式：防止重复初始化
        # 使用 hasattr 判断属性是否存在，比判断 True/False 更安全
        if hasattr(self, "_initialized") and self._initialized:
            # 如果需要更新 sim_instance，可以在这里处理，但通常控制器只负责数据
            if sim_instance:
                self.sim_instance = sim_instance
            return

        # --- 下面是只执行一次的初始化代码 ---

        self.sim_instance = sim_instance
        self._trigger_db: pd.DataFrame = pd.DataFrame()
        self._effect_db: Dict[str, Dict[str, float]] = {}

        # 使用 defaultdict(dict) 可以在访问新角色名时自动创建空字典，防止 KeyError
        # 结构: { "CharacterName": { "BuffName": BuffInstance }, ... }
        self.exist_buff_dict: Dict[str, Dict[str, Any]] = defaultdict(dict)

        # 加载数据
        self._load_databases()

        # 标记为已初始化
        self._initialized = True

    def _load_databases(self):
        """加载所有必要的 CSV 数据库"""
        try:
            # 1. 加载触发判断 (Buff 基础配置)
            # 确保文件路径存在，建议加上错误捕获或路径检查
            self._trigger_db = pd.read_csv(EXIST_FILE_PATH)
            # 建立索引以加速查找
            self._trigger_db.set_index("BuffName", inplace=False, drop=False)

            # 2. 加载效果表 (Buff 数值效果)
            # 复用并优化原 buff_class.py 中的解析逻辑
            self._effect_db = self._parse_effect_csv(EFFECT_FILE_PATH)

            report_to_log(
                f"[GlobalBuffController] 初始化完成，加载了 {len(self._trigger_db)} 个Buff定义。",
                level=1,
            )

        except Exception as e:
            report_to_log(f"[GlobalBuffController] 数据库加载失败: {e}", level=4)
            raise e

    def _parse_effect_csv(self, csv_path: str) -> Dict[str, Dict[str, float]]:
        """
        解析 buff_effect.csv。
        格式: Name, key1, value1, key2, value2 ...
        返回: { "BuffName": { "攻击力": 100, "增伤": 0.5 }, ... }
        """
        try:
            df = pd.read_csv(csv_path)
        except FileNotFoundError:
            report_to_log(f"[GlobalBuffController] 警告: 未找到效果文件 {csv_path}", level=3)
            return {}

        result = {}
        # 计算有多少对 key-value (列数 - Name列) / 2
        width = int(np.ceil((df.shape[1] - 1) / 2))

        for _, row in df.iterrows():
            name = row.get("名称")  # 使用 .get 防止列名不存在报错
            if pd.isna(name):
                continue

            effects = {}
            for i in range(1, width + 1):
                try:
                    key = row.get(f"key{i}")
                    val = row.get(f"value{i}")

                    if pd.notna(key) and pd.notna(val):
                        # 尝试转换为 float，如果不是数值（比如特殊标志）则保持原样或忽略
                        try:
                            effects[str(key)] = float(val)
                        except ValueError:
                            # 暂时只支持数值型效果，非数值型可能需要 TriggerEffect 处理
                            continue
                except KeyError:
                    continue

            if effects:
                result[name] = effects

        return result

    def instantiate_buff(self, buff_id: str, sim_instance=None) -> Buff:
        """
        [Factory Method] 根据 ID 创建一个新的 Buff 实例。

        Args:
            buff_id: Buff 的唯一标识符 (BuffName)。
            sim_instance: 模拟器实例引用。如果调用时未传入，尝试使用初始化时保存的。

        Returns:
            初始化完成并填充了 Effects 的 Buff 对象。
        """
        # 优先使用传入的 sim_instance，其次使用 self.sim_instance
        sim = sim_instance if sim_instance is not None else self.sim_instance

        # 1. 获取配置数据
        # 使用 loc 查找比 mask 更快，且可以直接处理 key 不存在的情况
        if buff_id not in self._trigger_db.index:
            raise ValueError(f"Buff ID '{buff_id}' not found in database.")

        # 因为我们 set_index 了 BuffName，可以直接用 loc
        config_series = self._trigger_db.loc[buff_id]

        # 如果有重复的 BuffName，loc 会返回 DataFrame 而不是 Series，需要处理
        if isinstance(config_series, pd.DataFrame):
            config_series = config_series.iloc[0]

        # 2. 创建实例 (Phase 1 的 Buff 类)
        # 注意：这里使用了全关键字参数，防止参数顺序冲突
        buff = Buff(
            config=config_series,  # 假设你的 Buff 类接收 config 参数
            sim_instance=sim,
        )

        # 3. 注入 Effects (这是 Phase 2 的核心补充)
        buff.effects = self._create_effects_for_buff(buff_id)

        return buff

    def _create_effects_for_buff(self, buff_id: str) -> List[EffectBase]:
        """为指定 Buff 构建效果列表"""
        effects: List[EffectBase] = []

        # 1. 处理数值加成效果 (BonusEffect)
        raw_effects = self._effect_db.get(buff_id, {})
        for attr_name, value in raw_effects.items():
            # 简单的映射逻辑：根据属性名判断是加算还是乘算
            # 这部分规则未来可以提取到配置文件中
            calc_mode = (
                "final_mul" if "独立" in attr_name else ("mul" if "乘区" in attr_name else "add")
            )

            # 使用 kw_only=True 后的调用方式，显式指定参数名
            effect = BonusEffect(
                source_buff_id=buff_id, target_attribute=attr_name, value=value, calc_mode=calc_mode
            )
            effects.append(effect)

        # 2. 处理触发器效果 (TriggerEffect)
        # TODO: 从触发判断.csv 的某些字段解析 TriggerEffect
        # 例如: 如果 simple_hit_logic 为 True，可能意味着需要注册 Hit 事件

        return effects

    # 提供给外部的快捷访问
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls()
        return cls._instance
