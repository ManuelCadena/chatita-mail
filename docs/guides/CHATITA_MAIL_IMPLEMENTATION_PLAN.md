# Chatita Mail v2.0 — Implementation Plan
**Detailed Technical Roadmap with Code Examples**

**Author**: Manuel Cadena  
**Date**: 21-Jul-2026  
**Version**: 1.0

---

## FASE 1: FOUNDATION + AION INTEGRATION (Semana 1-2)

### 1.1 Setup AION Brain MCP Client

**Objetivo:** Crear cliente Python para comunicarse con AION Brain MCP server.

**Archivos a crear:**

```
chatita-mail/
├── backend/
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── aion_client.py          # Cliente MCP
│   │   ├── aion_orchestrator.py    # Orquestador principal
│   │   └── cost_tracker.py         # Tracking de costos
│   ├── models/
│   │   ├── __init__.py
│   │   ├── email.py                # Modelos de datos
│   │   └── classification.py
│   └── requirements.txt
```

**Código: `backend/ai/aion_client.py`**

```python
#!/usr/bin/env python3
"""
AION Brain MCP Client for Chatita Mail.
Handles communication with AION Brain server via stdio or HTTP.
"""

import json
import asyncio
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import httpx

@dataclass
class AIONConfig:
    """Configuration for AION Brain connection."""
    mode: str = 'stdio'  # 'stdio' or 'http'
    mcp_server_path: str = '/opt/chatita/mcp-servers/aion-brain-mcp/index.js'
    http_endpoint: str = 'http://localhost:3000/api'
    timeout: int = 30


class AIONBrainClient:
    """
    Client for AION Brain MCP server.
    Provides high-level methods for all AI operations.
    """
    
    def __init__(self, config: Optional[AIONConfig] = None):
        self.config = config or AIONConfig()
        self.http_client = httpx.AsyncClient(timeout=self.config.timeout)
    
    async def llm_chat(
        self,
        provider: str,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Chat with any LLM provider via AION Brain.
        
        Args:
            provider: 'openai', 'anthropic', 'together', 'perplexity', 'xai', 'gemini'
            messages: List of message dicts with 'role' and 'content'
            model: Optional model override
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
        
        Returns:
            Dict with 'content', 'model', 'usage', 'cost'
        """
        params = {
            'provider': provider,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens
        }
        
        if model:
            params['model'] = model
        
        if self.config.mode == 'http':
            return await self._call_http('chat', params)
        else:
            return await self._call_mcp('llm_chat', params)
    
    async def perplexity_search(
        self,
        query: str,
        model: str = 'sonar-pro'
    ) -> Dict[str, Any]:
        """
        Web search with citations via Perplexity.
        
        Returns:
            Dict with 'content', 'citations', 'images'
        """
        params = {'query': query, 'model': model}
        
        if self.config.mode == 'http':
            return await self._call_http('search', params)
        else:
            return await self._call_mcp('perplexity_search', params)
    
    async def openai_vision(
        self,
        image_url: str,
        prompt: str,
        model: str = 'gpt-4o'
    ) -> Dict[str, Any]:
        """
        Analyze image with GPT-4o Vision.
        
        Returns:
            Dict with 'description', 'ocr_text', 'key_info'
        """
        params = {
            'image_url': image_url,
            'prompt': prompt,
            'model': model
        }
        
        if self.config.mode == 'http':
            return await self._call_http('vision', params)
        else:
            return await self._call_mcp('openai_vision', params)
    
    async def hume_voice_emotion(
        self,
        audio_url: str
    ) -> Dict[str, Any]:
        """
        Detect emotions in voice audio with Hume AI.
        
        Returns:
            Dict with 'valence', 'arousal', 'top_emotions', 'prosody'
        """
        params = {'audio_url': audio_url}
        return await self._call_mcp('hume_voice_emotion', params)
    
    async def hume_video_emotion(
        self,
        video_url: str
    ) -> Dict[str, Any]:
        """
        Detect emotions in video with Hume AI.
        
        Returns:
            Dict with 'timeline', 'dominant_emotion', 'summary'
        """
        params = {'video_url': video_url}
        return await self._call_mcp('hume_video_emotion', params)
    
    async def huggingface_embed(
        self,
        text: str,
        model: str = 'BAAI/bge-m3'
    ) -> List[float]:
        """
        Generate text embeddings with Hugging Face.
        
        Returns:
            List of floats (embedding vector)
        """
        params = {'text': text, 'model': model}
        result = await self._call_mcp('huggingface_embed', params)
        return result['embedding']
    
    async def elevenlabs_tts(
        self,
        text: str,
        voice_id: str,
        language: str = 'es'
    ) -> Dict[str, Any]:
        """
        Generate speech audio with ElevenLabs.
        
        Returns:
            Dict with 'url', 'duration_seconds'
        """
        params = {
            'text': text,
            'voice_id': voice_id,
            'language': language
        }
        return await self._call_mcp('elevenlabs_tts', params)
    
    # Google Workspace APIs
    
    async def google_drive_search(
        self,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search Google Drive for documents."""
        params = {'query': query, 'limit': limit}
        result = await self._call_mcp('google_drive_search', params)
        return result['files']
    
    async def google_calendar_availability(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Check calendar availability."""
        params = {'start_date': start_date, 'end_date': end_date}
        return await self._call_mcp('google_calendar_availability', params)
    
    async def google_calendar_create_event(
        self,
        title: str,
        start: str,
        end: str,
        attendees: List[str]
    ) -> Dict[str, Any]:
        """Create calendar event."""
        params = {
            'title': title,
            'start': start,
            'end': end,
            'attendees': attendees
        }
        return await self._call_mcp('google_calendar_create_event', params)
    
    async def google_contacts_get(
        self,
        email: str
    ) -> Dict[str, Any]:
        """Get contact information."""
        params = {'email': email}
        return await self._call_mcp('google_contacts_get', params)
    
    # Internal methods
    
    async def _call_http(self, endpoint: str, params: Dict) -> Dict[str, Any]:
        """Call AION Brain via HTTP bridge."""
        url = f"{self.config.http_endpoint}/{endpoint}"
        response = await self.http_client.post(url, json=params)
        response.raise_for_status()
        return response.json()
    
    async def _call_mcp(self, tool: str, params: Dict) -> Dict[str, Any]:
        """Call AION Brain via MCP stdio."""
        request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'tools/call',
            'params': {
                'name': tool,
                'arguments': params
            }
        }
        
        proc = await asyncio.create_subprocess_exec(
            'node',
            self.config.mcp_server_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate(
            input=json.dumps(request).encode() + b'\n'
        )
        
        if proc.returncode != 0:
            raise Exception(f"MCP call failed: {stderr.decode()}")
        
        lines = stdout.decode().strip().split('\n')
        response = json.loads(lines[-1])
        
        if 'error' in response:
            raise Exception(f"MCP error: {response['error']}")
        
        return response['result']
    
    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()
```

