def _create_ticket(client, headers, catalog):
    return client.post(
        "/api/v1/chamados",
        json={
            "title": "Erro no ERP",
            "description": "erro 500",
            "category_id": catalog["categoria"],
            "priority_id": catalog["prioridade"],
        },
        headers=headers,
    )


def _user_id(app, email):
    from app.models.user import Usuario

    with app.app_context():
        return Usuario.query.filter_by(email=email).first().id


def test_create_ticket_starts_aberto(client, make_user, api_login, catalog):
    email, _ = make_user(role="Solicitante", email="sol@test.com")
    resp = _create_ticket(client, api_login(email), catalog)
    assert resp.status_code == 201
    assert resp.get_json()["status"] == "Aberto"


def test_solicitante_cannot_change_status(client, make_user, api_login, catalog):
    email, _ = make_user(role="Solicitante", email="sol@test.com")
    headers = api_login(email)
    tid = _create_ticket(client, headers, catalog).get_json()["id"]
    resp = client.post(
        f"/api/v1/chamados/{tid}/status",
        json={"status": "EM_ATENDIMENTO"},
        headers=headers,
    )
    assert resp.status_code == 403


def test_admin_change_status_records_history(app, client, make_user, api_login, catalog):
    sol_email, _ = make_user(role="Solicitante", email="sol@test.com")
    adm_email, _ = make_user(role="Admin", email="adm@test.com")
    # catalog["categoria"] é "Infraestrutura" (1ª em ordem alfabética no seed).
    tec_email, _ = make_user(
        role="Atendente", email="tec@test.com", area="Infraestrutura"
    )
    adm_headers = api_login(adm_email)

    tid = _create_ticket(client, api_login(sol_email), catalog).get_json()["id"]

    # Sem responsável atribuído, a mudança de status é bloqueada.
    assert client.post(
        f"/api/v1/chamados/{tid}/status",
        json={"status": "EM_ATENDIMENTO"},
        headers=adm_headers,
    ).status_code == 400

    client.post(
        f"/api/v1/chamados/{tid}/atribuir",
        json={"assignee_id": _user_id(app, tec_email)},
        headers=adm_headers,
    )

    resp = client.post(
        f"/api/v1/chamados/{tid}/status",
        json={"status": "EM_ATENDIMENTO"},
        headers=adm_headers,
    )
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "Em Atendimento"

    history = client.get(
        f"/api/v1/chamados/{tid}/historico", headers=adm_headers
    ).get_json()
    assert len(history) == 1
    assert history[0]["previous_status"] == "Aberto"
    assert history[0]["new_status"] == "Em Atendimento"


def test_atendente_sees_only_own_area(client, make_user, api_login, areas):
    sol_email, _ = make_user(role="Solicitante", email="sol@test.com", area="RH")
    rh_email, _ = make_user(role="Atendente", email="rh@test.com", area="RH")
    infra_email, _ = make_user(
        role="Atendente", email="infra@test.com", area="Infraestrutura"
    )

    # Solicitante abre um chamado na área RH.
    pid = client.get("/api/v1/prioridades", headers=api_login(rh_email)).get_json()[0][
        "id"
    ]
    client.post(
        "/api/v1/chamados",
        json={
            "title": "Folha de pagamento",
            "description": "duvida",
            "category_id": areas["RH"],
            "priority_id": pid,
        },
        headers=api_login(sol_email),
    )

    # Atendente de RH enxerga; atendente de Infraestrutura não.
    assert len(client.get("/api/v1/chamados", headers=api_login(rh_email)).get_json()) == 1
    assert client.get("/api/v1/chamados", headers=api_login(infra_email)).get_json() == []


def test_status_change_records_motivo(app, client, make_user, api_login, catalog):
    sol_email, _ = make_user(role="Solicitante", email="sol@test.com")
    adm_email, _ = make_user(role="Admin", email="adm@test.com")
    tec_email, _ = make_user(
        role="Atendente", email="tec@test.com", area="Infraestrutura"
    )
    adm_headers = api_login(adm_email)
    tid = _create_ticket(client, api_login(sol_email), catalog).get_json()["id"]
    client.post(
        f"/api/v1/chamados/{tid}/atribuir",
        json={"assignee_id": _user_id(app, tec_email)},
        headers=adm_headers,
    )

    resp = client.post(
        f"/api/v1/chamados/{tid}/status",
        json={"status": "EM_ATENDIMENTO", "motivo": "Iniciando atendimento"},
        headers=adm_headers,
    )
    assert resp.status_code == 200
    hist = client.get(
        f"/api/v1/chamados/{tid}/historico", headers=adm_headers
    ).get_json()
    assert hist[0]["motivo"] == "Iniciando atendimento"


