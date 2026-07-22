# 🫀 CHATITA MAIL — HEARTBEAT (Documento Maestro de Desarrollo)

> **Este es el documento maestro vivo de Chatita Mail.**  
> Se actualiza tras CADA acción significativa. Nunca perder el hilo del desarrollo.

---

## 📌 METADATOS

| Campo | Valor |
|-------|-------|
| **Producto** | Chatita Mail v3.0 |
| **Tipo** | App standalone + link en side menu de Chatita |
| **Motor AI** | AION Brain v3.2 vía **MCP** (ya publicado) |
| **Repo** | https://github.com/ManuelCadena/chatita-mail |
| **Autor** | Manuel Cadena |
| **Última actualización** | 22-Jul-2026 08:25 (UTC-06:00) |
| **Fase actual** | 🟢 **FASE 1 ~90%** — pipeline LLM real E2E VERIFICADO (AION Brain conectado). Falta: conectores email (B-4), side menu (B-5) |
| **Meta usuario** | ≤5 min/día en email · 100% importantes atendidos · 0% spam |

---

## 🎯 OBJETIVO DEL PRODUCTO (NO CAMBIA)

Chatita Mail debe lograr que Manny:
1. Gaste **≤5 minutos diarios** revisando/contestando emails.
2. Nunca pierda un email importante (**100% cobertura**).
3. Tenga **0% spam/ruido** ocultando lo importante.
4. Maximice eficiencia laboral y personal.
5. Tenga gestión impecable con **explicabilidad (XAI)** y **control humano**.

---

## 🏛️ DECISIONES ARQUITECTÓNICAS FIJAS (INVIOLABLES)

Estas decisiones NO se re-discuten salvo autorización explícita de Manny:

| # | Decisión | Detalle |
|---|----------|---------|
| **AD-1** | **Standalone** | App autocontenida con su propio backend + frontend |
| **AD-2** | **AION Brain vía MCP** | NO reimplementar LLM routing. Consumir AION Brain (ya publicado) vía protocolo MCP |
| **AD-3** | **UI en side menu de Chatita** | Link de acceso dentro del menú lateral de Chatita (localhost + servidor) |
| **AD-4** | **Doble entorno** | Local (`localhost`) + AWS Chatita (`54.212.177.221`) |
| **AD-5** | **Stack backend** | Python 3.11 + FastAPI + PostgreSQL 15 + pgvector + Redis 7 |
| **AD-6** | **Stack frontend** | React 18 + TypeScript + Vite + TailwindCSS |
| **AD-7** | **XAI obligatorio** | Toda decisión AI muestra su razonamiento (Liu 2022, Al-Subaiey 2024) |
| **AD-8** | **Human-in-the-loop** | Acciones críticas requieren aprobación (Goodman 2022) |

---

## 🖥️ INFRAESTRUCTURA DE DESPLIEGUE

### Entorno LOCAL (desarrollo primario)
```
Ruta local:     /Users/manuelcadena/chatita-local/chatita-mail/
Backend:        http://localhost:8000
Frontend:       http://localhost:5173 (Vite dev)
AION Brain MCP: stdio local O http://localhost:3100
PostgreSQL:     localhost:5432 / DB: chatita_mail
Redis:          localhost:6379
UI link:        Chatita local side menu → /mail
```

### Entorno PRODUCCIÓN — Servidor "Chatita" (AWS)
```
IP:             54.212.177.221
SSH:            ssh -i ~/.ssh/citrusmax-key.pem -p 2222 ec2-user@54.212.177.221
Dominio:        chatita.ai
Backend:        /opt/chatita-mail/  → puerto interno 8000
Frontend:       nginx → https://chatita.ai/mail/
AION Brain:     /opt/aion-brain/ (v3.2, puerto 3100) — YA DESPLEGADO
PostgreSQL:     local en Chatita server (puerto 5432, SG restringido)
UI link:        Chatita prod side menu → https://chatita.ai/mail/
```

### Comando de deploy a Chatita (rsync)
```bash
rsync -avz -e "ssh -i ~/.ssh/citrusmax-key.pem -p 2222" \
  --exclude node_modules --exclude .git --exclude __pycache__ --exclude .env \
  /Users/manuelcadena/chatita-local/chatita-mail/ \
  ec2-user@54.212.177.221:/opt/chatita-mail/
```

> ⚠️ **REGLA SERVIDOR**: Chatita Mail va en servidor **Chatita (54.212.177.221)**, NO en M5.  
> AION Brain ya está en Chatita. NUNCA confundir servidores.

