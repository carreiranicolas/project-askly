"""
Presentation Layer - Interface com o mundo externo.

Esta camada contém:
- API: REST endpoints com documentação Swagger
- Web: Blueprints Flask com templates Jinja2
- Middlewares: CORS, rate limiting, error handlers

REGRAS:
- Depende das camadas Application e Infrastructure
- Não contém lógica de negócio
- Responsável por serialização/deserialização
"""
