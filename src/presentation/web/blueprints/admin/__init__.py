"""Admin blueprint."""

from flask import Blueprint

admin_bp = Blueprint('web_admin', __name__)

from src.presentation.web.blueprints.admin import routes  # noqa
