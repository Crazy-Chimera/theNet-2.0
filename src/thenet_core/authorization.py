"""Policy-gated authorization decisions for prepared CommitIntent records."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from typing import Mapping
from ._canonical import canonical_json, require_non_empty_strings
from .attestation import SignedAttestation, TrustedKey, verify_attestation
from .commit_intent import CommitIntent
from .genesis import SCHEMA_VERSION
from .replay_protection import NonceStore

@dataclass(frozen=True, slots=True)
class AuthorizationPolicy:
    """Caller-provided local policy; provenance and integrity are external."""
    allowed_actions: tuple[str, ...]
    allowed_targets: tuple[str, ...]
    required_context: str
    required_issuers: tuple[str, ...]
    version: int = SCHEMA_VERSION

@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    """Immutable decision record; it is not an execution capability."""
    intent_id: str
    status: str
    reason: str
    evidence_ids: tuple[str, ...]
    decided_at: str
    version: int = SCHEMA_VERSION

def authorization_evidence_payload(intent: CommitIntent) -> str:
    """Return canonical payload an issuer must sign for this exact intent."""
    if not isinstance(intent, CommitIntent):
        raise ValueError("intent must be a CommitIntent instance")
    return canonical_json({
        "action": intent.action, "identity_binding": intent.identity_binding,
        "intent_id": intent.id, "proposed_change_digest": intent.proposed_change_digest,
        "target": intent.target, "version": SCHEMA_VERSION,
    })

def _reject(intent: CommitIntent, reason: str, evidence_ids: tuple[str, ...], now: str) -> AuthorizationDecision:
    return AuthorizationDecision(intent.id, "rejected", reason, evidence_ids, now)

def authorize_commit_intent(
    intent: CommitIntent, attestations: tuple[SignedAttestation, ...],
    trusted_keys: Mapping[str, TrustedKey], policy: AuthorizationPolicy, now: str,
    nonce_store: NonceStore | None = None,
) -> AuthorizationDecision:
    """Re-verify intent-bound evidence and atomically consume its nonces.

    A durable, shared NonceStore is required for production use. The decision
    remains descriptive only; it is not an execution capability.
    """
    if not isinstance(intent, CommitIntent):
        raise ValueError("intent must be a CommitIntent instance")
    if not isinstance(policy, AuthorizationPolicy):
        raise ValueError("policy must be an AuthorizationPolicy instance")
    if not isinstance(attestations, tuple) or any(not isinstance(item, SignedAttestation) for item in attestations):
        raise ValueError("attestations must be a tuple of SignedAttestation records")
    if not isinstance(trusted_keys, Mapping):
        raise ValueError("trusted_keys must be a mapping")
    require_non_empty_strings(now=now, required_context=policy.required_context)
    if nonce_store is not None and not callable(getattr(nonce_store, "claim_many", None)):
        raise ValueError("nonce_store must implement claim_many")
    if not policy.required_issuers or any(not isinstance(v, str) or not v.strip() for v in policy.required_issuers):
        raise ValueError("required_issuers must contain non-empty issuer IDs")
    if len(set(policy.required_issuers)) != len(policy.required_issuers):
        raise ValueError("required_issuers must be unique")
    if not policy.allowed_actions or not policy.allowed_targets:
        return _reject(intent, "policy_has_empty_allowlist", (), now)
    if intent.status != "prepared" or intent.authorization_status != "not_authorized":
        return _reject(intent, "intent_not_prepared", (), now)
    if intent.action not in policy.allowed_actions:
        return _reject(intent, "action_not_allowed", (), now)
    if intent.target not in policy.allowed_targets:
        return _reject(intent, "target_not_allowed", (), now)
    evidence_ids = tuple(sorted(item.id for item in attestations))
    if len(set(evidence_ids)) != len(evidence_ids):
        return _reject(intent, "duplicate_attestation", evidence_ids, now)
    expected_digest = sha256(authorization_evidence_payload(intent).encode("utf-8")).hexdigest()
    valid_issuers: set[str] = set()
    claims: list[tuple[str, str, str]] = []
    for attestation in attestations:
        verification = verify_attestation(attestation, trusted_keys, now)
        if verification.status != "verified":
            return _reject(intent, "evidence_" + verification.reason, evidence_ids, now)
        if attestation.subject_id != intent.identity_binding:
            return _reject(intent, "evidence_subject_mismatch", evidence_ids, now)
        if attestation.context != policy.required_context:
            return _reject(intent, "evidence_context_mismatch", evidence_ids, now)
        if attestation.payload_digest != expected_digest:
            return _reject(intent, "evidence_does_not_bind_intent", evidence_ids, now)
        if attestation.issuer_id not in policy.required_issuers:
            return _reject(intent, "issuer_not_required", evidence_ids, now)
        if attestation.issuer_id in valid_issuers:
            return _reject(intent, "duplicate_issuer_evidence", evidence_ids, now)
        valid_issuers.add(attestation.issuer_id)
        claims.append((attestation.issuer_id + "/" + attestation.key_id, attestation.nonce, attestation.expires_at))
    if set(policy.required_issuers) - valid_issuers:
        return _reject(intent, "required_issuer_evidence_missing", evidence_ids, now)
    if nonce_store is None:
        return _reject(intent, "replay_store_required", evidence_ids, now)
    try:
        claimed = nonce_store.claim_many(tuple(claims), now)
    except Exception:
        # Storage outages and transaction errors must never become authorization.
        # Keep the decision non-sensitive; operational details belong in protected logs.
        return _reject(intent, "nonce_store_unavailable", evidence_ids, now)
    if not claimed:
        return _reject(intent, "replay_detected", evidence_ids, now)
    return AuthorizationDecision(intent.id, "authorized", "policy_evidence_and_nonce_valid", evidence_ids, now)
