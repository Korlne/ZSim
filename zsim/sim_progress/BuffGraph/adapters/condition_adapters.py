from __future__ import annotations

from typing import Any, Mapping

from .base import BuffGraphAdapterContext, BuffGraphAdapterResult


class CharacterIdentityConditionAdapter:
    adapter_id = "condition.character_identity.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        expected = context.node.params.get("owner_name") or context.node.params.get("character")
        owner = context.prepared_context.get("owner_name") or context.prepared_context.get("owner")
        return BuffGraphAdapterResult(outputs={"passed": expected is None or owner == expected})


class BuffActiveConditionAdapter:
    adapter_id = "condition.buff_active.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        buff_index = context.node.params.get("buff_index")
        buffs = _mapping(context.prepared_context.get("buffs"))
        buff_state = _mapping(buffs.get(buff_index))
        active = bool(buff_state.get("active", False))
        return BuffGraphAdapterResult(
            outputs={
                "passed": active,
                "active": active,
                "count": buff_state.get("count", 0),
                "remaining_ticks": buff_state.get("remaining_ticks", 0),
            }
        )


def build_low_risk_condition_adapters() -> Mapping[str, object]:
    adapters = (CharacterIdentityConditionAdapter(), BuffActiveConditionAdapter())
    return {adapter.adapter_id: adapter for adapter in adapters}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
