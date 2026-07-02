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
    BuffGraphBlockDefinition(
        block_id="state.last_observed_enemy_state",
        family=NodeFamily.STATE,
        display_name="Last Observed Enemy State",
        adapter_id="state.last_observed_enemy_state.v1",
        input_ports=(BlockPort("anomaly_state", "Anomaly State", "enemy_anomaly_state"),),
        output_ports=(
            BlockPort("previous_state", "Previous State", "any"),
            BlockPort("current_state", "Current State", "any"),
            BlockPort("changed", "Changed", "bool"),
        ),
        param_schema={"state_key": "state_key"},
    ),
    BuffGraphBlockDefinition(
        block_id="state.edge_memory",
        family=NodeFamily.STATE,
        display_name="Edge Memory",
        adapter_id="state.edge_memory.v1",
        input_ports=(BlockPort("current", "Current", "any"),),
        output_ports=(
            BlockPort("previous", "Previous", "any"),
            BlockPort("current", "Current", "any"),
            BlockPort("rising_edge", "Rising Edge", "bool"),
            BlockPort("falling_edge", "Falling Edge", "bool"),
            BlockPort("changed", "Changed", "bool"),
        ),
        param_schema={"state_key": "state_key"},
    ),
    BuffGraphBlockDefinition(
        block_id="state.anomaly_signal",
        family=NodeFamily.STATE,
        display_name="Anomaly Signal",
        adapter_id="state.anomaly_signal.v1",
        input_ports=(BlockPort("anomaly_state", "Anomaly State", "enemy_anomaly_state"),),
        output_ports=(
            BlockPort("anomaly_signal", "Anomaly Signal", "anomaly_signal"),
            BlockPort("active", "Active", "bool"),
        ),
        param_schema={"signal_key": "string"},
    ),
)

