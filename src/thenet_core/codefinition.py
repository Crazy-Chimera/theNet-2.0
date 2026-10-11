"""Rho Relational Co-definition: explicit, provenance-linked joint claims."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Sequence

from ._canonical import canonical_json, require_non_empty_strings
from .genesis import SCHEMA_VERSION
from .self_knowledge import SelfKnowledge


@dataclass(frozen=True, slots=True)
class CoDefinitionContribution:
    """A contributor's declared input, linked to a SelfKnowledge snapshot."""

    id: str
    contributor_id: str
    self_knowledge_id: str
    contribution_digest: str
    assents: bool
    version: int = SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CoDefinition:
    """Immutable joint-definition snapshot; agreement is not external verification."""

    id: str
    context_digest: str
    contributions: tuple[CoDefinitionContribution, ...]
    agreement_status: str
    verification_status: str
    version: int = SCHEMA_VERSION


def create_codefinition_contribution(
    self_knowledge: SelfKnowledge,
    contributor_id: str,
    contribution: str,
    assents: bool,
) -> CoDefinitionContribution:
    """Create a declared contribution linked to a self-model snapshot."""
    if not isinstance(self_knowledge, SelfKnowledge):
        raise ValueError("self_knowledge must be a SelfKnowledge instance")
    require_non_empty_strings(
        contributor_id=contributor_id,
        contribution=contribution,
    )
    if type(assents) is not bool:
        raise ValueError("assents must be a boolean")

    contribution_digest = sha256(contribution.encode("utf-8")).hexdigest()
    canonical = canonical_json({
        "assents": assents,
        "contribution_digest": contribution_digest,
        "contributor_id": contributor_id,
        "self_knowledge_id": self_knowledge.id,
        "version": SCHEMA_VERSION,
    })
    identifier = sha256(canonical.encode("utf-8")).hexdigest()
    return CoDefinitionContribution(
        id=identifier,
        contributor_id=contributor_id,
        self_knowledge_id=self_knowledge.id,
        contribution_digest=contribution_digest,
        assents=assents,
    )


def create_codefinition(
    context: str,
    contributions: Sequence[CoDefinitionContribution],
) -> CoDefinition:
    """Create a deterministic co-definition from at least two unique contributors.

    Agreement is declared only when every contribution explicitly assents.
    Verification status remains "unverified": this module does not authenticate
    contributor identities, establish legal authority, or judge contribution truth.
    """
    require_non_empty_strings(context=context)
    items = tuple(contributions)
    if len(items) < 2:
        raise ValueError("at least two contributions are required")
    if any(not isinstance(item, CoDefinitionContribution) for item in items):
        raise ValueError("contributions must contain only CoDefinitionContribution instances")
    contributor_ids = [item.contributor_id for item in items]
    if len(contributor_ids) != len(set(contributor_ids)):
        raise ValueError("contributor IDs must be unique")
    if len([item.id for item in items]) != len(set(item.id for item in items)):
        raise ValueError("contribution IDs must be unique")

    ordered = tuple(sorted(items, key=lambda item: (item.contributor_id, item.id)))
    agreement_status = "agreed" if all(item.assents for item in ordered) else "disputed"
    context_digest = sha256(context.encode("utf-8")).hexdigest()
    canonical = canonical_json({
        "agreement_status": agreement_status,
        "context_digest": context_digest,
        "contributions": [
            {
                "assents": item.assents,
                "contribution_digest": item.contribution_digest,
                "contributor_id": item.contributor_id,
                "id": item.id,
                "self_knowledge_id": item.self_knowledge_id,
                "version": item.version,
            }
            for item in ordered
        ],
        "verification_status": "unverified",
        "version": SCHEMA_VERSION,
    })
    identifier = sha256(canonical.encode("utf-8")).hexdigest()
    return CoDefinition(
        id=identifier,
        context_digest=context_digest,
        contributions=ordered,
        agreement_status=agreement_status,
        verification_status="unverified",
    )
