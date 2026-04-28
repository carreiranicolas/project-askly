"""
Infrastructure Layer - Implementações concretas.

Esta camada contém:
- Persistence: Repositórios SQLAlchemy, Unit of Work
- Security: Password hasher, decorators de autenticação
- Services: Serviços externos (email, etc.)

REGRAS:
- Implementa interfaces definidas na camada Domain
- Conhece detalhes de frameworks e bibliotecas
- Não contém lógica de negócio
"""

from src.infrastructure.persistence.sqlalchemy.models import db
from src.infrastructure.persistence.sqlalchemy.repositories import SQLAlchemyUnitOfWork
from src.infrastructure.security import PasswordHasher

__all__ = [
    "db",
    "SQLAlchemyUnitOfWork",
    "PasswordHasher",
]
