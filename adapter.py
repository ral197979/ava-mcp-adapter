"""
Ava MCP Adapter — REST bridge
──────────────────────────────────────────────────────────────────────────────
Translates JarvisEPC's MCP REST contract (/tools, /execute, /health) into
calls against the deployed Ava_Agent (ava-agent-qzmu.onrender.com), which
in turn routes to CommandDeck specialist brains.

JarvisEPC expects:
  GET  /health                 → {status, ...}
  GET  /tools                  → {tools: [{name, cat, desc, params, live}]}
  POST /execute  {tool, params}→ tool-specific JSON result

Upstream Ava_Agent is authenticated via AVA_AGENT_API_KEY; this adapter is
unauthenticated (JarvisEPC's fetchAva does not send credentials) but runs
in a private relationship with JarvisEPC only. If you need to lock it
down, add an ADAPTER_API_KEY check in the `execute` entry point.

Env:
  AVA_AGENT_URL         default https://ava-agent-qzmu.onrender.com
  AVA_AGENT_API_KEY     required for any endpoint that mutates / reads
                        protected Ava_Agent surface (chat, tasks, memory).
  PORT                  Render-provided
"""
from __future__ import annotations

import os
import time
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

AVA_AGENT_URL = os.environ.get("AVA_AGENT_URL", "https://ava-agent-qzmu.onrender.com").rstrip("/")
AVA_AGENT_API_KEY = os.environ.get("AVA_AGENT_API_KEY", "")
TIMEOUT = float(os.environ.get("AVA_AGENT_TIMEOUT", "30"))