def test_invalid_transition_rejected(client, make_user, api_login, catalog):
    sol_email, _ = make_user(role="Solicitante", email="sol@test.com")
    adm_email, _ = make_user(role="Admin", email="adm@test.com")
    adm_headers = api_login(adm_email)
    tid = _create_ticket(client, api_login(sol_email), catalog).get_json()["id"]

    # ABERTO -> CANCELADO é válido
    assert client.post(
        f"/api/v1/chamados/{tid}/status",
        json={"status": "CANCELADO"},
        headers=adm_headers,
    ).status_code == 200
    # CANCELADO é terminal: qualquer transição é inválida
    assert client.post(
        f"/api/v1/chamados/{tid}/status",
        json={"status": "EM_ATENDIMENTO"},
        headers=adm_headers,
    ).status_code == 400


def _open_ticket_in(client, headers, area_id, priority_id):
    return client.post(
        "/api/v1/chamados",
        json={
            "title": "Chamado",
            "description": "x",
            "category_id": area_id,
            "priority_id": priority_id,
        },
        headers=headers,
    ).get_json()["id"]


def test_assign_only_to_same_area(app, client, make_user, api_login, areas):
    sol_email, _ = make_user(role="Solicitante", email="sol@test.com", area="RH")
    adm_email, _ = make_user(role="Admin", email="adm@test.com")
    rh_email, _ = make_user(role="Atendente", email="rh@test.com", area="RH")
    infra_email, _ = make_user(
        role="Atendente", email="infra@test.com", area="Infraestrutura"
    )
    adm_headers = api_login(adm_email)

    pid = client.get("/api/v1/prioridades", headers=adm_headers).get_json()[0]["id"]
    tid = _open_ticket_in(client, api_login(sol_email), areas["RH"], pid)

    # Atendente de outra área não pode ser responsável.
    assert client.post(
        f"/api/v1/chamados/{tid}/atribuir",
        json={"assignee_id": _user_id(app, infra_email)},
        headers=adm_headers,
    ).status_code == 400
    # Atendente da área do chamado pode.
    assert client.post(
        f"/api/v1/chamados/{tid}/atribuir",
        json={"assignee_id": _user_id(app, rh_email)},
        headers=adm_headers,
    ).status_code == 200


def test_approval_closes_ticket(app, client, make_user, api_login, areas):
    sol_email, _ = make_user(role="Solicitante", email="sol@test.com", area="RH")
    adm_email, _ = make_user(role="Admin", email="adm@test.com")
    rh_email, _ = make_user(role="Atendente", email="rh@test.com", area="RH")
    adm_headers = api_login(adm_email)
    sol_headers = api_login(sol_email)

    pid = client.get("/api/v1/prioridades", headers=adm_headers).get_json()[0]["id"]
    tid = _open_ticket_in(client, sol_headers, areas["RH"], pid)

    client.post(
        f"/api/v1/chamados/{tid}/atribuir",
        json={"assignee_id": _user_id(app, rh_email)},
        headers=adm_headers,
    )
    # Técnico conclui o atendimento: vai para "Aguardando Aprovação".
    resp = client.post(
        f"/api/v1/chamados/{tid}/status",
        json={"status": "AGUARDANDO_APROVACAO"},
        headers=adm_headers,
    )
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "Aguardando Aprovação"

    # Quem não abriu o chamado não pode aprovar.
    assert client.post(
        f"/api/v1/chamados/{tid}/aprovar", headers=adm_headers
    ).status_code == 403
    # Quem abriu aprova: o chamado fecha automaticamente.
    resp = client.post(f"/api/v1/chamados/{tid}/aprovar", headers=sol_headers)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "Fechado"


