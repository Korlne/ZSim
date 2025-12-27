from typing import TYPE_CHECKING, Iterable

from zsim.sim_progress.Buff.Effect.definitions import TriggerEffect
from zsim.sim_progress.Buff.Event.callbacks import BuffCallbackRepository

# 引入现有的事件系统基类 (根据你提供的文件内容)
from zsim.sim_progress.zsim_event_system.Handler.base_handler_class import ZSimEventHandler
from zsim.sim_progress.zsim_event_system.zsim_events import (
    BaseZSimEventContext,
    EventMessage,
    ZSimEventABC,
)

if TYPE_CHECKING:
    from zsim.sim_progress.Buff.buff_class import Buff


class BuffTriggerHandler(ZSimEventHandler):
    """
    通用 Buff 事件处理器。

    职责：
    1. 监听特定的事件类型 (defined in TriggerEffect)。
    2. 检查过滤条件 (如 skill_tags, cooldown)。
    3. 如果满足，调用 Repository 中的回调函数。
    """

    def __init__(self, owner_id: str, buff: "Buff", effect: TriggerEffect):
        self.owner_id = owner_id
        self.buff = buff
        self.effect = effect
        self.callback_func = BuffCallbackRepository.get_callback(effect.callback_logic_id)

    def supports(self, event: ZSimEventABC) -> bool:
        """
        检查事件是否应该触发此 Buff 效果。
        """
        # 1. Buff 必须是激活状态 (或者某些特殊的被动Buff一直生效)
        if not self.buff.dy.active:
            # 某些Buff可能是“后台生效”的，这里需要根据 ft.passively_updating 细化
            # 暂时假设只有 Active 的 Buff 响应事件
            return False

        # 2. 事件类型匹配 (字符串匹配，或枚举匹配)
        # 注意：这里假设 event_type 是字符串或枚举，需与 TriggerEffect 中的定义一致
        if str(event.event_type) != self.effect.trigger_event_type:
            return False

        # 3. 检查来源/目标限制 (非常重要)
        # 大多数 Buff 只响应持有者的行为
        if hasattr(event, "source_id") and event.source_id != self.owner_id:
            return False

        # 4. 检查技能标签 (Skill Tags)
        if self.effect.skill_tags:
            # 假设 event 有 tags 属性 (如 SkillEvent)
            if not hasattr(event, "tags"):
                return False
            # 集合求交集，只要有一个 tag 匹配即可 (或视需求改为全匹配)
            event_tags = set(event.tags)
            required_tags = set(self.effect.skill_tags)
            if not event_tags.intersection(required_tags):
                return False

        # 5. 检查冷却时间 (CD)
        current_tick = getattr(event, "timestamp", 0)
        if self.effect.cooldown > 0:
            if current_tick < self.buff.dy.last_trigger_tick + self.effect.cooldown:
                return False

        return True

    def handle(
        self, event: ZSimEventABC, context: BaseZSimEventContext
    ) -> Iterable[ZSimEventABC[EventMessage]]:
        """
        执行触发逻辑。
        """
        if not self.callback_func:
            return []

        # 执行回调
        result = self.callback_func(self.buff, event, context)

        # 更新冷却时间
        if hasattr(event, "timestamp"):
            self.buff.dy.last_trigger_tick = event.timestamp

        # 如果回调产生了新的事件 (例如触发了额外的攻击事件)，yield 出去
        if result and isinstance(result, Iterable):
            yield from result
        elif result:
            yield result

        return []
