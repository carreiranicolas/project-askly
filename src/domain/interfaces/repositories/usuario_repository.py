"""User repository interface."""

from abc import abstractmethod
from uuid import UUID

from src.domain.entities import Usuario
from src.domain.enums import PerfilUsuario
from src.domain.interfaces.repositories.base import IRepository


class IUsuarioRepository(IRepository[Usuario]):
    """
    Interface de repositório para Usuários.

    Estende as operações básicas com métodos específicos do domínio.
    """

    @abstractmethod
    def get_by_email(self, email: str) -> Usuario | None:
        """
        Busca usuário por email.

        Args:
            email: Email do usuário (case insensitive)

        Returns:
            Usuário encontrado ou None
        """

    @abstractmethod
    def email_exists(self, email: str, exclude_id: UUID | None = None) -> bool:
        """
        Verifica se email já está cadastrado.

        Args:
            email: Email a verificar
            exclude_id: ID de usuário a excluir da verificação (para updates)

        Returns:
            True se email existe, False caso contrário
        """

    @abstractmethod
    def get_by_perfil(self, perfil: PerfilUsuario) -> list[Usuario]:
        """
        Lista usuários por perfil.

        Args:
            perfil: Perfil a filtrar

        Returns:
            Lista de usuários com o perfil especificado
        """

    @abstractmethod
    def get_ativos(self) -> list[Usuario]:
        """
        Lista usuários ativos.

        Returns:
            Lista de usuários ativos
        """

    @abstractmethod
    def get_atendentes_ativos(self) -> list[Usuario]:
        """
        Lista atendentes ativos.

        Returns:
            Lista de usuários atendentes ativos
        """

    @abstractmethod
    def get_paginated(
        self,
        page: int = 1,
        per_page: int = 10,
        perfil: PerfilUsuario | None = None,
        apenas_ativos: bool = False,
    ) -> tuple[list[Usuario], int]:
        """
        Lista usuários paginados.

        Args:
            page: Número da página (1-indexed)
            per_page: Itens por página
            perfil: Filtro opcional por perfil
            apenas_ativos: Se True, retorna apenas ativos

        Returns:
            Tupla com (lista de usuários, total de registros)
        """
