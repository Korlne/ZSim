from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UnsupportedXLogicPattern:
    pattern_id: str
    reason: str
    evidence: str
