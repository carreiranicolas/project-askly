"""Tickets blueprint."""

from flask import Blueprint

tickets_bp = Blueprint("web_tickets", __name__)

from src.presentation.web.blueprints.tickets import routes  # noqa
