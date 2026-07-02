from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol

from zsim.sim_progress.BuffGraph.spec.schema import BuffGraphNode


@dataclass(frozen=True, slots=True)
class BuffGraphAdapterContext:
    graph_id: str
    node: BuffGraphNode
    inputs: Mapping[str, Any] = field(default_factory=dict)
    prepared_context: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class BuffGraphAdapterResult:
    outputs: Mapping[str, Any] = field(default_factory=dict)
    trace: Mapping[str, Any] = field(default_factory=dict)


class BuffGraphAdapter(Protocol):
    adapter_id: str

    def execute(self, context: BuffGraphAdapterContext) -> BuffGraphAdapterResult:
        """Execute one controlled Buff graph building block."""

