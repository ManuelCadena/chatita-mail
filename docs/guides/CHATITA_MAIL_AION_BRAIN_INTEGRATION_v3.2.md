# Chatita Mail — AION Brain v3.2 Integration Guide
**Complete Integration with Production AION Brain Repository**

**Author**: Manuel Cadena  
**Date**: 22-Jul-2026  
**Version**: 3.2 (Updated from GitHub repo)  
**Repo**: https://github.com/ManuelCadena/aion-brain

---

## 🎯 AION BRAIN v3.2 — PRODUCTION READY

### Estado Actual
- ✅ **Versión**: 3.2.0 (21-Jul-2026)
- ✅ **Status**: Production Ready
- ✅ **Deployments**: 5+ sistemas en producción
- ✅ **Validación**: R² = 0.9746, N=100, p < 0.0001
- ✅ **Ahorro validado**: 68-93% (promedio 68.7%)

---

## 📊 CAPACIDADES COMPLETAS

### 1. LLM PROVIDERS (11 Total)

| Provider | Modelos | Costo/1M Input | Contexto | Especialidad | API Key |
|----------|---------|----------------|----------|--------------|---------|
| **Together.ai** | Llama 3.3 70B, Qwen 72B | $0.18-$1.20 | 131K | Budget, Open Source | `TOGETHER_API_KEY` |
| **DeepSeek** | Chat, Coder, Reasoner | $0.14-$2.19 | 64K | Math, Code (99% cheaper) | `DEEPSEEK_API_KEY` |
| **HuggingFace** | BGE-M3, BART, FinBERT, MEL | **$0 (GRATIS)** | 8K | Embeddings, NER, Classification | `HF_TOKEN` |
| **Cohere** | Command R+, Command A | $0.15-$3.00 | 128K | RAG, Enterprise | `COHERE_API_KEY` |
| **Perplexity** | Sonar Pro, Sonar Reasoning | $1-$5 | 127K | Web Search (real-time) | `PERPLEXITY_API_KEY` |
| **Google Gemini** | Gemini 1.5 Pro, 2.0 Flash | $1.25-$5 | **1M** | Long Context | `GEMINI_API_KEY` |
| **Mistral** | Mistral Large, Codestral, Pixtral | $2-$6 | 128K | EU-compliant, Code, Vision | `MISTRAL_API_KEY` |
| **OpenAI** | GPT-4o, GPT-4o-mini, o1, o3 | $2.50-$15 | 128K | General, Vision | `OPENAI_API_KEY` |
| **Anthropic** | Claude Opus 4, Sonnet 4 | $3-$15 | 200K | Reasoning, Safety | `ANTHROPIC_API_KEY` |
| **xAI** | Grok-3, Grok-3-mini | $3-$15 | 128K | X/Twitter Data | `XAI_API_KEY` |
| **Replicate** | 1000+ modelos | $0.001/sec | 4K | Custom Models | `REPLICATE_API_TOKEN` |

---

### 2. TASK ROUTING (17 Tipos)

```javascript
// ROUTING AUTOMÁTICO POR TIPO DE TAREA

// ── Cost-Optimized ──────────────────────────────────
simple          → Together Llama-3.3      // $0.18/1M (98% savings)
budget          → DeepSeek Chat           // $0.14/1M (99% savings)
ultra_budget    → Cohere Command-R7B      // $0.15/1M

// ── Quality-Optimized ───────────────────────────────
medium          → GPT-4o Mini             // $0.15/1M
complex         → Claude Sonnet 4         // $3/1M
critical        → Claude Opus 4           // $15/1M (máxima calidad)

// ── Specialized Tasks ───────────────────────────────
search          → Perplexity Sonar Pro    // Real-time web + citations
reasoning       → xAI Grok-3              // X/Twitter intelligence
math            → DeepSeek Reasoner       // Math/science
long_context    → Gemini 1.5 Pro          // 1M token context
code            → DeepSeek Coder          // Programming
code_mistral    → Mistral Codestral       // EU-compliant code
vision          → GPT-4o / Gemini / Pixtral // Images

// ── Free Tier (HuggingFace) ────────────────────────
embedding       → HuggingFace BGE-M3      // Free embeddings
classification  → HuggingFace BART-MNLI   // Free zero-shot
ner_legal       → HuggingFace MEL         // Free legal NER (ES)
sentiment_fin   → HuggingFace FinBERT     // Free financial sentiment

// ── Enterprise ──────────────────────────────────────
rag             → Cohere Command-R+       // Grounded RAG
enterprise      → Cohere Command-A        // Enterprise scale
```

