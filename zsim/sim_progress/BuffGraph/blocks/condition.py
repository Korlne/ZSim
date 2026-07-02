from zsim.sim_progress.BuffGraph.blocks.registry import BlockPort, BuffGraphBlockDefinition
from zsim.sim_progress.BuffGraph.spec.schema import NodeFamily


CONDITION_BLOCKS = (
    BuffGraphBlockDefinition(
        block_id="condition.character_identity",
        family=NodeFamily.CONDITION,
        display_name="Character Identity",
        adapter_id="condition.character_identity.v1",
        input_ports=(BlockPort("context", "Context", "prepared_context"),),
        output_ports=(BlockPort("result", "Result", "bool"),),
        param_schema={"character": "character_selector"},
    ),
    BuffGraphBlockDefinition(
        block_id="condition.buff_active",
        family=NodeFamily.CONDITION,
        display_name="Buff Active",
        adapter_id="condition.buff_active.v1",
        input_ports=(BlockPort("context", "Context", "prepared_context"),),
        output_ports=(BlockPort("result", "Result", "bool"),),
        param_schema={"buff_index": "string"},
    ),
)

