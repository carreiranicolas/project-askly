"""Base repository interface."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from src.domain.entities.base import Entity

T = TypeVar("T", bound=Entity)


class IRepository(ABC, Generic[T]):
    """
    Interface base para repositórios.

    Define operações CRUD básicas que todos os repositórios devem implementar.
    Segue o Repository Pattern para abstrair o acesso a dados.
    """

    @abstractmethod
    def get_by_id(self, entity_id: UUID) -> T | None:
        """
        Busca entidade por ID.

        Args:
            entity_id: UUID da entidade

        Returns:
            Entidade encontrada ou None
        """
        pass

    @abstractmethod
    def get_all(self) -> list[T]:
        """
        Retorna todas as entidades.

        Returns:
            Lista de entidades
        """
        pass

    @abstractmethod
    def add(self, entity: T) -> T:
        """
        Adiciona uma nova entidade.

        Args:
            entity: Entidade a ser adicionada

        Returns:
            Entidade adicionada (com ID gerado se aplicável)
        """
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        """
        Atualiza uma entidade existente.

        Args:
            entity: Entidade com dados atualizados

        Returns:
            Entidade atualizada
        """
        pass

    @abstractmethod
    def delete(self, entity_id: UUID) -> bool:
        """
        Remove uma entidade.

        Args:
            entity_id: UUID da entidade a remover

        Returns:
            True se removida, False se não encontrada
        """
        pass

    @abstractmethod
    def exists(self, entity_id: UUID) -> bool:
        """
        Verifica se entidade existe.

        Args:
            entity_id: UUID da entidade

        Returns:
            True se existe, False caso contrário
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Conta total de entidades.

        Returns:
            Número total de entidades
        """
        pass