---

### 3. SERVICIOS ADICIONALES (91+ Total)

#### 3.1 Vision & Image (8 servicios)

| Servicio | Capacidad | API Key | Uso en Chatita Mail |
|----------|-----------|---------|---------------------|
| **fal.ai** | FLUX, SD 3.5, Kling | `FAL_API_KEY` | Generación de imágenes para emails |
| **Stability AI** | SDXL, SD3 | `STABILITY_AI_KEY` | Generación de imágenes |
| **BFL** | Flux Pro | `BFL_API_KEY` | Imágenes alta calidad |
| **Hume AI** | Emotion detection | `HUME_API_KEY` | **Detectar emociones en fotos de perfil** |
| **Plant.ID** | Plant identification | `PLANT_ID_API_KEY` | Identificar plantas en attachments |
| **D-ID** | Face animation | `DID_API_KEY` | Animar avatares |
| **Google Vision** | OCR, labels | `GOOGLE_API_KEY` | **OCR en attachments** |
| **OpenAI Vision** | GPT-4o vision | `OPENAI_API_KEY` | **Análisis de imágenes adjuntas** |

**Casos de uso en Chatita Mail:**
- ✅ OCR de screenshots adjuntos
- ✅ Análisis de facturas/invoices en imágenes
- ✅ Detección de emociones en fotos de perfil
- ✅ Extracción de texto de documentos escaneados

---

#### 3.2 Video Services (5 servicios)

| Servicio | Capacidad | API Key | Uso en Chatita Mail |
|----------|-----------|---------|---------------------|
| **HeyGen** | AI avatars | `HEYGEN_API_KEY` | **Video replies con avatar** |
| **Runway** | Gen-3 video | `RUNWAY_API_KEY` | Generación de videos |
| **Synthesia** | Video generation | `SYNTHESIA_API_KEY` | Videos corporativos |
| **D-ID** | Lip-sync | `DID_API_KEY` | Sincronización labial |
| **fal.ai/Kling** | Text-to-video | `FAL_API_KEY` | Texto a video |

**Casos de uso en Chatita Mail:**
- ✅ Respuestas en video con avatar de Manny
- ✅ Análisis de videos adjuntos
- ✅ Generación de video briefings

---

#### 3.3 Audio Services (8 servicios)

| Servicio | Capacidad | API Key | Uso en Chatita Mail |
|----------|-----------|---------|---------------------|
| **ElevenLabs** | TTS, voice cloning | `ELEVENLABS_API_KEY` | **Audio briefings con voz de Manny** |
| **Deepgram** | STT streaming | `DEEPGRAM_API_KEY` | Transcripción en tiempo real |
| **AssemblyAI** | Speaker diarization | `ASSEMBLYAI_API_KEY` | Identificar speakers en audio |
| **OpenAI Whisper** | Transcription | `OPENAI_API_KEY` | **Transcribir notas de voz** |
| **OpenAI TTS** | Text-to-speech | `OPENAI_API_KEY` | TTS alternativo |
| **Google STT** | Speech-to-text | `GOOGLE_API_KEY` | STT alternativo |
| **Google TTS** | Text-to-speech | `GOOGLE_API_KEY` | TTS alternativo |
| **Hume Voice** | Emotion in speech | `HUME_API_KEY` | **Detectar emociones en voz** |