---

## 🔌 CÓMO USAR AION BRAIN (GUÍA DE INTEGRACIÓN MCP)

### Modelo de consumo
Chatita Mail **NO** implementa routing de LLMs. Delega TODO a AION Brain vía MCP.

### Opción A — MCP stdio (local dev)
```python
# backend/ai/aion_client.py
import asyncio, json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class AIONBrainClient:
    def __init__(self, server_path: str):
        self.params = StdioServerParameters(
            command="node",
            args=[server_path]  # /opt/aion-brain/mcp-server.js
        )

    async def orchestrate(self, prompt: str, task_type: str = "medium", **kwargs):
        async with stdio_client(self.params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "aion_orchestrate",
                    arguments={"prompt": prompt, "task_type": task_type, **kwargs}
                )
                return json.loads(result.content[0].text)
```

### Opción B — HTTP API (producción, más simple)
```python
# backend/ai/aion_client.py (HTTP variant)
import httpx

class AIONBrainHTTPClient:
    def __init__(self, base_url: str = "http://localhost:3100"):
        self.base_url = base_url

    async def orchestrate(self, prompt: str, task_type: str = "medium", **kwargs):
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}/orchestrate",
                json={"prompt": prompt, "task_type": task_type, **kwargs}
            )
            resp.raise_for_status()
            return resp.json()

    async def execute_tool(self, tool: str, params: dict):
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}/tool",
                json={"tool": tool, "params": params}
            )
            resp.raise_for_status()
            return resp.json()
```

### Task types de AION Brain (routing automático de costo/calidad)
| task_type | Modelo destino | Uso en Chatita Mail |
|-----------|----------------|---------------------|
| `simple` | Together Llama-3.3 ($0.18/1M) | Clasificación, urgencia, unsubscribe |
| `medium` | GPT-4o-mini | Resúmenes cortos, recomendaciones |
| `complex` | Claude Sonnet 4 | Task extraction, style learning, replies |
| `critical` | Claude Opus 4 | Phishing detection, decisiones irreversibles |
| `search` | Perplexity Sonar | Verificación de remitentes en web |
| `embedding` | HF BGE-M3 (gratis) | Búsqueda semántica, RAG |
| `classification` | HF BART-MNLI (gratis) | Zero-shot categorías |

### Herramientas AION Brain usadas por Chatita Mail
```
LLM:        aion_orchestrate (routing automático)
Vision:     hf_plant_disease→NO / openai_vision (OCR attachments)
NLP:        hf_sentiment_fin, hf_ner, hf_classify, hf_embed
Google:     google_calendar_*, google_drive_*, gmail_*
Corporate:  opencorporates_search (sender reputation)
Comms:      telegram_send_message (notificaciones)
Audio:      hf_transcribe_url (voice notes), elevenlabs TTS (voice replies)
```

---

## 🔬 FUNDAMENTO CIENTÍFICO (5 documentos de investigación integrados)

### Hallazgos que guían el diseño (papers 2001-2026)

| Hallazgo research | Fuente | Decisión de diseño en Chatita Mail |
|-------------------|--------|-----------------------------------|
| Clasificación ML alcanza **95-99%** vs reglas estáticas | Ghosh 2023 (RF 99.9%), Preetika 2025 | Clasificador híbrido: reglas rápidas + LLM para casos ambiguos |
| Spam **evoluciona** → filtros estáticos fallan | Jeeva 2023, Asliyuksek 2025 | Clasificación adaptativa vía LLM (no solo reglas) |
| Modelos **degradan con spam nuevo** (temporal drift) | Asliyuksek 2025, Kshirsagar 2025 | Feedback loop + re-evaluación continua |
| Asistente desplegado: **92.4% acc, 90.1% prec, 91.3% recall** multi-categoría | Chikodi 2025 | Meta de precisión mínima para clasificación producción |
| **EMAILSUM**: 2,549 threads, T5 full-thread = baseline fuerte | Zhang 2021 | Summarization de threads con contexto completo, no por email |
| ROUGE/BERTScore **correlacionan débil** con juicio humano | Zhang 2021 | Evaluar summaries con feedback real de Manny, no solo métricas |
| Modelos fallan en **intent/role understanding** en threads | Zhang 2021 | Pasar contexto de relación (sender history) al LLM |
| Summarization + **detección de intención maliciosa** juntas | Kashapov 2022 | Combinar summary con phishing analysis en un paso |
| **TF-IDF+LR = 2ms/email**, rápido y preciso | Jáñez-Martino 2023 | Pre-filtro lexical barato antes de invocar LLM (ahorro costo) |
| Mejor modelo depende de **dataset/idioma** (EN vs ES) | Jáñez-Martino 2023 | Clasificación multilingüe (Manny usa EN+ES) |
| AI **mejor que humanos** detectando commitments | Morrison 2024 | Commitment tracking automático |
| **Trust cae** si se revela autoría AI | Liu 2022 | 3 opciones de reply + edición + XAI |
| Email→Action ahorra **3-4x tiempo** | Navarro 2025 | Workflow automation con 91+ APIs |

