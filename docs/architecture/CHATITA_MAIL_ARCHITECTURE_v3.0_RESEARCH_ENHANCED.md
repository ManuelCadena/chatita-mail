# Chatita Mail v3.0 — Research-Enhanced Architecture
**The World's Most Intelligent Email Application**

**Author**: Manuel Cadena  
**Date**: 22-Jul-2026  
**Version**: 3.0 (Research-Driven)  
**Based on**: 50 Academic Papers (2008-2026) + AION Brain v3.2

---

## 🎯 DESIGN PHILOSOPHY

**User Goal**: Spend **≤5 minutes/day** on email while maintaining **100% coverage** of important communications.

**Core Principles** (Research-Validated):
1. **Trust Through Transparency** (Liu et al. 2022) → XAI for all AI decisions
2. **Automation with Control** (Goodman et al. 2022) → User approves critical actions
3. **Security First** (Eze & Shamir 2024) → Phishing detection + prompt injection defense
4. **Personalization** (Novelo et al. 2025) → Learn user's writing style
5. **Workflow Integration** (Navarro et al. 2025) → Email→Action automation

---

## 🏗️ SYSTEM ARCHITECTURE

```
┌────────────────────────────────────────────────────────────────────┐
│                     CHATITA MAIL v3.0                              │
│              Research-Enhanced AI Email Assistant                  │
│                                                                    │
│  Goal: ≤5 min/day | 100% important emails | 0% spam/noise        │
└────────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
        ┌───────────────┐               ┌───────────────┐
        │   FRONTEND    │               │   BACKEND     │
        │   React + TS  │◄─────────────►│   FastAPI     │
        │   TailwindCSS │   WebSocket   │   Python 3.11 │
        └───────────────┘               └───────┬───────┘
                                                │
                        ┌───────────────────────┼───────────────────────┐
                        ▼                       ▼                       ▼
                ┌───────────────┐       ┌───────────────┐     ┌───────────────┐
                │  SECURITY     │       │  WORKFLOW     │     │ PERSONALIZATION│
                │  LAYER        │       │  AUTOMATION   │     │  ENGINE       │
                └───────┬───────┘       └───────┬───────┘     └───────┬───────┘
                        │                       │                     │
        ┌───────────────┼───────────────┐      │                     │
        ▼               ▼               ▼       ▼                     ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Phishing     │ │ Prompt       │ │ Sender       │ │ Task         │ │ Style        │
│ Detection    │ │ Injection    │ │ Reputation   │ │ Extraction   │ │ Learning     │
│ (XAI)        │ │ Defense      │ │ (OpenCorp)   │ │ (NER)        │ │ Engine       │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
        │               │               │               │               │
        └───────────────┴───────────────┴───────────────┴───────────────┘
                                        │
                        ┌───────────────┴───────────────┐
                        ▼                               ▼
                ┌───────────────┐               ┌───────────────┐
                │  AION BRAIN   │               │  KNOWLEDGE    │
                │  v3.2         │◄─────────────►│  BASE (RAG)   │
                │               │               │               │
                │  11 LLMs      │               │  PostgreSQL   │
                │  91+ APIs     │               │  + pgvector   │
                │  17 Tasks     │               │               │
                └───────┬───────┘               └───────────────┘
                        │
        ┌───────────────┼───────────────┬───────────────┬───────────────┐
        ▼               ▼               ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Together.ai  │ │ Anthropic    │ │ Perplexity   │ │ HuggingFace  │ │ Google       │
│ (Budget)     │ │ (Critical)   │ │ (Search)     │ │ (Free)       │ │ Workspace    │
│ $0.18/1M     │ │ $3-15/1M     │ │ $1-5/1M      │ │ $0/1M        │ │ APIs         │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

---

## 🔒 LAYER 1: SECURITY (Research-Validated)

### **1.1 Phishing Detection with XAI**

**Research Basis**:
- Al-Subaiey et al. (2024): **95%+ accuracy** with ML + XAI
- Viswanathan et al. (2025): Multi-modal analysis (content + metadata + URLs + sender network)
- Eze & Shamir (2024): GenAI makes phishing easier → need adaptive defense

**Implementation**:

```python
class PhishingDetector:
    """
    Multi-layer phishing detection with explainability.
    Research-validated approach combining:
    - Content analysis (urgency, impersonation)
    - Sender reputation (OpenCorporates, ICIJ)
    - URL analysis (malicious domains)
    - Attachment safety (file types, names)
    """
    
    async def analyze_email(self, email: Email) -> SecurityAnalysis:
        # Layer 1: Content Analysis (HuggingFace FinBERT)
        sentiment = await self.aion.execute_tool(
            tool='hf_sentiment_fin',
            params={'texts': [email.body]}
        )
        
        # Layer 2: Urgency Detection
        urgency_analysis = await self.aion.orchestrate(
            prompt=f"""Analyze urgency indicators in this email:
            
{email.body}

Detect:
- Artificial urgency ("act now", "limited time")
- Threats ("account will be closed")
- Impersonation attempts
- Suspicious requests (password, payment)

Return JSON with:
- urgency_score: 0-100
- indicators: [list of red flags]
- impersonation_risk: 0-100
""",
            task_type='simple'  # Together Llama-3.3 (fast + cheap)
        )
        
        # Layer 3: Sender Reputation
        sender_reputation = await self.check_sender_reputation(email.from_addr)
        
        # Layer 4: URL Analysis
        urls = extract_urls(email.body)
        url_safety = await self.analyze_urls(urls)
        
        # Layer 5: Attachment Safety
        attachment_safety = await self.analyze_attachments(email.attachments)
        
        # Combine all signals
        risk_score = self.calculate_risk_score(
            sentiment=sentiment,
            urgency=urgency_analysis,
            sender=sender_reputation,
            urls=url_safety,
            attachments=attachment_safety
        )
        
        # Generate XAI explanation
        explanation = self.generate_explanation(
            risk_score=risk_score,
            factors={
                'sentiment': sentiment,
                'urgency': urgency_analysis,
                'sender': sender_reputation,
                'urls': url_safety,
                'attachments': attachment_safety
            }
        )
        
        return SecurityAnalysis(
            risk_score=risk_score,
            risk_level='safe' if risk_score < 30 else 'suspicious' if risk_score < 70 else 'dangerous',
            explanation=explanation,
            recommended_action='allow' if risk_score < 30 else 'quarantine' if risk_score < 90 else 'block'
        )
    
    async def check_sender_reputation(self, email_addr: str) -> SenderReputation:
        """
        Check sender reputation using corporate intelligence.
        Research basis: No other consumer email app does this.
        """
        domain = email_addr.split('@')[1]
        
        # Check if domain is known/trusted
        if domain in self.trusted_domains:
            return SenderReputation(score=100, status='trusted')
        
        # Check corporate registry
        company_info = await self.aion.execute_tool(
            tool='opencorporates_search',
            params={'name': domain}
        )
        
        if not company_info:
            # Domain doesn't exist in corporate registries → suspicious
            return SenderReputation(score=20, status='unknown', reason='Domain not found in corporate registries')
        
        # Check offshore jurisdictions
        if company_info['jurisdiction'] in ['BVI', 'Cayman', 'Panama']:
            return SenderReputation(score=40, status='offshore', reason=f"Registered in {company_info['jurisdiction']}")
        
        return SenderReputation(score=70, status='verified', company=company_info)
