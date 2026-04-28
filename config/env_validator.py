"""Environment variables validation for application startup."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class EnvValidationResult:
    ok: bool
    missing: list[str]


REQUIRED_ENV_VARS: tuple[str, ...] = (
    "FLASK_APP",
    "FLASK_ENV",
    "FLASK_DEBUG",
    "SECRET_KEY",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "DATABASE_URL",
)


def validate_required_env(required: tuple[str, ...] = REQUIRED_ENV_VARS) -> EnvValidationResult:
    missing: list[str] = []
    for key in required:
        value = os.environ.get(key)
        if value is None or str(value).strip() == "":
            missing.append(key)
    return EnvValidationResult(ok=len(missing) == 0, missing=missing)


def assert_required_env(required: tuple[str, ...] = REQUIRED_ENV_VARS) -> None:
    """
    Raises RuntimeError if any required env var is missing/empty.
    """
    result = validate_required_env(required)
    if not result.ok:
        missing_list = ", ".join(result.missing)
        raise RuntimeError(
            "Variáveis de ambiente obrigatórias ausentes ou vazias: "
            f"{missing_list}. "
            "Verifique seu arquivo `.env` e o ambiente do processo."
        )

