"""Domain entities - Entidades de negócio."""

from src.domain.entities.base import Entity
from src.domain.entities.categoria import Categoria
from src.domain.entities.chamado import Chamado
from src.domain.entities.comentario import Comentario
from src.domain.entities.historico_status import HistoricoStatus
from src.domain.entities.usuario import Usuario

__all__ = [
    "Entity",
    "Usuario",
    "Categoria",
    "Chamado",
    "Comentario",
    "HistoricoStatus",
]
