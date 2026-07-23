"""
Chatita Mail v3.0 — AION Brain client.

Chatita Mail delegates ALL LLM orchestration to AION Brain (already deployed).
Two transports supported:
  - "http"  : REST API (recommended, prod)   -> AION_BRAIN_URL
  - "stdio" : local MCP server via stdio       -> AION_BRAIN_MCP_PATH

If AION Brain is unreachable and AION_ALLOW_FALLBACK is true, a minimal local
heuristic is used so Phase-1 pipelines keep working during development.
"""
from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from backend.config import settings

logger = logging.getLogger("chatita_mail.aion")


class AIONBrainError(Exception):
    """Raised when AION Brain cannot fulfill a request and no fallback applies."""


class AIONBrainClient:
    """Async client for AION Brain orchestration + tool execution."""

    def __init__(
        self,
        mode: str | None = None,
        base_url: str | None = None,
        timeout: int | None = None,
        allow_fallback: bool | None = None,
    ) -> None:
        self.mode = mode or settings.aion_mode
        self.base_url = (base_url or settings.aion_brain_url).rstrip("/")
        self.timeout = timeout or settings.aion_timeout_seconds
        self.allow_fallback = (
            settings.aion_allow_fallback if allow_fallback is None else allow_fallback
        )

    # ── Public API ──────────────────────────────────────────
    async def orchestrate(
        self, prompt: str, task_type: str = "medium", **kwargs: Any
    ) -> dict[str, Any]:
        """
        Send a prompt to AION Brain's intelligent router.

        task_type routes cost/quality:
          simple | medium | complex | critical | search | embedding | classification
        Returns a dict with at least {"text": str} plus provider metadata.
        """
        try:
            if self.mode == "http":
                return await self._orchestrate_http(prompt, task_type, **kwargs)
            return await self._orchestrate_stdio(prompt, task_type, **kwargs)
        except Exception as exc:  # noqa: BLE001
            logger.warning("AION Brain orchestrate failed: %s", exc)
            if self.allow_fallback:
                return self._fallback_response(prompt, task_type)
            raise AIONBrainError(str(exc)) from exc

    async def execute_tool(self, tool: str, params: dict[str, Any]) -> dict[str, Any]:
        """Invoke a specialized AION Brain tool (calendar, telegram, opencorporates, ...)."""
        try:
            if self.mode == "http":
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(
                        f"{self.base_url}/execute_tool",
                        json={"toolName": tool, "parameters": params},
                    )
                    resp.raise_for_status()
                    return resp.json()
            return await self._execute_tool_stdio(tool, params)
        except Exception as exc:  # noqa: BLE001
            logger.warning("AION Brain tool '%s' failed: %s", tool, exc)
            if self.allow_fallback:
                return {"ok": False, "fallback": True, "error": str(exc)}
            raise AIONBrainError(str(exc)) from exc

    async def health(self) -> dict[str, Any]:
        """Check AION Brain connectivity. Never raises."""
        try:
            if self.mode == "http":
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.get(f"{self.base_url}/health")
                    return {
                        "reachable": resp.status_code == 200,
                        "mode": "http",
                        "status_code": resp.status_code,
                        "url": self.base_url,
                    }
            # stdio: a full spawn is heavy for a health probe; report configured.
            return {"reachable": None, "mode": "stdio", "path": settings.aion_brain_mcp_path}
        except Exception as exc:  # noqa: BLE001
            return {"reachable": False, "mode": self.mode, "error": str(exc)}

    # ── HTTP transport ──────────────────────────────────────
    async def _orchestrate_http(
        self, prompt: str, task_type: str, **kwargs: Any
    ) -> dict[str, Any]:
        # AION Brain HTTP contract: {query, taskType, userId, priority}
        payload = {
            "query": prompt,
            "taskType": task_type,
            "userId": kwargs.get("user_id", "chatita-mail"),
            "priority": kwargs.get("priority", "P2"),
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/orchestrate", json=payload)
            resp.raise_for_status()
            return self._normalize(resp.json())

    # ── stdio (MCP) transport ───────────────────────────────
    async def _orchestrate_stdio(
        self, prompt: str, task_type: str, **kwargs: Any
    ) -> dict[str, Any]:
        args = {"query": prompt, "taskType": task_type, **kwargs}
        result = await self._call_mcp_tool("aion_orchestrate", args)
        return self._normalize(result)

    # Sentinel values AION Brain uses in its top-level "result" field that are
    # status flags, NOT the model's textual answer.
    _RESULT_FLAGS = {"error", "success", "policy_violation", "ok", "completed"}

    @classmethod
    def _normalize(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Map AION Brain's orchestrate response to Chatita Mail's expected shape.

        AION Brain's HTTP pipeline has evolved across versions and returns the
        model answer in different places depending on the path:
          - data["execution"]["output"]   (tool-augmented / older shape)
          - data["output"]                (12-layer pipeline success shape)
          - data["result"]                (plain-text paths; but can be a flag)
          - data["text"]                  (some direct paths)
        We also detect error/policy states (data["error"] or result == "error")
        so callers fall back cleanly instead of treating an error as an answer.
        """
        if not isinstance(data, dict):
            return {"text": str(data), "ok": bool(data)}

        execution = data.get("execution") or {}
        result_field = data.get("result")

        text = execution.get("output") or data.get("output")
        if not text and isinstance(result_field, str) and result_field not in cls._RESULT_FLAGS:
            text = result_field
        if not text:
            text = data.get("text", "") or ""

        err = data.get("error")
        is_error = bool(err) or result_field == "error" or result_field == "policy_violation"
        ok = (not is_error) and bool(text)

        return {
            "text": text,
            "ok": ok,
            "error": err,
            "result_flag": result_field if isinstance(result_field, str) else None,
            "model": data.get("selectedModel"),
            "provider": execution.get("provider") or data.get("routedApi"),
            "routed_api": data.get("routedApi"),
            "estimated_cost": data.get("estimatedCost"),
            "latency_ms": data.get("totalLatency") or data.get("processingTime"),
            "raw": data,
        }

    async def _execute_tool_stdio(self, tool: str, params: dict[str, Any]) -> dict[str, Any]:
        return await self._call_mcp_tool(tool, params)

    async def _call_mcp_tool(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
        # Imported lazily so HTTP-only deployments don't require the mcp package.
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        params = StdioServerParameters(command="node", args=[settings.aion_brain_mcp_path])
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool, arguments=arguments)
                content = result.content[0].text if result.content else "{}"
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return {"text": content}

    # ── Fallback heuristic (development only) ───────────────
    @staticmethod
    def _fallback_response(prompt: str, task_type: str) -> dict[str, Any]:
        """
        Minimal offline response so pipelines don't crash when AION Brain is down.
        Clearly flagged so it's never mistaken for a real model output.
        """
        return {
            "text": "",
            "fallback": True,
            "task_type": task_type,
            "note": "AION Brain unreachable; returned neutral fallback.",
        }


# Module-level singleton for convenience
aion = AIONBrainClient()
