# CHATITA MAIL — Arquitectura State-of-the-Art
## Aplicación de Email Inteligente con IA Integrada

**Versión:** 1.0  
**Fecha:** 21-Julio-2026  
**Autor:** Cascade AI (PhD-level Computer Systems & Email Application Development)  
**Cliente:** Manuel Cadena  

---

## EXECUTIVE SUMMARY

**Chatita Mail** es una aplicación de correo electrónico de próxima generación que integra inteligencia artificial profunda para eliminar el ruido, priorizar lo importante y ahorrar tiempo masivamente en la gestión de email.

### Objetivo Principal
**Reducir el tiempo de Manny en email de ~2-3 horas/día a <30 minutos/día**, eliminando spam/ruido y concentrándose solo en emails de trabajo importantes y personales valiosos.

### Diferenciadores Clave vs. Competencia

| Feature | Superhuman | HEY | Spark | **Chatita Mail** |
|---------|-----------|-----|-------|------------------|
| **AI Nativa Chatita** | ❌ | ❌ | ❌ | ✅ Integración total con Chatita AI |
| **Multi-cuenta (Gmail + iCloud)** | ✅ | ⚠️ Limitado | ✅ | ✅ IMAP universal |
| **Clasificación AI Profunda** | ⚠️ Básica | ⚠️ Manual | ⚠️ Básica | ✅ NLP + embeddings + learning |
| **Auto-respuestas en tu voz** | ✅ | ❌ | ⚠️ Básica | ✅ Fine-tuned en tu estilo |
| **Integración Dashboard** | ❌ | ❌ | ❌ | ✅ Embebido en chatita.ai |
| **Modo Agente Autónomo** | ❌ | ❌ | ❌ | ✅ Chatita maneja inbox 24/7 |
| **Precio** | $30/mes | $99/año | $8/mes | **GRATIS** (parte del ecosistema) |

---

## PARTE 1: BENCHMARK DE MERCADO — ANÁLISIS COMPETITIVO

### 1.1 Aplicaciones Líderes Analizadas

#### **Superhuman** — El Estándar de Oro para Power Users
- **Precio:** $30/mes
- **Fortalezas:**
  - Velocidad extrema (keyboard-first, <100ms latency)
  - Split Inbox (separa importante de ruido)
  - AI triage y búsqueda en lenguaje natural
  - Reminders y follow-ups automáticos
  - Instant replies con AI
- **Debilidades:**
  - Precio premium
  - Solo Gmail + Outlook (no iCloud IMAP genérico)
  - AI no personalizada profundamente
  - No tiene agente autónomo

#### **HEY** — Filosofía de Control Total
- **Precio:** $99/año
- **Fortalezas:**
  - "Screener" — tú decides quién puede escribirte
  - Separación manual de categorías (Imbox, Feed, Paper Trail)
  - Privacidad extrema
  - Calendario integrado
- **Debilidades:**
  - Requiere cambiar de email (@hey.com)
  - Clasificación mayormente manual
  - AI limitada
  - Curva de aprendizaje alta

#### **Spark** — El Mejor Gratuito con AI
- **Precio:** Gratis / $8/mes Pro
- **Fortalezas:**
  - Smart Inbox con auto-categorización
  - AI writing assistant
  - Colaboración en equipo
  - Cross-platform (Mac, iOS, Android, Windows)
  - Gatekeeper para bloquear senders
- **Debilidades:**
  - AI menos sofisticada que Superhuman
  - Performance inferior en inboxes grandes (>10K emails)
  - Búsqueda limitada

#### **Shortwave** — AI-Native para Gmail
- **Precio:** Gratis / $7-10/mes
- **Fortalezas:**
  - AI summaries de threads largos
  - Smart bundling automático
  - Voice-matched drafts
  - Task-style email handling
- **Debilidades:**
  - Solo Gmail
  - Menos maduro que competidores
  - Features AI aún en desarrollo

### 1.2 Features State-of-the-Art Identificadas

De la investigación de mercado, estas son las capacidades que **DEBE** tener Chatita Mail para ser líder:

#### **Tier 0: Inbox Management Inteligente**
1. ✅ **Auto-categorización multi-nivel**
   - Trabajo vs Personal vs Transaccional vs Marketing
   - Por remitente (VIP, team, vendors, unknown)
   - Por intent (action required, FYI, calendar, invoice)
   - Por urgencia (crítico, importante, normal, low-priority)

2. ✅ **Priority Inbox con AI Scoring**
   - Cada email recibe score 0-100 basado en:
     - Sender importance (histórico de interacciones)
     - Content sentiment (urgente, angry, question, FYI)
     - Thread context (continuación de conversación importante)
     - Timing (deadline mentions, time-sensitive keywords)
   - Top 10-20 emails del día siempre visibles primero

