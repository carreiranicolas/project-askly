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


def test_admin_change_status_records_history(client, make_user, api_login, catalog):
    sol_email, _ = make_user(role="Solicitante", email="sol@test.com")
    adm_email, _ = make_user(role="Admin", email="adm@test.com")
    sol_headers = api_login(sol_email)
    adm_headers = api_login(adm_email)

    tid = _create_ticket(client, sol_headers, catalog).get_json()["id"]
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


def test_status_change_records_motivo(client, make_user, api_login, catalog):
    sol_email, _ = make_user(role="Solicitante", email="sol@test.com")
    adm_email, _ = make_user(role="Admin", email="adm@test.com")
    tid = _create_ticket(client, api_login(sol_email), catalog).get_json()["id"]

    resp = client.post(
        f"/api/v1/chamados/{tid}/status",
        json={"status": "EM_ATENDIMENTO", "motivo": "Iniciando atendimento"},
        headers=api_login(adm_email),
    )
    assert resp.status_code == 200
    hist = client.get(
        f"/api/v1/chamados/{tid}/historico", headers=api_login(adm_email)
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
