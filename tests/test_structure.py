from dataclasses import FrozenInstanceError

import pytest

from thenet_core import (
    create_agent_state,
    create_genesis,
    create_relation,
    create_structure,
)


STAMP = "2026-10-11T00:00:00Z"
GENESIS = create_genesis("theNet-2.0", STAMP)
STATE_A = create_agent_state("agent:a", GENESIS.id, STAMP)
STATE_B = create_agent_state("agent:b", GENESIS.id, STAMP)
RELATION = create_relation("agent:a", "agent:b", "trust", STAMP)


def test_structure_accepts_consistent_snapshot():
    structure = create_structure(GENESIS, [STATE_A, STATE_B], [RELATION])
    assert structure.genesis_id == GENESIS.id
    assert structure.states == tuple(sorted([STATE_A, STATE_B], key=lambda item: item.id))
    assert structure.relations == (RELATION,)
    assert structure.version == 1
    assert len(structure.id) == 64


def test_structure_identity_is_deterministic_and_order_independent():
    first = create_structure(GENESIS, [STATE_A, STATE_B], [RELATION])
    second = create_structure(GENESIS, [STATE_B, STATE_A], [RELATION])
    assert first == second
    assert first.id == second.id


def test_empty_structure_is_valid_genesis_snapshot():
    structure = create_structure(GENESIS, [], [])
    assert structure.states == ()
    assert structure.relations == ()


def test_structure_rejects_wrong_genesis_type():
    with pytest.raises(ValueError, match="Genesis"):
        create_structure("not-genesis", [], [])


def test_structure_rejects_state_from_another_genesis():
    other_genesis = create_genesis("other-origin", STAMP)
    foreign_state = create_agent_state("agent:a", other_genesis.id, STAMP)
    with pytest.raises(ValueError, match="anchored"):
        create_structure(GENESIS, [foreign_state], [])


@pytest.mark.parametrize("bad_states,bad_relations", [
    ([object()], []),
    ([], [object()]),
])
def test_structure_rejects_wrong_member_types(bad_states, bad_relations):
    with pytest.raises(ValueError):
        create_structure(GENESIS, bad_states, bad_relations)


def test_structure_rejects_relation_with_missing_source():
    dangling = create_relation("agent:missing", "agent:b", "trust", STAMP)
    with pytest.raises(ValueError, match="source_id"):
        create_structure(GENESIS, [STATE_A, STATE_B], [dangling])


def test_structure_rejects_relation_with_missing_target():
    dangling = create_relation("agent:a", "agent:missing", "trust", STAMP)
    with pytest.raises(ValueError, match="target_id"):
        create_structure(GENESIS, [STATE_A, STATE_B], [dangling])


def test_structure_rejects_duplicate_subjects():
    duplicate_subject = create_agent_state("agent:a", GENESIS.id, "2026-10-12T00:00:00Z")
    with pytest.raises(ValueError, match="subject_id"):
        create_structure(GENESIS, [STATE_A, duplicate_subject], [])


def test_structure_is_immutable():
    structure = create_structure(GENESIS, [STATE_A, STATE_B], [RELATION])
    with pytest.raises(FrozenInstanceError):
        structure.genesis_id = "mutated"
    with pytest.raises(AttributeError):
        structure.states.append(STATE_A)
