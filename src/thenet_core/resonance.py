"""Phi-Omega-squared Resonance: validated coherence across structure and memory."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Sequence

from ._canonical import canonical_json
from .genesis import SCHEMA_VERSION
from .memory import MemoryEntry
from .structure import Structure


@dataclass(frozen=True, slots=True)
class Resonance:
    """Deterministic coherence snapshot across a structure and memory chain."""

    id: str
    structure_id: str
    genesis_id: str
    memory_entries: tuple[MemoryEntry, ...]
    subject_count: int
    relation_count: int
    memory_count: int
    version: int = SCHEMA_VERSION


def create_resonance(
    structure: Structure,
    memory_entries: Sequence[MemoryEntry],
) -> Resonance:
    """Validate and bind a structure to a coherent set of memory entries.

    Every memory entry must belong to the same Genesis and a subject in the
    structure. Its terminal state must match that subject's state in the
    structure. If a predecessor is referenced, it must be present and form a
    contiguous transition chain. This validates supplied records only; it is
    not cryptographic authentication, a causal proof, or external persistence.
    """
    if not isinstance(structure, Structure):
        raise ValueError("structure must be a Structure instance")
    entries = tuple(memory_entries)
    if any(not isinstance(entry, MemoryEntry) for entry in entries):
        raise ValueError("memory_entries must contain only MemoryEntry instances")

    ids = [entry.id for entry in entries]
    if len(ids) != len(set(ids)):
        raise ValueError("memory entry identifiers must be unique")

    states_by_subject = {state.subject_id: state for state in structure.states}
    entries_by_id = {entry.id: entry for entry in entries}
    for entry in entries:
        if entry.genesis_id != structure.genesis_id:
            raise ValueError("memory entry must share the structure Genesis")
        state = states_by_subject.get(entry.subject_id)
        if state is None:
            raise ValueError("memory subject is not represented in structure")
        if entry.to_state_id != state.id:
            raise ValueError("memory terminal state does not match structure state")
        if entry.previous_entry_id is not None:
            previous = entries_by_id.get(entry.previous_entry_id)
            if previous is None:
                raise ValueError("referenced predecessor is missing from resonance")
            if previous.subject_id != entry.subject_id:
                raise ValueError("memory chain changes subject")
            if previous.genesis_id != entry.genesis_id:
                raise ValueError("memory chain changes Genesis")
            if previous.to_state_id != entry.from_state_id:
                raise ValueError("memory chain is not contiguous")

    ordered = tuple(sorted(entries, key=lambda item: item.id))
    canonical = canonical_json({
        "genesis_id": structure.genesis_id,
        "memory_entry_ids": [entry.id for entry in ordered],
        "structure_id": structure.id,
        "version": SCHEMA_VERSION,
    })
    identifier = sha256(canonical.encode("utf-8")).hexdigest()
    return Resonance(
        id=identifier,
        structure_id=structure.id,
        genesis_id=structure.genesis_id,
        memory_entries=ordered,
        subject_count=len(structure.states),
        relation_count=len(structure.relations),
        memory_count=len(ordered),
    )
