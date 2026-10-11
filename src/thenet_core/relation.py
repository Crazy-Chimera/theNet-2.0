"""Relation: an immutable, directed relation between two identified subjects."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from ._canonical import canonical_json, require_non_empty_strings

SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class Relation:
    id: str
    source_id: str
    target_id: str
    kind: str
    created_at: str
    version: int = SCHEMA_VERSION


def create_relation(
    source_id: str,
    target_id: str,
    kind: str,
    created_at: str,
) -> Relation:
    """Create a deterministic directed relation from validated fields."""
    require_non_empty_strings(
        source_id=source_id,
        target_id=target_id,
        kind=kind,
        created_at=created_at,
    )
    canonical = canonical_json(
        {
            "created_at": created_at,
            "kind": kind,
            "source_id": source_id,
            "target_id": target_id,
            "version": SCHEMA_VERSION,
        }
    )
    identifier = sha256(canonical.encode("utf-8")).hexdigest()
    return Relation(
        id=identifier,
        source_id=source_id,
        target_id=target_id,
        kind=kind,
        created_at=created_at,
    )
