"""Pytest configuration and fixtures."""

import os
import pytest
from uuid import uuid4

from src.presentation.app_factory import create_app
from src.infrastructure.persistence.sqlalchemy.models import db as _db
from src.infrastructure.security import PasswordHasher


def _ensure_test_database_exists(database_url: str) -> None:
    """
    Ensure the configured Postgres test database exists.

    If the DB in DATABASE_URL does not exist, create it by connecting to the
    default 'postgres' database.
    """
    if not database_url.startswith("postgresql"):
        return

    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.engine.url import make_url
    except Exception:
        return

    url = make_url(database_url)
    db_name = url.database
    if not db_name:
        return

    admin_url = url.set(database="postgres")

    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": db_name},
            ).scalar()
            if not exists:
                conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    finally:
        engine.dispose()


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')
    
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SERVER_NAME': 'localhost.localdomain',
    })
    
    with app.app_context():
        _ensure_test_database_exists(app.config["SQLALCHEMY_DATABASE_URI"])
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """Create database for each test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def password_hasher():
    """Password hasher instance."""
    return PasswordHasher()


@pytest.fixture
def auth_headers(client, db, password_hasher):
    """Get authentication headers for API tests."""
    from src.infrastructure.persistence.sqlalchemy.models import UsuarioModel
    
    user = UsuarioModel(
        id=uuid4(),
        nome='Test User',
        email='test@test.com',
        senha_hash=password_hasher.hash('password123'),
        perfil='solicitante',
        ativo=True,
    )
    db.session.add(user)
    db.session.commit()
    
    response = client.post('/api/v1/auth/login', json={
        'email': 'test@test.com',
        'senha': 'password123',
    })
    
    data = response.get_json()
    token = data.get('access_token', '')
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }


@pytest.fixture
def admin_user(db, password_hasher):
    """Create admin user."""
    from src.infrastructure.persistence.sqlalchemy.models import UsuarioModel
    
    user = UsuarioModel(
        id=uuid4(),
        nome='Admin User',
        email='admin@test.com',
        senha_hash=password_hasher.hash('admin123'),
        perfil='admin',
        ativo=True,
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def atendente_user(db, password_hasher):
    """Create atendente user."""
    from src.infrastructure.persistence.sqlalchemy.models import UsuarioModel
    
    user = UsuarioModel(
        id=uuid4(),
        nome='Atendente User',
        email='atendente@test.com',
        senha_hash=password_hasher.hash('atendente123'),
        perfil='atendente',
        ativo=True,
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def solicitante_user(db, password_hasher):
    """Create solicitante user."""
    from src.infrastructure.persistence.sqlalchemy.models import UsuarioModel
    
    user = UsuarioModel(
        id=uuid4(),
        nome='Solicitante User',
        email='solicitante@test.com',
        senha_hash=password_hasher.hash('solicitante123'),
        perfil='solicitante',
        ativo=True,
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def categoria(db):
    """Create test category."""
    from src.infrastructure.persistence.sqlalchemy.models import CategoriaModel
    
    cat = CategoriaModel(
        id=uuid4(),
        nome='TI - Teste',
        descricao='Categoria de teste',
        ativa=True,
    )
    db.session.add(cat)
    db.session.commit()
    return cat
