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


class TriggerBuffCountCompareConditionAdapter:
    adapter_id = "condition.trigger_buff_count_compare.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        trigger_state = _trigger_buff_state(context)
        actual_count = int(trigger_state.get("count", 0))
        expected_count = int(context.node.params.get("expected_count", 0))
        operator = str(context.node.params.get("operator", "equals"))
        passed = _compare(actual_count, expected_count, operator)
        return BuffGraphAdapterResult(
            outputs={
                "passed": passed,
                "actual_count": actual_count,
                "expected_count": expected_count,
                "operator": operator,
            }
        )


class SkillTriggerLevelConditionAdapter:
    adapter_id = "condition.skill_trigger_level.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        actual_level = int(_skill_trigger_level(context) or 0)
        expected_level = int(context.node.params.get("expected_level", 0))
        operator = str(context.node.params.get("operator", "equals"))
        passed = _compare(actual_level, expected_level, operator)
        return BuffGraphAdapterResult(
            outputs={
                "passed": passed,
                "actual_level": actual_level,
                "expected_level": expected_level,
                "operator": operator,
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


class EnemyStateConditionAdapter:
    adapter_id = "condition.enemy_state.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        anomaly_state = _anomaly_state(context)
        actual_state = _state_value(anomaly_state)
        expected_state = context.node.params.get("expected_state")
        expected_active = context.node.params.get("active")
        active = bool(anomaly_state.get("active", actual_state))
        passed = expected_state is None or actual_state == expected_state
        if expected_active is not None:
            passed = passed and active is bool(expected_active)
        return BuffGraphAdapterResult(
            outputs={
                "passed": passed,
                "actual_state": actual_state,
                "expected_state": expected_state,
                "active": active,
            }
        )


class EdgeTransitionConditionAdapter:
    adapter_id = "condition.edge_transition.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        edge_state = _edge_state(context)
        previous = edge_state.get("previous")
        current = edge_state.get("current")
        transition = str(context.node.params.get("transition", "changed"))
        passed = _edge_transition_passed(
            previous=previous,
            current=current,
            transition=transition,
            from_state=context.node.params.get("from_state"),
            to_state=context.node.params.get("to_state"),
        )
        return BuffGraphAdapterResult(
            outputs={
                "passed": passed,
                "previous": previous,
                "current": current,
                "transition": transition,
            }
        )


class TickWindowConditionAdapter:
    adapter_id = "condition.tick_window.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        tick = _first_upstream_value(context.inputs, "tick")
        if tick is None:
            tick = context.prepared_context.get("tick", 0)
        tick = int(tick)
        start_tick = context.node.params.get("start_tick")
        end_tick = context.node.params.get("end_tick")
        start_ok = start_tick is None or tick >= int(start_tick)
        end_ok = end_tick is None or tick <= int(end_tick)
        return BuffGraphAdapterResult(
            outputs={
                "passed": start_ok and end_ok,
                "tick": tick,
                "start_tick": start_tick,
                "end_tick": end_tick,
            }
        )


def build_low_risk_condition_adapters() -> Mapping[str, object]:
    adapters = (CharacterIdentityConditionAdapter(), BuffActiveConditionAdapter())
    return {adapter.adapter_id: adapter for adapter in adapters}


def build_prepared_context_condition_adapters() -> Mapping[str, object]:
    adapters = (
        EquipperIdentityConditionAdapter(),
        TriggerBuffActiveConditionAdapter(),
        TriggerBuffBoxSizeEqualsConditionAdapter(),
        TriggerBuffCountCompareConditionAdapter(),
        SkillTriggerLevelConditionAdapter(),
        EquipperIsBackgroundConditionAdapter(),
        EquipperIsForegroundConditionAdapter(),
    )
    return {adapter.adapter_id: adapter for adapter in adapters}


def build_enemy_anomaly_state_condition_adapters() -> Mapping[str, object]:
    adapters = (EnemyStateConditionAdapter(), EdgeTransitionConditionAdapter())
    return {adapter.adapter_id: adapter for adapter in adapters}


def build_runtime_command_scheduled_signal_condition_adapters() -> Mapping[str, object]:
    adapters = (TickWindowConditionAdapter(),)
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


def _compare(actual: int, expected: int, operator: str) -> bool:
    if operator in {"equals", "==", "eq"}:
        return actual == expected
    if operator in {"not_equals", "!=", "ne"}:
        return actual != expected
    if operator in {"at_least", ">=", "gte"}:
        return actual >= expected
    if operator in {"greater_than", ">", "gt"}:
        return actual > expected
    if operator in {"at_most", "<=", "lte"}:
        return actual <= expected
    if operator in {"less_than", "<", "lt"}:
        return actual < expected
    return False


def _skill_trigger_level(context: BuffGraphAdapterContext) -> Any:
    upstream_level = _first_upstream_value(context.inputs, "trigger_level")
    if upstream_level is not None:
        return upstream_level
    event = _mapping(context.prepared_context.get("event"))
    if "trigger_level" in event:
        return event["trigger_level"]
    skill = _mapping(context.prepared_context.get("skill_node"))
    if "trigger_level" in skill:
        return skill["trigger_level"]
    return context.prepared_context.get("trigger_level")


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


def _anomaly_state(context: BuffGraphAdapterContext) -> Mapping[str, Any]:
    upstream_state = _first_upstream_value(context.inputs, "anomaly_state")
    if isinstance(upstream_state, Mapping):
        return upstream_state
    return _mapping(context.prepared_context.get("enemy_anomaly_state"))


def _edge_state(context: BuffGraphAdapterContext) -> Mapping[str, Any]:
    upstream_state = _first_upstream_value(context.inputs, "edge_state")
    if isinstance(upstream_state, Mapping):
        return upstream_state
    return _mapping(context.prepared_context.get("enemy_edge_state"))


def _state_value(state: Mapping[str, Any]) -> Any:
    for key in ("state", "status", "value", "anomaly_state"):
        if key in state:
            return state[key]
    return None


def _edge_transition_passed(
    *,
    previous: Any,
    current: Any,
    transition: str,
    from_state: Any,
    to_state: Any,
) -> bool:
    if from_state is not None and previous != from_state:
        return False
    if to_state is not None and current != to_state:
        return False
    if transition in {"changed", "change"}:
        return previous != current
    if transition in {"rising", "rising_edge"}:
        return not bool(previous) and bool(current)
    if transition in {"falling", "falling_edge"}:
        return bool(previous) and not bool(current)
    if transition in {"entered", "to"}:
        return previous != current and (to_state is None or current == to_state)
    if transition in {"exited", "from"}:
        return previous != current and (from_state is None or previous == from_state)
    return False