3. ✅ **Noise Reduction Agresivo**
   - Auto-archive newsletters (con opción de digest semanal)
   - Auto-bundle notifications (GitHub, Jira, AWS, etc.)
   - Spam/junk filtering con ML (no solo reglas)
   - "Gatekeeper" — nuevos senders requieren aprobación

#### **Tier 1: AI Writing & Responses**
4. ✅ **Smart Replies Contextuales**
   - Suggested replies de 1-click para emails comunes
   - Aprende de tus respuestas pasadas
   - Considera thread history completo

5. ✅ **AI Draft Generation en Tu Voz**
   - Fine-tuned en tu estilo de escritura (análisis de 1000+ emails enviados)
   - Tono adaptativo (formal para clientes, casual para equipo)
   - Grounded en contexto: CRM data, calendar, docs previos
   - **Proactive drafts** — Chatita prepara respuestas antes de que las pidas

6. ✅ **Compose Assistant**
   - "Help me write" desde cero
   - Rewrite (más formal, más conciso, más amigable)
   - Grammar & tone check
   - Multi-idioma (ES/EN)

#### **Tier 2: Productivity & Automation**
7. ✅ **Follow-up & Reminders**
   - Auto-detect emails que necesitan respuesta
   - Snooze inteligente (resurface en momento óptimo)
   - Remind if no reply after X days

8. ✅ **Calendar & Meeting Intelligence**
   - Parse meeting requests automáticamente
   - Suggest meeting times basado en calendar availability
   - Generate meeting prep summaries
   - Post-meeting follow-up drafts

9. ✅ **Search en Lenguaje Natural**
   - "Muéstrame emails de clientes sobre renovaciones en Mayo"
   - "¿Qué dijo Laura sobre el proyecto X?"
   - Semantic search (no solo keywords)

10. ✅ **Thread Summarization**
    - Resumen de 1-párrafo de threads largos
    - Highlighted action items
    - Timeline de decisiones clave

#### **Tier 3: Agentic & Autonomous**
11. ✅ **Modo Agente Autónomo** (ÚNICO EN CHATITA MAIL)
    - Chatita revisa inbox cada hora
    - Auto-archive ruido
    - Draft replies para emails rutinarios
    - Daily briefing: "Aquí están los 5 emails que necesitas ver hoy"
    - **Opcional:** Auto-send replies simples (confirmaciones, "gracias", etc.) con guardrails

12. ✅ **Proactive Assistance**
    - "Vi que tienes meeting con X mañana, aquí está el contexto de sus últimos 3 emails"
    - "Este email menciona un deadline, ¿agrego a tu calendar?"
    - "Detecté 3 emails duplicados de diferentes senders sobre el mismo tema, ¿los agrupo?"

---

## PARTE 2: ARQUITECTURA TÉCNICA

### 2.1 Stack Tecnológico

#### **Backend (Python)**
```
chatita-local/
├── chatita-mail/
│   ├── core/
│   │   ├── account_manager.py      # Multi-account orchestration
│   │   ├── imap_client.py          # IMAP protocol layer
│   │   ├── smtp_client.py          # SMTP protocol layer
│   │   └── sync_engine.py          # Real-time sync state machine
│   ├── ai/
│   │   ├── classifier.py           # Email categorization (HF + embeddings)
│   │   ├── priority_scorer.py      # Urgency/importance scoring
│   │   ├── draft_generator.py      # AI reply generation (fine-tuned)
│   │   ├── summarizer.py           # Thread summarization
│   │   └── voice_matcher.py        # Style transfer to match user's voice
│   ├── storage/
│   │   ├── message_repo.py         # PostgreSQL repository
│   │   ├── vector_store.py         # Embeddings for semantic search
│   │   └── cache.py                # Redis for real-time state
│   ├── api/
│   │   ├── rest_api.py             # FastAPI endpoints
│   │   └── websocket.py            # Real-time updates to frontend
│   └── agent/
│       ├── autonomous_agent.py     # Chatita Mail Agent (cron-based)
│       └── briefing_generator.py   # Daily digest creation
```

#### **Frontend (React + TypeScript)**
```
chatita-mail-ui/
├── src/
│   ├── components/
│   │   ├── InboxView.tsx           # Main inbox with priority lanes
│   │   ├── EmailThread.tsx         # Thread view with AI summaries
│   │   ├── ComposeWindow.tsx       # Compose with AI assist
│   │   ├── SmartReplies.tsx        # 1-click reply suggestions
│   │   └── AgentDashboard.tsx      # Autonomous agent controls
│   ├── hooks/
│   │   ├── useRealtimeSync.ts      # WebSocket connection
│   │   └── useAIDrafts.ts          # AI draft generation hook
│   └── services/
│       ├── api.ts                  # Backend API client
│       └── websocket.ts            # WebSocket manager
```

