"""AgentState: an immutable state anchored to a Genesis identity."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from ._canonical import canonical_json, require_non_empty_strings
from .genesis import SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class AgentState:
    id: str
    subject_id: str
    genesis_id: str
    created_at: str
    version: int = SCHEMA_VERSION


def create_agent_state(
    subject_id: str,
    genesis_id: str,
    created_at: str,
) -> AgentState:
    """Create a deterministic state record; inputs are identifiers, not credentials."""
    require_non_empty_strings(
        subject_id=subject_id,
        genesis_id=genesis_id,
        created_at=created_at,
    )
    canonical = canonical_json(
        {
            "created_at": created_at,
            "genesis_id": genesis_id,
            "subject_id": subject_id,
            "version": SCHEMA_VERSION,
        }
    )
    identifier = sha256(canonical.encode("utf-8")).hexdigest()
    return AgentState(
        id=identifier,
        subject_id=subject_id,
        genesis_id=genesis_id,
        created_at=created_at,
    )
