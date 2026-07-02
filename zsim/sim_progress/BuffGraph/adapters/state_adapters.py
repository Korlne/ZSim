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


class LastObservedEnemyStateAdapter:
    adapter_id = "state.last_observed_enemy_state.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        key = str(context.node.params.get("state_key", context.node.node_id))
        previous_state = _state(context).get(key)
        current_state = _first_upstream_value(context.inputs, "state_value")
        if current_state is None:
            current_state = _state_value(_first_upstream_mapping(context.inputs, "anomaly_state"))
        return BuffGraphAdapterResult(
            outputs={
                "previous_state": previous_state,
                "current_state": current_state,
                "changed": previous_state != current_state,
            }
        )


class EdgeMemoryStateAdapter:
    adapter_id = "state.edge_memory.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        key = str(context.node.params.get("state_key", context.node.node_id))
        previous = _state(context).get(key)
        current = _first_upstream_value(context.inputs, "current")
        if current is None:
            current = _first_upstream_value(context.inputs, "active")
        if current is None:
            current = _first_upstream_value(context.inputs, "passed")
        return BuffGraphAdapterResult(
            outputs={
                "previous": previous,
                "current": current,
                "rising_edge": not bool(previous) and bool(current),
                "falling_edge": bool(previous) and not bool(current),
                "changed": previous != current,
            }
        )


class AnomalySignalStateAdapter:
    adapter_id = "state.anomaly_signal.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        signal_key = context.node.params.get("signal_key") or context.node.node_id
        anomaly_state = _first_upstream_mapping(context.inputs, "anomaly_state")
        anomaly_bar = _first_upstream_mapping(context.inputs, "anomaly_bar")
        dot_runtime_state = _first_upstream_mapping(context.inputs, "dot_runtime_state")
        active = bool(
            _first_upstream_value(context.inputs, "active")
            or anomaly_state.get("active")
            or dot_runtime_state.get("active")
        )
        signal = {
            "signal_key": signal_key,
            "anomaly_state": anomaly_state,
            "anomaly_bar": anomaly_bar,
            "dot_runtime_state": dot_runtime_state,
            "active": active,
        }
        return BuffGraphAdapterResult(outputs={"anomaly_signal": signal, "active": active})


def build_low_risk_state_adapters() -> Mapping[str, object]:
    adapters = (LastActiveTickStateAdapter(), CooldownGateStateAdapter())
    return {adapter.adapter_id: adapter for adapter in adapters}


def build_enemy_anomaly_state_state_adapters() -> Mapping[str, object]:
    adapters = (
        LastObservedEnemyStateAdapter(),
        EdgeMemoryStateAdapter(),
        AnomalySignalStateAdapter(),
    )
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


def _first_upstream_value(inputs: Mapping[str, Any], key: str) -> Any:
    upstream = inputs.get("upstream")
    if not isinstance(upstream, Mapping):
        return None
    for output in upstream.values():
        if isinstance(output, Mapping) and key in output:
            return output[key]
    return None


def _first_upstream_mapping(inputs: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = _first_upstream_value(inputs, key)
    return value if isinstance(value, Mapping) else {}


def _state_value(state: Mapping[str, Any]) -> Any:
    for key in ("state", "status", "value", "anomaly_state"):
        if key in state:
            return state[key]
    return None
