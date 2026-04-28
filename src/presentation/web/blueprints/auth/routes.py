"""Auth web routes."""

from urllib.parse import urlparse

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from src.application.dtos import LoginDTO, UsuarioCreateDTO
from src.application.use_cases import LoginUseCase, RegisterUseCase
from src.domain.exceptions import DomainException
from src.infrastructure import PasswordHasher, SQLAlchemyUnitOfWork, db
from src.infrastructure.persistence.sqlalchemy.models import UsuarioModel
from src.infrastructure.persistence.sqlalchemy.repositories import UsuarioRepository
from src.presentation.web.blueprints.auth import auth_bp


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for("web_tickets.listar"))

    if request.method == "POST":
        dto = LoginDTO(
            email=request.form.get("email", ""),
            senha=request.form.get("senha", ""),
            lembrar=request.form.get("lembrar") == "on",
        )

        hasher = PasswordHasher()
        repo = UsuarioRepository(db.session)
        use_case = LoginUseCase(usuario_repository=repo, password_hasher=hasher)

        try:
            result = use_case.execute(dto)

            user_model = db.session.get(UsuarioModel, result.usuario.id)
            if user_model:
                login_user(user_model, remember=dto.lembrar)

                next_page = request.args.get("next")
                if next_page and urlparse(next_page).netloc == "":
                    return redirect(next_page)
                return redirect(url_for("web_tickets.listar"))

        except DomainException as e:
            flash(e.message, "danger")

    return render_template("auth/login.html")


@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    """Registration page."""
    if current_user.is_authenticated:
        return redirect(url_for("web_tickets.listar"))

    if request.method == "POST":
        dto = UsuarioCreateDTO(
            nome=request.form.get("nome", ""),
            email=request.form.get("email", ""),
            senha=request.form.get("senha", ""),
            confirmar_senha=request.form.get("confirmar_senha", ""),
        )

        hasher = PasswordHasher()
        uow = SQLAlchemyUnitOfWork(lambda: db.session)
        repo = UsuarioRepository(db.session)
        use_case = RegisterUseCase(
            usuario_repository=repo,
            unit_of_work=uow,
            password_hasher=hasher,
        )

        try:
            use_case.execute(dto)
            flash("Cadastro realizado com sucesso! Faça login para continuar.", "success")
            return redirect(url_for("web_auth.login"))
        except DomainException as e:
            flash(e.message, "danger")

    return render_template("auth/cadastro.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Logout."""
    logout_user()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("web_auth.login"))
