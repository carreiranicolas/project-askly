import os
import sys

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate, upgrade
from flask_wtf.csrf import CSRFProtect

from .models import db

load_dotenv()

csrf = CSRFProtect()
login_manager = LoginManager()
migrate = Migrate()


def _database_uri():
    uri = os.environ.get("DATABASE_URL")
    if uri:
        return uri

    user = os.environ.get("POSTGRES_USER", "askly")
    password = os.environ.get("POSTGRES_PASSWORD", "askly_dev_password")
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    name = os.environ.get("POSTGRES_DB", "askly_db")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"


def _running_dev_server():
    # Aplica as migrations só quando o servidor sobe (flask run / python run.py),
    # nunca durante comandos `flask db ...` ou os testes.
    if "run" not in sys.argv and os.path.basename(sys.argv[0]) != "run.py":
        return False
    # Com o reloader ativo, evita rodar no processo monitor (só no worker).
    debug = os.environ.get("FLASK_DEBUG", "") in ("1", "true", "True")
    if debug and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        return False
    return True


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = _database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    # Define a rota para onde o usuário será jogado se tentar acessar algo restrito sem login
    login_manager.login_view = "web_auth.login"
    login_manager.login_message = "Por favor, faça o login para acessar esta página."
    login_manager.login_message_category = "warning"

    # Importa o modelo User para que o login_manager consiga usá-lo no loader
    from .models.user import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    from .routes.main import main_bp, web_auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(web_auth_bp)

    @app.context_processor
    def inject_askly_version():
        return {"ASKLY_VERSION": "0.1.0"}

    if _running_dev_server():
        with app.app_context():
            upgrade()

    return app
