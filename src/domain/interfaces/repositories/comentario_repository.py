"""Comment repository interface."""

from abc import abstractmethod
from uuid import UUID

from src.domain.entities import Comentario
from src.domain.interfaces.repositories.base import IRepository


class IComentarioRepository(IRepository[Comentario]):
    """
    Interface de repositório para Comentários.
    """
    
    @abstractmethod
    def get_by_chamado(
        self, 
        chamado_id: UUID,
        order_asc: bool = True
    ) -> list[Comentario]:
        """
        Lista comentários de um chamado.
        
        Args:
            chamado_id: ID do chamado
            order_asc: Se True, ordena por data crescente
            
        Returns:
            Lista de comentários ordenados
        """
        pass
    
    @abstractmethod
    def count_by_chamado(self, chamado_id: UUID) -> int:
        """
        Conta comentários de um chamado.
        
        Args:
            chamado_id: ID do chamado
            
        Returns:
            Número de comentários
        """
        pass
    
    @abstractmethod
    def get_by_autor(self, autor_id: UUID) -> list[Comentario]:
        """
        Lista comentários de um autor.
        
        Args:
            autor_id: ID do autor
            
        Returns:
            Lista de comentários
        """
        pass
