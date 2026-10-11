from dataclasses import FrozenInstanceError

import pytest

from thenet_core import (
    create_agent_state, create_genesis, create_memory_entry, create_movement,
)

STAMP = "2026-10-11T00:00:00Z"
GENESIS = create_genesis("theNet-2.0", STAMP)
S0 = create_agent_state("agent:a", GENESIS.id, STAMP)
S1 = create_agent_state("agent:a", GENESIS.id, "2026-10-11T00:01:00Z")
S2 = create_agent_state("agent:a", GENESIS.id, "2026-10-11T00:02:00Z")
M1 = create_movement(S0, S1, "observation")
M2 = create_movement(S1, S2, "verified update")


def test_memory_entry_records_digest_and_transition():
    entry = create_memory_entry(M1, "private payload", STAMP)
    assert entry.subject_id == "agent:a"
    assert entry.from_state_id == S0.id
    assert entry.to_state_id == S1.id
    assert entry.payload_digest != "private payload"
    assert len(entry.payload_digest) == 64
    assert not hasattr(entry, "payload")
    assert entry.previous_entry_id is None


def test_memory_entry_is_deterministic():
    first = create_memory_entry(M1, "same payload", STAMP)
    second = create_memory_entry(M1, "same payload", STAMP)
    assert first == second
    assert first.id == second.id


def test_memory_entry_links_contiguous_transition():
    first = create_memory_entry(M1, "first", STAMP)
    second = create_memory_entry(M2, "second", "2026-10-11T00:02:00Z", first)
    assert second.previous_entry_id == first.id
    assert second.from_state_id == first.to_state_id


def test_memory_rejects_disconnected_chain():
    first = create_memory_entry(M1, "first", STAMP)
    unrelated_state = create_agent_state("agent:a", GENESIS.id, "2026-10-11T00:03:00Z")
    unrelated = create_movement(S2, unrelated_state, "disconnected")
    with pytest.raises(ValueError, match="continue"):
        create_memory_entry(unrelated, "next", "2026-10-11T00:03:00Z", first)


def test_memory_rejects_cross_subject_chain():
    first = create_memory_entry(M1, "first", STAMP)
    other = create_agent_state("agent:b", GENESIS.id, "2026-10-11T00:02:00Z")
    other_next = create_agent_state("agent:b", GENESIS.id, "2026-10-11T00:03:00Z")
    movement = create_movement(other, other_next, "other subject")
    with pytest.raises(ValueError, match="same subject"):
        create_memory_entry(movement, "payload", STAMP, first)


def test_memory_rejects_cross_genesis_chain():
    first = create_memory_entry(M1, "first", STAMP)
    other_genesis = create_genesis("other", STAMP)
    before = create_agent_state("agent:a", other_genesis.id, STAMP)
    after = create_agent_state("agent:a", other_genesis.id, "2026-10-11T00:01:00Z")
    movement = create_movement(before, after, "other genesis")
    with pytest.raises(ValueError, match="same Genesis"):
        create_memory_entry(movement, "payload", STAMP, first)


@pytest.mark.parametrize("payload,recorded_at", [("", STAMP), ("payload", "  ")])
def test_memory_rejects_empty_required_values(payload, recorded_at):
    with pytest.raises(ValueError):
        create_memory_entry(M1, payload, recorded_at)


def test_memory_rejects_invalid_movement_and_predecessor_types():
    with pytest.raises(ValueError, match="Movement"):
        create_memory_entry(object(), "payload", STAMP)
    with pytest.raises(ValueError, match="MemoryEntry"):
        create_memory_entry(M1, "payload", STAMP, object())


def test_memory_entry_is_immutable():
    entry = create_memory_entry(M1, "payload", STAMP)
    with pytest.raises(FrozenInstanceError):
        entry.payload_digest = "tampered"
