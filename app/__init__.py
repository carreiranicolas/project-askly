import os

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from .models import db

csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "dev-only-change-me"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///askly.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    csrf.init_app(app)

    db.init_app(app)

    from .routes.main import main_bp, web_auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(web_auth_bp)

    @app.context_processor
    def inject_askly_version():
        return {"ASKLY_VERSION": "0.1.0"}

    return app