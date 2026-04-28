"""Tickets web routes."""

from uuid import UUID

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from src.application.dtos import (
    AlterarStatusDTO,
    AtribuirAtendenteDTO,
    ChamadoCreateDTO,
    ChamadoListFilterDTO,
    ComentarioCreateDTO,
)
from src.application.use_cases import (
    AddCommentUseCase,
    AssignAttendantUseCase,
    ChangeStatusUseCase,
    CreateTicketUseCase,
    GetTicketUseCase,
    ListCategoriesUseCase,
    ListTicketsUseCase,
)
from src.domain.entities import Usuario
from src.domain.enums import PerfilUsuario, Prioridade, StatusChamado
from src.domain.exceptions import DomainException
from src.infrastructure import SQLAlchemyUnitOfWork, db
from src.infrastructure.persistence.sqlalchemy.repositories import UsuarioRepository
from src.presentation.utils import get_current_user_entity, require_current_user_entity
from src.presentation.web.blueprints.tickets import tickets_bp


@tickets_bp.route("/")
@login_required
def listar():
    """List tickets."""
    user = require_current_user_entity()

    status = request.args.get("status")
    prioridade = request.args.get("prioridade")
    categoria_id = request.args.get("categoria")
    tipo = request.args.get("tipo")

    solicitante_id = user.id if tipo == "meus" else None
    atendente_id = user.id if tipo == "atribuidos" else None

    filters = ChamadoListFilterDTO(
        page=request.args.get("page", 1, type=int),
        per_page=10,
        status=StatusChamado(status) if status else None,
        prioridade=Prioridade(prioridade) if prioridade else None,
        categoria_id=UUID(categoria_id) if categoria_id else None,
        solicitante_id=solicitante_id,
        atendente_id=atendente_id,
    )

    uow = SQLAlchemyUnitOfWork(lambda: db.session)
    use_case = ListTicketsUseCase(unit_of_work=uow)
    result = use_case.execute(filters, user)

    cat_use_case = ListCategoriesUseCase(unit_of_work=uow)
    categorias = cat_use_case.execute(apenas_ativas=True)

    metrics = None
    if tipo == "meus":
        from sqlalchemy import func

        from src.infrastructure.persistence.sqlalchemy.models import ChamadoModel

        with uow:
            counts = (
                db.session.query(ChamadoModel.status_atual, func.count(ChamadoModel.id))
                .filter(ChamadoModel.solicitante_id == user.id)
                .group_by(ChamadoModel.status_atual)
                .all()
            )

            metrics = {}
            for st_val, count in counts:
                metrics[st_val] = count

            for s in StatusChamado:
                if s.value not in metrics:
                    metrics[s.value] = 0
            metrics["total"] = sum(metrics.values())

    return render_template(
        "tickets/listar.html",
        chamados=result,
        categorias=categorias,
        metrics=metrics,
        filtros={
            "status": status,
            "prioridade": prioridade,
            "categoria": categoria_id,
            "tipo": tipo,
        },
    )


@tickets_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    """Create new ticket."""
    user = require_current_user_entity()

    uow = SQLAlchemyUnitOfWork(lambda: db.session)
    cat_use_case = ListCategoriesUseCase(unit_of_work=uow)
    categorias = cat_use_case.execute(apenas_ativas=True)

    if request.method == "POST":
        dto = ChamadoCreateDTO(
            titulo=request.form.get("titulo", ""),
            descricao=request.form.get("descricao", ""),
            categoria_id=UUID(request.form.get("categoria_id")),
            prioridade=Prioridade(request.form.get("prioridade", "MEDIA")),
        )

        use_case = CreateTicketUseCase(unit_of_work=uow)

        try:
            result = use_case.execute(dto, user)
            flash("Chamado criado com sucesso!", "success")
            return redirect(url_for("web_tickets.detalhe", id=result.id))
        except DomainException as e:
            flash(e.message, "danger")

    return render_template("tickets/novo.html", categorias=categorias)


@tickets_bp.route("/<uuid:id>")
@login_required
def detalhe(id: UUID):
    """Ticket details."""
    user = require_current_user_entity()

    uow = SQLAlchemyUnitOfWork(lambda: db.session)
    use_case = GetTicketUseCase(unit_of_work=uow)

    try:
        result = use_case.execute(id, user)

        atendentes = []
        if user.pode_atribuir_chamados():
            repo = UsuarioRepository(db.session)  # type: ignore[arg-type]
            atendentes = repo.get_atendentes_ativos()

        return render_template(
            "tickets/detalhe.html",
            chamado=result.chamado,
            comentarios=result.comentarios,
            historico=result.historico,
            atendentes=atendentes,
        )
    except DomainException as e:
        flash(e.message, "danger")
        return redirect(url_for("web_tickets.listar"))


@tickets_bp.route("/<uuid:id>/status", methods=["POST"])
@login_required
def alterar_status(id: UUID):
    """Change ticket status."""
    user = require_current_user_entity()

    dto = AlterarStatusDTO(
        chamado_id=id,
        novo_status=StatusChamado(request.form.get("status")),
        motivo=request.form.get("motivo"),
    )

    uow = SQLAlchemyUnitOfWork(lambda: db.session)
    use_case = ChangeStatusUseCase(unit_of_work=uow)

    try:
        result = use_case.execute(dto, user)
        flash(f"Status alterado para {result.status_display}!", "success")
    except DomainException as e:
        flash(e.message, "danger")

    return redirect(url_for("web_tickets.detalhe", id=id))


@tickets_bp.route("/<uuid:id>/atribuir", methods=["POST"])
@login_required
def atribuir(id: UUID):
    """Assign attendant."""
    user = require_current_user_entity()

    atendente_id = request.form.get("atendente_id")
    if not atendente_id:
        atendente_id = str(user.id)

    dto = AtribuirAtendenteDTO(
        chamado_id=id,
        atendente_id=UUID(atendente_id),
    )

    uow = SQLAlchemyUnitOfWork(lambda: db.session)
    use_case = AssignAttendantUseCase(unit_of_work=uow)

    try:
        result = use_case.execute(dto, user)
        flash(f"Chamado atribuído para {result.atendente_nome}!", "success")
    except DomainException as e:
        flash(e.message, "danger")

    return redirect(url_for("web_tickets.detalhe", id=id))


@tickets_bp.route("/<uuid:id>/comentarios", methods=["POST"])
@login_required
def adicionar_comentario(id: UUID):
    """Add comment."""
    user = require_current_user_entity()

    dto = ComentarioCreateDTO(
        chamado_id=id,
        conteudo=request.form.get("conteudo", ""),
    )

    uow = SQLAlchemyUnitOfWork(lambda: db.session)
    use_case = AddCommentUseCase(unit_of_work=uow)

    try:
        use_case.execute(dto, user)
        flash("Comentário adicionado!", "success")
    except DomainException as e:
        flash(e.message, "danger")

    return redirect(url_for("web_tickets.detalhe", id=id))
