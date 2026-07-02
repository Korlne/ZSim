from __future__ import annotations

from typing import Any, Mapping

from .base import BuffGraphAdapterContext, BuffGraphAdapterResult


class LastActiveTickStateAdapter:
    adapter_id = "state.last_active_tick.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        tick = int(context.prepared_context.get("tick", 0))
        previous = _state(context).get(context.node.node_id)
        active = _first_upstream_bool(context)
        value = tick if active else previous
        return BuffGraphAdapterResult(outputs={"last_active_tick": value, "active": active})


class CooldownGateStateAdapter:
    adapter_id = "state.cooldown_gate.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        tick = int(context.prepared_context.get("tick", 0))
        cooldown_ticks = int(context.node.params.get("cooldown_ticks", 0))
        key = str(context.node.params.get("state_key", context.node.node_id))
        last_tick = _state(context).get(key)
        ready = last_tick is None or tick - int(last_tick) >= cooldown_ticks
        return BuffGraphAdapterResult(outputs={"ready": ready, "last_tick": last_tick})


def build_low_risk_state_adapters() -> Mapping[str, object]:
    adapters = (LastActiveTickStateAdapter(), CooldownGateStateAdapter())
    return {adapter.adapter_id: adapter for adapter in adapters}


def _state(context: BuffGraphAdapterContext) -> Mapping[str, Any]:
    state = context.prepared_context.get("state")
    return state if isinstance(state, Mapping) else {}


def _first_upstream_bool(context: BuffGraphAdapterContext) -> bool:
    upstream = context.inputs.get("upstream")
    if not isinstance(upstream, Mapping):
        return False
    for output in upstream.values():
        if isinstance(output, Mapping):
            for key in ("matched", "passed", "ready", "active"):
                if key in output:
                    return bool(output[key])
    return False
