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
    BuffGraphBlockDefinition(
        block_id="condition.equipper_identity",
        family=NodeFamily.CONDITION,
        display_name="Equipper Identity",
        adapter_id="condition.equipper_identity.v1",
        input_ports=(BlockPort("equipper", "Equipper", "character"),),
        output_ports=(BlockPort("result", "Result", "bool"),),
        param_schema={"equipper": "character_selector"},
    ),
    BuffGraphBlockDefinition(
        block_id="condition.trigger_buff_active",
        family=NodeFamily.CONDITION,
        display_name="Trigger Buff Active",
        adapter_id="condition.trigger_buff_active.v1",
        input_ports=(BlockPort("trigger_buff_state", "Trigger Buff State", "buff_state"),),
        output_ports=(BlockPort("result", "Result", "bool"),),
        param_schema={"trigger_buff_index": "string"},
    ),
    BuffGraphBlockDefinition(
        block_id="condition.trigger_buff_box_size_equals",
        family=NodeFamily.CONDITION,
        display_name="Trigger Buff Box Size Equals",
        adapter_id="condition.trigger_buff_box_size_equals.v1",
        input_ports=(BlockPort("trigger_buff_state", "Trigger Buff State", "buff_state"),),
        output_ports=(BlockPort("result", "Result", "bool"),),
        param_schema={"expected_size": "number", "trigger_buff_index": "string"},
    ),
    BuffGraphBlockDefinition(
        block_id="condition.equipper_is_background",
        family=NodeFamily.CONDITION,
        display_name="Equipper Is Background",
        adapter_id="condition.equipper_is_background.v1",
        input_ports=(BlockPort("equipper", "Equipper", "character"),),
        output_ports=(BlockPort("result", "Result", "bool"),),
    ),
    BuffGraphBlockDefinition(
        block_id="condition.equipper_is_foreground",
        family=NodeFamily.CONDITION,
        display_name="Equipper Is Foreground",
        adapter_id="condition.equipper_is_foreground.v1",
        input_ports=(BlockPort("equipper", "Equipper", "character"),),
        output_ports=(BlockPort("result", "Result", "bool"),),
    ),
)

