"""JWT token service (API tokenização)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt


@dataclass(frozen=True)
class TokenPayload:
    """Token payload normalized."""

    sub: str  # user id
    perfil: str
    iat: int
    exp: int


class TokenService:
    """Service for JWT token encoding/decoding (HS256)."""

    def __init__(self, secret_key: str, exp_seconds: int = 3600, issuer: str = "askly"):
        self._secret_key = secret_key
        self._exp_seconds = exp_seconds
        self._issuer = issuer

    def create_access_token(self, user_id: str, perfil: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "perfil": perfil,
            "iss": self._issuer,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=self._exp_seconds)).timestamp()),
            "type": "access",
        }
        return jwt.encode(payload, self._secret_key, algorithm="HS256")

    def decode(self, token: str) -> dict[str, Any]:
        return jwt.decode(
            token,
            self._secret_key,
            algorithms=["HS256"],
            options={"require": ["exp", "iat", "sub"]},
            issuer=self._issuer,
        )