#### **Database Schema (PostgreSQL)**
```sql
-- Accounts
CREATE TABLE email_accounts (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    provider VARCHAR(50),  -- 'gmail', 'icloud', 'imap'
    email_address VARCHAR(255) UNIQUE,
    imap_config JSONB,
    smtp_config JSONB,
    sync_state JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    account_id UUID REFERENCES email_accounts(id),
    message_uid VARCHAR(255),  -- IMAP UID
    mailbox VARCHAR(255),      -- INBOX, Sent, Archive, etc.
    thread_id UUID,
    from_addr VARCHAR(255),
    to_addrs TEXT[],
    cc_addrs TEXT[],
    subject TEXT,
    body_text TEXT,
    body_html TEXT,
    received_at TIMESTAMPTZ,
    flags TEXT[],              -- \Seen, \Flagged, etc.
    
    -- AI-generated metadata
    category VARCHAR(50),      -- work, personal, transactional, marketing
    priority_score INT,        -- 0-100
    intent VARCHAR(50),        -- action_required, fyi, calendar, invoice
    sentiment VARCHAR(50),     -- neutral, urgent, angry, question
    ai_summary TEXT,
    action_items TEXT[],
    
    -- Embeddings for semantic search
    embedding vector(1024),    -- BGE-M3 embeddings
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_messages_account ON messages(account_id);
CREATE INDEX idx_messages_thread ON messages(thread_id);
CREATE INDEX idx_messages_priority ON messages(priority_score DESC);
CREATE INDEX idx_messages_category ON messages(category);
CREATE INDEX idx_messages_embedding ON messages USING ivfflat (embedding vector_cosine_ops);

-- Drafts (AI-generated)
CREATE TABLE ai_drafts (
    id UUID PRIMARY KEY,
    message_id UUID REFERENCES messages(id),
    draft_text TEXT,
    confidence_score FLOAT,  -- 0-1, how confident AI is
    user_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User writing style profile
CREATE TABLE writing_style_profile (
    user_id UUID PRIMARY KEY,
    avg_email_length INT,
    common_phrases TEXT[],
    tone_formal_casual_ratio FLOAT,
    signature TEXT,
    language_preference VARCHAR(10),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent activity log
CREATE TABLE agent_activity_log (
    id UUID PRIMARY KEY,
    account_id UUID REFERENCES email_accounts(id),
    action_type VARCHAR(50),  -- 'auto_archive', 'draft_reply', 'send_briefing'
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.2 Arquitectura de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    CHATITA MAIL FRONTEND                     │
│  (React App embebida en chatita.ai/mail)                    │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Priority │  │  Thread  │  │ Compose  │  │  Agent   │   │
│  │  Inbox   │  │   View   │  │  + AI    │  │Dashboard │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│         │              │              │              │      │
│         └──────────────┴──────────────┴──────────────┘      │
│                        │                                     │
│                   WebSocket + REST API                       │
└────────────────────────┼────────────────────────────────────┘
                         │
┌────────────────────────┼────────────────────────────────────┐
│              CHATITA MAIL BACKEND (Python)                   │
│                        │                                     │
│  ┌─────────────────────┴──────────────────────────────┐    │
│  │              API Layer (FastAPI)                     │    │
│  │  /api/mail/accounts, /messages, /drafts, /search   │    │
│  └─────────────────────┬──────────────────────────────┘    │
│                        │                                     │
│  ┌────────────────────┴─────────────────────────────────┐  │
│  │           Account Manager (Multi-Account)             │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │  │
│  │  │ Gmail    │  │ iCloud   │  │ IMAP     │           │  │
│  │  │ Account  │  │ Account  │  │ Generic  │           │  │
│  │  └──────────┘  └──────────┘  └──────────┘           │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│  ┌────────────────────┴─────────────────────────────────┐  │
│  │              Sync Engine (State Machine)              │  │
│  │  - IMAP IDLE for real-time updates                    │  │
│  │  - Incremental UID-based sync                         │  │
│  │  - Conflict resolution (server = source of truth)     │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│  ┌────────────────────┴─────────────────────────────────┐  │
│  │                 AI Pipeline                            │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │ 1. Classifier (category, intent, sentiment)  │    │  │
│  │  │    - HF zero-shot (facebook/bart-large-mnli) │    │  │
│  │  │    - Fine-tuned on user's email history      │    │  │
│  │  └──────────────────────────────────────────────┘    │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │ 2. Priority Scorer (urgency + importance)    │    │  │
│  │  │    - Sender history analysis                  │    │  │
│  │  │    - Content NLP (deadlines, questions)      │    │  │
│  │  │    - Thread context                           │    │  │
│  │  └──────────────────────────────────────────────┘    │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │ 3. Draft Generator (AI replies)               │    │  │
│  │  │    - Together.ai Llama-3.3-70B base          │    │  │
│  │  │    - Fine-tuned LoRA on user's sent emails   │    │  │
│  │  │    - Voice matching (tone, length, phrases)  │    │  │
│  │  └──────────────────────────────────────────────┘    │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │ 4. Summarizer (thread summaries)              │    │  │
│  │  │    - HF summarization model                   │    │  │
│  │  │    - Action item extraction                   │    │  │
│  │  └──────────────────────────────────────────────┘    │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │ 5. Embeddings (semantic search)               │    │  │
│  │  │    - BAAI/bge-m3 (1024 dims, multilingual)   │    │  │
│  │  │    - Stored in PostgreSQL with pgvector      │    │  │
│  │  └──────────────────────────────────────────────┘    │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│  ┌────────────────────┴─────────────────────────────────┐  │
│  │         Autonomous Agent (Cron-based)                 │  │
│  │  - Runs every hour                                    │  │
│  │  - Auto-archive low-priority emails                   │  │
│  │  - Generate drafts for routine emails                 │  │
│  │  - Daily briefing at 7:00 AM                          │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│  ┌────────────────────┴─────────────────────────────────┐  │
│  │              Storage Layer                             │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │  │
│  │  │ PostgreSQL   │  │ Redis Cache  │  │ S3 (attach│  │  │
│  │  │ (messages,   │  │ (sync state, │  │ments)     │  │  │
│  │  │  threads,    │  │  sessions)   │  │           │  │  │
│  │  │  embeddings) │  │              │  │           │  │  │
│  │  └──────────────┘  └──────────────┘  └───────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                         │
                         │ IMAP/SMTP
                         │
┌────────────────────────┴────────────────────────────────────┐
│                  EMAIL SERVERS                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Gmail        │  │ iCloud Mail  │  │ Any IMAP     │     │
│  │ (IMAP/SMTP)  │  │ (IMAP/SMTP)  │  │ Server       │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

### 2.3 Flujo de Datos — Email Lifecycle

#### **Flujo 1: Email Entrante (Incoming)**
```
1. IMAP Server → Sync Engine (IDLE notification o polling cada 30s)
2. Sync Engine → Download email (headers first, body on-demand)
3. Message Repo → Store in PostgreSQL
4. AI Pipeline (async):
   a. Classifier → category, intent, sentiment
   b. Priority Scorer → urgency score 0-100
   c. Embeddings Generator → vector for semantic search
   d. Summarizer (if thread >3 emails) → summary + action items
   e. Draft Generator (if action_required) → proactive draft
