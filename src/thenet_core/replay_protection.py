"""Atomic nonce replay protection with an explicit storage boundary.

The in-memory implementation is process-local and non-durable. Production
multi-process deployments must provide a durable, transactional implementation
of the NonceStore protocol (for example, a database uniqueness constraint).
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Protocol, TypeAlias

NonceClaim: TypeAlias = tuple[str, str, str]  # (issuer/key scope, nonce, expires_at)

def _utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("timestamp must be a non-empty UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError("timestamp must include a UTC timezone")
    return parsed.astimezone(timezone.utc)

class NonceStore(Protocol):
    """Atomically claim all nonce values or claim none of them."""
    def claim_many(self, claims: tuple[NonceClaim, ...], now: str) -> bool:
        """Return False if any claim is already active; must be all-or-none."""
        ...

@dataclass(frozen=True, slots=True)
class NonceStoreStats:
    active_claims: int

class InMemoryNonceStore:
    """Thread-safe nonce store for one process; not durable or distributed."""
    def __init__(self) -> None:
        self._lock = Lock()
        self._claims: dict[tuple[str, str], datetime] = {}

    def claim_many(self, claims: tuple[NonceClaim, ...], now: str) -> bool:
        if not isinstance(claims, tuple):
            raise ValueError("claims must be a tuple")
        current = _utc(now)
        parsed: list[tuple[tuple[str, str], datetime]] = []
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
                return False
            seen.add(key)
            parsed.append((key, expiry))
        with self._lock:
            self._claims = {key: expiry for key, expiry in self._claims.items() if expiry > current}
            if any(key in self._claims for key, _ in parsed):
                return False
            self._claims.update(parsed)
            return True

    def stats(self, now: str) -> NonceStoreStats:
        current = _utc(now)
        with self._lock:
            self._claims = {key: expiry for key, expiry in self._claims.items() if expiry > current}
            return NonceStoreStats(active_claims=len(self._claims))
