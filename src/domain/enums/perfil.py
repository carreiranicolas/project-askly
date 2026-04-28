"""Enum de perfis de usuário do sistema."""

from enum import Enum


class PerfilUsuario(str, Enum):
    """
    Perfis de usuário disponíveis no sistema (RBAC).

    Attributes:
        SOLICITANTE: Colaborador que abre e acompanha chamados
        ATENDENTE: Técnico/Analista que atende chamados
        ADMIN: Administrador com acesso total
    """

    SOLICITANTE = "solicitante"
    ATENDENTE = "atendente"
    ADMIN = "admin"

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        """Retorna lista de choices para formulários."""
        return [(p.value, p.display_name) for p in cls]

    @property
    def display_name(self) -> str:
        """Nome de exibição do perfil."""
        names = {
            self.SOLICITANTE: "Solicitante",
            self.ATENDENTE: "Atendente",
            self.ADMIN: "Administrador",
        }
        return names.get(self, self.value)

    def pode_ver_todos_chamados(self) -> bool:
        """Verifica se o perfil pode ver todos os chamados."""
        return self in (self.ATENDENTE, self.ADMIN)

    def pode_gerenciar_usuarios(self) -> bool:
        """Verifica se o perfil pode gerenciar usuários."""
        return self == self.ADMIN

    def pode_gerenciar_categorias(self) -> bool:
        """Verifica se o perfil pode gerenciar categorias."""
        return self == self.ADMIN
