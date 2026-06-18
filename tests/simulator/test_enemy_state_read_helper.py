from __future__ import annotations

from types import SimpleNamespace

import pytest

from zsim.sim_progress.Buff.BuffXLogic.enemy_state_read import (
    read_enemy_shock_active,
    read_enemy_stun_active,
)


class _EnemyDynamicStateProbe:
    def __init__(self, *, shock: bool, stun: bool) -> None:
        self._shock = shock
        self._stun = stun
        self.shock_reads = 0
        self.stun_reads = 0

    @property
    def shock(self) -> bool:
        self.shock_reads += 1
        return self._shock

    @property
    def stun(self) -> bool:
        self.stun_reads += 1
        return self._stun


@pytest.mark.parametrize("shock", [True, False])
def test_read_enemy_shock_active_reads_dynamic_shock_once(*, shock: bool) -> None:
    dynamic = _EnemyDynamicStateProbe(shock=shock, stun=not shock)
    enemy = SimpleNamespace(dynamic=dynamic)

    assert read_enemy_shock_active(enemy) is shock
    assert dynamic.shock_reads == 1
    assert dynamic.stun_reads == 0


@pytest.mark.parametrize("stun", [True, False])
def test_read_enemy_stun_active_reads_dynamic_stun_once(*, stun: bool) -> None:
    dynamic = _EnemyDynamicStateProbe(shock=not stun, stun=stun)
    enemy = SimpleNamespace(dynamic=dynamic)

    assert read_enemy_stun_active(enemy) is stun
    assert dynamic.stun_reads == 1
    assert dynamic.shock_reads == 0
