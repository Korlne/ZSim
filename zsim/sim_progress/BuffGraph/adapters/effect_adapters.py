from __future__ import annotations

from typing import Any, Mapping

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


class UpdateTemplateBuffEffectAdapter:
    adapter_id = "effect.update_template_buff.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        command = {
            "type": "update_template_buff",
            "template_buff_index": context.node.params.get("template_buff_index"),
            "mode": context.node.params.get("mode", "set"),
            "count": context.node.params.get("count"),
            "delta": context.node.params.get("delta"),
        }
        return BuffGraphAdapterResult(outputs={"command": command})


class BindPreparedRecordEffectAdapter:
    adapter_id = "effect.bind_prepared_record.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        binding = {
            "record_key": context.node.params.get("record_key"),
            "owner": context.prepared_context.get("prepared_owner")
            or context.prepared_context.get("owner")
            or context.prepared_context.get("owner_name"),
            "equipper": context.prepared_context.get("prepared_equipper")
            or context.prepared_context.get("equipper"),
            "value": context.node.params.get("value"),
        }
        return BuffGraphAdapterResult(outputs={"binding": _without_none(binding)})


class RegisterListenerEffectAdapter:
    adapter_id = "effect.register_listener.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        listener_key = context.node.params.get("listener_key")
        registration = {
            "listener_key": listener_key,
            "source_buff_index": context.node.params.get("source_buff_index")
            or context.prepared_context.get("source_buff_index"),
            "owner": context.prepared_context.get("prepared_owner")
            or context.prepared_context.get("owner")
            or context.prepared_context.get("owner_name"),
            "equipper": context.prepared_context.get("prepared_equipper")
            or context.prepared_context.get("equipper"),
            "payload": context.node.params.get("payload"),
        }
        return BuffGraphAdapterResult(
            outputs={"listener_registration": _without_none(registration)}
        )


class ConsumeListenerSignalEffectAdapter:
    adapter_id = "effect.consume_listener_signal.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        signal = _first_upstream_value(context.inputs, "listener_signal")
        if signal is None:
            signal = context.prepared_context.get("listener_signal")
        listener_key = context.node.params.get("listener_key") or _signal_key(signal)
        consumption = {
            "listener_key": listener_key,
            "consumed": bool(context.node.params.get("consume", True) and signal),
            "signal": signal,
        }
        return BuffGraphAdapterResult(
            outputs={"listener_consumption": _without_none(consumption)}
        )


def build_low_risk_effect_adapters() -> Mapping[str, object]:
    adapters = (StartBuffEffectAdapter(), UpdateBuffCountEffectAdapter())
    return {adapter.adapter_id: adapter for adapter in adapters}


def build_prepared_context_effect_adapters() -> Mapping[str, object]:
    adapters = (
        UpdateTemplateBuffEffectAdapter(),
        BindPreparedRecordEffectAdapter(),
        RegisterListenerEffectAdapter(),
        ConsumeListenerSignalEffectAdapter(),
    )
    return {adapter.adapter_id: adapter for adapter in adapters}


def build_active_buffs_listener_effect_adapters() -> Mapping[str, object]:
    adapters = (RegisterListenerEffectAdapter(), ConsumeListenerSignalEffectAdapter())
    return {adapter.adapter_id: adapter for adapter in adapters}


def _without_none(value: Mapping[str, Any]) -> Mapping[str, Any]:
    return {key: item for key, item in value.items() if item is not None}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _first_upstream_value(inputs: Mapping[str, Any], key: str) -> Any:
    upstream = _mapping(inputs.get("upstream"))
    for outputs in upstream.values():
        output_mapping = _mapping(outputs)
        if key in output_mapping:
            return output_mapping[key]
    return None


def _signal_key(signal: Any) -> Any:
    signal_mapping = _mapping(signal)
    return (
        signal_mapping.get("listener_key")
        or signal_mapping.get("signal_key")
        or signal_mapping.get("key")
    )
