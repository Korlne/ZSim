from typing import Protocol


class _EnemyDynamicWithAnomalyRead(Protocol):
    def is_under_anomaly(self) -> bool: ...


class _EnemyWithDynamicAnomalyRead(Protocol):
    dynamic: _EnemyDynamicWithAnomalyRead


def read_enemy_anomaly_active(enemy: _EnemyWithDynamicAnomalyRead) -> bool:
    return enemy.dynamic.is_under_anomaly()
