"""Genesis: the deterministic origin record for a local domain history."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from ._canonical import canonical_json, require_non_empty_strings

SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class Genesis:
    """Immutable origin record; it does not claim global uniqueness or trust."""

    id: str
    origin_id: str
    created_at: str
    version: int = SCHEMA_VERSION


def create_genesis(origin_id: str, created_at: str) -> Genesis:
    """Create a stable Genesis ID from the versioned canonical origin payload."""
    require_non_empty_strings(origin_id=origin_id, created_at=created_at)
    canonical = canonical_json(
        {
            "created_at": created_at,
            "origin_id": origin_id,
            "version": SCHEMA_VERSION,
        }
    )
    identifier = sha256(canonical.encode("utf-8")).hexdigest()
    return Genesis(
        id=identifier,
        origin_id=origin_id,
        created_at=created_at,
    )
