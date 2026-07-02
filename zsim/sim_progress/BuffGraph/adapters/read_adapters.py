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


class EnemyContextReadAdapter:
    adapter_id = "read.enemy_context.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        enemy_context = _mapping(
            context.prepared_context.get("enemy_context")
            or context.prepared_context.get("enemy")
        )
        return BuffGraphAdapterResult(outputs={"enemy_context": enemy_context})


class EnemyAnomalyStateReadAdapter:
    adapter_id = "read.enemy_anomaly_state.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        anomaly_key = context.node.params.get("anomaly_key") or context.node.params.get("element")
        enemy_context = _enemy_context(context)
        anomaly_state = _select_keyed_mapping(
            enemy_context.get("anomaly_states")
            or enemy_context.get("enemy_anomaly_states")
            or context.prepared_context.get("enemy_anomaly_states"),
            anomaly_key,
        )
        if not anomaly_state:
            anomaly_state = _mapping(
                enemy_context.get("anomaly_state")
                or context.prepared_context.get("enemy_anomaly_state")
            )
        state_value = _state_value(anomaly_state)
        active = bool(anomaly_state.get("active", state_value))
        return BuffGraphAdapterResult(
            outputs={
                "anomaly_state": anomaly_state,
                "state_value": state_value,
                "active": active,
                "anomaly_key": anomaly_key,
            }
        )


class EnemyAnomalyBarReadAdapter:
    adapter_id = "read.enemy_anomaly_bar.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        anomaly_key = context.node.params.get("anomaly_key") or context.node.params.get("element")
        enemy_context = _enemy_context(context)
        anomaly_bar = _select_keyed_mapping(
            enemy_context.get("anomaly_bars")
            or enemy_context.get("enemy_anomaly_bars")
            or context.prepared_context.get("enemy_anomaly_bars"),
            anomaly_key,
        )
        if not anomaly_bar:
            anomaly_bar = _mapping(
                enemy_context.get("anomaly_bar")
                or context.prepared_context.get("enemy_anomaly_bar")
            )
        value = _number(
            anomaly_bar.get("value")
            if "value" in anomaly_bar
            else anomaly_bar.get("current", anomaly_bar.get("amount", 0))
        )
        threshold = _number(
            anomaly_bar.get("threshold")
            if "threshold" in anomaly_bar
            else anomaly_bar.get("max", anomaly_bar.get("limit", 0))
        )
        ratio = value / threshold if threshold else 0.0
        return BuffGraphAdapterResult(
            outputs={
                "anomaly_bar": anomaly_bar,
                "anomaly_value": value,
                "anomaly_threshold": threshold,
                "anomaly_ratio": ratio,
                "anomaly_key": anomaly_key,
            }
        )


class EnemyEdgeStateReadAdapter:
    adapter_id = "read.enemy_edge_state.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        edge_key = context.node.params.get("edge_key") or context.node.params.get("state_key")
        edge_state = _select_keyed_mapping(context.prepared_context.get("enemy_edge_states"), edge_key)
        if not edge_state:
            edge_state = _mapping(context.prepared_context.get("enemy_edge_state"))
        previous = edge_state.get("previous")
        current = edge_state.get("current")
        return BuffGraphAdapterResult(
            outputs={
                "edge_state": edge_state,
                "previous": previous,
                "current": current,
                "changed": bool(edge_state.get("changed", previous != current)),
            }
        )


class DotRuntimeStateReadAdapter:
    adapter_id = "read.dot_runtime_state.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        dot_key = context.node.params.get("dot_key")
        dot_runtime_state = _select_keyed_mapping(
            context.prepared_context.get("dot_runtime_states"),
            dot_key,
        )
        if not dot_runtime_state:
            dot_runtime_state = _mapping(context.prepared_context.get("dot_runtime_state"))
        return BuffGraphAdapterResult(
            outputs={
                "dot_runtime_state": dot_runtime_state,
                "active": bool(dot_runtime_state.get("active", False)),
                "dot_key": dot_key,
            }
        )


class SkillNodeReadAdapter:
    adapter_id = "read.skill_node.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        skill_key = context.node.params.get("skill_key")
        skill_node = _select_keyed_mapping(
            context.prepared_context.get("skill_nodes"),
            skill_key,
        )
        if not skill_node:
            skill_node = _mapping(
                context.prepared_context.get("skill_node")
                or context.prepared_context.get("current_skill")
            )
        tag_key = context.node.params.get("tag_key") or "skill_tag"
        skill_tag = skill_node.get(tag_key) or skill_node.get("tag") or skill_node.get("skill_tag")
        trigger_level = skill_node.get("trigger_level")
        hit_index = skill_node.get("hit_index", skill_node.get("hit"))
        is_last_hit = bool(
            skill_node.get("is_last_hit")
            or skill_node.get("last_hit")
            or skill_node.get("hit_is_last")
        )
        return BuffGraphAdapterResult(
            outputs={
                "skill_node": skill_node,
                "skill_tag": skill_tag,
                "trigger_level": trigger_level,
                "hit_index": hit_index,
                "is_last_hit": is_last_hit,
            }
        )


