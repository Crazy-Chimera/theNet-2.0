"""Ed25519 attestations and explicit local trust-policy verification."""

from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from ._canonical import canonical_json, require_non_empty_strings
from .genesis import SCHEMA_VERSION


def _parse_utc(value: str, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError(f"{field} must include a UTC timezone")
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class TrustedKey:
    """A locally configured trust entry; configuration provenance is external."""

    key_id: str
    issuer_id: str
    public_key: bytes
    allowed_contexts: tuple[str, ...]
    revoked: bool = False
    version: int = SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SignedAttestation:
    """Signed claims about a subject and content digest; not the content itself."""

    id: str
    issuer_id: str
    subject_id: str
    context: str
    payload_digest: str
    issued_at: str
    expires_at: str
    nonce: str
    key_id: str
    signature: str
    version: int = SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class AttestationVerification:
    """Result of applying a local trust policy at a specified instant."""

    attestation_id: str
    status: str
    reason: str
    policy_key_id: str
    verified_at: str
    version: int = SCHEMA_VERSION


def _signed_payload(issuer_id, subject_id, context, payload_digest, issued_at, expires_at, nonce, key_id) -> bytes:
    return canonical_json({
        "context": context, "expires_at": expires_at, "issued_at": issued_at,
        "issuer_id": issuer_id, "key_id": key_id, "nonce": nonce,
        "payload_digest": payload_digest, "subject_id": subject_id,
        "version": SCHEMA_VERSION,
    }).encode("utf-8")


def create_signed_attestation(
    private_key: Ed25519PrivateKey, issuer_id: str, subject_id: str, context: str,
    payload: str, issued_at: str, expires_at: str, nonce: str, key_id: str,
) -> SignedAttestation:
    """Sign canonical claims; key custody and real-world identity proof are external."""
    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("private_key must be an Ed25519PrivateKey")
    require_non_empty_strings(issuer_id=issuer_id, subject_id=subject_id, context=context,
                              payload=payload, nonce=nonce, key_id=key_id)
    issued = _parse_utc(issued_at, "issued_at")
    expires = _parse_utc(expires_at, "expires_at")
    if expires <= issued:
        raise ValueError("expires_at must be later than issued_at")
    digest = sha256(payload.encode("utf-8")).hexdigest()
    body = _signed_payload(issuer_id, subject_id, context, digest, issued_at, expires_at, nonce, key_id)
    signature = base64.b64encode(private_key.sign(body)).decode("ascii")
    identifier = sha256(body + b"." + signature.encode("ascii")).hexdigest()
    return SignedAttestation(identifier, issuer_id, subject_id, context, digest, issued_at,
                             expires_at, nonce, key_id, signature)


def verify_attestation(
    attestation: SignedAttestation, trusted_keys: Mapping[str, TrustedKey], now: str,
) -> AttestationVerification:
    """Verify Ed25519 signature and the supplied local trust policy."""
    if not isinstance(attestation, SignedAttestation):
        raise ValueError("attestation must be a SignedAttestation instance")
    if not isinstance(trusted_keys, Mapping):
        raise ValueError("trusted_keys must be a mapping")
    current = _parse_utc(now, "now")
    verified_at = current.isoformat().replace("+00:00", "Z")
    key = trusted_keys.get(attestation.key_id)
    if not isinstance(key, TrustedKey):
        return AttestationVerification(attestation.id, "rejected", "unknown_key", attestation.key_id, verified_at)
    if key.key_id != attestation.key_id or key.issuer_id != attestation.issuer_id:
        return AttestationVerification(attestation.id, "rejected", "issuer_or_key_mismatch", key.key_id, verified_at)
    if key.revoked:
        return AttestationVerification(attestation.id, "rejected", "key_revoked", key.key_id, verified_at)
    if attestation.context not in key.allowed_contexts:
        return AttestationVerification(attestation.id, "rejected", "context_not_allowed", key.key_id, verified_at)
    try:
        issued = _parse_utc(attestation.issued_at, "issued_at")
        expires = _parse_utc(attestation.expires_at, "expires_at")
        if expires <= issued:
            return AttestationVerification(attestation.id, "rejected", "invalid_validity_window", key.key_id, verified_at)
        if current < issued:
            return AttestationVerification(attestation.id, "rejected", "not_yet_valid", key.key_id, verified_at)
        if current >= expires:
            return AttestationVerification(attestation.id, "rejected", "expired", key.key_id, verified_at)
        if len(key.public_key) != 32:
            return AttestationVerification(attestation.id, "rejected", "invalid_public_key", key.key_id, verified_at)
        signature = base64.b64decode(attestation.signature, validate=True)
        body = _signed_payload(attestation.issuer_id, attestation.subject_id, attestation.context,
                               attestation.payload_digest, attestation.issued_at, attestation.expires_at,
                               attestation.nonce, attestation.key_id)
        Ed25519PublicKey.from_public_bytes(key.public_key).verify(signature, body)
        expected_id = sha256(body + b"." + attestation.signature.encode("ascii")).hexdigest()
        if attestation.id != expected_id:
            return AttestationVerification(attestation.id, "rejected", "attestation_id_mismatch", key.key_id, verified_at)
    except (ValueError, TypeError, binascii.Error):
        return AttestationVerification(attestation.id, "rejected", "malformed_attestation", key.key_id, verified_at)
    except InvalidSignature:
        return AttestationVerification(attestation.id, "rejected", "invalid_signature", key.key_id, verified_at)
    return AttestationVerification(attestation.id, "verified", "signature_and_policy_valid", key.key_id, verified_at)


def raw_public_key(private_key: Ed25519PrivateKey) -> bytes:
    """Export public bytes for trust provisioning; never export the private key."""
    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("private_key must be an Ed25519PrivateKey")
    return private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
