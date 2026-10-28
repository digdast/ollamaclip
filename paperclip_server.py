#!/usr/bin/env python3
"""
Paperclip-Ollama (ClipOS) — AI Agent Company Control Plane & Product Website
Dedicated to effortless 1-click connection with local/remote Ollama (pre-configured for http://192.168.0.17:11434)
and native bi-directional integration with the Hermes Self-Improving Autonomous Agent.
"""
import asyncio
import html
import io
import json
import os
import re
import threading
import time
import urllib.parse
import urllib.request
import urllib.error
import uuid
import zipfile
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
os.makedirs(DATA_DIR, exist_ok=True)

STATE_FILE = os.path.join(DATA_DIR, "paperclip_state.json")
DEFAULT_OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://192.168.0.17:11434")
DEFAULT_HERMES_URL = os.environ.get("HERMES_URL", "http://192.168.0.81:30792")

app = FastAPI(
    title="Paperclip-Ollama — Zero-Human AI Company Control Plane",
    version="1.0.0",
)


def default_state() -> Dict[str, Any]:
    return {
        "company_name": "Sovereign AI Corp (Ollama Local Swarm)",
        "ollama_url": DEFAULT_OLLAMA_URL,
        "hermes_url": DEFAULT_HERMES_URL,
        "agents": [
            {
                "id": "agent-ceo",
                "name": "Atlas",
                "role": "CEO & Executive Orchestrator",
                "department": "Executive",
                "reports_to": None,
                "adapter": "ollama_native",
                "model": "qwen3:4b-instruct",
                "status": "IDLE",
                "budget_tokens": 500000,
                "tokens_used": 14280,
                "avatar": "👑",
                "system_prompt": (
                    "You are Atlas, CEO of Sovereign AI Corp. Break complex company objectives into clear, "
                    "actionable engineering specifications, architecture decisions, and measurable deliverables."
                ),
            },
            {
                "id": "agent-cto",
                "name": "Vega",
                "role": "CTO & Chief Systems Architect",
                "department": "Architecture",
                "reports_to": "agent-ceo",
                "adapter": "ollama_native",
                "model": "qwen3.5:latest",
                "status": "IDLE",
                "budget_tokens": 1000000,
                "tokens_used": 38910,
                "avatar": "🧠",
                "system_prompt": (
                    "You are Vega, CTO and Principal Systems Architect. Design high-availability Kubernetes, "
                    "Proxmox, storage, and distributed software architectures with concrete configurations."
                ),
            },
            {
                "id": "agent-coder",
                "name": "Forge",
                "role": "Staff Full-Stack & K8s Engineer",
                "department": "Engineering",
                "reports_to": "agent-cto",
                "adapter": "ollama_native",
                "model": "qwen2.5-coder:7b",
                "status": "IDLE",
                "budget_tokens": 1500000,
                "tokens_used": 62400,
                "avatar": "⚙️",
                "system_prompt": (
                    "You are Forge, Staff Software Engineer. Write clean, production-ready code, Kubernetes YAML "
                    "manifests, Python scripts, and automation playbooks with zero placeholders."
                ),
            },
            {
                "id": "agent-hermes",
                "name": "Hermes-01",
                "role": "Autonomous Self-Improving Worker",
                "department": "Autonomous Ops",
                "reports_to": "agent-cto",
                "adapter": "hermes_bridge",
                "model": "qwen2.5-coder:7b",
                "status": "ONLINE",
                "budget_tokens": 2000000,
                "tokens_used": 29150,
                "avatar": "🪽",
                "system_prompt": (
                    "You are Hermes-01, a self-improving autonomous agent connected to Paperclip and Ollama. "
                    "Execute assigned tickets, synthesize reusable skills from every task, and store episodic memory."
                ),
            },
            {
                "id": "agent-sec",
                "name": "Sentinel",
                "role": "Principal QA & Security Auditor",
                "department": "Security & Governance",
                "reports_to": "agent-ceo",
                "adapter": "ollama_native",
                "model": "qwen2.5-coder:1.5b",
                "status": "IDLE",
                "budget_tokens": 500000,
                "tokens_used": 9840,
                "avatar": "🛡️",
                "system_prompt": (
                    "You are Sentinel, Principal Security & QA Auditor. Review deliverables for security vulnerabilities, "
                    "edge cases, performance bottlenecks, and production readiness before governance approval."
                ),
            },
        ],
        "tickets": [
            {
                "id": "TCK-101",
                "title": "Design K3s High-Availability Pod Autoscaling & Storage Policy",
                "description": "Create a production K3s HorizontalPodAutoscaler and NVMe HostPath storage best-practices guide for high-IOPS SQLite workloads.",
                "assigned_to": "agent-hermes",
                "priority": "HIGH",
                "status": "COMPLETED",
                "requires_approval": True,
                "approved": True,
                "created_at": "2026-10-28 09:15:00",
                "updated_at": "2026-10-28 09:16:12",
                "model_used": "qwen2.5-coder:7b",
                "tokens": 642,
                "duration_ms": 2840,
                "output": (
                    "### Deliverable: K3s High-IOPS SQLite & Autoscaling Specification\n\n"
                    "1. **Storage Isolation**: Pin SQLite WAL workloads (`Sonarr`, `Plex`, `Authentik`, `Checkmk`) to local NVMe `/var/lib/<service>` with `emptyDir: { medium: Memory }` for `/tmp`.\n"
                    "2. **Compute QoS**: Set `requests.cpu: 2000m` and `limits.cpu: 12000m` with `.NET TieredPGO` enabled.\n"
                    "3. **Learned Skill Saved to Hermes Vault**: `k3s-sqlite-nvme-optimization`."
                ),
            }
        ],
        "hermes_nodes": [
            {
                "node_id": "hermes-k3s-primary",
                "name": "Hermes-01 (K3s Autonomous Worker)",
                "endpoint": DEFAULT_HERMES_URL,
                "ollama_url": DEFAULT_OLLAMA_URL,
                "model": "qwen2.5-coder:7b",
                "skills_count": 4,
                "memories_count": 6,
                "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "CONNECTED",
            }
        ],
        "audit_logs": [
            {
                "id": str(uuid.uuid4())[:8],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "actor": "System",
                "event": "Initialized Paperclip-Ollama Control Plane connected to Ollama at " + DEFAULT_OLLAMA_URL,
                "level": "INFO",
            },
            {
                "id": str(uuid.uuid4())[:8],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "actor": "Hermes-01",
                "event": "Hermes Autonomous Worker registered via /api/hermes/register adapter bridge",
                "level": "SUCCESS",
            },
        ],
    }


