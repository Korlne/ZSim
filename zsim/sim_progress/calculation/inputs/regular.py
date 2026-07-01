from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from zsim.sim_progress.calculation.identities import (
    ELECTRIC_AFFINITY,
    ETHER_AFFINITY,
    FIRE_AFFINITY,
    ICE_AFFINITY,
    PHYSICAL_AFFINITY,
    MultiplierAffinity,
)
from zsim.sim_progress.calculation.inputs.common import DamageIdentityProfile


@dataclass(frozen=True, slots=True, init=False)
class AffinityValueMap:
    """Read-only multiplier-affinity keyed numeric values."""

    values: tuple[tuple[MultiplierAffinity, float], ...]

    def __init__(
        self,
        values: Mapping[MultiplierAffinity, float]
        | Iterable[tuple[MultiplierAffinity, float]],
    ) -> None:
        object.__setattr__(
            self,
            "values",
            tuple(values.items() if isinstance(values, Mapping) else values),
        )

    def get(self, affinity: MultiplierAffinity, default: float = 0.0) -> float:
        for current_affinity, value in self.values:
            if current_affinity == affinity:
                return value
        return default


@dataclass(frozen=True, slots=True)
class RegularBaseAttributeInput:
    """Read-only scalar inputs for regular base attribute and base damage math."""

    damage_ratio: float
    hit_times: float
    diff_multiplier: int
    attack: float
    field_attack_percentage: float
    flat_attack: float
    hp: float
    field_hp_percentage: float
    flat_hp: float
    defense: float
    field_defense_percentage: float
    flat_defense: float
    anomaly_proficiency: float
    field_anomaly_proficiency: float
    flat_anomaly_proficiency: float
    extra_damage_ratio: float
    base_damage_increase_percentage: float
    base_damage_increase: float
    sheer_attack_conversion_rates: tuple[tuple[int, float], ...] = ()
    field_sheer_attack_percentage: float = 0.0
    flat_sheer_attack: float = 0.0


@dataclass(frozen=True, slots=True)
class RegularDamageBonusInput:
    """Read-only scalar inputs for the regular damage bonus multiplier."""

    identity: DamageIdentityProfile
    static_damage_bonuses: AffinityValueMap
    dynamic_damage_bonuses: AffinityValueMap
    trigger_buff_level: int
    trigger_damage_bonuses: tuple[float, ...]
    all_damage_bonus: float
    aftershock_attack: bool = False
    aftershock_attack_damage_bonus: float = 0.0


@dataclass(frozen=True, slots=True)
class RegularCritInput:
    """Read-only crit-rate and crit-damage inputs for regular damage."""

    static_crit_rate: float
    dynamic_crit_rate: float
    field_crit_rate: float
    crit_rate_received_increase: float
    static_crit_damage: float
    dynamic_crit_damage: float
    field_crit_damage: float
    received_crit_damage_bonus: float
    aftershock_attack: bool = False
    aftershock_attack_crit_damage_bonus: float = 0.0


@dataclass(frozen=True, slots=True)
class RegularDamageMultipliers:
    """Fully assembled regular damage multipliers in legacy vector order."""

    base_damage: float
    damage_bonus: float
    crit_rate: float
    crit_damage: float
    crit_expectation: float
    defense_multiplier: float
    resistance_multiplier: float
    damage_vulnerability_multiplier: float
    stun_vulnerability_multiplier: float
    special_multiplier: float
    sheer_damage_bonus: float


@dataclass(frozen=True, slots=True)
class RegularDamageInput:
    """Read-only input snapshot for one regular damage product."""

    identity: DamageIdentityProfile
    multipliers: RegularDamageMultipliers


@dataclass(frozen=True, slots=True)
class DefenseMultiplierInput:
    """Read-only inputs for regular defense-zone helpers."""

    max_defense: float
    percentage_defense_reduction: float
    flat_defense_reduction: float
    static_pen_ratio: float
    dynamic_pen_ratio: float
    static_pen_numeric: float
    dynamic_pen_numeric: float
    base_attribute: int
    attacker_level: int


@dataclass(frozen=True, slots=True)
class ResistanceMultiplierInput:
    """Read-only inputs for regular resistance-zone helpers."""

    affinity: MultiplierAffinity
    target_resistances: AffinityValueMap
    damage_resistance_decreases: AffinityValueMap
    resistance_penetrations: AffinityValueMap
    all_damage_resistance_decrease: float
    all_resistance_penetration: float
    snapshot_resistance_penetration: float = 0.0


@dataclass(frozen=True, slots=True)
class DamageVulnerabilityInput:
    """Read-only inputs for elemental vulnerability-zone helpers."""

    affinity: MultiplierAffinity
    damage_vulnerabilities: AffinityValueMap
    all_vulnerability: float


@dataclass(frozen=True, slots=True)
class StunVulnerabilityInput:
    """Read-only inputs for stun vulnerability-zone helpers."""

    is_stunned: bool
    stun_damage_taken_ratio: float
    stun_vulnerability_increase: float
    stun_vulnerability_increase_all_time: float


@dataclass(frozen=True, slots=True)
class SpecialMultiplierInput:
    """Read-only inputs for special and sheer multiplier helpers."""

    special_multiplier_zone: float
    diff_multiplier: int
    sheer_damage_bonus: float


def multiplier_affinity_from_regular_element_type(element_type: int) -> MultiplierAffinity:
    """Map current legacy regular-damage element_type values to multiplier affinity."""

    if element_type == 0:
        return PHYSICAL_AFFINITY
    if element_type == 1:
        return FIRE_AFFINITY
    if element_type in (2, 5):
        return ICE_AFFINITY
    if element_type == 3:
        return ELECTRIC_AFFINITY
    if element_type in (4, 6):
        return ETHER_AFFINITY
    raise ValueError(
        f"Invalid regular element_type: {element_type}, must be an integer in 0..6"
    )


__all__ = [
    "AffinityValueMap",
    "DamageVulnerabilityInput",
    "DefenseMultiplierInput",
    "RegularBaseAttributeInput",
    "RegularCritInput",
    "RegularDamageBonusInput",
    "RegularDamageInput",
    "RegularDamageMultipliers",
    "ResistanceMultiplierInput",
    "SpecialMultiplierInput",
    "StunVulnerabilityInput",
    "multiplier_affinity_from_regular_element_type",
]
