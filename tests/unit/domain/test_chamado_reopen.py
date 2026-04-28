"""Tests for chamado reopen bug fix (L2).

Validates that resolvido_em is properly cleared when a ticket
transitions from RESOLVIDO back to EM_ATENDIMENTO.
"""

import pytest
from datetime import datetime, timezone, timedelta

from src.domain.enums import StatusChamado, PerfilUsuario
from tests.fixtures.factories import UsuarioFactory, ChamadoFactory


class TestChamadoReopen:
    """Tests for the reopen flow and resolvido_em handling."""

    def test_reopen_clears_resolvido_em(self):
        """Test that reopening a resolved ticket clears resolvido_em."""
        atendente = UsuarioFactory(atendente=True)
        chamado = ChamadoFactory(
            status_atual=StatusChamado.RESOLVIDO,
            resolvido_em=datetime.now(timezone.utc) - timedelta(hours=1),
            atendente_id=atendente.id,
        )

        assert chamado.resolvido_em is not None

        # Reopen: RESOLVIDO -> EM_ATENDIMENTO
        chamado.alterar_status(
            StatusChamado.EM_ATENDIMENTO,
            atendente.perfil,
            atendente.id,
        )

        assert chamado.status_atual == StatusChamado.EM_ATENDIMENTO
        assert chamado.resolvido_em is None

    def test_resolve_sets_resolvido_em(self):
        """Test that resolving a ticket sets resolvido_em."""
        atendente = UsuarioFactory(atendente=True)
        chamado = ChamadoFactory(
            status_atual=StatusChamado.EM_ATENDIMENTO,
            atendente_id=atendente.id,
        )

        chamado.alterar_status(
            StatusChamado.RESOLVIDO,
            atendente.perfil,
            atendente.id,
        )

        assert chamado.status_atual == StatusChamado.RESOLVIDO
        assert chamado.resolvido_em is not None

    def test_close_sets_fechado_em(self):
        """Test that closing a ticket sets fechado_em."""
        admin = UsuarioFactory(admin=True)
        chamado = ChamadoFactory(
            status_atual=StatusChamado.RESOLVIDO,
            resolvido_em=datetime.now(timezone.utc),
        )

        chamado.alterar_status(
            StatusChamado.FECHADO,
            admin.perfil,
            admin.id,
        )

        assert chamado.status_atual == StatusChamado.FECHADO
        assert chamado.fechado_em is not None

    def test_full_lifecycle_resolvido_em_integrity(self):
        """Test full lifecycle: open -> attending -> resolved -> reopen -> resolved."""
        atendente = UsuarioFactory(atendente=True)
        chamado = ChamadoFactory(
            status_atual=StatusChamado.ABERTO,
            atendente_id=atendente.id,
        )

        # ABERTO -> EM_ATENDIMENTO
        chamado.alterar_status(StatusChamado.EM_ATENDIMENTO, atendente.perfil, atendente.id)
        assert chamado.resolvido_em is None

        # EM_ATENDIMENTO -> RESOLVIDO
        chamado.alterar_status(StatusChamado.RESOLVIDO, atendente.perfil, atendente.id)
        first_resolve = chamado.resolvido_em
        assert first_resolve is not None

        # RESOLVIDO -> EM_ATENDIMENTO (reopen)
        chamado.alterar_status(StatusChamado.EM_ATENDIMENTO, atendente.perfil, atendente.id)
        assert chamado.resolvido_em is None

        # EM_ATENDIMENTO -> RESOLVIDO (again)
        chamado.alterar_status(StatusChamado.RESOLVIDO, atendente.perfil, atendente.id)
        assert chamado.resolvido_em is not None
        assert chamado.resolvido_em >= first_resolve
