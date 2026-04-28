"""Tickets API endpoints."""

from uuid import UUID

from flask import request
from flask_restx import Namespace, Resource, fields

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
    ListTicketsUseCase,
)
from src.domain.enums import Prioridade, StatusChamado
from src.domain.exceptions import DomainException
from src.infrastructure import SQLAlchemyUnitOfWork, db
from src.presentation.api.api_auth import api_auth_required
from src.presentation.utils import get_current_user_entity, require_current_user_entity

tickets_ns = Namespace("chamados", description="Gestão de chamados/tickets")

ticket_create = tickets_ns.model(
    "TicketCreate",
    {
        "titulo": fields.String(
            required=True, description="Título do chamado", example="Computador não liga"
        ),
        "descricao": fields.String(
            required=True,
            description="Descrição detalhada",
            example="Ao pressionar o botão, nada acontece",
        ),
        "categoria_id": fields.String(required=True, description="ID da categoria"),
        "prioridade": fields.String(
            description="Prioridade (BAIXA, MEDIA, ALTA, CRITICA)", default="MEDIA"
        ),
    },
)

ticket_response = tickets_ns.model(
    "TicketResponse",
    {
        "id": fields.String(description="ID do chamado"),
        "titulo": fields.String(),
        "descricao": fields.String(),
        "prioridade": fields.String(),
        "prioridade_display": fields.String(),
        "status_atual": fields.String(),
        "status_display": fields.String(),
        "status_cor": fields.String(description="Cor hex do status"),
        "categoria_nome": fields.String(),
        "solicitante_nome": fields.String(),
        "atendente_nome": fields.String(),
        "criado_em": fields.DateTime(),
        "atualizado_em": fields.DateTime(),
        "transicoes_disponiveis": fields.List(
            fields.String(), description="Status disponíveis para transição"
        ),
    },
)

change_status_model = tickets_ns.model(
    "ChangeStatus",
    {
        "status": fields.String(
            required=True,
            description="Novo status",
            enum=["EM_ATENDIMENTO", "AGUARDANDO_RETORNO", "RESOLVIDO", "FECHADO"],
        ),
        "motivo": fields.String(description="Motivo da alteração"),
    },
)

assign_model = tickets_ns.model(
    "AssignAttendant",
    {
        "atendente_id": fields.String(required=True, description="ID do atendente"),
    },
)

comment_create = tickets_ns.model(
    "CommentCreate",
    {
        "conteudo": fields.String(required=True, description="Texto do comentário"),
    },
)

comment_response = tickets_ns.model(
    "CommentResponse",
    {
        "id": fields.String(),
        "autor_nome": fields.String(),
        "conteudo": fields.String(),
        "criado_em": fields.DateTime(),
    },
)

pagination_model = tickets_ns.model(
    "Pagination",
    {
        "page": fields.Integer(),
        "per_page": fields.Integer(),
        "total": fields.Integer(),
        "pages": fields.Integer(),
        "has_next": fields.Boolean(),
        "has_prev": fields.Boolean(),
    },
)

ticket_list_response = tickets_ns.model(
    "TicketListResponse",
    {
        "items": fields.List(fields.Nested(ticket_response)),
        "pagination": fields.Nested(pagination_model),
    },
)