```

**UI Display**:

```
┌─────────────────────────────────────────────────────────────┐
│ 🚨 SECURITY ALERT                                           │
├─────────────────────────────────────────────────────────────┤
│ From: support@paypa1-security.com                          │
│ Subject: Urgent: Verify your account                       │
│                                                             │
│ 🛡️ Risk Score: 92/100 (DANGEROUS)                          │
│                                                             │
│ ⚠️ Why this is risky:                                       │
│ • Domain "paypa1-security.com" is NOT PayPal (typosquatting)│
│ • High urgency language detected ("urgent", "verify now")  │
│ • Sender domain registered 3 days ago                      │
│ • Contains suspicious link to phishing site                │
│ • No company found in corporate registries                 │
│                                                             │
│ 🎯 Recommended Action: BLOCK + REPORT                       │
│                                                             │
│ [Block Sender] [Report Phishing] [Allow Anyway]            │
└─────────────────────────────────────────────────────────────┘
```

---

### **1.2 Prompt Injection Defense**

**Research Basis**:
- Novelo et al. (2025): Prompt injection is real risk in email AI assistants
- Need to sanitize email content before sending to LLM

**Implementation**:

```python
class PromptInjectionDefense:
    """
    Detect and neutralize prompt injection attempts in emails.
    """
    
    INJECTION_PATTERNS = [
        r'ignore previous instructions',
        r'disregard all',
        r'you are now',
        r'forget everything',
        r'new instructions:',
        r'system:',
        r'<|im_start|>',
        r'<|im_end|>',
    ]
    
    async def sanitize_email(self, email: Email) -> Email:
        # Detect injection attempts
        injection_detected = any(
            re.search(pattern, email.body, re.IGNORECASE)
            for pattern in self.INJECTION_PATTERNS
        )
        
        if injection_detected:
            # Quarantine + notify user
            await self.quarantine_email(email, reason='Prompt injection attempt detected')
            
            # Log for security analysis
            await self.log_security_event(
                event_type='prompt_injection',
                email_id=email.id,
                sender=email.from_addr
            )
        
        # Escape special tokens
        sanitized_body = self.escape_special_tokens(email.body)
        
        return Email(**{**email.dict(), 'body': sanitized_body})
