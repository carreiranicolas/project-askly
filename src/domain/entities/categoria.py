"""Category domain entity."""

from dataclasses import dataclass, field
from datetime import datetime

from src.domain.entities.base import Entity


@dataclass
class Categoria(Entity):
    """
    Entidade de categoria de chamados.

    Categorias são usadas para classificar e organizar chamados.
    Gerenciadas exclusivamente por administradores.

    Attributes:
        nome: Nome único da categoria
        descricao: Descrição opcional da categoria
        ativa: Se a categoria está ativa (disponível para novos chamados)
        criado_em: Data de criação do registro
    """

    nome: str = ""
    descricao: str | None = None
    ativa: bool = True
    criado_em: datetime = field(default_factory=Entity.now)

    def __post_init__(self):
        """Normaliza o nome."""
        if self.nome:
            self.nome = self.nome.strip()

    def desativar(self) -> None:
        """Desativa a categoria."""
        self.ativa = False

    def ativar(self) -> None:
        """Ativa a categoria."""
        self.ativa = True

    def __repr__(self) -> str:
        status = "ativa" if self.ativa else "inativa"
        return f"Categoria(id={self.id}, nome='{self.nome}', {status})"
