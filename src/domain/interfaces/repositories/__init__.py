"""Repository interfaces - Contratos de acesso a dados."""

from src.domain.interfaces.repositories.base import IRepository
from src.domain.interfaces.repositories.usuario_repository import IUsuarioRepository
from src.domain.interfaces.repositories.categoria_repository import ICategoriaRepository
from src.domain.interfaces.repositories.chamado_repository import IChamadoRepository
from src.domain.interfaces.repositories.comentario_repository import IComentarioRepository
from src.domain.interfaces.repositories.historico_status_repository import IHistoricoStatusRepository
from src.domain.interfaces.repositories.unit_of_work import IUnitOfWork

__all__ = [
    "IRepository",
    "IUsuarioRepository",
    "ICategoriaRepository",
    "IChamadoRepository",
    "IComentarioRepository",
    "IHistoricoStatusRepository",
    "IUnitOfWork",
]
