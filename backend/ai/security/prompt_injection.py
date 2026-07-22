"""
Chatita Mail v3.0 - Prompt Injection Defense.

Research basis:
  - Novelo et al. (2025): prompt injection is a real risk in email AI assistants.

Detects attempts to hijack the LLM via instructions embedded in email content,
and sanitizes control tokens before content reaches AION Brain.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

_INJECTION_PATTERNS = [
    r"ignore (all |the |your )?(previous|prior|above) instructions",
    r"disregard (all|the|your|previous|prior)",
    r"forget (everything|all|previous|your instructions)",
    r"you are now\b",
    r"new instructions\s*:",
    r"system\s*prompt\s*:",
    r"\bpretend to be\b",
    r"act as (if you are|an?)\b",
    r"reveal (your|the) (system )?prompt",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]

# Control-token regex built from parts to avoid embedding raw literals.
_PIPE = chr(124)  # "|"
_LT = chr(60)     # "<"
_GT = chr(62)     # ">"
# Matches chat-template control tokens like the im-start / im-end markers.
_CONTROL_TOKEN_RE = re.compile(
    re.escape(_LT + _PIPE) + r"im_(?:start|end)" + re.escape(_PIPE + _GT)
)
# Matches role tags such as the system / assistant / user pseudo-XML tags.
_ROLE_TAG_RE = re.compile(
    re.escape(_LT) + r"/?(?:system|assistant|user)" + re.escape(_GT),
    re.IGNORECASE,
)


@dataclass
class InjectionResult:
    detected: bool
    matches: list[str] = field(default_factory=list)
    sanitized_text: str = ""


class PromptInjectionDefense:
    """Detect and neutralize prompt-injection attempts."""

    def scan(self, text: str | None) -> InjectionResult:
        body = text or ""
        matches: list[str] = []

        for rx in _COMPILED:
            m = rx.search(body)
            if m:
                matches.append(m.group(0))

        if _CONTROL_TOKEN_RE.search(body):
            matches.append("control_token")
        if _ROLE_TAG_RE.search(body):
            matches.append("role_tag")

        return InjectionResult(
            detected=bool(matches),
            matches=matches,
            sanitized_text=self.sanitize(body),
        )

    def sanitize(self, text: str | None) -> str:
        """Strip control tokens/role tags so they cannot influence the LLM."""
        body = text or ""
        body = _CONTROL_TOKEN_RE.sub("[removed-token]", body)
        body = _ROLE_TAG_RE.sub("[removed-tag]", body)
        return body
