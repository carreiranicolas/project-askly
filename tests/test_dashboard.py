def test_dashboard_requires_login(client):
    assert client.get("/dashboard/").status_code == 302


def test_dashboard_metrics_scoped_by_area(app, make_user, areas):
    """Admin vê todos os chamados; o técnico (Atendente) só os da própria área."""
    from app.models.priority import Prioridade
    from app.models.user import Usuario
    from app.services import ticket_service

    sol_email, _ = make_user(role="Solicitante", email="sol-dash@test.com", area="RH")
    rh_email, _ = make_user(role="Atendente", email="rh-dash@test.com", area="RH")
    adm_email, _ = make_user(role="Admin", email="adm-dash@test.com")

    with app.app_context():
        sol = Usuario.query.filter_by(email=sol_email).first()
        rh = Usuario.query.filter_by(email=rh_email).first()
        adm = Usuario.query.filter_by(email=adm_email).first()
        pid = Prioridade.query.first().id

        ticket_service.create_ticket(
            sol, title="RH", description="x", category_id=areas["RH"], priority_id=pid
        )
        ticket_service.create_ticket(
            sol,
            title="Infra",
            description="x",
            category_id=areas["Infraestrutura"],
            priority_id=pid,
        )

        # Atendente de RH só conta o chamado da própria área.
        assert ticket_service.dashboard_metrics(rh)["total"] == 1
        # Admin contabiliza todos.
        assert ticket_service.dashboard_metrics(adm)["total"] == 2


def test_dashboard_em_aberto_counts_active_states(app, make_user, areas):
    """'Em aberto' = qualquer status ativo (não só ABERTO)."""
    from app.models.priority import Prioridade
    from app.models.user import Usuario
    from app.services import ticket_service

    sol_email, _ = make_user(role="Solicitante", email="sol-ab@test.com", area="RH")
    rh_email, _ = make_user(role="Atendente", email="rh-ab@test.com", area="RH")
    adm_email, _ = make_user(role="Admin", email="adm-ab@test.com")

    with app.app_context():
        sol = Usuario.query.filter_by(email=sol_email).first()
        rh = Usuario.query.filter_by(email=rh_email).first()
        adm = Usuario.query.filter_by(email=adm_email).first()
        pid = Prioridade.query.first().id

        t = ticket_service.create_ticket(
            sol,
            title="Chamado teste",
            description="Descrição do chamado.",
            category_id=areas["RH"],
            priority_id=pid,
        )
        ticket_service.assign_ticket(adm, t.id, rh.id)
        ticket_service.change_status(rh, t.id, "EM_ATENDIMENTO")

        m = ticket_service.dashboard_metrics(adm)
        assert m["abertos"] == 1  # "Em Atendimento" conta como em aberto

        ticket_service.change_status(rh, t.id, "AGUARDANDO_APROVACAO")
        m = ticket_service.dashboard_metrics(adm)
        assert m["abertos"] == 0
        assert m["aguardando_aprovacao"] == 1


def test_fresh_ticket_is_not_overdue(app, make_user, areas):
    """Regressão: chamado recém-aberto não pode constar como atrasado
    (created_at é gravado em UTC consciente, evitando o deslocamento de fuso)."""
    from datetime import datetime, timedelta, timezone

    from app.extensions import db
    from app.models.priority import Prioridade
    from app.models.ticket import Chamado
    from app.models.user import Usuario
    from app.services import ticket_service

    sol_email, _ = make_user(role="Solicitante", email="sol-sla@test.com", area="RH")
    with app.app_context():
        sol = Usuario.query.filter_by(email=sol_email).first()
        # SLA curto (1h) — pior caso para o bug de fuso.
        p = Prioridade(name="Imediata", description="x", sla_hours=1, is_active=True)
        db.session.add(p)
        db.session.commit()

        t = ticket_service.create_ticket(
            sol, title="novo", description="x", category_id=areas["RH"], priority_id=p.id
        )
        assert ticket_service.is_overdue(db.session.get(Chamado, t.id)) is False

        # Forçar criação bem no passado deve, sim, marcar como atrasado.
        old = db.session.get(Chamado, t.id)
        old.created_at = datetime.now(timezone.utc) - timedelta(hours=5)
        db.session.commit()
        assert ticket_service.is_overdue(db.session.get(Chamado, t.id)) is True


def test_sla_report_has_expected_shape(app, make_user):
    from app.models.user import Usuario
    from app.services import ticket_service

    adm_email, _ = make_user(role="Admin", email="adm-sla@test.com")
    with app.app_context():
        adm = Usuario.query.filter_by(email=adm_email).first()
        report = ticket_service.sla_report(adm)
        assert "ativos" in report
        assert "por_area" in report


def test_dashboard_ok_for_logged_user(client, make_user):
    email, password = make_user(role="Admin", email="adm@test.com")
    client.post("/login", data={"email": email, "password": password})
    resp = client.get("/dashboard/")
    assert resp.status_code == 200
    assert "Dashboard" in resp.get_data(as_text=True)


def test_sla_page_requires_admin(client, make_user):
    """SLA & Métricas é restrito a administradores."""
    adm_email, adm_pass = make_user(role="Admin", email="adm-sla-page@test.com")
    sol_email, sol_pass = make_user(role="Solicitante", email="sol-sla-page@test.com")

    client.post("/login", data={"email": sol_email, "password": sol_pass})
    assert client.get("/dashboard/sla").status_code == 403

    client.post("/login", data={"email": adm_email, "password": adm_pass})
    assert client.get("/dashboard/sla").status_code == 200


def test_web_search_filters(client, make_user, api_login, catalog):
    email, password = make_user(role="Solicitante", email="sol@test.com")
    headers = api_login(email)
    for title in ("Impressora quebrada", "Acesso VPN"):
        client.post(
            "/api/v1/chamados",
            json={
                "title": title,
                "description": "x",
                "category_id": catalog["categoria"],
                "priority_id": catalog["prioridade"],
            },
            headers=headers,
        )
    client.post("/login", data={"email": email, "password": password})
    body = client.get("/chamados/?q=Impressora").get_data(as_text=True)
    assert "Impressora quebrada" in body
    assert "Acesso VPN" not in body
