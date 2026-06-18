from typing import Protocol


class _EnemyDynamicWithFrozenEdgeRead(Protocol):
    @property
    def frozen(self) -> bool | None: ...


class _EnemyWithDynamicFrozenEdgeRead(Protocol):
    dynamic: _EnemyDynamicWithFrozenEdgeRead


class _EnemyDynamicWithStunEdgeRead(Protocol):
    @property
    def stun(self) -> bool | None: ...


class _EnemyWithDynamicStunEdgeRead(Protocol):
    dynamic: _EnemyDynamicWithStunEdgeRead


class _EnemyDynamicWithFrostFrostbiteEdgeRead(Protocol):
    @property
    def frost_frostbite(self) -> bool | None: ...


class _EnemyWithDynamicFrostFrostbiteEdgeRead(Protocol):
    dynamic: _EnemyDynamicWithFrostFrostbiteEdgeRead


def read_enemy_frozen_edge_state(enemy: _EnemyWithDynamicFrozenEdgeRead) -> bool:
    frozen = enemy.dynamic.frozen
    return False if frozen is None else frozen


def read_enemy_stun_edge_state(
    enemy: _EnemyWithDynamicStunEdgeRead,
) -> bool | None:
    return enemy.dynamic.stun


def read_enemy_frost_frostbite_edge_state(
    enemy: _EnemyWithDynamicFrostFrostbiteEdgeRead,
) -> bool | None:
    return enemy.dynamic.frost_frostbite
