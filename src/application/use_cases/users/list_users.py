"""List Users Use Case."""

from dataclasses import dataclass

from src.application.dtos import UsuarioResponseDTO
from src.domain.entities import Usuario
from src.domain.enums import PerfilUsuario
from src.domain.exceptions import AuthorizationException
from src.domain.value_objects import PaginatedResult


@dataclass
class ListUsersUseCase:
    """
    Use Case para listagem de usuários.

    Apenas administradores podem listar usuários.
    """

    unit_of_work: "IUnitOfWork"

    def execute(
        self,
        usuario: Usuario,
        page: int = 1,
        per_page: int = 10,
        perfil: PerfilUsuario | None = None,
    ) -> PaginatedResult[UsuarioResponseDTO]:
        """
        Lista usuários.

        Args:
            usuario: Usuário realizando a consulta
            page: Página
            per_page: Itens por página
            perfil: Filtro por perfil

        Returns:
            Lista paginada de usuários

        Raises:
            AuthorizationException: Se não é admin
        """
        if not usuario.pode_gerenciar_usuarios():
            raise AuthorizationException(
                "Apenas administradores podem listar usuários", required_permission="manage_users"
            )

        with self.unit_of_work:
            usuarios, total = self.unit_of_work.usuarios.get_paginated(
                page=page,
                per_page=per_page,
                perfil=perfil,
            )

        items = [UsuarioResponseDTO.from_entity(u) for u in usuarios]

        return PaginatedResult(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
        )


from src.domain.interfaces.repositories import IUnitOfWork
