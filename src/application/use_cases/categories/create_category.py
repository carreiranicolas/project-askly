"""Create Category Use Case."""

from dataclasses import dataclass

from src.application.dtos import CategoriaCreateDTO, CategoriaResponseDTO
from src.domain.entities import Categoria, Usuario
from src.domain.exceptions import AuthorizationException, ValidationException


@dataclass
class CreateCategoryUseCase:
    """
    Use Case para criação de categoria.

    Apenas administradores podem criar categorias.
    """

    unit_of_work: "IUnitOfWork"

    def execute(self, dto: CategoriaCreateDTO, usuario: Usuario) -> CategoriaResponseDTO:
        """
        Cria uma nova categoria.

        Args:
            dto: Dados da categoria
            usuario: Usuário realizando a criação

        Returns:
            Dados da categoria criada

        Raises:
            AuthorizationException: Se usuário não é admin
            ValidationException: Se nome já existe ou inválido
        """
        if not usuario.pode_gerenciar_categorias():
            raise AuthorizationException(
                "Apenas administradores podem criar categorias",
                required_permission="manage_categories",
            )

        if not dto.nome or not dto.nome.strip():
            raise ValidationException("Nome é obrigatório", field="nome")

        nome = dto.nome.strip()

        with self.unit_of_work:
            if self.unit_of_work.categorias.nome_exists(nome):
                raise ValidationException("Já existe uma categoria com este nome", field="nome")

            categoria = Categoria(
                nome=nome,
                descricao=dto.descricao.strip() if dto.descricao else None,
                ativa=True,
            )

            self.unit_of_work.categorias.add(categoria)
            self.unit_of_work.commit()

        return CategoriaResponseDTO.from_entity(categoria)


from src.domain.interfaces.repositories import IUnitOfWork