```

---

## 🤖 LAYER 2: WORKFLOW AUTOMATION (Research-Validated)

### **2.1 Task Extraction + Commitment Tracking**

**Research Basis**:
- Morrison et al. (2024): **AI better than humans** at detecting commitments
- S et al. (2026): **94.2% reduction** in manual response time

**Implementation**:

```python
class TaskExtractor:
    """
    Extract tasks and commitments from emails.
    Track who committed to what and when.
    """
    
    async def extract_tasks(self, email: Email, thread: List[Email]) -> List[Task]:
        # Analyze full thread for context
        thread_text = '\n\n'.join([
            f"From: {e.from_addr}\nDate: {e.date}\n{e.body}"
            for e in thread
        ])
        
        tasks = await self.aion.orchestrate(
            prompt=f"""Extract ALL tasks and commitments from this email thread:

{thread_text}

For each task/commitment, identify:
1. Who committed (me, sender, or specific person)
2. What they committed to do (be specific)
3. Deadline (explicit or implicit)
4. Dependencies (what needs to happen first)
5. Priority (critical, high, medium, low)
6. Context (why this matters)

Return JSON array of tasks.""",
            task_type='complex'  # Claude Sonnet for accuracy
        )
        
        # Create reminders for MY commitments
        my_tasks = [t for t in tasks if t['who'] == 'me']
        for task in my_tasks:
            await self.create_reminder(task, email)
        
        # Track OTHERS' commitments for follow-up
        others_tasks = [t for t in tasks if t['who'] != 'me']
        for task in others_tasks:
            await self.track_commitment(task, email)
        
        return tasks
    
    async def create_reminder(self, task: Task, email: Email):
        """Create Google Calendar reminder for my commitment."""
        # Calculate reminder time (e.g., 1 day before deadline)
        reminder_time = task['deadline'] - timedelta(days=1)
        
        await self.aion.execute_tool(
            tool='google_calendar_create_event',
            params={
                'summary': f"⏰ Reminder: {task['what']}",
                'description': f"""Commitment from email: {email.subject}

From: {email.from_addr}
Deadline: {task['deadline']}
Priority: {task['priority']}

Context: {task['context']}

Original email: {email.permalink}""",
                'start': reminder_time,
                'end': reminder_time + timedelta(hours=1),
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 0},
                        {'method': 'email', 'minutes': 60}
                    ]
                }
            }
        )
    
    async def track_commitment(self, task: Task, email: Email):
        """Track others' commitments and auto-follow-up if not completed."""
        # Save to DB
        await self.db.commitments.insert({
            'email_id': email.id,
            'who': task['who'],
            'what': task['what'],
            'deadline': task['deadline'],
            'status': 'pending',
            'created_at': datetime.now()
        })
        
        # Schedule follow-up check
        check_time = task['deadline'] + timedelta(days=1)
        await self.schedule_task(
            task_type='check_commitment',
            run_at=check_time,
            params={'commitment_id': task['id']}
        )
    
    async def check_commitment_status(self, commitment_id: str):
        """Check if commitment was fulfilled, suggest follow-up if not."""
        commitment = await self.db.commitments.get(commitment_id)
        
        # Search for follow-up emails
        followup_emails = await self.search_emails(
            from_addr=commitment['who'],
            after=commitment['deadline'],
            keywords=extract_keywords(commitment['what'])
        )
        
        if not followup_emails:
            # No follow-up detected → suggest reminder email
            draft = await self.generate_followup_email(commitment)
            
            await self.notify_user(
                title=f"Commitment not fulfilled: {commitment['what']}",
                message=f"{commitment['who']} committed to {commitment['what']} by {commitment['deadline']} but no follow-up detected.",
                action='Send follow-up email?',
                draft=draft
            )
