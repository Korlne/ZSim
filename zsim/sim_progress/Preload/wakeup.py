from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from zsim.sim_progress.Preload.PreloadEngine import SwapCancelValidateEngine

if TYPE_CHECKING:
    from zsim.sim_progress.Preload.PreloadClass import PreloadClass
    from zsim.sim_progress.Preload.SkillsQueue import SkillNode


@dataclass(frozen=True, slots=True)
class PreloadWakeupSource:
    """Projects the next Preload/APL-observable action boundary."""

    preload: "PreloadClass"
    name: str = "preload-action"

    def next_wakeup_tick(self, current_tick: int) -> int | None:
        data = self.preload.preload_data
        candidates: list[int] = []

        if data.preload_action_list_before_confirm:
            candidates.append(current_tick + 1)

        for stack in data.personal_node_stack.values():
            for node in stack:
                self._collect_node_wakeups(node, current_tick, candidates)

        for node in data.current_node_stack:
            self._collect_node_wakeups(node, current_tick, candidates)

        if not data.personal_node_stack:
            candidates.append(current_tick + 1)

        future_candidates = [tick for tick in candidates if tick > current_tick]
        if not future_candidates:
            return None
        return min(future_candidates)

    @staticmethod
    def _collect_node_wakeups(
        node: "SkillNode",
        current_tick: int,
        candidates: list[int],
    ) -> None:
        if node.preload_tick > current_tick:
            candidates.append(node.preload_tick)
        if node.end_tick > current_tick:
            candidates.append(node.end_tick)
        if not node.active_generation:
            return
        swap_tick = (
            node.preload_tick
            + node.skill.swap_cancel_ticks
            + SwapCancelValidateEngine.spawn_lag_time(node)
        )
        if swap_tick > current_tick:
            candidates.append(swap_tick)


__all__ = ["PreloadWakeupSource"]
