"""Integration tests for Auth API."""

import pytest


class TestAuthAPI:
    """Tests for authentication API endpoints."""

    def test_login_success(self, client, db, solicitante_user):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "solicitante@test.com",
                "senha": "solicitante123",
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "usuario" in data
        assert data["usuario"]["email"] == "solicitante@test.com"

    def test_login_invalid_credentials(self, client, db):
        """Test login with invalid credentials."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrong@test.com",
                "senha": "wrongpassword",
            },
        )

        assert response.status_code == 401
        data = response.get_json()
        assert "error" in data

    def test_register_success(self, client, db):
        """Test successful registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "nome": "New User",
                "email": "newuser@test.com",
                "senha": "password123",
                "confirmar_senha": "password123",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["email"] == "newuser@test.com"
        assert data["perfil"] == "solicitante"

    def test_register_duplicate_email(self, client, db, solicitante_user):
        """Test registration with existing email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "nome": "Another User",
                "email": "solicitante@test.com",
                "senha": "password123",
                "confirmar_senha": "password123",
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_me_authenticated(self, client, db, solicitante_user):
        """Test /me endpoint when authenticated."""
        client.post(
            "/api/v1/auth/login",
            json={
                "email": "solicitante@test.com",
                "senha": "solicitante123",
            },
        )

        response = client.get("/api/v1/auth/me")

        assert response.status_code == 200
        data = response.get_json()
        assert data["email"] == "solicitante@test.com"

    def test_me_unauthenticated(self, client, db):
        """Test /me endpoint when not authenticated."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401
