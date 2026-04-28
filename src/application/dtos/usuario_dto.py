"""User DTOs."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.domain.enums import PerfilUsuario


@dataclass
class UsuarioCreateDTO:
    """DTO para criação de usuário."""

    nome: str
    email: str
    senha: str
    confirmar_senha: str
    perfil: PerfilUsuario = PerfilUsuario.SOLICITANTE


@dataclass
class UsuarioUpdateDTO:
    """DTO para atualização de usuário."""

    id: UUID
    nome: str | None = None
    email: str | None = None
    perfil: PerfilUsuario | None = None
    ativo: bool | None = None


@dataclass
class UsuarioResponseDTO:
    """DTO de resposta de usuário."""

    id: UUID
    nome: str
    email: str
    perfil: str
    perfil_display: str
    ativo: bool
    criado_em: datetime

    @classmethod
    def from_entity(cls, usuario) -> "UsuarioResponseDTO":
        """Cria DTO a partir de entidade."""
        return cls(
            id=usuario.id,
            nome=usuario.nome,
            email=usuario.email,
            perfil=(
                usuario.perfil.value
                if isinstance(usuario.perfil, PerfilUsuario)
                else usuario.perfil
            ),
            perfil_display=(
                usuario.perfil.display_name
                if isinstance(usuario.perfil, PerfilUsuario)
                else usuario.perfil
            ),
            ativo=usuario.ativo,
            criado_em=usuario.criado_em,
        )


@dataclass
class LoginDTO:
    """DTO para login."""

    email: str
    senha: str
    lembrar: bool = False


@dataclass
class LoginResponseDTO:
    """DTO de resposta de login."""

    usuario: UsuarioResponseDTO
    token: str | None = None
