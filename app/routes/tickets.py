from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.models.ticket import StatusEnum
from app.services import catalog_service, is_staff, ticket_service, user_service
from app.services.exceptions import ServiceError

web_tickets_bp = Blueprint("web_tickets", __name__, url_prefix="/chamados")


@web_tickets_bp.route("/")
@login_required
def listar():
    chamados = ticket_service.list_tickets(
        current_user,
        tipo=request.args.get("tipo"),
        categoria_id=request.args.get("categoria", type=int),
    )
    return render_template("tickets/listar.html", chamados=chamados)


@web_tickets_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    if request.method == "POST":
        try:
            ticket = ticket_service.create_ticket(
                current_user,
                title=request.form.get("title", ""),
                description=request.form.get("description", ""),
                category_id=request.form.get("category_id", type=int),
                priority_id=request.form.get("priority_id", type=int),
            )
        except ServiceError as exc:
            flash(exc.message, "danger")
        else:
            flash("Chamado aberto com sucesso.", "success")
            return redirect(url_for("web_tickets.detalhe", id=ticket.id))

    return render_template(
        "tickets/novo.html",
        categorias=catalog_service.list_categorias(),
        prioridades=catalog_service.list_prioridades(),
    )


@web_tickets_bp.route("/<int:id>")
@login_required
def detalhe(id):
    try:
        chamado = ticket_service.get_ticket(current_user, id)
    except ServiceError as exc:
        flash(exc.message, "danger")
        return redirect(url_for("web_tickets.listar"))

    staff = is_staff(current_user)
    return render_template(
        "tickets/detalhe.html",
        chamado=chamado,
        comentarios=ticket_service.list_comments(current_user, id),
        historico=ticket_service.list_history(current_user, id),
        status_options=list(StatusEnum) if staff else [],
        atendentes=user_service.list_staff() if staff else [],
    )


@web_tickets_bp.route("/<int:id>/comentario", methods=["POST"])
@login_required
def adicionar_comentario(id):
    try:
        ticket_service.add_comment(current_user, id, request.form.get("content", ""))
        flash("Comentário adicionado.", "success")
    except ServiceError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("web_tickets.detalhe", id=id))


@web_tickets_bp.route("/<int:id>/status", methods=["POST"])
@login_required
def alterar_status(id):
    try:
        ticket_service.change_status(current_user, id, request.form.get("status"))
        flash("Status atualizado.", "success")
    except ServiceError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("web_tickets.detalhe", id=id))


@web_tickets_bp.route("/<int:id>/atribuir", methods=["POST"])
@login_required
def atribuir(id):
    try:
        ticket_service.assign_ticket(
            current_user, id, request.form.get("atendente_id", type=int)
        )
        flash("Chamado atribuído.", "success")
    except ServiceError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("web_tickets.detalhe", id=id))
