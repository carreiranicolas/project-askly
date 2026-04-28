"""Integration tests for Tickets API."""

import pytest


class TestTicketsAPI:
    """Tests for tickets API endpoints."""

    def test_create_ticket_success(self, client, db, solicitante_user, categoria):
        """Test successful ticket creation."""
        client.post(
            "/api/v1/auth/login",
            json={
                "email": "solicitante@test.com",
                "senha": "solicitante123",
            },
        )

        response = client.post(
            "/api/v1/chamados",
            json={
                "titulo": "Test Ticket",
                "descricao": "Test description for the ticket",
                "categoria_id": str(categoria.id),
                "prioridade": "MEDIA",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["titulo"] == "Test Ticket"
        assert data["status_atual"] == "ABERTO"

    def test_create_ticket_unauthenticated(self, client, db, categoria):
        """Test ticket creation without authentication."""
        response = client.post(
            "/api/v1/chamados",
            json={
                "titulo": "Test Ticket",
                "descricao": "Test description",
                "categoria_id": str(categoria.id),
            },
        )

        assert response.status_code == 401

    def test_list_tickets(self, client, db, solicitante_user, categoria):
        """Test listing tickets."""
        client.post(
            "/api/v1/auth/login",
            json={
                "email": "solicitante@test.com",
                "senha": "solicitante123",
            },
        )

        client.post(
            "/api/v1/chamados",
            json={
                "titulo": "Ticket 1",
                "descricao": "Description 1",
                "categoria_id": str(categoria.id),
            },
        )

        response = client.get("/api/v1/chamados")

        assert response.status_code == 200
        data = response.get_json()
        assert "items" in data
        assert "pagination" in data

    def test_get_ticket_detail(self, client, db, solicitante_user, categoria):
        """Test getting ticket details."""
        client.post(
            "/api/v1/auth/login",
            json={
                "email": "solicitante@test.com",
                "senha": "solicitante123",
            },
        )

        create_response = client.post(
            "/api/v1/chamados",
            json={
                "titulo": "Detail Test",
                "descricao": "Description",
                "categoria_id": str(categoria.id),
            },
        )
        ticket_id = create_response.get_json()["id"]

        response = client.get(f"/api/v1/chamados/{ticket_id}")

        assert response.status_code == 200
        data = response.get_json()
        assert "chamado" in data
        assert "comentarios" in data
        assert "historico" in data

    def test_change_status(self, client, db, atendente_user, solicitante_user, categoria):
        """Test changing ticket status."""
        client.post(
            "/api/v1/auth/login",
            json={
                "email": "solicitante@test.com",
                "senha": "solicitante123",
            },
        )

        create_response = client.post(
            "/api/v1/chamados",
            json={
                "titulo": "Status Test",
                "descricao": "Description",
                "categoria_id": str(categoria.id),
            },
        )
        ticket_id = create_response.get_json()["id"]

        client.post("/api/v1/auth/logout")
        client.post(
            "/api/v1/auth/login",
            json={
                "email": "atendente@test.com",
                "senha": "atendente123",
            },
        )

        response = client.post(
            f"/api/v1/chamados/{ticket_id}/status",
            json={
                "status": "EM_ATENDIMENTO",
                "motivo": "Iniciando atendimento",
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["chamado"]["status_atual"] == "EM_ATENDIMENTO"

    def test_add_comment(self, client, db, solicitante_user, categoria):
        """Test adding comment to ticket."""
        client.post(
            "/api/v1/auth/login",
            json={
                "email": "solicitante@test.com",
                "senha": "solicitante123",
            },
        )

        create_response = client.post(
            "/api/v1/chamados",
            json={
                "titulo": "Comment Test",
                "descricao": "Description",
                "categoria_id": str(categoria.id),
            },
        )
        ticket_id = create_response.get_json()["id"]

        response = client.post(
            f"/api/v1/chamados/{ticket_id}/comentarios",
            json={
                "conteudo": "This is a test comment",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["conteudo"] == "This is a test comment"
