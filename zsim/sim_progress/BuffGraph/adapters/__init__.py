from collections.abc import Mapping

from .base import BuffGraphAdapter, BuffGraphAdapterContext, BuffGraphAdapterResult
from .compose_adapters import (
    build_calculator_runtime_formula_compose_adapters,
    build_low_risk_compose_adapters,
)
from .condition_adapters import (
    build_calculator_runtime_formula_condition_adapters,
    build_character_manager_side_effect_condition_adapters,
    build_enemy_anomaly_state_condition_adapters,
    build_low_risk_condition_adapters,
    build_prepared_context_condition_adapters,
    build_runtime_command_scheduled_signal_condition_adapters,
    build_yuzuha_cinema2_qte_signal_condition_adapters,
)
from .effect_adapters import (
    build_active_buffs_listener_effect_adapters,
    build_calculator_runtime_formula_effect_adapters,
    build_character_manager_side_effect_effect_adapters,
    build_dot_anomaly_output_effect_adapters,
    build_low_risk_effect_adapters,
    build_prepared_context_effect_adapters,
    build_runtime_command_scheduled_signal_effect_adapters,
    build_yuzuha_cinema2_qte_signal_effect_adapters,
)
from .read_adapters import (
    build_active_buffs_listener_read_adapters,
    build_calculator_runtime_formula_read_adapters,
    build_character_manager_side_effect_read_adapters,
    build_enemy_anomaly_state_read_adapters,
    build_low_risk_read_adapters,
    build_prepared_context_read_adapters,
    build_runtime_command_scheduled_signal_read_adapters,
    build_yuzuha_cinema2_qte_signal_read_adapters,
)
from .state_adapters import (
    build_character_manager_side_effect_state_adapters,
    build_dot_anomaly_output_state_adapters,
    build_enemy_anomaly_state_state_adapters,
    build_low_risk_state_adapters,
    build_runtime_command_scheduled_signal_state_adapters,
    build_yuzuha_cinema2_qte_signal_state_adapters,
)
from .trigger_adapters import build_low_risk_trigger_adapters


def build_default_adapter_mapping() -> Mapping[str, BuffGraphAdapter]:
    adapters: dict[str, BuffGraphAdapter] = {}
    for group in (
        build_low_risk_trigger_adapters(),
        build_low_risk_condition_adapters(),
        build_prepared_context_condition_adapters(),
        build_enemy_anomaly_state_condition_adapters(),
        build_runtime_command_scheduled_signal_condition_adapters(),
        build_character_manager_side_effect_condition_adapters(),
        build_calculator_runtime_formula_condition_adapters(),
        build_yuzuha_cinema2_qte_signal_condition_adapters(),
        build_low_risk_read_adapters(),
        build_prepared_context_read_adapters(),
        build_active_buffs_listener_read_adapters(),
        build_enemy_anomaly_state_read_adapters(),
        build_runtime_command_scheduled_signal_read_adapters(),
        build_character_manager_side_effect_read_adapters(),
        build_calculator_runtime_formula_read_adapters(),
        build_yuzuha_cinema2_qte_signal_read_adapters(),
        build_low_risk_effect_adapters(),
        build_prepared_context_effect_adapters(),
        build_active_buffs_listener_effect_adapters(),
        build_runtime_command_scheduled_signal_effect_adapters(),
        build_character_manager_side_effect_effect_adapters(),
        build_dot_anomaly_output_effect_adapters(),
        build_calculator_runtime_formula_effect_adapters(),
        build_yuzuha_cinema2_qte_signal_effect_adapters(),
        build_low_risk_state_adapters(),
        build_enemy_anomaly_state_state_adapters(),
        build_runtime_command_scheduled_signal_state_adapters(),
        build_character_manager_side_effect_state_adapters(),
        build_dot_anomaly_output_state_adapters(),
        build_yuzuha_cinema2_qte_signal_state_adapters(),
        build_low_risk_compose_adapters(),
        build_calculator_runtime_formula_compose_adapters(),
    ):
        adapters.update(group)
    return adapters

__all__ = [
    "BuffGraphAdapter",
    "BuffGraphAdapterContext",
    "BuffGraphAdapterResult",
    "build_default_adapter_mapping",
]

