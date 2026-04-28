"""Comment DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class ComentarioCreateDTO:
    """DTO para criação de comentário."""
    chamado_id: UUID
    conteudo: str


@dataclass
class ComentarioResponseDTO:
    """DTO de resposta de comentário."""
    id: UUID
    chamado_id: UUID
    autor_id: UUID
    autor_nome: str | None
    conteudo: str
    criado_em: datetime
    
    @classmethod
    def from_entity(cls, comentario, autor_nome: str | None = None) -> "ComentarioResponseDTO":
        """Cria DTO a partir de entidade."""
        return cls(
            id=comentario.id,
            chamado_id=comentario.chamado_id,
            autor_id=comentario.autor_id,
            autor_nome=autor_nome,
            conteudo=comentario.conteudo,
            criado_em=comentario.criado_em,
        )
