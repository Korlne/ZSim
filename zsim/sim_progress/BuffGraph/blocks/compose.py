from zsim.sim_progress.BuffGraph.blocks.registry import BlockPort, BuffGraphBlockDefinition
from zsim.sim_progress.BuffGraph.spec.schema import NodeFamily


COMPOSE_BLOCKS = (
    BuffGraphBlockDefinition(
        block_id="compose.all",
        family=NodeFamily.COMPOSE,
        display_name="All Conditions",
        adapter_id="compose.all.v1",
        input_ports=(BlockPort("conditions", "Conditions", "bool_list"),),
        output_ports=(BlockPort("result", "Result", "bool"),),
    ),
    BuffGraphBlockDefinition(
        block_id="compose.branch",
        family=NodeFamily.COMPOSE,
        display_name="Branch",
        adapter_id="compose.branch.v1",
        input_ports=(BlockPort("condition", "Condition", "bool"),),
        output_ports=(
            BlockPort("true", "True", "control"),
            BlockPort("false", "False", "control"),
        ),
    ),
    BuffGraphBlockDefinition(
        block_id="compose.not",
        family=NodeFamily.COMPOSE,
        display_name="Not",
        adapter_id="compose.not.v1",
        input_ports=(BlockPort("condition", "Condition", "bool"),),
        output_ports=(BlockPort("result", "Result", "bool"),),
    ),
    BuffGraphBlockDefinition(
        block_id="compose.numeric_formula",
        family=NodeFamily.COMPOSE,
        display_name="Numeric Formula",
        adapter_id="compose.numeric_formula.v1",
        input_ports=(BlockPort("value", "Value", "number"),),
        output_ports=(BlockPort("value", "Value", "number"),),
        param_schema={
            "operation": "numeric_formula_operation",
            "subtract": "number",
            "multiplier": "number",
            "offset": "number",
            "min_value": "number",
            "max_value": "number",
        },
    ),
)

