"""Status history repository interface."""

from abc import abstractmethod
from uuid import UUID

from src.domain.entities import HistoricoStatus
from src.domain.interfaces.repositories.base import IRepository


class IHistoricoStatusRepository(IRepository[HistoricoStatus]):
    """
    Interface de repositório para Histórico de Status.
    
    IMPORTANTE: Este repositório é crítico para auditoria.
    """
    
    @abstractmethod
    def get_by_chamado(
        self, 
        chamado_id: UUID,
        order_asc: bool = True
    ) -> list[HistoricoStatus]:
        """
        Lista histórico de um chamado.
        
        Args:
            chamado_id: ID do chamado
            order_asc: Se True, ordena por data crescente
            
        Returns:
            Lista de registros de histórico ordenados
        """
        pass
    
    @abstractmethod
    def get_ultimo_by_chamado(self, chamado_id: UUID) -> HistoricoStatus | None:
        """
        Retorna o último registro de histórico de um chamado.
        
        Args:
            chamado_id: ID do chamado
            
        Returns:
            Último registro ou None
        """
        pass
    
    @abstractmethod
    def count_by_chamado(self, chamado_id: UUID) -> int:
        """
        Conta registros de histórico de um chamado.
        
        Args:
            chamado_id: ID do chamado
            
        Returns:
            Número de registros
        """
        pass
    
    @abstractmethod
    def get_by_usuario(self, usuario_id: UUID) -> list[HistoricoStatus]:
        """
        Lista alterações feitas por um usuário.
        
        Args:
            usuario_id: ID do usuário
            
        Returns:
            Lista de registros
        """
        pass