```

---

### **2.2 Meeting Scheduling Automation**

**Research Basis**:
- Morrison et al. (2024): AI-powered reminders improve collaboration
- Navarro et al. (2025): Email as interface to automation → <8s processing

**Implementation**:

```python
class MeetingScheduler:
    """
    Automatically schedule meetings from email requests.
    """
    
    async def detect_meeting_request(self, email: Email) -> Optional[MeetingRequest]:
        # Detect if email is requesting a meeting
        analysis = await self.aion.orchestrate(
            prompt=f"""Analyze if this email is requesting a meeting:

{email.body}

If yes, extract:
- Proposed times (if any)
- Duration (if mentioned)
- Attendees (if mentioned)
- Topic/purpose
- Urgency

Return JSON or null if not a meeting request.""",
            task_type='simple'
        )
        
        if not analysis:
            return None
        
        return MeetingRequest(**analysis)
    
    async def auto_schedule_meeting(self, request: MeetingRequest, email: Email):
        """
        Find available slots and propose/create meeting.
        """
        # Get my availability
        my_availability = await self.aion.execute_tool(
            tool='google_calendar_availability',
            params={
                'start_date': datetime.now(),
                'end_date': datetime.now() + timedelta(days=14),
                'duration_minutes': request.duration or 60
            }
        )
        
        # Get sender's availability (if they shared calendar)
        sender_availability = await self.get_sender_availability(email.from_addr)
        
        # Find overlapping slots
        available_slots = find_overlapping_slots(
            my_availability,
            sender_availability,
            duration=request.duration or 60
        )
        
        if not available_slots:
            # No overlap → propose my top 3 slots
            await self.propose_meeting_times(email, my_availability[:3])
            return
        
        # Auto-create meeting in best slot
        best_slot = available_slots[0]
        
        meeting = await self.aion.execute_tool(
            tool='google_calendar_create_event',
            params={
                'summary': request.topic or f"Meeting with {email.from_name}",
                'description': f"Scheduled automatically from email: {email.subject}",
                'start': best_slot['start'],
                'end': best_slot['end'],
                'attendees': [email.from_addr],
                'sendUpdates': 'all'
            }
        )
        
        # Reply to email confirming meeting
        reply = await self.generate_meeting_confirmation(meeting, email)
        await self.send_email(reply)
