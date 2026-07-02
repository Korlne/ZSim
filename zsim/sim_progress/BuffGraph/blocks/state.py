from zsim.sim_progress.BuffGraph.blocks.registry import BlockPort, BuffGraphBlockDefinition
from zsim.sim_progress.BuffGraph.spec.schema import NodeFamily


STATE_BLOCKS = (
    BuffGraphBlockDefinition(
        block_id="state.last_active_tick",
        family=NodeFamily.STATE,
        display_name="Last Active Tick",
        adapter_id="state.last_active_tick.v1",
        input_ports=(BlockPort("tick", "Tick", "tick"),),
        output_ports=(BlockPort("previous", "Previous", "tick"),),
        param_schema={"key": "state_key"},
    ),
    BuffGraphBlockDefinition(
        block_id="state.cooldown_gate",
        family=NodeFamily.STATE,
        display_name="Cooldown Gate",
        adapter_id="state.cooldown_gate.v1",
        input_ports=(BlockPort("tick", "Tick", "tick"),),
        output_ports=(BlockPort("ready", "Ready", "bool"),),
        param_schema={"cooldown_ticks": "int"},
    ),
)

