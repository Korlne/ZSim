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


class _EnemyDynamicWithEdgeStateRead(
    _EnemyDynamicWithFrozenEdgeRead,
    _EnemyDynamicWithStunEdgeRead,
    _EnemyDynamicWithFrostFrostbiteEdgeRead,
    Protocol,
):
    pass


class _EnemyWithDynamicEdgeStateRead(Protocol):
    dynamic: _EnemyDynamicWithEdgeStateRead


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


class EnemyEdgeStateReadPort:
    def __init__(self, enemy: _EnemyWithDynamicEdgeStateRead) -> None:
        self._enemy = enemy

    def frozen_edge_state(self) -> bool:
        return read_enemy_frozen_edge_state(self._enemy)

    def stun_edge_state(self) -> bool | None:
        return read_enemy_stun_edge_state(self._enemy)

    def frost_frostbite_edge_state(self) -> bool | None:
        return read_enemy_frost_frostbite_edge_state(self._enemy)