### Arquitectura de clasificación en 2 etapas (costo-óptima)
```
Email entrante
    │
    ▼
[ETAPA 1: Pre-filtro lexical] ← TF-IDF + reglas (2ms, $0)
    │
    ├─ Confianza alta (>90%) → categoría directa ✅
    │
    └─ Ambiguo (<90%) → [ETAPA 2: LLM zero-shot] ← HF BART / Together ($0.0002)
                              │
                              └─ Casos críticos/seguridad → Claude ($0.003)
```
**Justificación**: Jáñez-Martino (2ms lexical) + Chikodi (92%+ LLM) + ahorro de costo AION.

---

## 🗺️ ROADMAP MAESTRO — 5 FASES

### Estado global
```
[ ] FASE 0 — Setup & Fundaciones        (Semana 1)      ⏸️ PENDIENTE
[ ] FASE 1 — Seguridad & Triage Core    (Semanas 1-3)   ⏸️ PENDIENTE
[ ] FASE 2 — Workflow Automation        (Semanas 4-6)   ⏸️ PENDIENTE
[ ] FASE 3 — Personalización & Trust    (Semanas 7-8)   ⏸️ PENDIENTE
[ ] FASE 4 — Features Avanzadas + Deploy(Semanas 9-10)  ⏸️ PENDIENTE
```

---

## ✅ FASE 0 — SETUP & FUNDACIONES (Semana 1)

**Objetivo**: Infra lista para desarrollar. Conexión AION Brain verificada.

### Tareas desglosadas

- [ ] **T0.1** — Crear entorno Python
  - `cd backend && python3.11 -m venv venv && source venv/bin/activate`
  - `pip install -r requirements.txt`
  - **Evidencia**: `pip list` muestra fastapi, sqlalchemy, etc.

- [ ] **T0.2** — Setup PostgreSQL local + pgvector
  - `createdb chatita_mail`
  - `psql chatita_mail -c "CREATE EXTENSION IF NOT EXISTS vector;"`
  - **Evidencia**: `psql chatita_mail -c "\dx"` muestra `vector`

- [ ] **T0.3** — Setup Redis local
  - Verificar `redis-cli ping` → `PONG`

- [ ] **T0.4** — Crear esquema de BD inicial (`scripts/setup_db.py`)
  - Tablas: `emails`, `email_accounts`, `classifications`, `tasks`, `commitments`, `style_profiles`, `security_events`, `embeddings`
  - **Evidencia**: `psql chatita_mail -c "\dt"` lista tablas

- [ ] **T0.5** — Implementar `AIONBrainClient` (HTTP + stdio)
  - Archivo: `backend/ai/aion_client.py`
  - **Evidencia**: test de conexión retorna respuesta de AION Brain

- [ ] **T0.6** — Test de humo AION Brain
  - `python -m backend.tests.test_aion_connection`
  - Llamar `orchestrate("Say OK", task_type="simple")` → verificar respuesta
  - **Evidencia**: output literal con respuesta del LLM

- [ ] **T0.7** — Esqueleto FastAPI (`backend/main.py`)
  - Endpoints: `GET /health`, `GET /version`
  - **Evidencia**: `curl localhost:8000/health` → 200

- [ ] **T0.8** — Esqueleto React (`frontend/`)
  - `npm create vite@latest . -- --template react-ts`
  - Configurar TailwindCSS
  - **Evidencia**: `npm run dev` levanta en :5173

- [ ] **T0.9** — Configurar `.env` local (sin commitear)
  - Copiar `.env.example` → `.env`, llenar keys
  - **Evidencia**: `python -c "from dotenv import load_dotenv; load_dotenv()"` sin error

**Criterio de salida FASE 0**: `curl localhost:8000/health` OK + AION Brain responde + DB con tablas.

---

## ✅ FASE 1 — SEGURIDAD & TRIAGE CORE (Semanas 1-3)