```

---

## 🎨 LAYER 3: PERSONALIZATION ENGINE (Research-Validated)

### **3.1 Style Learning**

**Research Basis**:
- Novelo et al. (2025): **Personalized LLM assistants** with feedback-driven refinement
- Goodman et al. (2022): Users prefer control over full automation

**Implementation**:

```python
class StyleLearningEngine:
    """
    Learn user's writing style from sent emails.
    Generate replies that sound authentic.
    """
    
    async def learn_user_style(self, user_id: str) -> StyleProfile:
        """
        One-time analysis of user's sent emails.
        """
        # Get last 100 sent emails
        sent_emails = await self.get_sent_emails(user_id, limit=100)
        
        # Analyze style
        style_profile = await self.aion.orchestrate(
            prompt=f"""Analyze these 100 emails I wrote and extract my writing style:

{sent_emails}

Return detailed JSON profile:
{{
  "tone": "casual|professional|mixed",
  "formality_level": 1-10,
  "avg_length": "brief|medium|detailed",
  "sentence_structure": "simple|complex|varied",
  "vocabulary_level": "simple|moderate|advanced",
  "common_phrases": ["phrase1", "phrase2", ...],
  "greeting_style": "...",
  "closing_style": "...",
  "emoji_usage": "never|rare|frequent",
  "emoji_types": ["😊", "👍", ...],
  "language_mix": {{"en": 0.7, "es": 0.3}},
  "punctuation_style": "minimal|moderate|heavy",
  "paragraph_length": "short|medium|long",
  "uses_contractions": true|false,
  "humor_level": 1-10,
  "directness": 1-10
}}""",
            task_type='complex'
        )
        
        # Save to DB
        await self.db.style_profiles.upsert(user_id, style_profile)
        
        return StyleProfile(**style_profile)
    
    async def generate_personalized_reply(
        self,
        email: Email,
        style_profile: StyleProfile,
        context: EmailContext
    ) -> List[ReplyOption]:
        """
        Generate 3 reply options in different styles.
        Research basis: Liu et al. (2022) - users want options.
        """
        # Option 1: User's natural style
        natural_reply = await self.aion.orchestrate(
            prompt=f"""Generate reply to this email IN MY EXACT STYLE:

Email: {email.body}

My style profile:
{style_profile}

Context:
- Sender: {context.sender_relationship}
- Previous emails: {context.thread_history}
- Sender's tone: {context.sender_tone}

Generate reply that sounds EXACTLY like me, not like AI.
Match my:
- Tone ({style_profile.tone})
- Formality level ({style_profile.formality_level}/10)
- Typical length ({style_profile.avg_length})
- Common phrases
- Greeting/closing style
- Emoji usage ({style_profile.emoji_usage})

Make it authentic and natural.""",
            task_type='complex'
        )
        
        # Option 2: More professional
        professional_reply = await self.aion.orchestrate(
            prompt=f"""Generate PROFESSIONAL version of reply:

Email: {email.body}

Keep my personality but make it more formal and polished.
Suitable for: executives, clients, formal contexts.

Length: {style_profile.avg_length}
Tone: Professional but warm""",
            task_type='medium'
        )
        
        # Option 3: Brief version
        brief_reply = await self.aion.orchestrate(
            prompt=f"""Generate BRIEF version (1-2 sentences):

Email: {email.body}

Direct and to the point.
Still friendly but minimal words.""",
            task_type='simple'
        )
        
        return [
            ReplyOption(
                text=natural_reply,
                style='natural',
                explanation='This sounds like your typical emails',
                confidence=0.9
            ),
            ReplyOption(
                text=professional_reply,
                style='professional',
                explanation='More formal, good for business contexts',
                confidence=0.85
            ),
            ReplyOption(
                text=brief_reply,
                style='brief',
                explanation='Quick response when you\'re busy',
                confidence=0.8
            )
        ]
    
    async def learn_from_edit(
        self,
        original_reply: str,
        edited_reply: str,
        user_id: str
    ):
        """
        Update style profile based on user edits.
        Research basis: Feedback-driven refinement (Novelo 2025).
        """
        # Analyze what changed
        diff_analysis = await self.aion.orchestrate(
            prompt=f"""Analyze what the user changed:

Original (AI-generated):
{original_reply}

Edited (user's version):
{edited_reply}

What patterns changed?
- Tone adjustments
- Length changes
- Word choice preferences
- Structural changes

Return JSON with insights.""",
            task_type='simple'
        )
        
        # Update style profile
        await self.update_style_profile(user_id, diff_analysis)
