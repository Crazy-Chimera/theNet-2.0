"""Pi Meaning: a declared interpretation linked to explicit convergence evidence."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Sequence

from ._canonical import canonical_json, require_non_empty_strings
from .convergence import Convergence
from .genesis import SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class Meaning:
    """Immutable interpretation record; it is not itself a verified fact."""

    id: str
    convergence_id: str
    proposal_id: str
    interpretation: str
    basis_check_ids: tuple[str, ...]
    convergence_decision: str
    version: int = SCHEMA_VERSION


def create_meaning(
    convergence: Convergence,
    interpretation: str,
    basis_check_ids: Sequence[str],
) -> Meaning:
    """Bind an interpretation to one or more check records in a convergence.

    Interpretations may describe accepted or rejected proposals. Every basis
    ID must exist in the referenced convergence. This verifies referential
    consistency only: the text's truth, quality, authorship and semantics are
    not authenticated or automatically inferred.
    """
    if not isinstance(convergence, Convergence):
        raise ValueError("convergence must be a Convergence instance")
    require_non_empty_strings(interpretation=interpretation)

    basis = tuple(basis_check_ids)
    if not basis:
        raise ValueError("basis_check_ids must not be empty")
    if any(not isinstance(item, str) or not item.strip() for item in basis):
        raise ValueError("basis check IDs must be non-empty strings")
    if len(basis) != len(set(basis)):
        raise ValueError("basis check IDs must be unique")

    available = {check.check_id for check in convergence.checks}
    missing = set(basis) - available
    if missing:
        raise ValueError("basis check IDs must exist in the convergence")

    ordered_basis = tuple(sorted(basis))
    canonical = canonical_json({
        "basis_check_ids": list(ordered_basis),
        "convergence_decision": convergence.decision,
        "convergence_id": convergence.id,
        "interpretation": interpretation,
        "proposal_id": convergence.proposal_id,
        "version": SCHEMA_VERSION,
    })
    identifier = sha256(canonical.encode("utf-8")).hexdigest()
    return Meaning(
        id=identifier,
        convergence_id=convergence.id,
        proposal_id=convergence.proposal_id,
        interpretation=interpretation,
        basis_check_ids=ordered_basis,
        convergence_decision=convergence.decision,
    )
