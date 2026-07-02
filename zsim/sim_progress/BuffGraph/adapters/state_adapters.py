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


class ScheduledSignalStateAdapter:
    adapter_id = "state.scheduled_signal.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        signal_key = context.node.params.get("signal_key") or context.node.node_id
        tick = _first_upstream_value(context.inputs, "tick")
        if tick is None:
            tick = context.prepared_context.get("tick", 0)
        scheduled_signal = _scheduled_signal(context.prepared_context, signal_key)
        scheduled_tick = context.node.params.get("scheduled_tick")
        if scheduled_tick is None:
            scheduled_tick = scheduled_signal.get("scheduled_tick")
        if scheduled_tick is None:
            scheduled_tick = tick
        active = bool(
            scheduled_signal.get("active", False)
            or scheduled_signal.get("due", False)
            or int(tick) >= int(scheduled_tick)
        )
        signal = {
            "signal_key": signal_key,
            "scheduled_tick": scheduled_tick,
            "current_tick": tick,
            "active": active,
            "payload": scheduled_signal.get("payload", {}),
        }
        return BuffGraphAdapterResult(
            outputs={
                "scheduled_signal": signal,
                "active": active,
                "scheduled_tick": scheduled_tick,
            }
        )


class LastObservedSkillStateAdapter:
    adapter_id = "state.last_observed_skill.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        key = str(context.node.params.get("state_key", context.node.node_id))
        previous_skill = _state(context).get(key)
        current_skill = _first_upstream_mapping(context.inputs, "skill_node")
        if not current_skill:
            current_skill = _mapping(
                context.prepared_context.get("skill_node")
                or context.prepared_context.get("current_skill")
            )
        return BuffGraphAdapterResult(
            outputs={
                "previous_skill": previous_skill,
                "current_skill": current_skill,
                "changed": previous_skill != current_skill,
            }
        )


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


def build_runtime_command_scheduled_signal_state_adapters() -> Mapping[str, object]:
    adapters = (ScheduledSignalStateAdapter(),)
    return {adapter.adapter_id: adapter for adapter in adapters}


def build_character_manager_side_effect_state_adapters() -> Mapping[str, object]:
    adapters = (LastObservedSkillStateAdapter(),)
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


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _state_value(state: Mapping[str, Any]) -> Any:
    for key in ("state", "status", "value", "anomaly_state"):
        if key in state:
            return state[key]
    return None


def _scheduled_signal(prepared_context: Mapping[str, Any], signal_key: Any) -> Mapping[str, Any]:
    signals = prepared_context.get("scheduled_signals")
    if isinstance(signals, Mapping):
        if signal_key in signals:
            value = signals.get(signal_key)
            return value if isinstance(value, Mapping) else {"payload": value, "active": True}
        if signal_key is None and signals:
            value = next(iter(signals.values()))
            return value if isinstance(value, Mapping) else {"payload": value, "active": True}
    signal = prepared_context.get("scheduled_signal")
    return signal if isinstance(signal, Mapping) else {}
