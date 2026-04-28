"""REST API with Swagger documentation."""

from flask import Blueprint
from flask_restx import Api

api_bp = Blueprint("api", __name__)

api = Api(
    api_bp,
    version="1.0",
    title="Askly API",
    # Mantemos a home do Swagger “limpa”, exibindo essencialmente as rotas.
    description="",
    # Vamos servir nossa própria UI em /api/docs (com Light/Dark toggle).
    doc=False,
    authorizations={
        "Bearer": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": 'JWT Authorization header. Example: "Bearer {token}"',
        }
    },
    security="Bearer",
)

from src.presentation.api.v1 import auth_ns, categories_ns, tickets_ns, users_ns

api.add_namespace(auth_ns, path="/v1/auth")
api.add_namespace(tickets_ns, path="/v1/chamados")
api.add_namespace(categories_ns, path="/v1/categorias")
api.add_namespace(users_ns, path="/v1/usuarios")


@api_bp.get("/docs")
def swagger_ui():
    """Custom Swagger UI (light/dark)."""
    from flask import render_template

    return render_template("api/swagger.html")
