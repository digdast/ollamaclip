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
                "node_id": "hermes-host-17",
                "name": "Hermes-GPU (plexadmin@192.168.0.17)",
                "endpoint": "http://192.168.0.17:7892",
                "ollama_url": "http://127.0.0.1:11434",
                "model": "qwen2.5-coder:14b",
                "skills_count": 4,
                "memories_count": 6,
                "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "CONNECTED",
            },
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
        "active_hermes_node_id": "hermes-host-17",
        "hermes_ticket_logs": [
            {
                "id": "hlog-init-101",
                "ticket_id": "TCK-101",
                "title": "Design K3s High-Availability Pod Autoscaling & Storage Policy",
                "agent_name": "Hermes-01",
                "node_id": "hermes-k3s-primary",
                "model": "qwen2.5-coder:7b",
                "tokens": 642,
                "tok_per_sec": 71.4,
                "duration_ms": 2840,
                "completed_at": "2026-10-28 09:16:12",
                "learned_skill": "k3s-sqlite-nvme-optimization",
                "memory_summary": "Pinned SQLite WAL workloads to local NVMe hostPath to prevent NFS lock contention.",
                "steps": [
                    {"step": "Task Ingested", "time": "0.0s", "detail": "Paperclip assigned TCK-101 to Hermes-01"},
                    {"step": "Skills Vault Prime", "time": "0.1s", "detail": "Retrieved 4 skills from Hermes vault"},
                    {"step": "Inference Complete", "time": "2.8s", "detail": "Generated 642 tokens via qwen2.5-coder:7b"},
                    {"step": "Skill Synthesis", "time": "2.9s", "detail": "Synthesized 'k3s-sqlite-nvme-optimization' into vault"},
                ],
                "status": "SUCCESS",
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
        "telegram": {
            "enabled": True,
            "bot_token": os.environ.get("TELEGRAM_BOT_TOKEN", ""),
            "chat_id": os.environ.get("TELEGRAM_CHAT_ID", ""),
            "target_phone": "908-845-3667",
            "bot_username": os.environ.get("TELEGRAM_BOT_USERNAME", ""),
            "notify_on_ticket_completed": True,
            "notify_on_hire": True,
            "status": "CONFIGURED",
            "last_message": None,
        },
    }


def load_state() -> Dict[str, Any]:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                st = json.load(f)
            
            # Ensure telegram configuration exists
            if "telegram" not in st:
                st["telegram"] = {
                    "enabled": True,
                    "bot_token": os.environ.get("TELEGRAM_BOT_TOKEN", ""),
                    "chat_id": os.environ.get("TELEGRAM_CHAT_ID", ""),
                    "target_phone": "908-845-3667",
                    "bot_username": os.environ.get("TELEGRAM_BOT_USERNAME", ""),
                    "notify_on_ticket_completed": True,
                    "notify_on_hire": True,
                    "status": "CONFIGURED",
                    "last_message": None,
                }
            else:
                st["telegram"].setdefault("target_phone", "908-845-3667")
                st["telegram"].setdefault("enabled", True)
                st["telegram"].setdefault("notify_on_ticket_completed", True)
                st["telegram"].setdefault("notify_on_hire", True)
                if not st["telegram"].get("bot_token") and os.environ.get("TELEGRAM_BOT_TOKEN"):
                    st["telegram"]["bot_token"] = os.environ.get("TELEGRAM_BOT_TOKEN")
                if not st["telegram"].get("chat_id") and os.environ.get("TELEGRAM_CHAT_ID"):
                    st["telegram"]["chat_id"] = os.environ.get("TELEGRAM_CHAT_ID")
            
            # Ensure hermes-host-17 is in hermes_nodes
            node_ids = {n.get("node_id") for n in st.get("hermes_nodes", [])}
            if "hermes-host-17" not in node_ids:
                st.setdefault("hermes_nodes", []).insert(0, {
                    "node_id": "hermes-host-17",
                    "name": "Hermes-GPU (plexadmin@192.168.0.17)",
                    "endpoint": "http://192.168.0.17:7892",
                    "ollama_url": "http://127.0.0.1:11434",
                    "model": "qwen2.5-coder:14b",
                    "skills_count": 4,
                    "memories_count": 6,
                    "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "CONNECTED",
                })
            if not st.get("active_hermes_node_id"):
                st["active_hermes_node_id"] = "hermes-host-17"
            
            # Ensure Hermes-17 agent exists in agents
            agent_ids = {a.get("id") for a in st.get("agents", [])}
            if "agent-hermes-17" not in agent_ids:
                st.setdefault("agents", []).append({
                    "id": "agent-hermes-17",
                    "name": "Hermes-17",
                    "role": "Host Autonomous GPU Worker (192.168.0.17)",
                    "department": "Autonomous Ops",
                    "reports_to": "agent-cto",
                    "adapter": "hermes_bridge",
                    "endpoint": "http://192.168.0.17:7892",
                    "model": "qwen2.5-coder:14b",
                    "status": "ONLINE",
                    "budget_tokens": 2000000,
                    "tokens_used": 0,
                    "avatar": "🪽",
                    "system_prompt": "You are Hermes-17, an autonomous self-improving agent running directly on the GPU host at 192.168.0.17. Execute tickets with low latency and synthesize reusable skills."
                })
            return st
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
            "num_predict": 2048,
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
    msg = (data.get("message", {}).get("content") or "").strip()
    thinking = (data.get("message", {}).get("thinking") or "").strip()
    
    # If reasoning model spent tokens in thinking and content is empty, surface the thinking as answer
    if not msg and thinking:
        msg = f"### [Reasoning & Analysis]\n\n{thinking}"
    elif thinking and msg and len(thinking) > 30:
        # Show concise summary of thinking alongside the deliverable
        first_few_thoughts = "\n".join(thinking.splitlines()[:12])
        msg = f"<details><summary>🧠 Thought Process</summary>\n\n{first_few_thoughts}\n\n</details>\n\n{msg}"

    eval_tokens = int(data.get("eval_count", 0)) + int(data.get("prompt_eval_count", 0))
    return {
        "content": msg.strip() or "(Task executed successfully)",
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
@app.post("/api/agents/dispatch")
async def save_agent(payload: Dict[str, Any] = Body(...)):
    state = load_state()
    agent_id = payload.get("id") or f"agent-{str(uuid.uuid4())[:6]}"
    new_agent = {
        "id": agent_id,
        "name": (payload.get("name") or "New Agent").strip(),
        "role": (payload.get("role") or "Autonomous Specialist").strip(),
        "department": (payload.get("department") or "Engineering").strip(),
        "reports_to": payload.get("reports_to") or "agent-cto",
        "adapter": payload.get("adapter") or "ollama_native",
        "model": payload.get("model") or "qwen2.5-coder:7b",
        "status": "ONLINE" if payload.get("adapter") == "hermes_bridge" else "IDLE",
        "budget_tokens": int(payload.get("budget_tokens", 1000000)),
        "tokens_used": int(payload.get("tokens_used", 0)),
        "avatar": payload.get("avatar") or "🤖",
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

    action_word = "Updated" if replaced else "Dispatched new"
    add_audit(
        state,
        new_agent["name"],
        f"{action_word} agent '{new_agent['name']}' ({new_agent['role']}, dept: {new_agent['department']}, adapter: {new_agent['adapter']}) -> Model: {new_agent['model']}",
        "SUCCESS",
    )
    save_state(state)

    # If an initial mission / task was supplied when dispatching the agent, create & execute the ticket automatically
    initial_task = (payload.get("initial_task") or "").strip()
    dispatched_ticket = None
    if initial_task:
        tck_res = await create_and_run_ticket(
            {
                "title": payload.get("initial_task_title") or f"Initial Mission for {new_agent['name']}: {initial_task[:64]}",
                "description": initial_task,
                "assigned_to": new_agent["id"],
                "priority": payload.get("priority", "HIGH"),
                "auto_execute": bool(payload.get("auto_execute", True)),
            }
        )
        dispatched_ticket = tck_res.get("ticket")
        state = tck_res.get("state", load_state())

    return {"ok": True, "agent": new_agent, "ticket": dispatched_ticket, "state": state}


@app.delete("/api/agents/{agent_id}")
async def delete_agent(agent_id: str):
    state = load_state()
    target = next((a for a in state["agents"] if a["id"] == agent_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Agent not found")
    if len(state["agents"]) <= 1:
        raise HTTPException(status_code=400, detail="Cannot remove the last remaining agent in the company")
    state["agents"] = [a for a in state["agents"] if a["id"] != agent_id]
    add_audit(state, "Admin", f"Decommissioned agent '{target['name']}' ({target['role']})", "WARN")
    save_state(state)
    return {"ok": True, "removed": agent_id, "state": state}


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


# --- TELEGRAM AGENT SWARM NOTIFICATION CORE ---
def get_telegram_config(state: Dict[str, Any]) -> Dict[str, Any]:
    tg = state.get("telegram")
    if not isinstance(tg, dict):
        tg = {}
    return {
        "enabled": tg.get("enabled", True),
        "bot_token": tg.get("bot_token") or os.environ.get("TELEGRAM_BOT_TOKEN", ""),
        "chat_id": tg.get("chat_id") or os.environ.get("TELEGRAM_CHAT_ID", ""),
        "target_phone": tg.get("target_phone", "908-845-3667"),
        "bot_username": tg.get("bot_username", ""),
        "notify_on_ticket_completed": tg.get("notify_on_ticket_completed", True),
        "notify_on_hire": tg.get("notify_on_hire", True),
        "status": tg.get("status", "CONFIGURED"),
    }


def send_telegram_raw(bot_token: str, chat_id: str, text: str) -> bool:
    if not bot_token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    chunks = []
    rem = text
    while len(rem) > 3900:
        split_idx = rem.rfind("\n", 0, 3900)
        if split_idx == -1 or split_idx < 1000:
            split_idx = 3900
        chunks.append(rem[:split_idx])
        rem = rem[split_idx:].lstrip()
    if rem:
        chunks.append(rem)

    ok = True
    for c in chunks:
        payload = json.dumps({
            "chat_id": chat_id,
            "text": c,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                pass
        except Exception:
            try:
                payload = json.dumps({"chat_id": chat_id, "text": c}).encode("utf-8")
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=12) as resp:
                    pass
            except Exception:
                ok = False
    return ok


def telegram_notify_sync(text: str) -> bool:
    try:
        st = load_state()
        tg = get_telegram_config(st)
        if not tg.get("enabled"):
            return False
        return send_telegram_raw(tg.get("bot_token"), tg.get("chat_id"), text)
    except Exception:
        return False


async def telegram_notify_async(text: str):
    await asyncio.to_thread(telegram_notify_sync, text)


def handle_cto_autonomous_hiring(ticket: Dict[str, Any], state: Dict[str, Any]) -> Optional[str]:
    """Allows CTO (Vega) and Executive agents to autonomously hire/spawn agents and delegate tasks."""
    title = ticket.get("title", "").strip()
    desc = ticket.get("description", "").strip()
    full_text = f"{title}\n{desc}"
    
    actions = []
    
    # 1. Detect Hiring Intent
    # e.g., "hire jack as systems administrator", "hire hermes worker", "add CTO", "hire a database architect"
    hire_patterns = [
        r'\b(?:hire|add|create|dispatch|onboard)\s+(?:a\s+|an\s+|new\s+)?([a-zA-Z0-9_-]+)(?:\s+as\s+([a-zA-Z0-9\s/&_-]+))?',
        r'\b([a-zA-Z0-9_-]+)\s+as\s+([a-zA-Z0-9\s/&_-]+)',
    ]
    
    for pat in hire_patterns:
        m = re.search(pat, full_text, re.IGNORECASE)
        if m:
            raw_target = m.group(1).strip()
            raw_role = (m.group(2) or "").strip()
            # If target is a generic noun, refine
            is_hermes = "hermes" in raw_target.lower() or "hermes" in raw_role.lower() or "worker" in raw_target.lower()
            if is_hermes:
                hermes_count = len([a for a in state["agents"] if "hermes" in a.get("adapter", "") or "hermes" in a["name"].lower()])
                name = f"Hermes-{hermes_count + 1:02d}"
                role = raw_role.title() if raw_role else "Autonomous Field Worker"
                adapter = "hermes_bridge"
                model = "qwen2.5-coder:14b"
                avatar = "🪽"
                dept = "Autonomous Ops"
            elif raw_target.lower() in ("agent", "worker", "employee", "specialist"):
                name = (raw_role.split()[0] if raw_role else "Specialist").capitalize()
                role = raw_role.title() if raw_role else "Technical Specialist"
                adapter = "ollama_native"
                model = "qwen2.5-coder:7b"
                avatar = "🤖"
                dept = "Engineering"
            else:
                name = raw_target.capitalize()
                role = raw_role.title() if raw_role else "Systems Specialist"
                adapter = "hermes_bridge" if "hermes" in full_text.lower() else "ollama_native"
                model = "qwen2.5-coder:7b"
                avatar = "🪽" if adapter == "hermes_bridge" else "🛠️"
                dept = "Autonomous Ops" if adapter == "hermes_bridge" else "Engineering"
            
            # Check if this agent already exists
            existing = next((a for a in state["agents"] if a["name"].lower() == name.lower()), None)
            if not existing:
                new_ag = {
                    "id": f"agent-{name.lower()}-{str(uuid.uuid4())[:4]}",
                    "name": name,
                    "role": role,
                    "department": dept,
                    "reports_to": "agent-cto",
                    "adapter": adapter,
                    "model": model,
                    "status": "ONLINE" if adapter == "hermes_bridge" else "IDLE",
                    "budget_tokens": 1500000,
                    "tokens_used": 0,
                    "avatar": avatar,
                    "system_prompt": f"You are {name}, {role} at Sovereign AI Corp. Execute engineering tasks and write production-ready code with zero placeholders."
                }
                state["agents"].append(new_ag)
                add_audit(state, "Vega (CTO)", f"Hired & registered new employee '{name}' ({role}) -> Adapter: {adapter}, Model: {model}", "SUCCESS")
                try:
                    tg = get_telegram_config(state)
                    if tg.get("enabled") and tg.get("notify_on_hire") and tg.get("bot_token") and tg.get("chat_id"):
                        tg_msg = (
                            f"🧠 <b>CTO Vega Dispatched New Specialist!</b>\n"
                            f"<b>Name:</b> {avatar} {name} ({role})\n"
                            f"<b>Department:</b> {dept} | <b>Manager:</b> Vega (CTO)\n"
                            f"<b>Model:</b> <code>{model}</code> ({adapter})\n"
                            f"📱 <b>Target Phone:</b> <code>{tg.get('target_phone')}</code>"
                        )
                        asyncio.create_task(telegram_notify_async(tg_msg))
                except Exception:
                    pass
                actions.append(
                    f"✅ **CTO Action: Agent Hired & Onboarded into Sovereign AI Corp**\n"
                    f"- **Employee Name**: `{name}` ({avatar})\n"
                    f"- **Role**: `{role}`\n"
                    f"- **Department**: `{dept}`\n"
                    f"- **Execution Engine**: `{adapter}` ({model})\n"
                    f"- **Manager**: `Vega (CTO)`\n"
                )
            break
            
    # 2. Detect Delegation Intent
    # e.g., "tell jack to create a test vm in pve-00", "ask jack to create vms in pve-00"
    del_m = re.search(r'\b(?:tell|ask|assign|instruct)\s+([a-zA-Z0-9_-]+)\s+to\s+(.+)', full_text, re.IGNORECASE)
    if del_m:
        tgt_name = del_m.group(1).strip().lower()
        instruction = del_m.group(2).strip()
        matched_ag = next((a for a in state["agents"] if a["name"].lower() == tgt_name), None)
        if matched_ag:
            actions.append(
                f"📋 **CTO Action: Delegated Execution to {matched_ag['avatar']} {matched_ag['name']}** (`{matched_ag['role']}`)\n"
                f"- **Assigned Objective**: *{instruction}*\n"
                f"- **Model & Adapter**: `{matched_ag['model']}` via `{matched_ag['adapter']}`\n"
            )
            
    return "\n\n".join(actions) if actions else None


async def execute_ticket_internal(ticket_id: str) -> Dict[str, Any]:
    state = load_state()
    ticket = next((t for t in state["tickets"] if t["id"] == ticket_id), None)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    agent = next((a for a in state["agents"] if a["id"] == ticket["assigned_to"]), state["agents"][0])
    agent["status"] = "WORKING"
    ticket["status"] = "IN_PROGRESS"
    save_state(state)

    # If assigned to CTO or CEO, check for autonomous hiring or delegation actions first
    cto_hiring_result = None
    if agent["id"] in ("agent-cto", "agent-ceo"):
        cto_hiring_result = handle_cto_autonomous_hiring(ticket, state)
        if cto_hiring_result:
            save_state(state)

    # Check if delegated to Hermes bridge and Hermes is reachable
    if agent.get("adapter") == "hermes_bridge":
        candidate_eps = []
        if agent.get("endpoint"):
            candidate_eps.append(agent["endpoint"])
            
        active_id = state.get("active_hermes_node_id")
        active_node = next((n for n in state.get("hermes_nodes", []) if n.get("node_id") == active_id), None)
        if active_node and active_node.get("endpoint") and active_node["endpoint"] not in candidate_eps:
            candidate_eps.append(active_node["endpoint"])
            
        for n in state.get("hermes_nodes", []):
            ep = n.get("endpoint")
            if ep and ep not in candidate_eps:
                candidate_eps.append(ep)
                
        fallback_eps = [
            "http://192.168.0.17:7892",
            os.environ.get("HERMES_URL", "http://hermes.ai.svc.cluster.local:7892"),
            "http://hermes.ai.svc.cluster.local:7892",
            "http://192.168.0.81:30792",
            "http://127.0.0.1:7892",
        ]
        for f_ep in fallback_eps:
            if f_ep not in candidate_eps:
                candidate_eps.append(f_ep)

        for hermes_ep in candidate_eps:
            try:
                def _call_hermes():
                    req = urllib.request.Request(
                        f"{hermes_ep.rstrip('/')}/api/execute_ticket",
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
                
                # Attach rich Hermes Ticket Completion Log
                matching_node = next((n for n in state.get("hermes_nodes", []) if n.get("endpoint") == hermes_ep), None)
                matched_node_id = matching_node["node_id"] if matching_node else state.get("active_hermes_node_id", "hermes-host-17")

                c_log = h_res.get("completion_log")
                if not c_log:
                    elapsed_s = max(0.1, round(ticket["duration_ms"] / 1000.0, 2))
                    c_log = {
                        "id": f"hlog-{str(uuid.uuid4())[:8]}",
                        "ticket_id": ticket_id,
                        "title": ticket["title"],
                        "agent_name": agent["name"],
                        "node_id": matched_node_id,
                        "model": ticket["model_used"],
                        "tokens": ticket["tokens"],
                        "tok_per_sec": round(ticket["tokens"] / elapsed_s, 1),
                        "duration_ms": ticket["duration_ms"],
                        "completed_at": ticket["updated_at"],
                        "learned_skill": h_res.get("learned_skill", "autonomous-ops"),
                        "memory_summary": f"Completed ticket {ticket_id} ('{ticket['title']}') and synthesized skill '{h_res.get('learned_skill', 'autonomous-ops')}'.",
                        "steps": [
                            {"step": "Task Ingested", "time": "0.0s", "detail": f"Paperclip assigned {ticket_id} to {agent['name']}"},
                            {"step": "Skills Vault Primed", "time": "0.2s", "detail": f"Primed with skills vault and episodic memory"},
                            {"step": "Inference Complete", "time": f"{elapsed_s}s", "detail": f"Generated {ticket['tokens']} tokens ({ticket['duration_ms']} ms)"},
                            {"step": "Skill Synthesis", "time": f"{elapsed_s}s", "detail": f"Synthesized reusable skill '{h_res.get('learned_skill', 'autonomous-ops')}' into vault"},
                        ],
                        "status": "SUCCESS",
                    }
                else:
                    c_log["node_id"] = matched_node_id
                ticket["hermes_log"] = c_log
                state.setdefault("hermes_ticket_logs", []).insert(0, c_log)
                state["hermes_ticket_logs"] = state["hermes_ticket_logs"][:100]

                add_audit(
                    state,
                    agent["name"],
                    f"Hermes executed {ticket_id} & synthesized skill '{c_log.get('learned_skill', 'autonomous-ops')}' ({ticket['tokens']} tokens in {ticket['duration_ms']} ms)",
                    "SUCCESS",
                )
                save_state(state)
                try:
                    tg = get_telegram_config(state)
                    if tg.get("enabled") and tg.get("notify_on_ticket_completed") and tg.get("bot_token") and tg.get("chat_id"):
                        tg_msg = (
                            f"📎 <b>Ticket Deliverable Ready: {ticket_id}</b>\n"
                            f"<b>Title:</b> {html.escape(ticket['title'])}\n"
                            f"<b>Agent:</b> {agent.get('avatar', '🪽')} {html.escape(agent['name'])} ({html.escape(agent['role'])})\n"
                            f"<b>Node:</b> <code>{matched_node_id}</code> | <b>Model:</b> <code>{ticket.get('model_used')}</code>\n"
                            f"<b>Learned Skill:</b> <code>{c_log.get('learned_skill', 'autonomous-ops')}</code>\n"
                            f"<b>Speed:</b> {ticket.get('tokens')} tokens in {ticket.get('duration_ms')} ms\n\n"
                            f"<b>Deliverable Preview:</b>\n<pre>{html.escape(ticket.get('output', '')[:2800])}</pre>"
                        )
                        asyncio.create_task(telegram_notify_async(tg_msg))
                except Exception:
                    pass
                return {"ticket": ticket, "state": state}
            except Exception:
                continue

    # Ollama execution fallback / direct execution
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
        output_body = res["content"]
        if cto_hiring_result:
            output_body = f"{cto_hiring_result}\n\n### Deliverable & Strategic Direction\n\n{output_body}"
        ticket["output"] = output_body
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
        try:
            tg = get_telegram_config(state)
            if tg.get("enabled") and tg.get("notify_on_ticket_completed") and tg.get("bot_token") and tg.get("chat_id"):
                tg_msg = (
                    f"📎 <b>Ticket Deliverable Ready: {ticket_id}</b>\n"
                    f"<b>Title:</b> {html.escape(ticket['title'])}\n"
                    f"<b>Agent:</b> {agent.get('avatar', '🤖')} {html.escape(agent['name'])} ({html.escape(agent['role'])})\n"
                    f"<b>Model:</b> <code>{ticket.get('model_used')}</code> | <b>Tokens:</b> {ticket.get('tokens')} ({ticket.get('duration_ms')} ms)\n\n"
                    f"<b>Deliverable Preview:</b>\n<pre>{html.escape(ticket.get('output', '')[:2800])}</pre>"
                )
                asyncio.create_task(telegram_notify_async(tg_msg))
        except Exception:
            pass
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
    hermes_agent_ids = {
        a["id"] for a in state["agents"]
        if a.get("adapter") == "hermes_bridge" or a["id"] == "agent-hermes"
    }
    queued = [
        t for t in state["tickets"]
        if t["assigned_to"] in hermes_agent_ids and t["status"] == "QUEUED"
    ]
    return {"tasks": queued, "ollama_url": state["ollama_url"]}


@app.get("/api/hermes/ticket_logs")
async def get_hermes_ticket_completion_logs():
    state = load_state()
    logs = state.get("hermes_ticket_logs", [])
    # Also include any ticket that has a hermes_log
    seen_ids = {l["id"] for l in logs if "id" in l}
    for t in state.get("tickets", []):
        hl = t.get("hermes_log")
        if hl and hl.get("id") and hl["id"] not in seen_ids:
            logs.append(hl)
            seen_ids.add(hl["id"])
    return {"logs": logs, "count": len(logs)}


@app.get("/api/hermes/nodes")
async def get_hermes_nodes():
    state = load_state()
    return {
        "nodes": state.get("hermes_nodes", []),
        "active_node_id": state.get("active_hermes_node_id", "hermes-host-17"),
        "agents": [a for a in state["agents"] if a.get("adapter") == "hermes_bridge"]
    }


@app.post("/api/hermes/nodes/select")
async def select_hermes_node(payload: Dict[str, Any] = Body(...)):
    state = load_state()
    node_id = payload.get("node_id")
    if not node_id:
        raise HTTPException(status_code=400, detail="node_id is required")
    
    target_node = next((n for n in state.get("hermes_nodes", []) if n["node_id"] == node_id), None)
    if not target_node:
        raise HTTPException(status_code=404, detail="Hermes node not found")
        
    state["active_hermes_node_id"] = node_id
    add_audit(state, "Control Plane", f"Switched active Hermes agent connection to '{target_node['name']}' ({target_node['endpoint']})", "INFO")
    save_state(state)
    return {"ok": True, "active_node_id": node_id, "node": target_node, "state": state}


@app.post("/api/hermes/nodes/connect")
async def connect_custom_hermes_node(payload: Dict[str, Any] = Body(...)):
    endpoint = payload.get("endpoint", "").strip().rstrip("/")
    if not endpoint:
        raise HTTPException(status_code=400, detail="Agent endpoint URL is required (e.g. http://192.168.0.17:7892)")
    
    if not (endpoint.startswith("http://") or endpoint.startswith("https://")):
        endpoint = f"http://{endpoint}"
        
    probe_url = f"{endpoint}/api/state"
    remote_data = {}
    try:
        def _probe():
            req = urllib.request.Request(probe_url, headers={"User-Agent": "Paperclip-Probe/1.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                return json.loads(resp.read().decode("utf-8"))
        remote_data = await asyncio.to_thread(_probe)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to probe agent endpoint at {endpoint}: {exc}")

    state = load_state()
    raw_node_id = payload.get("node_id") or remote_data.get("node_id") or f"hermes-{str(uuid.uuid4())[:6]}"
    node_id = re.sub(r'[^a-zA-Z0-9_-]', '-', raw_node_id).lower()
    
    host_label = urllib.parse.urlparse(endpoint).netloc or endpoint
    node_name = payload.get("name") or remote_data.get("agent_name") or f"Hermes ({host_label})"
    remote_model = remote_data.get("model") or "qwen2.5-coder:14b"
    skills_count = len(remote_data.get("skills", []))
    memories_count = len(remote_data.get("episodic_memories", []))
    
    node_info = {
        "node_id": node_id,
        "name": node_name,
        "endpoint": endpoint,
        "ollama_url": remote_data.get("ollama_url", state["ollama_url"]),
        "model": remote_model,
        "skills_count": skills_count,
        "memories_count": memories_count,
        "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "CONNECTED",
    }
    
    existing_idx = next((i for i, n in enumerate(state.get("hermes_nodes", [])) if n["node_id"] == node_id), None)
    if existing_idx is not None:
        state["hermes_nodes"][existing_idx] = node_info
    else:
        state.setdefault("hermes_nodes", []).append(node_info)
        
    state["active_hermes_node_id"] = node_id
    
    agent_id = f"agent-{node_id}"
    agent_found = next((a for a in state["agents"] if a["id"] == agent_id or a.get("endpoint") == endpoint), None)
    if not agent_found:
        state["agents"].append({
            "id": agent_id,
            "name": node_name.split("(")[0].strip() or "Hermes Custom",
            "role": f"Remote Autonomous Worker ({host_label})",
            "department": "Autonomous Ops",
            "reports_to": "agent-cto",
            "adapter": "hermes_bridge",
            "endpoint": endpoint,
            "model": remote_model,
            "status": "ONLINE",
            "budget_tokens": 2000000,
            "tokens_used": 0,
            "avatar": "🪽",
            "system_prompt": f"You are an autonomous agent connected via {endpoint}. Execute tickets and synthesize reusable skills."
        })
    else:
        agent_found["endpoint"] = endpoint
        agent_found["status"] = "ONLINE"
        agent_found["model"] = remote_model

    add_audit(state, "Control Plane", f"Connected new agent node '{node_name}' at {endpoint} (Model: {remote_model}, Skills: {skills_count})", "SUCCESS")
    save_state(state)
    return {"ok": True, "node": node_info, "state": state}


@app.delete("/api/hermes/nodes/{node_id}")
async def unregister_hermes_node(node_id: str):
    state = load_state()
    nodes = state.get("hermes_nodes", [])
    if len(nodes) <= 1:
        raise HTTPException(status_code=400, detail="Cannot remove the last active Hermes node")
    
    target = next((n for n in nodes if n["node_id"] == node_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Node not found")
        
    state["hermes_nodes"] = [n for n in nodes if n["node_id"] != node_id]
    if state.get("active_hermes_node_id") == node_id:
        state["active_hermes_node_id"] = state["hermes_nodes"][0]["node_id"]
        
    add_audit(state, "Control Plane", f"Unregistered agent node '{target['name']}' ({target['endpoint']})", "WARN")
    save_state(state)
    return {"ok": True, "removed": node_id, "state": state}


# --- TELEGRAM BOT TWO-WAY COMMUNICATION BRIDGE ---
TELEGRAM_POLLING_RUNNING: bool = False
TELEGRAM_LAST_UPDATE_OFFSET: int = 0
TELEGRAM_POLL_THREAD: Optional[threading.Thread] = None


def telegram_polling_worker():
    global TELEGRAM_LAST_UPDATE_OFFSET, TELEGRAM_POLLING_RUNNING
    TELEGRAM_POLLING_RUNNING = True
    while TELEGRAM_POLLING_RUNNING:
        try:
            st = load_state()
            tg = get_telegram_config(st)
            token = tg.get("bot_token")
            if not token or not tg.get("enabled"):
                time.sleep(4)
                continue

            url = f"https://api.telegram.org/bot{token}/getUpdates?offset={TELEGRAM_LAST_UPDATE_OFFSET + 1}&timeout=15"
            req = urllib.request.Request(url, headers={"User-Agent": "Paperclip-Ollama-Telegram/1.0"})
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            if not data.get("ok"):
                time.sleep(4)
                continue

            for upd in data.get("result", []):
                TELEGRAM_LAST_UPDATE_OFFSET = max(TELEGRAM_LAST_UPDATE_OFFSET, upd.get("update_id", 0))
                msg = upd.get("message") or upd.get("channel_post")
                if not msg:
                    continue

                chat = msg.get("chat", {})
                chat_id = str(chat.get("id"))
                sender = msg.get("from", {})
                first_name = sender.get("first_name") or sender.get("username") or "Commander"
                raw_text = (msg.get("text") or "").strip()

                # Automatically bind chat_id on first contact
                if st.get("telegram", {}).get("chat_id") != chat_id:
                    st.setdefault("telegram", {})["chat_id"] = chat_id
                    st["telegram"]["status"] = "CONNECTED"
                    st["telegram"]["last_paired_user"] = first_name
                    save_state(st)
                    add_audit(st, "Telegram", f"Paired Telegram bot with {first_name} (Chat ID: {chat_id}, Phone: {tg.get('target_phone')})", "SUCCESS")
                    save_state(st)

                if not raw_text:
                    continue

                if raw_text == "/start" or raw_text.startswith("/start"):
                    welcome = (
                        f"👋 <b>Welcome to Sovereign AI Corp, {html.escape(first_name)}!</b>\n\n"
                        f"Your Telegram account (<code>{tg.get('target_phone')}</code>) is now paired with the <b>Paperclip-Ollama Control Plane</b> and <b>Hermes Agent Swarm</b>.\n\n"
                        f"<b>⚡ Available Commands:</b>\n"
                        f"• <code>/status</code> — Cluster, Ollama &amp; active agent nodes\n"
                        f"• <code>/agents</code> — List active agents and their assigned LLMs\n"
                        f"• <code>/nodes</code> — View registered Hermes workers (Host 17 &amp; K3s)\n"
                        f"• <code>/hire &lt;role&gt;</code> — Instruct CTO Vega to hire a new specialist\n\n"
                        f"💬 <b>Direct Task Execution:</b>\n"
                        f"Simply reply with any engineering objective, coding request, or infrastructure task (e.g. <i>'Check NVMe IOPS on Host 17'</i> or <i>'Write a K3s pod health check script'</i>). Your agents will execute it via local Ollama and return deliverables directly here."
                    )
                    send_telegram_raw(token, chat_id, welcome)

                elif raw_text == "/status" or raw_text.startswith("/status"):
                    st = load_state()
                    active_nid = st.get("active_hermes_node_id")
                    act_node = next((n for n in st.get("hermes_nodes", []) if n["node_id"] == active_nid), None)
                    node_str = f"{act_node['name']} ({act_node['endpoint']})" if act_node else "Default"
                    txt = (
                        f"📊 <b>Sovereign AI Corp Swarm Status</b>\n\n"
                        f"🏢 <b>Company:</b> {html.escape(st.get('company_name', 'Sovereign AI Corp'))}\n"
                        f"🦙 <b>Ollama Backend:</b> <code>{st.get('ollama_url')}</code>\n"
                        f"🪽 <b>Active Agent Node:</b> <code>{node_str}</code>\n"
                        f"🤖 <b>Total Agents:</b> {len(st.get('agents', []))}\n"
                        f"📋 <b>Total Tickets:</b> {len(st.get('tickets', []))}\n"
                        f"📜 <b>Hermes Vault Skills:</b> {len(st.get('hermes_ticket_logs', []))}\n"
                        f"📱 <b>Paired Phone:</b> <code>{tg.get('target_phone')}</code>"
                    )
                    send_telegram_raw(token, chat_id, txt)

                elif raw_text == "/agents" or raw_text.startswith("/agents"):
                    st = load_state()
                    agent_lines = []
                    for a in st.get("agents", []):
                        agent_lines.append(
                            f"{a.get('avatar', '🤖')} <b>{html.escape(a.get('name'))}</b> ({html.escape(a.get('role'))})\n"
                            f"   └ Model: <code>{a.get('model')}</code> | Dept: {a.get('department')} | Status: {a.get('status')}"
                        )
                    txt = "👥 <b>Active AI Company Agents:</b>\n\n" + "\n\n".join(agent_lines)
                    send_telegram_raw(token, chat_id, txt)

                elif raw_text == "/nodes" or raw_text.startswith("/nodes"):
                    st = load_state()
                    active_nid = st.get("active_hermes_node_id")
                    node_lines = []
                    for n in st.get("hermes_nodes", []):
                        is_act = n.get("node_id") == active_nid
                        node_lines.append(
                            f"{'🟢' if is_act else '⚪'} <b>{html.escape(n.get('name'))}</b> ({'ACTIVE' if is_act else 'STANDBY'})\n"
                            f"   └ Endpoint: <code>{n.get('endpoint')}</code>\n"
                            f"   └ Model: <code>{n.get('model')}</code> | Skills: {n.get('skills_count')}"
                        )
                    txt = "🪽 <b>Hermes Autonomous Worker Nodes:</b>\n\n" + "\n\n".join(node_lines)
                    send_telegram_raw(token, chat_id, txt)

                else:
                    # User dispatched an instruction / ticket via Telegram!
                    st = load_state()
                    t_low = raw_text.lower()
                    assigned_agent = "agent-hermes-17"
                    if "hire" in t_low or raw_text.startswith("/hire") or "cto" in t_low:
                        assigned_agent = "agent-cto"
                    elif "ceo" in t_low or "strategy" in t_low or "roadmap" in t_low:
                        assigned_agent = "agent-ceo"
                    elif "security" in t_low or "audit" in t_low:
                        sec_ag = next((a for a in st.get("agents", []) if "sec" in a["id"] or "aegis" in a["name"].lower()), None)
                        if sec_ag:
                            assigned_agent = sec_ag["id"]

                    ag_obj = next((a for a in st.get("agents", []) if a["id"] == assigned_agent), st["agents"][0])

                    send_telegram_raw(
                        token,
                        chat_id,
                        f"⏳ <b>Task Ingested via Telegram</b>\n"
                        f"<b>Assigned to:</b> {ag_obj.get('avatar')} {ag_obj.get('name')} ({ag_obj.get('model')})\n"
                        f"<b>Prompt:</b> <i>{html.escape(raw_text[:200])}...</i>\n\n"
                        f"Executing via local Ollama &amp; Hermes GPU node..."
                    )

                    def _run_ticket_sync():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            tck_id = f"TCK-{101 + len(st['tickets'])}"
                            ticket = {
                                "id": tck_id,
                                "title": raw_text[:80].replace("\n", " ").strip(),
                                "description": raw_text,
                                "assigned_to": ag_obj["id"],
                                "priority": "HIGH",
                                "status": "IN_PROGRESS",
                                "requires_approval": False,
                                "approved": True,
                                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                                "model_used": ag_obj["model"],
                                "tokens": 0,
                                "duration_ms": 0,
                                "output": "Executing via Telegram trigger...",
                            }
                            st_cur = load_state()
                            st_cur["tickets"].insert(0, ticket)
                            add_audit(st_cur, f"Telegram ({first_name})", f"Dispatched {tck_id} assigned to {ag_obj['name']}", "INFO")
                            save_state(st_cur)

                            res = loop.run_until_complete(execute_ticket_internal(tck_id))
                            t_done = res.get("ticket", ticket)
                            out_text = t_done.get("output", "")
                            
                            deliverable_msg = (
                                f"✅ <b>Deliverable Ready: {tck_id}</b>\n"
                                f"<b>Objective:</b> {html.escape(t_done.get('title', ''))}\n"
                                f"<b>Agent:</b> {ag_obj.get('avatar')} {ag_obj.get('name')} (<code>{t_done.get('model_used')}</code>)\n"
                                f"<b>Speed:</b> {t_done.get('tokens')} tokens in {t_done.get('duration_ms')} ms\n\n"
                                f"<b>Deliverable:</b>\n<pre>{html.escape(out_text)}</pre>"
                            )
                            send_telegram_raw(token, chat_id, deliverable_msg)
                        except Exception as exc:
                            send_telegram_raw(token, chat_id, f"❌ <b>Execution Error:</b> {html.escape(str(exc))}")
                        finally:
                            loop.close()

                    threading.Thread(target=_run_ticket_sync, daemon=True).start()

        except Exception:
            time.sleep(3)


def start_telegram_worker_if_needed():
    global TELEGRAM_POLL_THREAD
    if TELEGRAM_POLL_THREAD is None or not TELEGRAM_POLL_THREAD.is_alive():
        TELEGRAM_POLL_THREAD = threading.Thread(target=telegram_polling_worker, daemon=True)
        TELEGRAM_POLL_THREAD.start()


@app.get("/api/telegram")
async def get_telegram_status():
    state = load_state()
    tg = get_telegram_config(state)
    bot_info = None
    if tg.get("bot_token"):
        try:
            def _check():
                u = f"https://api.telegram.org/bot{tg['bot_token']}/getMe"
                req = urllib.request.Request(u, headers={"User-Agent": "Paperclip-Probe/1.0"})
                with urllib.request.urlopen(req, timeout=6) as r:
                    return json.loads(r.read().decode())
            res = await asyncio.to_thread(_check)
            if res.get("ok"):
                bot_info = res.get("result", {})
                tg["bot_username"] = bot_info.get("username", "")
                tg["status"] = "CONNECTED" if tg.get("chat_id") else "ONLINE_WAITING_FOR_USER"
        except Exception as e:
            tg["status"] = f"ERROR: {e}"

    masked_token = (tg["bot_token"][:6] + "..." + tg["bot_token"][-4:]) if len(tg.get("bot_token", "")) > 10 else ""
    return {
        "ok": True,
        "telegram": {
            "enabled": tg.get("enabled", True),
            "target_phone": tg.get("target_phone", "908-845-3667"),
            "bot_token_masked": masked_token,
            "has_token": bool(tg.get("bot_token")),
            "chat_id": tg.get("chat_id"),
            "has_chat_id": bool(tg.get("chat_id")),
            "bot_username": tg.get("bot_username", ""),
            "bot_info": bot_info,
            "status": tg["status"],
            "notify_on_ticket_completed": tg.get("notify_on_ticket_completed", True),
            "notify_on_hire": tg.get("notify_on_hire", True),
        }
    }


@app.post("/api/telegram/config")
async def update_telegram_config(payload: Dict[str, Any] = Body(...)):
    state = load_state()
    tg = state.setdefault("telegram", {})

    token = payload.get("bot_token", "").strip()
    if token:
        try:
            def _validate():
                u = f"https://api.telegram.org/bot{token}/getMe"
                req = urllib.request.Request(u, headers={"User-Agent": "Paperclip-Validate/1.0"})
                with urllib.request.urlopen(req, timeout=8) as r:
                    return json.loads(r.read().decode())
            val_res = await asyncio.to_thread(_validate)
            if not val_res.get("ok"):
                raise HTTPException(status_code=400, detail="Invalid Telegram Bot Token. Verify token with @BotFather.")
            bot_info = val_res.get("result", {})
            tg["bot_token"] = token
            tg["bot_username"] = bot_info.get("username", "")
            tg["status"] = "CONNECTED" if tg.get("chat_id") else "ONLINE_WAITING_FOR_USER"
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Failed to verify Bot Token with Telegram API: {exc}")

    if "chat_id" in payload:
        tg["chat_id"] = str(payload.get("chat_id", "")).strip()
    if "target_phone" in payload:
        tg["target_phone"] = payload.get("target_phone", "908-845-3667").strip()
    if "enabled" in payload:
        tg["enabled"] = bool(payload.get("enabled", True))
    if "notify_on_ticket_completed" in payload:
        tg["notify_on_ticket_completed"] = bool(payload.get("notify_on_ticket_completed", True))
    if "notify_on_hire" in payload:
        tg["notify_on_hire"] = bool(payload.get("notify_on_hire", True))

    save_state(state)
    add_audit(state, "Telegram", f"Updated Telegram integration settings (Phone: {tg.get('target_phone')}, Bot: @{tg.get('bot_username')})", "INFO")
    save_state(state)
    start_telegram_worker_if_needed()
    return {"ok": True, "telegram": tg, "state": state}


@app.post("/api/telegram/test")
async def send_telegram_test():
    state = load_state()
    tg = get_telegram_config(state)
    token = tg.get("bot_token")
    chat_id = tg.get("chat_id")

    if not token:
        raise HTTPException(status_code=400, detail="Telegram Bot Token is not configured yet. Create a bot with @BotFather and save the token.")
    if not chat_id:
        raise HTTPException(
            status_code=400,
            detail=f"Bot Token is active (@{tg.get('bot_username')}), but your chat is not paired yet! Open your bot on Telegram from phone {tg.get('target_phone')} and send '/start' to pair automatically."
        )

    test_msg = (
        f"⚡ <b>Sovereign AI Corp Communication Link Verified!</b>\n\n"
        f"👑 <b>Atlas (CEO):</b> System link established with Telegram.\n"
        f"🧠 <b>Vega (CTO):</b> Swarm routing online.\n"
        f"🪽 <b>Hermes-17:</b> GPU worker on Host 17 ready to execute tickets.\n"
        f"📱 <b>Target Phone:</b> <code>{tg.get('target_phone')}</code>\n\n"
        f"All company agents are now connected and can talk directly to your Telegram. Send any task here to dispatch tickets immediately!"
    )
    ok = await asyncio.to_thread(send_telegram_raw, token, chat_id, test_msg)
    if ok:
        add_audit(state, "Telegram", f"Dispatched live test alert to Telegram chat {chat_id} ({tg.get('target_phone')})", "SUCCESS")
        save_state(state)
        return {"ok": True, "message": "Test alert successfully delivered to Telegram!", "chat_id": chat_id}
    else:
        raise HTTPException(status_code=502, detail="Failed to deliver message via Telegram Bot API. Verify bot has access to chat_id.")


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


@app.on_event("startup")
async def app_startup_event():
    start_telegram_worker_if_needed()


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "7891"))
    uvicorn.run(app, host="0.0.0.0", port=port)
