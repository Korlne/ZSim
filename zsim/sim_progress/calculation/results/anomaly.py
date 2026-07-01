from __future__ import annotations

from dataclasses import dataclass

from zsim.sim_progress.calculation.inputs.common import AnomalyIdentityProfile
from zsim.sim_progress.calculation.results.common import MultiplierVector


@dataclass(frozen=True, slots=True)
class AnomalyDamageResult:
    """Scalar anomaly damage output with multiplier evidence."""

    value: float
    identity: AnomalyIdentityProfile
    multipliers: MultiplierVector
    scaling_factor: float
    cancelled_snapshot_impact: float
    cancelled_snapshot_stun_bonus: float


__all__ = [
    "AnomalyDamageResult",
]
