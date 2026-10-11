"""Omega-squared Memory: content-addressed, linked memory metadata."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from ._canonical import canonical_json, require_non_empty_strings
from .genesis import SCHEMA_VERSION
from .movement import Movement


@dataclass(frozen=True, slots=True)
class MemoryEntry:
    """Immutable memory metadata; raw payload is never retained in the entry."""

    id: str
    subject_id: str
    genesis_id: str
    movement_id: str
    from_state_id: str
    to_state_id: str
    payload_digest: str
    recorded_at: str
    previous_entry_id: str | None = None
    version: int = SCHEMA_VERSION


def create_memory_entry(
    movement: Movement,
    payload: str,
    recorded_at: str,
    previous: MemoryEntry | None = None,
) -> MemoryEntry:
    """Create a deterministic memory link for a movement and payload.

    Only a SHA-256 digest of payload is retained. When a predecessor is
    supplied, it must belong to the same subject and Genesis, and its ending
    state must equal the current movement's starting state. This is a local
    integrity check, not proof of external persistence or authenticity.
    """
    if not isinstance(movement, Movement):
        raise ValueError("movement must be a Movement instance")
    require_non_empty_strings(payload=payload, recorded_at=recorded_at)
    if previous is not None:
        if not isinstance(previous, MemoryEntry):
            raise ValueError("previous must be a MemoryEntry instance or None")
        if previous.subject_id != movement.subject_id:
            raise ValueError("memory chain must keep the same subject")
        if previous.genesis_id != movement.genesis_id:
            raise ValueError("memory chain must keep the same Genesis")
        if previous.to_state_id != movement.from_state_id:
            raise ValueError("movement must continue from the previous memory state")

    payload_digest = sha256(payload.encode("utf-8")).hexdigest()
    previous_id = previous.id if previous is not None else None
    canonical = canonical_json({
        "from_state_id": movement.from_state_id,
        "genesis_id": movement.genesis_id,
        "movement_id": movement.id,
        "payload_digest": payload_digest,
        "previous_entry_id": previous_id,
        "recorded_at": recorded_at,
        "subject_id": movement.subject_id,
        "to_state_id": movement.to_state_id,
        "version": SCHEMA_VERSION,
    })
    identifier = sha256(canonical.encode("utf-8")).hexdigest()
    return MemoryEntry(
        id=identifier,
        subject_id=movement.subject_id,
        genesis_id=movement.genesis_id,
        movement_id=movement.id,
        from_state_id=movement.from_state_id,
        to_state_id=movement.to_state_id,
        payload_digest=payload_digest,
        recorded_at=recorded_at,
        previous_entry_id=previous_id,
    )
