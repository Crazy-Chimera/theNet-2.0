"""Gamma Convergence: deterministic decision over explicit verification checks."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Sequence

from ._canonical import canonical_json, require_non_empty_strings
from .genesis import SCHEMA_VERSION
from .resonance import Resonance


@dataclass(frozen=True, slots=True)
class VerificationCheck:
    """An explicitly supplied check result; the record does not authenticate itself."""

    check_id: str
    passed: bool
    evidence_digest: str
    version: int = SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class Convergence:
    """Immutable decision snapshot; it never executes or activates a proposal."""

    id: str
    resonance_id: str
    proposal_id: str
    required_check_ids: tuple[str, ...]
    checks: tuple[VerificationCheck, ...]
    decision: str
    missing_check_ids: tuple[str, ...]
    failed_check_ids: tuple[str, ...]
    version: int = SCHEMA_VERSION


def create_verification_check(
    check_id: str,
    passed: bool,
    evidence_digest: str,
) -> VerificationCheck:
    """Create a check result tied to a non-empty evidence digest."""
    require_non_empty_strings(check_id=check_id, evidence_digest=evidence_digest)
    if type(passed) is not bool:
        raise ValueError("passed must be a boolean")
    return VerificationCheck(
        check_id=check_id,
        passed=passed,
        evidence_digest=evidence_digest,
    )


def create_convergence(
    resonance: Resonance,
    proposal_id: str,
    required_check_ids: Sequence[str],
    checks: Sequence[VerificationCheck],
) -> Convergence:
    """Evaluate whether all required checks are present and passing.

    Missing required checks or any failed required check rejects the proposal.
    Duplicate IDs, malformed records and unrequested checks are rejected as
    invalid input. This is deterministic policy evaluation over supplied
    records, not authentication, semantic judgment, execution, or activation.
    """
    if not isinstance(resonance, Resonance):
        raise ValueError("resonance must be a Resonance instance")
    require_non_empty_strings(proposal_id=proposal_id)

    required = tuple(required_check_ids)
    if not required:
        raise ValueError("required_check_ids must not be empty")
    if any(not isinstance(item, str) or not item.strip() for item in required):
        raise ValueError("required check IDs must be non-empty strings")
    if len(required) != len(set(required)):
        raise ValueError("required check IDs must be unique")

    check_items = tuple(checks)
    if any(not isinstance(item, VerificationCheck) for item in check_items):
        raise ValueError("checks must contain only VerificationCheck instances")
    check_ids = [item.check_id for item in check_items]
    if len(check_ids) != len(set(check_ids)):
        raise ValueError("check IDs must be unique")
    unexpected = set(check_ids) - set(required)
    if unexpected:
        raise ValueError("checks contain unrequested check IDs")

    by_id = {item.check_id: item for item in check_items}
    missing = tuple(sorted(set(required) - set(by_id)))
    failed = tuple(sorted(item.check_id for item in check_items if not item.passed))
    decision = "accepted" if not missing and not failed else "rejected"
    ordered_checks = tuple(sorted(check_items, key=lambda item: item.check_id))
    ordered_required = tuple(sorted(required))
    canonical = canonical_json({
        "checks": [
            {
                "check_id": item.check_id,
                "evidence_digest": item.evidence_digest,
                "passed": item.passed,
                "version": item.version,
            }
            for item in ordered_checks
        ],
        "decision": decision,
        "failed_check_ids": list(failed),
        "missing_check_ids": list(missing),
        "proposal_id": proposal_id,
        "required_check_ids": list(ordered_required),
        "resonance_id": resonance.id,
        "version": SCHEMA_VERSION,
    })
    identifier = sha256(canonical.encode("utf-8")).hexdigest()
    return Convergence(
        id=identifier,
        resonance_id=resonance.id,
        proposal_id=proposal_id,
        required_check_ids=ordered_required,
        checks=ordered_checks,
        decision=decision,
        missing_check_ids=missing,
        failed_check_ids=failed,
    )
