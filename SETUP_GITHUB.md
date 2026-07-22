# Setup GitHub Repository for Chatita Mail

**Fecha**: 22-Jul-2026  
**Autor**: Manuel Cadena

---

## 🎯 Objetivo

Crear repositorio GitHub dedicado para **Chatita Mail v2.0** y migrar toda la documentación y código desde `chatita-local`.

---

## 📋 Pasos para Setup

### 1. Crear Repositorio en GitHub

```bash
# Opción A: Via GitHub CLI (recomendado)
gh repo create ManuelCadena/chatita-mail \
  --public \
  --description "AI-Powered Email Management System with AION Brain Integration" \
  --clone

# Opción B: Via web
# 1. Ir a https://github.com/new
# 2. Owner: ManuelCadena
# 3. Repository name: chatita-mail
# 4. Description: AI-Powered Email Management System with AION Brain Integration
# 5. Public
# 6. Add README: NO (ya lo tenemos)
# 7. Add .gitignore: NO (ya lo tenemos)
# 8. Choose a license: MIT (ya lo tenemos)
# 9. Create repository
```

---

### 2. Inicializar Git en el Directorio Local

```bash
cd /Users/manuelcadena/chatita-local/chatita-mail

# Inicializar git
git init

# Agregar remote
git remote add origin https://github.com/ManuelCadena/chatita-mail.git

# Verificar
git remote -v
```

---

### 3. Mover Documentación Existente

```bash
# Crear estructura de carpetas
mkdir -p docs/architecture
mkdir -p docs/api
mkdir -p docs/guides
mkdir -p backend/ai
mkdir -p backend/models
mkdir -p backend/routes
mkdir -p backend/services
mkdir -p backend/tests
mkdir -p frontend/src
mkdir -p scripts

# Copiar documentos desde chatita-local/docs
cp /Users/manuelcadena/chatita-local/docs/CHATITA_MAIL_*.md docs/

# Organizar por categoría
mv docs/CHATITA_MAIL_ARCHITECTURE_*.md docs/architecture/
mv docs/CHATITA_MAIL_AION_API_MATRIX.md docs/api/
mv docs/CHATITA_MAIL_EXECUTIVE_SUMMARY.md docs/
mv docs/CHATITA_MAIL_IMPLEMENTATION_PLAN.md docs/guides/
```

---

### 4. Crear Estructura de Proyecto

```bash
# Backend structure
touch backend/__init__.py
touch backend/main.py
touch backend/requirements.txt
touch backend/.env.example

# Frontend structure
touch frontend/package.json
touch frontend/tsconfig.json
touch frontend/.env.example

# Scripts
touch scripts/setup_db.py
touch scripts/deploy.sh
chmod +x scripts/deploy.sh

# GitHub workflows
mkdir -p .github/workflows
touch .github/workflows/ci.yml
touch .github/workflows/deploy.yml
```

---

### 5. Crear .env.example

```bash
cat > backend/.env.example << 'EOF'
# ============================================================
# Chatita Mail v2.0 — Environment Variables Template
# Copy this file to .env and fill in your API keys
# NEVER commit .env to git
# ============================================================

# ── Server Configuration ────────────────────────────────────
CHATITA_MAIL_PORT=8000
CHATITA_MAIL_ENV=development
SECRET_KEY=your-secret-key-here

# ── Database ────────────────────────────────────────────────
DATABASE_URL=postgresql://user:password@localhost:5432/chatita_mail
REDIS_URL=redis://localhost:6379/0

# ── AION Brain ──────────────────────────────────────────────
AION_BRAIN_URL=http://localhost:3100
# Or use MCP stdio:
AION_BRAIN_MCP_PATH=/opt/chatita/aion-brain/mcp-server.js

# ── Email Accounts ──────────────────────────────────────────
# Gmail
GMAIL_CLIENT_ID=your-gmail-client-id
GMAIL_CLIENT_SECRET=your-gmail-client-secret
GMAIL_REFRESH_TOKEN=your-gmail-refresh-token

# iCloud
ICLOUD_USERNAME=your-icloud-email
ICLOUD_APP_PASSWORD=your-icloud-app-password

# ── Google Workspace ────────────────────────────────────────
GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/service-account.json
GOOGLE_DRIVE_FOLDER_ID=your-drive-folder-id

# ── LLM Providers (via AION Brain) ──────────────────────────
# These are used by AION Brain, not directly by Chatita Mail
# Configure them in AION Brain's .env instead

# ── Optional: Direct API Keys ───────────────────────────────
# Only needed if bypassing AION Brain for specific services
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
HUME_API_KEY=...
ELEVENLABS_API_KEY=...

# ── Communication ───────────────────────────────────────────
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id

# ── Monitoring ──────────────────────────────────────────────
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO
EOF
```

---

### 6. Crear requirements.txt

```bash
cat > backend/requirements.txt << 'EOF'
# Chatita Mail v2.0 — Python Dependencies

# ── Web Framework ───────────────────────────────────────────
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.2
pydantic-settings==2.6.0

# ── Database ────────────────────────────────────────────────
sqlalchemy==2.0.36
asyncpg==0.30.0
alembic==1.14.0
psycopg2-binary==2.9.10
redis==5.2.0

# ── Vector Store ────────────────────────────────────────────
pgvector==0.3.6
numpy==2.1.3

# ── Email ───────────────────────────────────────────────────
imapclient==3.0.1
email-validator==2.2.0
python-email==0.1.0

# ── Google APIs ─────────────────────────────────────────────
google-auth==2.36.0
google-auth-oauthlib==1.2.1
google-auth-httplib2==0.2.0
google-api-python-client==2.154.0

# ── HTTP Client ─────────────────────────────────────────────
httpx==0.28.1
aiohttp==3.11.10

# ── AI/ML ───────────────────────────────────────────────────
openai==1.57.2
anthropic==0.39.0
sentence-transformers==3.3.1

# ── Utilities ───────────────────────────────────────────────
python-dotenv==1.0.1
pydantic-settings==2.6.0
python-multipart==0.0.20
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dateutil==2.9.0.post0

# ── Testing ─────────────────────────────────────────────────
pytest==8.3.4
pytest-asyncio==0.24.0
pytest-cov==6.0.0
httpx==0.28.1

# ── Code Quality ────────────────────────────────────────────
black==24.10.0
pylint==3.3.2
mypy==1.13.0
isort==5.13.2

# ── Monitoring ──────────────────────────────────────────────
sentry-sdk==2.19.2
prometheus-client==0.21.0
EOF
```

