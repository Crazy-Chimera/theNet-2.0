from dataclasses import FrozenInstanceError

import pytest

from thenet_core import (
    create_agent_state,
    create_convergence,
    create_genesis,
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
REQUIRED = ("unit-tests", "policy", "integrity")
CHECKS = (
    create_verification_check("unit-tests", True, "a" * 64),
    create_verification_check("policy", True, "b" * 64),
    create_verification_check("integrity", True, "c" * 64),
)


def test_convergence_accepts_complete_passing_checks():
    result = create_convergence(RESONANCE, "proposal:1", REQUIRED, CHECKS)
    assert result.decision == "accepted"
    assert result.missing_check_ids == ()
    assert result.failed_check_ids == ()
    assert result.resonance_id == RESONANCE.id
    assert len(result.id) == 64


def test_convergence_rejects_missing_check():
    result = create_convergence(RESONANCE, "proposal:1", REQUIRED, CHECKS[:2])
    assert result.decision == "rejected"
    assert result.missing_check_ids == ("integrity",)


def test_convergence_rejects_failed_check():
    failed = create_verification_check("policy", False, "d" * 64)
    result = create_convergence(
        RESONANCE, "proposal:1", REQUIRED, (CHECKS[0], failed, CHECKS[2])
    )
    assert result.decision == "rejected"
    assert result.failed_check_ids == ("policy",)


def test_convergence_is_deterministic_and_order_independent():
    first = create_convergence(RESONANCE, "proposal:1", REQUIRED, CHECKS)
    second = create_convergence(RESONANCE, "proposal:1", reversed(REQUIRED), reversed(CHECKS))
    assert first == second
    assert first.id == second.id


def test_convergence_rejects_wrong_resonance_type():
    with pytest.raises(ValueError, match="Resonance"):
        create_convergence(object(), "proposal:1", REQUIRED, CHECKS)


def test_convergence_rejects_duplicate_required_checks():
    with pytest.raises(ValueError, match="unique"):
        create_convergence(RESONANCE, "proposal:1", ("policy", "policy"), ())


def test_convergence_rejects_duplicate_check_records():
    with pytest.raises(ValueError, match="unique"):
        create_convergence(RESONANCE, "proposal:1", REQUIRED, (CHECKS[0], CHECKS[0]))


def test_convergence_rejects_unrequested_checks():
    extra = create_verification_check("unrequested", True, "e" * 64)
    with pytest.raises(ValueError, match="unrequested"):
        create_convergence(RESONANCE, "proposal:1", REQUIRED, (*CHECKS, extra))


def test_convergence_rejects_invalid_check_types():
    with pytest.raises(ValueError, match="VerificationCheck"):
        create_convergence(RESONANCE, "proposal:1", REQUIRED, (object(),))


def test_verification_check_requires_boolean_status():
    with pytest.raises(ValueError, match="boolean"):
        create_verification_check("policy", 1, "f" * 64)


def test_convergence_is_immutable():
    result = create_convergence(RESONANCE, "proposal:1", REQUIRED, CHECKS)
    with pytest.raises(FrozenInstanceError):
        result.decision = "accepted"
