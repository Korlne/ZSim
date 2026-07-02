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
    BuffGraphBlockDefinition(
        block_id="effect.register_listener",
        family=NodeFamily.EFFECT,
        display_name="Register Listener",
        adapter_id="effect.register_listener.v1",
        input_ports=(BlockPort("context", "Context", "prepared_context"),),
        output_ports=(BlockPort("listener_registration", "Listener Registration", "effect_result"),),
        param_schema={"listener_key": "string", "source_buff_index": "string"},
    ),
    BuffGraphBlockDefinition(
        block_id="effect.consume_listener_signal",
        family=NodeFamily.EFFECT,
        display_name="Consume Listener Signal",
        adapter_id="effect.consume_listener_signal.v1",
        input_ports=(BlockPort("listener_signal", "Listener Signal", "listener_signal"),),
        output_ports=(BlockPort("listener_consumption", "Listener Consumption", "effect_result"),),
        param_schema={"listener_key": "string", "consume": "bool"},
    ),
    BuffGraphBlockDefinition(
        block_id="effect.issue_runtime_command",
        family=NodeFamily.EFFECT,
        display_name="Issue Runtime Command Intent",
        adapter_id="effect.issue_runtime_command.v1",
        input_ports=(BlockPort("condition", "Condition", "bool"),),
        output_ports=(BlockPort("runtime_command_intent", "Runtime Command Intent", "intent"),),
        param_schema={"command_type": "string", "command_name": "string", "payload": "object"},
    ),
    BuffGraphBlockDefinition(
        block_id="effect.issue_allowed_runtime_command",
        family=NodeFamily.EFFECT,
        display_name="Issue Allowed Runtime Command Intent",
        adapter_id="effect.issue_allowed_runtime_command.v1",
        input_ports=(BlockPort("condition", "Condition", "bool"),),
        output_ports=(BlockPort("runtime_command_intent", "Runtime Command Intent", "intent"),),
        param_schema={"command_type": "string", "command_name": "string", "payload": "object"},
    ),
    BuffGraphBlockDefinition(
        block_id="effect.emit_scheduled_event",
        family=NodeFamily.EFFECT,
        display_name="Emit Scheduled Event Intent",
        adapter_id="effect.emit_scheduled_event.v1",
        input_ports=(BlockPort("condition", "Condition", "bool"),),
        output_ports=(BlockPort("scheduled_event_intent", "Scheduled Event Intent", "intent"),),
        param_schema={"event_type": "string", "scheduled_tick": "int", "payload": "object"},
    ),
)

