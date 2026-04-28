"""Create Ticket Use Case."""

from dataclasses import dataclass

from src.application.dtos import ChamadoCreateDTO, ChamadoResponseDTO
from src.domain.entities import Chamado, HistoricoStatus, Usuario
from src.domain.enums import StatusChamado
from src.domain.exceptions import EntityNotFoundException, ValidationException


@dataclass
class CreateTicketUseCase:
    """
    Use Case para criação de chamado.

    CONSTRAINT CRÍTICO: A criação DEVE gerar registro inicial
    em historico_status na mesma transação.
    """

    unit_of_work: "IUnitOfWork"

    def execute(self, dto: ChamadoCreateDTO, solicitante: Usuario) -> ChamadoResponseDTO:
        """
        Cria um novo chamado.

        Args:
            dto: Dados do chamado
            solicitante: Usuário solicitante

        Returns:
            Dados do chamado criado

        Raises:
            ValidationException: Se dados inválidos
            EntityNotFoundException: Se categoria não existe
        """
        if not dto.titulo or not dto.titulo.strip():
            raise ValidationException("Título é obrigatório", field="titulo")

        if not dto.descricao or not dto.descricao.strip():
            raise ValidationException("Descrição é obrigatória", field="descricao")

        with self.unit_of_work:
            categoria = self.unit_of_work.categorias.get_by_id(dto.categoria_id)
            if not categoria:
                raise EntityNotFoundException("Categoria", dto.categoria_id)

            if not categoria.ativa:
                raise ValidationException("Esta categoria está desativada", field="categoria_id")

            chamado = Chamado(
                titulo=dto.titulo.strip(),
                descricao=dto.descricao.strip(),
                prioridade=dto.prioridade,
                status_atual=StatusChamado.ABERTO,
                categoria_id=dto.categoria_id,
                solicitante_id=solicitante.id,
            )

            self.unit_of_work.chamados.add(chamado)

            historico = HistoricoStatus.criar_para_novo_chamado(
                chamado_id=chamado.id, usuario_id=solicitante.id
            )
            self.unit_of_work.historico_status.add(historico)

            self.unit_of_work.commit()

        return ChamadoResponseDTO.from_entity(
            chamado, categoria_nome=categoria.nome, solicitante_nome=solicitante.nome
        )


from src.domain.interfaces.repositories import IUnitOfWork