**Casos de uso en Chatita Mail:**
- ✅ Transcribir notas de voz adjuntas
- ✅ Detectar frustración/urgencia en audio
- ✅ Generar audio briefings diarios
- ✅ Voice replies automáticos

---

#### 3.4 Corporate Intelligence (8+ servicios)

| Servicio | Capacidad | API Key | Uso en Chatita Mail |
|----------|-----------|---------|---------------------|
| **LibreBOR** | Registro Mercantil ES | `LIBREBOR_API_KEY` | Verificar empresas españolas |
| **EInforma** | Empresas ES | `EINFORMA_API_KEY` | Due diligence España |
| **OpenCorporates** | Empresas globales | Gratis | Verificar senders corporativos |
| **ICIJ** | Offshore Leaks | Gratis | Detectar offshore entities |
| **SEC EDGAR** | Empresas US | Gratis | Verificar empresas públicas US |
| **Companies House** | Empresas UK | Gratis | Verificar empresas UK |
| **CNBV** | Instituciones MX | Gratis | Verificar bancos/financieras MX |
| **Banxico** | Datos económicos MX | `BANXICO_TOKEN` | Contexto económico MX |

**Casos de uso en Chatita Mail:**
- ✅ Verificar legitimidad de sender corporativo
- ✅ Enriquecer contexto con datos de empresa
- ✅ Detectar red flags (offshore, sanciones)
- ✅ Auto-research de empresas mencionadas

---

#### 3.5 Government APIs (25+ servicios — TODOS GRATIS)

| Agencia | Datos | API Key | Uso en Chatita Mail |
|---------|-------|---------|---------------------|
| **FRED** | Economía US | `FRED_API_KEY` | Contexto económico |
| **BLS** | Empleo US | `BLS_API_KEY` | Datos de empleo |
| **Census** | Demografía US | `CENSUS_API_KEY` | Datos demográficos |
| **NASA** | Espacio, clima | `NASA_API_KEY` | Imágenes, datos científicos |
| **USDA** | Agricultura | `USDA_API_KEY` | Datos agrícolas |
| **OpenFDA** | Medicamentos | Gratis | Verificar medicamentos |
| **PubMed** | Research papers | Gratis | Buscar papers académicos |
| **NIH** | Salud | Gratis | Datos de salud |
| **SEC EDGAR** | Finanzas | Gratis | Reportes corporativos |
| **USPTO** | Patentes | Gratis | Buscar patentes |
| **Weather.gov** | Clima US | Gratis | Pronóstico clima |
| **USGS** | Terremotos, agua | Gratis | Datos geológicos |
| **Banxico** | Economía MX | `BANXICO_TOKEN` | Tipo de cambio, inflación |
| **INEGI** | Estadísticas MX | `INEGI_TOKEN` | Datos México |

**Casos de uso en Chatita Mail:**
- ✅ Enriquecer contexto con datos oficiales
- ✅ Verificar claims en emails (fact-checking)
- ✅ Agregar contexto económico a respuestas
- ✅ Buscar research papers mencionados

---

#### 3.6 Weather & Satellite (7 servicios)

| Servicio | Capacidad | API Key | Uso en Chatita Mail |
|----------|-----------|---------|---------------------|
| **Tomorrow.io** | Pronóstico preciso | `TOMORROW_API_KEY` | Contexto para eventos outdoor |
| **OpenWeather** | Clima global | `OPENWEATHER_API_KEY` | Clima alternativo |
| **Weather.gov** | Clima US oficial | Gratis | Clima US |
| **Sentinel Hub** | Imágenes satelitales | `SENTINEL_HUB_KEY` | Imágenes de ubicaciones |
| **NASA EONET** | Eventos naturales | Gratis | Desastres naturales |
| **USGS Earthquakes** | Terremotos | Gratis | Alertas sísmicas |
| **NOAA** | Océanos, clima | Gratis | Datos oceanográficos |

**Casos de uso en Chatita Mail:**
- ✅ Sugerir cambio de fecha si lluvia
- ✅ Alertar sobre clima adverso
- ✅ Contexto para viajes mencionados

