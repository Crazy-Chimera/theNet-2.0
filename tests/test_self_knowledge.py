from dataclasses import FrozenInstanceError

import pytest

from thenet_core import (
    create_agent_state,
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
CONVERGENCE = create_convergence(RESONANCE, "proposal:self-knowledge", ("unit-tests",), (CHECK,))
MEANING = create_meaning(CONVERGENCE, "Declared checks passed.", ("unit-tests",))
EXPRESSION = create_expression(MEANING, "internal", "text/plain", "Output artifact")


def build(**overrides):
    args = {
        "expression": EXPRESSION,
        "self_model": "I can record and compare declared state metadata.",
        "declared_capabilities": ("canonicalize records", "compare digests"),
        "known_limitations": ("cannot authenticate external claims",),
    }
    args.update(overrides)
    return create_self_knowledge(**args)


def test_self_knowledge_binds_to_expression_and_meaning():
    result = build()
    assert result.expression_id == EXPRESSION.id
    assert result.meaning_id == MEANING.id
    assert len(result.self_model_digest) == 64
    assert result.known_limitations == ("cannot authenticate external claims",)


def test_self_knowledge_is_deterministic_and_order_independent():
    first = build(
        declared_capabilities=("compare digests", "canonicalize records"),
        known_limitations=("cannot authenticate external claims", "cannot prove consciousness"),
    )
    second = build(
        declared_capabilities=("canonicalize records", "compare digests"),
        known_limitations=("cannot prove consciousness", "cannot authenticate external claims"),
    )
    assert first == second
    assert first.id == second.id


def test_self_knowledge_identity_changes_when_self_model_changes():
    first = build(self_model="Model A")
    second = build(self_model="Model B")
    assert first.id != second.id
    assert first.self_model_digest != second.self_model_digest


def test_self_knowledge_rejects_wrong_expression_type():
    with pytest.raises(ValueError, match="Expression"):
        create_self_knowledge(object(), "model", (), ("limitation",))


def test_self_knowledge_requires_non_empty_model():
    with pytest.raises(ValueError, match="self_model"):
        build(self_model=" ")


def test_self_knowledge_requires_at_least_one_limitation():
    with pytest.raises(ValueError, match="at least one limitation"):
        build(known_limitations=())


@pytest.mark.parametrize(
    "field,values",
    [
        ("declared_capabilities", ("valid", " ")),
        ("known_limitations", ("valid", "")),
    ],
)
def test_self_knowledge_rejects_empty_claims(field, values):
    with pytest.raises(ValueError, match="non-empty strings"):
        build(**{field: values})


@pytest.mark.parametrize(
    "field,values",
    [
        ("declared_capabilities", ("same", "same")),
        ("known_limitations", ("same", "same")),
    ],
)
def test_self_knowledge_rejects_duplicate_claims(field, values):
    with pytest.raises(ValueError, match="unique"):
        build(**{field: values})


def test_self_knowledge_is_immutable():
    result = build()
    with pytest.raises(FrozenInstanceError):
        result.self_model_digest = "tampered"


def test_self_knowledge_does_not_claim_consciousness_or_authority():
    result = build()
    assert not hasattr(result, "consciousness_score")
    assert not hasattr(result, "self_modification_authority")
