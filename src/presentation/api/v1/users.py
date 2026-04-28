"""Users API endpoints."""

from uuid import UUID

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_login import current_user

from src.application.use_cases import ListUsersUseCase, ChangeProfileUseCase
from src.infrastructure import db, SQLAlchemyUnitOfWork
from src.domain.enums import PerfilUsuario
from src.domain.exceptions import DomainException
from src.presentation.api.api_auth import api_auth_required

users_ns = Namespace('usuarios', description='Gestão de usuários (admin)')

user_response = users_ns.model('UserResponse', {
    'id': fields.String(),
    'nome': fields.String(),
    'email': fields.String(),
    'perfil': fields.String(),
    'perfil_display': fields.String(),
    'ativo': fields.Boolean(),
    'criado_em': fields.DateTime(),
})

change_profile_model = users_ns.model('ChangeProfile', {
    'perfil': fields.String(required=True, description='Novo perfil', 
                           enum=['solicitante', 'atendente', 'admin']),
})


def get_current_user_entity():
    """Convert Flask-Login user to domain entity."""
    from src.domain.entities import Usuario
    
    if not current_user.is_authenticated:
        return None
    
    return Usuario(
        id=current_user.id,
        nome=current_user.nome,
        email=current_user.email,
        perfil=PerfilUsuario(current_user.perfil) if isinstance(current_user.perfil, str) else current_user.perfil,
        ativo=current_user.ativo,
        criado_em=current_user.criado_em,
    )


@users_ns.route('')
class UserListResource(Resource):
    """User list (admin only)."""
    
    @users_ns.doc('list_users', security='Bearer')
    @users_ns.param('page', 'Página', type=int, default=1)
    @users_ns.param('per_page', 'Itens por página', type=int, default=10)
    @users_ns.param('perfil', 'Filtrar por perfil')
    @users_ns.response(200, 'Lista de usuários')
    @users_ns.response(403, 'Não autorizado')
    @api_auth_required
    def get(self):
        """
        Listar usuários.
        
        Apenas administradores podem listar usuários.
        """
        user = get_current_user_entity()
        
        perfil_str = request.args.get('perfil')
        perfil = PerfilUsuario(perfil_str) if perfil_str else None
        
        uow = SQLAlchemyUnitOfWork(lambda: db.session)
        use_case = ListUsersUseCase(unit_of_work=uow)
        
        try:
            result = use_case.execute(
                usuario=user,
                page=request.args.get('page', 1, type=int),
                per_page=request.args.get('per_page', 10, type=int),
                perfil=perfil,
            )
            
            return {
                'items': [
                    {
                        'id': str(u.id),
                        'nome': u.nome,
                        'email': u.email,
                        'perfil': u.perfil,
                        'perfil_display': u.perfil_display,
                        'ativo': u.ativo,
                        'criado_em': u.criado_em.isoformat(),
                    }
                    for u in result.items
                ],
                'pagination': {
                    'page': result.page,
                    'per_page': result.per_page,
                    'total': result.total,
                    'pages': result.pages,
                }
            }, 200
        except DomainException as e:
            return e.to_dict(), 403


@users_ns.route('/<string:id>/perfil')
class UserProfileResource(Resource):
    """User profile management."""
    
    @users_ns.doc('change_profile', security='Bearer')
    @users_ns.expect(change_profile_model)
    @users_ns.response(200, 'Perfil alterado', user_response)
    @users_ns.response(403, 'Não autorizado')
    @api_auth_required
    def put(self, id: str):
        """
        Alterar perfil de usuário.
        
        Apenas administradores podem alterar perfis.
        """
        admin = get_current_user_entity()
        data = request.json
        
        uow = SQLAlchemyUnitOfWork(lambda: db.session)
        use_case = ChangeProfileUseCase(unit_of_work=uow)
        
        try:
            result = use_case.execute(
                usuario_id=UUID(id),
                novo_perfil=PerfilUsuario(data.get('perfil')),
                admin=admin,
            )
            
            return {
                'id': str(result.id),
                'nome': result.nome,
                'email': result.email,
                'perfil': result.perfil,
                'perfil_display': result.perfil_display,
                'ativo': result.ativo,
                'criado_em': result.criado_em.isoformat(),
            }, 200
        except DomainException as e:
            return e.to_dict(), 403
