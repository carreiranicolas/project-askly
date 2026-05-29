from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.models.ticket import StatusEnum
from app.services import catalog_service, is_staff, ticket_service, user_service
from app.services.exceptions import ServiceError

web_tickets_bp = Blueprint("web_tickets", __name__, url_prefix="/chamados")

PER_PAGE = 10


def _list_filters():
    """Filtros da listagem normalizados (usados na query, paginação e busca).

    Aceita ``categoria_id`` (preferido, alinhado com a API) e ``categoria``
    (legado, mantido para não quebrar bookmarks existentes da sidebar).
    """
    return {
        "tipo": request.args.get("tipo") or None,
        "categoria_id": (
            request.args.get("categoria_id", type=int) or request.args.get("categoria", type=int)
        ),
        "q": (request.args.get("q") or "").strip() or None,
    }


@web_tickets_bp.route("/")
@login_required
def listar():
    filters = _list_filters()
    query = ticket_service.tickets_query(current_user, **filters)
    pagination = query.paginate(
        page=request.args.get("page", 1, type=int),
        per_page=PER_PAGE,
        error_out=False,
    )
    return render_template(
        "tickets/listar.html",
        chamados=pagination,
        q=filters["q"] or "",
        filters=filters,
        is_overdue=ticket_service.is_overdue,
    )


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
            flash(f"Chamado #{ticket.id} aberto com sucesso.", "success")
            return redirect(url_for("web_tickets.detalhe", id=ticket.id))

    # Apenas catálogo ativo: o solicitante não deve ver áreas/prioridades
    # desativadas pelo admin.
    return render_template(
        "tickets/novo.html",
        categorias=catalog_service.list_categorias(only_active=True),
        prioridades=catalog_service.list_prioridades(only_active=True),
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
    # Solicitante (não staff) só pode cancelar o próprio chamado enquanto
    # ele ainda estiver ativo (não fechado/cancelado/aguardando aprovação).
    pode_cancelar = (
        not staff
        and chamado.requester_id == current_user.id
        and StatusEnum.CANCELADO in ticket_service.allowed_transitions(chamado.status)
    )
    return render_template(
        "tickets/detalhe.html",
        chamado=chamado,
        staff=staff,
        comentarios=ticket_service.list_comments(current_user, id),
        historico=ticket_service.list_history(current_user, id),
        status_options=ticket_service.allowed_transitions(chamado.status) if staff else [],
        # Atribuição restrita à área do chamado.
        atendentes=user_service.list_staff_for_area(chamado.category_id) if staff else [],
        pode_aprovar=ticket_service.can_approve(current_user, chamado),
        pode_cancelar=pode_cancelar,
        sla_deadline=ticket_service.sla_deadline(chamado),
        sla_overdue=ticket_service.is_overdue(chamado),
        sla_remaining=ticket_service.sla_remaining_label(chamado),
        is_overdue=ticket_service.is_overdue,
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
        ticket_service.change_status(
            current_user,
            id,
            request.form.get("status"),
            motivo=request.form.get("motivo"),
        )
        flash("Status atualizado.", "success")
    except ServiceError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("web_tickets.detalhe", id=id))


@web_tickets_bp.route("/<int:id>/aprovar", methods=["POST"])
@login_required
def aprovar(id):
    try:
        ticket_service.approve_resolution(current_user, id, motivo=request.form.get("motivo"))
        flash("Solução aprovada. Chamado fechado.", "success")
    except ServiceError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("web_tickets.detalhe", id=id))


@web_tickets_bp.route("/<int:id>/recusar", methods=["POST"])
@login_required
def recusar(id):
    try:
        ticket_service.reject_resolution(current_user, id, motivo=request.form.get("motivo"))
        flash("Solução recusada. O chamado foi reaberto para o responsável.", "info")
    except ServiceError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("web_tickets.detalhe", id=id))


@web_tickets_bp.route("/<int:id>/atribuir", methods=["POST"])
@login_required
def atribuir(id):
    try:
        ticket_service.assign_ticket(current_user, id, request.form.get("atendente_id", type=int))
        flash("Chamado atribuído.", "success")
    except ServiceError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("web_tickets.detalhe", id=id))