class NextTeamMemberReadAdapter:
    adapter_id = "read.next_team_member.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        name_box = context.prepared_context.get("name_box")
        team = list(name_box) if isinstance(name_box, (list, tuple)) else []
        current = (
            _first_upstream_value(context.inputs, "character")
            or context.prepared_context.get("operating_character")
            or context.prepared_context.get("foreground_character")
        )
        offset = int(context.node.params.get("offset", 1))
        if not team:
            return BuffGraphAdapterResult(outputs={"character": None, "team_index": None})
        if current in team:
            index = (team.index(current) + offset) % len(team)
        else:
            index = offset % len(team)
        return BuffGraphAdapterResult(outputs={"character": team[index], "team_index": index})


class CalculatorAttributeReadAdapter:
    adapter_id = "read.calculator_attribute.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        attribute = context.node.params.get("attribute")
        source = context.node.params.get("source")
        value = _calculator_attribute(context.prepared_context, attribute, source)
        if value is None:
            value = context.node.params.get("default", 0)
        return BuffGraphAdapterResult(
            outputs={
                "value": _number(value),
                "attribute": attribute,
                "source": source,
            }
        )


class RefinementReadAdapter:
    adapter_id = "read.refinement.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        source = context.node.params.get("source")
        refinement = _refinement(context.prepared_context, source)
        if refinement is None:
            refinement = context.node.params.get("default", 1)
        return BuffGraphAdapterResult(outputs={"refinement": _number(refinement)})


class CurrentActionReadAdapter:
    adapter_id = "read.current_action.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        action = _mapping(
            context.prepared_context.get("current_action")
            or context.prepared_context.get("action")
        )
        action_name = (
            action.get("action_name")
            or action.get("name")
            or context.prepared_context.get("current_action_name")
        )
        trigger_level = action.get("trigger_level", context.prepared_context.get("trigger_level"))
        return BuffGraphAdapterResult(
            outputs={
                "action": action,
                "action_name": action_name,
                "trigger_level": trigger_level,
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


def build_enemy_anomaly_state_read_adapters() -> Mapping[str, object]:
    adapters = (
        EnemyContextReadAdapter(),
        EnemyAnomalyStateReadAdapter(),
        EnemyAnomalyBarReadAdapter(),
        EnemyEdgeStateReadAdapter(),
        DotRuntimeStateReadAdapter(),
    )
    return {adapter.adapter_id: adapter for adapter in adapters}


def build_runtime_command_scheduled_signal_read_adapters() -> Mapping[str, object]:
    adapters = (SkillNodeReadAdapter(),)
    return {adapter.adapter_id: adapter for adapter in adapters}


def build_character_manager_side_effect_read_adapters() -> Mapping[str, object]:
    adapters = (NextTeamMemberReadAdapter(),)
    return {adapter.adapter_id: adapter for adapter in adapters}


def build_calculator_runtime_formula_read_adapters() -> Mapping[str, object]:
    adapters = (
        CalculatorAttributeReadAdapter(),
        RefinementReadAdapter(),
        CurrentActionReadAdapter(),
    )
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


def _enemy_context(context: BuffGraphAdapterContext) -> Mapping[str, Any]:
    upstream_context = _first_upstream_value(context.inputs, "enemy_context")
    if isinstance(upstream_context, Mapping):
        return upstream_context
    return _mapping(
        context.prepared_context.get("enemy_context")
        or context.prepared_context.get("enemy")
    )


def _select_keyed_mapping(value: Any, key: Any) -> Mapping[str, Any]:
    mapping = _mapping(value)
    if key is not None and key in mapping:
        return _mapping(mapping.get(key))
    if key is None and len(mapping) == 1:
        return _mapping(next(iter(mapping.values())))
    return {}


def _state_value(state: Mapping[str, Any]) -> Any:
    for key in ("state", "status", "value", "anomaly_state"):
        if key in state:
            return state[key]
    return None


def _number(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _calculator_attribute(
    prepared_context: Mapping[str, Any],
    attribute: Any,
    source: Any,
) -> Any:
    attributes = _mapping(
        prepared_context.get("calculator_attributes")
        or prepared_context.get("calculation_attributes")
    )
    if source is not None:
        sourced = _mapping(attributes.get(source))
        if attribute in sourced:
            return sourced.get(attribute)
    if attribute in attributes:
        return attributes.get(attribute)

    calculator = _mapping(prepared_context.get("calculator"))
    if source is not None:
        sourced = _mapping(calculator.get(source))
        if attribute in sourced:
            return sourced.get(attribute)
    return calculator.get(attribute)


def _refinement(prepared_context: Mapping[str, Any], source: Any) -> Any:
    refinements = _mapping(prepared_context.get("refinements"))
    if source is not None and source in refinements:
        return refinements.get(source)
    if "refinement" in prepared_context:
        return prepared_context.get("refinement")
    equip = _mapping(prepared_context.get("equipment") or prepared_context.get("w_engine"))
    return equip.get("refinement")


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
