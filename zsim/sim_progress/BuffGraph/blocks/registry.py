from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping

from zsim.sim_progress.BuffGraph.spec.schema import (
    FORBIDDEN_NODE_FAMILIES,
    BuffGraphNode,
    NodeFamily,
)


@dataclass(frozen=True, slots=True)
class BlockPort:
    port_id: str
    display_name: str
    value_type: str = "any"


@dataclass(frozen=True, slots=True)
class BuffGraphBlockDefinition:
    block_id: str
    family: NodeFamily
    display_name: str
    adapter_id: str
    input_ports: tuple[BlockPort, ...] = ()
    output_ports: tuple[BlockPort, ...] = ()
    param_schema: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_controlled_block_text(
            block_id=self.block_id,
            adapter_id=self.adapter_id,
            family=self.family,
        )

    def create_node(
        self,
        *,
        node_id: str,
        params: Mapping[str, Any] | None = None,
    ) -> BuffGraphNode:
        return BuffGraphNode(
            node_id=node_id,
            family=self.family,
            block_id=self.block_id,
            adapter_id=self.adapter_id,
            params={} if params is None else dict(params),
            display_name=self.display_name,
        )


class BuffGraphBlockRegistry:
    def __init__(self, blocks: Iterable[BuffGraphBlockDefinition] = ()) -> None:
        self._blocks: dict[str, BuffGraphBlockDefinition] = {}
        for block in blocks:
            self.register(block)

    def register(self, block: BuffGraphBlockDefinition) -> None:
        self._validate_block(block)
        if block.block_id in self._blocks:
            raise ValueError(f"duplicate Buff graph block id: {block.block_id}")
        self._blocks[block.block_id] = block

    def get(self, block_id: str) -> BuffGraphBlockDefinition:
        try:
            return self._blocks[block_id]
        except KeyError as exc:
            raise KeyError(f"unknown Buff graph block id: {block_id}") from exc

    def all(self) -> tuple[BuffGraphBlockDefinition, ...]:
        return tuple(self._blocks.values())

    def by_family(self, family: NodeFamily) -> tuple[BuffGraphBlockDefinition, ...]:
        return tuple(block for block in self._blocks.values() if block.family == family)

    @staticmethod
    def _validate_block(block: BuffGraphBlockDefinition) -> None:
        _validate_controlled_block_text(
            block_id=block.block_id,
            adapter_id=block.adapter_id,
            family=block.family,
        )
        if not block.block_id.strip():
            raise ValueError("Buff graph block_id must be non-empty")
        if not block.adapter_id.strip():
            raise ValueError("Buff graph adapter_id must be non-empty")


def build_default_block_registry() -> BuffGraphBlockRegistry:
    from .compose import COMPOSE_BLOCKS
    from .condition import CONDITION_BLOCKS
    from .effect import EFFECT_BLOCKS
    from .read import READ_BLOCKS
    from .state import STATE_BLOCKS
    from .trigger import TRIGGER_BLOCKS

    return BuffGraphBlockRegistry(
        (
            *TRIGGER_BLOCKS,
            *CONDITION_BLOCKS,
            *READ_BLOCKS,
            *EFFECT_BLOCKS,
            *STATE_BLOCKS,
            *COMPOSE_BLOCKS,
        )
    )


def _validate_controlled_block_text(
    *,
    block_id: str,
    adapter_id: str,
    family: NodeFamily,
) -> None:
    text = f"{block_id} {adapter_id} {family.value}".lower()
    if any(token in text for token in FORBIDDEN_NODE_FAMILIES | {"eval", "exec"}):
        raise ValueError(
            "Buff graph blocks must be controlled domain blocks, not Python/script/code nodes"
        )
