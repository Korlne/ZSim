from typing import Protocol


class _EnemyDynamicWithShockRead(Protocol):
    @property
    def shock(self) -> bool: ...


class _EnemyWithDynamicShockRead(Protocol):
    dynamic: _EnemyDynamicWithShockRead


class _EnemyDynamicWithStunRead(Protocol):
    @property
    def stun(self) -> bool: ...


class _EnemyWithDynamicStunRead(Protocol):
    dynamic: _EnemyDynamicWithStunRead


class _EnemyDynamicWithStateRead(
    _EnemyDynamicWithShockRead,
    _EnemyDynamicWithStunRead,
    Protocol,
):
    pass


class _EnemyWithDynamicStateRead(Protocol):
    dynamic: _EnemyDynamicWithStateRead


def read_enemy_shock_active(enemy: _EnemyWithDynamicShockRead) -> bool:
    return enemy.dynamic.shock


def read_enemy_stun_active(enemy: _EnemyWithDynamicStunRead) -> bool:
    return enemy.dynamic.stun


class EnemyStateReadPort:
    def __init__(self, enemy: _EnemyWithDynamicStateRead) -> None:
        self._enemy = enemy

    def shock_active(self) -> bool:
        return read_enemy_shock_active(self._enemy)

    def stun_active(self) -> bool:
        return read_enemy_stun_active(self._enemy)
