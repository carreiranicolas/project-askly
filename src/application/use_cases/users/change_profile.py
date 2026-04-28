"""Change User Profile Use Case."""

from dataclasses import dataclass
from uuid import UUID

from src.application.dtos import UsuarioResponseDTO
from src.domain.entities import Usuario
from src.domain.enums import PerfilUsuario
from src.domain.exceptions import (
    AuthorizationException,
    EntityNotFoundException,
    ValidationException,
)


@dataclass
class ChangeProfileUseCase:
    """
    Use Case para alteração de perfil de usuário.

    Apenas administradores podem alterar perfis.
    """

    unit_of_work: "IUnitOfWork"

    def execute(
        self, usuario_id: UUID, novo_perfil: PerfilUsuario, admin: Usuario
    ) -> UsuarioResponseDTO:
        """
        Altera o perfil de um usuário.

        Args:
            usuario_id: ID do usuário a alterar
            novo_perfil: Novo perfil
            admin: Administrador realizando a alteração

        Returns:
            Dados do usuário atualizado

        Raises:
            AuthorizationException: Se não é admin
            EntityNotFoundException: Se usuário não existe
        """
        if not admin.pode_gerenciar_usuarios():
            raise AuthorizationException(
                "Apenas administradores podem alterar perfis", required_permission="manage_users"
            )

        with self.unit_of_work:
            usuario = self.unit_of_work.usuarios.get_by_id(usuario_id)
            if not usuario:
                raise EntityNotFoundException("Usuário", usuario_id)

            if usuario.id == admin.id and novo_perfil != PerfilUsuario.ADMIN:
                raise ValidationException("Você não pode rebaixar seu próprio perfil de admin")

            usuario.alterar_perfil(novo_perfil)

            self.unit_of_work.usuarios.update(usuario)
            self.unit_of_work.commit()

        return UsuarioResponseDTO.from_entity(usuario)


from src.domain.interfaces.repositories import IUnitOfWork
