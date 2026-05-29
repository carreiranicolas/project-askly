import click

from .models import db
from .models.category import Categoria
from .models.priority import Prioridade
from .models.role import Cargo

CARGOS = [
    ("Solicitante", "Abre e acompanha os próprios chamados."),
    ("Atendente", "Atende e resolve chamados atribuídos."),
    ("Admin", "Administra usuários, categorias e o sistema."),
]

# Áreas responsáveis pelos chamados (entidade Categoria reaproveitada como Área).
AREAS = [
    ("RH", "Recursos Humanos: pessoas, folha e benefícios."),
    ("Financeiro", "Pagamentos, faturamento e contas."),
    ("Comercial", "Vendas, propostas e relacionamento com clientes."),
    ("Jurídico", "Contratos, compliance e questões legais."),
    ("Desenvolvimento", "Software, sistemas internos e integrações."),
    ("Infraestrutura", "Servidores, rede, equipamentos e ambiente."),
]

PRIORIDADES = [
    ("Baixa", "Sem impacto imediato.", 72),
    ("Média", "Impacto moderado no trabalho.", 24),
    ("Alta", "Impacto relevante, requer atenção.", 8),
    ("Crítica", "Parada total, exige ação imediata.", 2),
]


def register_commands(app):
    @app.cli.command("seed")
    def seed():
        """Popula dados base: cargos, categorias e prioridades (idempotente)."""
        created = 0

        for name, description in CARGOS:
            if not Cargo.query.filter_by(name=name).first():
                db.session.add(Cargo(name=name, description=description, is_active=True))
                created += 1

        for name, description in AREAS:
            if not Categoria.query.filter_by(name=name).first():
                db.session.add(Categoria(name=name, description=description, is_active=True))
                created += 1

        for name, description, sla_hours in PRIORIDADES:
            if not Prioridade.query.filter_by(name=name).first():
                db.session.add(
                    Prioridade(
                        name=name,
                        description=description,
                        sla_hours=sla_hours,
                        is_active=True,
                    )
                )
                created += 1

        db.session.commit()
        click.echo(f"Seed concluído. {created} novo(s) registro(s) inserido(s).")