**Objetivo**: Eliminar 80% del ruido + proteger contra phishing. **60→10 min/día**.

### Módulo 1.1 — Ingesta de Email (multi-cuenta)

- [ ] **T1.1.1** — Conector Gmail (OAuth + API)
  - `backend/services/email/gmail_connector.py`
  - Usar `gmail_*` de AION Brain O google-api-python-client directo
  - **Evidencia**: listar 10 emails reales de inbox de Manny

- [ ] **T1.1.2** — Conector iCloud (IMAP)
  - `backend/services/email/icloud_connector.py`
  - **Evidencia**: conexión IMAP exitosa

- [ ] **T1.1.3** — Modelo unificado `Email` + persistencia
  - Guardar emails en `emails` table
  - **Evidencia**: `SELECT count(*) FROM emails` > 0

- [ ] **T1.1.4** — Sync incremental (webhook/polling)
  - **Evidencia**: nuevo email aparece en DB en <60s

### Módulo 1.2 — Clasificación en 2 Etapas (research-driven)

- [ ] **T1.2.1** — Pre-filtro lexical (TF-IDF + reglas)
  - `backend/ai/classifier/lexical_prefilter.py`
  - Basado en Jáñez-Martino (2ms/email)
  - **Evidencia**: clasifica newsletter conocido sin llamar LLM

- [ ] **T1.2.2** — Clasificador LLM zero-shot (casos ambiguos)
  - 6 categorías: CRITICAL, IMPORTANT, MEDIUM, LOW, SPAM, NOISE
  - `aion.orchestrate(task_type="simple")` (Together, barato)
  - **Evidencia**: JSON con categoría + confianza

- [ ] **T1.2.3** — Métrica de precisión (meta: ≥92% Chikodi)
  - Set de validación con 50 emails etiquetados por Manny
  - **Evidencia**: reporte accuracy/precision/recall

- [ ] **T1.2.4** — Feedback loop (temporal drift, Asliyuksek)
  - Si Manny reclasifica → guardar y reajustar
  - **Evidencia**: reclasificación persiste en DB

### Módulo 1.3 — Seguridad (Phishing + Prompt Injection)

- [ ] **T1.3.1** — `PhishingDetector` con XAI
  - Multi-capa: contenido + urgencia + sender + URLs + attachments
  - `task_type="critical"` (Claude Opus)
  - **Evidencia**: detecta email phishing de prueba con explicación

- [ ] **T1.3.2** — Sender reputation vía OpenCorporates
  - `aion.execute_tool("opencorporates_search", ...)`
  - **Evidencia**: dominio desconocido → flag

- [ ] **T1.3.3** — Prompt injection defense (sanitizer)
  - Detectar patrones "ignore instructions", tokens especiales
  - **Evidencia**: email con inyección → quarantine

- [ ] **T1.3.4** — Attachment safety
  - Análisis de tipos/nombres de archivo
  - **Evidencia**: .exe adjunto → flag

### Módulo 1.4 — Acciones Automáticas de Limpieza

- [ ] **T1.4.1** — Auto-unsubscribe inteligente
  - Detectar newsletters nunca abiertos → extraer link → unsubscribe
  - **Evidencia**: unsubscribe ejecutado en newsletter de prueba

- [ ] **T1.4.2** — Auto-archive LOW/NOISE
  - **Evidencia**: email NOISE archivado, sigue searchable

- [ ] **T1.4.3** — Notificaciones Telegram (CRITICAL/IMPORTANT)
  - `aion.execute_tool("telegram_send_message", ...)`
  - **Evidencia**: mensaje llega a Telegram de Manny

### Módulo 1.5 — UI Bandeja Inteligente (MVP)

- [ ] **T1.5.1** — Vista de inbox categorizado (React)
- [ ] **T1.5.2** — Badge de seguridad + panel XAI por email
- [ ] **T1.5.3** — Integrar link en side menu de Chatita (local)
  - **Evidencia**: click en menú Chatita → abre /mail

**Criterio de salida FASE 1**: inbox 100→20 emails/día, phishing bloqueado 95%+, tiempo 60→10 min.

---

## ✅ FASE 2 — WORKFLOW AUTOMATION (Semanas 4-6)

**Objetivo**: Email→Action automático. **10→5 min/día**.

- [ ] **T2.1** — `TaskExtractor` (Morrison 2024)
  - Extraer tareas + commitments de threads
  - **Evidencia**: tareas extraídas de email de prueba

- [ ] **T2.2** — Commitment tracking (propios + de otros)
  - Crear reminders en Google Calendar
  - **Evidencia**: evento creado en calendario

