from dataclasses import FrozenInstanceError

import pytest

from thenet_core import create_agent_state, create_genesis


STAMP = "2026-10-11T00:00:00Z"
GENESIS_ID = create_genesis("theNet-2.0", STAMP).id
BASE = ("agent:alpha", GENESIS_ID, STAMP)


def test_agent_state_is_anchored_to_genesis():
    state = create_agent_state(*BASE)
    assert state.subject_id == BASE[0]
    assert state.genesis_id == GENESIS_ID
    assert state.created_at == STAMP
    assert state.version == 1
    assert len(state.id) == 64
    assert create_agent_state(*BASE) == state


@pytest.mark.parametrize("index", range(3))
def test_agent_state_rejects_blank_required_fields(index):
    values = list(BASE)
    values[index] = " "
    with pytest.raises(ValueError):
        create_agent_state(*values)


def test_agent_state_rejects_non_string_field():
    with pytest.raises(ValueError):
        create_agent_state("agent:alpha", None, STAMP)


def test_genesis_anchor_is_part_of_state_identity():
    other_genesis = create_genesis("another-origin", STAMP).id
    assert create_agent_state(*BASE).id != create_agent_state(BASE[0], other_genesis, STAMP).id


def test_agent_state_is_immutable():
    state = create_agent_state(*BASE)
    with pytest.raises(FrozenInstanceError):
        state.subject_id = "agent:beta"
