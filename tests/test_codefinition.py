from dataclasses import FrozenInstanceError

import pytest

from thenet_core import (
    create_agent_state,
    create_codefinition,
    create_codefinition_contribution,
    create_convergence,
    create_expression,
    create_genesis,
    create_meaning,
    create_memory_entry,
    create_movement,
    create_resonance,
    create_self_knowledge,
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
CHECK = create_verification_check("unit-tests", True, "a" * 64)
CONVERGENCE = create_convergence(RESONANCE, "proposal:codefinition", ("unit-tests",), (CHECK,))
MEANING = create_meaning(CONVERGENCE, "Declared checks passed.", ("unit-tests",))
EXPRESSION = create_expression(MEANING, "internal", "text/plain", "Joint definition")
SK = create_self_knowledge(
    EXPRESSION, "A bounded self-model.", ("canonicalize",), ("cannot authenticate identities",)
)
SK2 = create_self_knowledge(
    EXPRESSION, "Another bounded self-model.", ("compare",), ("cannot verify external claims",)
)


def contribution(who="agent:a", text="I support the proposal.", assents=True, sk=SK):
    return create_codefinition_contribution(sk, who, text, assents)


def test_codefinition_binds_contributions_context_and_agreement():
    result = create_codefinition(
        "context:shared-goal",
        (contribution("agent:a"), contribution("agent:b", "I also support.", sk=SK2)),
    )
    assert result.agreement_status == "agreed"
    assert result.verification_status == "unverified"
    assert len(result.context_digest) == 64
    assert tuple(item.contributor_id for item in result.contributions) == ("agent:a", "agent:b")


def test_codefinition_is_deterministic_and_contribution_order_independent():
    a = contribution("agent:a", "A", True, SK)
    b = contribution("agent:b", "B", True, SK2)
    first = create_codefinition("shared context", (a, b))
    second = create_codefinition("shared context", (b, a))
    assert first == second
    assert first.id == second.id


def test_codefinition_marks_non_unanimous_input_as_disputed():
    result = create_codefinition(
        "shared context",
        (contribution("agent:a", "yes", True), contribution("agent:b", "no", False, SK2)),
    )
    assert result.agreement_status == "disputed"
    assert result.verification_status == "unverified"


def test_codefinition_identity_binds_context():
    items = (contribution("agent:a"), contribution("agent:b", sk=SK2))
    first = create_codefinition("context one", items)
    second = create_codefinition("context two", items)
    assert first.id != second.id


def test_contribution_binds_self_knowledge_and_content_digest():
    item = contribution()
    assert item.self_knowledge_id == SK.id
    assert len(item.contribution_digest) == 64


def test_contribution_rejects_wrong_self_knowledge_type():
    with pytest.raises(ValueError, match="SelfKnowledge"):
        create_codefinition_contribution(object(), "agent:a", "content", True)


def test_contribution_rejects_invalid_assent_type():
    with pytest.raises(ValueError, match="boolean"):
        create_codefinition_contribution(SK, "agent:a", "content", 1)


@pytest.mark.parametrize(
    "contributor_id,content",
    [(" ", "content"), ("agent:a", " ")],
)
def test_contribution_rejects_empty_required_fields(contributor_id, content):
    with pytest.raises(ValueError):
        create_codefinition_contribution(SK, contributor_id, content, True)


def test_codefinition_requires_two_contributions():
    with pytest.raises(ValueError, match="at least two"):
        create_codefinition("context", (contribution(),))


def test_codefinition_rejects_duplicate_contributors():
    with pytest.raises(ValueError, match="contributor IDs must be unique"):
        create_codefinition("context", (contribution("same"), contribution("same", sk=SK2)))


def test_codefinition_rejects_invalid_contribution_type():
    with pytest.raises(ValueError, match="CoDefinitionContribution"):
        create_codefinition("context", (contribution(), object()))


def test_codefinition_requires_non_empty_context():
    with pytest.raises(ValueError, match="context"):
        create_codefinition(" ", (contribution(), contribution("agent:b", sk=SK2)))


def test_codefinition_is_immutable():
    result = create_codefinition("context", (contribution(), contribution("agent:b", sk=SK2)))
    with pytest.raises(FrozenInstanceError):
        result.agreement_status = "agreed"


def test_codefinition_does_not_claim_external_verification():
    result = create_codefinition("context", (contribution(), contribution("agent:b", sk=SK2)))
    assert result.verification_status == "unverified"
    assert not hasattr(result, "verified_by")
    assert not hasattr(result, "legal_authority")