@tickets_ns.route("")
class TicketListResource(Resource):
    """Ticket list and creation."""

    @tickets_ns.doc("list_tickets", security="Bearer")
    @tickets_ns.param("page", "Página", type=int, default=1)
    @tickets_ns.param("per_page", "Itens por página", type=int, default=10)
    @tickets_ns.param("status", "Filtrar por status")
    @tickets_ns.param("prioridade", "Filtrar por prioridade")
    @tickets_ns.param("categoria_id", "Filtrar por categoria")
    @tickets_ns.response(200, "Lista de chamados", ticket_list_response)
    @api_auth_required
    def get(self):
        """
        Listar chamados.

        Retorna lista paginada de chamados.
        Solicitantes veem apenas seus chamados.
        Atendentes e admins veem todos.
        """
        user = require_current_user_entity()

        status = request.args.get("status")
        prioridade = request.args.get("prioridade")

        filters = ChamadoListFilterDTO(
            page=request.args.get("page", 1, type=int),
            per_page=min(request.args.get("per_page", 10, type=int), 100),
            status=StatusChamado(status) if status else None,
            prioridade=Prioridade(prioridade) if prioridade else None,
            categoria_id=(
                UUID(request.args.get("categoria_id")) if request.args.get("categoria_id") else None
            ),
        )

        uow = SQLAlchemyUnitOfWork(lambda: db.session)
        use_case = ListTicketsUseCase(unit_of_work=uow)

        result = use_case.execute(filters, user)

        return {
            "items": [
                {
                    "id": str(item.id),
                    "titulo": item.titulo,
                    "prioridade": item.prioridade,
                    "prioridade_display": item.prioridade_display,
                    "status_atual": item.status_atual,
                    "status_display": item.status_display,
                    "status_cor": item.status_cor,
                    "categoria_nome": item.categoria_nome,
                    "solicitante_nome": item.solicitante_nome,
                    "atendente_nome": item.atendente_nome,
                    "criado_em": item.criado_em.isoformat(),
                }
                for item in result.items
            ],
            "pagination": {
                "page": result.page,
                "per_page": result.per_page,
                "total": result.total,
                "pages": result.pages,
                "has_next": result.has_next,
                "has_prev": result.has_prev,
            },
        }, 200

    @tickets_ns.doc("create_ticket", security="Bearer")
    @tickets_ns.expect(ticket_create)
    @tickets_ns.response(201, "Chamado criado", ticket_response)
    @tickets_ns.response(400, "Dados inválidos")
    @api_auth_required
    def post(self):
        """
        Criar novo chamado.

        Cria um chamado com status ABERTO.
        Apenas solicitantes podem criar chamados.
        """
        user = require_current_user_entity()
        data = request.json

        prioridade_str = data.get("prioridade", "MEDIA")

        dto = ChamadoCreateDTO(
            titulo=data.get("titulo", ""),
            descricao=data.get("descricao", ""),
            categoria_id=UUID(data.get("categoria_id")),
            prioridade=Prioridade(prioridade_str),
        )

        uow = SQLAlchemyUnitOfWork(lambda: db.session)
        use_case = CreateTicketUseCase(unit_of_work=uow)

        try:
            result = use_case.execute(dto, user)

            return {
                "id": str(result.id),
                "titulo": result.titulo,
                "descricao": result.descricao,
                "prioridade": result.prioridade,
                "status_atual": result.status_atual,
                "status_display": result.status_display,
                "categoria_nome": result.categoria_nome,
                "solicitante_nome": result.solicitante_nome,
                "criado_em": result.criado_em.isoformat(),
            }, 201
        except DomainException as e:
            return e.to_dict(), 400


@tickets_ns.route("/<string:id>")
class TicketResource(Resource):
    """Single ticket operations."""

    @tickets_ns.doc("get_ticket", security="Bearer")
    @tickets_ns.response(200, "Detalhes do chamado")
    @tickets_ns.response(404, "Chamado não encontrado")
    @api_auth_required
    def get(self, id: str):
        """
        Obter detalhes do chamado.

        Retorna informações completas incluindo comentários e histórico.
        """
        user = require_current_user_entity()

        uow = SQLAlchemyUnitOfWork(lambda: db.session)
        use_case = GetTicketUseCase(unit_of_work=uow)

        try:
            result = use_case.execute(UUID(id), user)

            return {
                "chamado": {
                    "id": str(result.chamado.id),
                    "titulo": result.chamado.titulo,
                    "descricao": result.chamado.descricao,
                    "prioridade": result.chamado.prioridade,
                    "prioridade_display": result.chamado.prioridade_display,
                    "status_atual": result.chamado.status_atual,
                    "status_display": result.chamado.status_display,
                    "status_cor": result.chamado.status_cor,
                    "categoria_nome": result.chamado.categoria_nome,
                    "solicitante_nome": result.chamado.solicitante_nome,
                    "atendente_nome": result.chamado.atendente_nome,
                    "criado_em": result.chamado.criado_em.isoformat(),
                    "atualizado_em": result.chamado.atualizado_em.isoformat(),
                    "transicoes_disponiveis": result.chamado.transicoes_disponiveis,
                },
                "comentarios": [
                    {
                        "id": str(c.id),
                        "autor_nome": c.autor_nome,
                        "conteudo": c.conteudo,
                        "criado_em": c.criado_em.isoformat(),
                    }
                    for c in result.comentarios
                ],
                "historico": result.historico,
            }, 200
        except DomainException as e:
            return e.to_dict(), 404 if "NOT_FOUND" in e.code else 400


