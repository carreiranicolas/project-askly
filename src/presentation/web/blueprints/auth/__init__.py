"""Auth blueprint."""

from flask import Blueprint

auth_bp = Blueprint('web_auth', __name__)

from src.presentation.web.blueprints.auth import routes  # noqa
