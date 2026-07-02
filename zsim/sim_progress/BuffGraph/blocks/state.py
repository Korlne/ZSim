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
    BuffGraphBlockDefinition(
        block_id="state.scheduled_signal",
        family=NodeFamily.STATE,
        display_name="Scheduled Signal",
        adapter_id="state.scheduled_signal.v1",
        input_ports=(BlockPort("tick", "Tick", "tick"),),
        output_ports=(
            BlockPort("scheduled_signal", "Scheduled Signal", "scheduled_signal"),
            BlockPort("active", "Active", "bool"),
            BlockPort("scheduled_tick", "Scheduled Tick", "tick"),
        ),
        param_schema={"signal_key": "string", "scheduled_tick": "int"},
    ),
    BuffGraphBlockDefinition(
        block_id="state.last_observed_skill",
        family=NodeFamily.STATE,
        display_name="Last Observed Skill",
        adapter_id="state.last_observed_skill.v1",
        input_ports=(BlockPort("skill_node", "Skill Node", "skill_node"),),
        output_ports=(
            BlockPort("previous_skill", "Previous Skill", "skill_node"),
            BlockPort("current_skill", "Current Skill", "skill_node"),
            BlockPort("changed", "Changed", "bool"),
        ),
        param_schema={"state_key": "state_key"},
    ),
    BuffGraphBlockDefinition(
        block_id="state.counter",
        family=NodeFamily.STATE,
        display_name="Counter",
        adapter_id="state.counter.v1",
        input_ports=(BlockPort("active", "Active", "bool"),),
        output_ports=(
            BlockPort("count", "Count", "number"),
            BlockPort("active", "Active", "bool"),
        ),
        param_schema={"state_key": "state_key", "step": "int"},
    ),
)

