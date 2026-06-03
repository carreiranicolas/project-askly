from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.routes.decorators import admin_required
from app.services import ROLE_ATENDENTE, role_of, ticket_service

web_dashboard_bp = Blueprint("web_dashboard", __name__, url_prefix="/dashboard")


@web_dashboard_bp.route("/")
@login_required
def index():
    metrics = ticket_service.dashboard_metrics(current_user)
    user_role = role_of(current_user)
    # Atendente só enxerga uma área — o card "Por área" é redundante.
    show_por_area = user_role != ROLE_ATENDENTE
    return render_template(
        "dashboard/index.html",
        metrics=metrics,
        show_por_area=show_por_area,
    )


@web_dashboard_bp.route("/sla")
@admin_required
def sla():
    return render_template(
        "dashboard/sla.html",
        report=ticket_service.sla_report(current_user),
    )
