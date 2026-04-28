"""SQLAlchemy Unit of Work implementation."""

from sqlalchemy.orm import Session

from src.domain.interfaces.repositories import IUnitOfWork
from src.infrastructure.persistence.sqlalchemy.repositories.usuario_repository import UsuarioRepository
from src.infrastructure.persistence.sqlalchemy.repositories.categoria_repository import CategoriaRepository
from src.infrastructure.persistence.sqlalchemy.repositories.chamado_repository import ChamadoRepository
from src.infrastructure.persistence.sqlalchemy.repositories.comentario_repository import ComentarioRepository
from src.infrastructure.persistence.sqlalchemy.repositories.historico_status_repository import HistoricoStatusRepository


class SQLAlchemyUnitOfWork(IUnitOfWork):
    """
    SQLAlchemy implementation of Unit of Work pattern.
    
    Garante que múltiplas operações de repositório sejam
    executadas como uma única transação atômica.
    
    Uso:
        with uow:
            uow.chamados.add(chamado)
            uow.historico_status.add(historico)
            uow.commit()
    """
    
    def __init__(self, session_factory):
        """
        Initialize Unit of Work.
        
        Args:
            session_factory: Callable that returns a new SQLAlchemy session
        """
        self._session_factory = session_factory
        self._session: Session | None = None
    
    def __enter__(self) -> "SQLAlchemyUnitOfWork":
        self._session = self._session_factory()
        
        self.usuarios = UsuarioRepository(self._session)
        self.categorias = CategoriaRepository(self._session)
        self.chamados = ChamadoRepository(self._session)
        self.comentarios = ComentarioRepository(self._session)
        self.historico_status = HistoricoStatusRepository(self._session)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()
        
        if self._session:
            self._session.close()
            self._session = None
    
    def commit(self) -> None:
        """Confirma todas as operações da transação."""
        if self._session:
            self._session.commit()
    
    def rollback(self) -> None:
        """Desfaz todas as operações da transação."""
        if self._session:
            self._session.rollback()
