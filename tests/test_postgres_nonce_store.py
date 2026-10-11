from __future__ import annotations

from datetime import datetime, timezone

import pytest

from thenet_core.postgres_nonce_store import PostgresNonceStore

NOW = "2026-10-11T07:00:00Z"
EXPIRY = "2026-10-11T08:00:00Z"


class FakeCursor:
    def __init__(self, conflict_at: int | None = None, fail_at: int | None = None):
        self.rowcount = 1
        self.statements: list[tuple[str, tuple]] = []
        self.conflict_at = conflict_at
        self.fail_at = fail_at
        self.insert_count = 0
        self.closed = False

    def execute(self, sql, params=()):
        self.statements.append((sql, params))
        if sql.startswith("INSERT"):
            self.insert_count += 1
            if self.fail_at == self.insert_count:
                raise RuntimeError("database unavailable")
            self.rowcount = 0 if self.conflict_at == self.insert_count else 1
        else:
            self.rowcount = 1

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, cursor: FakeCursor):
        self._cursor = cursor
        self.autocommit = True
        self.commits = 0
        self.rollbacks = 0
        self.closed = False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True


def make_store(cursor):
    connection = FakeConnection(cursor)
    store = PostgresNonceStore(lambda: connection)
    return store, connection


def test_claim_many_commits_whole_batch_and_uses_unique_constraint():
    cursor = FakeCursor()
    store, connection = make_store(cursor)

    assert store.claim_many((("issuer/key", "n1", EXPIRY), ("issuer/key", "n2", EXPIRY)), NOW)
    assert connection.commits == 1
    assert connection.rollbacks == 0
    assert connection.autocommit is False
    assert connection.closed and cursor.closed
    assert "DELETE FROM thenet_nonce_claims" in cursor.statements[0][0]
    assert all("ON CONFLICT (scope, nonce) DO NOTHING" in sql for sql, _ in cursor.statements[1:])


def test_conflict_rolls_back_every_claim_in_batch():
    cursor = FakeCursor(conflict_at=2)
    store, connection = make_store(cursor)

    assert not store.claim_many((("issuer/key", "n1", EXPIRY), ("issuer/key", "n2", EXPIRY)), NOW)
    assert connection.commits == 0
    assert connection.rollbacks == 1
    assert connection.closed


def test_database_failure_rolls_back_and_propagates():
    cursor = FakeCursor(fail_at=2)
    store, connection = make_store(cursor)

    with pytest.raises(RuntimeError, match="database unavailable"):
        store.claim_many((("issuer/key", "n1", EXPIRY), ("issuer/key", "n2", EXPIRY)), NOW)
    assert connection.commits == 0
    assert connection.rollbacks == 1
    assert connection.closed and cursor.closed


def test_duplicate_claim_inside_batch_is_rejected_before_opening_connection():
    calls = 0

    def factory():
        nonlocal calls
        calls += 1
        raise AssertionError("connection must not be opened")

    store = PostgresNonceStore(factory)
    assert not store.claim_many((("issuer/key", "same", EXPIRY), ("issuer/key", "same", EXPIRY)), NOW)
    assert calls == 0


def test_invalid_or_expired_claim_is_rejected_before_opening_connection():
    store = PostgresNonceStore(lambda: pytest.fail("connection must not be opened"))
    with pytest.raises(ValueError, match="later than now"):
        store.claim_many((("issuer/key", "n1", NOW),), NOW)


def test_empty_batch_is_a_noop():
    store = PostgresNonceStore(lambda: pytest.fail("connection must not be opened"))
    assert store.claim_many((), NOW)
