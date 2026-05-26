import os

from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from .models import db

csrf = CSRFProtect()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "dev-only-change-me"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///askly.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    csrf.init_app(app)

    db.init_app(app)


    login_manager.init_app(app)
    # Define a rota para onde o usuário será jogado se tentar acessar algo restrito sem login
    login_manager.login_view = "web_auth.login"
    login_manager.login_message = "Por favor, faça o login para acessar esta página."
    login_manager.login_message_category = "warning"

    # Importa o modelo User para que o login_manager consiga usá-lo no loader
    # (Ajuste o caminho do import caso o seu modelo de usuário esteja em outro arquivo dentro de models)
    from .models.user import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    # -------------------------------------    

    from .routes.main import main_bp, web_auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(web_auth_bp)

    @app.context_processor
    def inject_askly_version():
        return {"ASKLY_VERSION": "0.1.0"}

    return app