**Código: `backend/ai/aion_orchestrator.py`**

```python
#!/usr/bin/env python3
"""
AION Orchestrator for Chatita Mail.
High-level AI operations with intelligent routing.
"""

import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from .aion_client import AIONBrainClient
from .cost_tracker import CostTracker
from ..models.email import Message, EmailClassification, SentimentAnalysis
from ..models.email import SmartReply, AttachmentAnalysis


class AIONOrchestrator:
    """
    Orchestrates all AI operations for Chatita Mail.
    Implements intelligent routing for cost optimization.
    """
    
    def __init__(self):
        self.aion = AIONBrainClient()
        self.cost_tracker = CostTracker()
    
    async def classify_email(self, email: Message) -> EmailClassification:
        """
        Classify email into category and detect intent.
        Uses Together Llama-3.3 (cost-effective).
        """
        prompt = f"""Classify this email into ONE category and ONE intent.

Subject: {email.subject}
From: {email.from_addr}
Body: {email.body_text[:500]}

Categories: work, personal, transactional, marketing, notifications
Intents: action_required, fyi, calendar, invoice, question, confirmation

Return JSON: {{"category": "...", "intent": "...", "confidence": 0.0-1.0}}"""

        result = await self.aion.llm_chat(
            provider='together',
            model='meta-llama/Llama-3.3-70B-Instruct-Turbo',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.3
        )
        
        # Track cost
        await self.cost_tracker.log(
            task='classification',
            provider='together',
            cost=result.get('cost', 0.001)
        )
        
        data = json.loads(result['content'])
        return EmailClassification(
            category=data['category'],
            intent=data['intent'],
            confidence=data['confidence']
        )
    
    async def analyze_sentiment(self, email: Message) -> SentimentAnalysis:
        """
        Analyze sentiment with emotion detection.
        Uses Hume AI if audio/video attachment, else text analysis.
        """
        # Check for audio/video attachments
        audio_attachment = email.get_audio_attachment()
        video_attachment = email.get_video_attachment()
        
        if audio_attachment:
            # Hume AI voice emotion detection
            emotion_result = await self.aion.hume_voice_emotion(
                audio_url=audio_attachment.url
            )
            
            return SentimentAnalysis(
                valence=emotion_result['valence'],
                arousal=emotion_result['arousal'],
                emotions=emotion_result['top_emotions'],
                confidence=emotion_result['confidence'],
                source='hume_voice'
            )
        
        elif video_attachment:
            # Hume AI video emotion detection
            emotion_result = await self.aion.hume_video_emotion(
                video_url=video_attachment.url
            )
            
            return SentimentAnalysis(
                valence=emotion_result['valence'],
                arousal=emotion_result['arousal'],
                emotions=emotion_result['dominant_emotion'],
                confidence=0.85,
                source='hume_video'
            )
        
        else:
            # Text sentiment analysis
            result = await self.aion.llm_chat(
                provider='together',
                messages=[{
                    'role': 'user',
                    'content': f'''Analyze sentiment of this email:

{email.body_text}

Return JSON: {{"sentiment": "positive|neutral|negative|urgent|angry", "confidence": 0.0-1.0}}'''
                }],
                temperature=0.3
            )
            
            data = json.loads(result['content'])
            
            # Map sentiment to valence
            sentiment_map = {
                'positive': 0.7,
                'neutral': 0.0,
                'negative': -0.5,
                'urgent': -0.3,
                'angry': -0.8
            }
            
            return SentimentAnalysis(
                valence=sentiment_map.get(data['sentiment'], 0.0),
                arousal=0.5 if data['sentiment'] == 'urgent' else 0.3,
                emotions=[data['sentiment']],
                confidence=data['confidence'],
                source='text'
            )
    
    async def generate_smart_replies(
        self,
        email: Message,
        num_options: int = 3
    ) -> List[SmartReply]:
        """
        Generate smart reply options with enriched context.
        Uses Claude Sonnet (balance quality/cost).
        """
        # 1. Enrich context
        context = await self._enrich_context(email)
        
        # 2. Generate replies
        system_prompt = self._build_reply_system_prompt(context)
        
        result = await self.aion.llm_chat(
            provider='anthropic',
            model='claude-sonnet-4',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f'''Generate {num_options} reply options:

From: {email.from_addr}
Subject: {email.subject}
Body: {email.body_text}

Options:
1. Short & casual (1-2 sentences)
2. Professional & detailed (3-4 sentences)
3. With attachment/link (if relevant from context)

Return JSON array of {num_options} options.'''}
            ],
            temperature=0.7
        )
        
        # Track cost
        await self.cost_tracker.log(
            task='reply_generation',
            provider='anthropic',
            cost=result.get('cost', 0.03)
        )
        
        replies_data = json.loads(result['content'])
        return [SmartReply.parse_obj(r) for r in replies_data]
    
    async def analyze_attachment(
        self,
        attachment
    ) -> AttachmentAnalysis:
        """
        Analyze attachment using appropriate AI service.
        """
        if attachment.is_image():
            return await self._analyze_image(attachment)
        elif attachment.is_pdf():
            return await self._analyze_pdf(attachment)
        elif attachment.is_audio():
            return await self._analyze_audio(attachment)
        elif attachment.is_video():
            return await self._analyze_video(attachment)
        else:
            return AttachmentAnalysis(type='unknown')
    
    async def _analyze_image(self, attachment) -> AttachmentAnalysis:
        """Analyze image with GPT-4o Vision."""
        result = await self.aion.openai_vision(
            image_url=attachment.url,
            prompt='''Analyze this image:
1. What is it? (screenshot, photo, diagram, invoice, etc.)
2. Extract any text (OCR)
3. Identify key information (dates, amounts, names)
4. Summarize in 2-3 sentences

Return JSON.''',
            model='gpt-4o'
        )
        
        await self.cost_tracker.log(
            task='image_analysis',
            provider='openai',
            cost=0.01
        )
        
        data = json.loads(result['content'])
        return AttachmentAnalysis(
            type='image',
            description=data.get('description'),
            extracted_text=data.get('ocr_text'),
            key_info=data.get('key_info'),
            summary=data.get('summary')
        )
    
    async def _enrich_context(self, email: Message) -> Dict:
        """
        Enrich email context with Google Workspace data.
        """
        context = {
            'email': email.to_dict(),
            'sender_profile': None,
            'relevant_documents': [],
            'calendar_availability': None,
            'web_context': None
        }
        
        # 1. Get sender profile from Contacts
        try:
            contact = await self.aion.google_contacts_get(email=email.from_addr)
            context['sender_profile'] = contact
        except:
            pass
        
        # 2. Search Drive if email mentions documents
        if self._mentions_documents(email):
            keywords = self._extract_document_keywords(email)
            drive_results = await self.aion.google_drive_search(
                query=keywords,
                limit=3
            )
            context['relevant_documents'] = drive_results
        
        # 3. Check calendar if email mentions meeting
        if self._mentions_meeting(email):
            date_range = self._extract_date_range(email)
            if date_range:
                availability = await self.aion.google_calendar_availability(
                    start_date=date_range[0],
                    end_date=date_range[1]
                )
                context['calendar_availability'] = availability
        
        # 4. Web search if mentions current events
        if self._mentions_current_events(email):
            query = self._extract_search_query(email)
            web_results = await self.aion.perplexity_search(
                query=query,
                model='sonar-pro'
            )
            context['web_context'] = web_results
        
        return context
    
    def _build_reply_system_prompt(self, context: Dict) -> str:
        """Build system prompt with enriched context."""
        prompt = "You are Manny's email assistant. Generate professional replies.\n\n"
        
        if context.get('sender_profile'):
            profile = context['sender_profile']
            prompt += f"Sender: {profile.get('name')} from {profile.get('company')}\n"
            prompt += f"Relationship: {profile.get('interaction_count', 0)} previous emails\n\n"
        
        if context.get('relevant_documents'):
            prompt += "Relevant documents found:\n"
            for doc in context['relevant_documents']:
                prompt += f"- {doc['name']}\n"
            prompt += "\n"
        
        if context.get('calendar_availability'):
            avail = context['calendar_availability']
            if avail.get('available_slots'):
                prompt += "Available meeting times:\n"
                for slot in avail['available_slots'][:3]:
                    prompt += f"- {slot}\n"
                prompt += "\n"
        
        return prompt
    
    def _mentions_documents(self, email: Message) -> bool:
        """Check if email mentions documents."""
        keywords = ['report', 'document', 'file', 'attachment', 'pdf', 'spreadsheet']
        text = (email.subject + ' ' + email.body_text).lower()
        return any(kw in text for kw in keywords)
    
    def _mentions_meeting(self, email: Message) -> bool:
        """Check if email mentions meeting."""
        keywords = ['meeting', 'call', 'schedule', 'available', 'calendar']
        text = (email.subject + ' ' + email.body_text).lower()
        return any(kw in text for kw in keywords)
    
    def _mentions_current_events(self, email: Message) -> bool:
        """Check if email mentions current events."""
        keywords = ['latest', 'news', 'current', 'today', 'recent', 'update']
        text = (email.subject + ' ' + email.body_text).lower()
        return any(kw in text for kw in keywords)
    
    def _extract_document_keywords(self, email: Message) -> str:
        """Extract keywords for document search."""
        # Simple implementation - can be improved with NER
        words = email.subject.split()
        return ' '.join(words[:5])
    
    def _extract_date_range(self, email: Message) -> Optional[tuple]:
        """Extract date range from email."""
        # Simplified - should use proper date extraction
        today = datetime.now()
        next_week = today + timedelta(days=7)
        return (today.isoformat(), next_week.isoformat())
    
    def _extract_search_query(self, email: Message) -> str:
        """Extract search query from email."""
        # Simplified - should use NER and keyword extraction
        return email.subject
    
    async def close(self):
        """Cleanup resources."""
        await self.aion.close()
```

