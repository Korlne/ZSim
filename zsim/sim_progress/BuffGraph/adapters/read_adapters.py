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


class ActiveBuffsForEquipperReadAdapter:
    adapter_id = "read.active_buffs_for_equipper.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        equipper = _first_upstream_value(context.inputs, "equipper")
        if equipper is None:
            equipper = context.prepared_context.get("prepared_equipper")
        if equipper is None:
            equipper = context.prepared_context.get("equipper")
        active_buffs = _active_buffs_for_equipper(context.prepared_context, equipper)
        return BuffGraphAdapterResult(
            outputs={
                "active_buffs": active_buffs,
                "active_buff_count": len(active_buffs),
                "equipper": equipper,
            }
        )


class ListenerSignalReadAdapter:
    adapter_id = "read.listener_signal.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        listener_key = context.node.params.get("listener_key") or context.node.params.get(
            "signal_key"
        )
        signal, matched = _listener_signal(context.prepared_context, listener_key)
        return BuffGraphAdapterResult(
            outputs={
                "listener_signal": signal,
                "matched": matched,
                "listener_key": listener_key,
            }
        )


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
        ActiveBuffsForEquipperReadAdapter(),
        ListenerSignalReadAdapter(),
    )
    return {adapter.adapter_id: adapter for adapter in adapters}


def build_active_buffs_listener_read_adapters() -> Mapping[str, object]:
    adapters = (ActiveBuffsForEquipperReadAdapter(), ListenerSignalReadAdapter())
    return {adapter.adapter_id: adapter for adapter in adapters}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _first_upstream_value(inputs: Mapping[str, Any], key: str) -> Any:
    upstream = _mapping(inputs.get("upstream"))
    for outputs in upstream.values():
        output_mapping = _mapping(outputs)
        if key in output_mapping:
            return output_mapping[key]
    return None


def _active_buffs_for_equipper(
    prepared_context: Mapping[str, Any],
    equipper: Any,
) -> list[Any]:
    by_equipper = _mapping(prepared_context.get("active_buffs_by_equipper"))
    if equipper is not None and equipper in by_equipper:
        return _active_entries(by_equipper.get(equipper))

    active_buffs = prepared_context.get("active_buffs")
    entries = _active_entries(active_buffs)
    if equipper is None:
        return entries

    filtered: list[Any] = []
    for entry in entries:
        entry_mapping = _mapping(entry)
        entry_equipper = (
            entry_mapping.get("equipper")
            or entry_mapping.get("owner")
            or entry_mapping.get("owner_name")
        )
        if entry_equipper == equipper:
            filtered.append(entry)
    return filtered


def _active_entries(value: Any) -> list[Any]:
    if isinstance(value, Mapping):
        candidates = list(value.values())
    elif isinstance(value, (list, tuple)):
        candidates = list(value)
    elif value is None:
        candidates = []
    else:
        candidates = [value]

    return [entry for entry in candidates if _mapping(entry).get("active", True) is not False]


def _listener_signal(
    prepared_context: Mapping[str, Any],
    listener_key: Any,
) -> tuple[Any, bool]:
    signals = prepared_context.get("listener_signals")
    if isinstance(signals, Mapping):
        if listener_key is not None and listener_key in signals:
            return signals.get(listener_key), True
        if listener_key is None and signals:
            first_key = next(iter(signals))
            return signals.get(first_key), True

    if isinstance(signals, (list, tuple)):
        if listener_key is None and signals:
            return signals[0], True
        for signal in signals:
            signal_mapping = _mapping(signal)
            signal_key = (
                signal_mapping.get("listener_key")
                or signal_mapping.get("signal_key")
                or signal_mapping.get("key")
            )
            if signal_key == listener_key:
                return signal, True

    signal = prepared_context.get("listener_signal")
    if signal is not None and listener_key is None:
        return signal, True
    if signal is not None:
        signal_mapping = _mapping(signal)
        signal_key = (
            signal_mapping.get("listener_key")
            or signal_mapping.get("signal_key")
            or signal_mapping.get("key")
        )
        return signal, signal_key == listener_key
    return {}, False


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
