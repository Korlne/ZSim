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


class PreparedOwnerReadAdapter:
    adapter_id = "read.prepared_owner.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        owner = context.prepared_context.get("prepared_owner")
        if owner is None:
            owner = context.prepared_context.get("owner")
        if owner is None:
            owner = context.prepared_context.get("owner_name")
        return BuffGraphAdapterResult(outputs={"owner": owner})


class PreparedEquipperReadAdapter:
    adapter_id = "read.prepared_equipper.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        equipper = context.prepared_context.get("prepared_equipper")
        if equipper is None:
            equipper = context.prepared_context.get("equipper")
        return BuffGraphAdapterResult(outputs={"equipper": equipper})


class PreparedTemplateBuffReadAdapter:
    adapter_id = "read.prepared_template_buff.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        template_buff_index = context.node.params.get("template_buff_index")
        templates = _mapping(context.prepared_context.get("template_buffs"))
        if template_buff_index is not None and template_buff_index in templates:
            template_buff = _mapping(templates.get(template_buff_index))
        else:
            template_buff = _mapping(
                context.prepared_context.get("prepared_template_buff")
                or context.prepared_context.get("template_buff")
            )
        return BuffGraphAdapterResult(
            outputs={
                "template_buff": template_buff,
                "template_buff_index": template_buff_index,
            }
        )


class TriggerBuffStateReadAdapter:
    adapter_id = "read.trigger_buff_state.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        trigger_buff_index = context.node.params.get("trigger_buff_index")
        trigger_states = _mapping(
            context.prepared_context.get("trigger_buff_states")
            or context.prepared_context.get("trigger_buffs")
        )
        trigger_state = _mapping(trigger_states.get(trigger_buff_index))
        if not trigger_state:
            trigger_state = _mapping(context.prepared_context.get("trigger_buff_state"))
        box_size = _built_in_buff_box_size(trigger_state)
        count = trigger_state.get("count", box_size)
        active = bool(trigger_state.get("active", count or box_size))
        return BuffGraphAdapterResult(
            outputs={
                "trigger_buff_state": trigger_state,
                "trigger_buff_index": trigger_buff_index,
                "active": active,
                "count": count,
                "built_in_buff_box_size": box_size,
            }
        )


class ForegroundCharacterReadAdapter:
    adapter_id = "read.foreground_character.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        character = context.prepared_context.get("foreground_character")
        if character is None:
            name_box = context.prepared_context.get("name_box")
            if isinstance(name_box, (list, tuple)) and name_box:
                character = name_box[0]
        return BuffGraphAdapterResult(outputs={"character": character})


def build_low_risk_read_adapters() -> Mapping[str, object]:
    adapters = (CurrentTickReadAdapter(), BuffRuntimeViewReadAdapter())
    return {adapter.adapter_id: adapter for adapter in adapters}


def build_prepared_context_read_adapters() -> Mapping[str, object]:
    adapters = (
        PreparedOwnerReadAdapter(),
        PreparedEquipperReadAdapter(),
        PreparedTemplateBuffReadAdapter(),
        TriggerBuffStateReadAdapter(),
        ForegroundCharacterReadAdapter(),
    )
    return {adapter.adapter_id: adapter for adapter in adapters}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


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
