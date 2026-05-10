# Askly (MVP) — Gestão de Chamados Internos

Plataforma web para **gestão de chamados internos** (MVP), construída em **Flask 3.x + PostgreSQL (Docker)**, com **Clean Architecture**, **RBAC** (Solicitante/Atendente/Admin), **auditoria obrigatória de status** e **UI em Bulma**.

## Sumário

- [Stack](#stack)
- [Arquitetura (Clean Architecture)](#arquitetura-clean-architecture)
- [Setup rápido](#setup-rápido)
- [Comandos úteis](#comandos-úteis)
- [Swagger / OpenAPI](#swagger--openapi)
- [Segurança (onde está cada proteção)](#segurança-onde-está-cada-proteção)
  - [CSRF (Web)](#csrf-web)
  - [XSS / CSP / Security Headers](#xss--csp--security-headers)
  - [Tokenização (JWT) na API](#tokenização-jwt-na-api)
  - [Hash de senha](#hash-de-senha)
  - [RBAC (Solicitante / Atendente / Admin)](#rbac-solicitante--atendente--admin)
  - [Rate limiting](#rate-limiting)
- [Auditoria obrigatória de mudança de status](#auditoria-obrigatória-de-mudança-de-status)
- [Testes](#testes)

## Stack

- **Backend**: Flask 3.x
- **DB**: PostgreSQL (Docker)
- **ORM/Migrations**: SQLAlchemy + Flask-Migrate (Alembic)
- **Auth (Web)**: Flask-Login (sessão/cookies)
- **Auth (API)**: JWT Bearer token (tokenização)
- **Docs API**: `flask-restx` (Swagger UI)
- **UI**: Jinja2 + Bulma

## Arquitetura 


## Setup rápido

### 1) Banco de dados (PostgreSQL via Docker)

```bash
docker compose up -d
```

### 2) Ambiente Python

```bash
python -m venv venv
source venv/bin/activate #Linux/Mac
pip install .
```


### 5) Rodar

```bash
flask run 

#ou

python run.py
```

## Comandos úteis

- **Criar migração**: `flask db migrate -m "..." && flask db upgrade`
- **Rodar testes**: `pytest`
- **Seed**: `flask seed`



## Testes

Estrutura:
- Unit: `tests/unit/`
- Integração API: `tests/integration/api/`
- Factories: `tests/fixtures/factories.py`

Rodar:

```bash
pytest
```
