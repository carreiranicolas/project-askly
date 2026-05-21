from app.ext.db import db

from .user import Usuario
from .role import Cargo
from .category import Categoria
from .ticket import Chamado
from .commentary import Comentario
from .history import HistoricoStatus
from .priority import Prioridade

__all__ = ["db", "Usuario", "Cargo", "Categoria", "Chamado", "Prioridade", "Comentario", "HistoricoStatus"]