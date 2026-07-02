from zsim.sim_progress.BuffGraph.blocks.registry import BlockPort, BuffGraphBlockDefinition
from zsim.sim_progress.BuffGraph.spec.schema import NodeFamily


TRIGGER_BLOCKS = (
    BuffGraphBlockDefinition(
        block_id="trigger.skill_hit",
        family=NodeFamily.TRIGGER,
        display_name="Skill Hit",
        adapter_id="trigger.skill_hit.v1",
        input_ports=(),
        output_ports=(BlockPort("event", "Event", "skill_event"),),
        param_schema={"skill_tag": "string", "hit_window": "optional_tick_range"},
    ),
    BuffGraphBlockDefinition(
        block_id="trigger.buff_refresh",
        family=NodeFamily.TRIGGER,
        display_name="Buff Refresh",
        adapter_id="trigger.buff_refresh.v1",
        input_ports=(),
        output_ports=(BlockPort("event", "Event", "buff_event"),),
        param_schema={"buff_index": "string"},
    ),
)

