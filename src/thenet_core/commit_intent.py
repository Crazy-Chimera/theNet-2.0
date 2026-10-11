"""Prepared commit intent for bounded, non-executing system evolution."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from ._canonical import canonical_json, require_non_empty_strings
from .closure import Closure
from .genesis import SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CommitIntent:
    """A prepared change proposal; this record grants no execution authority."""

    id: str
    closure_id: str
    identity_binding: str
    action: str
    target: str
    proposed_change_digest: str
    status: str
    authorization_status: str
    version: int = SCHEMA_VERSION


def create_commit_intent(
    closure: Closure,
    action: str,
    target: str,
    proposed_change: str,
) -> CommitIntent:
    """Prepare an intent only when the declared decision and assent gates pass.

    The closure remains externally unverified. Therefore this function always
    returns status="prepared" and authorization_status="not_authorized"; it
    never executes a change, mutates system state, or creates a Git commit.
    """
    if not isinstance(closure, Closure):
        raise ValueError("closure must be a Closure instance")
    require_non_empty_strings(action=action, target=target, proposed_change=proposed_change)
    if closure.convergence_decision != "accepted":
        raise ValueError("commit intent requires an accepted convergence decision")
    if closure.agreement_status != "agreed":
        raise ValueError("commit intent requires unanimous declared assent")
    if closure.verification_status != "unverified":
        raise ValueError("closure verification status is outside the supported contract")

    proposed_change_digest = sha256(proposed_change.encode("utf-8")).hexdigest()
    payload = {
        "action": action,
        "authorization_status": "not_authorized",
        "closure_id": closure.id,
        "identity_binding": closure.self_knowledge_id,
        "proposed_change_digest": proposed_change_digest,
        "status": "prepared",
        "target": target,
        "version": SCHEMA_VERSION,
    }
    identifier = sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return CommitIntent(
        id=identifier,
        closure_id=closure.id,
        identity_binding=closure.self_knowledge_id,
        action=action,
        target=target,
        proposed_change_digest=proposed_change_digest,
        status="prepared",
        authorization_status="not_authorized",
    )
