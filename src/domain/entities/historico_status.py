"""Status history domain entity - Audit trail."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.domain.entities.base import Entity
from src.domain.enums import StatusChamado


@dataclass
class HistoricoStatus(Entity):
    """
    Entidade de histórico de status - Trilha de Auditoria.

    CONSTRAINT CRÍTICO: Toda mudança de status DEVE gerar um registro aqui.
    Esta é uma exigência mandatória do contrato de negócio.

    Attributes:
        chamado_id: ID do chamado relacionado
        alterado_por_usuario_id: ID do usuário que realizou a alteração
        status_anterior: Status antes da alteração (vazio se criação)
        status_novo: Novo status aplicado
        motivo: Motivo opcional da alteração
        alterado_em: Data/hora da alteração
    """

    chamado_id: UUID | None = None
    alterado_por_usuario_id: UUID | None = None
    status_anterior: str = ""
    status_novo: str = ""
    motivo: str | None = None
    alterado_em: datetime = field(default_factory=Entity.now)

    @property
    def is_criacao(self) -> bool:
        """Verifica se é o registro de criação (sem status anterior)."""
        return not self.status_anterior or self.status_anterior == ""

    @property
    def status_anterior_enum(self) -> StatusChamado | None:
        """Retorna o status anterior como enum."""
        if not self.status_anterior:
            return None
        try:
            return StatusChamado(self.status_anterior)
        except ValueError:
            return None

    @property
    def status_novo_enum(self) -> StatusChamado:
        """Retorna o status novo como enum."""
        return StatusChamado(self.status_novo)

    @classmethod
    def criar_para_novo_chamado(cls, chamado_id: UUID, usuario_id: UUID) -> "HistoricoStatus":
        """
        Factory method para criar histórico de novo chamado.

        Args:
            chamado_id: ID do chamado criado
            usuario_id: ID do usuário que criou

        Returns:
            HistoricoStatus com status_anterior vazio e status_novo ABERTO
        """
        return cls(
            chamado_id=chamado_id,
            alterado_por_usuario_id=usuario_id,
            status_anterior="",
            status_novo=StatusChamado.ABERTO.value,
            motivo="Chamado criado",
        )

    @classmethod
    def criar_para_transicao(
        cls,
        chamado_id: UUID,
        usuario_id: UUID,
        status_anterior: StatusChamado,
        status_novo: StatusChamado,
        motivo: str | None = None,
    ) -> "HistoricoStatus":
        """
        Factory method para criar histórico de transição.

        Args:
            chamado_id: ID do chamado
            usuario_id: ID do usuário que alterou
            status_anterior: Status antes da alteração
            status_novo: Novo status
            motivo: Motivo opcional

        Returns:
            HistoricoStatus preenchido
        """
        return cls(
            chamado_id=chamado_id,
            alterado_por_usuario_id=usuario_id,
            status_anterior=status_anterior.value,
            status_novo=status_novo.value,
            motivo=motivo,
        )

    def __repr__(self) -> str:
        return f"HistoricoStatus({self.status_anterior or 'NOVO'} -> {self.status_novo})"