def test_rejection_reopens_ticket(app, client, make_user, api_login, areas):
    sol_email, _ = make_user(role="Solicitante", email="sol@test.com", area="RH")
    adm_email, _ = make_user(role="Admin", email="adm@test.com")
    rh_email, _ = make_user(role="Atendente", email="rh@test.com", area="RH")
    adm_headers = api_login(adm_email)
    sol_headers = api_login(sol_email)

    pid = client.get("/api/v1/prioridades", headers=adm_headers).get_json()[0]["id"]
    tid = _open_ticket_in(client, sol_headers, areas["RH"], pid)
    client.post(
        f"/api/v1/chamados/{tid}/atribuir",
        json={"assignee_id": _user_id(app, rh_email)},
        headers=adm_headers,
    )
    client.post(
        f"/api/v1/chamados/{tid}/status",
        json={"status": "AGUARDANDO_APROVACAO"},
        headers=adm_headers,
    )

    # Quem não abriu não pode recusar.
    assert client.post(
        f"/api/v1/chamados/{tid}/recusar", headers=adm_headers
    ).status_code == 403
    # Quem abriu recusa: o chamado reabre (volta para "Aberto").
    resp = client.post(f"/api/v1/chamados/{tid}/recusar", headers=sol_headers)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "Aberto"


def test_meus_lists_opened_tickets_in_any_area(client, make_user, api_login, areas):
    """Chamados que abri (tipo=meus) inclui chamados direcionados a outra área."""
    sol_email, _ = make_user(role="Solicitante", email="sol-outra@test.com", area="RH")
    tec_email, _ = make_user(
        role="Atendente", email="tec-outra@test.com", area="RH"
    )
    sol_headers = api_login(sol_email)
    tec_headers = api_login(tec_email)
    pid = client.get("/api/v1/prioridades", headers=sol_headers).get_json()[0]["id"]

    # Solicitante abre chamado na área Infraestrutura (área do cadastro é RH).
    client.post(
        "/api/v1/chamados",
        json={
            "title": "VPN corporativa",
            "description": "Preciso de acesso",
            "category_id": areas["Infraestrutura"],
            "priority_id": pid,
        },
        headers=sol_headers,
    )
    meus_sol = client.get(
        "/api/v1/chamados", headers=sol_headers, query_string={"tipo": "meus"}
    ).get_json()
    assert len(meus_sol) == 1
    assert meus_sol[0]["category_id"] == areas["Infraestrutura"]

    # Atendente de RH abre chamado em RH — aparece em meus.
    client.post(
        "/api/v1/chamados",
        json={
            "title": "Folha de pagamento",
            "description": "Dúvida",
            "category_id": areas["RH"],
            "priority_id": pid,
        },
        headers=tec_headers,
    )
    meus_tec = client.get(
        "/api/v1/chamados", headers=tec_headers, query_string={"tipo": "meus"}
    ).get_json()
    assert len(meus_tec) == 1

    # Na fila da área (sem tipo), o atendente de RH não vê o próprio chamado
    # aberto em Infraestrutura — só o que está na área dele.
    client.post(
        "/api/v1/chamados",
        json={
            "title": "Servidor fora",
            "description": "Queda",
            "category_id": areas["Infraestrutura"],
            "priority_id": pid,
        },
        headers=tec_headers,
    )
    fila_rh = client.get("/api/v1/chamados", headers=tec_headers).get_json()
    assert all(c["category_id"] == areas["RH"] for c in fila_rh)


def test_solicitante_sees_only_own_tickets(client, make_user, api_login, catalog):
    a_email, _ = make_user(role="Solicitante", email="a@test.com")
    b_email, _ = make_user(role="Solicitante", email="b@test.com")
    a_headers = api_login(a_email)
    b_headers = api_login(b_email)

    tid = _create_ticket(client, a_headers, catalog).get_json()["id"]

    # B não enxerga e não acessa o chamado de A
    assert client.get("/api/v1/chamados", headers=b_headers).get_json() == []
    assert client.get(f"/api/v1/chamados/{tid}", headers=b_headers).status_code == 403
    # A enxerga o próprio
    assert len(client.get("/api/v1/chamados", headers=a_headers).get_json()) == 1
