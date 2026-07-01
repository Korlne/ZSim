from __future__ import annotations

from dataclasses import dataclass

from zsim.sim_progress.calculation.identities import (
    AnomalyStateIdentity,
    DamageIdentity,
    MultiplierAffinity,
)


@dataclass(frozen=True, slots=True)
class FormulaLevelContext:
    """Common level values used by formula-family snapshots."""

    source_level: int
    target_level: int


@dataclass(frozen=True, slots=True)
class FormulaSourceContext:
    """Formula source identity without a live Character, SkillNode, or runtime object."""

    source_name: str
    skill_tag: str


@dataclass(frozen=True, slots=True)
class DamageIdentityProfile:
    """Damage identity paired with the multiplier family used to read formula bonuses."""

    damage_identity: DamageIdentity
    multiplier_affinity: MultiplierAffinity


@dataclass(frozen=True, slots=True)
class AnomalyIdentityProfile:
    """Anomaly formula identity profile with damage, multiplier, and state separated."""

    damage_identity: DamageIdentity
    multiplier_affinity: MultiplierAffinity
    anomaly_state_identity: AnomalyStateIdentity
