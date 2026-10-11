"""Psi Expression: a content-addressed output artifact bound to a Meaning."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from ._canonical import canonical_json, require_non_empty_strings
from .genesis import SCHEMA_VERSION
from .meaning import Meaning


@dataclass(frozen=True, slots=True)
class Expression:
    """Immutable output metadata; raw content is not retained or dispatched."""

    id: str
    meaning_id: str
    channel: str
    format: str
    content_digest: str
    version: int = SCHEMA_VERSION


def create_expression(
    meaning: Meaning,
    channel: str,
    format: str,
    content: str,
) -> Expression:
    """Bind output content to a declared Meaning using a SHA-256 digest.

    The expression records intended channel and format but does not deliver
    content, authenticate the meaning, or claim that an external recipient
    received or accepted anything. Raw content is not retained.
    """
    if not isinstance(meaning, Meaning):
        raise ValueError("meaning must be a Meaning instance")
    require_non_empty_strings(channel=channel, format=format, content=content)

    content_digest = sha256(content.encode("utf-8")).hexdigest()
    canonical = canonical_json({
        "channel": channel,
        "content_digest": content_digest,
        "format": format,
        "meaning_id": meaning.id,
        "version": SCHEMA_VERSION,
    })
    identifier = sha256(canonical.encode("utf-8")).hexdigest()
    return Expression(
        id=identifier,
        meaning_id=meaning.id,
        channel=channel,
        format=format,
        content_digest=content_digest,
    )
