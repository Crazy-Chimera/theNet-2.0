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

MIGRATION = Path(__file__).resolve().parents[1] / "migrations" / "0001_nonce_claims.sql"
NOW = "2026-10-11T07:00:00Z"
EXPIRY = "2026-10-11T08:00:00Z"


@pytest.fixture(autouse=True)
def prepare_table():
    with psycopg.connect(DSN) as conn:
        conn.execute(MIGRATION.read_text(encoding="utf-8"))
        conn.execute("TRUNCATE TABLE thenet_nonce_claims")
    yield
    with psycopg.connect(DSN) as conn:
        conn.execute("TRUNCATE TABLE thenet_nonce_claims")


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
