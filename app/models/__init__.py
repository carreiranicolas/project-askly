from app.ext.db import db

from .user import Usuario
from .role import Cargo
from .category import Categoria
from .ticket import Chamado
from .commentary import Comentario
from .history import HistoricoStatus

__all__ = ["db", "Usuario", "Cargo", "Categoria", "Chamado", "Comentario", "HistoricoStatus"]