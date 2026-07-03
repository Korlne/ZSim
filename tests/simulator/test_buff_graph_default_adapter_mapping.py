from __future__ import annotations

import json
from pathlib import Path

from zsim.sim_progress.BuffGraph.adapters import build_default_adapter_mapping
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.runtime.activation import _spec_from_mapping
from zsim.sim_progress.BuffGraph.runtime.compiler import compile_buff_graph_spec


GENERATED_SPECS_ROOT = Path("zsim/sim_progress/BuffGraph/generated_specs")


def test_default_adapter_mapping_covers_default_block_registry() -> None:
    registry = build_default_block_registry()
    adapters = build_default_adapter_mapping()

    required_adapter_ids = {block.adapter_id for block in registry.all()}

    assert set(adapters) == required_adapter_ids
    for adapter_id, adapter in adapters.items():
        assert adapter_id == adapter.adapter_id
        assert callable(adapter.execute)
        assert _forbidden_node_token(adapter_id) is None


def test_default_adapter_mapping_covers_all_generated_specs() -> None:
    registry = build_default_block_registry()
    adapters = build_default_adapter_mapping()
    spec_paths = sorted(GENERATED_SPECS_ROOT.glob("*/*.buffgraph.json"))
    missing_by_spec: list[dict[str, object]] = []

    for path in spec_paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        spec = _spec_from_mapping(payload["spec"])
        compile_result = compile_buff_graph_spec(spec, block_registry=registry)
        required_adapter_ids = {node.adapter_id for node in spec.nodes}
        missing_adapter_ids = sorted(required_adapter_ids - set(adapters))
        if not compile_result.passed or missing_adapter_ids:
            missing_by_spec.append(
                {
                    "path": path.as_posix(),
                    "compile_errors": [
                        {
                            "code": error.code,
                            "message": error.message,
                            "path": error.path,
                        }
                        for error in compile_result.errors
                    ],
                    "missing_adapter_ids": missing_adapter_ids,
                }
            )

    assert len(spec_paths) == 150
    assert missing_by_spec == []


def _forbidden_node_token(value: str) -> str | None:
    text = value.lower()
    for token in ("python", "script", "code", "eval", "exec"):
        if token in text:
            return token
    return None
