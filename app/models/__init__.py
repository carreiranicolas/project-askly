from app.ext.db import db

from .user import Usuario
from .category import Categoria
from .ticket import Chamado
from .commentary import Comentario
from .history import HistoricoStatus

__all__ = ["db", "Usuario", "Categoria", "Chamado", "Comentario", "HistoricoStatus"]