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
    BuffGraphBlockDefinition(
        block_id="effect.update_template_buff",
        family=NodeFamily.EFFECT,
        display_name="Update Template Buff",
        adapter_id="effect.update_template_buff.v1",
        input_ports=(
            BlockPort("template_buff", "Template Buff", "buff_template"),
            BlockPort("condition", "Condition", "bool"),
        ),
        output_ports=(BlockPort("result", "Result", "effect_result"),),
        param_schema={"template_buff_index": "string", "mode": "set_or_add"},
    ),
    BuffGraphBlockDefinition(
        block_id="effect.bind_prepared_record",
        family=NodeFamily.EFFECT,
        display_name="Bind Prepared Record",
        adapter_id="effect.bind_prepared_record.v1",
        input_ports=(BlockPort("context", "Context", "prepared_context"),),
        output_ports=(BlockPort("binding", "Binding", "prepared_record_binding"),),
        param_schema={"record_key": "string"},
    ),
)

