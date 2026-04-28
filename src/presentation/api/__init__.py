"""REST API with Swagger documentation."""

from flask import Blueprint
from flask_restx import Api

api_bp = Blueprint('api', __name__)

api = Api(
    api_bp,
    version='1.0',
    title='Askly API',
    description='''
## API de Gestão de Chamados Internos

API RESTful para o sistema Askly - Plataforma de gestão de chamados internos.

### Autenticação
A API utiliza autenticação via JWT Bearer Token. 
Inclua o token no header `Authorization: Bearer <token>`.

### Perfis de Usuário
- **Solicitante**: Cria e acompanha seus chamados
- **Atendente**: Gerencia fila de atendimento
- **Admin**: Acesso completo ao sistema

### Status do Chamado
| Status | Descrição | Cor |
|--------|-----------|-----|
| ABERTO | Chamado aguardando atendimento | Azul claro |
| EM_ATENDIMENTO | Em análise pelo atendente | Azul |
| AGUARDANDO_RETORNO | Aguardando resposta do solicitante | Verde |
| RESOLVIDO | Problema resolvido, aguardando confirmação | Amarelo |
| FECHADO | Chamado encerrado | Vermelho |
    ''',
    doc='/docs',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Authorization header. Example: "Bearer {token}"'
        }
    },
    security='Bearer',
)

from src.presentation.api.v1 import auth_ns, tickets_ns, categories_ns, users_ns

api.add_namespace(auth_ns, path='/v1/auth')
api.add_namespace(tickets_ns, path='/v1/chamados')
api.add_namespace(categories_ns, path='/v1/categorias')
api.add_namespace(users_ns, path='/v1/usuarios')