5. WebSocket → Push update to frontend (real-time)
6. Frontend → Display in appropriate inbox lane (Priority, Work, Personal, etc.)
```

#### **Flujo 2: Usuario Compone Email (Outgoing)**
```
1. Frontend → User types in Compose Window
2. AI Assist (real-time):
   a. Grammar check (on-demand)
   b. Tone suggestions (formal/casual toggle)
   c. "Help me write" → full draft generation
3. User → Clicks Send
4. SMTP Client → Submit to mail server
5. IMAP Client → Move to Sent folder (via IMAP APPEND)
6. Writing Style Profiler → Update user's style model (async)
```

#### **Flujo 3: Agente Autónomo (Hourly)**
```
1. Cron → Trigger autonomous_agent.py every hour
2. Agent → Fetch new emails since last run
3. For each email:
   a. If priority_score < 20 AND category='marketing' → Auto-archive
   b. If priority_score < 30 AND category='notifications' → Bundle in digest
   c. If intent='action_required' AND confidence>0.8 → Generate draft
   d. If sender in VIP list → Flag for immediate attention
4. Agent → Generate daily briefing (if 7:00 AM):
   - Top 5 priority emails
   - Pending action items
   - Calendar conflicts detected
5. Agent → Send briefing via Telegram to Manny
```

### 2.4 Integración con Chatita AI

**Chatita Mail NO es una aplicación standalone** — es una extensión del ecosistema Chatita AI:

```javascript
// chatita-local/tools/hub-mail.js

