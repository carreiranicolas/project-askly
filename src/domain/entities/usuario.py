"""User domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.domain.entities.base import Entity
from src.domain.enums import PerfilUsuario


@dataclass
class Usuario(Entity):
    """
    Entidade de usuário do sistema.

    Representa um usuário com suas credenciais e perfil de acesso.
    A senha é armazenada como hash (nunca em texto plano).

    Attributes:
        nome: Nome completo do usuário
        email: Email único (usado para login)
        senha_hash: Hash da senha (Werkzeug/bcrypt)
        perfil: Perfil de acesso (RBAC)
        ativo: Se o usuário está ativo no sistema
        criado_em: Data de criação do registro
    """

    nome: str = ""
    email: str = ""
    senha_hash: str = ""
    perfil: PerfilUsuario = PerfilUsuario.SOLICITANTE
    ativo: bool = True
    criado_em: datetime = field(default_factory=Entity.now)

    def __post_init__(self):
        """Normaliza o email para lowercase."""
        if self.email:
            self.email = self.email.lower().strip()

    @property
    def is_admin(self) -> bool:
        return self.perfil == PerfilUsuario.ADMIN

    @property
    def is_atendente(self) -> bool:
        return self.perfil == PerfilUsuario.ATENDENTE

    @property
    def is_solicitante(self) -> bool:
        return self.perfil == PerfilUsuario.SOLICITANTE

    def pode_ver_todos_chamados(self) -> bool:
        """Admin e atendente podem ver todos os chamados."""
        return self.perfil.pode_ver_todos_chamados()

    def pode_gerenciar_usuarios(self) -> bool:
        """Somente admin pode gerenciar usuários."""
        return self.perfil.pode_gerenciar_usuarios()

    def pode_gerenciar_categorias(self) -> bool:
        """Somente admin pode gerenciar categorias."""
        return self.perfil.pode_gerenciar_categorias()

    def pode_atribuir_chamados(self) -> bool:
        """Atendente e admin podem atribuir chamados."""
        return self.perfil in (PerfilUsuario.ATENDENTE, PerfilUsuario.ADMIN)

    def pode_acessar_relatorios(self) -> bool:
        """Somente admin pode acessar relatórios."""
        return self.perfil == PerfilUsuario.ADMIN

    def alterar_perfil(self, novo_perfil: PerfilUsuario) -> None:
        """Altera o perfil do usuário."""
        self.perfil = novo_perfil

    def desativar(self) -> None:
        """Desativa o usuário."""
        self.ativo = False

    def ativar(self) -> None:
        """Ativa o usuário."""
        self.ativo = True

    def __repr__(self) -> str:
        return f"Usuario(id={self.id}, email='{self.email}', perfil={self.perfil.value})"
