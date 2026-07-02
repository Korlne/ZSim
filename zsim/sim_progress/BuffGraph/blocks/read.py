from zsim.sim_progress.BuffGraph.blocks.registry import BlockPort, BuffGraphBlockDefinition
from zsim.sim_progress.BuffGraph.spec.schema import NodeFamily


READ_BLOCKS = (
    BuffGraphBlockDefinition(
        block_id="read.current_tick",
        family=NodeFamily.READ,
        display_name="Current Tick",
        adapter_id="read.current_tick.v1",
        input_ports=(),
        output_ports=(BlockPort("tick", "Tick", "tick"),),
    ),
    BuffGraphBlockDefinition(
        block_id="read.buff_runtime_view",
        family=NodeFamily.READ,
        display_name="Buff Runtime View",
        adapter_id="read.buff_runtime_view.v1",
        input_ports=(BlockPort("context", "Context", "prepared_context"),),
        output_ports=(BlockPort("value", "Value", "buff_state"),),
        param_schema={"field": "buff_runtime_field"},
    ),
    BuffGraphBlockDefinition(
        block_id="read.prepared_owner",
        family=NodeFamily.READ,
        display_name="Prepared Owner",
        adapter_id="read.prepared_owner.v1",
        input_ports=(BlockPort("context", "Context", "prepared_context"),),
        output_ports=(BlockPort("owner", "Owner", "character"),),
    ),
    BuffGraphBlockDefinition(
        block_id="read.prepared_equipper",
        family=NodeFamily.READ,
        display_name="Prepared Equipper",
        adapter_id="read.prepared_equipper.v1",
        input_ports=(BlockPort("context", "Context", "prepared_context"),),
        output_ports=(BlockPort("equipper", "Equipper", "character"),),
    ),
    BuffGraphBlockDefinition(
        block_id="read.prepared_template_buff",
        family=NodeFamily.READ,
        display_name="Prepared Template Buff",
        adapter_id="read.prepared_template_buff.v1",
        input_ports=(BlockPort("context", "Context", "prepared_context"),),
        output_ports=(BlockPort("template_buff", "Template Buff", "buff_template"),),
        param_schema={"template_buff_index": "string"},
    ),
    BuffGraphBlockDefinition(
        block_id="read.trigger_buff_state",
        family=NodeFamily.READ,
        display_name="Trigger Buff State",
        adapter_id="read.trigger_buff_state.v1",
        input_ports=(BlockPort("context", "Context", "prepared_context"),),
        output_ports=(
            BlockPort("trigger_buff_state", "Trigger Buff State", "buff_state"),
            BlockPort("active", "Active", "bool"),
            BlockPort("count", "Count", "number"),
            BlockPort("built_in_buff_box_size", "Built-In Buff Box Size", "number"),
        ),
        param_schema={"trigger_buff_index": "string"},
    ),
    BuffGraphBlockDefinition(
        block_id="read.foreground_character",
        family=NodeFamily.READ,
        display_name="Foreground Character",
        adapter_id="read.foreground_character.v1",
        input_ports=(BlockPort("context", "Context", "prepared_context"),),
        output_ports=(BlockPort("character", "Character", "character"),),
    ),
)

