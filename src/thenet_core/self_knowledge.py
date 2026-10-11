"""Theta Self-Knowledge: a bounded, evidence-linked self-model snapshot."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Sequence

from ._canonical import canonical_json, require_non_empty_strings
from .expression import Expression
from .genesis import SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SelfKnowledge:
    """Immutable self-model claims; not proof of consciousness or correctness."""

    id: str
    expression_id: str
    meaning_id: str
    self_model_digest: str
    declared_capabilities: tuple[str, ...]
    known_limitations: tuple[str, ...]
    version: int = SCHEMA_VERSION


def create_self_knowledge(
    expression: Expression,
    self_model: str,
    declared_capabilities: Sequence[str],
    known_limitations: Sequence[str],
) -> SelfKnowledge:
    """Record a self-model linked to an Expression and an explicit limitation set.

    Capabilities and limitations are declarations supplied by the caller.
    At least one limitation must be recorded to make the snapshot's boundary
    explicit. This function does not test whether any claim is true, measure
    consciousness, or grant the subject authority to change itself.
    """
    if not isinstance(expression, Expression):
        raise ValueError("expression must be an Expression instance")
    require_non_empty_strings(self_model=self_model)

    capabilities = tuple(declared_capabilities)
    limitations = tuple(known_limitations)
    for label, values in (
        ("declared_capabilities", capabilities),
        ("known_limitations", limitations),
    ):
        if any(not isinstance(item, str) or not item.strip() for item in values):
            raise ValueError(f"{label} must contain only non-empty strings")
        if len(values) != len(set(values)):
            raise ValueError(f"{label} must contain unique values")
    if not limitations:
        raise ValueError("known_limitations must contain at least one limitation")

    ordered_capabilities = tuple(sorted(capabilities))
    ordered_limitations = tuple(sorted(limitations))
    self_model_digest = sha256(self_model.encode("utf-8")).hexdigest()
    canonical = canonical_json({
        "declared_capabilities": list(ordered_capabilities),
        "expression_id": expression.id,
        "known_limitations": list(ordered_limitations),
        "meaning_id": expression.meaning_id,
        "self_model_digest": self_model_digest,
        "version": SCHEMA_VERSION,
    })
    identifier = sha256(canonical.encode("utf-8")).hexdigest()
    return SelfKnowledge(
        id=identifier,
        expression_id=expression.id,
        meaning_id=expression.meaning_id,
        self_model_digest=self_model_digest,
        declared_capabilities=ordered_capabilities,
        known_limitations=ordered_limitations,
    )