---

#### 3.7 Communication (6 servicios)

| Servicio | Capacidad | API Key | Uso en Chatita Mail |
|----------|-----------|---------|---------------------|
| **Telegram** | Notificaciones | `TELEGRAM_BOT_TOKEN` | **Notificar emails urgentes** |
| **Twilio** | SMS, llamadas | `TWILIO_ACCOUNT_SID` | SMS para urgencias |
| **SendGrid** | Email transaccional | `SENDGRID_API_KEY` | Enviar emails |
| **Slack** | Mensajería | `SLACK_BOT_TOKEN` | Notificar a Slack |
| **Discord** | Webhooks | `DISCORD_WEBHOOK` | Notificar a Discord |
| **WhatsApp** | Mensajería | `WHATSAPP_TOKEN` | WhatsApp notifications |

**Casos de uso en Chatita Mail:**
- ✅ Notificar vía Telegram emails priority >90
- ✅ SMS para emails críticos
- ✅ Integración con Slack teams

---

#### 3.8 Web Automation (3 servicios)

| Servicio | Capacidad | API Key | Uso en Chatita Mail |
|----------|-----------|---------|---------------------|
| **Browserbase** | Browser cloud | `BROWSERBASE_API_KEY` | Scraping de links en emails |
| **Steel** | Browser automation | `STEEL_API_KEY` | Automatización web |
| **Playwright** | Browser control | N/A (local) | Testing, scraping |

**Casos de uso en Chatita Mail:**
- ✅ Preview de links mencionados
- ✅ Scraping de páginas referenciadas
- ✅ Auto-fill de forms mencionados

---

#### 3.9 Computation (5 servicios)

| Servicio | Capacidad | API Key | Uso en Chatita Mail |
|----------|-----------|---------|---------------------|
| **DeepSeek** | Math reasoning | `DEEPSEEK_API_KEY` | Resolver cálculos en emails |
| **Wolfram Alpha** | Symbolic math | `WOLFRAM_APP_ID` | Matemáticas simbólicas |
| **Posit Cloud** | R statistics | `RSCLOUD_CLIENT_ID` | Análisis estadístico |
| **Together** | Embeddings | `TOGETHER_API_KEY` | Embeddings alternativos |
| **HuggingFace** | ML inference | `HF_TOKEN` | Modelos ML gratis |

**Casos de uso en Chatita Mail:**
- ✅ Resolver cálculos mencionados
- ✅ Análisis estadístico de datos
- ✅ Embeddings para semantic search

---

#### 3.10 Research (6 servicios)

| Servicio | Capacidad | API Key | Uso en Chatita Mail |
|----------|-----------|---------|---------------------|
| **Perplexity** | Web search + citations | `PERPLEXITY_API_KEY` | **Buscar info actual** |
| **Brave Search** | Privacy search | `BRAVE_API_KEY` | Búsqueda privada |
| **Serper** | Google search API | `SERPER_API_KEY` | Google search |
| **PubMed** | Medical research | Gratis | Papers médicos |
| **arXiv** | Scientific papers | Gratis | Papers científicos |
| **Semantic Scholar** | Academic search | Gratis | Búsqueda académica |

**Casos de uso en Chatita Mail:**
- ✅ Research de temas mencionados
- ✅ Verificar claims con fuentes
- ✅ Buscar papers referenciados

---

## 🏗️ ARQUITECTURA — 12-LAYER PIPELINE