- [ ] **T2.3** — Auto-follow-up (commitments incumplidos)
  - **Evidencia**: draft de seguimiento generado

- [ ] **T2.4** — `MeetingScheduler` (Navarro 2025)
  - Detectar solicitud → buscar disponibilidad → proponer/crear
  - **Evidencia**: meeting agendado automáticamente

- [ ] **T2.5** — Thread summarization (EMAILSUM/Zhang 2021)
  - Resumir thread completo con contexto de relación
  - **Evidencia**: resumen de thread largo con puntos accionables

- [ ] **T2.6** — Document generation desde email
  - Buscar docs en Drive + generar draft
  - **Evidencia**: doc creado en Drive

- [ ] **T2.7** — Motor de aprobación (human-in-the-loop)
  - Acciones críticas esperan OK de Manny
  - **Evidencia**: acción pausada hasta aprobación

**Criterio de salida FASE 2**: tiempo 10→5 min, 0 commitments olvidados, 80% meetings auto.

---

## ✅ FASE 3 — PERSONALIZACIÓN & TRUST (Semanas 7-8)

**Objetivo**: Replies auténticos + confianza total. **85%+ acceptance**.

- [ ] **T3.1** — `StyleLearningEngine` (Novelo 2025)
  - Analizar 100 emails enviados → perfil de estilo
  - **Evidencia**: JSON de style_profile guardado

- [ ] **T3.2** — Multi-style replies (3 opciones, Liu 2022)
  - Natural / Professional / Brief + XAI
  - **Evidencia**: 3 opciones generadas con explicación

- [ ] **T3.3** — Feedback loop de ediciones (Goodman 2022)
  - Aprender de cambios de Manny
  - **Evidencia**: style_profile actualizado tras edición

- [ ] **T3.4** — XAI universal (toda decisión explicada)
  - **Evidencia**: cada recomendación muestra reasoning

- [ ] **T3.5** — Multi-idioma EN/ES (Jáñez-Martino)
  - **Evidencia**: reply en ES para email en ES

**Criterio de salida FASE 3**: reply acceptance 85%+, trust score 90%+, ediciones <20%.

---

## ✅ FASE 4 — FEATURES AVANZADAS + DEPLOY PRODUCCIÓN (Semanas 9-10)

**Objetivo**: Pulido + despliegue a servidor Chatita.

- [ ] **T4.1** — Voice replies (ElevenLabs vía AION)
- [ ] **T4.2** — Attachment auto-suggest desde Drive
- [ ] **T4.3** — Accessibility mode (Goodman 2022, dyslexia)
- [ ] **T4.4** — Dashboard de analytics (tiempo ahorrado, métricas)
- [ ] **T4.5** — Suite de tests E2E (Playwright)
- [ ] **T4.6** — Build frontend producción (`npm run build`)
- [ ] **T4.7** — Deploy backend a Chatita server (rsync + systemd)
  - **Evidencia**: `curl https://chatita.ai/mail/api/health` → 200
- [ ] **T4.8** — Configurar nginx `/mail/` en Chatita
- [ ] **T4.9** — Link en side menu de Chatita PRODUCCIÓN
  - **Evidencia**: chatita.ai side menu → /mail abre
- [ ] **T4.10** — Verificar AION Brain conectado en prod
  - **Evidencia**: clasificación funciona en servidor Chatita

**Criterio de salida FASE 4**: chatita.ai/mail operativo, meta ≤5 min/día validada.

---

## 📊 MÉTRICAS DE ÉXITO (tracking continuo)

| KPI | Meta | Actual | Fuente research |
|-----|------|--------|-----------------|
| Tiempo/día en email | ≤5 min | — | Objetivo Manny |
| Emails importantes perdidos | 0 | — | — |
| Phishing bloqueado | ≥95% | — | Viswanathan 2025 |
| Precisión clasificación | ≥92% | — | Chikodi 2025 |
| Spam en inbox | <5% | — | Mathew 2026 |
| Reply acceptance rate | ≥85% | — | — |
| Costo mensual AION | <$15 | — | — |

---

## 📓 BITÁCORA DE CAMBIOS (actualizar SIEMPRE)

