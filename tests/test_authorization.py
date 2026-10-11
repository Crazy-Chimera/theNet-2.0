from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from thenet_core import TrustedKey, authorize_commit_intent, authorization_evidence_payload, create_signed_attestation, raw_public_key
from thenet_core.authorization import AuthorizationPolicy
from thenet_core.replay_protection import InMemoryNonceStore
from test_commit_intent import build

NOW = "2026-10-11T06:00:00Z"
ISSUED = "2026-10-11T05:00:00Z"
EXPIRES = "2026-10-11T07:00:00Z"
PRIVATE = Ed25519PrivateKey.generate()
TRUST = {"key:issuer-a": TrustedKey("key:issuer-a", "issuer:a", raw_public_key(PRIVATE), ("theNet:commit-intent", "other"))}
POLICY = AuthorizationPolicy(("propose",), ("system:core",), "theNet:commit-intent", ("issuer:a",))

def evidence(intent=None, **overrides):
    intent = intent or build()
    args = dict(private_key=PRIVATE, issuer_id="issuer:a", subject_id=intent.identity_binding,
        context="theNet:commit-intent", payload=authorization_evidence_payload(intent),
        issued_at=ISSUED, expires_at=EXPIRES, nonce="nonce:authorization-001", key_id="key:issuer-a")
    args.update(overrides)
    return create_signed_attestation(**args)

def decide(intent=None, attestations=None, policy=POLICY, trusted_keys=TRUST, now=NOW, nonce_store=None):
    intent = intent or build()
    return authorize_commit_intent(intent, tuple(attestations if attestations is not None else (evidence(intent),)),
                                   trusted_keys, policy, now, nonce_store or InMemoryNonceStore())

def test_valid_bound_evidence_authorizes_decision_only():
    intent = build()
    item = evidence(intent)
    result = decide(intent, (item,))
    assert (result.status, result.reason) == ("authorized", "policy_evidence_and_nonce_valid")
    assert result.intent_id == intent.id and result.evidence_ids == (item.id,)
    assert intent.authorization_status == "not_authorized"
    assert not hasattr(result, "commit_sha") and not hasattr(result, "executed_at")

def test_replay_is_rejected_on_second_use():
    intent = build()
    item = evidence(intent)
    store = InMemoryNonceStore()
    assert decide(intent, (item,), nonce_store=store).status == "authorized"
    second = decide(intent, (item,), nonce_store=store)
    assert (second.status, second.reason) == ("rejected", "replay_detected")

def test_missing_nonce_store_fails_closed():
    intent = build()
    item = evidence(intent)
    result = authorize_commit_intent(intent, (item,), TRUST, POLICY, NOW)
    assert (result.status, result.reason) == ("rejected", "replay_store_required")

def test_store_claims_are_atomic_when_one_nonce_repeats():
    store = InMemoryNonceStore()
    assert store.claim_many((("issuer-a/key-a", "n1", EXPIRES),), NOW)
    assert not store.claim_many((("issuer-a/key-a", "n2", EXPIRES), ("issuer-a/key-a", "n1", EXPIRES)), NOW)
    assert store.stats(NOW).active_claims == 1
    assert not store.claim_many((("issuer-a/key-a", "n2", EXPIRES), ("issuer-a/key-a", "n2", EXPIRES)), NOW)
    assert store.stats(NOW).active_claims == 1

def test_concurrent_claim_has_single_winner():
    store = InMemoryNonceStore()
    def claim(_):
        return store.claim_many((("issuer/key", "same", EXPIRES),), NOW)
    with ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(claim, range(64)))
    assert sum(results) == 1

def test_expired_claim_is_pruned_and_nonce_can_be_reused_after_expiry():
    store = InMemoryNonceStore()
    assert store.claim_many((("issuer/key", "n", EXPIRES),), NOW)
    after = "2026-10-11T07:00:00Z"
    assert store.stats(after).active_claims == 0
    assert store.claim_many((("issuer/key", "n", "2026-10-11T08:00:00Z"),), after)

def test_action_allowlist():
    intent = build(action="delete")
    assert decide(intent, attestations=()).reason == "action_not_allowed"

def test_target_allowlist():
    intent = build(target="system:other")
    assert decide(intent, attestations=()).reason == "target_not_allowed"

def test_missing_evidence_rejected():
    assert decide(attestations=()).reason == "required_issuer_evidence_missing"

def test_evidence_for_another_intent_rejected():
    other = build(proposed_change="different change")
    assert decide(intent=build(), attestations=(evidence(other),)).reason == "evidence_does_not_bind_intent"

def test_wrong_subject_rejected():
    intent = build()
    assert decide(intent, (evidence(intent, subject_id="agent:other"),)).reason == "evidence_subject_mismatch"

def test_unknown_or_revoked_key_rejected():
    intent = build()
    item = evidence(intent)
    assert decide(intent, (item,), trusted_keys={}).reason == "evidence_unknown_key"
    revoked = {"key:issuer-a": TrustedKey("key:issuer-a", "issuer:a", raw_public_key(PRIVATE),
                                           ("theNet:commit-intent", "other"), True)}
    assert decide(intent, (item,), trusted_keys=revoked).reason == "evidence_key_revoked"

def test_wrong_context_rejected():
    intent = build()
    assert decide(intent, (evidence(intent, context="other"),)).reason == "evidence_context_mismatch"

def test_duplicate_evidence_and_required_issuer_policy():
    intent = build()
    item = evidence(intent)
    assert decide(intent, (item, item)).reason == "duplicate_attestation"
    two = AuthorizationPolicy(("propose",), ("system:core",), "theNet:commit-intent", ("issuer:a", "issuer:b"))
    assert decide(intent, (item,), policy=two).reason == "required_issuer_evidence_missing"

def test_immutable_and_deterministic_for_fresh_store():
    intent = build()
    item = evidence(intent)
    one, two = decide(intent, (item,)), decide(intent, (item,))
    assert one == two
    with pytest.raises(FrozenInstanceError):
        one.status = "executed"

def test_input_validation():
    with pytest.raises(ValueError, match="CommitIntent"):
        authorization_evidence_payload(object())
    with pytest.raises(ValueError, match="AuthorizationPolicy"):
        authorize_commit_intent(build(), (), TRUST, object(), NOW)
