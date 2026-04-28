"""List Categories Use Case."""

from dataclasses import dataclass

from src.application.dtos import CategoriaResponseDTO


@dataclass
class ListCategoriesUseCase:
    """
    Use Case para listagem de categorias.
    """
    
    unit_of_work: "IUnitOfWork"
    
    def execute(self, apenas_ativas: bool = True) -> list[CategoriaResponseDTO]:
        """
        Lista categorias.
        
        Args:
            apenas_ativas: Se True, retorna apenas ativas
            
        Returns:
            Lista de categorias
        """
        with self.unit_of_work:
            if apenas_ativas:
                categorias = self.unit_of_work.categorias.get_ativas()
            else:
                categorias = self.unit_of_work.categorias.get_all_ordered()
        
        return [CategoriaResponseDTO.from_entity(c) for c in categorias]


from src.domain.interfaces.repositories import IUnitOfWork
