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


def build_low_risk_effect_adapters() -> Mapping[str, object]:
    adapters = (StartBuffEffectAdapter(), UpdateBuffCountEffectAdapter())
    return {adapter.adapter_id: adapter for adapter in adapters}


def build_prepared_context_effect_adapters() -> Mapping[str, object]:
    adapters = (UpdateTemplateBuffEffectAdapter(), BindPreparedRecordEffectAdapter())
    return {adapter.adapter_id: adapter for adapter in adapters}


def _without_none(value: Mapping[str, Any]) -> Mapping[str, Any]:
    return {key: item for key, item in value.items() if item is not None}
