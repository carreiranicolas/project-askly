from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.services import ROLE_ADMIN, catalog_service, role_of, user_service
from app.services.exceptions import ServiceError

web_admin_bp = Blueprint("web_admin", __name__, url_prefix="/admin")


def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if role_of(current_user) != ROLE_ADMIN:
            abort(403)
        return fn(*args, **kwargs)

    return wrapper


@web_admin_bp.route("/usuarios")
@admin_required
def usuarios():
    return render_template(
        "admin/usuarios.html",
        usuarios=user_service.list_users(),
        cargos=catalog_service.list_cargos(),
        areas=catalog_service.list_categorias(),
    )


@web_admin_bp.route("/usuarios/<int:id>/cargo", methods=["POST"])
@admin_required
def alterar_perfil(id):
    try:
        user_service.update_user(
            id,
            role_id=request.form.get("role_id", type=int),
            area_id=request.form.get("area_id", type=int),
        )
        flash("Usuário atualizado.", "success")
    except ServiceError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("web_admin.usuarios"))


@web_admin_bp.route("/categorias")
@admin_required
def categorias():
    return render_template(
        "admin/categorias.html", categorias=catalog_service.list_categorias()
    )


@web_admin_bp.route("/categorias/criar", methods=["POST"])
@admin_required
def criar_categoria():
    try:
        catalog_service.create_categoria(
            request.form.get("name", "").strip(),
            request.form.get("description", "").strip(),
        )
        flash("Categoria criada.", "success")
    except ServiceError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("web_admin.categorias"))


@web_admin_bp.route("/categorias/<int:id>/toggle", methods=["POST"])
@admin_required
def toggle_categoria(id):
    try:
        categoria = catalog_service.get_categoria(id)
        catalog_service.update_categoria(id, is_active=not categoria.is_active)
        flash("Categoria atualizada.", "success")
    except ServiceError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("web_admin.categorias"))
