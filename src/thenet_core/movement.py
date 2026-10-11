"""Omega Pohyb: a verified, immutable transition between agent states."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from ._canonical import canonical_json, require_non_empty_strings
from .agent_state import AgentState
from .genesis import SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class Movement:
    """A transition record; it describes state change without executing it."""

    id: str
    subject_id: str
    genesis_id: str
    from_state_id: str
    to_state_id: str
    cause: str
    version: int = SCHEMA_VERSION


def create_movement(
    previous: AgentState,
    current: AgentState,
    cause: str,
) -> Movement:
    """Create a deterministic transition between two states of one subject.

    Both states must belong to the same subject and Genesis. The transition
    must change state identity. This function records a transition; it does
    not mutate an agent, assert authorization, or persist anything.
    """
    if not isinstance(previous, AgentState) or not isinstance(current, AgentState):
        raise ValueError("previous and current must be AgentState instances")
    require_non_empty_strings(cause=cause)
    if previous.subject_id != current.subject_id:
        raise ValueError("movement states must belong to the same subject")
    if previous.genesis_id != current.genesis_id:
        raise ValueError("movement states must share the same Genesis")
    if previous.id == current.id:
        raise ValueError("movement must change state identity")

    canonical = canonical_json({
        "cause": cause,
        "from_state_id": previous.id,
        "genesis_id": previous.genesis_id,
        "subject_id": previous.subject_id,
        "to_state_id": current.id,
        "version": SCHEMA_VERSION,
    })
    identifier = sha256(canonical.encode("utf-8")).hexdigest()
    return Movement(
        id=identifier,
        subject_id=previous.subject_id,
        genesis_id=previous.genesis_id,
        from_state_id=previous.id,
        to_state_id=current.id,
        cause=cause,
    )
