from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Protocol


class _EnemyWithDynamicAnomalyMapRead(Protocol):
    dynamic: object


def read_enemy_anomaly_state(
    enemy: _EnemyWithDynamicAnomalyMapRead,
    name: str,
) -> Any:
    return getattr(enemy.dynamic, name)


def snapshot_enemy_anomaly_states(
    enemy: _EnemyWithDynamicAnomalyMapRead,
    names: Iterable[str],
) -> dict[str, Any]:
    return {name: getattr(enemy.dynamic, name) for name in names}
