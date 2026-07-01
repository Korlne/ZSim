from __future__ import annotations

from dataclasses import dataclass

from zsim.sim_progress.calculation.inputs.common import AnomalyIdentityProfile


@dataclass(frozen=True, slots=True)
class AnomalyDamageSnapshot:
    """Legacy anomaly damage snapshot values needed by anomaly damage formulas."""

    base_damage: float
    damage_bonus: float
    anomaly_mastery_multiplier: float
    anomaly_damage_bonus: float
    snapshot_impact: float
    snapshot_stun_bonus: float


@dataclass(frozen=True, slots=True)
class AnomalyDamageMultipliers:
    """Explicit non-snapshot multipliers assembled outside runtime-bound formulas."""

    level_multiplier: float
    active_crit_multiplier: float
    defense_multiplier: float
    resistance_multiplier: float
    vulnerability_multiplier: float
    stun_vulnerability_multiplier: float
    special_multiplier: float


@dataclass(frozen=True, slots=True)
class AnomalyDamageInput:
    """Read-only input snapshot for one anomaly damage calculation."""

    identity: AnomalyIdentityProfile
    snapshot: AnomalyDamageSnapshot
    multipliers: AnomalyDamageMultipliers
    scaling_factor: float


__all__ = [
    "AnomalyDamageInput",
    "AnomalyDamageMultipliers",
    "AnomalyDamageSnapshot",
]
