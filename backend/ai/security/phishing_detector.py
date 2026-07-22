"""
Chatita Mail v3.0 - Phishing Detector with XAI.

Research basis:
  - Al-Subaiey et al. (2024): XAI necessary for user trust; ML reaches 95%+.
  - Viswanathan et al. (2025): multi-modal (content + metadata + URLs + sender).
  - Eze & Shamir (2024): GenAI makes phishing easier -> adaptive defense needed.

Combines cheap deterministic signals with an AION Brain critical-tier judgment,
and always returns a human-readable explanation (XAI).
"""
from __future__ import annotations

import logging
import re

from backend.ai.aion_client import AIONBrainClient
from backend.config import settings
from backend.models.entities import RiskLevel
from backend.models.schemas import SecurityResult

logger = logging.getLogger("chatita_mail.security")

# ── Deterministic signals ───────────────────────────────────
_URGENCY_TERMS = (
    "urgent", "immediately", "act now", "verify your account", "suspended",
    "unusual activity", "confirm your identity", "within 24 hours",
    "your account will be closed", "final notice", "reactivate",
)

_CREDENTIAL_TERMS = (
    "password", "login", "sign in", "ssn", "social security",
    "credit card", "bank account", "wire transfer", "gift card",
)

_BRANDS = (
    "paypal", "apple", "microsoft", "amazon", "google", "netflix",
    "bank", "irs", "fedex", "ups", "dhl", "docusign",
)

_URL_RE = re.compile(r'https?://[^\s"\'<>]+', re.IGNORECASE)
_IP_URL_RE = re.compile(r'https?://\d{1,3}(\.\d{1,3}){3}', re.IGNORECASE)
# Common trusted TLD+domain shortlist expands over time / via config.
_SUSPICIOUS_TLDS = (".zip", ".mov", ".xyz", ".top", ".click", ".link", ".country")


def _contains_any(text: str, terms: tuple[str, ...]) -> list[str]:
    low = text.lower()
    return [t for t in terms if t in low]


