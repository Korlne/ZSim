from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from zsim.sim_progress.Dot.BaseDot import Dot


class _EnemyDynamicWithDotRuntimeRead(Protocol):
    @property
    def dynamic_dot_list(self) -> Iterable[Dot]: ...


class _EnemyWithDotRuntimeRead(Protocol):
    dynamic: _EnemyDynamicWithDotRuntimeRead


def snapshot_enemy_dot_runtime_state(
    enemy: _EnemyWithDotRuntimeRead,
) -> tuple[Dot, ...]:
    return tuple(enemy.dynamic.dynamic_dot_list)


class DotRuntimeStateReadPort:
    def __init__(self, enemy: _EnemyWithDotRuntimeRead) -> None:
        self._enemy = enemy

    def snapshot(self) -> tuple[Dot, ...]:
        return snapshot_enemy_dot_runtime_state(self._enemy)

    def find_by_index(self, dot_index: str | None) -> Dot | None:
        for dot in self.snapshot():
            if dot.ft.index == dot_index:
                return dot
        return None

    def find_active_by_index(self, dot_index: str | None) -> Dot | None:
        for dot in self.snapshot():
            if dot.ft.index == dot_index and dot.dy.active:
                return dot
        return None
