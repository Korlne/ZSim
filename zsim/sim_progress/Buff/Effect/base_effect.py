from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..buff_class import Buff


class EffectBaseClass(ABC):
    """
    Base class for all Buff Effects.
    An Effect represents a single unit of functionality provided by a Buff.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config

    @abstractmethod
    def on_attach(self, buff: "Buff") -> None:
        """Called when the effect is attached to a Buff instance."""
        pass

    @abstractmethod
    def on_detach(self, buff: "Buff") -> None:
        """Called when the effect is removed from a Buff instance."""
        pass
