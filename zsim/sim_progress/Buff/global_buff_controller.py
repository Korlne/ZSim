import json
import os
from typing import Dict, Optional, List, Any

# 引入核心数据模型
from zsim.sim_progress.Buff.buff_model import BuffFeature, Buff
from zsim.sim_progress.Buff.effects.base_effect import EffectBase
from zsim.sim_progress.Buff.effects.bonus_effect import BonusEffect
from zsim.sim_progress.Buff.effects.trigger_effect import TriggerEffect
from zsim.sim_progress.Buff.effects.conditions import ConditionFactory, PeriodicTimer
from zsim.sim_progress.Buff.effects.actions import ActionFactory, DealDotDamageAction
from zsim.sim_progress.Buff.effects.dot_effect import DotEffect

class GlobalBuffController:
    """
    全局 Buff 控制器 (单例)
    负责加载 Buff 配置数据，并充当 Buff 创建的工厂。
    """
    _instance: Optional["GlobalBuffController"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalBuffController, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        # 注册表：存储所有 Buff 的静态配置 (BuffFeature) 和 关联效果 (List[Effect])
        # Key: buff_id (str)
        self._feature_registry: Dict[str, BuffFeature] = {}
        self._effect_registry: Dict[str, List[EffectBase]] = {}
        
        self.load_buff_data()
        self._initialized = True

    def load_buff_data(self, file_path: str = None) -> None:
        """
        从 JSON 文件加载 Buff 配置数据
        """
        if file_path is None:
            # 自动定位默认路径: zsim/data/generated/buff_db.json
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 回退到 zsim 根目录 (sim_progress/Buff/GlobalBuffControllerClass -> ... -> zsim)
            # 路径层级: zsim/sim_progress/Buff/GlobalBuffControllerClass
            # 需要回退 3 层到 zsim 根目录同级，或者 2 层到 zsim 包内部
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            file_path = os.path.join(project_root, "data", "generated", "buff_db.json")

        if not os.path.exists(file_path):
            print(f"[GlobalBuffController] ❌ 警告: 找不到 Buff 数据文件: {file_path}")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data_map = json.load(f)
            
            count = 0
            for buff_id, entry in data_map.items():
                self._parse_and_register_entry(buff_id, entry)
                count += 1
            
            print(f"[GlobalBuffController] ✅ 成功加载 {count} 个 Buff 配置")
            
        except Exception as e:
            print(f"[GlobalBuffController] ❌ 加载 Buff 数据失败: {e}")
            import traceback
            traceback.print_exc()

    def _parse_and_register_entry(self, buff_id: str, entry: Dict[str, Any]):
        """
        解析单个 Buff 条目并注册
        """
        # 1. 解析 Feature (静态属性)
        feat_data = entry.get("feature", {})
        # 确保 buff_id 一致
        feat_data["buff_id"] = buff_id 
        
        feature = BuffFeature(
            buff_id=str(feat_data.get("buff_id")),
            name=feat_data.get("name", "Unknown Buff"),
            max_stacks=feat_data.get("max_stacks", 1),
            max_duration=feat_data.get("max_duration", -1.0),
            stack_increment=feat_data.get("stack_increment", 1),
            independent_stacks=feat_data.get("independent_stacks", False),
            allows_refresh=feat_data.get("allows_refresh", True),
            tags=set(feat_data.get("tags", []))
        )
        self._feature_registry[buff_id] = feature

        # 2. 解析 Effects (效果列表)
        effects_list = []
        raw_effects = entry.get("effects", [])
        
        for eff_data in raw_effects:
            eff_type = eff_data.get("type")
            
            try:
                if eff_type == "bonus":
                    effect = BonusEffect(
                        target_key=eff_data["target_key"],
                        value=eff_data["value"],
                        conditions=eff_data.get("conditions") # 可选条件
                    )
                    effects_list.append(effect)
                    
                elif eff_type == "trigger":
                    # 1. 创建条件对象列表
                    raw_conditions = eff_data.get("conditions", {})
                    condition_objs = ConditionFactory.create_conditions(raw_conditions)
                    
                    # 2. 创建行为对象列表
                    raw_actions = eff_data.get("actions", [])
                    action_objs = ActionFactory.create_actions(raw_actions)

                    effect = TriggerEffect(
                        trigger_event_type=eff_data.get("trigger_event"),
                        conditions=condition_objs, # 传入对象列表
                        actions=action_objs,       # 传入对象列表
                        source_buff_id=buff_id
                    )
                    effects_list.append(effect)
                
                elif eff_type == "dot":
                    # Dot 解析逻辑
                    # 获取配置，默认值为 1.0 (秒)
                    interval = eff_data.get("interval", 1.0) 
                    dmg_rate = eff_data.get("damage_rate", 1.0)
                    element = eff_data.get("element", "Physical")
                    
                    # 构建周期性条件 (PeriodicTimer 接收秒)
                    condition_objs = [PeriodicTimer(interval=float(interval))]
                    
                    # 构建伤害行为
                    action_objs = [
                        DealDotDamageAction(
                            dot_type=element,      
                            damage_multiplier=float(dmg_rate), 
                            source_buff_id=str(buff_id) # 注入当前 Buff ID 用于校验 Tick
                        )
                    ]
                    
                    # 包装为 DotEffect 
                    
                    effect = DotEffect(
                        trigger_event_type="PERIODIC_BUFF_TICK",
                        conditions=condition_objs,
                        actions=action_objs,
                        source_buff_id=int(buff_id),
                        dot_type=element,
                        tick_interval=float(interval),
                        damage_multiplier=float(dmg_rate)
                    )
                    effects_list.append(effect)

                else:
                    # 未知类型或特殊逻辑占位符，暂时忽略或记录
                    pass
                    
            except KeyError as e:
                print(f"[GlobalBuffController] ⚠️ 解析 Buff {buff_id} 的效果时缺少字段: {e}")

        self._effect_registry[buff_id] = effects_list

    def create_buff(self, buff_id: str) -> Optional[Buff]:
        """
        工厂方法：创建一个新的 Buff 运行时实例
        """
        feature = self._feature_registry.get(str(buff_id))
        if not feature:
            print(f"[GlobalBuffController] ❌ 尝试创建不存在的 Buff ID: {buff_id}")
            return None
            
        # 获取关联的效果模板
        effects = self._effect_registry.get(str(buff_id), [])
        
        # 创建全新的动态实例
        # 注意：这里我们传入的是 Effect 对象的引用。
        # 由于 Effect 通常是无状态的（逻辑容器），多个 Buff 实例共享同一个 Effect 对象是安全的。
        return Buff(feature=feature, effects=effects)

    def get_buff_feature(self, buff_id: str) -> Optional[BuffFeature]:
        return self._feature_registry.get(str(buff_id))

# 全局单例访问点
g_buff_controller = GlobalBuffController()