"""Categories API endpoints."""

from flask import request
from flask_restx import Namespace, Resource, fields

from src.application.dtos import CategoriaCreateDTO
from src.application.use_cases import CreateCategoryUseCase, ListCategoriesUseCase
from src.domain.exceptions import DomainException
from src.infrastructure import SQLAlchemyUnitOfWork, db
from src.presentation.api.api_auth import api_auth_required
from src.presentation.utils import get_current_user_entity

categories_ns = Namespace("categorias", description="Gestão de categorias")

category_create = categories_ns.model(
    "CategoryCreate",
    {
        "nome": fields.String(
            required=True, description="Nome da categoria", example="TI - Infraestrutura"
        ),
        "descricao": fields.String(description="Descrição"),
    },
)

category_response = categories_ns.model(
    "CategoryResponse",
    {
        "id": fields.String(),
        "nome": fields.String(),
        "descricao": fields.String(),
        "ativa": fields.Boolean(),
        "criado_em": fields.DateTime(),
    },
)


@categories_ns.route("")
class CategoryListResource(Resource):
    """Category list and creation."""

    @categories_ns.doc("list_categories", security="Bearer")
    @categories_ns.param("todas", "Incluir inativas (apenas admin)", type=bool, default=False)
    @categories_ns.response(200, "Lista de categorias")
    @api_auth_required
    def get(self):
        """
        Listar categorias.

        Por padrão retorna apenas ativas.
        Admins podem ver todas passando `todas=true`.
        """
        apenas_ativas = not request.args.get("todas", False, type=bool)

        uow = SQLAlchemyUnitOfWork(lambda: db.session)
        use_case = ListCategoriesUseCase(unit_of_work=uow)

        result = use_case.execute(apenas_ativas=apenas_ativas)

        return {
            "items": [
                {
                    "id": str(cat.id),
                    "nome": cat.nome,
                    "descricao": cat.descricao,
                    "ativa": cat.ativa,
                    "criado_em": cat.criado_em.isoformat(),
                }
                for cat in result
            ]
        }, 200

    @categories_ns.doc("create_category", security="Bearer")
    @categories_ns.expect(category_create)
    @categories_ns.response(201, "Categoria criada", category_response)
    @categories_ns.response(400, "Dados inválidos")
    @categories_ns.response(403, "Não autorizado")
    @api_auth_required
    def post(self):
        """
        Criar categoria.

        Apenas administradores podem criar categorias.
        """
        user = get_current_user_entity()
        data = request.json

        dto = CategoriaCreateDTO(
            nome=data.get("nome", ""),
            descricao=data.get("descricao"),
        )

        uow = SQLAlchemyUnitOfWork(lambda: db.session)
        use_case = CreateCategoryUseCase(unit_of_work=uow)

        try:
            result = use_case.execute(dto, user)

            return {
                "id": str(result.id),
                "nome": result.nome,
                "descricao": result.descricao,
                "ativa": result.ativa,
                "criado_em": result.criado_em.isoformat(),
            }, 201
        except DomainException as e:
            status = 403 if "AUTHORIZATION" in e.code else 400
            return e.to_dict(), status
