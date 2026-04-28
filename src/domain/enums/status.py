"""Enum de status de chamados com regras de transição."""

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.enums.perfil import PerfilUsuario


class StatusChamado(str, Enum):
    """
    Status do ciclo de vida de um chamado.

    Fluxo:
        ABERTO → EM_ATENDIMENTO → AGUARDANDO_RETORNO ↔ EM_ATENDIMENTO
                                ↓
                            RESOLVIDO → FECHADO
                                ↓
                          (reabertura até 3 dias)
                                ↓
                          EM_ATENDIMENTO
    """

    ABERTO = "ABERTO"
    EM_ATENDIMENTO = "EM_ATENDIMENTO"
    AGUARDANDO_RETORNO = "AGUARDANDO_RETORNO"
    RESOLVIDO = "RESOLVIDO"
    FECHADO = "FECHADO"

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        """Retorna lista de choices para formulários."""
        return [(s.value, s.display_name) for s in cls]

    @property
    def display_name(self) -> str:
        """Nome de exibição do status."""
        names = {
            self.ABERTO: "Aberto",
            self.EM_ATENDIMENTO: "Em Atendimento",
            self.AGUARDANDO_RETORNO: "Aguardando Retorno",
            self.RESOLVIDO: "Resolvido",
            self.FECHADO: "Fechado",
        }
        return names.get(self, self.value)

    @property
    def cor_hex(self) -> str:
        """Cor hexadecimal conforme especificação do contrato."""
        cores = {
            self.ABERTO: "#209cee",
            self.EM_ATENDIMENTO: "#3273dc",
            self.AGUARDANDO_RETORNO: "#00d1b2",
            self.RESOLVIDO: "#ffdd57",
            self.FECHADO: "#ff3860",
        }
        return cores.get(self, "#363636")

    @property
    def cor_bulma(self) -> str:
        """Classe CSS Bulma correspondente."""
        cores = {
            self.ABERTO: "is-info",
            self.EM_ATENDIMENTO: "is-link",
            self.AGUARDANDO_RETORNO: "is-primary",
            self.RESOLVIDO: "is-warning",
            self.FECHADO: "is-danger",
        }
        return cores.get(self, "is-light")

    def transicoes_permitidas(self) -> list["StatusChamado"]:
        """Retorna lista de status para os quais pode transicionar."""
        from src.domain.enums.perfil import PerfilUsuario

        transicoes = {
            self.ABERTO: [self.EM_ATENDIMENTO],
            self.EM_ATENDIMENTO: [self.AGUARDANDO_RETORNO, self.RESOLVIDO],
            self.AGUARDANDO_RETORNO: [self.EM_ATENDIMENTO, self.RESOLVIDO],
            self.RESOLVIDO: [self.FECHADO, self.EM_ATENDIMENTO],
            self.FECHADO: [],
        }
        return transicoes.get(self, [])

    def roles_permitidos_transicao(self, destino: "StatusChamado") -> list["PerfilUsuario"]:
        """Retorna perfis que podem realizar a transição para o destino."""
        from src.domain.enums.perfil import PerfilUsuario

        if destino not in self.transicoes_permitidas():
            return []

        regras = {
            (self.ABERTO, self.EM_ATENDIMENTO): [PerfilUsuario.ATENDENTE, PerfilUsuario.ADMIN],
            (self.EM_ATENDIMENTO, self.AGUARDANDO_RETORNO): [
                PerfilUsuario.ATENDENTE,
                PerfilUsuario.ADMIN,
            ],
            (self.EM_ATENDIMENTO, self.RESOLVIDO): [PerfilUsuario.ATENDENTE, PerfilUsuario.ADMIN],
            (self.AGUARDANDO_RETORNO, self.EM_ATENDIMENTO): [
                PerfilUsuario.ATENDENTE,
                PerfilUsuario.ADMIN,
            ],
            (self.AGUARDANDO_RETORNO, self.RESOLVIDO): [
                PerfilUsuario.ATENDENTE,
                PerfilUsuario.ADMIN,
            ],
            (self.RESOLVIDO, self.FECHADO): [
                PerfilUsuario.SOLICITANTE,
                PerfilUsuario.ADMIN,
            ],
            (self.RESOLVIDO, self.EM_ATENDIMENTO): [
                PerfilUsuario.SOLICITANTE,
                PerfilUsuario.ATENDENTE,
                PerfilUsuario.ADMIN,
            ],
        }
        return regras.get((self, destino), [])

    def is_terminal(self) -> bool:
        """Verifica se é um status terminal (sem transições)."""
        return self == self.FECHADO

    def is_ativo(self) -> bool:
        """Verifica se o chamado está ativo (não fechado)."""
        return self not in (self.FECHADO, self.RESOLVIDO)
