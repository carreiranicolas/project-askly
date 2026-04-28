"""
Application Layer - Casos de Uso.

Esta camada contém:
- Use Cases: Orquestração da lógica de aplicação
- DTOs: Data Transfer Objects para entrada/saída

REGRAS:
- Depende apenas da camada Domain
- Não conhece detalhes de infraestrutura
- Use Cases são a única forma de executar operações de negócio
"""

from src.application.use_cases import (
    LoginUseCase,
    RegisterUseCase,
    CreateTicketUseCase,
    ChangeStatusUseCase,
    AssignAttendantUseCase,
    ListTicketsUseCase,
    GetTicketUseCase,
    AddCommentUseCase,
    CreateCategoryUseCase,
    ListCategoriesUseCase,
    ListUsersUseCase,
    ChangeProfileUseCase,
)

__all__ = [
    "LoginUseCase",
    "RegisterUseCase",
    "CreateTicketUseCase",
    "ChangeStatusUseCase",
    "AssignAttendantUseCase",
    "ListTicketsUseCase",
    "GetTicketUseCase",
    "AddCommentUseCase",
    "CreateCategoryUseCase",
    "ListCategoriesUseCase",
    "ListUsersUseCase",
    "ChangeProfileUseCase",
]
