from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from zsim.sim_progress.calculation.inputs.common import (
    AnomalyIdentityProfile,
    DamageIdentityProfile,
)


@dataclass(frozen=True, slots=True, init=False)
class MultiplierVector:
    """Read-only multiplier labels and values returned by formula-family modules."""

    values: tuple[float, ...]
    labels: tuple[str, ...] = ()

    def __init__(
        self,
        values: Iterable[float],
        labels: Iterable[str] = (),
    ) -> None:
        object.__setattr__(self, "values", tuple(values))
        object.__setattr__(self, "labels", tuple(labels))
        if self.labels and len(self.labels) != len(self.values):
            raise ValueError("MultiplierVector labels must match values length")


@dataclass(frozen=True, slots=True)
class DamageScalarResult:
    """Scalar damage output with identity and multiplier evidence attached."""

    value: float
    identity: DamageIdentityProfile
    multipliers: MultiplierVector = field(default_factory=lambda: MultiplierVector(()))


@dataclass(frozen=True, slots=True)
class AnomalyScalarResult:
    """Scalar anomaly output with separated damage, affinity, and state identity."""

    value: float
    identity: AnomalyIdentityProfile
    multipliers: MultiplierVector = field(default_factory=lambda: MultiplierVector(()))
