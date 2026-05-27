#!/bin/sh
set -e

echo "[entrypoint] Aplicando migrations..."
flask db upgrade

echo "[entrypoint] Iniciando gunicorn..."
exec gunicorn \
    --workers "${GUNICORN_WORKERS:-3}" \
    --bind "0.0.0.0:8000" \
    --access-logfile - \
    --error-logfile - \
    "run:app"
