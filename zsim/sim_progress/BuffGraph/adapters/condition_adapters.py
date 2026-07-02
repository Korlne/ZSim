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


class EquipperIdentityConditionAdapter:
    adapter_id = "condition.equipper_identity.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        expected = context.node.params.get("equipper") or context.node.params.get("owner_name")
        equipper = _first_upstream_value(context.inputs, "equipper")
        if equipper is None:
            equipper = context.prepared_context.get("prepared_equipper")
        if equipper is None:
            equipper = context.prepared_context.get("equipper")
        return BuffGraphAdapterResult(outputs={"passed": expected is None or equipper == expected})


class TriggerBuffActiveConditionAdapter:
    adapter_id = "condition.trigger_buff_active.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        trigger_state = _trigger_buff_state(context)
        active = bool(trigger_state.get("active", trigger_state.get("count", 0)))
        return BuffGraphAdapterResult(outputs={"passed": active, "active": active})


class TriggerBuffBoxSizeEqualsConditionAdapter:
    adapter_id = "condition.trigger_buff_box_size_equals.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        expected_size = int(context.node.params.get("expected_size", 0))
        trigger_state = _trigger_buff_state(context)
        actual_size = _built_in_buff_box_size(trigger_state)
        return BuffGraphAdapterResult(
            outputs={
                "passed": actual_size == expected_size,
                "actual_size": actual_size,
                "expected_size": expected_size,
            }
        )


class EquipperIsBackgroundConditionAdapter:
    adapter_id = "condition.equipper_is_background.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        equipper = _equipper(context)
        foreground = _foreground_character(context)
        name_box = context.prepared_context.get("name_box")
        in_team = not isinstance(name_box, (list, tuple)) or equipper in name_box
        passed = equipper is not None and foreground is not None and equipper != foreground and in_team
        return BuffGraphAdapterResult(outputs={"passed": passed})


class EquipperIsForegroundConditionAdapter:
    adapter_id = "condition.equipper_is_foreground.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        equipper = _equipper(context)
        foreground = _foreground_character(context)
        return BuffGraphAdapterResult(
            outputs={"passed": equipper is not None and equipper == foreground}
        )


def build_low_risk_condition_adapters() -> Mapping[str, object]:
    adapters = (CharacterIdentityConditionAdapter(), BuffActiveConditionAdapter())
    return {adapter.adapter_id: adapter for adapter in adapters}


def build_prepared_context_condition_adapters() -> Mapping[str, object]:
    adapters = (
        EquipperIdentityConditionAdapter(),
        TriggerBuffActiveConditionAdapter(),
        TriggerBuffBoxSizeEqualsConditionAdapter(),
        EquipperIsBackgroundConditionAdapter(),
        EquipperIsForegroundConditionAdapter(),
    )
    return {adapter.adapter_id: adapter for adapter in adapters}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _first_upstream_value(inputs: Mapping[str, Any], key: str) -> Any:
    upstream = _mapping(inputs.get("upstream"))
    for output in upstream.values():
        mapped_output = _mapping(output)
        if key in mapped_output:
            return mapped_output[key]
    return None


def _trigger_buff_state(context: BuffGraphAdapterContext) -> Mapping[str, Any]:
    upstream_state = _first_upstream_value(context.inputs, "trigger_buff_state")
    if isinstance(upstream_state, Mapping):
        return upstream_state
    trigger_buff_index = context.node.params.get("trigger_buff_index")
    trigger_states = _mapping(
        context.prepared_context.get("trigger_buff_states")
        or context.prepared_context.get("trigger_buffs")
    )
    if trigger_buff_index is not None and trigger_buff_index in trigger_states:
        return _mapping(trigger_states.get(trigger_buff_index))
    return _mapping(context.prepared_context.get("trigger_buff_state"))


def _built_in_buff_box_size(trigger_state: Mapping[str, Any]) -> int:
    explicit_size = trigger_state.get("built_in_buff_box_size")
    if explicit_size is not None:
        return int(explicit_size)
    box = trigger_state.get("built_in_buff_box") or trigger_state.get("built_in_buff_box_list")
    if isinstance(box, Mapping):
        return len(box)
    if isinstance(box, (list, tuple, set)):
        return len(box)
    return 0


def _equipper(context: BuffGraphAdapterContext) -> Any:
    equipper = _first_upstream_value(context.inputs, "equipper")
    if equipper is None:
        equipper = context.prepared_context.get("prepared_equipper")
    if equipper is None:
        equipper = context.prepared_context.get("equipper")
    return equipper


def _foreground_character(context: BuffGraphAdapterContext) -> Any:
    foreground = _first_upstream_value(context.inputs, "character")
    if foreground is None:
        foreground = context.prepared_context.get("foreground_character")
    if foreground is None:
        name_box = context.prepared_context.get("name_box")
        if isinstance(name_box, (list, tuple)) and name_box:
            foreground = name_box[0]
    return foreground
