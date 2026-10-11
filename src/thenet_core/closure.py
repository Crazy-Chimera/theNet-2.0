"""Sigma / Iota closure: a coherent, provenance-linked architecture snapshot."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from ._canonical import canonical_json
from .codefinition import CoDefinition
from .convergence import Convergence
from .expression import Expression
from .genesis import Genesis, SCHEMA_VERSION
from .meaning import Meaning
from .resonance import Resonance
from .self_knowledge import SelfKnowledge
from .structure import Structure


@dataclass(frozen=True, slots=True)
class Closure:
    """Immutable closure across the implemented existence-architecture layers.

    Structural coherence is distinct from proposal acceptance, contributor
    agreement, external verification, deployment, or claims of metaphysical unity.
    """

    id: str
    genesis_id: str
    structure_id: str
    resonance_id: str
    convergence_id: str
    meaning_id: str
    expression_id: str
    self_knowledge_id: str
    codefinition_id: str
    convergence_decision: str
    agreement_status: str
    verification_status: str
    version: int = SCHEMA_VERSION


def create_closure(
    genesis: Genesis,
    structure: Structure,
    resonance: Resonance,
    convergence: Convergence,
    meaning: Meaning,
    expression: Expression,
    self_knowledge: SelfKnowledge,
    codefinition: CoDefinition,
) -> Closure:
    """Bind the Σ / ΙΩΤΑ closure after validating every declared reference.

    This is a structural integration check over immutable supplied records.
    It does not authenticate identities/evidence, execute proposals, or verify
    any claim externally. A coherent closure may still contain a rejected
    proposal or a disputed co-definition.
    """
    typed = (
        ("genesis", genesis, Genesis),
        ("structure", structure, Structure),
        ("resonance", resonance, Resonance),
        ("convergence", convergence, Convergence),
        ("meaning", meaning, Meaning),
        ("expression", expression, Expression),
        ("self_knowledge", self_knowledge, SelfKnowledge),
        ("codefinition", codefinition, CoDefinition),
    )
    for name, value, expected in typed:
        if not isinstance(value, expected):
            raise ValueError(f"{name} must be a {expected.__name__} instance")

    if structure.genesis_id != genesis.id:
        raise ValueError("structure must reference the supplied Genesis")
    if resonance.structure_id != structure.id or resonance.genesis_id != genesis.id:
        raise ValueError("resonance must reference the supplied structure and Genesis")
    if convergence.resonance_id != resonance.id:
        raise ValueError("convergence must reference the supplied resonance")
    if meaning.convergence_id != convergence.id:
        raise ValueError("meaning must reference the supplied convergence")
    if meaning.proposal_id != convergence.proposal_id:
        raise ValueError("meaning proposal must match convergence proposal")
    if meaning.convergence_decision != convergence.decision:
        raise ValueError("meaning decision must match convergence decision")
    if expression.meaning_id != meaning.id:
        raise ValueError("expression must reference the supplied meaning")
    if self_knowledge.expression_id != expression.id:
        raise ValueError("self-knowledge must reference the supplied expression")
    if self_knowledge.meaning_id != meaning.id:
        raise ValueError("self-knowledge must reference the supplied meaning")
    if not any(
        item.self_knowledge_id == self_knowledge.id
        for item in codefinition.contributions
    ):
        raise ValueError("co-definition must include the supplied self-knowledge record")

    payload = {
        "agreement_status": codefinition.agreement_status,
        "codefinition_id": codefinition.id,
        "convergence_decision": convergence.decision,
        "convergence_id": convergence.id,
        "expression_id": expression.id,
        "genesis_id": genesis.id,
        "meaning_id": meaning.id,
        "resonance_id": resonance.id,
        "self_knowledge_id": self_knowledge.id,
        "structure_id": structure.id,
        "verification_status": "unverified",
        "version": SCHEMA_VERSION,
    }
    identifier = sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return Closure(
        id=identifier,
        genesis_id=genesis.id,
        structure_id=structure.id,
        resonance_id=resonance.id,
        convergence_id=convergence.id,
        meaning_id=meaning.id,
        expression_id=expression.id,
        self_knowledge_id=self_knowledge.id,
        codefinition_id=codefinition.id,
        convergence_decision=convergence.decision,
        agreement_status=codefinition.agreement_status,
        verification_status="unverified",
    )