```
┌─────────────────────────────────────────────────────────────┐
│                    AION BRAIN v3.2                          │
│          Universal AI Orchestration Platform                │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  MCP Server  │    │  HTTP Server │    │   Gateway    │
│   (stdio)    │    │  (port 3100) │    │   (API)      │
└──────────────┘    └──────────────┘    └──────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │         12-LAYER PIPELINE             │
        ├───────────────────────────────────────┤
        │ 1. Gateway (rate limit)               │
        │ 2. Hard Rules                         │
        │ 3. Security Gates (OFAC)              │
        │ 4. Validator                          │
        │ 5. Query Rewriter                     │
        │ 6. Prompt Compiler                    │
        │ 7. CoT Decision Engine                │
        │ 8. Hierarchical Retriever             │
        │ 9. Cost Estimator                     │
        │ 10. Intelligent Router                │
        │ 11. Adaptive Router (LinUCB)          │
        │ 12. LLM Executor + Fallback           │
        └───────────────┬───────────────────────┘
                        │
    ┌───────┬───────┬──┴──┬───────┬───────┬───────┐
    │OpenAI │Anthr. │Toget│Perp.  │Gemini │DeepSeek│ ...11 providers
    └───────┴───────┴─────┴───────┴───────┴───────┘
```

---

## 💰 COST SAVINGS VALIDADOS

### Resultados Experimentales
```
Sample Size: N = 100 tasks
R²: 0.9746
p-value: < 0.0001
Savings: 68.7% average
CI 95%: [62.2%, ∞]
```

### Deployments Reales

| Sistema | Antes | Después | Ahorro |
|---------|-------|---------|--------|
| **CitrusMax AI** (Agriculture) | $450/mo | $42/mo | **90.7%** |
| **NEMESIS OSINT** (Intelligence) | $4,250/mo | $600/mo | **85.9%** |
| **Dev Team (10 developers)** | $2,000/mo | $180/mo | **91%** |
| **Chatita Mail (proyectado)** | $85/mo | **$30/mo** | **65%** |

---

## 🔌 INTEGRACIÓN CON CHATITA MAIL

### Opción 1: MCP Server (RECOMENDADO)

**Configuración en Chatita Mail backend:**

```python
# backend/ai/aion_client.py

import subprocess
import json
import asyncio

class AIONBrainMCPClient:
    """
    Cliente MCP para AION Brain v3.2.
    Comunicación vía stdio con el servidor MCP.
    """
    
    def __init__(self, mcp_server_path='/opt/chatita/aion-brain/mcp-server.js'):
        self.mcp_server_path = mcp_server_path
    
    async def llm_chat(self, provider, messages, model=None, temperature=0.7, max_tokens=4096):
        """
        Chat con cualquier LLM provider vía AION Brain.
        
        Routing automático si provider='auto'.
        """
        request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'tools/call',
            'params': {
                'name': 'llm_chat',
                'arguments': {
                    'provider': provider,
                    'messages': messages,
                    'model': model,
                    'temperature': temperature,
                    'max_tokens': max_tokens
                }
            }
        }
        
        proc = await asyncio.create_subprocess_exec(
            'node',
            self.mcp_server_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate(
            input=json.dumps(request).encode() + b'\n'
        )
        
        if proc.returncode != 0:
            raise Exception(f"MCP error: {stderr.decode()}")
        
        lines = stdout.decode().strip().split('\n')
        response = json.loads(lines[-1])
        
        return response['result']
```

---

### Opción 2: HTTP API

**Endpoint:** `http://localhost:3100`

```python
# backend/ai/aion_client.py

import httpx

class AIONBrainHTTPClient:
    """
    Cliente HTTP para AION Brain v3.2.
    Comunicación vía REST API.
    """
    
    def __init__(self, base_url='http://localhost:3100'):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30)
    
    async def orchestrate(self, prompt, task_type='auto', max_tokens=4096):
        """
        Orquestación automática con routing inteligente.
        
        task_type: 'auto', 'simple', 'complex', 'search', 'math', etc.
        """
        response = await self.client.post(
            f"{self.base_url}/orchestrate",
            json={
                'prompt': prompt,
                'task_type': task_type,
                'max_tokens': max_tokens
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def chat_completions(self, messages, model='auto', temperature=0.7):
        """
        OpenAI-compatible endpoint.
        """
        response = await self.client.post(
            f"{self.base_url}/v1/chat/completions",
            json={
                'model': model,
                'messages': messages,
                'temperature': temperature
            }
        )
        response.raise_for_status()
        return response.json()
```