const TOOLS = [
  {
    name: 'chatita_mail_check_inbox',
    description: 'Check priority inbox and get top N important emails',
    parameters: { limit: 'number', account: 'string' }
  },
  {
    name: 'chatita_mail_search',
    description: 'Semantic search across all emails in natural language',
    parameters: { query: 'string', account: 'string', limit: 'number' }
  },
  {
    name: 'chatita_mail_draft_reply',
    description: 'Generate AI draft reply for a specific email',
    parameters: { message_id: 'string', context: 'string' }
  },
  {
    name: 'chatita_mail_send',
    description: 'Send email on behalf of user',
    parameters: { to: 'string', subject: 'string', body: 'string', account: 'string' }
  },
  {
    name: 'chatita_mail_summarize_thread',
    description: 'Get AI summary of an email thread',
    parameters: { thread_id: 'string' }
  },
  {
    name: 'chatita_mail_auto_archive',
    description: 'Auto-archive emails matching criteria',
    parameters: { criteria: 'object' }
  }
];
```

**Ejemplo de uso conversacional:**

```
Manny: "Chatita, ¿tengo algo importante en mi email?"

Chatita: [llama chatita_mail_check_inbox(limit=5)]
"Sí, tienes 3 emails importantes:
1. Laura Chen - Design Review moved to Thursday (urgente)
2. Mike Torres - Sprint planning agenda (requiere acción)
3. Cliente ABC - Propuesta de renovación (deadline viernes)

¿Quieres que te ayude a responder alguno?"

Manny: "Sí, responde a Laura confirmando que estoy disponible el jueves"

Chatita: [llama chatita_mail_draft_reply(message_id=..., context="confirmar disponibilidad jueves")]
"Aquí está el borrador:

'Hi Laura,

Thanks for the heads up. Thursday at 2pm works perfectly for me. I'll review the design materials beforehand.

See you then,
Manny'

¿Lo envío o quieres que lo ajuste?"
```

---

## PARTE 3: FEATURES DETALLADAS

### 3.1 Priority Inbox — Algoritmo de Scoring

```python
# chatita-mail/ai/priority_scorer.py

def calculate_priority_score(message: Message, user_profile: UserProfile) -> int:
    """
    Returns priority score 0-100.
    
    Factors:
    - Sender importance (40 points)
    - Content urgency (30 points)
    - Thread context (20 points)
    - Timing (10 points)
    """
    score = 0
    
    # 1. Sender importance (0-40 points)
    sender = message.from_addr
    if sender in user_profile.vip_senders:
        score += 40
    elif sender in user_profile.frequent_contacts:
        score += 30
    elif sender in user_profile.team_domain:
        score += 20
    elif is_first_time_sender(sender):
        score += 5  # New senders get low priority by default
    
    # 2. Content urgency (0-30 points)
    urgency_keywords = {
        'urgent': 30, 'asap': 30, 'critical': 30,
        'deadline': 25, 'today': 25, 'tomorrow': 20,
        'important': 15, 'please review': 15,
        'fyi': 5, 'update': 5
    }
    
    body_lower = message.body_text.lower()
    for keyword, points in urgency_keywords.items():
        if keyword in body_lower:
            score += points
            break  # Only count highest urgency keyword
    
    # Sentiment analysis
    sentiment = analyze_sentiment(message.body_text)
    if sentiment == 'angry' or sentiment == 'complaint':
        score += 25
    elif sentiment == 'question':
        score += 15
    
    # 3. Thread context (0-20 points)
    if message.thread_id:
        thread = get_thread(message.thread_id)
        if thread.user_participated:  # User already replied in this thread
            score += 20
        elif thread.message_count > 5:  # Long ongoing conversation
            score += 15
    
    # 4. Timing (0-10 points)
    if has_deadline_mention(message.body_text):
        deadline = extract_deadline(message.body_text)
        days_until = (deadline - datetime.now()).days
        if days_until <= 1:
            score += 10
        elif days_until <= 3:
            score += 7
        elif days_until <= 7:
            score += 5
    
    return min(score, 100)  # Cap at 100
```

### 3.2 AI Draft Generator — Voice Matching

```python
# chatita-mail/ai/draft_generator.py