| Fecha | Acción | Estado | Evidencia |
|-------|--------|--------|-----------|
| 22-Jul-2026 02:40 | Repo GitHub creado + estructura + docs | DEPLOY-VERIFICADO | commit 08d506b, push OK |
| 22-Jul-2026 02:51 | Análisis research v3.0 (50 papers) | HECHO VERIFICADO | commit c9f7125 |
| 22-Jul-2026 02:58 | Arquitectura v3.0 + Executive Summary | HECHO VERIFICADO | commit 106491b |
| 22-Jul-2026 03:00 | HEARTBEAT maestro creado (este doc) | HECHO VERIFICADO | este archivo |
| 22-Jul-2026 03:10 | FASE 0 completa: config, DB (8 tablas+pgvector), AIONClient, FastAPI | HECHO VERIFICADO | `setup_db` OK, `/health` DB✅ Redis✅ |
| 22-Jul-2026 03:10 | FASE 1 backend: clasificador 2 etapas, phishing+XAI, prompt-injection, triage, unsubscribe, notifier, 9 rutas API | HECHO VERIFICADO | E2E ingest+triage+analyze OK; 9/9 tests PASSED |
| 22-Jul-2026 03:10 | FASE 1 frontend: React+TS+Vite+Tailwind, inbox categorizado, filtros, panel XAI (clasificación+seguridad) | BUILD-VERIFICADO | `npm run build` OK (131 módulos, dist generado, exit 0) |
| 22-Jul-2026 08:25 | B-3 AION Brain conectado: arrancado http-server.js :3100, corregido contrato (query/taskType + execution.output) en aion_client.py | HECHO VERIFICADO | `/health` aion reachable:true; orchestrate 200 OK |
| 22-Jul-2026 08:25 | FIX ruta: /preview capturado como {email_id} → reordenado en classify.py | HECHO VERIFICADO | causa raíz en log (DataError UUID 'preview'), post-fix clasifica OK |
| 22-Jul-2026 08:25 | E2E con LLM real: clasificación IMPORTANT/CRITICAL stage=llm + reasoning; phishing crítico score 95 dangerous/block con XAI de Claude | HECHO VERIFICADO | 9/9 tests PASSED; triage E2E "contrato hoy"→CRITICAL 0.95 |

---

## 🚧 BLOQUEOS / PENDIENTES DE DECISIÓN

| # | Bloqueo | Necesita | Estado |
|---|---------|----------|--------|
| B-1 | Aprobación arquitectura v3.0 | OK de Manny | ✅ APROBADO (procede) |
| B-2 | ¿Empezar FASE 0 ya? | Confirmación | ✅ HECHO |
| B-3 | Conectar AION Brain :3100 (orchestrate) | — | ✅ RESUELTO (orchestrate LLM+phishing verificado). ⚠️ Parcial: `execute_tool` (opencorporates/telegram) degrada — AION rutea tools vía gateway :8088 no activo + esos tools no están en su registro de 67 |
| B-4 | Conectores reales Gmail/iCloud (ingesta) | OAuth + credenciales | 🔴 ABIERTO — hoy ingesta vía POST /api/inbox/ingest |
| B-5 | Integrar link `/mail` en side menu de Chatita (local) | Editar UI de Chatita | 🔴 ABIERTO |
| B-6 | AION Brain no arranca como servicio persistente (hoy proceso manual :3100) | systemd/pm2 o launchd | 🟡 ABIERTO — arranque manual verificado |

---

## 🔗 DOCUMENTOS RELACIONADOS

- `README.md` — overview del producto
- `docs/EXECUTIVE_SUMMARY_v3.0.md` — resumen ejecutivo
- `docs/CHATITA_MAIL_RESEARCH_ANALYSIS_v3.0.md` — 23 áreas de oportunidad
- `docs/architecture/CHATITA_MAIL_ARCHITECTURE_v3.0_RESEARCH_ENHANCED.md` — arquitectura técnica
- `docs/guides/CHATITA_MAIL_AION_BRAIN_INTEGRATION_v3.2.md` — integración AION Brain
- `docs/api/CHATITA_MAIL_AION_API_MATRIX.md` — matriz de APIs

---

## 📖 PROTOCOLO DE ACTUALIZACIÓN DE ESTE HEARTBEAT

1. Tras CADA tarea completada → marcar `[x]` + agregar fila en Bitácora con evidencia.
2. Al iniciar sesión de desarrollo → leer este doc primero.
3. Al cambiar de fase → actualizar "Fase actual" en metadatos.
4. Nunca declarar tarea completa sin evidencia (regla M-CHEX).
5. Commitear este doc tras cada actualización significativa.

---

**FIN DEL HEARTBEAT — Chatita Mail v3.0**  
*Última línea de defensa contra perder el hilo del desarrollo.*
