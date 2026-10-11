"""Phi Structure: a deterministic, validated snapshot of a relational state."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Sequence

from ._canonical import canonical_json
from .agent_state import AgentState
from .genesis import Genesis, SCHEMA_VERSION
from .relation import Relation


@dataclass(frozen=True, slots=True)
class Structure:
    """Immutable aggregate whose relations must resolve to included subjects."""

    id: str
    genesis_id: str
    states: tuple[AgentState, ...]
    relations: tuple[Relation, ...]
    version: int = SCHEMA_VERSION


def create_structure(
    genesis: Genesis,
    states: Sequence[AgentState],
    relations: Sequence[Relation],
) -> Structure:
    """Validate and create an order-independent structural snapshot.

    A relation endpoint is a subject_id in this snapshot. State records must
    be anchored to the supplied Genesis. No persistence or network I/O occurs.
    """
    if not isinstance(genesis, Genesis):
        raise ValueError("genesis must be a Genesis instance")

    state_items = tuple(states)
    relation_items = tuple(relations)

    if any(not isinstance(item, AgentState) for item in state_items):
        raise ValueError("states must contain only AgentState instances")
    if any(not isinstance(item, Relation) for item in relation_items):
        raise ValueError("relations must contain only Relation instances")

    if any(item.genesis_id != genesis.id for item in state_items):
        raise ValueError("every state must be anchored to the supplied Genesis")

    subject_ids = [item.subject_id for item in state_items]
    state_ids = [item.id for item in state_items]
    relation_ids = [item.id for item in relation_items]

    if len(subject_ids) != len(set(subject_ids)):
        raise ValueError("state subject_id values must be unique")
    if len(state_ids) != len(set(state_ids)):
        raise ValueError("state identifiers must be unique")
    if len(relation_ids) != len(set(relation_ids)):
        raise ValueError("relation identifiers must be unique")

    known_subjects = set(subject_ids)
    for relation in relation_items:
        if relation.source_id not in known_subjects:
            raise ValueError(
                f"relation source_id is not represented in structure: {relation.source_id}"
            )
        if relation.target_id not in known_subjects:
            raise ValueError(
                f"relation target_id is not represented in structure: {relation.target_id}"
            )

    canonical_states = tuple(sorted(state_items, key=lambda item: item.id))
    canonical_relations = tuple(sorted(relation_items, key=lambda item: item.id))
    canonical = canonical_json(
        {
            "genesis_id": genesis.id,
            "relations": [item.id for item in canonical_relations],
            "states": [item.id for item in canonical_states],
            "version": SCHEMA_VERSION,
        }
    )
    identifier = sha256(canonical.encode("utf-8")).hexdigest()

    return Structure(
        id=identifier,
        genesis_id=genesis.id,
        states=canonical_states,
        relations=canonical_relations,
    )
