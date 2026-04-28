"""
Domain Layer - Núcleo da aplicação.

Esta camada contém:
- Entities: Objetos de negócio com identidade
- Value Objects: Objetos imutáveis sem identidade
- Enums: Enumerações do domínio
- Exceptions: Exceções de negócio
- Interfaces: Contratos (Repository, Services)

REGRAS:
- Esta camada NÃO depende de nenhuma outra
- Contém apenas lógica de negócio pura
- Agnóstica de frameworks e infraestrutura
"""

from src.domain.entities import (
    Entity,
    Usuario,
    Categoria,
    Chamado,
    Comentario,
    HistoricoStatus,
)
from src.domain.enums import (
    PerfilUsuario,
    Prioridade,
    StatusChamado,
)
from src.domain.value_objects import (
    Email,
    Senha,
    PaginationParams,
    PaginatedResult,
)

__all__ = [
    # Entities
    "Entity",
    "Usuario",
    "Categoria",
    "Chamado",
    "Comentario",
    "HistoricoStatus",
    # Enums
    "PerfilUsuario",
    "Prioridade",
    "StatusChamado",
    # Value Objects
    "Email",
    "Senha",
    "PaginationParams",
    "PaginatedResult",
]
