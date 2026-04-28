"""Admin web routes."""

from uuid import UUID

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from src.application.dtos import CategoriaCreateDTO
from src.application.use_cases import (
    ChangeProfileUseCase,
    CreateCategoryUseCase,
    ListCategoriesUseCase,
    ListUsersUseCase,
)
from src.domain.entities import Usuario
from src.domain.enums import PerfilUsuario
from src.domain.exceptions import DomainException
from src.infrastructure import SQLAlchemyUnitOfWork, db
from src.infrastructure.persistence.sqlalchemy.models import CategoriaModel
from src.infrastructure.security import admin_required
from src.presentation.utils import get_current_user_entity
from src.presentation.web.blueprints.admin import admin_bp


@admin_bp.route("/usuarios")
@login_required
@admin_required
def usuarios():
    """List users."""
    user = get_current_user_entity()

    perfil_str = request.args.get("perfil")
    perfil = PerfilUsuario(perfil_str) if perfil_str else None

    uow = SQLAlchemyUnitOfWork(lambda: db.session)
    use_case = ListUsersUseCase(unit_of_work=uow)

    result = use_case.execute(
        usuario=user,
        page=request.args.get("page", 1, type=int),
        per_page=10,
        perfil=perfil,
    )

    return render_template(
        "admin/usuarios.html",
        usuarios=result,
        perfil_filtro=perfil_str,
    )


@admin_bp.route("/usuarios/<uuid:id>/perfil", methods=["POST"])
@login_required
@admin_required
def alterar_perfil(id: UUID):
    """Change user profile."""
    admin = get_current_user_entity()

    novo_perfil = PerfilUsuario(request.form.get("perfil"))

    uow = SQLAlchemyUnitOfWork(lambda: db.session)
    use_case = ChangeProfileUseCase(unit_of_work=uow)

    try:
        result = use_case.execute(id, novo_perfil, admin)
        flash(f"Perfil de {result.nome} alterado para {result.perfil_display}.", "success")
    except DomainException as e:
        flash(e.message, "danger")

    return redirect(url_for("web_admin.usuarios"))


@admin_bp.route("/categorias")
@login_required
@admin_required
def categorias():
    """List categories."""
    uow = SQLAlchemyUnitOfWork(lambda: db.session)
    use_case = ListCategoriesUseCase(unit_of_work=uow)
    result = use_case.execute(apenas_ativas=False)

    return render_template("admin/categorias.html", categorias=result)


@admin_bp.route("/categorias", methods=["POST"])
@login_required
@admin_required
def criar_categoria():
    """Create category."""
    user = get_current_user_entity()

    dto = CategoriaCreateDTO(
        nome=request.form.get("nome", ""),
        descricao=request.form.get("descricao"),
    )

    uow = SQLAlchemyUnitOfWork(lambda: db.session)
    use_case = CreateCategoryUseCase(unit_of_work=uow)

    try:
        result = use_case.execute(dto, user)
        flash(f'Categoria "{result.nome}" criada com sucesso!', "success")
    except DomainException as e:
        flash(e.message, "danger")

    return redirect(url_for("web_admin.categorias"))


@admin_bp.route("/categorias/<uuid:id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_categoria(id: UUID):
    """Toggle category active status."""
    categoria = db.session.get(CategoriaModel, id)
    if categoria:
        categoria.ativa = not categoria.ativa
        db.session.commit()
        status = "ativada" if categoria.ativa else "desativada"
        flash(f'Categoria "{categoria.nome}" {status}.', "success")

    return redirect(url_for("web_admin.categorias"))
