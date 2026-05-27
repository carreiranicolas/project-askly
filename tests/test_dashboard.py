def test_dashboard_requires_login(client):
    assert client.get("/dashboard/").status_code == 302


def test_dashboard_ok_for_logged_user(client, make_user):
    email, password = make_user(role="Admin", email="adm@test.com")
    client.post("/login", data={"email": email, "password": password})
    resp = client.get("/dashboard/")
    assert resp.status_code == 200
    assert "Dashboard" in resp.get_data(as_text=True)


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
