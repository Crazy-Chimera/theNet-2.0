"""Canonical encoding helpers shared by immutable domain primitives."""

from __future__ import annotations

import json
from typing import Any


def canonical_json(payload: dict[str, Any]) -> str:
    """Serialize JSON-compatible data with stable key and separator ordering."""
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def require_non_empty_strings(**values: object) -> None:
    """Reject missing, non-string, or whitespace-only required fields."""
    for name, value in values.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a non-empty string")