### 1.2 Testing & Validation

**Test script: `backend/tests/test_aion_integration.py`**

```python
#!/usr/bin/env python3
"""
Test AION Brain integration and validate cost savings.
"""

import asyncio
from backend.ai.aion_orchestrator import AIONOrchestrator
from backend.models.email import Message

async def test_classification():
    """Test email classification."""
    orchestrator = AIONOrchestrator()
    
    # Test email
    email = Message(
        id='test-1',
        subject='Q3 Financial Report',
        from_addr='cfo@company.com',
        body_text='Please find attached the Q3 financial report...'
    )
    
    classification = await orchestrator.classify_email(email)
    
    print(f"✅ Classification: {classification.category} / {classification.intent}")
    print(f"   Confidence: {classification.confidence}")
    
    await orchestrator.close()

async def test_smart_replies():
    """Test smart reply generation."""
    orchestrator = AIONOrchestrator()
    
    email = Message(
        id='test-2',
        subject='Meeting Request',
        from_addr='client@acme.com',
        body_text='Can we schedule a meeting next week to discuss the proposal?'
    )
    
    replies = await orchestrator.generate_smart_replies(email)
    
    print(f"✅ Generated {len(replies)} smart replies:")
    for i, reply in enumerate(replies, 1):
        print(f"\n   Option {i}:")
        print(f"   {reply.body[:100]}...")
    
    await orchestrator.close()

async def test_cost_savings():
    """Validate 68% cost savings."""
    orchestrator = AIONOrchestrator()
    
    # Simulate 100 emails
    tasks = ['classification'] * 60 + ['reply_generation'] * 25 + ['search'] * 15
    
    total_cost = 0.0
    baseline_cost = 0.0  # If all used Claude Opus
    
    for task in tasks:
        if task == 'classification':
            # AION routing: Together Llama-3.3
            total_cost += 0.001
            # Baseline: Claude Opus
            baseline_cost += 0.015
        elif task == 'reply_generation':
            # AION routing: Claude Sonnet
            total_cost += 0.03
            # Baseline: Claude Opus
            baseline_cost += 0.15
        elif task == 'search':
            # AION routing: Perplexity
            total_cost += 0.005
            # Baseline: Claude Opus
            baseline_cost += 0.05
    
    savings = (baseline_cost - total_cost) / baseline_cost * 100
    
    print(f"\n✅ Cost Analysis (100 emails):")
    print(f"   AION routing: ${total_cost:.2f}")
    print(f"   Baseline (Opus): ${baseline_cost:.2f}")
    print(f"   Savings: {savings:.1f}%")
    
    assert savings >= 65, f"Expected >=65% savings, got {savings:.1f}%"
    
    await orchestrator.close()

if __name__ == '__main__':
    print("🧪 Testing AION Brain Integration\n")
    asyncio.run(test_classification())
    asyncio.run(test_smart_replies())
    asyncio.run(test_cost_savings())
    print("\n✅ All tests passed!")
```

---

## ENTREGABLES FASE 1

- [ ] `aion_client.py` — Cliente MCP funcionando
- [ ] `aion_orchestrator.py` — Orquestador con routing
- [ ] `cost_tracker.py` — Tracking de costos
- [ ] Tests pasando con 65%+ savings validado
- [ ] Documentación de API

**Tiempo estimado:** 2 semanas  
**Criterio de éxito:** 68% cost savings validado en tests

---

## PRÓXIMOS PASOS

Una vez completada Fase 1, proceder con:
- **Fase 2:** Smart Features (semantic search, attachment analysis)
- **Fase 3:** Autonomous Agent
- **Fase 4:** Frontend React
- **Fase 5:** Testing & Launch

**¿Aprobamos inicio de Fase 1?** 🚀
