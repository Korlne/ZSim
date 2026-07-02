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


def build_low_risk_compose_adapters() -> Mapping[str, object]:
    adapters = (AllComposeAdapter(), BranchComposeAdapter(), NotComposeAdapter())
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
