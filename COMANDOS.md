# Askly — Guia de Comandos Úteis

Este documento centraliza todos os comandos necessários para rodar, testar, fazer build e manter a aplicação.

---

## 🚀 1. Executando a Aplicação (Desenvolvimento)

**Subir o Banco de Dados (PostgreSQL):**
```bash
docker-compose up -d
```

**Iniciar o servidor Flask:**
```bash
# Ativa o ambiente virtual (se ainda não estiver ativo)
source .venv/bin/activate

# Roda o servidor
flask run
```

> **Aviso:** Se o servidor estiver rodando na porta 5000 e você não conseguir acessá-lo externamente, certifique-se de que o `host` no `run.py` (ou na variável de ambiente `FLASK_RUN_HOST`) esteja configurado para a interface correta (ex: `127.0.0.1` para localhost).

---

## 📦 2. Migrations (Banco de Dados)

O projeto usa `Flask-Migrate` (Alembic) para versionamento do banco de dados.

**Inicializar o repositório de migrations (apenas uma vez, já feito):**
```bash
flask db init
```

**Gerar uma nova migration após alterar os models:**
```bash
flask db migrate -m "Descrição clara do que mudou"
```

**Aplicar as migrations no banco de dados:**
```bash
flask db upgrade
```

**Reverter a última migration aplicada:**
```bash
flask db downgrade
```

---

## 🧪 3. Testes

O projeto usa `pytest` com 100% de cobertura nos testes unitários e testes de integração.

**Rodar TODOS os testes (unitários + integração):**
```bash
# Nota: Os testes de integração requerem o banco de dados de teste rodando
pytest -v --tb=short
```

**Rodar apenas os testes unitários (rápidos, não precisam de banco real):**
```bash
pytest tests/unit/ -v --tb=short
```

**Rodar apenas os testes de integração:**
```bash
pytest tests/integration/ -v --tb=short
```

**Verificar a cobertura de testes:**
```bash
pytest --cov=src --cov-report=term-missing tests/
```

---

## 🧹 4. Seed do Banco de Dados

Para popular o banco com dados iniciais (Categoria e Usuário Admin):

```bash
# Se quiser uma senha específica para o admin, defina a env var:
export ADMIN_SEED_PASSWORD="sua_senha_secreta"

# Roda o script de seed
flask seed
```

> **Nota de Segurança:** Se `ADMIN_SEED_PASSWORD` não for definida, o comando irá gerar e imprimir uma senha aleatória segura no console.

---

## 🔒 5. Hardening de Segurança (Em Produção)

Antes de realizar o deploy, lembre-se de configurar estas variáveis no seu ambiente (ex: AWS Secrets Manager, Vercel Env Vars, etc):

```bash
FLASK_ENV=production
FLASK_DEBUG=0

# Gerar com: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY="sua-chave-gerada"

# Senha forte para o banco
POSTGRES_PASSWORD="sua-senha-do-banco"

# Origens permitidas para a API (CORS)
CORS_ORIGINS="https://meudominio.com,https://app.meudominio.com"
```

---

## 🛠️ 6. Qualidade de Código (Linting & Type Checking)

Para garantir que o código segue os padrões do projeto:

**Verificação de tipos (MyPy):**
```bash
mypy src/
```

**Linting de código (Flake8):**
```bash
flake8 src/ tests/
```

**Formatação automática (Black):**
```bash
black src/ tests/
```

**Ordenação de imports (isort):**
```bash
isort src/ tests/
```
