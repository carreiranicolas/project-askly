import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://askly:askly_dev_password@localhost:5435/askly_test_db",
)
os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest

from app import create_app
from app.extensions import db as _db
from app.models.category import Categoria
from app.models.commentary import Comentario
from app.models.history import HistoricoStatus
from app.models.priority import Prioridade
from app.models.role import Cargo
from app.models.ticket import Chamado
from app.models.user import Usuario
from app.services import auth_service


def _seed_catalog():
    _db.session.add_all(
        [
            Cargo(name="Solicitante", description="x", is_active=True),
            Cargo(name="Atendente", description="x", is_active=True),
            Cargo(name="Admin", description="x", is_active=True),
            Categoria(name="RH", description="x", is_active=True),
            Categoria(name="Infraestrutura", description="x", is_active=True),
            Prioridade(name="Alta", description="x", sla_hours=8, is_active=True),
        ]
    )
    _db.session.commit()


@pytest.fixture(scope="session")
def app():
    flask_app = create_app()
    flask_app.config.update(
        TESTING=True, WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False
    )
    with flask_app.app_context():
        _db.drop_all()
        _db.create_all()
        _seed_catalog()
    yield flask_app
    with flask_app.app_context():
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(autouse=True)
def _clean_dynamic(app):
    """Limpa dados transacionais antes de cada teste, mantendo o catálogo."""
    with app.app_context():
        for model in (HistoricoStatus, Comentario, Chamado, Usuario):
            _db.session.query(model).delete()
        _db.session.commit()
    yield


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def cargo_ids(app):
    with app.app_context():
        return {c.name: c.id for c in Cargo.query.all()}


@pytest.fixture
def catalog(app):
    with app.app_context():
        return {
            "categoria": Categoria.query.order_by(Categoria.name).first().id,
            "prioridade": Prioridade.query.first().id,
        }


@pytest.fixture
def areas(app):
    with app.app_context():
        return {c.name: c.id for c in Categoria.query.all()}


@pytest.fixture
def make_user(app, cargo_ids):
    def _make(role="Solicitante", email=None, password="senha123", name="Teste", area=None):
        email = email or f"{role.lower()}@test.com"
        with app.app_context():
            area_id = Categoria.query.filter_by(name=area).first().id if area else None
            auth_service.register(
                name, email, password, cargo_ids[role], area_id=area_id
            )
        return email, password

    return _make


@pytest.fixture
def api_login(client):
    def _login(email, password="senha123"):
        resp = client.post(
            "/api/v1/auth/login", json={"email": email, "password": password}
        )
        token = resp.get_json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _login
