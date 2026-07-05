from abc import ABC, abstractmethod


class BaseUniqueMechanic(ABC):
    @abstractmethod
    def __init__(self, enemy_instance):
        self.enemy = enemy_instance

    @abstractmethod
    def update_myself(self, *args, **kwargs):
        pass

    @abstractmethod
    def event_active(self, *args, **kwargs):
        pass
