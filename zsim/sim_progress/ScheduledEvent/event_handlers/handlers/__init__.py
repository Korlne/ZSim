"""事件处理器模块

该模块包含所有具体的事件处理器实现和工厂类。
"""

from .abloom import AbloomEventHandler
from .anomaly import AnomalyEventHandler
from .disorder import DisorderEventHandler
from ..base import EventHandlerABC
from .factory import EventHandlerFactory, event_handler_factory
from .polarity_disorder import PolarityDisorderEventHandler
from .polarized_assault import PolarizedAssaultEventHandler
from .preload import PreloadEventHandler
from .quick_assist import QuickAssistEventHandler
from .refresh import RefreshEventHandler
from .skill import SkillEventHandler
from .stun_forced_termination import StunForcedTerminationEventHandler


def _create_default_handlers() -> list[EventHandlerABC]:
    return [
        SkillEventHandler(),
        AnomalyEventHandler(),
        DisorderEventHandler(),
        PolarityDisorderEventHandler(),
        AbloomEventHandler(),
        RefreshEventHandler(),
        QuickAssistEventHandler(),
        PreloadEventHandler(),
        StunForcedTerminationEventHandler(),
        PolarizedAssaultEventHandler(),
    ]


def register_all_handlers(factory: EventHandlerFactory | None = None) -> EventHandlerFactory:
    """Register the canonical ScheduledEvent handler set on a target factory."""
    target_factory = event_handler_factory if factory is None else factory
    target_factory.replace_handlers(_create_default_handlers())
    return target_factory


def create_default_event_handler_factory() -> EventHandlerFactory:
    """Create an isolated factory with the canonical ScheduledEvent handlers."""
    return register_all_handlers(EventHandlerFactory())


__all__ = [
    "SkillEventHandler",
    "AnomalyEventHandler",
    "DisorderEventHandler",
    "PolarityDisorderEventHandler",
    "AbloomEventHandler",
    "RefreshEventHandler",
    "QuickAssistEventHandler",
    "PreloadEventHandler",
    "StunForcedTerminationEventHandler",
    "PolarizedAssaultEventHandler",
    "EventHandlerFactory",
    "create_default_event_handler_factory",
    "event_handler_factory",
    "register_all_handlers",
]
