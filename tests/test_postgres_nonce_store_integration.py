"""Live PostgreSQL integration tests; enabled by THENET_TEST_POSTGRES_DSN."""
from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest

psycopg = pytest.importorskip("psycopg")
DSN = os.environ.get("THENET_TEST_POSTGRES_DSN")
if not DSN:
    pytest.skip("THENET_TEST_POSTGRES_DSN is not configured", allow_module_level=True)

from thenet_core.postgres_nonce_store import PostgresNonceStore
from test_authorization import NOW as AUTH_NOW, POLICY, TRUST, decide, evidence
from test_commit_intent import build

MIGRATION = Path(__file__).resolve().parents[1] / "migrations" / "0001_nonce_claims.sql"
NOW = "2026-10-11T07:00:00Z"
EXPIRY = "2026-10-11T08:00:00Z"


@pytest.fixture(autouse=True)
def prepare_table():
    with psycopg.connect(DSN) as conn:
        conn.execute(MIGRATION.read_text(encoding="utf-8"))
        conn.execute((MIGRATION.parent / "0002_authorization_results.sql").read_text(encoding="utf-8"))
        conn.execute("TRUNCATE TABLE thenet_nonce_claims")
        conn.execute("TRUNCATE TABLE thenet_authorization_results")
    yield
    with psycopg.connect(DSN) as conn:
        conn.execute("TRUNCATE TABLE thenet_nonce_claims")
        conn.execute("TRUNCATE TABLE thenet_authorization_results")


def store():
    return PostgresNonceStore(lambda: psycopg.connect(DSN))


def test_persisted_claim_survives_new_store_instance():
    assert store().claim_many((("issuer/key", "durable", EXPIRY),), NOW)
    assert not store().claim_many((("issuer/key", "durable", EXPIRY),), NOW)


def test_conflict_rolls_back_earlier_insert_in_same_batch():
    assert store().claim_many((("issuer/key", "taken", EXPIRY),), NOW)
    assert not store().claim_many(
        (("issuer/key", "fresh", EXPIRY), ("issuer/key", "taken", EXPIRY)), NOW
    )
    with psycopg.connect(DSN) as conn:
        rows = conn.execute(
            "SELECT nonce FROM thenet_nonce_claims ORDER BY nonce"
        ).fetchall()
    assert rows == [("taken",)]


def test_concurrent_independent_connections_have_one_winner():
    workers = 12
    barrier = Barrier(workers)

    def claim(_):
        barrier.wait(timeout=10)
        return store().claim_many((("issuer/key", "race", EXPIRY),), NOW)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        outcomes = list(pool.map(claim, range(workers)))
    assert sum(outcomes) == 1


def test_expired_claim_is_pruned_and_nonce_can_be_reused():
    with psycopg.connect(DSN) as conn:
        conn.execute(
            "INSERT INTO thenet_nonce_claims (scope, nonce, expires_at) VALUES (%s, %s, %s)",
            ("issuer/key", "old", "2026-10-11T06:59:00Z"),
        )
    assert store().claim_many((("issuer/key", "old", EXPIRY),), NOW)

def test_idempotent_result_and_nonce_commit_atomically():
    db = store()
    claims = (("issuer/key", "idempotent", EXPIRY),)
    payload = {"status": "authorized", "operation_id": "op-1"}
    first = db.claim_result("op-1", "digest-a", claims, payload, NOW)
    retry = db.claim_result("op-1", "digest-a", claims, {"status": "ignored"}, NOW)
    assert first == ("stored", payload)
    assert retry == ("existing", payload)


def test_idempotency_key_cannot_be_reused_for_different_request():
    db = store()
    claims = (("issuer/key", "idempotent-conflict", EXPIRY),)
    payload = {"status": "authorized", "operation_id": "op-2"}
    assert db.claim_result("op-2", "digest-a", claims, payload, NOW) == ("stored", payload)
    assert db.claim_result("op-2", "digest-b", claims, payload, NOW) == ("conflict", None)


def test_idempotent_result_rolls_back_when_nonce_conflicts():
    db = store()
    assert db.claim_many((("issuer/key", "already-taken", EXPIRY),), NOW)
    result = db.claim_result(
        "op-3", "digest-c",
        (("issuer/key", "fresh-in-batch", EXPIRY), ("issuer/key", "already-taken", EXPIRY)),
        {"status": "authorized"}, NOW,
    )
    assert result == ("replay", None)
    with psycopg.connect(DSN) as conn:
        assert conn.execute(
            "SELECT operation_id FROM thenet_authorization_results WHERE operation_id = %s",
            ("op-3",),
        ).fetchone() is None
        assert conn.execute(
            "SELECT nonce FROM thenet_nonce_claims WHERE nonce = %s",
            ("fresh-in-batch",),
        ).fetchone() is None


def test_authorization_retry_recovers_result_after_lost_commit_confirmation():
    intent = build()
    attestation = evidence(intent)
    db = store()

    class LostConfirmation:
        first = True

        def claim_result(self, operation_id, request_digest, claims, result_payload, now):
            result = db.claim_result(operation_id, request_digest, claims, result_payload, now)
            if self.first:
                self.first = False
                raise RuntimeError("commit succeeded but confirmation was lost")
            return result

    adapter = LostConfirmation()
    first = decide(intent, (attestation,), now=AUTH_NOW, nonce_store=adapter)
    retry = decide(intent, (attestation,), now=AUTH_NOW, nonce_store=adapter)

    assert (first.status, first.reason) == ("rejected", "nonce_store_unavailable")
    assert (retry.status, retry.reason) == ("authorized", "policy_evidence_and_nonce_valid")
    assert retry.decided_at == AUTH_NOW
    with psycopg.connect(DSN) as conn:
        assert conn.execute(
            "SELECT COUNT(*) FROM thenet_authorization_results WHERE operation_id = %s",
            (intent.id,),
        ).fetchone()[0] == 1
        assert conn.execute(
            "SELECT COUNT(*) FROM thenet_nonce_claims WHERE nonce = %s",
            (attestation.nonce,),
        ).fetchone()[0] == 1


def test_concurrent_authorization_retries_return_one_persisted_decision():
    intent = build()
    attestation = evidence(intent)
    workers = 8
    barrier = Barrier(workers)

    def authorize(_):
        barrier.wait(timeout=10)
        return decide(intent, (attestation,), now=AUTH_NOW, nonce_store=store())

    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(authorize, range(workers)))

    assert all(result.status == "authorized" for result in results)
    assert len(set(results)) == 1
    with psycopg.connect(DSN) as conn:
        assert conn.execute(
            "SELECT COUNT(*) FROM thenet_authorization_results WHERE operation_id = %s",
            (intent.id,),
        ).fetchone()[0] == 1
        assert conn.execute(
            "SELECT COUNT(*) FROM thenet_nonce_claims WHERE nonce = %s",
            (attestation.nonce,),
        ).fetchone()[0] == 1


def test_same_intent_with_different_policy_digest_is_rejected():
    from dataclasses import replace

    intent = build()
    attestation = evidence(intent)
    db = store()
    first = decide(intent, (attestation,), now=AUTH_NOW, nonce_store=db)
    changed_policy = replace(POLICY, version=POLICY.version + 1)
    conflict = decide(intent, (attestation,), policy=changed_policy, now=AUTH_NOW, nonce_store=db)

    assert first.status == "authorized"
    assert (conflict.status, conflict.reason) == ("rejected", "idempotency_key_conflict")