@tickets_ns.route("/<string:id>/status")
class TicketStatusResource(Resource):
    """Ticket status operations."""

    @tickets_ns.doc("change_status", security="Bearer")
    @tickets_ns.expect(change_status_model)
    @tickets_ns.response(200, "Status alterado")
    @tickets_ns.response(400, "Transição inválida")
    @api_auth_required
    def post(self, id: str):
        """
        Alterar status do chamado.

        Toda alteração gera registro no histórico (auditoria).
        """
        user = require_current_user_entity()
        data = request.json

        dto = AlterarStatusDTO(
            chamado_id=UUID(id),
            novo_status=StatusChamado(data.get("status")),
            motivo=data.get("motivo"),
        )

        uow = SQLAlchemyUnitOfWork(lambda: db.session)
        use_case = ChangeStatusUseCase(unit_of_work=uow)

        try:
            result = use_case.execute(dto, user)

            return {
                "message": f"Status alterado para {result.status_display}",
                "chamado": {
                    "id": str(result.id),
                    "status_atual": result.status_atual,
                    "status_display": result.status_display,
                    "transicoes_disponiveis": result.transicoes_disponiveis,
                },
            }, 200
        except DomainException as e:
            return e.to_dict(), 400


@tickets_ns.route("/<string:id>/atribuir")
class TicketAssignResource(Resource):
    """Ticket assignment operations."""

    @tickets_ns.doc("assign_attendant", security="Bearer")
    @tickets_ns.expect(assign_model)
    @tickets_ns.response(200, "Atendente atribuído")
    @api_auth_required
    def post(self, id: str):
        """
        Atribuir atendente ao chamado.

        Apenas atendentes e admins podem atribuir.
        """
        user = require_current_user_entity()
        data = request.json

        dto = AtribuirAtendenteDTO(
            chamado_id=UUID(id),
            atendente_id=UUID(data.get("atendente_id")),
        )

        uow = SQLAlchemyUnitOfWork(lambda: db.session)
        use_case = AssignAttendantUseCase(unit_of_work=uow)

        try:
            result = use_case.execute(dto, user)

            return {
                "message": f"Chamado atribuído para {result.atendente_nome}",
                "chamado": {
                    "id": str(result.id),
                    "atendente_nome": result.atendente_nome,
                },
            }, 200
        except DomainException as e:
            return e.to_dict(), 400


@tickets_ns.route("/<string:id>/comentarios")
class TicketCommentsResource(Resource):
    """Ticket comments operations."""

    @tickets_ns.doc("add_comment", security="Bearer")
    @tickets_ns.expect(comment_create)
    @tickets_ns.response(201, "Comentário adicionado", comment_response)
    @api_auth_required
    def post(self, id: str):
        """
        Adicionar comentário ao chamado.

        Participantes podem comentar em chamados não fechados.
        """
        user = require_current_user_entity()
        data = request.json

        dto = ComentarioCreateDTO(
            chamado_id=UUID(id),
            conteudo=data.get("conteudo", ""),
        )

        uow = SQLAlchemyUnitOfWork(lambda: db.session)
        use_case = AddCommentUseCase(unit_of_work=uow)

        try:
            result = use_case.execute(dto, user)

            return {
                "id": str(result.id),
                "autor_nome": result.autor_nome,
                "conteudo": result.conteudo,
                "criado_em": result.criado_em.isoformat(),
            }, 201
        except DomainException as e:
            return e.to_dict(), 400
