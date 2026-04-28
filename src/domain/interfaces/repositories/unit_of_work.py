"""Unit of Work interface - Transaction management."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.interfaces.repositories import (
        ICategoriaRepository,
        IChamadoRepository,
        IComentarioRepository,
        IHistoricoStatusRepository,
        IUsuarioRepository,
    )


class IUnitOfWork(ABC):
    """
    Interface Unit of Work - Gerenciamento de transações.

    Padrão que garante que múltiplas operações de repositório
    sejam executadas como uma única transação atômica.

    Uso típico:
        with uow:
            uow.chamados.add(chamado)
            uow.historico_status.add(historico)
            uow.commit()  # Ambos salvos atomicamente

    IMPORTANTE para constraint de auditoria:
        Alterações de status + registro em historico_status
        devem SEMPRE estar na mesma transação.
    """

    usuarios: "IUsuarioRepository"
    categorias: "ICategoriaRepository"
    chamados: "IChamadoRepository"
    comentarios: "IComentarioRepository"
    historico_status: "IHistoricoStatusRepository"

    @abstractmethod
    def __enter__(self) -> "IUnitOfWork":
        """Inicia o contexto da transação."""
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Finaliza o contexto da transação.

        Se houver exceção, faz rollback automaticamente.
        """
        pass

    @abstractmethod
    def commit(self) -> None:
        """
        Confirma todas as operações da transação.

        Raises:
            Exception: Se houver erro no commit
        """
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Desfaz todas as operações da transação."""
        pass