```

---

## 📊 COMPLETE FEATURE MATRIX

### **Implemented Features (23 Total)**

| Feature | Research Basis | AION Brain Tools | Status |
|---------|---------------|------------------|--------|
| **P0 — CRITICAL** |
| 1. Phishing Detection + XAI | Al-Subaiey 2024 | HF classification + OpenCorporates | ✅ Designed |
| 2. Auto-Unsubscribe | Dredze 2008, Mathew 2026 | Pattern detection + auto-click | ✅ Designed |
| 3. Task Extraction | Morrison 2024, S et al. 2026 | Claude Sonnet + NER | ✅ Designed |
| 4. Style Learning | Novelo 2025, Goodman 2022 | Analyze sent emails | ✅ Designed |
| 5. Workflow Automation | Navarro 2025 | 91+ APIs orchestration | ✅ Designed |
| **P1 — HIGH** |
| 6. Commitment Tracking | Morrison 2024 | NER + Calendar API | ✅ Designed |
| 7. Sender Reputation | Corporate intel papers | OpenCorporates + ICIJ | ✅ Designed |
| 8. Multi-Style Replies | Liu 2022 | 3 styles + XAI | ✅ Designed |
| 9. Urgency Detection | Hume AI papers | FinBERT sentiment | ✅ Designed |
| 10. Auto-Archive | Mathew 2026 | Classification + rules | ✅ Designed |
| 11. Thread Summarization | Multiple papers | Claude Sonnet | ⏸️ Pending |
| 12. Meeting Scheduling | Morrison 2024 | Calendar API | ✅ Designed |
| **P2 — MEDIUM** |
| 13-20 | Various | Various | ⏸️ Phase 3-4 |
| **P3 — INNOVATION** |
| 21-23 | Emerging trends | Agentic AI | ⏸️ Phase 4+ |

---

## 💰 COST OPTIMIZATION

### **LLM Routing Strategy**

```python
TASK_ROUTING = {
    # P0 tasks (accuracy critical)
    'phishing_detection': {
        'provider': 'anthropic',
        'model': 'claude-sonnet-4',
        'cost_per_1m': 3.00,
        'reason': 'Security critical, need high accuracy'
    },
    
    # P1 tasks (important but not critical)
    'task_extraction': {
        'provider': 'anthropic',
        'model': 'claude-sonnet-4',
        'cost_per_1m': 3.00,
        'reason': 'Commitment tracking requires precision'
    },
    
    # P2 tasks (can use cheaper models)
    'classification': {
        'provider': 'together',
        'model': 'Llama-3.3-70B',
        'cost_per_1m': 0.18,
        'reason': '98% cost savings vs GPT-4'
    },
    
    # Free tasks
    'embeddings': {
        'provider': 'huggingface',
        'model': 'BAAI/bge-m3',
        'cost_per_1m': 0.00,
        'reason': 'Free, high quality'
    }
}
```

**Monthly Cost Estimate** (100 emails/day):
- Phishing detection: 100 emails × 500 tokens × $3/1M = **$0.15/day** = $4.50/mo
- Task extraction: 20 emails × 1000 tokens × $3/1M = **$0.06/day** = $1.80/mo
- Classification: 100 emails × 200 tokens × $0.18/1M = **$0.004/day** = $0.12/mo
- Reply generation: 10 emails × 800 tokens × $3/1M = **$0.024/day** = $0.72/mo
- **TOTAL: ~$7-10/month** (vs $30 Superhuman)

---

## ✅ NEXT STEPS

1. ✅ **Review & Approve** this architecture
2. ⏸️ **Implement Phase 1** (Security + Core Automation)
3. ⏸️ **Test with real emails** (Manny's inbox)
4. ⏸️ **Iterate based on feedback**
5. ⏸️ **Deploy to production**

---

**Ready to proceed with implementation?** 🚀