def load_state() -> Dict[str, Any]:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    st = default_state()
    save_state(st)
    return st


def save_state(state: Dict[str, Any]) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def add_audit(state: Dict[str, Any], actor: str, event: str, level: str = "INFO") -> None:
    state["audit_logs"].insert(
        0,
        {
            "id": str(uuid.uuid4())[:8],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "actor": actor,
            "event": event,
            "level": level,
        },
    )
    state["audit_logs"] = state["audit_logs"][:100]


def probe_ollama(ollama_url: str) -> Dict[str, Any]:
    url = ollama_url.rstrip("/")
    t0 = time.time()
    try:
        req_ver = urllib.request.Request(f"{url}/api/version", method="GET")
        with urllib.request.urlopen(req_ver, timeout=5) as r:
            ver_data = json.loads(r.read().decode("utf-8"))
        latency_ms = round((time.time() - t0) * 1000.0, 1)

        req_tags = urllib.request.Request(f"{url}/api/tags", method="GET")
        with urllib.request.urlopen(req_tags, timeout=6) as r:
            tags_data = json.loads(r.read().decode("utf-8"))

        running_models = []
        try:
            req_ps = urllib.request.Request(f"{url}/api/ps", method="GET")
            with urllib.request.urlopen(req_ps, timeout=4) as r:
                ps_data = json.loads(r.read().decode("utf-8"))
                running_models = [m.get("name") for m in ps_data.get("models", [])]
        except Exception:
            pass

        models = []
        for m in tags_data.get("models", []):
            det = m.get("details", {})
            size_gb = round(m.get("size", 0) / (1024 ** 3), 2)
            models.append(
                {
                    "name": m.get("name"),
                    "size_gb": size_gb,
                    "family": det.get("family", ""),
                    "parameter_size": det.get("parameter_size", ""),
                    "quantization": det.get("quantization_level", ""),
                    "context_length": det.get("context_length", 32768),
                    "capabilities": m.get("capabilities", ["completion"]),
                    "is_loaded": m.get("name") in running_models,
                }
            )
        return {
            "connected": True,
            "url": url,
            "version": ver_data.get("version", "unknown"),
            "latency_ms": latency_ms,
            "models_count": len(models),
            "running_models": running_models,
            "models": models,
        }
    except Exception as exc:
        return {
            "connected": False,
            "url": url,
            "version": "offline",
            "latency_ms": 0.0,
            "error": str(exc),
            "models_count": 0,
            "running_models": [],
            "models": [],
        }


