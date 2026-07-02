from __future__ import annotations

from typing import Any, Mapping

from .base import BuffGraphAdapterContext, BuffGraphAdapterResult


class CurrentTickReadAdapter:
    adapter_id = "read.current_tick.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        tick = int(context.prepared_context.get("tick", 0))
        return BuffGraphAdapterResult(outputs={"tick": tick})


class BuffRuntimeViewReadAdapter:
    adapter_id = "read.buff_runtime_view.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        buff_index = context.node.params.get("buff_index")
        view = _mapping(context.prepared_context.get("buff_runtime_view"))
        value = _mapping(view.get(buff_index)) if buff_index is not None else view
        return BuffGraphAdapterResult(outputs={"value": value})


def build_low_risk_read_adapters() -> Mapping[str, object]:
    adapters = (CurrentTickReadAdapter(), BuffRuntimeViewReadAdapter())
    return {adapter.adapter_id: adapter for adapter in adapters}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
