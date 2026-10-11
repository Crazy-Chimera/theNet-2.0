from dataclasses import FrozenInstanceError

import pytest

from thenet_core import create_agent_state, create_genesis, create_movement

STAMP = "2026-10-11T00:00:00Z"
GENESIS = create_genesis("theNet-2.0", STAMP)
BEFORE = create_agent_state("agent:a", GENESIS.id, STAMP)
AFTER = create_agent_state("agent:a", GENESIS.id, "2026-10-11T00:01:00Z")


def test_movement_records_transition_without_mutating_states():
    movement = create_movement(BEFORE, AFTER, "new observation verified")
    assert movement.subject_id == BEFORE.subject_id
    assert movement.genesis_id == GENESIS.id
    assert movement.from_state_id == BEFORE.id
    assert movement.to_state_id == AFTER.id
    assert movement.version == 1
    assert len(movement.id) == 64
    assert BEFORE.created_at == STAMP


def test_movement_identity_is_deterministic():
    first = create_movement(BEFORE, AFTER, "verified")
    second = create_movement(BEFORE, AFTER, "verified")
    assert first == second
    assert first.id == second.id


def test_movement_rejects_different_subjects():
    other = create_agent_state("agent:b", GENESIS.id, "2026-10-11T00:01:00Z")
    with pytest.raises(ValueError, match="same subject"):
        create_movement(BEFORE, other, "verified")


def test_movement_rejects_different_genesis():
    other_genesis = create_genesis("other-origin", STAMP)
    other = create_agent_state("agent:a", other_genesis.id, "2026-10-11T00:01:00Z")
    with pytest.raises(ValueError, match="same Genesis"):
        create_movement(BEFORE, other, "verified")


def test_movement_rejects_unchanged_state():
    with pytest.raises(ValueError, match="change state identity"):
        create_movement(BEFORE, BEFORE, "no-op")


@pytest.mark.parametrize("previous,current", [(object(), AFTER), (BEFORE, object())])
def test_movement_rejects_invalid_state_types(previous, current):
    with pytest.raises(ValueError, match="AgentState"):
        create_movement(previous, current, "verified")


def test_movement_rejects_empty_cause():
    with pytest.raises(ValueError, match="cause"):
        create_movement(BEFORE, AFTER, "  ")


def test_movement_is_immutable():
    movement = create_movement(BEFORE, AFTER, "verified")
    with pytest.raises(FrozenInstanceError):
        movement.cause = "tampered"
