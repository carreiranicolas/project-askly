"""Shared presentation utilities.

Centralizes user entity conversion used across API and Web layers.
"""

from flask import g
from flask_login import current_user
from sqlalchemy.orm.exc import DetachedInstanceError

from src.domain.entities import Usuario
from src.domain.enums import PerfilUsuario


def get_current_user_entity() -> Usuario | None:
    """Convert Flask-Login/JWT user to domain entity.

    Handles:
    - Session auth (Flask-Login current_user)
    - JWT auth (g.api_user set by api_auth_required)
    - DetachedInstanceError (stale session)
    """
    principal = getattr(g, "api_user", None) or current_user

    if not getattr(principal, "is_authenticated", False):
        if not getattr(principal, "id", None):
            return None

    try:
        user_id = principal.id
        nome = principal.nome
        email = principal.email
        perfil = principal.perfil
        ativo = principal.ativo
        criado_em = principal.criado_em
    except DetachedInstanceError:
        from sqlalchemy import inspect as sa_inspect
        from src.infrastructure.persistence.sqlalchemy.models import UsuarioModel, db

        ident = sa_inspect(principal).identity
        principal_id = ident[0] if ident else None
        if principal_id is None:
            return None
        fresh = db.session.get(UsuarioModel, principal_id)
        if fresh is None:
            return None
        user_id = fresh.id
        nome = fresh.nome
        email = fresh.email
        perfil = fresh.perfil
        ativo = fresh.ativo
        criado_em = fresh.criado_em

    return Usuario(
        id=user_id,
        nome=nome,
        email=email,
        perfil=PerfilUsuario(perfil) if isinstance(perfil, str) else perfil,
        ativo=ativo,
        criado_em=criado_em,
    )