class DraftGenerator:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.style_profile = load_writing_style_profile(user_id)
        self.base_model = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
        self.lora_adapter = f"chatita-mail-{user_id}-voice"  # Fine-tuned LoRA
    
    def generate_draft(self, message: Message, context: str = None) -> str:
        """
        Generate reply draft that matches user's writing style.
        """
        # Build prompt with style constraints
        prompt = self._build_prompt(message, context)
        
        # Generate with Together.ai
        response = together_client.chat.completions.create(
            model=self.base_model,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        draft = response.choices[0].message.content
        
        # Post-process to match style
        draft = self._apply_style_transfer(draft)
        
        return draft
    
    def _get_system_prompt(self) -> str:
        """Build system prompt from user's writing style profile."""
        return f"""You are writing an email reply on behalf of {self.style_profile.name}.

Writing style guidelines:
- Average email length: {self.style_profile.avg_email_length} words
- Tone: {self.style_profile.tone_description}
- Common phrases: {', '.join(self.style_profile.common_phrases[:5])}
- Signature: {self.style_profile.signature}
- Language: {self.style_profile.language_preference}

Write a reply that sounds exactly like {self.style_profile.name} would write it.
Be natural, authentic, and match their voice perfectly."""
    
    def _build_prompt(self, message: Message, context: str) -> str:
        """Build the actual prompt for draft generation."""
        thread_context = ""
        if message.thread_id:
            thread = get_thread(message.thread_id)
            thread_context = f"\n\nThread history:\n{thread.get_summary()}"
        
        user_context = f"\n\nAdditional context: {context}" if context else ""
        
        return f"""Original email:
From: {message.from_addr}
Subject: {message.subject}

{message.body_text}
{thread_context}
{user_context}

Write a reply to this email."""
    
    def _apply_style_transfer(self, draft: str) -> str:
        """Fine-tune draft to match exact style patterns."""
        # Replace generic greetings with user's preferred ones
        for generic, preferred in self.style_profile.greeting_replacements.items():
            draft = draft.replace(generic, preferred)
        
        # Adjust formality level
        if self.style_profile.formality_score < 0.3:  # Very casual
            draft = draft.replace("I would like to", "I'd like to")
            draft = draft.replace("I am", "I'm")
        
        # Add signature if not present
        if self.style_profile.signature not in draft:
            draft += f"\n\n{self.style_profile.signature}"
        
        return draft
```

### 3.3 Autonomous Agent — Daily Briefing

```python
# chatita-mail/agent/briefing_generator.py

class BriefingGenerator:
    def generate_daily_briefing(self, user_id: str) -> str:
        """
        Generate morning briefing with top priority items.
        Sent via Telegram at 7:00 AM.
        """
        # Get yesterday's activity
        yesterday = datetime.now() - timedelta(days=1)
        
        # Fetch priority emails
        priority_emails = get_messages(
            user_id=user_id,
            received_after=yesterday,
            priority_score_min=70,
            limit=10
        )
        
        # Fetch pending action items
        action_items = get_messages(
            user_id=user_id,
            intent='action_required',
            flags__not_contains='\\Seen',
            limit=5
        )
        
        # Check calendar conflicts
        calendar_conflicts = check_calendar_conflicts(user_id)
        
        # Build briefing
        briefing = f"""🌅 **Good morning, Manny!**

📧 **Email Summary (last 24h)**
- {len(priority_emails)} priority emails
- {count_unread(user_id)} total unread
- {count_auto_archived(user_id, yesterday)} auto-archived (noise)

🔥 **Top Priority (requires attention):**
"""
        
        for i, email in enumerate(priority_emails[:5], 1):
            briefing += f"\n{i}. **{email.from_addr}** — {email.subject}"
            briefing += f"\n   Priority: {email.priority_score}/100 | {email.intent}"
            if email.ai_summary:
                briefing += f"\n   Summary: {email.ai_summary[:100]}..."
        
        if action_items:
            briefing += f"\n\n✅ **Action Items Pending:**\n"
            for item in action_items:
                briefing += f"- {item.subject} (from {item.from_addr})\n"
        
        if calendar_conflicts:
            briefing += f"\n\n⚠️ **Calendar Conflicts Detected:**\n"
            for conflict in calendar_conflicts:
                briefing += f"- {conflict.description}\n"
        
        briefing += f"\n\n💡 **AI Suggestions:**\n"
        briefing += self._generate_suggestions(priority_emails, action_items)
        
        briefing += f"\n\n🤖 I've auto-archived {count_auto_archived(user_id, yesterday)} low-priority emails."
        briefing += f"\n\nReady to tackle the day? 💪"
        
        return briefing
    
    def _generate_suggestions(self, priority_emails, action_items) -> str:
        """Generate AI suggestions based on inbox state."""
        suggestions = []
        
        # Suggest batch processing similar emails
        grouped = group_by_sender(priority_emails)
        for sender, emails in grouped.items():
            if len(emails) >= 3:
                suggestions.append(
                    f"- You have {len(emails)} emails from {sender}. "
                    f"Want me to summarize them together?"
                )
        
        # Suggest follow-ups
        overdue = get_overdue_followups(action_items)
        if overdue:
            suggestions.append(
                f"- {len(overdue)} emails need follow-up. "
                f"Should I draft replies?"
            )
        
        return "\n".join(suggestions) if suggestions else "- Inbox looks good! 👍"
```

---

## PARTE 4: ROADMAP DE IMPLEMENTACIÓN

### Fase 1: Foundation (Semana 1-2) ✅ CRÍTICO
**Objetivo:** Conectividad básica multi-cuenta + storage

- [ ] Setup PostgreSQL schema (messages, accounts, drafts)
- [ ] Implementar `imap_client.py` con soporte Gmail + iCloud
  - Gmail: OAuth2 + IMAP
  - iCloud: App-specific password + IMAP
- [ ] Implementar `smtp_client.py` para envío
- [ ] `account_manager.py` — multi-account orchestration
- [ ] `sync_engine.py` — IMAP IDLE + incremental sync
- [ ] Basic REST API (FastAPI):
  - `GET /api/mail/accounts` — list accounts
  - `GET /api/mail/messages` — list messages
  - `POST /api/mail/send` — send email
- [ ] **Testing:** Conectar cuenta Gmail + iCloud de Manny, sync 100 emails

**Entregable:** Backend funcional que puede leer/enviar emails de ambas cuentas

### Fase 2: AI Classification (Semana 3) 🧠
**Objetivo:** Clasificación inteligente + priority scoring

- [ ] `classifier.py`:
  - Integrar HF `facebook/bart-large-mnli` para zero-shot classification
  - Categories: work, personal, transactional, marketing, notifications
  - Intent: action_required, fyi, calendar, invoice, question
  - Sentiment: neutral, urgent, angry, complaint, question
- [ ] `priority_scorer.py`:
  - Implementar algoritmo de scoring (sender + content + thread + timing)
  - Build user profile from historical data
- [ ] `vector_store.py`:
  - Integrar BAAI/bge-m3 embeddings
  - Setup pgvector index
- [ ] Batch process: Clasificar todos los emails existentes de Manny
- [ ] **Testing:** Verificar que emails importantes tienen score >70

**Entregable:** Todos los emails clasificados y priorizados automáticamente

### Fase 3: AI Drafts & Voice Matching (Semana 4) ✍️
**Objetivo:** Generación de respuestas en la voz de Manny

- [ ] Analizar últimos 1000 emails enviados por Manny:
  - Extraer patrones de estilo (longitud, tono, frases comunes)
  - Build `writing_style_profile`
- [ ] `draft_generator.py`:
  - Integrar Together.ai Llama-3.3-70B
  - Implementar voice matching
  - Proactive draft generation para emails con intent='action_required'
- [ ] `summarizer.py`:
  - Thread summarization
  - Action item extraction
- [ ] API endpoints:
  - `POST /api/mail/drafts/generate` — generate draft
  - `GET /api/mail/threads/{id}/summary` — get summary
- [ ] **Testing:** Generar 10 drafts, que Manny valide si suenan como él

**Entregable:** AI que escribe emails que suenan exactamente como Manny

### Fase 4: Frontend MVP (Semana 5-6) 🎨
**Objetivo:** Interfaz web funcional embebida en chatita.ai

- [ ] Setup React app en `chatita-local/public/mail/`
- [ ] Components:
  - `InboxView.tsx` — Priority lanes (Urgent, Important, Normal, Low)
  - `EmailThread.tsx` — Thread view con AI summary
  - `ComposeWindow.tsx` — Compose con AI assist
  - `SmartReplies.tsx` — 1-click replies
- [ ] WebSocket integration para real-time updates
- [ ] Responsive design (desktop + mobile)
- [ ] **Embedding en chatita.ai:**
  - Agregar link en dashboard: "📧 Mail"
  - iframe embed de `/mail/` app
- [ ] **Testing:** Manny usa la app para leer/responder 20 emails

**Entregable:** UI funcional donde Manny puede gestionar su email

### Fase 5: Autonomous Agent (Semana 7) 🤖
**Objetivo:** Chatita maneja inbox automáticamente

- [ ] `autonomous_agent.py`:
  - Cron job cada hora
  - Auto-archive low-priority (score <20)
  - Bundle notifications
  - Generate proactive drafts
- [ ] `briefing_generator.py`:
  - Daily briefing at 7:00 AM
  - Send via Telegram
- [ ] Agent dashboard en frontend:
  - Ver actividad del agente
  - Configurar reglas (qué auto-archivar, qué no)
  - Aprobar/rechazar drafts generados
- [ ] **Testing:** Dejar agente corriendo 1 semana, medir reducción de tiempo

**Entregable:** Agente autónomo que reduce inbox de Manny en 70%+

### Fase 6: Advanced Features (Semana 8+) 🚀
**Objetivo:** Features avanzadas para superar competencia

- [ ] Semantic search en lenguaje natural
- [ ] Calendar integration (parse meeting requests, suggest times)
- [ ] Gatekeeper (nuevos senders requieren aprobación)
- [ ] Bulk actions (archive all from sender, unsubscribe)
- [ ] Email templates con variables
- [ ] Scheduled send
- [ ] Read receipts tracking
- [ ] Mobile app (React Native)

---

## PARTE 5: MÉTRICAS DE ÉXITO

### KPIs Principales

| Métrica | Baseline (Actual) | Target (3 meses) |
|---------|-------------------|------------------|
| **Tiempo diario en email** | 2-3 horas | <30 minutos |
| **Emails leídos/día** | ~100-150 | ~20-30 (solo importantes) |
| **% Auto-archived** | 0% | 70%+ |
| **Tiempo promedio de respuesta** | 24-48 horas | <4 horas (para importantes) |
| **Inbox Zero frecuencia** | Nunca | Diario |
| **Satisfacción con AI drafts** | N/A | >80% usables sin edición |

### Métricas de AI Performance

| Modelo | Métrica | Target |
|--------|---------|--------|
| **Classifier** | Accuracy | >90% |
| **Priority Scorer** | Precision@10 | >85% (top 10 son realmente importantes) |
| **Draft Generator** | User approval rate | >80% |
| **Summarizer** | ROUGE-L | >0.6 |
| **Embeddings Search** | Recall@5 | >90% |

---

## PARTE 6: COSTOS & ROI

### Costos Operacionales (Mensual)

| Componente | Costo |
|------------|-------|
| **Together.ai API** (draft generation) | ~$15/mes (estimado 500 drafts/mes) |
| **HuggingFace Inference** (classification, embeddings) | GRATIS (tier gratuito) |
| **PostgreSQL** (Supabase o self-hosted) | $0 (self-hosted en M5) |
| **Redis** | $0 (self-hosted) |
| **S3 Storage** (attachments) | ~$5/mes (50GB) |
| **Compute** (backend Python) | $0 (corre en M5 existente) |
| **TOTAL** | **~$20/mes** |

### ROI Calculation

**Valor del tiempo de Manny:**
- Asumiendo $200/hora (conservador para CEO/founder)
- Ahorro de tiempo: 2 horas/día → 30 min/día = **1.5 horas/día**
- **Ahorro mensual:** 1.5h × 22 días × $200 = **$6,600/mes**

**ROI:** ($6,600 - $20) / $20 = **32,900% ROI** 🚀

Incluso si el valor del tiempo es $50/hora:
- Ahorro: 1.5h × 22 × $50 = $1,650/mes
- ROI: ($1,650 - $20) / $20 = **8,150% ROI**

**Conclusión:** Chatita Mail se paga solo en <1 día de uso.

---

## PARTE 7: SEGURIDAD & PRIVACIDAD

### Principios de Seguridad

1. **Credentials Storage**
   - App-specific passwords almacenados en PostgreSQL encriptados (AES-256)
   - OAuth tokens en Redis con TTL
   - NUNCA almacenar contraseñas reales de Apple ID / Google

2. **Data Encryption**
   - TLS 1.3 para todas las conexiones IMAP/SMTP
   - Database encryption at rest
   - Email bodies encriptados en storage (opcional, para máxima privacidad)

3. **Access Control**
   - Solo Manny tiene acceso a sus emails
   - Chatita AI tiene acceso READ-ONLY (no puede enviar sin aprobación)
   - Autonomous agent tiene whitelist de acciones permitidas

4. **Privacy**
   - Emails NUNCA salen del servidor de Manny (M5 o Chatita server)
   - AI models corren local o vía APIs con zero data retention
   - No third-party analytics
   - No email content sharing con terceros

5. **Audit Log**
   - Todas las acciones del agente autónomo se loggean
   - Manny puede revisar qué hizo el agente en cualquier momento

---

## CONCLUSIÓN

**Chatita Mail** no es solo otra aplicación de email — es un **agente AI autónomo** que trabaja 24/7 para eliminar el ruido y maximizar la productividad de Manny.

### Ventajas Competitivas Únicas

1. ✅ **Integración nativa con Chatita AI** — conversacional, no solo UI
2. ✅ **Agente autónomo real** — no solo "smart inbox", sino gestión activa
3. ✅ **Voice matching perfecto** — AI que escribe exactamente como Manny
4. ✅ **Multi-cuenta universal** — Gmail + iCloud + cualquier IMAP
5. ✅ **Costo $0** — parte del ecosistema Chatita, no SaaS separado
6. ✅ **Privacy-first** — data nunca sale de los servidores de Manny

### Next Steps

1. **Aprobación de arquitectura** — Manny revisa este documento
2. **Priorización de features** — ¿Qué fases son P0?
3. **Inicio de desarrollo** — Fase 1 (Foundation) en próximos 7 días
4. **Iteración con feedback** — Manny prueba cada fase y ajustamos

**Estimado de tiempo total:** 8 semanas para MVP completo funcional.

**¿Procedemos con la implementación?** 🚀