---

## 🎯 CASOS DE USO ESPECÍFICOS PARA CHATITA MAIL

### 1. Email Classification

```python
# Clasificar email con routing automático
classification = await aion.orchestrate(
    prompt=f"Classify this email:\nSubject: {email.subject}\nBody: {email.body}",
    task_type='simple'  # → Together Llama-3.3 ($0.001)
)

# Resultado: 98% más barato que Claude Opus
```

---

### 2. Smart Replies con Contexto

```python
# Generar respuestas con contexto enriquecido
replies = await aion.orchestrate(
    prompt=f"""Generate 3 reply options for this email:

From: {email.from_addr}
Subject: {email.subject}
Body: {email.body}

Context:
- Sender: {contact_info}
- Recent docs: {drive_results}
- Calendar: {availability}

Options: short, professional, with-attachment""",
    task_type='complex'  # → Claude Sonnet ($0.03)
)

# Resultado: 80% más barato que Claude Opus
```

---

### 3. Web Search para Contexto

```python
# Buscar info actual sobre empresa mencionada
web_context = await aion.orchestrate(
    prompt=f"Latest news about {company_name}",
    task_type='search'  # → Perplexity Sonar Pro ($0.005)
)

# Resultado: 93% más barato que Claude Opus
# Bonus: Citations automáticas
```

---

### 4. Análisis de Imagen Adjunta

```python
# Analizar screenshot adjunto
image_analysis = await aion.execute_tool(
    tool='openai_vision',
    params={
        'image_url': attachment.url,
        'prompt': 'Extract all text and describe this image'
    }
)

# Costo: $0.01 por imagen
```

---

### 5. Transcripción de Audio

```python
# Transcribir nota de voz
transcription = await aion.execute_tool(
    tool='openai_whisper',
    params={
        'audio_url': voice_note.url,
        'language': 'es'
    }
)

# Costo: $0.006 por minuto
```

---

### 6. Emotion Detection en Voz

```python
# Detectar emociones en nota de voz
emotions = await aion.execute_tool(
    tool='hume_voice_emotion',
    params={
        'audio_url': voice_note.url
    }
)

# Resultado:
# {
#   'valence': -0.65,  # negativo
#   'arousal': 0.82,   # muy excitado
#   'top_emotions': ['frustrated', 'urgent', 'disappointed']
# }

# Acción: Aumentar priority score +25
```

---

### 7. Semantic Search con Embeddings Gratis

```python
# Generar embedding para búsqueda semántica
embedding = await aion.execute_tool(
    tool='huggingface_embed',
    params={
        'text': search_query,
        'model': 'BAAI/bge-m3'
    }
)

# Costo: $0 (HuggingFace gratis)
# Ahorro: 100% vs OpenAI embeddings
```

---

### 8. Daily Briefing con Audio

```python
# Generar briefing con Claude Opus (calidad máxima)
briefing_text = await aion.orchestrate(
    prompt=f"""Generate executive morning briefing:

Priority Emails: {priority_emails}
Calendar Today: {calendar_events}
Pending Actions: {action_items}

Format: Executive summary with emojis""",
    task_type='critical'  # → Claude Opus ($0.15)
)

# Generar audio con voz clonada de Manny
audio_url = await aion.execute_tool(
    tool='elevenlabs_tts',
    params={
        'text': briefing_text,
        'voice_id': 'manny_voice_clone',
        'language': 'es'
    }
)

# Enviar vía Telegram
await aion.execute_tool(
    tool='telegram_send_audio',
    params={
        'chat_id': MANNY_TELEGRAM_ID,
        'audio_url': audio_url,
        'caption': '🎧 Morning Briefing'
    }
)

# Costo total: $0.15 (briefing) + $0.30 (audio) = $0.45
```

---

## 📊 COMPARATIVA ACTUALIZADA

### Chatita Mail v2.0 con AION Brain v3.2

