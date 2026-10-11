from dataclasses import FrozenInstanceError

import pytest

from thenet_core import (
    create_agent_state,
    create_closure,
    create_codefinition,
    create_codefinition_contribution,
    create_commit_intent,
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
PASS = create_verification_check("unit-tests", True, "a" * 64)
CONVERGENCE = create_convergence(RESONANCE, "proposal:evolution", ("unit-tests",), (PASS,))
MEANING = create_meaning(CONVERGENCE, "Checks supplied as passing.", ("unit-tests",))
EXPRESSION = create_expression(MEANING, "internal", "text/plain", "Prepared change")
SK = create_self_knowledge(
    EXPRESSION, "Bounded model.", ("prepare intent",), ("cannot authorize execution",)
)
SK2 = create_self_knowledge(
    EXPRESSION, "Other bounded model.", ("review intent",), ("cannot authenticate evidence",)
)
CODEFINITION = create_codefinition(
    "context:evolution",
    (
        create_codefinition_contribution(SK, "agent:a", "I assent.", True),
        create_codefinition_contribution(SK2, "agent:b", "I also assent.", True),
    ),
)
CLOSURE = create_closure(
    GENESIS, STRUCTURE, RESONANCE, CONVERGENCE, MEANING, EXPRESSION, SK, CODEFINITION
)


def build(**overrides):
    args = {
        "closure": CLOSURE,
        "action": "propose",
        "target": "system:core",
        "proposed_change": "change-digest-source-content",
    }
    args.update(overrides)
    return create_commit_intent(**args)


def test_commit_intent_is_prepared_and_not_authorized():
    result = build()
    assert result.closure_id == CLOSURE.id
    assert result.identity_binding == SK.id
    assert result.status == "prepared"
    assert result.authorization_status == "not_authorized"
    assert len(result.proposed_change_digest) == 64


def test_commit_intent_is_deterministic():
    assert build() == build()
    assert build().id == build().id


def test_commit_intent_binds_action_target_and_change():
    base = build()
    assert build(action="review").id != base.id
    assert build(target="system:other").id != base.id
    assert build(proposed_change="different change").id != base.id


def test_commit_intent_rejects_wrong_closure_type():
    with pytest.raises(ValueError, match="Closure"):
        build(closure=object())


@pytest.mark.parametrize(
    "field,value",
    [
        ("action", " "),
        ("target", ""),
        ("proposed_change", "  "),
    ],
)
def test_commit_intent_rejects_empty_fields(field, value):
    with pytest.raises(ValueError):
        build(**{field: value})


def test_commit_intent_rejects_rejected_decision():
    rejected = create_convergence(
        RESONANCE,
        "proposal:rejected",
        ("unit-tests",),
        (create_verification_check("unit-tests", False, "b" * 64),),
    )
    meaning = create_meaning(rejected, "A required check failed.", ("unit-tests",))
    expression = create_expression(meaning, "internal", "text/plain", "Rejected")
    sk = create_self_knowledge(expression, "Model.", (), ("cannot authenticate",))
    other_sk = create_self_knowledge(expression, "Other model.", (), ("cannot verify",))
    codefinition = create_codefinition(
        "context:rejected",
        (
            create_codefinition_contribution(sk, "agent:a", "A", True),
            create_codefinition_contribution(other_sk, "agent:b", "B", True),
        ),
    )
    closure = create_closure(
        GENESIS, STRUCTURE, RESONANCE, rejected, meaning, expression, sk, codefinition
    )
    with pytest.raises(ValueError, match="accepted convergence"):
        build(closure=closure)


def test_commit_intent_rejects_disputed_agreement():
    disputed = create_codefinition(
        "context:disputed",
        (
            create_codefinition_contribution(SK, "agent:a", "A", True),
            create_codefinition_contribution(SK2, "agent:b", "B", False),
        ),
    )
    closure = create_closure(
        GENESIS, STRUCTURE, RESONANCE, CONVERGENCE, MEANING, EXPRESSION, SK, disputed
    )
    with pytest.raises(ValueError, match="unanimous"):
        build(closure=closure)


def test_commit_intent_is_immutable_and_does_not_execute():
    result = build()
    with pytest.raises(FrozenInstanceError):
        result.status = "executed"
    assert not hasattr(result, "executed_at")
    assert not hasattr(result, "commit_sha")
    assert result.authorization_status == "not_authorized"
