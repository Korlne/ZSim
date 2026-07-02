from __future__ import annotations

from typing import Any, Mapping

from .base import BuffGraphAdapterContext, BuffGraphAdapterResult


class SkillHitTriggerAdapter:
    adapter_id = "trigger.skill_hit.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        event = _mapping(context.prepared_context.get("event"))
        expected_tag = context.node.params.get("skill_tag")
        matched = event.get("kind") == "skill_hit"
        if expected_tag is not None:
            matched = matched and event.get("skill_tag") == expected_tag
        return BuffGraphAdapterResult(outputs={"matched": matched}, trace={"event_kind": event.get("kind")})


class BuffRefreshTriggerAdapter:
    adapter_id = "trigger.buff_refresh.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        event = _mapping(context.prepared_context.get("event"))
        expected_buff = context.node.params.get("buff_index")
        matched = event.get("kind") == "buff_refresh"
        if expected_buff is not None:
            matched = matched and event.get("buff_index") == expected_buff
        return BuffGraphAdapterResult(outputs={"matched": matched}, trace={"event_kind": event.get("kind")})


def build_low_risk_trigger_adapters() -> Mapping[str, object]:
    adapters = (SkillHitTriggerAdapter(), BuffRefreshTriggerAdapter())
    return {adapter.adapter_id: adapter for adapter in adapters}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
