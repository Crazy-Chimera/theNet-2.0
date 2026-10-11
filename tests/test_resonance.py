from dataclasses import FrozenInstanceError

import pytest

from thenet_core import (
    create_agent_state, create_genesis, create_memory_entry, create_movement,
    create_resonance, create_structure,
)

STAMP = "2026-10-11T00:00:00Z"
GENESIS = create_genesis("theNet-2.0", STAMP)
S0 = create_agent_state("agent:a", GENESIS.id, STAMP)
S1 = create_agent_state("agent:a", GENESIS.id, "2026-10-11T00:01:00Z")
S2 = create_agent_state("agent:a", GENESIS.id, "2026-10-11T00:02:00Z")
STRUCTURE = create_structure(GENESIS, [S2], [])
M1 = create_memory_entry(create_movement(S0, S1, "first"), "payload-1", STAMP)
M2 = create_memory_entry(
    create_movement(S1, S2, "second"), "payload-2", "2026-10-11T00:02:00Z", M1
)


def test_resonance_accepts_coherent_structure_and_memory_chain():
    result = create_resonance(STRUCTURE, [M2, M1])
    assert result.structure_id == STRUCTURE.id
    assert result.genesis_id == GENESIS.id
    assert result.memory_entries == tuple(sorted([M1, M2], key=lambda item: item.id))
    assert result.subject_count == 1
    assert result.relation_count == 0
    assert result.memory_count == 2
    assert len(result.id) == 64


def test_resonance_is_deterministic_and_order_independent():
    first = create_resonance(STRUCTURE, [M1, M2])
    second = create_resonance(STRUCTURE, [M2, M1])
    assert first == second
    assert first.id == second.id


def test_resonance_rejects_wrong_structure_type():
    with pytest.raises(ValueError, match="Structure"):
        create_resonance(object(), [])


def test_resonance_rejects_invalid_memory_type():
    with pytest.raises(ValueError, match="MemoryEntry"):
        create_resonance(STRUCTURE, [object()])


def test_resonance_rejects_foreign_genesis():
    other_genesis = create_genesis("other", STAMP)
    a = create_agent_state("agent:a", other_genesis.id, STAMP)
    b = create_agent_state("agent:a", other_genesis.id, "2026-10-11T00:01:00Z")
    memory = create_memory_entry(create_movement(a, b, "foreign"), "payload", STAMP)
    with pytest.raises(ValueError, match="Genesis"):
        create_resonance(STRUCTURE, [memory])


def test_resonance_rejects_memory_terminal_state_mismatch():
    with pytest.raises(ValueError, match="terminal state"):
        create_resonance(STRUCTURE, [M1])


def test_resonance_requires_complete_predecessor_chain():
    with pytest.raises(ValueError, match="predecessor"):
        create_resonance(STRUCTURE, [M2])


def test_resonance_rejects_duplicate_entries():
    with pytest.raises(ValueError, match="unique"):
        create_resonance(STRUCTURE, [M2, M2])


def test_resonance_is_immutable():
    result = create_resonance(STRUCTURE, [M1, M2])
    with pytest.raises(FrozenInstanceError):
        result.memory_count = 100
