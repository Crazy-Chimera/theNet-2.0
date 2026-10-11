from dataclasses import FrozenInstanceError

import pytest

from thenet_core import (
    create_agent_state,
    create_closure,
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
CONVERGENCE = create_convergence(RESONANCE, "proposal:closure", ("unit-tests",), (CHECK,))
MEANING = create_meaning(CONVERGENCE, "Declared checks passed.", ("unit-tests",))
EXPRESSION = create_expression(MEANING, "internal", "text/plain", "Closure snapshot")
SK = create_self_knowledge(
    EXPRESSION, "A bounded self-model.", ("canonicalize",), ("cannot authenticate identities",)
)
SK2 = create_self_knowledge(
    EXPRESSION, "Another bounded self-model.", ("compare",), ("cannot verify external claims",)
)
C1 = create_codefinition_contribution(SK, "agent:a", "I assent.", True)
C2 = create_codefinition_contribution(SK2, "agent:b", "I also assent.", True)
CODEFINITION = create_codefinition("context:closure", (C1, C2))


def build(**overrides):
    args = {
        "genesis": GENESIS,
        "structure": STRUCTURE,
        "resonance": RESONANCE,
        "convergence": CONVERGENCE,
        "meaning": MEANING,
        "expression": EXPRESSION,
        "self_knowledge": SK,
        "codefinition": CODEFINITION,
    }
    args.update(overrides)
    return create_closure(**args)


def test_closure_binds_all_architecture_layers():
    result = build()
    assert result.genesis_id == GENESIS.id
    assert result.structure_id == STRUCTURE.id
    assert result.resonance_id == RESONANCE.id
    assert result.convergence_id == CONVERGENCE.id
    assert result.meaning_id == MEANING.id
    assert result.expression_id == EXPRESSION.id
    assert result.self_knowledge_id == SK.id
    assert result.codefinition_id == CODEFINITION.id
    assert result.convergence_decision == "accepted"
    assert result.agreement_status == "agreed"
    assert result.verification_status == "unverified"


def test_closure_identity_is_deterministic():
    assert build() == build()
    assert build().id == build().id


def test_closure_rejects_wrong_types():
    with pytest.raises(ValueError, match="genesis must be a Genesis"):
        build(genesis=object())


@pytest.mark.parametrize(
    "field,value,message",
    [
        ("structure", create_structure(create_genesis("other", STAMP), [], []), "supplied Genesis"),
        ("resonance", object(), "resonance must be a Resonance"),
        ("convergence", object(), "convergence must be a Convergence"),
        ("meaning", object(), "meaning must be a Meaning"),
        ("expression", object(), "expression must be a Expression"),
        ("self_knowledge", object(), "self_knowledge must be a SelfKnowledge"),
        ("codefinition", object(), "codefinition must be a CoDefinition"),
    ],
)
def test_closure_rejects_invalid_layer_reference(field, value, message):
    with pytest.raises(ValueError, match=message):
        build(**{field: value})


def test_closure_rejects_mismatched_convergence_chain():
    other = create_convergence(RESONANCE, "other-proposal", ("unit-tests",), (CHECK,))
    with pytest.raises(ValueError, match="supplied convergence"):
        build(convergence=other)


def test_closure_rejects_co_definition_without_primary_self_knowledge():
    other = create_codefinition(
        "context:other",
        (
            create_codefinition_contribution(SK2, "agent:b", "B", True),
            create_codefinition_contribution(
                create_self_knowledge(
                    EXPRESSION, "Third model", (), ("cannot authenticate",)
                ),
                "agent:c",
                "C",
                True,
            ),
        ),
    )
    with pytest.raises(ValueError, match="must include the supplied self-knowledge"):
        build(codefinition=other)


def test_disputed_definition_and_rejected_decision_remain_explicit():
    disputed = create_codefinition(
        "context:disputed",
        (
            C1,
            create_codefinition_contribution(SK2, "agent:b", "I dissent.", False),
        ),
    )
    result = build(codefinition=disputed)
    assert result.agreement_status == "disputed"
    assert result.verification_status == "unverified"
    rejected = create_convergence(
        RESONANCE,
        "proposal:rejected",
        ("unit-tests",),
        (create_verification_check("unit-tests", False, "b" * 64),),
    )
    rejected_meaning = create_meaning(rejected, "A required check failed.", ("unit-tests",))
    rejected_expression = create_expression(
        rejected_meaning, "internal", "text/plain", "Rejected proposal"
    )
    rejected_sk = create_self_knowledge(
        rejected_expression,
        "A bounded model for a rejected proposal.",
        ("record outcomes",),
        ("cannot authenticate evidence",),
    )
    rejected_codefinition = create_codefinition(
        "context:rejected",
        (
            create_codefinition_contribution(rejected_sk, "agent:a", "Record rejection.", True),
            create_codefinition_contribution(SK2, "agent:b", "I acknowledge the record.", True),
        ),
    )
    result = build(
        convergence=rejected,
        meaning=rejected_meaning,
        expression=rejected_expression,
        self_knowledge=rejected_sk,
        codefinition=rejected_codefinition,
    )
    assert result.convergence_decision == "rejected"
    assert result.agreement_status == "agreed"
    assert result.verification_status == "unverified"


def test_closure_is_immutable():
    result = build()
    with pytest.raises(FrozenInstanceError):
        result.agreement_status = "agreed"


def test_closure_does_not_claim_external_verification_or_activation():
    result = build()
    assert result.verification_status == "unverified"
    assert not hasattr(result, "activated")
    assert not hasattr(result, "externally_verified")
