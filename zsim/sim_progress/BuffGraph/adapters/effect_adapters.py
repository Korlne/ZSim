from __future__ import annotations

from typing import Mapping

from .base import BuffGraphAdapterContext, BuffGraphAdapterResult


class StartBuffEffectAdapter:
    adapter_id = "effect.start_buff.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        command = {
            "type": "start_buff",
            "buff_index": context.node.params.get("buff_index"),
            "count": context.node.params.get("count", 1),
            "duration_ticks": context.node.params.get("duration_ticks"),
        }
        return BuffGraphAdapterResult(outputs={"command": command})


class UpdateBuffCountEffectAdapter:
    adapter_id = "effect.update_buff_count.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        command = {
            "type": "update_buff_count",
            "buff_index": context.node.params.get("buff_index"),
            "delta": context.node.params.get("delta", 1),
        }
        return BuffGraphAdapterResult(outputs={"command": command})


def build_low_risk_effect_adapters() -> Mapping[str, object]:
    adapters = (StartBuffEffectAdapter(), UpdateBuffCountEffectAdapter())
    return {adapter.adapter_id: adapter for adapter in adapters}
