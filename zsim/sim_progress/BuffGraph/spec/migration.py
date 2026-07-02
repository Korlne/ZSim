from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BuffGraphMigrationStatus:
    source_schema_version: str
    target_schema_version: str
    migrated: bool
    parity_stale: bool
    summary: str


def no_migration_needed(schema_version: str) -> BuffGraphMigrationStatus:
    return BuffGraphMigrationStatus(
        source_schema_version=schema_version,
        target_schema_version=schema_version,
        migrated=False,
        parity_stale=False,
        summary="schema version already current",
    )

