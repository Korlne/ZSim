# zsim/sim_progress/Buff/effects/dot_effect.py
from typing import Dict, Any, Optional
from zsim.sim_progress.Buff.effects.base_effect import EffectBase
# 引入旧的/现有的 Dot 工厂或基类
# from zsim.sim_progress.Dot.BaseDot import BaseDot 

class DotEffect(EffectBase):
    """
    DoT (Damage over Time) 效果适配器
    负责在 Buff 激活/生效时，调用具体的 DoT 逻辑类。
    """
    def __init__(self, dot_type: str, params: Dict[str, Any]):
        self.dot_type = dot_type  # 例如 "Shock", "Burn"
        self.params = params      # 例如倍率、间隔等
        self._dot_instance = None # 运行时存储具体的 DoT 对象实例

    def on_attach(self, owner, buff_instance):
        """当 Buff 被添加到角色身上时触发"""
        # 这里是连接点：实例化真正的 DoT 逻辑类
        # 假设您有一个 DotFactory 或者直接根据 type 实例化
        from zsim.sim_progress.Dot import get_dot_class_by_type # 假设有这个工厂方法
        
        DotClass = get_dot_class_by_type(self.dot_type)
        if DotClass:
            # 将 Buff 的持续时间、层数等信息传递给 DoT 对象
            self._dot_instance = DotClass(owner, **self.params)
            self._dot_instance.activate() # 调用旧逻辑的激活
            print(f"[DotEffect] 激活了 {self.dot_type} 异常状态")

    def on_detach(self, owner, buff_instance):
        """当 Buff 结束时触发"""
        if self._dot_instance:
            self._dot_instance.deactivate() # 调用旧逻辑的移除
            self._dot_instance = None

    def on_tick(self, owner, buff_instance, context):
        """如果 Buff 系统有统一的心跳机制，可以在这里驱动 DoT"""
        if self._dot_instance:
            self._dot_instance.on_tick(context)