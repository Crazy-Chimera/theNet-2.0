"""PostgreSQL-backed, durable implementation of the NonceStore contract.

The adapter uses only Python's DB-API 2.0 surface; supply a connection factory
for a PostgreSQL driver such as psycopg. The migration must be applied first.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Any

from .replay_protection import NonceClaim, _utc


class PostgresNonceStore:
    """Atomic cross-process nonce claims backed by PostgreSQL uniqueness.

    A fresh connection is requested for each claim batch. A conflict or duplicate
    inside the batch rolls back every insert. Database errors are rolled back and
    re-raised so callers can fail closed rather than misreporting a replay.
    """

    def __init__(self, connection_factory: Callable[[], Any]) -> None:
        if not callable(connection_factory):
            raise ValueError("connection_factory must be callable")
        self._connection_factory = connection_factory

    def claim_many(self, claims: tuple[NonceClaim, ...], now: str) -> bool:
        if not isinstance(claims, tuple):
            raise ValueError("claims must be a tuple")
        current = _utc(now)
        parsed: list[tuple[str, str, datetime]] = []
        seen: set[tuple[str, str]] = set()
        for item in claims:
            if not isinstance(item, tuple) or len(item) != 3:
                raise ValueError("each nonce claim must contain scope, nonce and expiry")
            scope, nonce, expires_at = item
            if not isinstance(scope, str) or not scope.strip():
                raise ValueError("nonce scope must be a non-empty string")
            if not isinstance(nonce, str) or not nonce.strip():
                raise ValueError("nonce must be a non-empty string")
            expiry = _utc(expires_at)
            if expiry <= current:
                raise ValueError("nonce claim expiry must be later than now")
            key = (scope, nonce)
            if key in seen:
                return False
            seen.add(key)
            parsed.append((scope, nonce, expiry))

        if not parsed:
            return True

        connection = self._connection_factory()
        cursor = None
        try:
            # DB-API connections default to transactional mode in supported
            # PostgreSQL drivers; explicitly disable autocommit where exposed.
            if hasattr(connection, "autocommit"):
                connection.autocommit = False
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM thenet_nonce_claims WHERE expires_at <= %s",
                (current,),
            )
            for scope, nonce, expiry in parsed:
                cursor.execute(
                    "INSERT INTO thenet_nonce_claims (scope, nonce, expires_at) "
                    "VALUES (%s, %s, %s) ON CONFLICT (scope, nonce) DO NOTHING",
                    (scope, nonce, expiry),
                )
                if cursor.rowcount != 1:
                    connection.rollback()
                    return False
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()
