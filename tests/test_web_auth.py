def test_cadastro_auto_login(client, cargo_ids, areas):
    resp = client.post(
        "/cadastro",
        data={
            "name": "Joao Web",
            "email": "joao@test.com",
            "password": "senha123",
            "confirm_password": "senha123",
            "role": str(cargo_ids["Solicitante"]),
            "area": str(areas["RH"]),
        },
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/"
    # Já autenticado: home redireciona para a lista de chamados.
    home = client.get("/")
    assert home.status_code == 302
    assert "/chamados" in home.headers["Location"]


def test_login_logout_flow(client, make_user):
    email, password = make_user(role="Solicitante", email="web@test.com")
    resp = client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    # Logout é POST-only.
    assert client.get("/logout").status_code == 405
    assert client.post("/logout").status_code == 302


def test_login_wrong_password_shows_form(client, make_user):
    email, _ = make_user(role="Solicitante", email="web@test.com")
    resp = client.post(
        "/login",
        data={"email": email, "password": "errada"},
        follow_redirects=False,
    )
    assert resp.status_code == 200  # re-renderiza o form, sem redirecionar
