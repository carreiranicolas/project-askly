"""Ticket DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.enums import Prioridade, StatusChamado


@dataclass
class ChamadoCreateDTO:
    """DTO para criação de chamado."""

    titulo: str
    descricao: str
    categoria_id: UUID
    prioridade: Prioridade = Prioridade.MEDIA


@dataclass
class ChamadoUpdateDTO:
    """DTO para atualização de chamado."""

    id: UUID
    titulo: str | None = None
    descricao: str | None = None
    prioridade: Prioridade | None = None


@dataclass
class ChamadoResponseDTO:
    """DTO de resposta de chamado."""

    id: UUID
    titulo: str
    descricao: str
    prioridade: str
    prioridade_display: str
    prioridade_css: str
    status_atual: str
    status_display: str
    status_cor: str
    status_css: str
    categoria_id: UUID
    categoria_nome: str | None
    solicitante_id: UUID
    solicitante_nome: str | None
    atendente_id: UUID | None
    atendente_nome: str | None
    resolvido_em: datetime | None
    fechado_em: datetime | None
    criado_em: datetime
    atualizado_em: datetime
    transicoes_disponiveis: list[str] | None = None

    @classmethod
    def from_entity(
        cls,
        chamado,
        categoria_nome: str | None = None,
        solicitante_nome: str | None = None,
        atendente_nome: str | None = None,
        transicoes: list[StatusChamado] | None = None,
    ) -> "ChamadoResponseDTO":
        """Cria DTO a partir de entidade."""
        status = chamado.status_atual
        prioridade = chamado.prioridade

        if isinstance(status, StatusChamado):
            status_val = status.value
            status_display = status.display_name
            status_cor = status.cor_hex
            status_css = status.cor_bulma
        else:
            status_val = status
            status_display = status
            status_cor = "#363636"
            status_css = "is-light"

        if isinstance(prioridade, Prioridade):
            prioridade_val = prioridade.value
            prioridade_display = prioridade.display_name
            prioridade_css = prioridade.cor_css
        else:
            prioridade_val = prioridade
            prioridade_display = prioridade
            prioridade_css = "is-light"

        return cls(
            id=chamado.id,
            titulo=chamado.titulo,
            descricao=chamado.descricao,
            prioridade=prioridade_val,
            prioridade_display=prioridade_display,
            prioridade_css=prioridade_css,
            status_atual=status_val,
            status_display=status_display,
            status_cor=status_cor,
            status_css=status_css,
            categoria_id=chamado.categoria_id,
            categoria_nome=categoria_nome,
            solicitante_id=chamado.solicitante_id,
            solicitante_nome=solicitante_nome,
            atendente_id=chamado.atendente_id,
            atendente_nome=atendente_nome,
            resolvido_em=chamado.resolvido_em,
            fechado_em=chamado.fechado_em,
            criado_em=chamado.criado_em,
            atualizado_em=chamado.atualizado_em,
            transicoes_disponiveis=[t.value for t in transicoes] if transicoes else None,
        )


@dataclass
class ChamadoListFilterDTO:
    """DTO para filtros de listagem de chamados."""

    status: StatusChamado | None = None
    prioridade: Prioridade | None = None
    categoria_id: UUID | None = None
    solicitante_id: UUID | None = None
    atendente_id: UUID | None = None
    data_inicio: datetime | None = None
    data_fim: datetime | None = None
    page: int = 1
    per_page: int = 10


@dataclass
class AlterarStatusDTO:
    """DTO para alteração de status."""

    chamado_id: UUID
    novo_status: StatusChamado
    motivo: str | None = None


@dataclass
class AtribuirAtendenteDTO:
    """DTO para atribuição de atendente."""

    chamado_id: UUID
    atendente_id: UUID
