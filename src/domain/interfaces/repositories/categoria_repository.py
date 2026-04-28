"""Category repository interface."""

from abc import abstractmethod
from uuid import UUID

from src.domain.entities import Categoria
from src.domain.interfaces.repositories.base import IRepository


class ICategoriaRepository(IRepository[Categoria]):
    """
    Interface de repositório para Categorias.
    """

    @abstractmethod
    def get_by_nome(self, nome: str) -> Categoria | None:
        """
        Busca categoria por nome.

        Args:
            nome: Nome da categoria (case insensitive)

        Returns:
            Categoria encontrada ou None
        """

    @abstractmethod
    def nome_exists(self, nome: str, exclude_id: UUID | None = None) -> bool:
        """
        Verifica se nome já existe.

        Args:
            nome: Nome a verificar
            exclude_id: ID a excluir da verificação

        Returns:
            True se nome existe, False caso contrário
        """

    @abstractmethod
    def get_ativas(self) -> list[Categoria]:
        """
        Lista categorias ativas.

        Returns:
            Lista de categorias ativas ordenadas por nome
        """

    @abstractmethod
    def get_all_ordered(self) -> list[Categoria]:
        """
        Lista todas as categorias ordenadas por nome.

        Returns:
            Lista de categorias ordenadas
        """
