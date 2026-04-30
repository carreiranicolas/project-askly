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

## Arquitetura (Clean Architecture)

Código organizado em camadas, com dependências **apontando sempre para dentro**:

- **Domain** (`src/domain/`): entidades, enums, value objects, regras de negócio, interfaces (contratos).
- **Application** (`src/application/`): use cases (orquestração) + DTOs.
- **Infrastructure** (`src/infrastructure/`): repositórios SQLAlchemy, Unit of Work, serviços de segurança.
- **Presentation** (`src/presentation/`): web (blueprints/templates) e API REST (Swagger).

## Setup rápido

### 1) Banco de dados (PostgreSQL via Docker)

```bash
docker compose up -d
```

### 2) Ambiente Python

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3) Migrations

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 4) Seed inicial (admin + categorias)

```bash
flask seed
```

Cria um admin padrão:
- **Email**: `admin@askly.com`
- **Senha**: `admin123` (troque em produção!)

### 5) Rodar

```bash
flask run
```

## Comandos úteis

- **Criar migração**: `flask db migrate -m "..." && flask db upgrade`
- **Rodar testes**: `pytest`
- **Seed**: `flask seed`

## Swagger / OpenAPI

- **Swagger UI**: `GET /api/docs`
- **Base path**: `/api/v1`

Exemplos de endpoints:
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register`
- `GET /api/v1/chamados`
- `POST /api/v1/chamados/{id}/status`

## Segurança (onde está cada proteção)

### CSRF (Web)

**Onde está**: `src/presentation/app_factory.py`

- A proteção é feita pelo **Flask-WTF CSRF**:
  - `csrf = CSRFProtect()`
  - `csrf.init_app(app)`
- **Importante**: a API REST (`/api/*`) é **isenta de CSRF** porque nela usamos **Bearer JWT** (ou sessão) e requests JSON:
  - `csrf.exempt(api_bp)` em `register_api()`

### XSS / CSP / Security Headers

**Onde está**: `src/presentation/app_factory.py` + `config/settings.py`

- **Jinja2 autoescape**: por padrão o Jinja2 escapa HTML em templates, reduzindo risco de XSS refletido/armazenado (não use `|safe` sem necessidade).
- **CSP + headers de segurança**: via **Flask-Talisman**.
  - Configuração da CSP em produção: `config/settings.py` → `ProductionConfig.TALISMAN_CONTENT_SECURITY_POLICY`
  - Inicialização no app: `src/presentation/app_factory.py` → `talisman.init_app(...)`

### Tokenização (JWT) na API

**Onde está**:
- Serviço de token: `src/infrastructure/security/token_service.py`
- Decorator de auth API: `src/presentation/api/api_auth.py` (`api_auth_required`)
- Emissão do token no login: `src/presentation/api/v1/auth.py` (`/login` retorna `access_token`)

**Como usar**:
1) Faça login:

```bash
curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@askly.com","senha":"admin123"}'
```

2) Use o token em requests:

```bash
curl -s http://localhost:5000/api/v1/chamados \
  -H "Authorization: Bearer <SEU_TOKEN>"
```

**Config**:
- `JWT_SECRET_KEY` e `JWT_EXP_SECONDS` em `config/settings.py` (podem vir do `.env`).

### Hash de senha

**Onde está**: `src/infrastructure/security/password_hasher.py`

- Usa `werkzeug.security.generate_password_hash` / `check_password_hash`.
- Senhas **nunca** são armazenadas em texto puro (apenas `senha_hash`).

### RBAC (Solicitante / Atendente / Admin)

**Onde está**:
- Regras de perfil no domínio: `src/domain/enums/perfil.py`
- Validações de transição (status) no domínio: `src/domain/entities/chamado.py`
- Use cases aplicam autorização por perfil e ownership (ex.: solicitante só mexe no próprio chamado).

### Rate limiting

**Onde está**: `src/presentation/app_factory.py` + `config/settings.py`

- Inicialização via `Flask-Limiter`:
  - `limiter.init_app(...)`
- Configuração:
  - `RATELIMIT_DEFAULT` e `RATELIMIT_STORAGE_URL`

## Auditoria obrigatória de mudança de status

Regra mandatória do contrato: **toda alteração de status deve gerar um registro em `historico_status`**, no **mesmo commit** (transação).

**Onde está garantido**:
- Entidade `HistoricoStatus` (factory): `src/domain/entities/historico_status.py`
- Use case de mudança de status (transação atômica): `src/application/use_cases/tickets/change_status.py`
  - Atualiza `Chamado.status_atual`
  - Insere `HistoricoStatus`
  - Faz `commit()` via Unit of Work

## Testes

Estrutura:
- Unit: `tests/unit/`
- Integração API: `tests/integration/api/`
- Factories: `tests/fixtures/factories.py`

Rodar:

```bash
pytest
```