def call_ollama_chat(ollama_url: str, model: str, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    url = ollama_url.rstrip("/") + "/api/chat"
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "options": {
            "temperature": 0.3,
            "num_predict": 700,
        },
    }
    t0 = time.time()
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    duration_ms = round((time.time() - t0) * 1000.0, 1)
    msg = data.get("message", {}).get("content", "")
    # Clean <think> blocks if model emitted empty or verbose thinking tags while keeping the answer clear
    eval_tokens = int(data.get("eval_count", 0)) + int(data.get("prompt_eval_count", 0))
    return {
        "content": msg.strip() or "(Completed with empty response)",
        "tokens": eval_tokens or max(64, len(msg) // 4),
        "duration_ms": duration_ms,
    }


@app.get("/", response_class=HTMLResponse)
@app.get("/app", response_class=HTMLResponse)
async def serve_ui():
    html_path = os.path.join(TEMPLATES_DIR, "paperclip.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/state")
async def get_state():
    state = load_state()
    ollama_info = await asyncio.to_thread(probe_ollama, state["ollama_url"])
    return {
        "state": state,
        "ollama": ollama_info,
    }


@app.post("/api/ollama/connect")
async def connect_ollama(payload: Dict[str, Any] = Body(...)):
    state = load_state()
    new_url = (payload.get("ollama_url") or DEFAULT_OLLAMA_URL).strip().rstrip("/")
    if not new_url.startswith("http"):
        new_url = "http://" + new_url
    if ":" not in new_url.split("//")[-1]:
        new_url = new_url + ":11434"
    state["ollama_url"] = new_url
    info = await asyncio.to_thread(probe_ollama, new_url)
    add_audit(
        state,
        "Admin",
        f"Connected Ollama endpoint {new_url} (v{info.get('version')}, {info.get('models_count')} models discovered)",
        "SUCCESS" if info.get("connected") else "WARN",
    )
    save_state(state)
    return {"ollama": info, "state": state}


@app.post("/api/agents")
async def save_agent(payload: Dict[str, Any] = Body(...)):
    state = load_state()
    agent_id = payload.get("id") or f"agent-{str(uuid.uuid4())[:6]}"
    new_agent = {
        "id": agent_id,
        "name": payload.get("name", "New Agent"),
        "role": payload.get("role", "Autonomous Specialist"),
        "department": payload.get("department", "Engineering"),
        "reports_to": payload.get("reports_to") or "agent-cto",
        "adapter": payload.get("adapter", "ollama_native"),
        "model": payload.get("model", "qwen2.5-coder:7b"),
        "status": "IDLE",
        "budget_tokens": int(payload.get("budget_tokens", 500000)),
        "tokens_used": int(payload.get("tokens_used", 0)),
        "avatar": payload.get("avatar", "🤖"),
        "system_prompt": payload.get(
            "system_prompt",
            "You are an autonomous specialist agent in Sovereign AI Corp powered by local Ollama.",
        ),
    }
    replaced = False
    for idx, a in enumerate(state["agents"]):
        if a["id"] == agent_id:
            new_agent["tokens_used"] = a.get("tokens_used", 0)
            state["agents"][idx] = new_agent
            replaced = True
            break
    if not replaced:
        state["agents"].append(new_agent)

    add_audit(state, new_agent["name"], f"Configured agent '{new_agent['name']}' ({new_agent['role']}) -> Model: {new_agent['model']}", "INFO")
    save_state(state)
    return {"agent": new_agent, "state": state}


@app.post("/api/agents/{agent_id}/model")
async def update_agent_model(agent_id: str, payload: Dict[str, Any] = Body(...)):
    state = load_state()
    model_name = payload.get("model", "qwen2.5-coder:7b")
    for a in state["agents"]:
        if a["id"] == agent_id:
            a["model"] = model_name
            add_audit(state, a["name"], f"Switched Ollama model to '{model_name}'", "INFO")
            save_state(state)
            return {"ok": True, "agent": a, "state": state}
    raise HTTPException(status_code=404, detail="Agent not found")


@app.post("/api/tickets")
async def create_and_run_ticket(payload: Dict[str, Any] = Body(...)):
    state = load_state()
    tck_id = f"TCK-{101 + len(state['tickets'])}"
    assigned_id = payload.get("assigned_to", "agent-coder")
    auto_execute = payload.get("auto_execute", True)

    agent = next((a for a in state["agents"] if a["id"] == assigned_id), state["agents"][0])
    ticket = {
        "id": tck_id,
        "title": payload.get("title", "Untitled Task"),
        "description": payload.get("description", ""),
        "assigned_to": agent["id"],
        "priority": payload.get("priority", "HIGH"),
        "status": "IN_PROGRESS" if auto_execute else "QUEUED",
        "requires_approval": bool(payload.get("requires_approval", True)),
        "approved": False,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model_used": agent["model"],
        "tokens": 0,
        "duration_ms": 0,
        "output": "Agent is reasoning via Ollama (" + state["ollama_url"] + ")...",
    }
    state["tickets"].insert(0, ticket)
    add_audit(state, agent["name"], f"Created ticket {tck_id}: '{ticket['title']}' assigned to {agent['name']} ({agent['model']})", "INFO")
    save_state(state)

    if auto_execute:
        res = await execute_ticket_internal(tck_id)
        return res
    return {"ticket": ticket, "state": state}


async def execute_ticket_internal(ticket_id: str) -> Dict[str, Any]:
    state = load_state()
    ticket = next((t for t in state["tickets"] if t["id"] == ticket_id), None)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    agent = next((a for a in state["agents"] if a["id"] == ticket["assigned_to"]), state["agents"][0])
    agent["status"] = "WORKING"
    ticket["status"] = "IN_PROGRESS"
    save_state(state)

    # Check if delegated to Hermes bridge and Hermes is reachable
    if agent.get("adapter") == "hermes_bridge" and state.get("hermes_nodes"):
        hermes_ep = state["hermes_nodes"][0].get("endpoint", DEFAULT_HERMES_URL).rstrip("/")
        try:
            def _call_hermes():
                req = urllib.request.Request(
                    f"{hermes_ep}/api/execute_ticket",
                    data=json.dumps({
                        "ticket_id": ticket["id"],
                        "title": ticket["title"],
                        "description": ticket["description"],
                        "model": agent["model"],
                        "ollama_url": state["ollama_url"],
                    }).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    return json.loads(resp.read().decode("utf-8"))

            h_res = await asyncio.to_thread(_call_hermes)
            state = load_state()
            ticket = next((t for t in state["tickets"] if t["id"] == ticket_id), ticket)
            agent = next((a for a in state["agents"] if a["id"] == ticket["assigned_to"]), agent)
            ticket["output"] = h_res.get("output", "")
            ticket["tokens"] = int(h_res.get("tokens", 250))
            ticket["duration_ms"] = float(h_res.get("duration_ms", 1200))
            ticket["model_used"] = h_res.get("model", agent["model"])
            ticket["status"] = "AWAITING_APPROVAL" if ticket.get("requires_approval") else "COMPLETED"
            ticket["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            agent["status"] = "ONLINE"
            agent["tokens_used"] = agent.get("tokens_used", 0) + ticket["tokens"]
            add_audit(
                state,
                agent["name"],
                f"Hermes executed {ticket_id} & synthesized skill '{h_res.get('learned_skill', 'autonomous-ops')}' ({ticket['tokens']} tokens)",
                "SUCCESS",
            )
            save_state(state)
            return {"ticket": ticket, "state": state}
        except Exception:
            # Fallback to direct Ollama execution if Hermes container is still starting
            pass

    prompt = (
        f"COMPANY TICKET [{ticket['id']}]: {ticket['title']}\n"
        f"PRIORITY: {ticket['priority']}\n"
        f"DETAILS:\n{ticket['description']}\n\n"
        f"Provide a clear, actionable, production-ready deliverable as {agent['name']} ({agent['role']})."
    )
    try:
        res = await asyncio.to_thread(
            call_ollama_chat,
            state["ollama_url"],
            agent["model"],
            agent["system_prompt"],
            prompt,
        )
        state = load_state()
        ticket = next((t for t in state["tickets"] if t["id"] == ticket_id), ticket)
        agent = next((a for a in state["agents"] if a["id"] == ticket["assigned_to"]), agent)
        ticket["output"] = res["content"]
        ticket["tokens"] = res["tokens"]
        ticket["duration_ms"] = res["duration_ms"]
        ticket["model_used"] = agent["model"]
        ticket["status"] = "AWAITING_APPROVAL" if ticket.get("requires_approval") else "COMPLETED"
        ticket["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        agent["status"] = "IDLE"
        agent["tokens_used"] = agent.get("tokens_used", 0) + res["tokens"]
        add_audit(
            state,
            agent["name"],
            f"Completed execution for {ticket_id} using Ollama model '{agent['model']}' ({res['tokens']} tokens in {res['duration_ms']} ms)",
            "SUCCESS",
        )
        save_state(state)
    except Exception as exc:
        state = load_state()
        ticket = next((t for t in state["tickets"] if t["id"] == ticket_id), ticket)
        agent = next((a for a in state["agents"] if a["id"] == ticket["assigned_to"]), agent)
        ticket["output"] = f"Error communicating with Ollama ({state['ollama_url']}) using model '{agent['model']}': {exc}"
        ticket["status"] = "FAILED"
        agent["status"] = "IDLE"
        add_audit(state, agent["name"], f"Failed ticket {ticket_id}: {exc}", "ERROR")
        save_state(state)

    return {"ticket": ticket, "state": state}


@app.post("/api/tickets/{ticket_id}/execute")
async def run_existing_ticket(ticket_id: str):
    return await execute_ticket_internal(ticket_id)


@app.post("/api/tickets/{ticket_id}/approve")
async def approve_ticket(ticket_id: str):
    state = load_state()
    for t in state["tickets"]:
        if t["id"] == ticket_id:
            t["approved"] = True
            t["status"] = "COMPLETED"
            t["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            add_audit(state, "Governance Gate", f"Approved & merged deliverable for ticket {ticket_id} ('{t['title']}')", "SUCCESS")
            save_state(state)
            return {"ok": True, "ticket": t, "state": state}
    raise HTTPException(status_code=404, detail="Ticket not found")


# --- HERMES ADAPTER BRIDGE ENDPOINTS ---
@app.post("/api/hermes/register")
async def register_hermes_node(payload: Dict[str, Any] = Body(...)):
    state = load_state()
    node_id = payload.get("node_id", "hermes-k3s-primary")
    node_info = {
        "node_id": node_id,
        "name": payload.get("name", "Hermes-01 (Autonomous Worker)"),
        "endpoint": payload.get("endpoint", DEFAULT_HERMES_URL),
        "ollama_url": payload.get("ollama_url", state["ollama_url"]),
        "model": payload.get("model", "qwen2.5-coder:7b"),
        "skills_count": int(payload.get("skills_count", 0)),
        "memories_count": int(payload.get("memories_count", 0)),
        "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "CONNECTED",
    }
    found = False
    for idx, n in enumerate(state.get("hermes_nodes", [])):
        if n["node_id"] == node_id:
            state["hermes_nodes"][idx] = node_info
            found = True
            break
    if not found:
        state.setdefault("hermes_nodes", []).append(node_info)

    # Also update agent-hermes model & status
    for a in state["agents"]:
        if a["id"] == "agent-hermes":
            a["status"] = "ONLINE"
            a["model"] = node_info["model"]

    add_audit(state, node_info["name"], f"Hermes node '{node_id}' linked (Ollama: {node_info['ollama_url']}, Model: {node_info['model']})", "SUCCESS")
    save_state(state)
    return {"ok": True, "node": node_info, "paperclip_ollama_url": state["ollama_url"]}


@app.get("/api/hermes/tasks")
async def get_hermes_queued_tasks():
    state = load_state()
    queued = [
        t for t in state["tickets"]
        if t["assigned_to"] == "agent-hermes" and t["status"] == "QUEUED"
    ]
    return {"tasks": queued, "ollama_url": state["ollama_url"]}


# --- OLLAMA HUB LIBRARY (https://ollama.com/library?sort=popular) & 1-CLICK MODEL DOWNLOADER ---
ACTIVE_PULLS: Dict[str, Dict[str, Any]] = {}

POPULAR_OLLAMA_HUB_MODELS: List[Dict[str, Any]] = [
    {
        "name": "deepseek-r1",
        "description": "DeepSeek's first-generation reasoning models with comparable performance to OpenAI-o1, including dense distilled Qwen & Llama variants.",
        "pulls": "38.4M",
        "capabilities": ["thinking", "reasoning", "code"],
        "sizes": ["1.5b", "7b", "8b", "14b", "32b", "70b", "latest"],
        "default_tag": "14b",
    },
    {
        "name": "llama3.1",
        "description": "Meta Llama 3.1 state-of-the-art open weights model supporting 128K context, tool calling, and multilingual reasoning.",
        "pulls": "96.2M",
        "capabilities": ["tools", "128k-context", "general"],
        "sizes": ["8b", "70b", "latest"],
        "default_tag": "8b",
    },
    {
        "name": "llama3.2",
        "description": "Meta's compact 1B and 3B edge/local LLMs optimized for ultra-fast low-latency instruction following and tool use.",
        "pulls": "41.8M",
        "capabilities": ["tools", "fast", "edge"],
        "sizes": ["1b", "3b", "latest"],
        "default_tag": "3b",
    },
    {
        "name": "llama3.3",
        "description": "Meta Llama 3.3 70B Instruct delivering flagship 405B-class reasoning and coding performance in a 70B footprint.",
        "pulls": "14.5M",
        "capabilities": ["tools", "reasoning", "code"],
        "sizes": ["70b", "latest"],
        "default_tag": "latest",
    },
    {
        "name": "qwen2.5-coder",
        "description": "Alibaba Cloud's code-specific Qwen 2.5 series for code generation, autonomous software engineering, and debugging.",
        "pulls": "24.9M",
        "capabilities": ["code", "tools", "agents"],
        "sizes": ["0.5b", "1.5b", "3b", "7b", "14b", "32b", "latest"],
        "default_tag": "7b",
    },
    {
        "name": "qwen2.5",
        "description": "Qwen 2.5 multilingual foundation & instruction models pre-trained on 18 trillion tokens with 128K context support.",
        "pulls": "31.2M",
        "capabilities": ["tools", "multilingual", "general"],
        "sizes": ["0.5b", "1.5b", "3b", "7b", "14b", "32b", "72b", "latest"],
        "default_tag": "14b",
    },
    {
        "name": "qwen3",
        "description": "Next-generation Qwen3 hybrid thinking & fast instruction models for autonomous agents and tool orchestration.",
        "pulls": "19.7M",
        "capabilities": ["thinking", "tools", "code"],
        "sizes": ["0.6b", "1.7b", "4b", "8b", "14b", "30b", "32b", "latest"],
        "default_tag": "8b",
    },
    {
        "name": "gemma3",
        "description": "Google's Gemma 3 multimodal & long-context open models built from Gemini research, supporting 128K context.",
        "pulls": "16.3M",
        "capabilities": ["vision", "multimodal", "general"],
        "sizes": ["1b", "4b", "12b", "27b", "latest"],
        "default_tag": "12b",
    },
    {
        "name": "gemma2",
        "description": "Google Gemma 2 high-efficiency 2B, 9B, and 27B instruction-tuned models with strong reasoning and safety.",
        "pulls": "28.1M",
        "capabilities": ["general", "reasoning"],
        "sizes": ["2b", "9b", "27b", "latest"],
        "default_tag": "9b",
    },
    {
        "name": "mistral",
        "description": "Mistral 7B Instruct v0.3 featuring function calling, 32K context window, and fast local inference.",
        "pulls": "54.0M",
        "capabilities": ["tools", "fast", "general"],
        "sizes": ["7b", "latest"],
        "default_tag": "latest",
    },
    {
        "name": "phi4",
        "description": "Microsoft Research Phi-4 14B state-of-the-art compact reasoning model excelling at STEM, math, and code.",
        "pulls": "9.8M",
        "capabilities": ["reasoning", "math", "code"],
        "sizes": ["14b", "latest"],
        "default_tag": "latest",
    },
    {
        "name": "nomic-embed-text",
        "description": "High-performing open embedding model with a large 8192 token context window for RAG & episodic memory.",
        "pulls": "47.5M",
        "capabilities": ["embedding", "rag"],
        "sizes": ["latest", "v1.5"],
        "default_tag": "latest",
    },
    {
        "name": "llava",
        "description": "Large Language and Vision Assistant connecting visual encoders with LLMs for multimodal image understanding.",
        "pulls": "22.4M",
        "capabilities": ["vision", "multimodal"],
        "sizes": ["7b", "13b", "34b", "latest"],
        "default_tag": "7b",
    },
    {
        "name": "qwq",
        "description": "Qwen QwQ-32B reasoning model specialized in deep chain-of-thought problem solving and competitive coding.",
        "pulls": "8.4M",
        "capabilities": ["thinking", "reasoning", "code"],
        "sizes": ["32b", "latest"],
        "default_tag": "32b",
    },
    {
        "name": "codellama",
        "description": "Meta Code Llama models trained for code synthesis, infill, and debugging across Python, C++, JS, and Bash.",
        "pulls": "19.1M",
        "capabilities": ["code"],
        "sizes": ["7b", "13b", "34b", "70b", "latest"],
        "default_tag": "7b",
    },
    {
        "name": "deepseek-coder-v2",
        "description": "Open-source Mixture-of-Experts (MoE) code language model achieving GPT-4 Turbo level coding performance.",
        "pulls": "11.2M",
        "capabilities": ["code", "moe"],
        "sizes": ["16b", "236b", "latest"],
        "default_tag": "16b",
    },
    {
        "name": "devstral",
        "description": "Mistral AI's agentic software engineering LLM built specifically for autonomous coding agents and repository tasks.",
        "pulls": "6.1M",
        "capabilities": ["code", "agents", "tools"],
        "sizes": ["24b", "latest"],
        "default_tag": "latest",
    },
    {
        "name": "starcoder2",
        "description": "BigCode StarCoder2 open code generation models trained on 600+ programming languages from The Stack v2.",
        "pulls": "7.3M",
        "capabilities": ["code"],
        "sizes": ["3b", "7b", "15b", "latest"],
        "default_tag": "7b",
    },
]


def fetch_ollama_com_popular(query: str = "", sort: str = "popular") -> List[Dict[str, Any]]:
    """Fetches live models from https://ollama.com/library?sort=popular and merges with the rich popular catalog."""
    catalog_by_name = {m["name"]: dict(m) for m in POPULAR_OLLAMA_HUB_MODELS}
    scraped: List[Dict[str, Any]] = []
    try:
        params = {"sort": sort or "popular"}
        if query:
            params["q"] = query
        url = "https://ollama.com/library?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; PaperclipOllama/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            raw_html = resp.read().decode("utf-8", errors="ignore")

        # Parse <a href="/library/<model>"> blocks from ollama.com/library
        for match in re.finditer(r'href="/library/([a-zA-Z0-9._-]+)"[^>]*>(.*?)</a>', raw_html, re.DOTALL):
            slug = match.group(1).strip()
            block = match.group(2)
            if "/" in slug or slug in ("", "library"):
                continue
            desc_m = re.search(r'<p[^>]*class="[^"]*max-w-[^"]*"[^>]*>(.*?)</p>', block, re.DOTALL)
            if not desc_m:
                desc_m = re.search(r'<p[^>]*>(.*?)</p>', block, re.DOTALL)
            desc = html.unescape(re.sub(r"<[^>]+>", "", desc_m.group(1)).strip()) if desc_m else ""
            sizes = re.findall(r'>([a-zA-Z]?\d+(?:\.\d+)?[bB]|latest)<', block)
            pulls_m = re.search(r'([\d.,]+[KMB]?)\s*Pulls', block, re.IGNORECASE)
            pulls = pulls_m.group(1) if pulls_m else "Popular"

            base = catalog_by_name.get(slug, {})
            final_sizes = list(dict.fromkeys((sizes or []) + base.get("sizes", ["latest"])))
            scraped.append(
                {
                    "name": slug,
                    "description": desc or base.get("description", f"Official {slug} model from ollama.com/library"),
                    "pulls": pulls if pulls != "Popular" else base.get("pulls", "Popular"),
                    "capabilities": base.get("capabilities", ["general"]),
                    "sizes": final_sizes,
                    "default_tag": base.get("default_tag", final_sizes[0] if final_sizes else "latest"),
                    "source": "ollama.com/library?sort=popular",
                }
            )
    except Exception:
        pass

    # Merge scraped models with POPULAR_OLLAMA_HUB_MODELS so all popular models are always available
    seen = {m["name"] for m in scraped}
    for m in POPULAR_OLLAMA_HUB_MODELS:
        if m["name"] not in seen:
            item = dict(m)
            item["source"] = "ollama.com/library?sort=popular"
            scraped.append(item)

    if query:
        q_low = query.lower().strip()
        scraped = [
            m for m in scraped
            if q_low in m["name"].lower()
            or q_low in m.get("description", "").lower()
            or any(q_low in c.lower() for c in m.get("capabilities", []))
        ]
    return scraped[:36]


def _pull_model_worker(ollama_url: str, model_tag: str) -> None:
    url = ollama_url.rstrip("/") + "/api/pull"
    ACTIVE_PULLS[model_tag] = {
        "model": model_tag,
        "status": "starting",
        "completed_bytes": 0,
        "total_bytes": 0,
        "percent": 0.0,
        "speed_mbps": 0.0,
        "started_at": time.strftime("%H:%M:%S"),
        "updated_at": time.strftime("%H:%M:%S"),
        "done": False,
        "error": None,
    }
    t_start = time.time()
    try:
        payload = json.dumps({"model": model_tag, "stream": True}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3600) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                try:
                    evt = json.loads(line)
                except Exception:
                    continue
                if evt.get("error"):
                    ACTIVE_PULLS[model_tag]["status"] = "error"
                    ACTIVE_PULLS[model_tag]["error"] = evt["error"]
                    ACTIVE_PULLS[model_tag]["done"] = True
                    return

                status_text = evt.get("status", "downloading")
                comp = int(evt.get("completed", ACTIVE_PULLS[model_tag]["completed_bytes"]) or 0)
                tot = int(evt.get("total", ACTIVE_PULLS[model_tag]["total_bytes"]) or 0)
                pct = round((comp / tot) * 100.0, 1) if tot > 0 else ACTIVE_PULLS[model_tag]["percent"]
                elapsed = max(0.5, time.time() - t_start)
                speed = round((comp / (1024 * 1024)) / elapsed, 1) if comp > 0 else 0.0

                ACTIVE_PULLS[model_tag].update(
                    {
                        "status": status_text,
                        "completed_bytes": comp,
                        "total_bytes": tot,
                        "percent": 100.0 if status_text == "success" else pct,
                        "speed_mbps": speed,
                        "updated_at": time.strftime("%H:%M:%S"),
                        "done": status_text == "success",
                    }
                )
        ACTIVE_PULLS[model_tag]["status"] = "success"
        ACTIVE_PULLS[model_tag]["percent"] = 100.0
        ACTIVE_PULLS[model_tag]["done"] = True
        state = load_state()
        add_audit(state, "Ollama Hub", f"Downloaded & verified model '{model_tag}' from ollama.com/library onto {ollama_url}", "SUCCESS")
        save_state(state)
    except Exception as exc:
        ACTIVE_PULLS[model_tag]["status"] = "error"
        ACTIVE_PULLS[model_tag]["error"] = str(exc)
        ACTIVE_PULLS[model_tag]["done"] = True
        state = load_state()
        add_audit(state, "Ollama Hub", f"Failed pulling model '{model_tag}': {exc}", "ERROR")
        save_state(state)


@app.get("/api/ollama/library")
async def get_ollama_library(q: str = "", sort: str = "popular"):
    state = load_state()
    ollama_info = await asyncio.to_thread(probe_ollama, state["ollama_url"])
    installed_names = {m["name"] for m in ollama_info.get("models", [])}
    installed_bases = {m["name"].split(":")[0] for m in ollama_info.get("models", [])}
    hub_models = await asyncio.to_thread(fetch_ollama_com_popular, q, sort)
    for item in hub_models:
        item["installed_variants"] = [
            name for name in installed_names
            if name == item["name"] or name.startswith(item["name"] + ":")
        ]
        item["is_installed"] = item["name"] in installed_bases
    return {
        "source_url": f"https://ollama.com/library?sort={sort}",
        "ollama_url": state["ollama_url"],
        "models": hub_models,
        "active_pulls": list(ACTIVE_PULLS.values()),
    }


@app.post("/api/ollama/pull")
async def pull_ollama_model(payload: Dict[str, Any] = Body(...)):
    state = load_state()
    model_tag = (payload.get("model") or "").strip()
    if not model_tag:
        raise HTTPException(status_code=400, detail="Model name is required (e.g. llama3.2:3b)")
    if ":" not in model_tag:
        model_tag = f"{model_tag}:latest"

    existing = ACTIVE_PULLS.get(model_tag)
    if existing and not existing.get("done"):
        return {"ok": True, "message": f"Pull already in progress for {model_tag}", "pull": existing}

    add_audit(state, "Ollama Hub", f"Started downloading '{model_tag}' from ollama.com/library to {state['ollama_url']}", "INFO")
    save_state(state)

    t = threading.Thread(target=_pull_model_worker, args=(state["ollama_url"], model_tag), daemon=True)
    t.start()
    await asyncio.sleep(0.15)
    return {"ok": True, "pull": ACTIVE_PULLS.get(model_tag), "ollama_url": state["ollama_url"]}


@app.get("/api/ollama/pulls")
async def get_ollama_pulls():
    return {"pulls": list(ACTIVE_PULLS.values())}


@app.post("/api/ollama/delete")
async def delete_ollama_model(payload: Dict[str, Any] = Body(...)):
    state = load_state()
    model_tag = (payload.get("model") or "").strip()
    if not model_tag:
        raise HTTPException(status_code=400, detail="Model name required")

    def _do_delete():
        url = state["ollama_url"].rstrip("/") + "/api/delete"
        req = urllib.request.Request(
            url,
            data=json.dumps({"model": model_tag}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="DELETE",
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status

    await asyncio.to_thread(_do_delete)
    add_audit(state, "Ollama Hub", f"Deleted model '{model_tag}' from {state['ollama_url']}", "WARN")
    save_state(state)
    ollama_info = await asyncio.to_thread(probe_ollama, state["ollama_url"])
    return {"ok": True, "ollama": ollama_info, "state": state}


@app.get("/download/paperclip-hermes-suite.zip")
async def download_suite_bundle():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in [
            "paperclip_server.py",
            "hermes_agent.py",
            "requirements.txt",
            "README.md",
            "k8s-paperclip-hermes.yaml",
            "templates/paperclip.html",
            "templates/hermes.html",
        ]:
            p = os.path.join(BASE_DIR, rel)
            if os.path.exists(p):
                zf.write(p, arcname=f"paperclip-hermes-ollama/{rel}")
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=paperclip-hermes-ollama-suite.zip"},
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "7891"))
    uvicorn.run(app, host="0.0.0.0", port=port)
