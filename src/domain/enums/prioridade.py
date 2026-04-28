"""Enum de prioridades de chamados."""

from enum import Enum


class Prioridade(str, Enum):
    """
    Níveis de prioridade para chamados.

    A prioridade define a urgência do atendimento.
    """

    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        """Retorna lista de choices para formulários."""
        return [(p.value, p.display_name) for p in cls]

    @property
    def display_name(self) -> str:
        """Nome de exibição da prioridade."""
        names = {
            self.BAIXA: "Baixa",
            self.MEDIA: "Média",
            self.ALTA: "Alta",
            self.CRITICA: "Crítica",
        }
        return names.get(self, self.value)

    @property
    def peso(self) -> int:
        """Peso numérico para ordenação (maior = mais urgente)."""
        pesos = {
            self.BAIXA: 1,
            self.MEDIA: 2,
            self.ALTA: 3,
            self.CRITICA: 4,
        }
        return pesos.get(self, 0)

    @property
    def cor_css(self) -> str:
        """Classe CSS Bulma para a prioridade."""
        cores = {
            self.BAIXA: "is-info",
            self.MEDIA: "is-warning",
            self.ALTA: "is-danger",
            self.CRITICA: "is-danger is-dark",
        }
        return cores.get(self, "is-light")
