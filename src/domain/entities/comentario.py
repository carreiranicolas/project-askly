"""Comment domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.domain.entities.base import Entity


@dataclass
class Comentario(Entity):
    """
    Entidade de comentário em chamado.

    Representa uma mensagem trocada dentro de um chamado,
    seja do solicitante, atendente ou administrador.

    Attributes:
        chamado_id: ID do chamado relacionado
        autor_id: ID do usuário autor do comentário
        conteudo: Texto do comentário
        criado_em: Data/hora de criação
    """

    chamado_id: UUID | None = None
    autor_id: UUID | None = None
    conteudo: str = ""
    criado_em: datetime = field(default_factory=Entity.now)

    def __post_init__(self):
        """Normaliza o conteúdo."""
        if self.conteudo:
            self.conteudo = self.conteudo.strip()

    @property
    def is_vazio(self) -> bool:
        return not self.conteudo or len(self.conteudo.strip()) == 0

    def __repr__(self) -> str:
        preview = self.conteudo[:50] if self.conteudo else ""
        return f"Comentario(id={self.id}, chamado_id={self.chamado_id}, conteudo='{preview}...')"