| Feature | v1.0 (Básico) | v2.0 (AION v3.2) | Mejora |
|---------|---------------|------------------|--------|
| **LLM Providers** | 1-2 | **11** | **5.5x** |
| **Servicios Totales** | 5-10 | **91+** | **9x** |
| **Task Types** | 3-5 | **17** | **3.4x** |
| **Embeddings** | Pagados | **Gratis (HF)** | **100% ahorro** |
| **Vision AI** | Básico | **8 servicios** | **8x** |
| **Audio AI** | Básico | **8 servicios** | **8x** |
| **Gov APIs** | 0 | **25+ gratis** | **∞** |
| **Emotion AI** | ❌ | **Hume AI** | **Único** |
| **Web Automation** | ❌ | **3 servicios** | **Nuevo** |
| **Costo Mensual** | $85 | **$30** | **65% ahorro** |

---

## 🚀 PRÓXIMOS PASOS

### 1. Setup AION Brain v3.2

```bash
# Clonar repo
git clone https://github.com/ManuelCadena/aion-brain.git
cd aion-brain

# Instalar
npm install

# Configurar .env (copiar de .env.example)
cp .env.example .env
# Editar .env con tus API keys

# Test
npm test

# Start MCP server
npm run mcp

# Start HTTP server (puerto 3100)
npm start
```

---

### 2. Integrar en Chatita Mail

```python
# backend/ai/aion_client.py
from aion_brain_client import AIONBrainMCPClient

aion = AIONBrainMCPClient()

# Usar en clasificación
classification = await aion.llm_chat(
    provider='together',  # o 'auto' para routing automático
    messages=[{'role': 'user', 'content': f'Classify: {email.subject}'}]
)
```

---

### 3. Deployment

**Opción A: Local (desarrollo)**
```bash
# En chatita-local
cd ~/chatita-local
git clone https://github.com/ManuelCadena/aion-brain.git
cd aion-brain
npm install
npm start  # HTTP en :3100
```

**Opción B: Servidor Chatita (producción)**
```bash
# SSH a Chatita server
ssh chatita-dev-alt

# Clonar en /opt/chatita
cd /opt/chatita
git clone https://github.com/ManuelCadena/aion-brain.git
cd aion-brain
npm install

# Configurar .env con keys de producción
nano .env

# Crear systemd service
sudo nano /etc/systemd/system/aion-brain.service
```

```ini
[Unit]
Description=AION Brain v3.2 HTTP Server
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/chatita/aion-brain
ExecStart=/usr/bin/node http-server.js
Restart=always
Environment=NODE_ENV=production
Environment=AION_PORT=3100

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl daemon-reload
sudo systemctl enable aion-brain
sudo systemctl start aion-brain

# Verificar
curl http://localhost:3100/health
```

---

## 📈 MÉTRICAS DE ÉXITO

### KPIs para Chatita Mail con AION Brain v3.2

1. **Cost Savings**: ≥65% (target: 68.7% validado)
2. **Response Time**: <2s promedio
3. **Accuracy**: ≥90% en clasificación
4. **Smart Reply Quality**: ≥85% acceptance rate
5. **Emotion Detection**: ≥80% accuracy
6. **Uptime**: ≥99.5%

---

## ✅ CONCLUSIÓN

**AION Brain v3.2** está **production-ready** y ofrece:

✅ **11 LLM providers** con routing inteligente  
✅ **91+ servicios** (vision, audio, gov, corporate, research)  
✅ **68-93% cost savings** validados experimentalmente  
✅ **17 task types** con routing automático  
✅ **Gratis**: HuggingFace embeddings, 25+ gov APIs  
✅ **Único**: Hume AI emotion detection  
✅ **Deployado**: 5+ sistemas en producción  

**Recomendación:** Integrar AION Brain v3.2 en Chatita Mail **inmediatamente**.

**Riesgo:** Bajo (ya validado en producción)  
**Upside:** Altísimo (mejor email app del mercado)

---

**¿Procedemos con integración?** 🚀