app = FastAPI(title="Ava MCP Adapter", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Tool catalog ─────────────────────────────────────────────────────────────
# JarvisEPC renders these as cards on the MCP tab. Categories map to the
# filter chips: AI, System, Security, Engineering.
TOOLS: list[dict[str, Any]] = [
    {
        "name": "ava_chat",
        "cat": "AI",
        "desc": "Route a question to CommandDeck specialist brains (engineering / math / science).",
        "params": ["query", "context", "preferred_brain"],
    },
    {
        "name": "ava_status",
        "cat": "System",
        "desc": "Ava_Agent orchestrator status: worker counts, project activity.",
        "params": [],
    },
    {
        "name": "ava_projects_list",
        "cat": "System",
        "desc": "List all projects currently registered with Ava_Agent.",
        "params": [],
    },
    {
        "name": "ava_task_submit",
        "cat": "AI",
        "desc": "Queue an agentic task for a registered project worker.",
        "params": ["project_id", "prompt"],
    },
    {
        "name": "ava_broadcast",
        "cat": "AI",
        "desc": "Submit the same prompt to every registered project at once.",
        "params": ["prompt"],
    },
    {
        "name": "ava_memory_recall",
        "cat": "AI",
        "desc": "Semantic recall from a project's long-term memory context.",
        "params": ["project_id", "query", "n"],
    },
    {
        "name": "ava_memory_summary",
        "cat": "AI",
        "desc": "Summary snapshot of a project's memory store.",
        "params": ["project_id"],
    },
    {
        "name": "ava_skill_invoke",
        "cat": "AI",
        "desc": "Invoke any skill in the CommandDeck skills registry by id.",
        "params": ["skill_id", "args"],
    },
    {
        "name": "ava_git_status",
        "cat": "System",
        "desc": "Git status + current branch for a project's workspace.",
        "params": ["project_id"],
    },
    {
        "name": "ava_git_log",
        "cat": "System",
        "desc": "Recent commits for a project's workspace.",
        "params": ["project_id", "n"],
    },
    {
        "name": "ava_git_commit",
        "cat": "System",
        "desc": "Stage + commit a project's workspace; optionally push to remote.",
        "params": ["project_id", "message", "push"],
    },
]


# ── HTTP helper ──────────────────────────────────────────────────────────────
def _headers() -> dict[str, str]:
    h = {"Content-Type": "application/json"}
    if AVA_AGENT_API_KEY:
        h["Authorization"] = f"Bearer {AVA_AGENT_API_KEY}"
    return h


async def _get(path: str, params: dict | None = None) -> Any:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(f"{AVA_AGENT_URL}{path}", headers=_headers(), params=params)
        r.raise_for_status()
        return r.json()


async def _post(path: str, body: dict | None = None, params: dict | None = None) -> Any:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.post(
            f"{AVA_AGENT_URL}{path}",
            headers=_headers(),
            json=body or {},
            params=params,
        )
        r.raise_for_status()
        return r.json()


def _p(params: dict[str, Any], key: str, default: Any = None, required: bool = False) -> Any:
    v = params.get(key, default)
    if required and v is None:
        raise HTTPException(400, f"missing required param: {key}")
    return v


# ── Tool dispatchers ─────────────────────────────────────────────────────────
async def dispatch(tool: str, params: dict[str, Any]) -> Any:
    if tool == "ava_chat":
        body = {
            "query": _p(params, "query", required=True),
            "context": _p(params, "context", ""),
            "preferred_brain": _p(params, "preferred_brain", "auto"),
        }
        return await _post("/chat", body)

    if tool == "ava_status":
        return await _get("/status")

    if tool == "ava_projects_list":
        return await _get("/projects")

    if tool == "ava_task_submit":
        pid = _p(params, "project_id", required=True)
        body = {"prompt": _p(params, "prompt", required=True)}
        return await _post(f"/projects/{pid}/tasks", body)

    if tool == "ava_broadcast":
        return await _post("/broadcast", {"prompt": _p(params, "prompt", required=True)})

    if tool == "ava_memory_recall":
        pid = _p(params, "project_id", required=True)
        return await _post(
            f"/projects/{pid}/memory/recall",
            params={"query": _p(params, "query", required=True), "n": int(_p(params, "n", 5))},
        )

    if tool == "ava_memory_summary":
        pid = _p(params, "project_id", required=True)
        return await _get(f"/projects/{pid}/memory")

    if tool == "ava_skill_invoke":
        return await _post(
            "/v1/skills/invoke",
            {
                "skill_id": _p(params, "skill_id", required=True),
                "args": _p(params, "args", {}),
            },
        )

    if tool == "ava_git_status":
        pid = _p(params, "project_id", required=True)
        return await _get(f"/projects/{pid}/git/status")

    if tool == "ava_git_log":
        pid = _p(params, "project_id", required=True)
        return await _get(f"/projects/{pid}/git/log", params={"n": int(_p(params, "n", 10))})

    if tool == "ava_git_commit":
        pid = _p(params, "project_id", required=True)
        return await _post(
            f"/projects/{pid}/git/commit",
            params={
                "message": _p(params, "message", required=True),
                "push": bool(_p(params, "push", False)),
            },
        )

    raise HTTPException(404, f"unknown tool: {tool}")


# ── REST surface ─────────────────────────────────────────────────────────────
class ExecuteRequest(BaseModel):
    tool: str
    params: dict[str, Any] | None = None


@app.get("/")
async def root() -> dict:
    return {
        "service": "ava-mcp-adapter",
        "version": app.version,
        "upstream": AVA_AGENT_URL,
        "endpoints": ["/health", "/tools", "/execute"],
    }


@app.get("/health")
async def health() -> dict:
    upstream_healthy = False
    upstream_info: dict = {}
    try:
        upstream_info = await _get("/health")
        upstream_healthy = upstream_info.get("status") == "ok"
    except Exception as e:
        upstream_info = {"error": str(e)[:200]}
    return {
        "status": "ok" if upstream_healthy else "degraded",
        "service": "ava-mcp-adapter",
        "version": app.version,
        "upstream": AVA_AGENT_URL,
        "upstream_healthy": upstream_healthy,
        "upstream": upstream_info,
        "tools": len(TOOLS),
    }


@app.get("/tools")
async def tools() -> dict:
    # Mark every tool `live` since the upstream is reachable from this service.
    catalog = [{**t, "live": True} for t in TOOLS]
    return {"tools": catalog, "count": len(catalog), "upstream": AVA_AGENT_URL}


@app.post("/execute")
async def execute(req: ExecuteRequest) -> dict:
    t0 = time.time()
    try:
        result = await dispatch(req.tool, req.params or {})
        return {
            "ok": True,
            "tool": req.tool,
            "result": result,
            "latency_ms": int((time.time() - t0) * 1000),
        }
    except HTTPException:
        raise
    except httpx.HTTPStatusError as e:
        return {
            "ok": False,
            "tool": req.tool,
            "error": f"upstream {e.response.status_code}: {e.response.text[:300]}",
            "latency_ms": int((time.time() - t0) * 1000),
        }
    except Exception as e:
        return {
            "ok": False,
            "tool": req.tool,
            "error": str(e)[:500],
            "latency_ms": int((time.time() - t0) * 1000),
        }
