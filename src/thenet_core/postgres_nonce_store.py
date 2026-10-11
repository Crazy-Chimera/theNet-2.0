"""PostgreSQL-backed, durable implementation of the NonceStore contract.

The adapter uses only Python's DB-API 2.0 surface; supply a connection factory
for a PostgreSQL driver such as psycopg. The migration must be applied first.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Callable, Any, Mapping

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

    def claim_result(
        self,
        operation_id: str,
        request_digest: str,
        claims: tuple[NonceClaim, ...],
        result_payload: Mapping[str, Any],
        now: str,
    ) -> tuple[str, dict[str, Any] | None]:
        """Atomically persist nonce claims and an idempotent operation result."""
        if not isinstance(operation_id, str) or not operation_id.strip():
            raise ValueError("operation_id must be a non-empty string")
        if not isinstance(request_digest, str) or not request_digest.strip():
            raise ValueError("request_digest must be a non-empty string")
        if not isinstance(result_payload, Mapping):
            raise ValueError("result_payload must be a mapping")
        if not isinstance(claims, tuple) or not claims:
            raise ValueError("claims must be a non-empty tuple")
        current = _utc(now)
        parsed: list[tuple[str, str, datetime]] = []
        seen: set[tuple[str, str]] = set()
        for item in claims:
            if not isinstance(item, tuple) or len(item) != 3:
                raise ValueError("each nonce claim must contain scope, nonce and expiry")
            scope, nonce, expires_at = item
            if not isinstance(scope, str) or not scope.strip() or not isinstance(nonce, str) or not nonce.strip():
                raise ValueError("nonce scope and value must be non-empty strings")
            expiry = _utc(expires_at)
            if expiry <= current:
                raise ValueError("nonce claim expiry must be later than now")
            key = (scope, nonce)
            if key in seen:
                return ("replay", None)
            seen.add(key)
            parsed.append((scope, nonce, expiry))
        payload = dict(result_payload)
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        expires_at = min(item[2] for item in parsed)
        connection = self._connection_factory()
        cursor = None
        try:
            if hasattr(connection, "autocommit"):
                connection.autocommit = False
            cursor = connection.cursor()
            cursor.execute("DELETE FROM thenet_nonce_claims WHERE expires_at <= %s", (current,))
            cursor.execute("DELETE FROM thenet_authorization_results WHERE expires_at <= %s", (current,))
            cursor.execute(
                "INSERT INTO thenet_authorization_results "
                "(operation_id, request_digest, result_json, expires_at) "
                "VALUES (%s, %s, %s, %s) ON CONFLICT (operation_id) DO NOTHING",
                (operation_id, request_digest, encoded, expires_at),
            )
            if cursor.rowcount != 1:
                cursor.execute(
                    "SELECT request_digest, result_json FROM thenet_authorization_results "
                    "WHERE operation_id = %s FOR UPDATE",
                    (operation_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    connection.rollback()
                    return ("conflict", None)
                existing_digest, existing_json = row
                connection.commit()
                if existing_digest != request_digest:
                    return ("conflict", None)
                if isinstance(existing_json, str):
                    existing_json = json.loads(existing_json)
                return ("existing", dict(existing_json))
            for scope, nonce, expiry in parsed:
                cursor.execute(
                    "INSERT INTO thenet_nonce_claims (scope, nonce, expires_at) "
                    "VALUES (%s, %s, %s) ON CONFLICT (scope, nonce) DO NOTHING",
                    (scope, nonce, expiry),
                )
                if cursor.rowcount != 1:
                    connection.rollback()
                    return ("replay", None)
            connection.commit()
            return ("stored", payload)
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()