class PhishingDetector:
    def __init__(self, aion: AIONBrainClient | None = None) -> None:
        from backend.ai.aion_client import aion as default_aion

        self.aion = aion or default_aion

    async def analyze(
        self,
        from_address: str,
        subject: str | None,
        body_text: str | None,
        attachments: list[dict] | None = None,
        trusted_domains: set[str] | None = None,
    ) -> SecurityResult:
        subject = subject or ""
        body = body_text or ""
        attachments = attachments or []
        trusted_domains = trusted_domains or set()
        combined = f"{subject}\n{body}"
        factors: list[str] = []
        score = 0

        domain = from_address.split("@")[-1].lower() if "@" in from_address else ""

        # 1) Urgency language
        urgency = _contains_any(combined, _URGENCY_TERMS)
        if urgency:
            score += min(25, 8 * len(urgency))
            factors.append(f"Urgency language: {', '.join(urgency[:3])}")

        # 2) Credential/payment requests
        creds = _contains_any(combined, _CREDENTIAL_TERMS)
        if creds:
            score += min(25, 10 * len(creds))
            factors.append(f"Requests sensitive info: {', '.join(creds[:3])}")

        # 3) Brand impersonation (brand in text but domain mismatch)
        brands = _contains_any(combined, _BRANDS)
        if brands and domain and not any(b in domain for b in brands):
            score += 20
            factors.append(
                f"Mentions brand ({', '.join(brands[:2])}) but sender domain '{domain}' does not match"
            )

        # 4) Suspicious URLs
        urls = _URL_RE.findall(body)
        if _IP_URL_RE.search(body):
            score += 20
            factors.append("Contains raw IP-address URL")
        bad_tld = [u for u in urls if any(u.lower().rstrip("/").endswith(t) for t in _SUSPICIOUS_TLDS)]
        if bad_tld:
            score += 15
            factors.append(f"Suspicious link TLD: {bad_tld[0]}")

        # 5) Attachment risk
        risky_ext = (".exe", ".scr", ".js", ".vbs", ".jar", ".iso", ".html", ".htm")
        for att in attachments:
            name = str(att.get("filename", "")).lower()
            if name.endswith(risky_ext):
                score += 25
                factors.append(f"Risky attachment: {att.get('filename')}")

        # 6) Sender reputation via AION Brain (OpenCorporates)
        sender_rep = None
        if domain and domain not in trusted_domains:
            sender_rep = await self._check_sender(domain)
            if sender_rep.get("status") in {"unknown", "offshore"}:
                score += 10
                factors.append(sender_rep.get("reason", "Sender reputation concern"))

        score = min(100, score)

        # 7) Escalate ambiguous mid-risk to AION Brain critical judgment
        explanation: str | None = None
        if 30 <= score < 90:
            llm = await self._llm_judgment(from_address, subject, body)
            if llm:
                score = max(score, llm.get("risk_score", score))
                explanation = llm.get("explanation")
                if llm.get("factors"):
                    factors.extend(llm["factors"])

        level, action = self._decide(score)
        if not explanation:
            explanation = self._build_explanation(level, factors)

        return SecurityResult(
            risk_score=score,
            risk_level=level,
            event_type="phishing",
            risk_factors=factors,
            explanation=explanation,
            recommended_action=action,
            sender_reputation=sender_rep,
        )

    # ── Helpers ─────────────────────────────────────────────
    async def _check_sender(self, domain: str) -> dict:
        try:
            result = await self.aion.execute_tool(
                "opencorporates_search", {"name": domain}
            )
            if result.get("fallback"):
                return {"status": "unverified", "reason": "Reputation check unavailable"}
            if not result.get("results"):
                return {"status": "unknown", "reason": f"Domain '{domain}' not found in corporate registries"}
            jurisdiction = str(result.get("jurisdiction", "")).lower()
            if any(j in jurisdiction for j in ("bvi", "cayman", "panama")):
                return {"status": "offshore", "reason": f"Sender registered in {jurisdiction}"}
            return {"status": "verified", "company": result.get("results", [])[:1]}
        except Exception as exc:  # noqa: BLE001
            logger.warning("Sender reputation check failed: %s", exc)
            return {"status": "unverified", "reason": "Reputation check error"}

    async def _llm_judgment(self, from_address: str, subject: str, body: str) -> dict | None:
        prompt = (
            "You are a security analyst. Assess phishing risk of this email.\n\n"
            f"From: {from_address}\nSubject: {subject}\n"
            f"Body (truncated):\n{body[:1500]}\n\n"
            "Return ONLY JSON: {\"risk_score\": 0-100, "
            "\"factors\": [\"...\"], \"explanation\": \"why, in plain language\"}"
        )
        try:
            out = await self.aion.orchestrate(prompt=prompt, task_type="critical")
            text = out.get("text", "") if isinstance(out, dict) else str(out)
            import json

            s, e = text.find("{"), text.rfind("}")
            if s == -1 or e <= s:
                return None
            data = json.loads(text[s : e + 1])
            data["risk_score"] = max(0, min(100, int(data.get("risk_score", 0))))
            return data
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM phishing judgment failed: %s", exc)
            return None

    def _decide(self, score: int) -> tuple[RiskLevel, str]:
        if score >= settings.phishing_block_threshold:
            return RiskLevel.DANGEROUS, "block"
        if score >= settings.phishing_quarantine_threshold:
            return RiskLevel.SUSPICIOUS, "quarantine"
        if score >= 30:
            return RiskLevel.SUSPICIOUS, "allow"
        return RiskLevel.SAFE, "allow"

    @staticmethod
    def _build_explanation(level: RiskLevel, factors: list[str]) -> str:
        if level == RiskLevel.SAFE:
            return "No significant phishing indicators detected."
        bullet = "; ".join(factors) if factors else "multiple heuristic signals"
        return f"Flagged as {level.value} because: {bullet}."
