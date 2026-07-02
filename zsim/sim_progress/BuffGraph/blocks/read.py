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
)

