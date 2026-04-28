"""Ticket repository interface."""

from abc import abstractmethod
from datetime import datetime
from uuid import UUID

from src.domain.entities import Chamado
from src.domain.enums import StatusChamado, Prioridade
from src.domain.interfaces.repositories.base import IRepository


class IChamadoRepository(IRepository[Chamado]):
    """
    Interface de repositório para Chamados.
    """
    
    @abstractmethod
    def get_by_solicitante(
        self, 
        solicitante_id: UUID,
        page: int = 1,
        per_page: int = 10
    ) -> tuple[list[Chamado], int]:
        """
        Lista chamados de um solicitante.
        
        Args:
            solicitante_id: ID do solicitante
            page: Página
            per_page: Itens por página
            
        Returns:
            Tupla com (lista de chamados, total)
        """
        pass
    
    @abstractmethod
    def get_by_atendente(
        self, 
        atendente_id: UUID,
        page: int = 1,
        per_page: int = 10
    ) -> tuple[list[Chamado], int]:
        """
        Lista chamados de um atendente.
        
        Args:
            atendente_id: ID do atendente
            page: Página
            per_page: Itens por página
            
        Returns:
            Tupla com (lista de chamados, total)
        """
        pass
    
    @abstractmethod
    def get_fila_atendimento(
        self,
        page: int = 1,
        per_page: int = 10,
        status: StatusChamado | None = None,
        prioridade: Prioridade | None = None,
        categoria_id: UUID | None = None
    ) -> tuple[list[Chamado], int]:
        """
        Lista fila de atendimento (chamados não fechados).
        
        Args:
            page: Página
            per_page: Itens por página
            status: Filtro por status
            prioridade: Filtro por prioridade
            categoria_id: Filtro por categoria
            
        Returns:
            Tupla com (lista de chamados, total)
        """
        pass
    
    @abstractmethod
    def get_paginated_filtered(
        self,
        page: int = 1,
        per_page: int = 10,
        status: StatusChamado | None = None,
        prioridade: Prioridade | None = None,
        categoria_id: UUID | None = None,
        solicitante_id: UUID | None = None,
        atendente_id: UUID | None = None,
        data_inicio: datetime | None = None,
        data_fim: datetime | None = None
    ) -> tuple[list[Chamado], int]:
        """
        Lista chamados com filtros avançados.
        
        Args:
            page: Página
            per_page: Itens por página
            status: Filtro por status
            prioridade: Filtro por prioridade
            categoria_id: Filtro por categoria
            solicitante_id: Filtro por solicitante
            atendente_id: Filtro por atendente
            data_inicio: Filtro por data inicial
            data_fim: Filtro por data final
            
        Returns:
            Tupla com (lista de chamados, total)
        """
        pass
    
    @abstractmethod
    def count_by_status(self) -> dict[StatusChamado, int]:
        """
        Conta chamados agrupados por status.
        
        Returns:
            Dicionário status -> contagem
        """
        pass
    
    @abstractmethod
    def count_by_categoria(self) -> dict[UUID, int]:
        """
        Conta chamados agrupados por categoria.
        
        Returns:
            Dicionário categoria_id -> contagem
        """
        pass
    
    @abstractmethod
    def get_abertos_sem_atendente(self) -> list[Chamado]:
        """
        Lista chamados abertos sem atendente atribuído.
        
        Returns:
            Lista de chamados
        """
        pass
