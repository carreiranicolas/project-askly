"""Flask Application Factory."""

import os
from pathlib import Path
from uuid import UUID

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config.settings import get_config
from config.env_validator import assert_required_env
from src.infrastructure.persistence.sqlalchemy.models import db, UsuarioModel


login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
talisman = Talisman()
# NOTE: Flask-Limiter 4.x expects configuration primarily in the constructor.
limiter = Limiter(key_func=get_remote_address)


def create_app(config_name: str | None = None) -> Flask:
    """
    Application factory pattern.
    
    Args:
        config_name: Configuration name (development, testing, production)
        
    Returns:
        Configured Flask application
    """
    # Frontend is kept separate from backend code (see /frontend).
    project_root = Path(__file__).resolve().parents[2]
    templates_dir = project_root / "frontend" / "templates"
    static_dir = project_root / "frontend" / "static"

    app = Flask(__name__, template_folder=str(templates_dir), static_folder=str(static_dir))
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    # Validate required env vars early (fail fast).
    # This runs after python-dotenv has loaded `.env` (see config/settings.py).
    assert_required_env()
    
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Security headers (anti-XSS) + CSP via Talisman
    csp = app.config.get("TALISMAN_CONTENT_SECURITY_POLICY")
    if csp:
        talisman.init_app(
            app,
            content_security_policy=csp,
            force_https=bool(app.config.get("TALISMAN_FORCE_HTTPS", False)),
            strict_transport_security=bool(app.config.get("TALISMAN_STRICT_TRANSPORT_SECURITY", False)),
        )

    # Rate limiting (Flask-Limiter 4.x)
    # Configure limits through attributes before init_app, to avoid incompatible kwargs.
    limiter._default_limits = [app.config.get("RATELIMIT_DEFAULT", "200 per day, 50 per hour")]
    limiter._storage_uri = app.config.get("RATELIMIT_STORAGE_URL", "memory://")
    limiter.enabled = bool(app.config.get("RATELIMIT_ENABLED", True))
    limiter.init_app(app)
    
    CORS(app, resources={
        r"/api/*": {
            "origins": [o.strip() for o in app.config.get("CORS_ORIGINS", "http://localhost:5000").split(",")],
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    login_manager.init_app(app)
    login_manager.login_view = 'web_auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id: str) -> UsuarioModel | None:
        try:
            return db.session.get(UsuarioModel, UUID(user_id))
        except (ValueError, TypeError):
            return None
    
    register_blueprints(app)
    register_api(app)
    register_error_handlers(app)
    register_context_processors(app)
    register_cli_commands(app)
    
    return app


def register_blueprints(app: Flask) -> None:
    """Register web blueprints."""
    from src.presentation.web.blueprints.auth import auth_bp
    from src.presentation.web.blueprints.tickets import tickets_bp
    from src.presentation.web.blueprints.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(tickets_bp, url_prefix='/chamados')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    @app.route('/')
    def index():
        from flask import redirect, url_for
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(url_for('web_tickets.listar'))
        return redirect(url_for('web_auth.login'))


def register_api(app: Flask) -> None:
    """Register REST API with Swagger."""
    from src.presentation.api import api_bp, api
    
    csrf.exempt(api_bp)
    # API endpoints should not be forced to use CSRF (use Bearer JWT or session).
    
    app.register_blueprint(api_bp, url_prefix='/api')


def register_error_handlers(app: Flask) -> None:
    """Register error handlers."""
    from flask import render_template, jsonify, request
    from src.domain.exceptions import (
        DomainException,
        EntityNotFoundException,
        ValidationException,
        AuthorizationException,
    )
    
    def is_api_request():
        return request.path.startswith('/api/')
    
    @app.errorhandler(400)
    def bad_request(error):
        if is_api_request():
            return jsonify({"error": {"code": "BAD_REQUEST", "message": str(error)}}), 400
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        if is_api_request():
            return jsonify({"error": {"code": "UNAUTHORIZED", "message": "Autenticação necessária"}}), 401
        return render_template('errors/401.html'), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        if is_api_request():
            return jsonify({"error": {"code": "FORBIDDEN", "message": "Acesso negado"}}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        if is_api_request():
            return jsonify({"error": {"code": "NOT_FOUND", "message": "Recurso não encontrado"}}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if is_api_request():
            return jsonify({"error": {"code": "INTERNAL_ERROR", "message": "Erro interno do servidor"}}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(DomainException)
    def handle_domain_exception(error: DomainException):
        status_code = 400
        if isinstance(error, EntityNotFoundException):
            status_code = 404
        elif isinstance(error, AuthorizationException):
            status_code = 403
        
        if is_api_request():
            return jsonify(error.to_dict()), status_code
        
        from flask import flash, redirect, request
        flash(error.message, 'danger')
        return redirect(request.referrer or '/')


def register_context_processors(app: Flask) -> None:
    """Register template context processors."""
    from src.domain.enums import StatusChamado, Prioridade, PerfilUsuario
    from src import __version__ as askly_version
    
    @app.context_processor
    def inject_enums():
        return {
            'StatusChamado': StatusChamado,
            'Prioridade': Prioridade,
            'PerfilUsuario': PerfilUsuario,
            'STATUS_COLORS': app.config.get('STATUS_COLORS', {}),
            'ASKLY_VERSION': askly_version,
        }


def register_cli_commands(app: Flask) -> None:
    """Register CLI commands."""
    import click
    
    @app.cli.command('seed')
    def seed_command():
        """Seed the database with initial data."""
        from src.infrastructure.security import PasswordHasher
        from src.infrastructure.persistence.sqlalchemy.models import (
            UsuarioModel, CategoriaModel
        )
        
        hasher = PasswordHasher()
        
        if not UsuarioModel.query.filter_by(email='admin@askly.com').first():
            admin_password = os.environ.get('ADMIN_SEED_PASSWORD')
            if not admin_password:
                import secrets
                admin_password = secrets.token_urlsafe(16)
                click.echo(f'Generated admin password: {admin_password}')
                click.echo('Set ADMIN_SEED_PASSWORD env var to use a fixed password.')
            
            admin = UsuarioModel(
                nome='Administrador',
                email='admin@askly.com',
                senha_hash=hasher.hash(admin_password),
                perfil='admin',
                ativo=True,
            )
            db.session.add(admin)
            click.echo('Admin user created: admin@askly.com')
        
        categorias = ['TI - Infraestrutura', 'TI - Software', 'RH', 'Financeiro', 'Facilities']
        for nome in categorias:
            if not CategoriaModel.query.filter_by(nome=nome).first():
                cat = CategoriaModel(nome=nome, ativa=True)
                db.session.add(cat)
                click.echo(f'Category created: {nome}')
        
        db.session.commit()
        click.echo('Database seeded successfully!')
