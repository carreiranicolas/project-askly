"""Auth helpers for REST API (Bearer JWT or session)."""

from __future__ import annotations

from functools import wraps
from uuid import UUID

import jwt as pyjwt
from flask import abort, current_app, g, request
from flask_login import current_user

from src.infrastructure.persistence.sqlalchemy.models import db, UsuarioModel
from src.infrastructure.security import TokenService


def _get_bearer_token() -> str | None:
    auth = request.headers.get("Authorization", "")
    if not auth:
        return None
    parts = auth.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return None


def api_auth_required(fn):
    """
    Require authentication for API endpoints.

    Accepts:
    - Session auth (Flask-Login)
    - Bearer JWT in Authorization header
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        # 1) Session auth
        if current_user.is_authenticated:
            g.api_user = current_user
            return fn(*args, **kwargs)

        # 2) Bearer JWT
        token = _get_bearer_token()
        if not token:
            abort(401)

        token_service = TokenService(
            secret_key=current_app.config["JWT_SECRET_KEY"],
            exp_seconds=int(current_app.config.get("JWT_EXP_SECONDS", 3600)),
        )
        try:
            payload = token_service.decode(token)
            user_id = payload.get("sub")
            if not user_id:
                abort(401)
            user = db.session.get(UsuarioModel, UUID(str(user_id)))
            if not user or not user.ativo:
                abort(401)
            g.api_user = user
            return fn(*args, **kwargs)
        except pyjwt.ExpiredSignatureError:
            abort(401)
        except pyjwt.InvalidTokenError:
            abort(401)
        except Exception:
            current_app.logger.exception("Unexpected error in API auth")
            abort(500)

    return wrapper

