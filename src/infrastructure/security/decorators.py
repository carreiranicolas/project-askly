"""Security decorators for route protection."""

from functools import wraps
from typing import Callable

from flask import abort, flash, g, redirect, request, url_for
from flask_login import current_user
from flask_login import login_required as flask_login_required

from src.domain.enums import PerfilUsuario

login_required = flask_login_required


def perfil_required(*perfis: PerfilUsuario | str) -> Callable:
    """
    Decorator to require specific user profiles.

    Usage:
        @perfil_required(PerfilUsuario.ADMIN)
        @perfil_required(PerfilUsuario.ATENDENTE, PerfilUsuario.ADMIN)
        @perfil_required('admin')
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            perfis_str = set()
            for p in perfis:
                if isinstance(p, PerfilUsuario):
                    perfis_str.add(p.value)
                else:
                    perfis_str.add(p)

            user_perfil = getattr(current_user, "perfil", None)
            if isinstance(user_perfil, PerfilUsuario):
                user_perfil = user_perfil.value

            if user_perfil not in perfis_str:
                is_api = request.path.startswith("/api/")
                if is_api:
                    abort(403)
                else:
                    flash("Você não tem permissão para acessar esta página.", "danger")
                    return redirect(url_for("web_tickets.listar"))

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f: Callable) -> Callable:
    """Decorator to require admin profile."""
    return perfil_required(PerfilUsuario.ADMIN)(f)  # type: ignore[no-any-return]


def atendente_required(f: Callable) -> Callable:
    """Decorator to require atendente or admin profile."""
    return perfil_required(PerfilUsuario.ATENDENTE, PerfilUsuario.ADMIN)(f)  # type: ignore[no-any-return]
