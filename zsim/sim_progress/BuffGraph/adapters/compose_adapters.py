from __future__ import annotations

from typing import Any, Mapping

from .base import BuffGraphAdapterContext, BuffGraphAdapterResult


class AllComposeAdapter:
    adapter_id = "compose.all.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        values = _upstream_booleans(context)
        return BuffGraphAdapterResult(outputs={"passed": bool(values) and all(values)})


class BranchComposeAdapter:
    adapter_id = "compose.branch.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        values = _upstream_booleans(context)
        condition = bool(values[0]) if values else False
        selected = context.node.params.get("true_value" if condition else "false_value")
        return BuffGraphAdapterResult(outputs={"condition": condition, "selected": selected})


class NotComposeAdapter:
    adapter_id = "compose.not.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        values = _upstream_booleans(context)
        value = bool(values[0]) if values else False
        return BuffGraphAdapterResult(outputs={"passed": not value})


class NumericFormulaComposeAdapter:
    adapter_id = "compose.numeric_formula.v1"

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        value = _first_upstream_number(context.inputs)
        if value is None:
            value = _number(context.node.params.get("base", 0))
        operation = str(context.node.params.get("operation", "linear"))
        subtract = _number(context.node.params.get("subtract", 0))
        multiplier = _number(context.node.params.get("multiplier", 1))
        offset = _number(context.node.params.get("offset", 0))

        if operation in {"linear", "subtract_multiply", "conversion"}:
            result = (value - subtract) * multiplier + offset
        elif operation in {"add", "offset"}:
            result = value + offset
        elif operation in {"multiply", "scale"}:
            result = value * multiplier
        elif operation in {"subtract"}:
            result = value - subtract
        else:
            result = value

        min_value = context.node.params.get("min_value")
        max_value = context.node.params.get("max_value")
        if min_value is not None:
            result = max(result, _number(min_value))
        if max_value is not None:
            result = min(result, _number(max_value))

        return BuffGraphAdapterResult(
            outputs={
                "value": result,
                "input": value,
                "operation": operation,
            }
        )


def build_low_risk_compose_adapters() -> Mapping[str, object]:
    adapters = (AllComposeAdapter(), BranchComposeAdapter(), NotComposeAdapter())
    return {adapter.adapter_id: adapter for adapter in adapters}


def build_calculator_runtime_formula_compose_adapters() -> Mapping[str, object]:
    adapters = (NumericFormulaComposeAdapter(),)
    return {adapter.adapter_id: adapter for adapter in adapters}


def _upstream_booleans(context: BuffGraphAdapterContext) -> tuple[bool, ...]:
    upstream = context.inputs.get("upstream")
    if not isinstance(upstream, Mapping):
        return ()
    values: list[bool] = []
    for output in upstream.values():
        if isinstance(output, Mapping):
            values.append(_output_bool(output))
    return tuple(values)


def _output_bool(output: Mapping[str, Any]) -> bool:
    for key in ("matched", "passed", "ready", "active"):
        if key in output:
            return bool(output[key])
    return bool(output)


def _first_upstream_number(inputs: Mapping[str, Any]) -> float | None:
    upstream = inputs.get("upstream")
    if not isinstance(upstream, Mapping):
        return None
    for output in upstream.values():
        if isinstance(output, Mapping):
            for key in ("value", "refinement", "trigger_level", "actual", "count"):
                if key in output:
                    return _number(output[key])
    return None


def _number(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
