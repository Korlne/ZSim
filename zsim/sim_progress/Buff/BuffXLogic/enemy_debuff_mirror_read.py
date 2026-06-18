from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from .. import Buff


_MIYABI_FROSTBURN_DEBUFF_INDEX = "Buff-角色-雅-核心被动-霜灼"


class _EnemyDynamicWithDebuffMirrorRead(Protocol):
    @property
    def dynamic_debuff_list(self) -> Iterable[object]: ...


class _EnemyWithDynamicDebuffMirrorRead(Protocol):
    dynamic: _EnemyDynamicWithDebuffMirrorRead


class MiyabiFrostburnDebuffMirrorReader:
    def __init__(self, enemy: _EnemyWithDynamicDebuffMirrorRead) -> None:
        self._dynamic_debuff_list = enemy.dynamic.dynamic_debuff_list

    def has_miyabi_frostburn_debuff(self) -> bool:
        for debuff in self._dynamic_debuff_list:
            if not isinstance(debuff, Buff):
                raise TypeError(f"{debuff}不是Buff类！")
            if debuff.ft.index == _MIYABI_FROSTBURN_DEBUFF_INDEX:
                return True
        return False
