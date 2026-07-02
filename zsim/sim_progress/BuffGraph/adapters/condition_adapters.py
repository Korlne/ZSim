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


class EnemyStunActiveConditionAdapter:
    adapter_id = "condition.enemy_stun_active.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        active = _first_upstream_value(context.inputs, "active")
        if active is None:
            stun_state = _mapping(_first_upstream_value(context.inputs, "enemy_stun_state"))
            active = stun_state.get("active")
        if active is None:
            active = context.prepared_context.get("enemy_stun_active", False)
        expected_active = context.node.params.get("active", True)
        passed = bool(active) is bool(expected_active)
        return BuffGraphAdapterResult(
            outputs={
                "passed": passed,
                "active": bool(active),
                "expected_active": bool(expected_active),
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


class HitFrameConditionAdapter:
    adapter_id = "condition.hit_frame.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        skill_node = _skill_node(context)
        hit_index = skill_node.get("hit_index", skill_node.get("hit"))
        expected_hit_index = context.node.params.get("expected_hit_index")
        require_last_hit = bool(context.node.params.get("require_last_hit", False))
        is_last_hit = bool(
            skill_node.get("is_last_hit")
            or skill_node.get("last_hit")
            or skill_node.get("hit_is_last")
        )
        passed = expected_hit_index is None or int(hit_index or -1) == int(expected_hit_index)
        if require_last_hit:
            passed = passed and is_last_hit
        return BuffGraphAdapterResult(
            outputs={
                "passed": passed,
                "hit_index": hit_index,
                "is_last_hit": is_last_hit,
            }
        )


class SkillTagInConditionAdapter:
    adapter_id = "condition.skill_tag_in.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        skill_node = _skill_node(context)
        skill_tag = skill_node.get("skill_tag") or skill_node.get("tag")
        expected_tags = context.node.params.get("skill_tags", ())
        if isinstance(expected_tags, str):
            expected_tags = (expected_tags,)
        passed = not expected_tags or skill_tag in set(expected_tags)
        return BuffGraphAdapterResult(outputs={"passed": passed, "skill_tag": skill_tag})


class SkillOwnerNotSelfConditionAdapter:
    adapter_id = "condition.skill_owner_not_self.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        skill_owner = _skill_owner(context)
        self_owner = (
            context.node.params.get("self_owner")
            or context.prepared_context.get("prepared_owner")
            or context.prepared_context.get("owner")
            or context.prepared_context.get("owner_name")
        )
        return BuffGraphAdapterResult(
            outputs={
                "passed": skill_owner is not None and skill_owner != self_owner,
                "skill_owner": skill_owner,
                "self_owner": self_owner,
            }
        )


class OperatingCharacterConditionAdapter:
    adapter_id = "condition.operating_character.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        expected = context.node.params.get("character")
        actual = _first_upstream_value(context.inputs, "character")
        if actual is None:
            actual = context.prepared_context.get("operating_character")
        if actual is None:
            actual = context.prepared_context.get("foreground_character")
        return BuffGraphAdapterResult(
            outputs={"passed": expected is None or actual == expected, "character": actual}
        )


class SkillOwnerConditionAdapter:
    adapter_id = "condition.skill_owner.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        expected = context.node.params.get("owner")
        skill_owner = _skill_owner(context)
        return BuffGraphAdapterResult(
            outputs={
                "passed": expected is None or skill_owner == expected,
                "skill_owner": skill_owner,
            }
        )


class CharacterStateConditionAdapter:
    adapter_id = "condition.character_state.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        character = (
            context.node.params.get("character")
            or _first_upstream_value(context.inputs, "character")
            or context.prepared_context.get("prepared_owner")
            or context.prepared_context.get("owner")
            or context.prepared_context.get("owner_name")
        )
        state_key = context.node.params.get("state_key")
        state_value = _character_state(context.prepared_context, character, state_key)
        expected_value = context.node.params.get("expected_value")
        passed = expected_value is None or state_value == expected_value
        return BuffGraphAdapterResult(
            outputs={
                "passed": passed,
                "character": character,
                "state_key": state_key,
                "state_value": state_value,
            }
        )


class CooldownReadyConditionAdapter:
    adapter_id = "condition.cooldown_ready.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        tick = _current_tick(context)
        cooldown_key = context.node.params.get("cooldown_key") or context.node.node_id
        cooldown_ticks = int(context.node.params.get("cooldown_ticks", 0))
        operator = str(context.node.params.get("operator", ">="))
        cooldowns = _mapping(context.prepared_context.get("cooldowns"))
        last_tick = cooldowns.get(cooldown_key)
        if last_tick is None:
            last_tick = _state(context).get(cooldown_key)
        elapsed = None if last_tick is None else tick - int(last_tick)
        ready = last_tick is None or _compare_float(float(elapsed), float(cooldown_ticks), operator)
        return BuffGraphAdapterResult(
            outputs={
                "passed": ready,
                "tick": tick,
                "cooldown_key": cooldown_key,
                "last_tick": last_tick,
                "elapsed": elapsed,
                "operator": operator,
            }
        )


class PreloadTickConditionAdapter:
    adapter_id = "condition.preload_tick.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        tick = _current_tick(context)
        expected_tick = int(context.node.params.get("expected_tick", tick))
        window_ticks = int(context.node.params.get("window_ticks", 0))
        passed = abs(tick - expected_tick) <= window_ticks
        return BuffGraphAdapterResult(
            outputs={"passed": passed, "tick": tick, "expected_tick": expected_tick}
        )


class NumericCompareConditionAdapter:
    adapter_id = "condition.numeric_compare.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        actual = _first_upstream_number(context.inputs)
        if actual is None:
            actual = _number(context.node.params.get("actual", 0))
        expected = _number(
            context.node.params.get("expected", context.node.params.get("threshold", 0))
        )
        operator = str(context.node.params.get("operator", ">="))
        passed = _compare_float(actual, expected, operator)
        return BuffGraphAdapterResult(
            outputs={
                "passed": passed,
                "actual": actual,
                "expected": expected,
                "operator": operator,
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
    adapters = (
        EnemyStateConditionAdapter(),
        EnemyStunActiveConditionAdapter(),
        EdgeTransitionConditionAdapter(),
    )
    return {adapter.adapter_id: adapter for adapter in adapters}


def build_runtime_command_scheduled_signal_condition_adapters() -> Mapping[str, object]:
    adapters = (TickWindowConditionAdapter(),)
    return {adapter.adapter_id: adapter for adapter in adapters}


def build_character_manager_side_effect_condition_adapters() -> Mapping[str, object]:
    adapters = (
        HitFrameConditionAdapter(),
        SkillTagInConditionAdapter(),
        SkillOwnerNotSelfConditionAdapter(),
        OperatingCharacterConditionAdapter(),
        SkillOwnerConditionAdapter(),
        CharacterStateConditionAdapter(),
        CooldownReadyConditionAdapter(),
        PreloadTickConditionAdapter(),
    )
    return {adapter.adapter_id: adapter for adapter in adapters}


def build_calculator_runtime_formula_condition_adapters() -> Mapping[str, object]:
    adapters = (NumericCompareConditionAdapter(),)
    return {adapter.adapter_id: adapter for adapter in adapters}


def build_yuzuha_cinema2_qte_signal_condition_adapters() -> Mapping[str, object]:
    adapters = (
        EnemyStunActiveConditionAdapter(),
        HitFrameConditionAdapter(),
        SkillTagInConditionAdapter(),
        CooldownReadyConditionAdapter(),
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


def _compare_float(actual: float, expected: float, operator: str) -> bool:
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


def _first_upstream_number(inputs: Mapping[str, Any]) -> float | None:
    upstream = _mapping(inputs.get("upstream"))
    for output in upstream.values():
        mapped_output = _mapping(output)
        for key in ("value", "refinement", "trigger_level", "actual", "count"):
            if key in mapped_output:
                return _number(mapped_output[key])
    return None


def _number(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


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


def _skill_node(context: BuffGraphAdapterContext) -> Mapping[str, Any]:
    upstream_node = _first_upstream_value(context.inputs, "skill_node")
    if isinstance(upstream_node, Mapping):
        return upstream_node
    return _mapping(
        context.prepared_context.get("skill_node")
        or context.prepared_context.get("current_skill")
    )


def _skill_owner(context: BuffGraphAdapterContext) -> Any:
    skill_node = _skill_node(context)
    return (
        skill_node.get("owner")
        or skill_node.get("owner_name")
        or skill_node.get("character")
        or skill_node.get("character_name")
        or context.prepared_context.get("skill_owner")
    )


def _character_state(
    prepared_context: Mapping[str, Any],
    character: Any,
    state_key: Any,
) -> Any:
    states = _mapping(prepared_context.get("character_states"))
    character_state = _mapping(states.get(character)) if character is not None else {}
    if not character_state:
        character_state = _mapping(prepared_context.get("character_state"))
    if state_key is None:
        return character_state
    return character_state.get(state_key)


def _current_tick(context: BuffGraphAdapterContext) -> int:
    tick = _first_upstream_value(context.inputs, "tick")
    if tick is None:
        tick = context.prepared_context.get("tick", 0)
    return int(tick)


def _state(context: BuffGraphAdapterContext) -> Mapping[str, Any]:
    return _mapping(context.prepared_context.get("state"))


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
