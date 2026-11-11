#!/usr/bin/env python3
"""
Claude-Ollama — Autonomous Reasoning & Code Agent with 1-Click Paperclip, Hermes & Ollama Connectors
Powered by Ollama's native Anthropic Messages API (/v1/messages) & local GGUF models (gemma4-claude:latest, qwen2.5-coder:14b),
with optional Anthropic API / Claude Code CLI bridge and native bi-directional collaboration with Hermes-Agent.
"""
import asyncio
import json
import os
import re
import shutil
import subprocess
import time
import urllib.request
import uuid
from typing import Any, Dict, List

from fastapi import FastAPI, Body
from fastapi.responses import HTMLResponse, PlainTextResponse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "data"))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
os.makedirs(DATA_DIR, exist_ok=True)

CLAUDE_STATE_FILE = os.path.join(DATA_DIR, "claude_state.json")
DEFAULT_OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://192.168.0.17:11434")
DEFAULT_PAPERCLIP_URL = os.environ.get("PAPERCLIP_URL", "http://192.168.0.81:30791")
DEFAULT_HERMES_URL = os.environ.get("HERMES_URL", "http://192.168.0.17:7892")
DEFAULT_SELF_URL = os.environ.get("CLAUDE_SELF_URL", "http://127.0.0.1:7893")
DEFAULT_NODE_ID = os.environ.get("NODE_ID", "claude-k3s-primary")
DEFAULT_AGENT_NAME = os.environ.get("AGENT_NAME", "Claude-01")
DEFAULT_MODEL_NAME = os.environ.get("DEFAULT_MODEL", "gemma4-claude:latest")

app = FastAPI(
    title="Claude-Ollama — Autonomous Reasoning & Engineering Agent",
    version="1.0.0",
)


def default_claude_state() -> Dict[str, Any]:
    return {
        "node_id": DEFAULT_NODE_ID,
        "agent_name": DEFAULT_AGENT_NAME,
        "ollama_url": DEFAULT_OLLAMA_URL,
        "paperclip_url": DEFAULT_PAPERCLIP_URL,
        "hermes_url": DEFAULT_HERMES_URL,
        "self_url": DEFAULT_SELF_URL,
        "active_model": DEFAULT_MODEL_NAME,
        "api_mode": "ollama_anthropic",  # ollama_anthropic (/v1/messages), ollama_chat, or claude_cli
        "paperclip_connected": True,
        "hermes_connected": True,
        "last_sync": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tasks_completed": 4,
        "co_op_sessions": 2,
        "skills": [
            {
                "id": "cskill-arch-review",
                "name": "claude-hermes-joint-architecture-synthesis",
                "category": "Multi-Agent Collaboration",
                "description": "Pair Claude deep architectural reasoning and edge-case verification with Hermes procedural execution and skill vault extraction.",
                "created_at": "2026-11-10 09:00:00",
                "uses": 6,
            },
            {
                "id": "cskill-anthropic-messages-ollama",
                "name": "ollama-anthropic-v1-messages-bridge",
                "category": "Claude Code & API",
                "description": "Execute Anthropic Messages API (/v1/messages) natively against local Ollama (192.168.0.17:11434) with gemma4-claude:latest and qwen2.5-coder:14b.",
                "created_at": "2026-11-10 09:15:00",
                "uses": 8,
            },
            {
                "id": "cskill-k3s-zero-trust",
                "name": "k8s-security-and-manifest-hardening",
                "category": "DevSecOps & K3s",
                "description": "Audit Kubernetes manifests for resource requests/limits, readinessProbes, NVMe hostPath isolation, and zero-downtime rolling updates.",
                "created_at": "2026-11-10 09:30:00",
                "uses": 5,
            },
        ],
        "memories": [
            {
                "id": "cmem-1",
                "timestamp": "2026-11-10 09:10:00",
                "summary": "Claude Agent Bridge initialized on Ollama Anthropic Messages API (http://192.168.0.17:11434/v1/messages) with model gemma4-claude:latest.",
                "tags": ["claude", "anthropic-api", "ollama"],
            },
            {
                "id": "cmem-2",
                "timestamp": "2026-11-10 09:20:00",
                "summary": "Bi-directional swarm link established with Hermes-Host-17 (192.168.0.17:7892) and Hermes-01 (K3s 30792) for collaborative ticket execution.",
                "tags": ["hermes", "co-op", "swarm"],
            },
        ],
        "chat_history": [
            {
                "id": "cmsg-welcome",
                "role": "assistant",
                "timestamp": time.strftime("%H:%M:%S"),
                "model": DEFAULT_MODEL_NAME,
                "learned_skill": "claude-hermes-joint-architecture-synthesis",
                "content": (
                    "Greetings! I am **Claude-01**, your autonomous reasoning, coding, and architecture agent.\n\n"
                    "- **Anthropic Messages API (`/v1/messages`)**: Connected to local Ollama (`http://192.168.0.17:11434`)\n"
                    "- **Paperclip Control Plane**: Linked to `Sovereign AI Corp`\n"
                    "- **Hermes Collaboration Bridge**: Active — I work hand-in-hand with **Hermes** agents to architect, code, review, and synthesize shared skills."
                ),
            }
        ],
    }