---

### 7. Crear package.json para Frontend

```bash
cat > frontend/package.json << 'EOF'
{
  "name": "chatita-mail-frontend",
  "version": "2.0.0-alpha",
  "description": "Chatita Mail Frontend - React + TypeScript",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "format": "prettier --write \"src/**/*.{ts,tsx,css}\"",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.28.0",
    "@tanstack/react-query": "^5.62.7",
    "axios": "^1.7.9",
    "lucide-react": "^0.468.0",
    "date-fns": "^4.1.0",
    "zustand": "^5.0.2",
    "react-hot-toast": "^2.4.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@typescript-eslint/eslint-plugin": "^8.15.0",
    "@typescript-eslint/parser": "^8.15.0",
    "@vitejs/plugin-react": "^4.3.4",
    "autoprefixer": "^10.4.20",
    "eslint": "^9.15.0",
    "eslint-plugin-react-hooks": "^5.0.0",
    "eslint-plugin-react-refresh": "^0.4.14",
    "postcss": "^8.4.49",
    "prettier": "^3.3.3",
    "tailwindcss": "^3.4.15",
    "typescript": "^5.7.2",
    "vite": "^6.0.3",
    "vitest": "^2.1.8"
  }
}
EOF
```

---

### 8. Primer Commit

```bash
cd /Users/manuelcadena/chatita-local/chatita-mail

# Stage all files
git add .

# Commit
git commit -m "Initial commit: Chatita Mail v2.0 with AION Brain integration

- Complete architecture documentation
- AION Brain v3.2 integration guide
- API matrix with 91+ services
- Executive summary and implementation plan
- Project structure setup
- Backend and frontend scaffolding
- MIT License"

# Push to GitHub
git branch -M main
git push -u origin main
```

---

### 9. Configurar GitHub Settings

**En GitHub web (https://github.com/ManuelCadena/chatita-mail/settings):**

1. **General**
   - ✅ Features: Issues, Projects, Wiki
   - ✅ Pull Requests: Allow squash merging
   - ✅ Automatically delete head branches

2. **Branches**
   - Branch protection rule for `main`:
     - ✅ Require pull request before merging
     - ✅ Require status checks to pass
     - ✅ Require branches to be up to date

3. **Secrets and Variables**
   - Add secrets para CI/CD:
     - `CHATITA_SERVER_SSH_KEY`
     - `SENTRY_DSN`
     - `DOCKER_USERNAME`
     - `DOCKER_PASSWORD`

4. **Topics**
   - Agregar tags: `email`, `ai`, `llm`, `fastapi`, `react`, `typescript`, `aion-brain`, `automation`

---

### 10. Crear GitHub Actions

```bash
cat > .github/workflows/ci.yml << 'EOF'
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: chatita_mail_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        cd backend
        pytest tests/ --cov --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v4
      with:
        file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run tests
      run: |
        cd frontend
        npm test
    
    - name: Build
      run: |
        cd frontend
        npm run build

  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Lint backend
      run: |
        cd backend
        pip install pylint black
        black --check .
        pylint ai/ models/ routes/
    
    - name: Lint frontend
      run: |
        cd frontend
        npm ci
        npm run lint
EOF
```

---

## ✅ Verificación Final

```bash
# Verificar estructura
tree -L 2 /Users/manuelcadena/chatita-local/chatita-mail

# Verificar git
cd /Users/manuelcadena/chatita-local/chatita-mail
git status
git remote -v

# Verificar en GitHub
open https://github.com/ManuelCadena/chatita-mail
```

---

## 📊 Resultado Esperado

```
chatita-mail/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── backend/
│   ├── ai/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── tests/
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── tsconfig.json
│   └── .env.example
├── docs/
│   ├── architecture/
│   │   ├── CHATITA_MAIL_ARCHITECTURE_v2.0_AION_POWERED.md
│   │   └── CHATITA_MAIL_ARCHITECTURE_PhD_v1.0.md
│   ├── api/
│   │   └── CHATITA_MAIL_AION_API_MATRIX.md
│   ├── guides/
│   │   ├── CHATITA_MAIL_IMPLEMENTATION_PLAN.md
│   │   └── CHATITA_MAIL_AION_BRAIN_INTEGRATION_v3.2.md
│   └── CHATITA_MAIL_EXECUTIVE_SUMMARY.md
├── scripts/
│   ├── setup_db.py
│   └── deploy.sh
├── .gitignore
├── LICENSE
├── README.md
└── SETUP_GITHUB.md
```

---

## 🚀 Próximos Pasos

1. ✅ Ejecutar todos los comandos de este documento
2. ✅ Verificar que el repo esté público en GitHub
3. ✅ Configurar branch protection
4. ✅ Agregar badges al README
5. ✅ Crear primer issue/milestone para Fase 1
6. ✅ Invitar colaboradores (si aplica)

---

**¿Procedemos con la creación del repositorio?** 🚀
