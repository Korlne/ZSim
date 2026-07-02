from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class BuffGraphViewport:
    x: float = 0.0
    y: float = 0.0
    zoom: float = 1.0


@dataclass(frozen=True, slots=True)
class BuffGraphNodeViewState:
    node_id: str
    x: float
    y: float
    collapsed: bool = False
    annotations: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class BuffGraphViewState:
    graph_id: str
    viewport: BuffGraphViewport = field(default_factory=BuffGraphViewport)
    nodes: tuple[BuffGraphNodeViewState, ...] = ()
    layout_hints: Mapping[str, Any] = field(default_factory=dict)
    editor_preferences: Mapping[str, Any] = field(default_factory=dict)

