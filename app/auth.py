"""API-key authentication for /v1.

GUARD DIRECTION (KEEL Principle 6): this guard fails CLOSED.
  - Key missing from the request            -> 401
  - Key wrong                               -> 401
  - Server has no key configured (unset/"") -> 503, never "let everyone in"

The key lives in the platform as a Fly secret named exactly STOCKGRADER_API_KEY
(Principle 4). It is never read from a file in this repo.

Scope: this guard authenticates. Rate limiting and per-client keys are not
built yet; they are tracked as an open ruling (D-006 in docs/decisions.md),
not as a blind spot of this guard.
"""
import os
import secrets

from fastapi import Header, HTTPException, status

API_KEY_ENV = "STOCKGRADER_API_KEY"


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    configured = os.environ.get(API_KEY_ENV, "")
    if not configured:
        # Misconfiguration is an error, not an open door.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Server API key not configured.",
        )
    if x_api_key is None or not secrets.compare_digest(x_api_key, configured):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid X-API-Key header.",
        )
