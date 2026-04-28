"""Authentication API endpoints."""

from flask import current_app, request, g
from flask_restx import Namespace, Resource, fields
from flask_login import login_user, logout_user, current_user

from src.application.dtos import LoginDTO, UsuarioCreateDTO
from src.application.use_cases import LoginUseCase, RegisterUseCase
from src.infrastructure import db, PasswordHasher, SQLAlchemyUnitOfWork
from src.infrastructure.persistence.sqlalchemy.repositories import UsuarioRepository
from src.infrastructure.security import TokenService
from src.domain.exceptions import DomainException
from src.presentation.api.api_auth import api_auth_required

auth_ns = Namespace('auth', description='Autenticação e registro de usuários')

login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='Email do usuário', example='usuario@empresa.com'),
    'senha': fields.String(required=True, description='Senha', example='minhasenha123'),
})

register_model = auth_ns.model('Register', {
    'nome': fields.String(required=True, description='Nome completo', example='João Silva'),
    'email': fields.String(required=True, description='Email', example='joao@empresa.com'),
    'senha': fields.String(required=True, description='Senha (mín. 6 caracteres)', example='minhasenha123'),
    'confirmar_senha': fields.String(required=True, description='Confirmação da senha', example='minhasenha123'),
})

user_response = auth_ns.model('UserResponse', {
    'id': fields.String(description='ID do usuário'),
    'nome': fields.String(description='Nome'),
    'email': fields.String(description='Email'),
    'perfil': fields.String(description='Perfil (solicitante, atendente, admin)'),
    'perfil_display': fields.String(description='Nome do perfil para exibição'),
    'ativo': fields.Boolean(description='Se está ativo'),
    'criado_em': fields.DateTime(description='Data de criação'),
})

login_response = auth_ns.model('LoginResponse', {
    'message': fields.String(description='Mensagem de sucesso'),
    'usuario': fields.Nested(user_response),
    'access_token': fields.String(description='JWT Bearer token para a API'),
})

error_response = auth_ns.model('ErrorResponse', {
    'error': fields.Nested(auth_ns.model('ErrorDetail', {
        'code': fields.String(description='Código do erro'),
        'message': fields.String(description='Mensagem do erro'),
    }))
})


@auth_ns.route('/login')
class LoginResource(Resource):
    """Login endpoint."""
    
    @auth_ns.doc('login')
    @auth_ns.expect(login_model)
    @auth_ns.response(200, 'Login bem-sucedido', login_response)
    @auth_ns.response(401, 'Credenciais inválidas', error_response)
    def post(self):
        """
        Autenticar usuário.
        
        Realiza login com email e senha.
        """
        data = request.json
        
        dto = LoginDTO(
            email=data.get('email', ''),
            senha=data.get('senha', ''),
        )
        
        hasher = PasswordHasher()
        repo = UsuarioRepository(db.session)
        
        use_case = LoginUseCase(
            usuario_repository=repo,
            password_hasher=hasher,
        )
        
        try:
            result = use_case.execute(dto)
            
            from src.infrastructure.persistence.sqlalchemy.models import UsuarioModel
            user_model = db.session.get(UsuarioModel, result.usuario.id)
            if user_model:
                login_user(user_model)

            token_service = TokenService(
                secret_key=current_app.config["JWT_SECRET_KEY"],
                exp_seconds=int(current_app.config.get("JWT_EXP_SECONDS", 3600)),
            )
            access_token = token_service.create_access_token(
                user_id=str(result.usuario.id),
                perfil=str(result.usuario.perfil),
            )
            
            return {
                'message': 'Login realizado com sucesso',
                'usuario': {
                    'id': str(result.usuario.id),
                    'nome': result.usuario.nome,
                    'email': result.usuario.email,
                    'perfil': result.usuario.perfil,
                    'perfil_display': result.usuario.perfil_display,
                    'ativo': result.usuario.ativo,
                    'criado_em': result.usuario.criado_em.isoformat(),
                },
                'access_token': access_token,
            }, 200
        except DomainException as e:
            return e.to_dict(), 401


@auth_ns.route('/register')
class RegisterResource(Resource):
    """Registration endpoint."""
    
    @auth_ns.doc('register')
    @auth_ns.expect(register_model)
    @auth_ns.response(201, 'Usuário criado', user_response)
    @auth_ns.response(400, 'Dados inválidos', error_response)
    def post(self):
        """
        Cadastrar novo usuário.
        
        Cria um novo usuário com perfil de Solicitante.
        """
        data = request.json
        
        dto = UsuarioCreateDTO(
            nome=data.get('nome', ''),
            email=data.get('email', ''),
            senha=data.get('senha', ''),
            confirmar_senha=data.get('confirmar_senha', ''),
        )
        
        hasher = PasswordHasher()
        uow = SQLAlchemyUnitOfWork(lambda: db.session)
        
        use_case = RegisterUseCase(
            usuario_repository=UsuarioRepository(db.session),
            unit_of_work=uow,
            password_hasher=hasher,
        )
        
        try:
            result = use_case.execute(dto)
            
            return {
                'id': str(result.id),
                'nome': result.nome,
                'email': result.email,
                'perfil': result.perfil,
                'perfil_display': result.perfil_display,
                'ativo': result.ativo,
                'criado_em': result.criado_em.isoformat(),
            }, 201
        except DomainException as e:
            return e.to_dict(), 400


@auth_ns.route('/logout')
class LogoutResource(Resource):
    """Logout endpoint."""
    
    @auth_ns.doc('logout', security='Bearer')
    @auth_ns.response(200, 'Logout realizado')
    @auth_ns.response(401, 'Não autenticado')
    @api_auth_required
    def post(self):
        """
        Realizar logout.
        
        Encerra a sessão do usuário atual.
        """
        # Se estiver autenticado por sessão, encerra a sessão.
        if current_user.is_authenticated:
            logout_user()
        return {"message": "Logout realizado com sucesso"}, 200


@auth_ns.route('/me')
class MeResource(Resource):
    """Current user endpoint."""
    
    @auth_ns.doc('me', security='Bearer')
    @auth_ns.response(200, 'Dados do usuário', user_response)
    @auth_ns.response(401, 'Não autenticado')
    @api_auth_required
    def get(self):
        """
        Obter dados do usuário atual.
        
        Retorna informações do usuário logado.
        """
        user = g.get("api_user") or current_user
        if not user or not getattr(user, "is_authenticated", False) and not getattr(user, "id", None):
            return {"error": {"code": "NOT_AUTHENTICATED", "message": "Não autenticado"}}, 401
        
        return {
            "id": str(user.id),
            "nome": user.nome,
            "email": user.email,
            "perfil": user.perfil,
            "perfil_display": user.perfil.title() if isinstance(user.perfil, str) else user.perfil,
            "ativo": user.ativo,
            "criado_em": user.criado_em.isoformat(),
        }, 200
