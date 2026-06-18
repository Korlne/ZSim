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


def read_enemy_shock_active(enemy: _EnemyWithDynamicShockRead) -> bool:
    return enemy.dynamic.shock


def read_enemy_stun_active(enemy: _EnemyWithDynamicStunRead) -> bool:
    return enemy.dynamic.stun
