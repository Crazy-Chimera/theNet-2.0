from dataclasses import FrozenInstanceError

import pytest

from thenet_core import (
    create_agent_state,
    create_convergence,
    create_genesis,
    create_meaning,
    create_memory_entry,
    create_movement,
    create_resonance,
    create_structure,
    create_verification_check,
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
RESONANCE = create_resonance(STRUCTURE, [M1, M2])
CHECKS = (
    create_verification_check("unit-tests", True, "a" * 64),
    create_verification_check("policy", True, "b" * 64),
)
CONVERGENCE = create_convergence(
    RESONANCE, "proposal:meaning", ("unit-tests", "policy"), CHECKS
)


def test_meaning_links_interpretation_to_check_evidence():
    result = create_meaning(
        CONVERGENCE, "The proposal passed the declared checks.", ("policy", "unit-tests")
    )
    assert result.convergence_id == CONVERGENCE.id
    assert result.proposal_id == "proposal:meaning"
    assert result.convergence_decision == "accepted"
    assert result.basis_check_ids == ("policy", "unit-tests")
    assert len(result.id) == 64


def test_meaning_is_deterministic_and_basis_order_independent():
    first = create_meaning(CONVERGENCE, "A declared interpretation.", ("policy", "unit-tests"))
    second = create_meaning(CONVERGENCE, "A declared interpretation.", ("unit-tests", "policy"))
    assert first == second
    assert first.id == second.id


def test_meaning_can_describe_a_rejected_proposal():
    failed = create_verification_check("policy", False, "c" * 64)
    rejected = create_convergence(
        RESONANCE, "proposal:rejected", ("unit-tests", "policy"),
        (CHECKS[0], failed),
    )
    result = create_meaning(rejected, "Policy check failed.", ("policy",))
    assert result.convergence_decision == "rejected"


def test_meaning_rejects_wrong_convergence_type():
    with pytest.raises(ValueError, match="Convergence"):
        create_meaning(object(), "interpretation", ("policy",))


def test_meaning_requires_non_empty_interpretation():
    with pytest.raises(ValueError, match="interpretation"):
        create_meaning(CONVERGENCE, "  ", ("policy",))


def test_meaning_requires_at_least_one_basis_check():
    with pytest.raises(ValueError, match="must not be empty"):
        create_meaning(CONVERGENCE, "interpretation", ())


def test_meaning_rejects_duplicate_basis_ids():
    with pytest.raises(ValueError, match="unique"):
        create_meaning(CONVERGENCE, "interpretation", ("policy", "policy"))


def test_meaning_rejects_unknown_basis_ids():
    with pytest.raises(ValueError, match="exist in the convergence"):
        create_meaning(CONVERGENCE, "interpretation", ("not-present",))


def test_meaning_is_immutable():
    result = create_meaning(CONVERGENCE, "interpretation", ("policy",))
    with pytest.raises(FrozenInstanceError):
        result.interpretation = "changed"
