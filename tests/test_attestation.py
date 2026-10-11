from dataclasses import FrozenInstanceError

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from thenet_core import SignedAttestation, TrustedKey, create_signed_attestation, raw_public_key, verify_attestation

NOW = "2026-10-11T06:00:00Z"
ISSUED = "2026-10-11T05:00:00Z"
EXPIRES = "2026-10-11T07:00:00Z"
PRIVATE = Ed25519PrivateKey.generate()
PUBLIC = raw_public_key(PRIVATE)
TRUST = {"key:issuer-a": TrustedKey("key:issuer-a", "issuer:a", PUBLIC, ("theNet:evolution",))}


def signed(**overrides):
    args = dict(private_key=PRIVATE, issuer_id="issuer:a", subject_id="agent:a",
                context="theNet:evolution", payload="approved proposal digest source",
                issued_at=ISSUED, expires_at=EXPIRES, nonce="nonce:001", key_id="key:issuer-a")
    args.update(overrides)
    return create_signed_attestation(**args)


def test_valid_signature_and_policy():
    result = verify_attestation(signed(), TRUST, NOW)
    assert (result.status, result.reason) == ("verified", "signature_and_policy_valid")


def test_wrong_key_rejected():
    other = Ed25519PrivateKey.generate()
    policy = {"key:issuer-a": TrustedKey("key:issuer-a", "issuer:a", raw_public_key(other), ("theNet:evolution",))}
    assert verify_attestation(signed(), policy, NOW).reason == "invalid_signature"


@pytest.mark.parametrize("policy,reason", [
    ({}, "unknown_key"),
    ({"key:issuer-a": TrustedKey("key:issuer-a", "issuer:other", PUBLIC, ("theNet:evolution",))}, "issuer_or_key_mismatch"),
    ({"key:issuer-a": TrustedKey("key:issuer-a", "issuer:a", PUBLIC, ("theNet:evolution",), True)}, "key_revoked"),
    ({"key:issuer-a": TrustedKey("key:issuer-a", "issuer:a", PUBLIC, ("other",))}, "context_not_allowed"),
])
def test_policy_rejections(policy, reason):
    result = verify_attestation(signed(), policy, NOW)
    assert (result.status, result.reason) == ("rejected", reason)


def test_expiry_and_future_issued_time():
    assert verify_attestation(signed(), TRUST, EXPIRES).reason == "expired"
    assert verify_attestation(signed(issued_at="2026-10-11T06:30:00Z"), TRUST, NOW).reason == "not_yet_valid"


def test_tampering_rejects():
    original = signed()
    tampered = SignedAttestation(original.id, original.issuer_id, "agent:forged", original.context,
                                 original.payload_digest, original.issued_at, original.expires_at,
                                 original.nonce, original.key_id, original.signature)
    assert verify_attestation(tampered, TRUST, NOW).reason == "invalid_signature"


def test_invalid_window_naive_time_and_types():
    with pytest.raises(ValueError, match="later"):
        signed(expires_at=ISSUED)
    with pytest.raises(ValueError, match="UTC"):
        signed(issued_at="2026-10-11T05:00:00")
    with pytest.raises(ValueError, match="Ed25519PrivateKey"):
        create_signed_attestation(object(), "i", "s", "c", "p", ISSUED, EXPIRES, "n", "k")
    with pytest.raises(ValueError, match="attestation"):
        verify_attestation(object(), TRUST, NOW)
    with pytest.raises(ValueError, match="subject_id"):
        signed(subject_id=" ")


def test_records_immutable_and_do_not_retain_payload():
    attestation = signed()
    result = verify_attestation(attestation, TRUST, NOW)
    with pytest.raises(FrozenInstanceError):
        result.status = "accepted"
    assert not hasattr(attestation, "payload")
    assert attestation.payload_digest

def test_attestation_id_is_bound_to_signed_content():
    original = signed()
    tampered = SignedAttestation(
        "f" * 64, original.issuer_id, original.subject_id, original.context,
        original.payload_digest, original.issued_at, original.expires_at,
        original.nonce, original.key_id, original.signature,
    )
    result = verify_attestation(tampered, TRUST, NOW)
    assert (result.status, result.reason) == ("rejected", "attestation_id_mismatch")
