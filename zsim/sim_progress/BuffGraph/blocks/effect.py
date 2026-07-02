from zsim.sim_progress.BuffGraph.blocks.registry import BlockPort, BuffGraphBlockDefinition
from zsim.sim_progress.BuffGraph.spec.schema import NodeFamily


EFFECT_BLOCKS = (
    BuffGraphBlockDefinition(
        block_id="effect.start_buff",
        family=NodeFamily.EFFECT,
        display_name="Start Buff",
        adapter_id="effect.start_buff.v1",
        input_ports=(
            BlockPort("condition", "Condition", "bool"),
            BlockPort("context", "Context", "prepared_context"),
        ),
        output_ports=(BlockPort("result", "Result", "effect_result"),),
        param_schema={"target_buff_index": "string"},
    ),
    BuffGraphBlockDefinition(
        block_id="effect.update_buff_count",
        family=NodeFamily.EFFECT,
        display_name="Update Buff Count",
        adapter_id="effect.update_buff_count.v1",
        input_ports=(BlockPort("value", "Value", "number"),),
        output_ports=(BlockPort("result", "Result", "effect_result"),),
        param_schema={"target_buff_index": "string", "mode": "set_or_add"},
    ),
)

