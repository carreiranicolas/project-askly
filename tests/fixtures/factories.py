"""Factory Boy factories for test data generation."""

from datetime import datetime, timezone
from uuid import uuid4

import factory
from factory import Faker

from src.domain.entities import Categoria, Chamado, Comentario, HistoricoStatus, Usuario
from src.domain.enums import PerfilUsuario, Prioridade, StatusChamado


class UsuarioFactory(factory.Factory):
    """Factory for Usuario domain entity."""

    class Meta:
        model = Usuario

    id = factory.LazyFunction(uuid4)
    nome = Faker("name", locale="pt_BR")
    email = Faker("email")
    senha_hash = "hashed_password"
    perfil = PerfilUsuario.SOLICITANTE
    ativo = True
    criado_em = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    class Params:
        admin = factory.Trait(perfil=PerfilUsuario.ADMIN)
        atendente = factory.Trait(perfil=PerfilUsuario.ATENDENTE)
        inativo = factory.Trait(ativo=False)


class CategoriaFactory(factory.Factory):
    """Factory for Categoria domain entity."""

    class Meta:
        model = Categoria

    id = factory.LazyFunction(uuid4)
    nome = Faker("word")
    descricao = Faker("sentence")
    ativa = True
    criado_em = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    class Params:
        inativa = factory.Trait(ativa=False)


class ChamadoFactory(factory.Factory):
    """Factory for Chamado domain entity."""

    class Meta:
        model = Chamado

    id = factory.LazyFunction(uuid4)
    titulo = Faker("sentence", nb_words=5)
    descricao = Faker("paragraph")
    prioridade = Prioridade.MEDIA
    status_atual = StatusChamado.ABERTO
    categoria_id = factory.LazyFunction(uuid4)
    solicitante_id = factory.LazyFunction(uuid4)
    atendente_id = None
    resolvido_em = None
    fechado_em = None
    criado_em = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    atualizado_em = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    class Params:
        alta_prioridade = factory.Trait(prioridade=Prioridade.ALTA)
        critica = factory.Trait(prioridade=Prioridade.CRITICA)
        em_atendimento = factory.Trait(status_atual=StatusChamado.EM_ATENDIMENTO)
        resolvido = factory.Trait(
            status_atual=StatusChamado.RESOLVIDO,
            resolvido_em=factory.LazyFunction(lambda: datetime.now(timezone.utc)),
        )
        fechado = factory.Trait(
            status_atual=StatusChamado.FECHADO,
            fechado_em=factory.LazyFunction(lambda: datetime.now(timezone.utc)),
        )


class ComentarioFactory(factory.Factory):
    """Factory for Comentario domain entity."""

    class Meta:
        model = Comentario

    id = factory.LazyFunction(uuid4)
    chamado_id = factory.LazyFunction(uuid4)
    autor_id = factory.LazyFunction(uuid4)
    conteudo = Faker("paragraph")
    criado_em = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class HistoricoStatusFactory(factory.Factory):
    """Factory for HistoricoStatus domain entity."""

    class Meta:
        model = HistoricoStatus

    id = factory.LazyFunction(uuid4)
    chamado_id = factory.LazyFunction(uuid4)
    alterado_por_usuario_id = factory.LazyFunction(uuid4)
    status_anterior = ""
    status_novo = StatusChamado.ABERTO.value
    motivo = "Chamado criado"
    alterado_em = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    class Params:
        transicao = factory.Trait(
            status_anterior=StatusChamado.ABERTO.value,
            status_novo=StatusChamado.EM_ATENDIMENTO.value,
            motivo="Iniciando atendimento",
        )
