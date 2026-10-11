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
CONVERGENCE = create_convergence(RESONANCE, "proposal:expression", ("unit-tests",), (CHECK,))
MEANING = create_meaning(
    CONVERGENCE, "The declared checks passed.", ("unit-tests",)
)


def test_expression_binds_output_to_meaning_and_stores_digest_only():
    content = "The proposal passed the declared checks."
    result = create_expression(MEANING, "chat", "text/plain", content)
    assert result.meaning_id == MEANING.id
    assert result.channel == "chat"
    assert result.format == "text/plain"
    assert result.content_digest != content
    assert len(result.content_digest) == 64
    assert not hasattr(result, "content")


def test_expression_identity_is_deterministic():
    first = create_expression(MEANING, "chat", "text/plain", "same output")
    second = create_expression(MEANING, "chat", "text/plain", "same output")
    assert first == second
    assert first.id == second.id


def test_expression_identity_binds_meaning_channel_format_and_content():
    baseline = create_expression(MEANING, "chat", "text/plain", "output")
    other_channel = create_expression(MEANING, "email", "text/plain", "output")
    other_format = create_expression(MEANING, "chat", "text/markdown", "output")
    other_content = create_expression(MEANING, "chat", "text/plain", "changed")
    assert len({baseline.id, other_channel.id, other_format.id, other_content.id}) == 4


def test_expression_rejects_wrong_meaning_type():
    with pytest.raises(ValueError, match="Meaning"):
        create_expression(object(), "chat", "text/plain", "output")


@pytest.mark.parametrize(
    "channel,format,content",
    [
        (" ", "text/plain", "output"),
        ("chat", "", "output"),
        ("chat", "text/plain", "  "),
    ],
)
def test_expression_rejects_empty_required_fields(channel, format, content):
    with pytest.raises(ValueError):
        create_expression(MEANING, channel, format, content)


def test_expression_is_immutable():
    result = create_expression(MEANING, "chat", "text/plain", "output")
    with pytest.raises(FrozenInstanceError):
        result.channel = "email"


def test_expression_does_not_claim_delivery():
    result = create_expression(MEANING, "chat", "text/plain", "output")
    assert not hasattr(result, "delivered")
    assert not hasattr(result, "recipient")
