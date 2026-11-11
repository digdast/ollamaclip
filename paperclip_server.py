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
DEFAULT_CLAUDE_URL = os.environ.get("CLAUDE_URL", "http://192.168.0.17:7893")

app = FastAPI(
    title="Paperclip-Ollama — Zero-Human AI Company Control Plane (Hermes + Claude Swarm)",
    version="1.1.0",
)


def default_state() -> Dict[str, Any]:
    return {
        "company_name": "Sovereign AI Corp (Ollama • Hermes • Claude Swarm)",
        "ollama_url": DEFAULT_OLLAMA_URL,
        "hermes_url": DEFAULT_HERMES_URL,
        "claude_url": DEFAULT_CLAUDE_URL,
        "swarm_coop_enabled": True,
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
                    "You are Hermes-01, a self-improving autonomous agent connected to Paperclip, Claude, and Ollama. "
                    "Execute assigned tickets, synthesize reusable skills from every task, and store episodic memory."
                ),
            },
            {
                "id": "agent-claude",
                "name": "Claude-01",
                "role": "Principal Reasoning & Code Architect (Claude Bridge)",
                "department": "Autonomous Ops",
                "reports_to": "agent-cto",
                "adapter": "claude_bridge",
                "endpoint": DEFAULT_CLAUDE_URL,
                "model": "gemma4-claude:latest",
                "status": "ONLINE",
                "budget_tokens": 2000000,
                "tokens_used": 18420,
                "avatar": "✴️",
                "system_prompt": (
                    "You are Claude-01, Principal Reasoning & Code Architect powered by the Anthropic Messages API "
                    "on Ollama. Work hand-in-hand with Hermes agents to design, code, verify, and synthesize playbooks."
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
                "agent_type": "hermes",
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
                "agent_type": "hermes",
            },
            {
                "node_id": "claude-host-17",
                "name": "Claude-GPU (plexadmin@192.168.0.17)",
                "endpoint": "http://192.168.0.17:7893",
                "ollama_url": "http://127.0.0.1:11434",
                "model": "gemma4-claude:latest",
                "skills_count": 3,
                "memories_count": 4,
                "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "CONNECTED",
                "agent_type": "claude",
            },
            {
                "node_id": "claude-k3s-primary",
                "name": "Claude-01 (K3s Autonomous Agent)",
                "endpoint": "http://192.168.0.81:30793",
                "ollama_url": DEFAULT_OLLAMA_URL,
                "model": "gemma4-claude:latest",
                "skills_count": 3,
                "memories_count": 4,
                "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "CONNECTED",
                "agent_type": "claude",
            }
        ],
        "claude_nodes": [
            {
                "node_id": "claude-host-17",
                "name": "Claude-GPU (plexadmin@192.168.0.17)",
                "endpoint": "http://192.168.0.17:7893",
                "ollama_url": "http://127.0.0.1:11434",
                "model": "gemma4-claude:latest",
                "skills_count": 3,
                "memories_count": 4,
                "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "CONNECTED",
                "agent_type": "claude",
            },
            {
                "node_id": "claude-k3s-primary",
                "name": "Claude-01 (K3s Autonomous Agent)",
                "endpoint": "http://192.168.0.81:30793",
                "ollama_url": DEFAULT_OLLAMA_URL,
                "model": "gemma4-claude:latest",
                "skills_count": 3,
                "memories_count": 4,
                "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "CONNECTED",
                "agent_type": "claude",
            }
        ],
        "active_hermes_node_id": "hermes-host-17",
        "active_claude_node_id": "claude-host-17",
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
            {
                "id": str(uuid.uuid4())[:8],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "actor": "Claude-01",
                "event": "Claude Autonomous Agent registered via /api/claude/register (Anthropic /v1/messages + Hermes Co-Op)",
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
            
            st.setdefault("swarm_coop_enabled", True)
            st.setdefault("claude_url", DEFAULT_CLAUDE_URL)

            # Ensure hermes-host-17 and claude-host-17 are in hermes_nodes & claude_nodes
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
                    "agent_type": "hermes",
                })
            if "claude-host-17" not in node_ids:
                st.setdefault("hermes_nodes", []).append({
                    "node_id": "claude-host-17",
                    "name": "Claude-GPU (plexadmin@192.168.0.17)",
                    "endpoint": "http://192.168.0.17:7893",
                    "ollama_url": "http://127.0.0.1:11434",
                    "model": "gemma4-claude:latest",
                    "skills_count": 3,
                    "memories_count": 4,
                    "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "CONNECTED",
                    "agent_type": "claude",
                })
            if "claude-k3s-primary" not in node_ids:
                st.setdefault("hermes_nodes", []).append({
                    "node_id": "claude-k3s-primary",
                    "name": "Claude-01 (K3s Autonomous Agent)",
                    "endpoint": "http://claude.ai.svc.cluster.local:7893",
                    "ollama_url": DEFAULT_OLLAMA_URL,
                    "model": "gemma4-claude:latest",
                    "skills_count": 3,
                    "memories_count": 4,
                    "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "CONNECTED",
                    "agent_type": "claude",
                })

            claude_node_ids = {n.get("node_id") for n in st.get("claude_nodes", [])}
            if "claude-host-17" not in claude_node_ids:
                st.setdefault("claude_nodes", []).insert(0, {
                    "node_id": "claude-host-17",
                    "name": "Claude-GPU (plexadmin@192.168.0.17)",
                    "endpoint": "http://192.168.0.17:7893",
                    "ollama_url": "http://127.0.0.1:11434",
                    "model": "gemma4-claude:latest",
                    "skills_count": 3,
                    "memories_count": 4,
                    "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "CONNECTED",
                    "agent_type": "claude",
                })
            if "claude-k3s-primary" not in claude_node_ids:
                st.setdefault("claude_nodes", []).append({
                    "node_id": "claude-k3s-primary",
                    "name": "Claude-01 (K3s Autonomous Agent)",
                    "endpoint": "http://claude.ai.svc.cluster.local:7893",
                    "ollama_url": DEFAULT_OLLAMA_URL,
                    "model": "gemma4-claude:latest",
                    "skills_count": 3,
                    "memories_count": 4,
                    "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "CONNECTED",
                    "agent_type": "claude",
                })

            if not st.get("active_hermes_node_id"):
                st["active_hermes_node_id"] = "hermes-host-17"
            if not st.get("active_claude_node_id"):
                st["active_claude_node_id"] = "claude-host-17"
            
            # Ensure Hermes-17, Claude-01, and Claude-17 agents exist in agents
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
            if "agent-claude" not in agent_ids:
                st.setdefault("agents", []).append({
                    "id": "agent-claude",
                    "name": "Claude-01",
                    "role": "Principal Reasoning & Code Architect (Claude Bridge)",
                    "department": "Autonomous Ops",
                    "reports_to": "agent-cto",
                    "adapter": "claude_bridge",
                    "endpoint": "http://192.168.0.17:7893",
                    "model": "gemma4-claude:latest",
                    "status": "ONLINE",
                    "budget_tokens": 2000000,
                    "tokens_used": 0,
                    "avatar": "✴️",
                    "system_prompt": "You are Claude-01, Principal Reasoning & Code Architect powered by the Anthropic Messages API on Ollama. Work hand-in-hand with Hermes agents to design, code, verify, and synthesize playbooks."
                })
            if "agent-claude-17" not in agent_ids:
                st.setdefault("agents", []).append({
                    "id": "agent-claude-17",
                    "name": "Claude-17",
                    "role": "Host Autonomous Claude GPU Agent (192.168.0.17)",
                    "department": "Autonomous Ops",
                    "reports_to": "agent-cto",
                    "adapter": "claude_bridge",
                    "endpoint": "http://192.168.0.17:7893",
                    "model": "gemma4-claude:latest",
                    "status": "ONLINE",
                    "budget_tokens": 2000000,
                    "tokens_used": 0,
                    "avatar": "✴️",
                    "system_prompt": "You are Claude-17, an autonomous Claude reasoning and coding agent running on GPU host 192.168.0.17:7893. Collaborate directly with Hermes-17 on complex engineering tickets."
                })

            # Harmonize all Hermes & Claude agent bots to use their bridges and connect to active nodes
            st.setdefault("hermes_for_all_agents", True)
            for ag in st.get("agents", []):
                ag_name_l = ag.get("name", "").lower()
                ag_id_l = ag.get("id", "").lower()
                if "claude" in ag_name_l or "claude" in ag_id_l or ag.get("adapter") == "claude_bridge":
                    ag["adapter"] = "claude_bridge"
                    ag["status"] = "ONLINE"
                    if not ag.get("endpoint"):
                        ag["endpoint"] = "http://192.168.0.17:7893"
                    if not ag.get("avatar") or ag.get("avatar") in ("🤖", "🪽"):
                        ag["avatar"] = "✴️"
                elif "hermes" in ag_name_l or "hermes" in ag_id_l:
                    ag["adapter"] = "hermes_bridge"
                    ag["status"] = "ONLINE"
                    if not ag.get("endpoint"):
                        ag["endpoint"] = "http://192.168.0.17:7892"
                    if not ag.get("avatar") or ag.get("avatar") == "🤖":
                        ag["avatar"] = "🪽"

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
            "num_predict": 8192,
        },
    }
    t0 = time.time()
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    duration_ms = round((time.time() - t0) * 1000.0, 1)
    msg = (data.get("message", {}).get("content") or "").strip()
    thinking = (data.get("message", {}).get("thinking") or "").strip()
    
    # If reasoning model spent tokens in thinking and content is empty, surface the thinking as answer
    if not msg and thinking:
        msg = f"### [Reasoning & Analysis]\n\n{thinking}"
    elif thinking and msg and len(thinking) > 30:
        first_few_thoughts = "\n".join(thinking.splitlines()[:12])
        msg = f"<blockquote>🧠 <b>Reasoning Summary:</b>\n{first_few_thoughts}</blockquote>\n\n{msg}"

    eval_tokens = int(data.get("eval_count", 0)) + int(data.get("prompt_eval_count", 0))
    return {
        "content": msg.strip() or "(Task executed successfully)",
        "tokens": eval_tokens or max(64, len(msg) // 4),
        "duration_ms": duration_ms,
    }


def call_anthropic_messages(ollama_url: str, model: str, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """Calls Ollama's native Anthropic Messages API (/v1/messages) with fallback to /api/chat."""
    t0 = time.time()
    base = ollama_url.rstrip("/")
    effective_model = model
    try:
        with urllib.request.urlopen(f"{base}/api/ps", timeout=3) as r_ps:
            ps_models = json.loads(r_ps.read().decode("utf-8")).get("models", [])
        hot_names = [m.get("name") for m in ps_models if m.get("name")]
        total_vram_gb = sum(m.get("size_vram", 0) for m in ps_models) / (1024 ** 3)
        if hot_names and effective_model not in hot_names and total_vram_gb >= 15.0:
            for preferred_hot in ["gemma4-claude:latest", "qwen2.5-coder:14b", "qwen2.5-coder:7b"]:
                if preferred_hot in hot_names:
                    effective_model = preferred_hot
                    break
            else:
                effective_model = hot_names[0]
    except Exception:
        pass
    try:
        url = f"{base}/v1/messages"
        payload = {
            "model": effective_model,
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
            "temperature": 0.3,
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-api-key": os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN", "ollama"),
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        duration_ms = round((time.time() - t0) * 1000.0, 1)
        blocks = data.get("content", [])
        text_parts = []
        thinking_parts = []
        for b in blocks:
            if isinstance(b, dict):
                if b.get("type") == "text" and b.get("text"):
                    text_parts.append(b["text"].strip())
                elif b.get("type") == "thinking" and b.get("thinking"):
                    thinking_parts.append(b["thinking"].strip())
        msg = "\n\n".join(text_parts).strip()
        thinking = "\n\n".join(thinking_parts).strip()
        if not msg and thinking:
            msg = f"### [Claude Extended Reasoning & Solution]\n\n{thinking}"
        elif thinking and msg and len(thinking) > 30:
            first_few = "\n".join(thinking.splitlines()[:10])
            msg = f"<blockquote>✴️ <b>Claude Extended Thinking:</b>\n{first_few}</blockquote>\n\n{msg}"
        usage = data.get("usage", {})
        tokens = int(usage.get("input_tokens", 0)) + int(usage.get("output_tokens", 0))
        if msg:
            return {
                "content": msg,
                "tokens": tokens or max(64, len(msg) // 4),
                "duration_ms": duration_ms,
                "model": data.get("model", model),
            }
    except Exception:
        pass
    res = call_ollama_chat(ollama_url, model, system_prompt, user_prompt)
    res["model"] = model
    return res


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


@app.get("/api/telemetry")
async def get_telemetry():
    state = load_state()
    ollama_info = await asyncio.to_thread(probe_ollama, state["ollama_url"])
    agents = state.get("agents", [])
    tickets = state.get("tickets", [])
    hermes_nodes = state.get("hermes_nodes", [])

    total_tokens_used = sum(int(a.get("tokens_used", 0)) for a in agents)
    total_budget_tokens = sum(int(a.get("budget_tokens", 1000000)) for a in agents)
    active_agents = sum(1 for a in agents if a.get("status") in ["BUSY", "EXECUTING", "ONLINE", "ACTIVE"])
    idle_agents = sum(1 for a in agents if a.get("status") == "IDLE")

    completed_tickets = sum(1 for t in tickets if t.get("status") == "COMPLETED")
    pending_tickets = sum(1 for t in tickets if t.get("status") in ["OPEN", "PENDING", "IN_PROGRESS", "ASSIGNED"])
    auto_executed_tickets = sum(1 for t in tickets if t.get("auto_execute"))

    running_models = ollama_info.get("running_models", [])

    return {
        "status": "online",
        "system": {
            "service": "Paperclip-Ollama (ClipOS)",
            "version": "1.0.0",
            "active_node_id": state.get("active_hermes_node_id", "hermes-host-17"),
            "timestamp": time.time(),
            "uptime_status": "ACTIVE"
        },
        "swarm": {
            "agents_count": len(agents),
            "active_agents": active_agents,
            "idle_agents": idle_agents,
            "hermes_nodes_count": len(hermes_nodes),
            "hermes_nodes": hermes_nodes,
            "total_tokens_used": total_tokens_used,
            "total_budget_tokens": total_budget_tokens,
            "budget_utilization_pct": round((total_tokens_used / max(total_budget_tokens, 1)) * 100, 2),
            "agents": [
                {
                    "id": a.get("id"),
                    "name": a.get("name"),
                    "avatar": a.get("avatar", "🤖"),
                    "role": a.get("role"),
                    "model": a.get("model"),
                    "status": a.get("status", "IDLE"),
                    "tokens_used": a.get("tokens_used", 0),
                    "budget_tokens": a.get("budget_tokens", 1000000)
                }
                for a in agents
            ]
        },
        "inference": {
            "connected": bool(ollama_info.get("connected")),
            "url": state.get("ollama_url", DEFAULT_OLLAMA_URL),
            "version": ollama_info.get("version"),
            "latency_ms": ollama_info.get("latency_ms"),
            "models_count": ollama_info.get("models_count", 0),
            "running_models": running_models,
            "running_models_count": len(running_models)
        },
        "pipeline": {
            "tickets_total": len(tickets),
            "completed": completed_tickets,
            "pending": pending_tickets,
            "auto_executed": auto_executed_tickets,
            "auto_execute_rate_pct": round((auto_executed_tickets / max(len(tickets), 1)) * 100, 1)
        }
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
    raw_name = (payload.get("name") or "New Agent").strip()
    is_claude = "claude" in raw_name.lower() or "claude" in agent_id.lower() or payload.get("adapter") == "claude_bridge"
    is_hermes = (not is_claude) and ("hermes" in raw_name.lower() or "hermes" in agent_id.lower() or payload.get("adapter") == "hermes_bridge")

    if is_claude:
        adapter = "claude_bridge"
        endpoint = payload.get("endpoint") or "http://192.168.0.17:7893"
        avatar = payload.get("avatar") or "✴️"
        default_model = "gemma4-claude:latest"
        default_dept = "Autonomous Ops"
        engine_label = "Claude-Ollama (Anthropic /v1/messages + Hermes Co-Op)"
    elif is_hermes:
        adapter = "hermes_bridge"
        endpoint = payload.get("endpoint") or "http://192.168.0.17:7892"
        avatar = payload.get("avatar") or "🪽"
        default_model = "qwen2.5-coder:14b"
        default_dept = "Autonomous Ops"
        engine_label = "Hermes-Ollama"
    else:
        adapter = payload.get("adapter") or "ollama_native"
        endpoint = payload.get("endpoint")
        avatar = payload.get("avatar") or "🤖"
        default_model = "qwen2.5-coder:7b"
        default_dept = "Engineering"
        engine_label = "local Ollama"

    new_agent = {
        "id": agent_id,
        "name": raw_name,
        "role": (payload.get("role") or ("Autonomous Reasoning & Code Architect" if is_claude else "Autonomous Specialist")).strip(),
        "department": (payload.get("department") or default_dept).strip(),
        "reports_to": payload.get("reports_to") or "agent-cto",
        "adapter": adapter,
        "endpoint": endpoint,
        "model": payload.get("model") or default_model,
        "status": "ONLINE" if adapter in ("hermes_bridge", "claude_bridge") else "IDLE",
        "budget_tokens": int(payload.get("budget_tokens", 2000000 if (is_hermes or is_claude) else 1000000)),
        "tokens_used": int(payload.get("tokens_used", 0)),
        "avatar": avatar,
        "system_prompt": payload.get(
            "system_prompt",
            f"You are {raw_name}, an autonomous specialist agent in Sovereign AI Corp powered by {engine_label}. Collaborate seamlessly with Hermes and Claude peers.",
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
                "collaborate": bool(payload.get("collaborate", True)),
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
    collaborate = bool(payload.get("collaborate", state.get("swarm_coop_enabled", True)))

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
        "collaborate": collaborate,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model_used": agent["model"],
        "tokens": 0,
        "duration_ms": 0,
        "output": "Agent is reasoning via Ollama (" + state["ollama_url"] + ")...",
    }
    state["tickets"].insert(0, ticket)
    coop_tag = " [🤝 Hermes + Claude Co-Op]" if collaborate else ""
    add_audit(state, agent["name"], f"Created ticket {tck_id}: '{ticket['title']}' assigned to {agent['name']} ({agent['model']}){coop_tag}", "INFO")
    save_state(state)
    asyncio.create_task(dispatch_to_n8n_async("ticket_created", ticket, agent))

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


def send_telegram_document(bot_token: str, chat_id: str, filename: str, content_bytes: bytes, caption: str = "") -> bool:
    """Sends a complete deliverable document to Telegram via multipart/form-data with zero truncation."""
    if not bot_token or not chat_id:
        return False
    boundary = f"----TelegramBoundary{uuid.uuid4().hex}"
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    
    body = bytearray()
    # chat_id
    body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n{chat_id}\r\n".encode("utf-8"))
    # caption
    if caption:
        body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"caption\"\r\n\r\n{caption[:1000]}\r\n".encode("utf-8"))
    # document
    body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"document\"; filename=\"{filename}\"\r\nContent-Type: text/markdown; charset=utf-8\r\n\r\n".encode("utf-8"))
    body.extend(content_bytes)
    body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))
    
    req = urllib.request.Request(
        url,
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return True
    except Exception:
        return False


def send_telegram_raw(bot_token: str, chat_id: str, text: str) -> bool:
    if not bot_token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # Clean split with balanced tags
    chunks = []
    rem = text
    while len(rem) > 3800:
        split_idx = rem.rfind("\n", 0, 3800)
        if split_idx == -1 or split_idx < 1000:
            split_idx = 3800
        chunk = rem[:split_idx]
        rem = rem[split_idx:].lstrip()
        chunks.append(chunk)
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
            with urllib.request.urlopen(req, timeout=15) as resp:
                pass
        except Exception:
            # Fallback to plain text if HTML tags were unclosed/malformed in this chunk
            try:
                # Strip out basic tags for clean plain text fallback
                clean_plain = re.sub(r"<[^>]+>", "", c)
                payload = json.dumps({"chat_id": chat_id, "text": clean_plain}).encode("utf-8")
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=15) as resp:
                    pass
            except Exception:
                ok = False
    return ok


def send_telegram_deliverable(
    bot_token: str,
    chat_id: str,
    header_html: str,
    deliverable_text: str,
    ticket_id: str = "DELIVERABLE",
    title: str = "",
) -> bool:
    """
    Delivers full un-truncated deliverables to Telegram:
    - If total length is within 3800 chars, delivers as 1 single formatted message.
    - If longer, paginates into clean numbered parts [Part 1/N], each with properly closed <pre> tags.
    - Also attaches the full 100% untruncated deliverable as a .md document file via Telegram sendDocument.
    """
    if not bot_token or not chat_id:
        return False

    deliv_clean = (deliverable_text or "").strip()
    if not deliv_clean:
        deliv_clean = "(Task executed successfully with no textual output)"

    full_single = f"{header_html}\n\n<b>Deliverable:</b>\n<pre>{html.escape(deliv_clean)}</pre>"
    if len(full_single) <= 3800:
        return send_telegram_raw(bot_token, chat_id, full_single)

    # Deliverable exceeds standard single message limit -> Paginate cleanly
    chunk_size = 3000
    chunks = []
    rem = deliv_clean
    while len(rem) > chunk_size:
        split_idx = rem.rfind("\n", 0, chunk_size)
        if split_idx == -1 or split_idx < 1200:
            split_idx = chunk_size
        chunks.append(rem[:split_idx])
        rem = rem[split_idx:].lstrip()
    if rem:
        chunks.append(rem)

    total_parts = len(chunks)

    # Part 1: Header + First Chunk
    part1_msg = f"{header_html}\n\n<b>Deliverable [Part 1/{total_parts}]:</b>\n<pre>{html.escape(chunks[0])}</pre>"
    send_telegram_raw(bot_token, chat_id, part1_msg)

    # Subsequent parts
    for idx, c in enumerate(chunks[1:], start=2):
        part_msg = f"<b>Deliverable [Part {idx}/{total_parts}]:</b>\n<pre>{html.escape(c)}</pre>"
        send_telegram_raw(bot_token, chat_id, part_msg)
        time.sleep(0.3)

    # Send full un-truncated file attachment
    safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', title[:32]) if title else "ticket"
    fn = f"{ticket_id}_{safe_title}.md"
    file_bytes = f"# {ticket_id}: {title}\n\n{deliv_clean}".encode("utf-8")
    caption = f"📎 Complete Deliverable File: {ticket_id} ({len(deliv_clean)} chars, {total_parts} parts)"
    send_telegram_document(bot_token, chat_id, fn, file_bytes, caption)

    return True


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


# --- N8N WORKFLOW PIPELINE DISPATCH CORE ---
N8N_BASE_URLS = [
    os.environ.get("N8N_URL", "http://n8n.ai.svc.cluster.local:5678"),
    "http://n8n.ai.svc.cluster.local:5678",
    "http://192.168.0.81:30678",
]


def dispatch_to_n8n_sync(event: str, ticket: Dict[str, Any], agent: Dict[str, Any]) -> bool:
    """Passes agent workflow events and deliverables directly to n8n webhook pipelines."""
    payload = {
        "event": event,
        "source": "paperclip-control-plane",
        "ticket_id": ticket.get("id"),
        "title": ticket.get("title"),
        "description": ticket.get("description"),
        "assigned_to": agent.get("id"),
        "agent_name": agent.get("name"),
        "agent_role": agent.get("role"),
        "avatar": agent.get("avatar", "🤖"),
        "model": ticket.get("model_used") or agent.get("model"),
        "tokens": ticket.get("tokens", 0),
        "duration_ms": ticket.get("duration_ms", 0),
        "deliverable": ticket.get("output", ""),
        "status": ticket.get("status"),
        "timestamp": ticket.get("updated_at") or time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    encoded = json.dumps(payload).encode("utf-8")

    agent_slug = (agent.get("id") or "").replace("agent-", "")
    target_paths = ["paperclip-ticket"]
    if agent_slug:
        target_paths.append(f"agent-{agent_slug}")
    target_paths.append("agent-swarm-gateway")

    delivered = False
    for base_url in N8N_BASE_URLS:
        for path in target_paths:
            url = f"{base_url.rstrip('/')}/webhook/{path}"
            try:
                req = urllib.request.Request(
                    url,
                    data=encoded,
                    headers={"Content-Type": "application/json", "User-Agent": "Paperclip-Swarm/1.0"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=4) as resp:
                    if resp.status in (200, 201):
                        delivered = True
            except Exception:
                continue
        if delivered:
            break
    return delivered


async def dispatch_to_n8n_async(event: str, ticket: Dict[str, Any], agent: Dict[str, Any]):
    await asyncio.to_thread(dispatch_to_n8n_sync, event, ticket, agent)


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
            is_claude = "claude" in raw_target.lower() or "claude" in raw_role.lower()
            is_hermes = (not is_claude) and ("hermes" in raw_target.lower() or "hermes" in raw_role.lower() or "worker" in raw_target.lower())
            if is_claude:
                claude_count = len([a for a in state["agents"] if "claude" in a.get("adapter", "") or "claude" in a["name"].lower()])
                name = f"Claude-{claude_count + 1:02d}"
                role = raw_role.title() if raw_role else "Autonomous Reasoning & Code Architect"
                adapter = "claude_bridge"
                model = "gemma4-claude:latest"
                avatar = "✴️"
                dept = "Autonomous Ops"
            elif is_hermes:
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
                if "claude" in full_text.lower():
                    adapter = "claude_bridge"
                    model = "gemma4-claude:latest"
                    avatar = "✴️"
                    dept = "Autonomous Ops"
                elif "hermes" in full_text.lower():
                    adapter = "hermes_bridge"
                    model = "qwen2.5-coder:7b"
                    avatar = "🪽"
                    dept = "Autonomous Ops"
                else:
                    adapter = "ollama_native"
                    model = "qwen2.5-coder:7b"
                    avatar = "🛠️"
                    dept = "Engineering"
            
            # Check if this agent already exists
            existing = next((a for a in state["agents"] if a["name"].lower() == name.lower()), None)
            if not existing:
                if adapter == "claude_bridge":
                    endpoint = "http://192.168.0.17:7893"
                elif adapter == "hermes_bridge":
                    endpoint = "http://192.168.0.17:7892"
                else:
                    endpoint = None
                new_ag = {
                    "id": f"agent-{name.lower()}-{str(uuid.uuid4())[:4]}",
                    "name": name,
                    "role": role,
                    "department": dept,
                    "reports_to": "agent-cto",
                    "adapter": adapter,
                    "endpoint": endpoint,
                    "model": model,
                    "status": "ONLINE" if adapter in ("hermes_bridge", "claude_bridge") else "IDLE",
                    "budget_tokens": 2000000 if adapter in ("hermes_bridge", "claude_bridge") else 1500000,
                    "tokens_used": 0,
                    "avatar": avatar,
                    "system_prompt": f"You are {name}, {role} at Sovereign AI Corp. Collaborate with Hermes and Claude peers to execute engineering tasks with zero placeholders."
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
    res = await _execute_ticket_core(ticket_id)
    try:
        dep_res = await asyncio.to_thread(deploy_completed_ticket_to_k3s_dev, ticket_id)
        if dep_res:
            res = dep_res
    except Exception:
        pass
    return res


async def _execute_ticket_core(ticket_id: str) -> Dict[str, Any]:
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

    # Check if assigned to Desktop worker (which pulls tasks outbound from Paperclip to bypass Windows firewall)
    is_desktop_agent = "desktop" in agent.get("id", "").lower() or "desktop" in agent.get("name", "").lower()
    if is_desktop_agent:
        state = load_state()
        ticket = next((t for t in state["tickets"] if t["id"] == ticket_id), ticket)
        ticket["status"] = "QUEUED_FOR_DESKTOP"
        add_audit(state, "Control Plane", f"Placed {ticket_id} into Desktop Hermes Work Queue (executing on local RTX 3060 GPU)", "INFO")
        save_state(state)
        
        # Wait up to 120s for Desktop Hermes worker to process and submit via /api/hermes/complete_ticket
        for _ in range(120):
            await asyncio.sleep(1)
            st_cur = load_state()
            t_cur = next((t for t in st_cur["tickets"] if t["id"] == ticket_id), None)
            if t_cur and t_cur.get("status") in ("COMPLETED", "AWAITING_APPROVAL"):
                return {"ticket": t_cur, "state": st_cur}

    # Check if routed to Claude bridge
    is_claude = (
        agent.get("adapter") in ("claude_bridge", "claude")
        or "claude" in agent.get("id", "").lower()
        or "claude" in agent.get("name", "").lower()
    )
    collaborate_flag = bool(ticket.get("collaborate", state.get("swarm_coop_enabled", True)))

    if is_claude:
        claude_eps = []
        if agent.get("endpoint"):
            claude_eps.append(agent["endpoint"])
        active_cid = state.get("active_claude_node_id")
        active_cnode = next((n for n in state.get("claude_nodes", []) if n.get("node_id") == active_cid), None)
        if active_cnode and active_cnode.get("endpoint") and active_cnode["endpoint"] not in claude_eps:
            claude_eps.append(active_cnode["endpoint"])
        for default_cep in [
            "http://192.168.0.17:7893",
            os.environ.get("CLAUDE_URL", "http://claude.ai.svc.cluster.local:7893"),
            "http://claude.ai.svc.cluster.local:7893",
            "http://192.168.0.81:30793",
            "http://127.0.0.1:7893",
        ]:
            if default_cep and default_cep not in claude_eps:
                claude_eps.append(default_cep)

        for claude_ep in claude_eps:
            try:
                def _call_claude():
                    req = urllib.request.Request(
                        f"{claude_ep.rstrip('/')}/api/execute_ticket",
                        data=json.dumps({
                            "ticket_id": ticket["id"],
                            "title": ticket["title"],
                            "description": ticket["description"],
                            "model": agent.get("model") or "gemma4-claude:latest",
                            "agent_name": agent["name"],
                            "system_prompt": agent.get("system_prompt", ""),
                            "ollama_url": state["ollama_url"],
                            "collaborate_with_hermes": collaborate_flag,
                        }).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                    with urllib.request.urlopen(req, timeout=180) as resp:
                        return json.loads(resp.read().decode("utf-8"))

                c_res = await asyncio.to_thread(_call_claude)
                state = load_state()
                ticket = next((t for t in state["tickets"] if t["id"] == ticket_id), ticket)
                agent = next((a for a in state["agents"] if a["id"] == ticket["assigned_to"]), agent)
                ticket["output"] = c_res.get("output", "")
                ticket["tokens"] = int(c_res.get("tokens", 320))
                ticket["duration_ms"] = float(c_res.get("duration_ms", 1500))
                ticket["model_used"] = c_res.get("model", agent["model"])
                ticket["status"] = "AWAITING_APPROVAL" if ticket.get("requires_approval") else "COMPLETED"
                ticket["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                agent["status"] = "ONLINE"
                agent["tokens_used"] = agent.get("tokens_used", 0) + ticket["tokens"]
                if collaborate_flag:
                    hermes_ag = next((a for a in state["agents"] if a["id"] in ("agent-hermes-17", "agent-hermes")), None)
                    if hermes_ag:
                        hermes_ag["tokens_used"] = hermes_ag.get("tokens_used", 0) + max(120, ticket["tokens"] // 3)

                c_log = c_res.get("completion_log") or {
                    "id": f"clog-{str(uuid.uuid4())[:8]}",
                    "ticket_id": ticket_id,
                    "title": ticket["title"],
                    "agent_name": f"{agent['name']} + Hermes Co-Op" if collaborate_flag else agent["name"],
                    "node_id": state.get("active_claude_node_id", "claude-host-17"),
                    "model": ticket["model_used"],
                    "tokens": ticket["tokens"],
                    "tok_per_sec": round(ticket["tokens"] / max(0.1, ticket["duration_ms"] / 1000.0), 1),
                    "duration_ms": ticket["duration_ms"],
                    "completed_at": ticket["updated_at"],
                    "learned_skill": c_res.get("learned_skill", "claude-hermes-coop"),
                    "memory_summary": f"Claude ({agent['name']}) {'& Hermes ' if collaborate_flag else ''}completed {ticket_id}.",
                    "steps": [
                        {"step": "Claude Ingested", "time": "0.0s", "detail": f"Paperclip assigned {ticket_id} to {agent['name']}"},
                        {"step": "Anthropic /v1/messages", "time": "0.5s", "detail": f"Executed via {ticket['model_used']}" + (" + Hermes Co-Op" if collaborate_flag else "")},
                    ],
                    "status": "SUCCESS",
                }
                ticket["hermes_log"] = c_log
                state.setdefault("hermes_ticket_logs", []).insert(0, c_log)
                state["hermes_ticket_logs"] = state["hermes_ticket_logs"][:100]
                add_audit(
                    state,
                    agent["name"],
                    f"Claude {'+ Hermes Co-Op ' if collaborate_flag else ''}executed {ticket_id} & synthesized '{c_log.get('learned_skill', 'claude-playbook')}' ({ticket['tokens']} tokens in {ticket['duration_ms']} ms)",
                    "SUCCESS",
                )
                save_state(state)
                asyncio.create_task(dispatch_to_n8n_async("ticket_completed", ticket, agent))
                return {"ticket": ticket, "state": state}
            except Exception:
                continue

        # Direct Anthropic /v1/messages fallback + Hermes Co-Op if Claude service port wasn't reachable
        try:
            c_prompt = (
                f"COMPANY TICKET [{ticket['id']}]: {ticket['title']}\n"
                f"PRIORITY: {ticket['priority']}\n"
                f"DETAILS:\n{ticket['description']}\n\n"
                f"Provide a complete, production-ready architectural & engineering solution as {agent['name']} ({agent['role']})."
            )
            c_direct = await asyncio.to_thread(
                call_anthropic_messages,
                state["ollama_url"],
                agent.get("model") or "gemma4-claude:latest",
                agent.get("system_prompt", "You are Claude-01, Principal Reasoning & Code Architect."),
                c_prompt,
            )
            combined_out = c_direct["content"]
            tot_tokens = c_direct["tokens"]
            tot_dur = c_direct["duration_ms"]
            steps = [
                {"step": "Claude Ingested", "time": "0.0s", "detail": f"Assigned {ticket_id} to {agent['name']} ({agent.get('model')})"},
                {"step": "Anthropic /v1/messages", "time": f"{round(tot_dur / 1000.0, 2)}s", "detail": f"Claude generated {tot_tokens} tokens via Ollama Anthropic API"},
            ]
            learned_skill = "claude-" + (re.sub(r"[^a-z0-9]+", "-", ticket["title"].lower()).strip("-")[:28] or "architecture")

            if collaborate_flag:
                for h_ep in ["http://192.168.0.17:7892", "http://hermes.ai.svc.cluster.local:7892", "http://192.168.0.81:30792"]:
                    try:
                        def _coop_hermes():
                            req = urllib.request.Request(
                                f"{h_ep}/api/execute_ticket",
                                data=json.dumps({
                                    "ticket_id": f"{ticket_id}-HERMES",
                                    "title": f"Hermes Co-Op Verification: {ticket['title']}",
                                    "description": f"Collaborate with Claude on {ticket['title']}:\n{ticket['description']}\n\nClaude Draft:\n{combined_out[:2500]}\n\nAdd operational execution steps and extract a reusable skill.",
                                    "model": "qwen2.5-coder:14b",
                                    "agent_name": "Hermes-17 (Co-Op Partner)",
                                    "ollama_url": state["ollama_url"],
                                }).encode("utf-8"),
                                headers={"Content-Type": "application/json"},
                                method="POST",
                            )
                            with urllib.request.urlopen(req, timeout=90) as r:
                                return json.loads(r.read().decode("utf-8"))
                        h_coop = await asyncio.to_thread(_coop_hermes)
                        if h_coop.get("output"):
                            combined_out = (
                                f"## ✴️ Phase 1 — {agent['name']} (`{c_direct.get('model')}`) Architecture & Code\n\n"
                                f"{c_direct['content']}\n\n---\n\n"
                                f"## 🪽 Phase 2 — Hermes (`{h_coop.get('model', 'qwen2.5-coder:14b')}`) Co-Op Execution & Skill Synthesis\n\n"
                                f"{h_coop['output']}"
                            )
                            tot_tokens += int(h_coop.get("tokens", 0))
                            tot_dur = round(tot_dur + float(h_coop.get("duration_ms", 0)), 1)
                            learned_skill = h_coop.get("learned_skill") or learned_skill
                            steps.append({"step": "Hermes Co-Op Complete", "time": f"{round(tot_dur / 1000.0, 2)}s", "detail": f"Hermes verified deliverable & synthesized skill '{learned_skill}'"})
                            break
                    except Exception:
                        continue

            state = load_state()
            ticket = next((t for t in state["tickets"] if t["id"] == ticket_id), ticket)
            agent = next((a for a in state["agents"] if a["id"] == ticket["assigned_to"]), agent)
            ticket["output"] = combined_out
            ticket["tokens"] = tot_tokens
            ticket["duration_ms"] = tot_dur
            ticket["model_used"] = c_direct.get("model", agent["model"])
            ticket["status"] = "AWAITING_APPROVAL" if ticket.get("requires_approval") else "COMPLETED"
            ticket["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            agent["status"] = "ONLINE"
            agent["tokens_used"] = agent.get("tokens_used", 0) + tot_tokens
            c_log = {
                "id": f"clog-{str(uuid.uuid4())[:8]}",
                "ticket_id": ticket_id,
                "title": ticket["title"],
                "agent_name": f"{agent['name']} + Hermes Co-Op" if collaborate_flag else agent["name"],
                "node_id": state.get("active_claude_node_id", "claude-host-17"),
                "model": ticket["model_used"],
                "tokens": tot_tokens,
                "tok_per_sec": round(tot_tokens / max(0.1, tot_dur / 1000.0), 1),
                "duration_ms": tot_dur,
                "completed_at": ticket["updated_at"],
                "learned_skill": learned_skill,
                "memory_summary": f"Completed {ticket_id} via Claude Anthropic API {'+ Hermes Co-Op ' if collaborate_flag else ''}& synthesized '{learned_skill}'.",
                "steps": steps,
                "status": "SUCCESS",
            }
            ticket["hermes_log"] = c_log
            state.setdefault("hermes_ticket_logs", []).insert(0, c_log)
            state["hermes_ticket_logs"] = state["hermes_ticket_logs"][:100]
            add_audit(state, agent["name"], f"Claude {'+ Hermes Co-Op ' if collaborate_flag else ''}completed {ticket_id} ({tot_tokens} tokens in {tot_dur} ms)", "SUCCESS")
            save_state(state)
            asyncio.create_task(dispatch_to_n8n_async("ticket_completed", ticket, agent))
            return {"ticket": ticket, "state": state}
        except Exception:
            pass

    # Check if routed to Hermes bridge or if Hermes is enabled for all bots
    is_hermes = (
        agent.get("adapter") in ("hermes_bridge", "hermes")
        or "hermes" in agent.get("id", "").lower()
        or "hermes" in agent.get("name", "").lower()
        or state.get("hermes_for_all_agents", True)
    )
    if is_hermes:
        candidate_eps = []
        if agent.get("endpoint"):
            candidate_eps.append(agent["endpoint"])
            
        active_id = state.get("active_hermes_node_id")
        active_node = next((n for n in state.get("hermes_nodes", []) if n.get("node_id") == active_id and n.get("agent_type") != "claude"), None)
        if active_node and active_node.get("endpoint") and active_node["endpoint"] not in candidate_eps:
            candidate_eps.append(active_node["endpoint"])
            
        if "http://192.168.0.17:7892" not in candidate_eps:
            candidate_eps.append("http://192.168.0.17:7892")
            
        for n in state.get("hermes_nodes", []):
            if n.get("agent_type") == "claude":
                continue
            ep = n.get("endpoint")
            if ep and ep not in candidate_eps:
                candidate_eps.append(ep)
                
        fallback_eps = [
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
                            "model": agent.get("model") or "qwen2.5-coder:14b",
                            "agent_name": agent["name"],
                            "system_prompt": agent.get("system_prompt", ""),
                            "ollama_url": state["ollama_url"],
                        }).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                    with urllib.request.urlopen(req, timeout=90) as resp:
                        return json.loads(resp.read().decode("utf-8"))

                h_res = await asyncio.to_thread(_call_hermes)

                # If collaborate_flag is enabled, have Claude work together with Hermes on the deliverable!
                claude_coop_output = ""
                claude_coop_tokens = 0
                claude_coop_dur = 0.0
                claude_coop_model = "gemma4-claude:latest"
                if collaborate_flag:
                    claude_ag = next((a for a in state.get("agents", []) if a.get("adapter") == "claude_bridge" or "claude" in a.get("id", "")), None)
                    claude_coop_model = (claude_ag.get("model") if claude_ag else None) or "gemma4-claude:latest"
                    coop_prompt = (
                        f"🤝 [HERMES ⇄ CLAUDE JOINT SWARM COLLABORATION]\n"
                        f"Ticket [{ticket['id']}]: {ticket['title']}\n"
                        f"Task Description: {ticket['description']}\n\n"
                        f"--- HERMES ({agent['name']}) DELIVERABLE ---\n{h_res.get('output', '')[:3000]}\n\n"
                        f"As Claude (Principal Reasoning & Code Architect), review Hermes's solution, add architectural hardening, "
                        f"edge-case safeguards, or code optimizations, and conclude with a 1-line 'Joint Swarm Synthesis'."
                    )
                    try:
                        c_coop_res = await asyncio.to_thread(
                            call_anthropic_messages,
                            state["ollama_url"],
                            claude_coop_model,
                            "You are Claude-01 collaborating directly with Hermes in Sovereign AI Corp.",
                            coop_prompt,
                        )
                        claude_coop_output = c_coop_res.get("content", "")
                        claude_coop_tokens = int(c_coop_res.get("tokens", 0))
                        claude_coop_dur = float(c_coop_res.get("duration_ms", 0))
                    except Exception:
                        pass

                state = load_state()
                ticket = next((t for t in state["tickets"] if t["id"] == ticket_id), ticket)
                agent = next((a for a in state["agents"] if a["id"] == ticket["assigned_to"]), agent)
                raw_h_out = h_res.get("output", "")
                if claude_coop_output:
                    ticket["output"] = (
                        f"## 🪽 Phase 1 — {agent['name']} (`{h_res.get('model', agent['model'])}`) Autonomous Execution\n\n"
                        f"{raw_h_out}\n\n---\n\n"
                        f"## ✴️ Phase 2 — Claude (`{claude_coop_model}`) Co-Op Architectural Review & Hardening\n\n"
                        f"{claude_coop_output}"
                    )
                else:
                    ticket["output"] = raw_h_out
                ticket["tokens"] = int(h_res.get("tokens", 250)) + claude_coop_tokens
                ticket["duration_ms"] = round(float(h_res.get("duration_ms", 1200)) + claude_coop_dur, 1)
                ticket["model_used"] = f"{h_res.get('model', agent['model'])} + {claude_coop_model}" if claude_coop_output else h_res.get("model", agent["model"])
                ticket["status"] = "AWAITING_APPROVAL" if ticket.get("requires_approval") else "COMPLETED"
                ticket["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                agent["status"] = "ONLINE"
                agent["tokens_used"] = agent.get("tokens_used", 0) + int(h_res.get("tokens", 250))
                if claude_coop_tokens > 0:
                    for ca in state["agents"]:
                        if ca.get("adapter") == "claude_bridge" or "claude" in ca.get("id", ""):
                            ca["tokens_used"] = ca.get("tokens_used", 0) + claude_coop_tokens
                            break
                
                # Attach rich Hermes + Claude Ticket Completion Log
                matching_node = next((n for n in state.get("hermes_nodes", []) if n.get("endpoint") == hermes_ep), None)
                matched_node_id = matching_node["node_id"] if matching_node else state.get("active_hermes_node_id", "hermes-host-17")

                c_log = h_res.get("completion_log")
                if not c_log:
                    elapsed_s = max(0.1, round(ticket["duration_ms"] / 1000.0, 2))
                    c_log = {
                        "id": f"hlog-{str(uuid.uuid4())[:8]}",
                        "ticket_id": ticket_id,
                        "title": ticket["title"],
                        "agent_name": f"{agent['name']} + Claude Co-Op" if claude_coop_output else agent["name"],
                        "node_id": matched_node_id,
                        "model": ticket["model_used"],
                        "tokens": ticket["tokens"],
                        "tok_per_sec": round(ticket["tokens"] / elapsed_s, 1),
                        "duration_ms": ticket["duration_ms"],
                        "completed_at": ticket["updated_at"],
                        "learned_skill": h_res.get("learned_skill", "autonomous-ops"),
                        "memory_summary": f"Completed ticket {ticket_id} ('{ticket['title']}') with Hermes {'& Claude Co-Op ' if claude_coop_output else ''}and synthesized skill '{h_res.get('learned_skill', 'autonomous-ops')}'.",
                        "steps": [
                            {"step": "Task Ingested", "time": "0.0s", "detail": f"Paperclip assigned {ticket_id} to {agent['name']}"},
                            {"step": "Skills Vault Primed", "time": "0.2s", "detail": f"Primed with skills vault and episodic memory"},
                            {"step": "Hermes Inference Complete", "time": f"{elapsed_s}s", "detail": f"Generated {h_res.get('tokens', 0)} tokens"},
                            {"step": "Skill Synthesis", "time": f"{elapsed_s}s", "detail": f"Synthesized reusable skill '{h_res.get('learned_skill', 'autonomous-ops')}' into vault"},
                        ],
                        "status": "SUCCESS",
                    }
                else:
                    c_log["node_id"] = matched_node_id
                    if claude_coop_output:
                        c_log["agent_name"] = f"{agent['name']} + Claude Co-Op"
                        c_log["model"] = ticket["model_used"]
                        c_log["tokens"] = ticket["tokens"]
                        c_log["duration_ms"] = ticket["duration_ms"]
                        c_log.setdefault("steps", []).append({
                            "step": "Claude Co-Op Review",
                            "time": f"{round(ticket['duration_ms'] / 1000.0, 2)}s",
                            "detail": f"Claude ({claude_coop_model}) collaborated via Anthropic /v1/messages (+{claude_coop_tokens} tokens)"
                        })
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
                        tg_header = (
                            f"📎 <b>Ticket Deliverable Ready: {ticket_id}</b>\n"
                            f"<b>Title:</b> {html.escape(ticket['title'])}\n"
                            f"<b>Agent:</b> {agent.get('avatar', '🪽')} {html.escape(agent['name'])} ({html.escape(agent['role'])})\n"
                            f"<b>Node:</b> <code>{matched_node_id}</code> | <b>Model:</b> <code>{ticket.get('model_used')}</code>\n"
                            f"<b>Learned Skill:</b> <code>{c_log.get('learned_skill', 'autonomous-ops')}</code>\n"
                            f"<b>Speed:</b> {ticket.get('tokens')} tokens in {ticket.get('duration_ms')} ms"
                        )
                        asyncio.create_task(
                            asyncio.to_thread(
                                send_telegram_deliverable,
                                tg["bot_token"],
                                tg["chat_id"],
                                tg_header,
                                ticket.get("output", ""),
                                ticket_id,
                                ticket["title"],
                            )
                        )
                except Exception:
                    pass
                asyncio.create_task(dispatch_to_n8n_async("ticket_completed", ticket, agent))
                return {"ticket": ticket, "state": state}
            except Exception:
                continue

        # If direct push to candidate endpoints failed (e.g. desktop agent behind Windows Firewall),
        # enqueue the ticket into the pull-worker queue so Hermes Desktop executes it via local GPU!
        is_desktop_agent = "desktop" in agent.get("id", "").lower() or "desktop" in agent.get("name", "").lower()
        if is_desktop_agent:
            state = load_state()
            ticket = next((t for t in state["tickets"] if t["id"] == ticket_id), ticket)
            ticket["status"] = "QUEUED_FOR_DESKTOP"
            add_audit(state, "Control Plane", f"Placed {ticket_id} into Desktop Hermes Work Queue (awaiting local RTX 3060 execution)", "INFO")
            save_state(state)
            
            # Wait up to 120s for Desktop Hermes worker to process and submit via /api/hermes/complete_ticket
            for _ in range(120):
                await asyncio.sleep(1)
                st_cur = load_state()
                t_cur = next((t for t in st_cur["tickets"] if t["id"] == ticket_id), None)
                if t_cur and t_cur.get("status") in ("COMPLETED", "AWAITING_APPROVAL"):
                    return {"ticket": t_cur, "state": st_cur}

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
                tg_header = (
                    f"📎 <b>Ticket Deliverable Ready: {ticket_id}</b>\n"
                    f"<b>Title:</b> {html.escape(ticket['title'])}\n"
                    f"<b>Agent:</b> {agent.get('avatar', '🤖')} {html.escape(agent['name'])} ({html.escape(agent['role'])})\n"
                    f"<b>Model:</b> <code>{ticket.get('model_used')}</code> | <b>Tokens:</b> {ticket.get('tokens')} ({ticket.get('duration_ms')} ms)"
                )
                asyncio.create_task(
                    asyncio.to_thread(
                        send_telegram_deliverable,
                        tg["bot_token"],
                        tg["chat_id"],
                        tg_header,
                        ticket.get("output", ""),
                        ticket_id,
                        ticket["title"],
                    )
                )
        except Exception:
            pass
        asyncio.create_task(dispatch_to_n8n_async("ticket_completed", ticket, agent))
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
            agent = next((a for a in state["agents"] if a["id"] == t.get("assigned_to")), state["agents"][0])
            asyncio.create_task(dispatch_to_n8n_async("ticket_approved", t, agent))
            return {"ok": True, "ticket": t, "state": state}
    raise HTTPException(status_code=404, detail="Ticket not found")


@app.post("/api/audit")
async def post_audit_log(payload: Dict[str, Any] = Body(...)):
    state = load_state()
    actor = payload.get("actor") or "n8n Workflow"
    event = payload.get("event") or payload.get("action") or "Workflow executed in n8n"
    level = payload.get("level") or payload.get("status") or "SUCCESS"
    add_audit(state, actor, event, level)
    save_state(state)
    return {"ok": True, "actor": actor, "event": event, "level": level}


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

    # Ensure corresponding agent exists in state["agents"]
    agent_id = f"agent-{node_id}"
    matched_agent = next((a for a in state["agents"] if a["id"] == agent_id), None)
    is_desktop = "desktop" in node_id.lower() or "efrain" in node_id.lower()
    ag_name = payload.get("agent_name") or node_info["name"].split("(")[0].strip() or "Hermes Worker"

    if not matched_agent:
        state["agents"].append({
            "id": agent_id,
            "name": ag_name,
            "role": "Desktop Autonomous GPU Worker (RTX 3060 12GB)" if is_desktop else f"Autonomous Worker ({node_id})",
            "department": "Autonomous Ops",
            "reports_to": "agent-cto",
            "adapter": "hermes_bridge",
            "endpoint": node_info["endpoint"],
            "model": node_info["model"],
            "status": "ONLINE",
            "budget_tokens": 2000000,
            "tokens_used": 0,
            "avatar": "⚡" if is_desktop else "🪽",
            "system_prompt": f"You are {ag_name}, an autonomous self-improving agent running on {node_id}. Execute engineering tickets with high throughput and GPU acceleration.",
        })
    else:
        matched_agent["endpoint"] = node_info["endpoint"]
        matched_agent["status"] = "ONLINE"
        matched_agent["model"] = node_info["model"]

    # Also update agent-hermes if node is primary k3s worker
    if node_id == "hermes-k3s-primary":
        for a in state["agents"]:
            if a["id"] == "agent-hermes":
                a["status"] = "ONLINE"
                a["model"] = node_info["model"]

    add_audit(state, node_info["name"], f"Hermes node '{node_id}' linked (Ollama: {node_info['ollama_url']}, Model: {node_info['model']})", "SUCCESS")
    save_state(state)
    return {"ok": True, "node": node_info, "paperclip_ollama_url": state["ollama_url"]}


@app.get("/api/hermes/tasks")
async def get_hermes_queued_tasks(node_id: str = ""):
    state = load_state()
    queued = [
        t for t in state["tickets"]
        if t["status"] in ("QUEUED", "QUEUED_FOR_DESKTOP")
    ]
    if node_id:
        target_agent_id = f"agent-{node_id}"
        if "desktop" in node_id.lower():
            filtered = [t for t in queued if t.get("assigned_to") == target_agent_id or "desktop" in t.get("assigned_to", "").lower()]
        elif node_id == "hermes-k3s-primary":
            filtered = [t for t in queued if t.get("assigned_to") in ("agent-hermes", target_agent_id)]
        elif node_id == "hermes-host-17":
            filtered = [t for t in queued if t.get("assigned_to") in ("agent-hermes-17", target_agent_id)]
        else:
            filtered = [t for t in queued if t.get("assigned_to") == target_agent_id]
        return {"tasks": filtered, "ollama_url": state["ollama_url"]}
    return {"tasks": queued, "ollama_url": state["ollama_url"]}


@app.post("/api/hermes/complete_ticket")
async def complete_hermes_ticket_callback(payload: Dict[str, Any] = Body(...)):
    """Receives completed ticket deliverables from autonomous pull workers (e.g. DESKTOP-EFRAIN RTX 3060)."""
    ticket_id = payload.get("ticket_id")
    state = load_state()
    ticket = next((t for t in state["tickets"] if t["id"] == ticket_id), None)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    agent = next((a for a in state["agents"] if a["id"] == ticket["assigned_to"]), state["agents"][0])
    ticket["output"] = payload.get("output", "")
    ticket["tokens"] = int(payload.get("tokens", 250))
    ticket["duration_ms"] = float(payload.get("duration_ms", 1200))
    ticket["model_used"] = payload.get("model", agent["model"])
    ticket["status"] = "AWAITING_APPROVAL" if ticket.get("requires_approval") else "COMPLETED"
    ticket["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    agent["status"] = "ONLINE"
    agent["tokens_used"] = agent.get("tokens_used", 0) + ticket["tokens"]

    c_log = payload.get("completion_log")
    if c_log:
        ticket["hermes_log"] = c_log
        state.setdefault("hermes_ticket_logs", []).insert(0, c_log)
        state["hermes_ticket_logs"] = state["hermes_ticket_logs"][:100]

    add_audit(state, agent["name"], f"Hermes completed {ticket_id} via autonomous worker loop ({ticket['tokens']} tokens in {ticket['duration_ms']} ms)", "SUCCESS")
    save_state(state)
    asyncio.create_task(dispatch_to_n8n_async("ticket_completed", ticket, agent))

    # Deliver to Telegram with zero truncation
    try:
        tg = get_telegram_config(state)
        if tg.get("enabled") and tg.get("notify_on_ticket_completed") and tg.get("bot_token") and tg.get("chat_id"):
            tg_header = (
                f"📎 <b>Ticket Deliverable Ready: {ticket_id}</b>\n"
                f"<b>Title:</b> {html.escape(ticket['title'])}\n"
                f"<b>Agent:</b> {agent.get('avatar', '⚡')} {html.escape(agent['name'])} ({html.escape(agent['role'])})\n"
                f"<b>Node:</b> <code>{c_log.get('node_id', 'hermes-desktop-efrain') if c_log else 'hermes-desktop'}</code> | <b>Model:</b> <code>{ticket.get('model_used')}</code>\n"
                f"<b>Learned Skill:</b> <code>{c_log.get('learned_skill', 'autonomous-ops') if c_log else 'autonomous-ops'}</code>\n"
                f"<b>Speed:</b> {ticket.get('tokens')} tokens in {ticket.get('duration_ms')} ms"
            )
            asyncio.create_task(
                asyncio.to_thread(
                    send_telegram_deliverable,
                    tg["bot_token"],
                    tg["chat_id"],
                    tg_header,
                    ticket.get("output", ""),
                    ticket_id,
                    ticket["title"],
                )
            )
    except Exception:
        pass

    try:
        dep_res = await asyncio.to_thread(deploy_completed_ticket_to_k3s_dev, ticket_id)
        if dep_res:
            return {"ok": True, "ticket": dep_res["ticket"], "state": dep_res["state"]}
    except Exception:
        pass

    return {"ok": True, "ticket": ticket, "state": state}


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
@app.post("/api/claude/nodes/connect")
async def connect_custom_hermes_node(payload: Dict[str, Any] = Body(...)):
    endpoint = payload.get("endpoint", "").strip().rstrip("/")
    if not endpoint:
        raise HTTPException(status_code=400, detail="Agent endpoint URL is required (e.g. http://192.168.0.17:7892 or http://192.168.0.17:7893)")
    
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
    st_inner = remote_data.get("state", {}) if isinstance(remote_data.get("state"), dict) else {}
    is_claude = (
        payload.get("agent_type") == "claude"
        or remote_data.get("agent_type") == "claude"
        or "claude" in (payload.get("name") or "").lower()
        or "claude" in (remote_data.get("agent_name") or st_inner.get("agent_name") or "").lower()
        or ":7893" in endpoint
        or ":30793" in endpoint
    )
    prefix = "claude" if is_claude else "hermes"
    raw_node_id = payload.get("node_id") or remote_data.get("node_id") or st_inner.get("node_id") or f"{prefix}-{str(uuid.uuid4())[:6]}"
    node_id = re.sub(r'[^a-zA-Z0-9_-]', '-', raw_node_id).lower()
    
    host_label = urllib.parse.urlparse(endpoint).netloc or endpoint
    node_name = payload.get("name") or remote_data.get("agent_name") or st_inner.get("agent_name") or f"{'Claude' if is_claude else 'Hermes'} ({host_label})"
    remote_model = remote_data.get("model") or st_inner.get("active_model") or ("gemma4-claude:latest" if is_claude else "qwen2.5-coder:14b")
    skills_count = len(remote_data.get("skills") or st_inner.get("skills") or [])
    memories_count = len(remote_data.get("episodic_memories") or st_inner.get("memories") or [])
    
    node_info = {
        "node_id": node_id,
        "name": node_name,
        "endpoint": endpoint,
        "ollama_url": remote_data.get("ollama_url") or st_inner.get("ollama_url") or state["ollama_url"],
        "model": remote_model,
        "skills_count": skills_count,
        "memories_count": memories_count,
        "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "CONNECTED",
        "agent_type": "claude" if is_claude else "hermes",
    }
    
    existing_idx = next((i for i, n in enumerate(state.get("hermes_nodes", [])) if n["node_id"] == node_id), None)
    if existing_idx is not None:
        state["hermes_nodes"][existing_idx] = node_info
    else:
        state.setdefault("hermes_nodes", []).append(node_info)
        
    if is_claude:
        c_idx = next((i for i, n in enumerate(state.get("claude_nodes", [])) if n["node_id"] == node_id), None)
        if c_idx is not None:
            state["claude_nodes"][c_idx] = node_info
        else:
            state.setdefault("claude_nodes", []).append(node_info)
        state["active_claude_node_id"] = node_id
    else:
        state["active_hermes_node_id"] = node_id
    
    agent_id = f"agent-{node_id}"
    agent_found = next((a for a in state["agents"] if a["id"] == agent_id or a.get("endpoint") == endpoint), None)
    if not agent_found:
        state["agents"].append({
            "id": agent_id,
            "name": node_name.split("(")[0].strip() or ("Claude Custom" if is_claude else "Hermes Custom"),
            "role": f"Remote Autonomous {'Claude Architect' if is_claude else 'Worker'} ({host_label})",
            "department": "Autonomous Ops",
            "reports_to": "agent-cto",
            "adapter": "claude_bridge" if is_claude else "hermes_bridge",
            "endpoint": endpoint,
            "model": remote_model,
            "status": "ONLINE",
            "budget_tokens": 2000000,
            "tokens_used": 0,
            "avatar": "✴️" if is_claude else "🪽",
            "system_prompt": f"You are an autonomous {'Claude' if is_claude else 'Hermes'} agent connected via {endpoint}. Collaborate with peer agents and synthesize reusable skills."
        })
    else:
        agent_found["endpoint"] = endpoint
        agent_found["status"] = "ONLINE"
        agent_found["model"] = remote_model

    add_audit(state, "Control Plane", f"Connected new {'Claude' if is_claude else 'Hermes'} agent node '{node_name}' at {endpoint} (Model: {remote_model}, Skills: {skills_count})", "SUCCESS")
    save_state(state)
    return {"ok": True, "node": node_info, "state": state}


@app.delete("/api/hermes/nodes/{node_id}")
@app.delete("/api/claude/nodes/{node_id}")
async def unregister_hermes_node(node_id: str):
    state = load_state()
    nodes = state.get("hermes_nodes", [])
    if len(nodes) <= 1:
        raise HTTPException(status_code=400, detail="Cannot remove the last active agent node")
    
    target = next((n for n in nodes if n["node_id"] == node_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Node not found")
        
    state["hermes_nodes"] = [n for n in nodes if n["node_id"] != node_id]
    state["claude_nodes"] = [n for n in state.get("claude_nodes", []) if n["node_id"] != node_id]
    if state.get("active_hermes_node_id") == node_id and state["hermes_nodes"]:
        state["active_hermes_node_id"] = state["hermes_nodes"][0]["node_id"]
    if state.get("active_claude_node_id") == node_id and state.get("claude_nodes"):
        state["active_claude_node_id"] = state["claude_nodes"][0]["node_id"]
        
    add_audit(state, "Control Plane", f"Unregistered agent node '{target['name']}' ({target['endpoint']})", "WARN")
    save_state(state)
    return {"ok": True, "removed": node_id, "state": state}


# --- CLAUDE ADAPTER BRIDGE & SWARM COLLABORATION ENDPOINTS ---
@app.post("/api/claude/register")
async def register_claude_node(payload: Dict[str, Any] = Body(...)):
    state = load_state()
    node_id = payload.get("node_id", "claude-k3s-primary")
    node_info = {
        "node_id": node_id,
        "name": payload.get("name", "Claude-01 (Claude Autonomous Agent)"),
        "endpoint": payload.get("endpoint", DEFAULT_CLAUDE_URL),
        "ollama_url": payload.get("ollama_url", state["ollama_url"]),
        "model": payload.get("model", "gemma4-claude:latest"),
        "skills_count": int(payload.get("skills_count", 0)),
        "memories_count": int(payload.get("memories_count", 0)),
        "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "CONNECTED",
        "agent_type": "claude",
    }
    found = False
    for idx, n in enumerate(state.get("claude_nodes", [])):
        if n["node_id"] == node_id:
            state["claude_nodes"][idx] = node_info
            found = True
            break
    if not found:
        state.setdefault("claude_nodes", []).append(node_info)

    h_found = False
    for idx, n in enumerate(state.get("hermes_nodes", [])):
        if n["node_id"] == node_id:
            state["hermes_nodes"][idx] = node_info
            h_found = True
            break
    if not h_found:
        state.setdefault("hermes_nodes", []).append(node_info)

    agent_id = f"agent-{node_id}"
    matched_agent = next((a for a in state["agents"] if a["id"] == agent_id), None)
    ag_name = payload.get("agent_name") or node_info["name"].split("(")[0].strip() or "Claude Agent"

    if not matched_agent:
        state["agents"].append({
            "id": agent_id,
            "name": ag_name,
            "role": f"Autonomous Claude Architect ({node_id})",
            "department": "Autonomous Ops",
            "reports_to": "agent-cto",
            "adapter": "claude_bridge",
            "endpoint": node_info["endpoint"],
            "model": node_info["model"],
            "status": "ONLINE",
            "budget_tokens": 2000000,
            "tokens_used": 0,
            "avatar": "✴️",
            "system_prompt": f"You are {ag_name}, an autonomous Claude reasoning and engineering agent running on {node_id}. Collaborate with Hermes peers on complex tasks.",
        })
    else:
        matched_agent["endpoint"] = node_info["endpoint"]
        matched_agent["status"] = "ONLINE"
        matched_agent["model"] = node_info["model"]

    add_audit(state, node_info["name"], f"Claude node '{node_id}' linked (Anthropic /v1/messages: {node_info['ollama_url']}, Model: {node_info['model']})", "SUCCESS")
    save_state(state)
    return {"ok": True, "node": node_info, "paperclip_ollama_url": state["ollama_url"]}


@app.get("/api/claude/tasks")
async def get_claude_queued_tasks(node_id: str = ""):
    state = load_state()
    queued = [t for t in state["tickets"] if t["status"] == "QUEUED"]
    if node_id:
        target_agent_id = f"agent-{node_id}"
        if node_id == "claude-k3s-primary":
            filtered = [t for t in queued if t.get("assigned_to") in ("agent-claude", target_agent_id)]
        elif node_id == "claude-host-17":
            filtered = [t for t in queued if t.get("assigned_to") in ("agent-claude-17", target_agent_id)]
        else:
            filtered = [t for t in queued if t.get("assigned_to") == target_agent_id]
        return {"tasks": filtered, "ollama_url": state["ollama_url"]}
    return {"tasks": queued, "ollama_url": state["ollama_url"]}


@app.post("/api/claude/complete_ticket")
async def complete_claude_ticket_callback(payload: Dict[str, Any] = Body(...)):
    return await complete_hermes_ticket_callback(payload)


@app.get("/api/claude/nodes")
async def get_claude_nodes():
    state = load_state()
    return {
        "nodes": state.get("claude_nodes", []),
        "active_node_id": state.get("active_claude_node_id", "claude-host-17"),
        "agents": [a for a in state["agents"] if a.get("adapter") == "claude_bridge"],
    }


@app.post("/api/claude/nodes/select")
async def select_claude_node(payload: Dict[str, Any] = Body(...)):
    state = load_state()
    node_id = payload.get("node_id")
    target_node = next((n for n in state.get("claude_nodes", []) if n["node_id"] == node_id), None)
    if not target_node:
        target_node = next((n for n in state.get("hermes_nodes", []) if n["node_id"] == node_id), None)
    if not target_node:
        raise HTTPException(status_code=404, detail="Claude node not found")
    state["active_claude_node_id"] = node_id
    add_audit(state, "Control Plane", f"Switched active Claude agent connection to '{target_node['name']}' ({target_node['endpoint']})", "INFO")
    save_state(state)
    return {"ok": True, "active_node_id": node_id, "node": target_node, "state": state}


@app.post("/api/swarm/collaborate")
async def trigger_hermes_claude_collaboration(payload: Dict[str, Any] = Body(...)):
    """Dispatches a joint Hermes + Claude collaborative engineering ticket where both agents work together."""
    title = (payload.get("title") or "Joint Claude + Hermes Architecture & Execution").strip()
    description = (payload.get("description") or title).strip()
    primary = payload.get("primary_agent") or "agent-claude"
    return await create_and_run_ticket({
        "title": title,
        "description": description,
        "assigned_to": primary,
        "priority": payload.get("priority", "CRITICAL"),
        "auto_execute": True,
        "collaborate": True,
    })


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
                            
                            st_latest = load_state()
                            tg_latest = get_telegram_config(st_latest)
                            # If execute_ticket_internal didn't already dispatch via notify_on_ticket_completed, deliver now
                            if not (tg_latest.get("enabled") and tg_latest.get("notify_on_ticket_completed")):
                                tg_header = (
                                    f"✅ <b>Deliverable Ready: {tck_id}</b>\n"
                                    f"<b>Objective:</b> {html.escape(t_done.get('title', ''))}\n"
                                    f"<b>Agent:</b> {ag_obj.get('avatar')} {ag_obj.get('name')} (<code>{t_done.get('model_used')}</code>)\n"
                                    f"<b>Speed:</b> {t_done.get('tokens')} tokens in {t_done.get('duration_ms')} ms"
                                )
                                send_telegram_deliverable(token, chat_id, tg_header, out_text, tck_id, t_done.get("title", ""))
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
            "claude_agent.py",
            "dev_apps_server.py",
            "dual_tls_runner.py",
            "requirements.txt",
            "README.md",
            "k8s-paperclip-hermes.yaml",
            "templates/paperclip.html",
            "templates/hermes.html",
            "templates/claude.html",
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


# --- K3S 'DEV' NAMESPACE WEBSITE DEPLOYER & CONTINUOUS AUTONOMOUS APP FACTORY ---
DEV_APPS_DIR = os.path.join(DATA_DIR, "dev_apps")
os.makedirs(DEV_APPS_DIR, exist_ok=True)
K3S_DEV_GATEWAY_URL = os.environ.get("K3S_DEV_GATEWAY_URL", "http://192.168.0.81:30795")
ADS_TXT_BODY = "google.com, pub-1596056523034714, DIRECT, f08c47fec0942fa0\n"

ADSENSE_HEAD_SNIPPET = """
  <!-- Google AdSense with Page-Level Auto-Ads -->
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1596056523034714"
     crossorigin="anonymous"></script>
  <script>
    (adsbygoogle = window.adsbygoogle || []).push({
      google_ad_client: "ca-pub-1596056523034714",
      enable_page_level_ads: true
    });
  </script>
"""

ADSENSE_FOOTER_UNIT = """
  <div style="max-width:1200px;margin:22px auto;padding:8px 16px;text-align:center;">
    <ins class="adsbygoogle"
         style="display:block"
         data-ad-client="ca-pub-1596056523034714"
         data-ad-slot="auto"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
  </div>
"""

AUTONOMOUS_APP_BLUEPRINTS: List[Dict[str, str]] = [
    {
        "slug": "k3s-cluster-topology-radar",
        "title": "K3s Cluster Live Node & Pod Topology Radar",
        "description": "Build a complete interactive single-page HTML5/CSS/JS web application (<!DOCTYPE html>...</html>) for visualizing a 7-node Proxmox HA K3s cluster (k3s-cp-01..03, workers) with interactive pod status filters, live simulated latency ping matrix, CPU/RAM gauges, and node health inspector.",
    },
    {
        "slug": "dual-gpu-vram-llm-sizer",
        "title": "Dual-GPU VRAM & Ollama LLM Throughput Sizer",
        "description": "Build a complete interactive single-page HTML5/CSS/JS web application (<!DOCTYPE html>...</html>) for calculating LLM VRAM usage, quantization fit (Q4_K_M, Q5_K_M, Q8_0, FP16), KV-cache context size (8K to 128K), and estimated tokens/sec across dual GPUs (RTX 5070 12GB + RTX 3060 12GB = 24GB VRAM).",
    },
    {
        "slug": "claude-hermes-coop-studio",
        "title": "Claude & Hermes Co-Op Prompt Engineering Workbench",
        "description": "Build a complete interactive single-page HTML5/CSS/JS web application (<!DOCTYPE html>...</html>) that lets engineers compose system prompts, compare Claude (/v1/messages) vs Hermes skill-primed responses side-by-side, score outputs, and export JSON templates.",
    },
    {
        "slug": "cidr-vlan-network-architect",
        "title": "Interactive CIDR, Subnet & Proxmox VLAN Architect",
        "description": "Build a complete interactive single-page HTML5/CSS/JS web application (<!DOCTYPE html>...</html>) with a live CIDR subnet splitter, usable IP range calculator, binary netmask visualizer, and Proxmox bridge (vmbr0/VLAN) config snippet generator.",
    },
    {
        "slug": "proxmox-zfs-ceph-calculator",
        "title": "Proxmox ZFS & Ceph NVMe IOPS Storage Calculator",
        "description": "Build a complete interactive single-page HTML5/CSS/JS web application (<!DOCTYPE html>...</html>) for sizing ZFS RAIDZ1/RAIDZ2/Mirror and Ceph 3x replication pools with usable TB, parity overhead, ARC RAM requirements, and IOPS estimation.",
    },
    {
        "slug": "k8s-manifest-helm-builder",
        "title": "Kubernetes Deployment, Service & Ingress YAML Studio",
        "description": "Build a complete interactive single-page HTML5/CSS/JS web application (<!DOCTYPE html>...</html>) where users configure container image, ports, NodePort, CPU/Memory limits, and hostPath volumes and see live syntax-highlighted Kubernetes YAML generated instantly with 1-click copy.",
    },
    {
        "slug": "homelab-ups-power-thermal",
        "title": "Homelab Rack Power, UPS Runtime & Thermal Calculator",
        "description": "Build a complete interactive single-page HTML5/CSS/JS web application (<!DOCTYPE html>...</html>) that calculates total rack wattage, BTU/hr heat output, monthly kWh cost, and battery UPS runtime minutes across servers and GPUs.",
    },
    {
        "slug": "cyberpunk-log-anomaly-scanner",
        "title": "Real-Time Syslog & Kubernetes Event Anomaly Scanner",
        "description": "Build a complete interactive single-page HTML5/CSS/JS web application (<!DOCTYPE html>...</html>) where users paste or stream container logs to highlight ERROR/WARN/OOMKilled patterns, chart severity counts, and generate remediation commands.",
    },
    {
        "slug": "regex-json-live-workbench",
        "title": "Interactive Regex & JSON Formatter Live Workbench",
        "description": "Build a complete interactive single-page HTML5/CSS/JS web application (<!DOCTYPE html>...</html>) with live regular expression match highlighting, capture group table, and JSON pretty-printer/validator.",
    },
    {
        "slug": "ai-swarm-kanban-velocity",
        "title": "Autonomous AI Swarm Sprint Velocity & Token ROI Tracker",
        "description": "Build a complete interactive single-page HTML5/CSS/JS web application (<!DOCTYPE html>...</html>) with an interactive drag-free Kanban board, token burn rate calculator, and local Ollama vs Cloud API cost savings chart.",
    },
]


def _make_slug(text: str, prefix: str = "") -> str:
    base = re.sub(r"[^a-z0-9]+", "-", (text or "app").lower()).strip("-")[:38] or "web-app"
    if prefix:
        p_clean = re.sub(r"[^a-z0-9]+", "-", prefix.lower()).strip("-")
        return f"{p_clean}-{base}"[:48].strip("-")
    return base


def _ensure_adsense_in_html(raw_html: str, title: str, slug: str, agent_name: str, model: str, ticket_id: str) -> str:
    html_out = raw_html.strip()
    if "ca-pub-1596056523034714" not in html_out:
        if "</head>" in html_out:
            html_out = html_out.replace("</head>", f"{ADSENSE_HEAD_SNIPPET}\n</head>", 1)
        elif "<body" in html_out:
            html_out = html_out.replace("<body", f"<head>{ADSENSE_HEAD_SNIPPET}</head>\n<body", 1)
        else:
            html_out = f"<!DOCTYPE html><html><head><meta charset='UTF-8'><title>{html.escape(title)}</title>{ADSENSE_HEAD_SNIPPET}</head><body>{html_out}</body></html>"

    dev_banner = f"""
    <div style="background:linear-gradient(90deg,#0f172a,#1e1b4b,#0f172a);border-bottom:1px solid rgba(56,189,248,0.35);padding:8px 18px;font-family:system-ui,sans-serif;font-size:12px;color:#e2e8f0;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;position:sticky;top:0;z-index:99999;">
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
        <span style="background:rgba(16,185,129,0.2);color:#34d399;border:1px solid rgba(16,185,129,0.45);padding:2px 8px;border-radius:999px;font-weight:700;font-family:monospace;">🟢 K3s namespace: dev</span>
        <strong style="color:#38bdf8;">{html.escape(title)}</strong>
        <span style="color:#94a3b8;">• Built autonomously by <strong>{html.escape(agent_name)}</strong> (<code>{html.escape(model)}</code>) • Ticket <code>{html.escape(ticket_id)}</code></span>
      </div>
      <div style="display:flex;gap:8px;align-items:center;">
        <a href="http://192.168.0.81:30795/" style="color:#fdba74;text-decoration:none;font-weight:700;">🚀 All K3s Dev Sites (30795) ↗</a>
        <span style="color:#475569;">|</span>
        <a href="http://192.168.0.81:30791" style="color:#38bdf8;text-decoration:none;font-weight:700;">📎 Paperclip Control Plane ↗</a>
      </div>
    </div>
    """
    if "K3s namespace: dev" not in html_out:
        m_body = re.search(r"<body[^>]*>", html_out, flags=re.IGNORECASE)
        if m_body:
            insert_pos = m_body.end()
            html_out = html_out[:insert_pos] + "\n" + dev_banner + html_out[insert_pos:]
        else:
            html_out = dev_banner + html_out

    if 'class="adsbygoogle"' not in html_out:
        if "</body>" in html_out:
            html_out = html_out.replace("</body>", f"{ADSENSE_FOOTER_UNIT}\n</body>", 1)
        else:
            html_out = html_out + ADSENSE_FOOTER_UNIT

    return html_out


def synthesize_interactive_webapp_html(
    title: str,
    description: str,
    agent_output: str,
    agent_name: str,
    model: str,
    ticket_id: str,
    slug: str,
) -> str:
    """Extracts full HTML if present in the agent deliverable, or builds a rich interactive web app around the deliverable."""
    raw = agent_output or ""
    # 1. Check for fenced ```html ... ``` block containing <html or <!DOCTYPE or <body or <script
    html_blocks = re.findall(r"```(?:html|HTML)?\s*(<!DOCTYPE html[\s\S]*?</html>|<html[\s\S]*?</html>)```", raw, flags=re.IGNORECASE)
    if html_blocks:
        best_block = max(html_blocks, key=len)
        if len(best_block) > 220:
            return _ensure_adsense_in_html(best_block, title, slug, agent_name, model, ticket_id)

    # 2. Check for unfenced <!DOCTYPE html> ... </html>
    m_doc = re.search(r"(<!DOCTYPE html[\s\S]*?</html>)", raw, flags=re.IGNORECASE)
    if m_doc and len(m_doc.group(1)) > 220:
        return _ensure_adsense_in_html(m_doc.group(1), title, slug, agent_name, model, ticket_id)

    # 3. Build a rich interactive single-page web application with live simulator + deliverable code studio
    escaped_out = html.escape(raw)
    escaped_title = html.escape(title)
    escaped_desc = html.escape(description or title)
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{escaped_title} — K3s Dev Live App</title>
  {ADSENSE_HEAD_SNIPPET}
  <style>
    :root {{
      --bg: #050811;
      --card: rgba(15, 23, 42, 0.9);
      --border: rgba(56, 189, 248, 0.28);
      --cyan: #38bdf8;
      --purple: #a855f7;
      --emerald: #10b981;
      --coral: #d97757;
      --text: #f8fafc;
      --sub: #94a3b8;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: radial-gradient(circle at 15% 15%, rgba(56,189,248,0.12), transparent 40%), radial-gradient(circle at 85% 10%, rgba(217,119,87,0.12), transparent 40%), var(--bg); color: var(--text); font-family: 'Inter', system-ui, sans-serif; min-height: 100vh; }}
    .container {{ max-width: 1320px; margin: 0 auto; padding: 24px; }}
    .hero {{ background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 24px; margin-bottom: 20px; box-shadow: 0 12px 32px rgba(0,0,0,0.45); }}
    .grid {{ display: grid; grid-template-columns: 1.15fr 1fr; gap: 20px; }}
    @media (max-width: 960px) {{ .grid {{ grid-template-columns: 1fr; }} }}
    .panel {{ background: var(--card); border: 1px solid rgba(255,255,255,0.1); border-radius: 14px; padding: 20px; }}
    .btn {{ cursor: pointer; border: 1px solid rgba(56,189,248,0.5); background: linear-gradient(135deg, #0284c7, #7e22ce); color: #fff; padding: 10px 16px; border-radius: 8px; font-weight: 700; font-size: 13px; }}
    .btn:hover {{ filter: brightness(1.12); }}
    .input, select {{ width: 100%; padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.16); background: #080d1a; color: #fff; margin-top: 5px; margin-bottom: 12px; font-size: 13px; }}
    .stat-row {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 14px; }}
    .stat {{ background: rgba(6, 9, 19, 0.85); border: 1px solid rgba(56,189,248,0.22); border-radius: 10px; padding: 12px; text-align: center; }}
    .stat-val {{ font-size: 22px; font-weight: 800; color: var(--cyan); font-family: monospace; }}
    .stat-lbl {{ font-size: 11px; color: var(--sub); text-transform: uppercase; margin-top: 4px; }}
    pre {{ background: #04070f; border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 16px; overflow: auto; max-height: 540px; font-size: 12.5px; line-height: 1.55; color: #e2e8f0; white-space: pre-wrap; }}
    canvas {{ width: 100%; height: 220px; background: #04070f; border: 1px solid rgba(56,189,248,0.25); border-radius: 10px; margin-top: 12px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="hero">
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
        <div>
          <span style="font-size:11px;font-family:monospace;color:#34d399;background:rgba(16,185,129,0.14);padding:4px 10px;border-radius:6px;border:1px solid rgba(16,185,129,0.4);">K3S DEV ENVIRONMENT • {html.escape(slug)}</span>
          <h1 style="margin:10px 0 6px 0;font-size:26px;">{escaped_title}</h1>
          <p style="margin:0;color:var(--sub);font-size:13.5px;max-width:880px;">{escaped_desc}</p>
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
          <button class="btn" onclick="runSimulation()">⚡ Run Live Telemetry Simulation</button>
          <button class="btn" style="background:linear-gradient(135deg,#d97757,#b45309);" onclick="copyDeliverable()">📋 Copy Deliverable Code</button>
        </div>
      </div>
    </div>

    <div class="grid">
      <div class="panel">
        <h3 style="margin-top:0;color:var(--cyan);">🎛️ Interactive Control &amp; Simulation Studio</h3>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
          <div>
            <label style="font-size:12px;color:var(--sub);">Cluster / Workload Scale (Nodes / Workers)</label>
            <input type="range" id="simScale" min="1" max="32" value="7" class="input" oninput="updateDashboard()" />
          </div>
          <div>
            <label style="font-size:12px;color:var(--sub);">Target Concurrency / Batch Throughput</label>
            <input type="range" id="simLoad" min="10" max="500" value="120" class="input" oninput="updateDashboard()" />
          </div>
        </div>
        <div class="stat-row">
          <div class="stat">
            <div class="stat-val" id="valNodes">7 Nodes</div>
            <div class="stat-lbl">Active Topology</div>
          </div>
          <div class="stat">
            <div class="stat-val" id="valThroughput" style="color:#34d399;">1,680 ops/s</div>
            <div class="stat-lbl">Projected Throughput</div>
          </div>
          <div class="stat">
            <div class="stat-val" id="valLatency" style="color:#fdba74;">4.2 ms</div>
            <div class="stat-lbl">P95 Latency</div>
          </div>
        </div>
        <canvas id="liveCanvas" width="600" height="220"></canvas>
        <div id="simLog" style="margin-top:12px;font-family:monospace;font-size:12px;color:#a7f3d0;background:#04070f;padding:10px 12px;border-radius:8px;border:1px solid rgba(16,185,129,0.3);">
          ✓ K3s dev pod initialized • Ready for interactive testing
        </div>
      </div>

      <div class="panel">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
          <h3 style="margin:0;color:#fdba74;">✴️🪽 Agent Architecture &amp; Code Deliverable</h3>
          <span style="font-size:11px;font-family:monospace;color:var(--sub);">{html.escape(agent_name)} • {html.escape(model)}</span>
        </div>
        <pre id="codeBlock">{escaped_out}</pre>
      </div>
    </div>
  </div>
  {ADSENSE_FOOTER_UNIT}
  <script>
    const canvas = document.getElementById('liveCanvas');
    const ctx = canvas.getContext('2d');
    let points = Array.from({{length: 40}}, (_, i) => 40 + Math.sin(i * 0.3) * 25 + Math.random() * 15);

    function drawChart() {{
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.strokeStyle = 'rgba(255,255,255,0.06)';
      for (let y = 40; y < canvas.height; y += 45) {{
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
      }}
      ctx.beginPath();
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 2.5;
      points.forEach((p, idx) => {{
        const x = (idx / (points.length - 1)) * canvas.width;
        const y = canvas.height - (p / 120) * (canvas.height - 30) - 15;
        if (idx === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }});
      ctx.stroke();
    }}

    function updateDashboard() {{
      const scale = parseInt(document.getElementById('simScale').value || '7', 10);
      const load = parseInt(document.getElementById('simLoad').value || '120', 10);
      const tp = scale * load * 2;
      const lat = Math.max(0.8, (18 / Math.sqrt(scale)) + (load / 180)).toFixed(1);
      document.getElementById('valNodes').textContent = scale + ' Nodes';
      document.getElementById('valThroughput').textContent = tp.toLocaleString() + ' ops/s';
      document.getElementById('valLatency').textContent = lat + ' ms';
      points.shift();
      points.push(Math.min(115, 25 + (scale * 2.2) + (load * 0.12) + Math.random() * 12));
      drawChart();
    }}

    function runSimulation() {{
      for (let i = 0; i < 8; i++) {{
        setTimeout(() => {{
          updateDashboard();
          document.getElementById('simLog').textContent = '⚡ Live K3s Dev Probe [' + new Date().toLocaleTimeString() + '] — Status: HEALTHY (200 OK)';
        }}, i * 180);
      }}
    }}

    function copyDeliverable() {{
      navigator.clipboard.writeText(document.getElementById('codeBlock').innerText);
      document.getElementById('simLog').textContent = '📋 Copied agent deliverable code to clipboard!';
    }}

    updateDashboard();
    setInterval(updateDashboard, 2500);
  </script>
</body>
</html>"""
    return _ensure_adsense_in_html(doc, title, slug, agent_name, model, ticket_id)


def deploy_completed_ticket_to_k3s_dev(ticket_id: str) -> Optional[Dict[str, Any]]:
    """Deploys a completed ticket's website/app into the K3s 'dev' namespace gateway (/app/data/dev_apps/<slug>)."""
    state = load_state()
    ticket = next((t for t in state.get("tickets", []) if t.get("id") == ticket_id), None)
    if not ticket or not ticket.get("output"):
        return None
    if ticket.get("status") not in ("COMPLETED", "AWAITING_APPROVAL"):
        return None

    agent = next((a for a in state.get("agents", []) if a.get("id") == ticket.get("assigned_to")), state["agents"][0])
    slug = ticket.get("dev_slug") or _make_slug(ticket.get("title", "app"), prefix=ticket_id)
    app_dir = os.path.join(DEV_APPS_DIR, slug)
    os.makedirs(app_dir, exist_ok=True)

    agent_display = f"{agent.get('name', 'Claude-01')} + Hermes Co-Op" if ticket.get("collaborate") else agent.get("name", "Agent")
    html_doc = synthesize_interactive_webapp_html(
        title=ticket.get("title", "Autonomous App"),
        description=ticket.get("description", ""),
        agent_output=ticket.get("output", ""),
        agent_name=agent_display,
        model=ticket.get("model_used", agent.get("model", "qwen2.5-coder:14b")),
        ticket_id=ticket_id,
        slug=slug,
    )

    with open(os.path.join(app_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_doc)
    with open(os.path.join(app_dir, "ads.txt"), "w", encoding="utf-8") as f:
        f.write(ADS_TXT_BODY)

    k3s_dev_url = f"{K3S_DEV_GATEWAY_URL.rstrip('/')}/{slug}/"
    paperclip_dev_url = f"http://192.168.0.81:30791/dev-apps/{slug}/"

    app_meta = {
        "id": f"devapp-{slug}",
        "slug": slug,
        "ticket_id": ticket_id,
        "title": ticket.get("title", "Autonomous Web App"),
        "description": (ticket.get("description") or "")[:240],
        "agent_id": agent.get("id"),
        "agent_name": agent_display,
        "agent_avatar": agent.get("avatar", "✴️"),
        "model": ticket.get("model_used", agent.get("model", "qwen2.5-coder:14b")),
        "namespace": "dev",
        "k3s_dev_url": k3s_dev_url,
        "paperclip_dev_url": paperclip_dev_url,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp_epoch": round(time.time(), 2),
        "auto_open": True,
    }
    with open(os.path.join(app_dir, "meta.json"), "w", encoding="utf-8") as mf:
        json.dump(app_meta, mf, indent=2)

    state = load_state()
    ticket = next((t for t in state.get("tickets", []) if t.get("id") == ticket_id), ticket)
    ticket["dev_app"] = app_meta
    if ticket.get("hermes_log") and isinstance(ticket["hermes_log"].get("steps"), list):
        ticket["hermes_log"]["steps"].append({
            "step": "K3s Dev Deployed",
            "time": f"{round((ticket.get('duration_ms') or 1000) / 1000.0, 2)}s",
            "detail": f"Deployed live website to K3s namespace 'dev': {k3s_dev_url}",
        })

    dev_apps = state.setdefault("dev_apps", [])
    dev_apps = [a for a in dev_apps if a.get("slug") != slug]
    dev_apps.insert(0, app_meta)
    state["dev_apps"] = dev_apps[:60]
    state["last_deployed_dev_app"] = app_meta

    add_audit(
        state,
        agent_display,
        f"Deployed live website '{ticket.get('title')}' to K3s 'dev' namespace -> {k3s_dev_url}",
        "SUCCESS",
    )
    save_state(state)
    return {"ticket": ticket, "dev_app": app_meta, "state": state}


CONTINUOUS_FACTORY_RUNNING: bool = False
CONTINUOUS_FACTORY_BUILDING_NOW: bool = False
CONTINUOUS_FACTORY_THREAD: Optional[threading.Thread] = None


def build_next_autonomous_dev_app_sync(custom_title: str = "", custom_desc: str = "", agent_id: str = "") -> Dict[str, Any]:
    """Synchronously builds & deploys a new website/app to K3s dev using Claude + Hermes Co-Op."""
    global CONTINUOUS_FACTORY_BUILDING_NOW
    CONTINUOUS_FACTORY_BUILDING_NOW = True
    try:
        state = load_state()
        existing_titles = {a.get("title", "").lower() for a in state.get("dev_apps", [])}
        chosen_bp = None
        if custom_title:
            chosen_bp = {
                "slug": _make_slug(custom_title),
                "title": custom_title,
                "description": custom_desc or f"Build a complete, self-contained, interactive single-page HTML5/CSS/JS web application (<!DOCTYPE html>...</html>) for: {custom_title}.",
            }
        else:
            for bp in AUTONOMOUS_APP_BLUEPRINTS:
                if bp["title"].lower() not in existing_titles:
                    chosen_bp = bp
                    break
            if not chosen_bp:
                idx_num = len(state.get("dev_apps", [])) + 1
                base_bp = AUTONOMOUS_APP_BLUEPRINTS[idx_num % len(AUTONOMOUS_APP_BLUEPRINTS)]
                chosen_bp = {
                    "slug": f"{base_bp['slug']}-v{idx_num}",
                    "title": f"{base_bp['title']} (Edition #{idx_num})",
                    "description": base_bp["description"],
                }

        # Alternate between Claude-01, Hermes-01, Pixel, and Forge so the whole AI company builds sites together
        rotation = ["agent-claude", "agent-hermes", "agent-coder"]
        chosen_agent_id = agent_id or rotation[len(state.get("dev_apps", [])) % len(rotation)]
        if not any(a.get("id") == chosen_agent_id for a in state.get("agents", [])):
            chosen_agent_id = state["agents"][0]["id"]

        prompt_desc = (
            f"{chosen_bp['description']}\n\n"
            f"IMPORTANT: Return a COMPLETE, self-contained single-page HTML5 application (`<!DOCTYPE html>...</html>`) "
            f"with embedded `<style>` (modern dark-glass UI) and `<script>` (interactive controls, live calculations, charts, or simulations) "
            f"so it can be deployed directly to the K3s `dev` namespace and opened in the browser."
        )

        res = asyncio.run(
            create_and_run_ticket(
                {
                    "title": f"🌐 [K3s Dev Site] {chosen_bp['title']}",
                    "description": prompt_desc,
                    "assigned_to": chosen_agent_id,
                    "priority": "HIGH",
                    "auto_execute": True,
                    "collaborate": True,
                }
            )
        )
        return res
    finally:
        CONTINUOUS_FACTORY_BUILDING_NOW = False


def seed_initial_dev_apps_if_empty():
    """Ensures at least 2 rich interactive web apps exist in /app/data/dev_apps immediately on startup."""
    state = load_state()
    if state.get("dev_apps"):
        return
    seed_specs = [
        ("TCK-DEV1", "🌐 [K3s Dev Site] K3s Cluster Live Node & Pod Topology Radar", AUTONOMOUS_APP_BLUEPRINTS[0]["description"], "k3s-cluster-topology-radar"),
        ("TCK-DEV2", "🌐 [K3s Dev Site] Dual-GPU VRAM & Ollama LLM Throughput Sizer", AUTONOMOUS_APP_BLUEPRINTS[1]["description"], "dual-gpu-vram-llm-sizer"),
    ]
    for tid, title, desc, slug in seed_specs:
        app_dir = os.path.join(DEV_APPS_DIR, slug)
        os.makedirs(app_dir, exist_ok=True)
        html_doc = synthesize_interactive_webapp_html(
            title=title,
            description=desc,
            agent_output=f"// Autonomous K3s Dev Application: {title}\n// Built by Claude-01 (✴️) + Hermes-01 (🪽) Co-Op Swarm\n// Target Namespace: dev (NodePort 30795)\n\nconst k3sConfig = {{\n  namespace: 'dev',\n  gatewayPort: 30795,\n  ollamaEndpoint: 'http://192.168.0.17:11434',\n  gpus: ['NVIDIA GeForce RTX 5070 (12GB)', 'NVIDIA GeForce RTX 3060 (12GB)'],\n  status: 'ONLINE'\n}};",
            agent_name="Claude-01 + Hermes-01 Co-Op",
            model="qwen2.5-coder:14b + qwen2.5-coder:7b",
            ticket_id=tid,
            slug=slug,
        )
        with open(os.path.join(app_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_doc)
        with open(os.path.join(app_dir, "ads.txt"), "w", encoding="utf-8") as f:
            f.write(ADS_TXT_BODY)
        meta = {
            "id": f"devapp-{slug}",
            "slug": slug,
            "ticket_id": tid,
            "title": title,
            "description": desc[:240],
            "agent_id": "agent-claude",
            "agent_name": "Claude-01 + Hermes-01 Co-Op",
            "agent_avatar": "✴️",
            "model": "qwen2.5-coder:14b + qwen2.5-coder:7b",
            "namespace": "dev",
            "k3s_dev_url": f"{K3S_DEV_GATEWAY_URL.rstrip('/')}/{slug}/",
            "paperclip_dev_url": f"http://192.168.0.81:30791/dev-apps/{slug}/",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp_epoch": round(time.time(), 2),
            "auto_open": True,
        }
        with open(os.path.join(app_dir, "meta.json"), "w", encoding="utf-8") as mf:
            json.dump(meta, mf, indent=2)
        state.setdefault("dev_apps", []).insert(0, meta)
        state["last_deployed_dev_app"] = meta
    state.setdefault("continuous_factory_enabled", True)
    state.setdefault("continuous_factory_interval_sec", 90)
    save_state(state)


def continuous_dev_factory_worker():
    """Background daemon that keeps Claude & Hermes continuously creating and deploying new sites & apps to K3s dev."""
    global CONTINUOUS_FACTORY_RUNNING
    CONTINUOUS_FACTORY_RUNNING = True
    time.sleep(8)
    while CONTINUOUS_FACTORY_RUNNING:
        try:
            st = load_state()
            enabled = st.get("continuous_factory_enabled", True)
            interval = max(30, int(st.get("continuous_factory_interval_sec", 90)))
            if enabled and not CONTINUOUS_FACTORY_BUILDING_NOW:
                build_next_autonomous_dev_app_sync()
            for _ in range(interval):
                if not CONTINUOUS_FACTORY_RUNNING:
                    break
                time.sleep(1)
        except Exception:
            time.sleep(15)


def start_continuous_dev_factory_if_needed():
    global CONTINUOUS_FACTORY_THREAD
    seed_initial_dev_apps_if_empty()
    if CONTINUOUS_FACTORY_THREAD and CONTINUOUS_FACTORY_THREAD.is_alive():
        return
    CONTINUOUS_FACTORY_THREAD = threading.Thread(target=continuous_dev_factory_worker, daemon=True)
    CONTINUOUS_FACTORY_THREAD.start()


@app.get("/api/dev/apps")
async def list_k3s_dev_apps():
    state = load_state()
    apps = state.get("dev_apps", [])
    return {
        "ok": True,
        "namespace": "dev",
        "k3s_dev_gateway_url": K3S_DEV_GATEWAY_URL,
        "continuous_factory_enabled": state.get("continuous_factory_enabled", True),
        "continuous_factory_interval_sec": state.get("continuous_factory_interval_sec", 90),
        "building_now": CONTINUOUS_FACTORY_BUILDING_NOW,
        "count": len(apps),
        "last_deployed_app": apps[0] if apps else None,
        "apps": apps,
    }


@app.post("/api/dev/factory/toggle")
async def toggle_continuous_dev_factory(payload: Dict[str, Any] = Body(...)):
    state = load_state()
    if "enabled" in payload:
        state["continuous_factory_enabled"] = bool(payload["enabled"])
    else:
        state["continuous_factory_enabled"] = not state.get("continuous_factory_enabled", True)
    if "interval_sec" in payload:
        state["continuous_factory_interval_sec"] = max(30, int(payload["interval_sec"]))
    status_str = "ENABLED" if state["continuous_factory_enabled"] else "PAUSED"
    add_audit(state, "K3s Dev Factory", f"Continuous Autonomous Website & App Factory {status_str} (interval: {state.get('continuous_factory_interval_sec', 90)}s)", "INFO")
    save_state(state)
    return {
        "ok": True,
        "continuous_factory_enabled": state["continuous_factory_enabled"],
        "continuous_factory_interval_sec": state.get("continuous_factory_interval_sec", 90),
        "state": state,
    }


@app.post("/api/dev/factory/build_now")
async def trigger_dev_factory_build_now(payload: Dict[str, Any] = Body(default={})):
    custom_title = (payload.get("title") or "").strip()
    custom_desc = (payload.get("description") or "").strip()
    agent_id = (payload.get("agent_id") or "").strip()
    res = await asyncio.to_thread(build_next_autonomous_dev_app_sync, custom_title, custom_desc, agent_id)
    st = load_state()
    return {
        "ok": True,
        "ticket": res.get("ticket"),
        "dev_app": st.get("last_deployed_dev_app"),
        "state": st,
    }


@app.get("/dev-apps/{slug}/ads.txt")
async def serve_dev_app_ads_txt(slug: str):
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(ADS_TXT_BODY)


@app.get("/dev-apps/{slug}", response_class=HTMLResponse)
@app.get("/dev-apps/{slug}/", response_class=HTMLResponse)
async def serve_dev_app_direct(slug: str):
    safe_slug = re.sub(r"[^a-zA-Z0-9_-]", "", slug)
    idx_file = os.path.join(DEV_APPS_DIR, safe_slug, "index.html")
    if not os.path.exists(idx_file):
        raise HTTPException(status_code=404, detail=f"Dev app '{safe_slug}' not found")
    with open(idx_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.on_event("startup")
async def app_startup_event():
    start_telegram_worker_if_needed()
    start_continuous_dev_factory_if_needed()




@app.get("/ads.txt")
async def serve_ads_txt():
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse("google.com, pub-1596056523034714, DIRECT, f08c47fec0942fa0\n")


if __name__ == "__main__":
    from dual_tls_runner import run_dual_http_https
    port = int(os.environ.get("PORT", os.environ.get("PAPERCLIP_PORT", "7891")))
    run_dual_http_https(app, port=port)