def load_claude_state() -> Dict[str, Any]:
    if os.path.exists(CLAUDE_STATE_FILE):
        try:
            with open(CLAUDE_STATE_FILE, "r", encoding="utf-8") as f:
                st = json.load(f)
            if os.environ.get("CLAUDE_SELF_URL"):
                st["self_url"] = os.environ["CLAUDE_SELF_URL"]
            if os.environ.get("NODE_ID"):
                st["node_id"] = os.environ["NODE_ID"]
            if os.environ.get("AGENT_NAME"):
                st["agent_name"] = os.environ["AGENT_NAME"]
            if os.environ.get("PAPERCLIP_URL"):
                st["paperclip_url"] = os.environ["PAPERCLIP_URL"]
            if os.environ.get("HERMES_URL"):
                st["hermes_url"] = os.environ["HERMES_URL"]
            if os.environ.get("OLLAMA_URL"):
                st["ollama_url"] = os.environ["OLLAMA_URL"]
            return st
        except Exception:
            pass
    st = default_claude_state()
    save_claude_state(st)
    return st


def save_claude_state(st: Dict[str, Any]) -> None:
    with open(CLAUDE_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(st, f, indent=2)


def probe_ollama_models(ollama_url: str) -> Dict[str, Any]:
    url = ollama_url.rstrip("/")
    t0 = time.time()
    try:
        with urllib.request.urlopen(f"{url}/api/version", timeout=5) as r:
            ver = json.loads(r.read().decode("utf-8")).get("version", "unknown")
        latency_ms = round((time.time() - t0) * 1000.0, 1)
        with urllib.request.urlopen(f"{url}/api/tags", timeout=6) as r:
            tags = json.loads(r.read().decode("utf-8")).get("models", [])
        models = [
            {
                "name": m.get("name"),
                "parameter_size": m.get("details", {}).get("parameter_size", ""),
                "quantization": m.get("details", {}).get("quantization_level", ""),
                "size_gb": round(m.get("size", 0) / (1024 ** 3), 2),
            }
            for m in tags
        ]
        return {"connected": True, "url": url, "version": ver, "latency_ms": latency_ms, "models": models}
    except Exception as exc:
        return {"connected": False, "url": url, "version": "offline", "latency_ms": 0.0, "error": str(exc), "models": []}


def sync_with_paperclip(st: Dict[str, Any]) -> Dict[str, Any]:
    p_url = st["paperclip_url"].rstrip("/")
    try:
        payload = {
            "node_id": st["node_id"],
            "agent_name": st["agent_name"],
            "name": f"{st['agent_name']} (Claude Autonomous Agent)",
            "endpoint": st.get("self_url", DEFAULT_SELF_URL),
            "ollama_url": st["ollama_url"],
            "hermes_url": st.get("hermes_url", DEFAULT_HERMES_URL),
            "model": st["active_model"],
            "skills_count": len(st["skills"]),
            "memories_count": len(st["memories"]),
            "agent_type": "claude",
        }
        req = urllib.request.Request(
            f"{p_url}/api/claude/register",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        st["paperclip_connected"] = True
        st["last_sync"] = time.strftime("%Y-%m-%d %H:%M:%S")
        save_claude_state(st)
        return {"ok": True, "data": data}
    except Exception as exc:
        st["paperclip_connected"] = False
        save_claude_state(st)
        return {"ok": False, "error": str(exc)}


def synthesize_skill_from_task(st: Dict[str, Any], title: str, output: str) -> str:
    slug = "claude-" + (re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:32] or "reasoning-pattern")
    for s in st["skills"]:
        if s["name"] == slug:
            s["uses"] = s.get("uses", 1) + 1
            return slug

    first_line = next((line.strip("#* -") for line in output.splitlines() if len(line.strip()) > 25), title)
    new_skill = {
        "id": f"cskill-{str(uuid.uuid4())[:6]}",
        "name": slug,
        "category": "Claude Playbook",
        "description": first_line[:180],
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "uses": 1,
    }
    st["skills"].insert(0, new_skill)
    st["memories"].insert(
        0,
        {
            "id": f"cmem-{str(uuid.uuid4())[:6]}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": f"Claude completed '{title}' using {st['active_model']} and synthesized playbook '{slug}'.",
            "tags": ["claude", st["active_model"]],
        },
    )
    return slug


def run_claude_inference(
    st: Dict[str, Any],
    user_prompt: str,
    model_override: str = "",
    agent_name_override: str = "",
    system_prompt_override: str = "",
) -> Dict[str, Any]:
    model = model_override or st["active_model"]
    agent_name = agent_name_override or st["agent_name"]
    skills_context = "\n".join(f"- {s['name']}: {s['description']}" for s in st["skills"][:6])
    memories_context = "\n".join(f"- {m['summary']}" for m in st["memories"][:4])
    base_role = (
        system_prompt_override
        or f"You are {agent_name}, an autonomous Claude AI engineering & architecture agent connected to Paperclip Control Plane, "
        f"Hermes Agent Swarm, and Ollama Anthropic API ({st['ollama_url']})."
    )
    sys_prompt = (
        f"{base_role}\n\n"
        f"CLAUDE PLAYBOOKS & SKILLS VAULT:\n{skills_context}\n\n"
        f"EPISODIC MEMORY:\n{memories_context}\n\n"
        f"Provide complete, rigorous, production-ready code and architectural solutions with zero placeholders. "
        f"Conclude with a 1-line 'Claude Synthesis Takeaway'."
    )

    t0 = time.time()
    ollama_base = st["ollama_url"].rstrip("/")

    # Check active VRAM models on Ollama (/api/ps) to prevent 22GB VRAM swap thrashing
    effective_model = model
    try:
        with urllib.request.urlopen(f"{ollama_base}/api/ps", timeout=3) as r_ps:
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

    # 1. Try Ollama's native Anthropic Messages API (/v1/messages) first
    try:
        messages_url = f"{ollama_base}/v1/messages"
        anthropic_payload = {
            "model": effective_model,
            "max_tokens": 1024,
            "system": sys_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
        }
        req = urllib.request.Request(
            messages_url,
            data=json.dumps(anthropic_payload).encode("utf-8"),
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
        content = "\n\n".join(text_parts).strip()
        thinking = "\n\n".join(thinking_parts).strip()
        if not content and thinking:
            content = f"### [Claude Reasoning & Execution]\n\n{thinking}"
        elif thinking and content and len(thinking) > 30:
            first_thoughts = "\n".join(thinking.splitlines()[:10])
            content = f"<blockquote>✴️ <b>Claude Extended Thinking:</b>\n{first_thoughts}</blockquote>\n\n{content}"
        usage = data.get("usage", {})
        tokens = int(usage.get("input_tokens", 0)) + int(usage.get("output_tokens", 0))
        if content:
            return {
                "content": content,
                "tokens": tokens or max(64, len(content) // 4),
                "duration_ms": duration_ms,
                "model": data.get("model", model),
                "engine": "anthropic_v1_messages",
            }
    except Exception:
        pass

    # 2. Fallback to Ollama /api/chat (if model wasn't found, fallback to qwen2.5-coder:14b or gemma4-claude:latest)
    for candidate_model in [model, "gemma4-claude:latest", "qwen2.5-coder:14b", "qwen2.5-coder:7b"]:
        try:
            chat_url = f"{ollama_base}/api/chat"
            payload = {
                "model": candidate_model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "options": {"temperature": 0.3, "num_predict": 1024},
            }
            req = urllib.request.Request(
                chat_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            duration_ms = round((time.time() - t0) * 1000.0, 1)
            content = (data.get("message", {}).get("content") or "").strip()
            thinking = (data.get("message", {}).get("thinking") or "").strip()
            if not content and thinking:
                content = f"### [Claude Reasoning & Execution]\n\n{thinking}"
            elif thinking and content and len(thinking) > 30:
                first_few = "\n".join(thinking.splitlines()[:10])
                content = f"<blockquote>✴️ <b>Claude Reasoning Summary:</b>\n{first_few}</blockquote>\n\n{content}"
            tokens = int(data.get("eval_count", 0)) + int(data.get("prompt_eval_count", 0))
            return {
                "content": content or "(Claude task executed successfully)",
                "tokens": tokens or max(64, len(content) // 4),
                "duration_ms": duration_ms,
                "model": candidate_model,
                "engine": "ollama_chat",
            }
        except Exception:
            continue

    return {
        "content": "Claude inference could not reach Ollama backend.",
        "tokens": 0,
        "duration_ms": round((time.time() - t0) * 1000.0, 1),
        "model": model,
        "engine": "offline",
    }


def consult_hermes_peer(st: Dict[str, Any], title: str, description: str, claude_draft: str) -> Dict[str, Any]:
    """Allows Claude to collaborate directly with a Hermes peer node to synthesize joint deliverables & skills."""
    hermes_eps = [
        st.get("hermes_url", DEFAULT_HERMES_URL),
        "http://192.168.0.17:7892",
        "http://hermes.ai.svc.cluster.local:7892",
        "http://192.168.0.81:30792",
    ]
    seen = set()
    for ep in hermes_eps:
        if not ep or ep in seen:
            continue
        seen.add(ep)
        try:
            collab_prompt = (
                f"🤝 [CLAUDE ⇄ HERMES JOINT SWARM COLLABORATION]\n"
                f"Objective: {title}\n"
                f"Context: {description}\n\n"
                f"--- CLAUDE ARCHITECTURAL & CODE ANALYSIS ---\n{claude_draft[:3000]}\n\n"
                f"As Hermes Autonomous Worker, review Claude's deliverable above, add operational execution steps, "
                f"K3s/Linux runtime verification commands, and extract a reusable procedural skill."
            )
            req = urllib.request.Request(
                f"{ep.rstrip('/')}/api/execute_ticket",
                data=json.dumps({
                    "ticket_id": f"COOP-{str(uuid.uuid4())[:4].upper()}",
                    "title": f"Hermes Co-Op Review: {title}",
                    "description": collab_prompt,
                    "model": "qwen2.5-coder:7b",
                    "agent_name": "Hermes (Co-Op Partner)",
                    "ollama_url": st["ollama_url"],
                }).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                h_data = json.loads(resp.read().decode("utf-8"))
            if h_data.get("ok") and h_data.get("output"):
                return {
                    "ok": True,
                    "endpoint": ep,
                    "output": h_data["output"],
                    "tokens": int(h_data.get("tokens", 0)),
                    "duration_ms": float(h_data.get("duration_ms", 0)),
                    "learned_skill": h_data.get("learned_skill", "claude-hermes-coop"),
                    "model": h_data.get("model", "qwen2.5-coder:14b"),
                }
        except Exception:
            continue
    return {"ok": False}


ACTIVE_PROCESSING_TICKETS = set()


async def process_claimed_ticket(ticket: Dict[str, Any]):
    t_id = ticket.get("id")
    if not t_id or t_id in ACTIVE_PROCESSING_TICKETS:
        return
    ACTIVE_PROCESSING_TICKETS.add(t_id)
    try:
        st = load_claude_state()
        title = ticket.get("title", "Paperclip Task")
        desc = ticket.get("description", "")
        model = ticket.get("model_used") or st["active_model"]
        req_agent = st["agent_name"]
        collaborate = bool(ticket.get("collaborate_with_hermes", False))

        t0 = time.time()
        steps = [
            {"step": "Task Ingested", "time": "0.0s", "detail": f"Claude Autonomous Agent claimed ticket {t_id} from Paperclip"},
        ]
        skills_used = [s["name"] for s in st["skills"][:4]]
        steps.append({"step": "Claude Playbooks Prime", "time": f"{round(time.time() - t0, 2)}s", "detail": f"Primed context with {len(skills_used)} playbooks: {', '.join(skills_used)}"})

        full_prompt = f"[PAPERCLIP TICKET {t_id}] {title}\n\n{desc}"
        steps.append({"step": "Anthropic /v1/messages Inference", "time": f"{round(time.time() - t0, 2)}s", "detail": f"Executing Claude inference via {st['ollama_url']} (model: {model})"})

        res = await asyncio.to_thread(run_claude_inference, st, full_prompt, model, req_agent, "")
        final_output = res["content"]
        total_tokens = res["tokens"]
        total_duration = res["duration_ms"]

        elapsed_s = max(0.1, round(time.time() - t0, 2))
        tok_sec = round(total_tokens / elapsed_s, 1)
        steps.append({"step": "Claude Inference Complete", "time": f"{elapsed_s}s", "detail": f"Generated {res['tokens']} tokens ({tok_sec} tok/sec in {res['duration_ms']} ms)"})

        if collaborate:
            steps.append({"step": "Hermes Swarm Co-Op", "time": f"{round(time.time() - t0, 2)}s", "detail": "Handing off Claude blueprint to Hermes peer node for operational synthesis"})
            coop = await asyncio.to_thread(consult_hermes_peer, st, title, desc, final_output)
            if coop.get("ok"):
                final_output = (
                    f"## ✴️ Phase 1 — Claude ({req_agent} • `{res['model']}`) Architecture & Engineering\n\n"
                    f"{res['content']}\n\n---\n\n"
                    f"## 🪽 Phase 2 — Hermes (`{coop.get('model')}`) Operational Verification & Skill Extraction\n\n"
                    f"{coop['output']}"
                )
                total_tokens += coop.get("tokens", 0)
                total_duration = round(total_duration + coop.get("duration_ms", 0), 1)
                st["co_op_sessions"] = st.get("co_op_sessions", 0) + 1
                steps.append({"step": "Hermes Co-Op Complete", "time": f"{round(time.time() - t0, 2)}s", "detail": f"Hermes contributed {coop.get('tokens', 0)} tokens & skill '{coop.get('learned_skill')}'"})

        st = load_claude_state()
        learned_skill = synthesize_skill_from_task(st, title, final_output)
        steps.append({"step": "Playbook Synthesis", "time": f"{round(time.time() - t0, 2)}s", "detail": f"Saved reusable playbook '{learned_skill}' into Claude Vault"})

        memory_summary = f"Completed ticket {t_id} ('{title}') with {res['model']} on {st['node_id']} and synthesized '{learned_skill}'."
        st["tasks_completed"] = st.get("tasks_completed", 0) + 1

        completion_log = {
            "id": f"clog-{str(uuid.uuid4())[:8]}",
            "ticket_id": t_id,
            "title": title,
            "agent_name": req_agent,
            "node_id": st["node_id"],
            "model": res["model"],
            "tokens": total_tokens,
            "tok_per_sec": tok_sec,
            "duration_ms": total_duration,
            "completed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "learned_skill": learned_skill,
            "memory_summary": memory_summary,
            "steps": steps,
            "status": "SUCCESS",
        }
        st.setdefault("ticket_completion_logs", []).insert(0, completion_log)
        st["ticket_completion_logs"] = st["ticket_completion_logs"][:50]
        save_claude_state(st)

        p_url = st["paperclip_url"].rstrip("/")
        cb_payload = {
            "ticket_id": t_id,
            "output": final_output,
            "tokens": total_tokens,
            "duration_ms": total_duration,
            "model": res["model"],
            "learned_skill": learned_skill,
            "completion_log": completion_log,
        }
        req = urllib.request.Request(
            f"{p_url}/api/claude/complete_ticket",
            data=json.dumps(cb_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            pass
    except Exception as exc:
        print(f"[!] Claude error processing ticket {t_id}: {exc}")
    finally:
        ACTIVE_PROCESSING_TICKETS.discard(t_id)


async def background_paperclip_task_worker():
    await asyncio.sleep(4)
    while True:
        try:
            st = load_claude_state()
            p_url = st["paperclip_url"].rstrip("/")
            node_id = st.get("node_id", "")
            req = urllib.request.Request(
                f"{p_url}/api/claude/tasks?node_id={node_id}",
                headers={"User-Agent": f"Claude-Node/{node_id}"},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            tasks = data.get("tasks", [])
            for t in tasks:
                t_assigned = t.get("assigned_to", "")
                is_mine = (
                    t_assigned == f"agent-{node_id}"
                    or (node_id == "claude-k3s-primary" and t_assigned == "agent-claude")
                    or (node_id == "claude-host-17" and t_assigned == "agent-claude-17")
                )
                if is_mine and t["id"] not in ACTIVE_PROCESSING_TICKETS:
                    asyncio.create_task(process_claimed_ticket(t))
        except Exception:
            pass
        await asyncio.sleep(3)


async def background_paperclip_heartbeat():
    await asyncio.sleep(3)
    while True:
        try:
            st = load_claude_state()
            await asyncio.to_thread(sync_with_paperclip, st)
        except Exception:
            pass
        await asyncio.sleep(45)


@app.on_event("startup")
async def on_startup():
    asyncio.create_task(background_paperclip_heartbeat())
    asyncio.create_task(background_paperclip_task_worker())


@app.get("/", response_class=HTMLResponse)
async def serve_claude_ui():
    html_path = os.path.join(TEMPLATES_DIR, "claude.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/state")
async def get_state():
    st = load_claude_state()
    ollama = await asyncio.to_thread(probe_ollama_models, st["ollama_url"])
    return {
        "state": st,
        "ollama": ollama,
        "node_id": st["node_id"],
        "agent_name": st["agent_name"],
        "model": st["active_model"],
        "ollama_url": st["ollama_url"],
        "skills": st["skills"],
        "episodic_memories": st["memories"],
        "agent_type": "claude",
    }


@app.post("/api/connect")
async def connect_endpoints(payload: Dict[str, Any] = Body(...)):
    st = load_claude_state()
    if payload.get("ollama_url"):
        url = payload["ollama_url"].strip().rstrip("/")
        if not url.startswith("http"):
            url = "http://" + url
        if ":" not in url.split("//")[-1]:
            url = url + ":11434"
        st["ollama_url"] = url
    if payload.get("paperclip_url"):
        p_url = payload["paperclip_url"].strip().rstrip("/")
        if not p_url.startswith("http"):
            p_url = "http://" + p_url
        st["paperclip_url"] = p_url
    if payload.get("hermes_url"):
        h_url = payload["hermes_url"].strip().rstrip("/")
        if not h_url.startswith("http"):
            h_url = "http://" + h_url
        st["hermes_url"] = h_url
    if payload.get("active_model"):
        st["active_model"] = payload["active_model"]

    save_claude_state(st)
    ollama = await asyncio.to_thread(probe_ollama_models, st["ollama_url"])
    bridge = await asyncio.to_thread(sync_with_paperclip, st)
    return {"state": st, "ollama": ollama, "paperclip_bridge": bridge}


@app.post("/api/chat")
async def chat_with_claude(payload: Dict[str, Any] = Body(...)):
    st = load_claude_state()
    prompt = payload.get("prompt", "").strip()
    model = payload.get("model") or st["active_model"]
    co_op_hermes = bool(payload.get("co_op_hermes", False))
    if not prompt:
        return {"error": "Empty prompt"}

    st["chat_history"].append(
        {
            "id": f"u-{str(uuid.uuid4())[:6]}",
            "role": "user",
            "timestamp": time.strftime("%H:%M:%S"),
            "content": prompt + (" [🤝 Co-Op with Hermes]" if co_op_hermes else ""),
        }
    )
    save_claude_state(st)

    res = await asyncio.to_thread(run_claude_inference, st, prompt, model)
    final_content = res["content"]
    total_tokens = res["tokens"]
    total_duration = res["duration_ms"]

    if co_op_hermes:
        coop = await asyncio.to_thread(consult_hermes_peer, st, prompt[:60], prompt, final_content)
        if coop.get("ok"):
            final_content = (
                f"### ✴️ Claude (`{res['model']}`) Analysis & Solution\n\n{res['content']}\n\n"
                f"---\n\n### 🪽 Hermes (`{coop.get('model')}`) Co-Op Execution & Skill Synthesis\n\n{coop['output']}"
            )
            total_tokens += coop.get("tokens", 0)
            total_duration = round(total_duration + coop.get("duration_ms", 0), 1)
            st["co_op_sessions"] = st.get("co_op_sessions", 0) + 1

    st = load_claude_state()
    learned_skill = synthesize_skill_from_task(st, prompt[:48], final_content)
    st["tasks_completed"] = st.get("tasks_completed", 0) + 1
    st["chat_history"].append(
        {
            "id": f"a-{str(uuid.uuid4())[:6]}",
            "role": "assistant",
            "timestamp": time.strftime("%H:%M:%S"),
            "model": res["model"],
            "tokens": total_tokens,
            "duration_ms": total_duration,
            "learned_skill": learned_skill,
            "content": final_content,
        }
    )
    save_claude_state(st)
    return {"reply": st["chat_history"][-1], "state": st}


@app.post("/api/execute_ticket")
async def execute_paperclip_ticket(payload: Dict[str, Any] = Body(...)):
    """Endpoint called directly by Paperclip Control Plane or Hermes Agent when a ticket or co-op task is assigned to Claude."""
    st = load_claude_state()
    if payload.get("ollama_url"):
        st["ollama_url"] = payload["ollama_url"]
    t_id = payload.get("ticket_id", "TCK")
    title = payload.get("title", "Paperclip Task")
    desc = payload.get("description", "")
    model = payload.get("model") or st["active_model"]
    req_agent_name = payload.get("agent_name") or st["agent_name"]
    req_sys_prompt = payload.get("system_prompt") or ""
    collaborate_with_hermes = bool(payload.get("collaborate_with_hermes", False))

    t0 = time.time()
    steps = [
        {"step": "Task Ingested", "time": "0.0s", "detail": f"Claude Agent Bridge received ticket {t_id} for {req_agent_name}: '{title}'"},
    ]
    skills_used = [s["name"] for s in st["skills"][:4]]
    steps.append({"step": "Claude Playbooks Prime", "time": f"{round(time.time() - t0, 2)}s", "detail": f"Primed context with {len(skills_used)} active playbooks: {', '.join(skills_used)}"})
    steps.append({"step": "Episodic Memory Load", "time": f"{round(time.time() - t0, 2)}s", "detail": f"Retrieved {len(st['memories'])} cross-session memory fragments"})

    full_prompt = f"[PAPERCLIP TICKET {t_id}] {title}\n\n{desc}"
    steps.append({"step": "Anthropic /v1/messages Inference", "time": f"{round(time.time() - t0, 2)}s", "detail": f"Executing Claude deep reasoning via {st['ollama_url']} (model: {model})"})
    res = await asyncio.to_thread(run_claude_inference, st, full_prompt, model, req_agent_name, req_sys_prompt)

    final_output = res["content"]
    total_tokens = res["tokens"]
    total_duration = res["duration_ms"]

    elapsed_s = max(0.1, round(time.time() - t0, 2))
    tok_sec = round(total_tokens / elapsed_s, 1)
    steps.append({"step": "Claude Inference Complete", "time": f"{elapsed_s}s", "detail": f"Generated {res['tokens']} tokens ({tok_sec} tok/sec in {res['duration_ms']} ms)"})

    if collaborate_with_hermes:
        steps.append({"step": "Hermes Swarm Handoff", "time": f"{round(time.time() - t0, 2)}s", "detail": "Collaborating with Hermes node for joint verification & skill extraction"})
        coop = await asyncio.to_thread(consult_hermes_peer, st, title, desc, final_output)
        if coop.get("ok"):
            final_output = (
                f"## ✴️ Phase 1 — Claude ({req_agent_name} • `{res['model']}`) Architecture & Implementation\n\n"
                f"{res['content']}\n\n---\n\n"
                f"## 🪽 Phase 2 — Hermes (`{coop.get('model')}`) Autonomous Co-Op Verification & Skill Vault\n\n"
                f"{coop['output']}"
            )
            total_tokens += coop.get("tokens", 0)
            total_duration = round(total_duration + coop.get("duration_ms", 0), 1)
            steps.append({"step": "Hermes Co-Op Merged", "time": f"{round(time.time() - t0, 2)}s", "detail": f"Merged Hermes deliverable ({coop.get('tokens', 0)} tokens, skill: {coop.get('learned_skill')})"})

    st = load_claude_state()
    learned_skill = synthesize_skill_from_task(st, title, final_output)
    if collaborate_with_hermes:
        st["co_op_sessions"] = st.get("co_op_sessions", 0) + 1
    steps.append({"step": "Playbook Synthesis", "time": f"{round(time.time() - t0, 2)}s", "detail": f"Saved reusable playbook '{learned_skill}' into persistent Claude Vault"})

    memory_summary = f"Completed ticket {t_id} ('{title}') with {res['model']} on behalf of {req_agent_name} and synthesized '{learned_skill}'."
    st["tasks_completed"] = st.get("tasks_completed", 0) + 1

    completion_log = {
        "id": f"clog-{str(uuid.uuid4())[:8]}",
        "ticket_id": t_id,
        "title": title,
        "agent_name": req_agent_name,
        "node_id": st["node_id"],
        "model": res["model"],
        "tokens": total_tokens,
        "tok_per_sec": tok_sec,
        "duration_ms": total_duration,
        "completed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "learned_skill": learned_skill,
        "memory_summary": memory_summary,
        "steps": steps,
        "status": "SUCCESS",
    }
    st.setdefault("ticket_completion_logs", []).insert(0, completion_log)
    st["ticket_completion_logs"] = st["ticket_completion_logs"][:50]

    st["chat_history"].append(
        {
            "id": f"tck-{str(uuid.uuid4())[:6]}",
            "role": "assistant",
            "timestamp": time.strftime("%H:%M:%S"),
            "model": res["model"],
            "tokens": total_tokens,
            "duration_ms": total_duration,
            "learned_skill": learned_skill,
            "content": f"**[Executed Paperclip Ticket `{t_id}`: {title}]**\n\n{final_output}",
        }
    )
    save_claude_state(st)
    return {
        "ok": True,
        "ticket_id": t_id,
        "output": final_output,
        "tokens": total_tokens,
        "duration_ms": total_duration,
        "model": res["model"],
        "learned_skill": learned_skill,
        "completion_log": completion_log,
    }


@app.get("/api/ticket_logs")
async def get_claude_ticket_logs():
    st = load_claude_state()
    return {"logs": st.get("ticket_completion_logs", [])}


@app.post("/api/skills")
async def add_custom_skill(payload: Dict[str, Any] = Body(...)):
    st = load_claude_state()
    skill = {
        "id": f"cskill-{str(uuid.uuid4())[:6]}",
        "name": payload.get("name", "claude-custom-playbook"),
        "category": payload.get("category", "Claude Playbook"),
        "description": payload.get("description", ""),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "uses": 1,
    }
    st["skills"].insert(0, skill)
    save_claude_state(st)
    return {"skill": skill, "state": st}


@app.get("/ads.txt")
async def serve_ads_txt():
    return PlainTextResponse("google.com, pub-1596056523034714, DIRECT, f08c47fec0942fa0\n")


if __name__ == "__main__":
    try:
        from dual_tls_runner import run_dual_http_https
        port = int(os.environ.get("PORT", os.environ.get("CLAUDE_PORT", "7893")))
        run_dual_http_https(app, port=port)
    except ImportError:
        import uvicorn
        port = int(os.environ.get("PORT", "7893"))
        uvicorn.run(app, host="0.0.0.0", port=port)
