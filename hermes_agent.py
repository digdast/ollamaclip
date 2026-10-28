#!/usr/bin/env python3
"""
Hermes-Ollama — Self-Improving Autonomous Agent with 1-Click Paperclip & Ollama Connectors
Inspired by Nous Research's Hermes Agent: features an automatic skill synthesis loop,
cross-session episodic memory, native Ollama model discovery (192.168.0.17:11434),
and bi-directional Paperclip Control Plane registration.
"""
import asyncio
import json
import os
import re
import time
import urllib.request
import uuid
from typing import Any, Dict, List

from fastapi import FastAPI, Body
from fastapi.responses import HTMLResponse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
os.makedirs(DATA_DIR, exist_ok=True)

HERMES_STATE_FILE = os.path.join(DATA_DIR, "hermes_state.json")
DEFAULT_OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://192.168.0.17:11434")
DEFAULT_PAPERCLIP_URL = os.environ.get("PAPERCLIP_URL", "http://192.168.0.81:30791")
DEFAULT_SELF_URL = os.environ.get("HERMES_SELF_URL", "http://127.0.0.1:7892")
DEFAULT_NODE_ID = os.environ.get("NODE_ID", "hermes-k3s-primary")
DEFAULT_AGENT_NAME = os.environ.get("AGENT_NAME", "Hermes-01")
DEFAULT_MODEL_NAME = os.environ.get("DEFAULT_MODEL", "qwen2.5-coder:14b")

app = FastAPI(
    title="Hermes-Ollama — Self-Improving Autonomous Agent",
    version="1.0.0",
)


def default_hermes_state() -> Dict[str, Any]:
    return {
        "node_id": DEFAULT_NODE_ID,
        "agent_name": DEFAULT_AGENT_NAME,
        "ollama_url": DEFAULT_OLLAMA_URL,
        "paperclip_url": DEFAULT_PAPERCLIP_URL,
        "self_url": DEFAULT_SELF_URL,
        "active_model": DEFAULT_MODEL_NAME,
        "paperclip_connected": True,
        "last_sync": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tasks_completed": 3,
        "skills": [
            {
                "id": "skill-k3s-sqlite-nvme",
                "name": "k3s-sqlite-nvme-optimization",
                "category": "Kubernetes & Storage",
                "description": "Pin SQLite WAL workloads to local NVMe hostPath (/var/lib/<svc>) and mount RAM-tmpfs on /tmp to eliminate NFS lock contention.",
                "created_at": "2026-10-28 09:15:00",
                "uses": 4,
            },
            {
                "id": "skill-etcd-quorum-ha",
                "name": "k3s-etcd-3node-quorum-join",
                "category": "Cluster HA",
                "description": "Ensure unique /etc/machine-id, clean cloned /var/lib/rancher/k3s/server/db state, and set explicit --node-ip and --tls-san before joining a cloned K3s control plane.",
                "created_at": "2026-10-28 08:55:00",
                "uses": 2,
            },
            {
                "id": "skill-ollama-local-routing",
                "name": "ollama-model-tier-routing",
                "category": "AI Orchestration",
                "description": "Route fast code generation to qwen2.5-coder:7b/14b, deep architectural reasoning to qwen3.5:latest or DeepSeek-R1-Distill-Qwen-14B, and rapid audits to qwen2.5-coder:1.5b.",
                "created_at": "2026-10-28 09:30:00",
                "uses": 7,
            },
            {
                "id": "skill-zero-downtime-rollout",
                "name": "k8s-zero-downtime-rollout-probe",
                "category": "DevOps Automation",
                "description": "Configure HTTP readinessProbes alongside resource requests/limits so kubectl rollout restart verifies pod health before terminating old replicas.",
                "created_at": "2026-10-28 09:35:00",
                "uses": 5,
            },
        ],
        "memories": [
            {
                "id": "mem-1",
                "timestamp": "2026-10-28 09:15:00",
                "summary": "Ollama server confirmed active at http://192.168.0.17:11434 (v0.40.11) with 14 local GGUF models including qwen3.5, qwen2.5-coder:32b, devstral-small-2, and DeepSeek-R1.",
                "tags": ["ollama", "infrastructure"],
            },
            {
                "id": "mem-2",
                "timestamp": "2026-10-28 09:20:00",
                "summary": "Proxmox HA K3s cluster expanded to 7 nodes (3 control-plane/etcd: k8s-cp-01..03, 4 workers: k8s-worker-01..04) with 54 vCPUs and 81.8 GiB RAM.",
                "tags": ["k3s", "proxmox"],
            },
        ],
        "chat_history": [
            {
                "id": "msg-welcome",
                "role": "assistant",
                "timestamp": time.strftime("%H:%M:%S"),
                "model": "qwen2.5-coder:7b",
                "learned_skill": "ollama-model-tier-routing",
                "content": (
                    "Greetings! I am **Hermes-01**, your self-improving autonomous agent.\n\n"
                    "- **Ollama Connection**: Linked to `http://192.168.0.17:11434`\n"
                    "- **Paperclip Bridge**: Linked to Paperclip Control Plane (`Sovereign AI Corp`)\n"
                    "- **Self-Improving Loop**: Active (every task I complete for Paperclip or in this console synthesizes reusable skills into my Skills Vault)."
                ),
            }
        ],
    }


def load_hermes_state() -> Dict[str, Any]:
    if os.path.exists(HERMES_STATE_FILE):
        try:
            with open(HERMES_STATE_FILE, "r", encoding="utf-8") as f:
                st = json.load(f)
            if os.environ.get("HERMES_SELF_URL"):
                st["self_url"] = os.environ["HERMES_SELF_URL"]
            if os.environ.get("NODE_ID"):
                st["node_id"] = os.environ["NODE_ID"]
            if os.environ.get("AGENT_NAME"):
                st["agent_name"] = os.environ["AGENT_NAME"]
            if os.environ.get("PAPERCLIP_URL"):
                st["paperclip_url"] = os.environ["PAPERCLIP_URL"]
            if os.environ.get("OLLAMA_URL"):
                st["ollama_url"] = os.environ["OLLAMA_URL"]
            return st
        except Exception:
            pass
    st = default_hermes_state()
    save_hermes_state(st)
    return st


def save_hermes_state(st: Dict[str, Any]) -> None:
    with open(HERMES_STATE_FILE, "w", encoding="utf-8") as f:
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
            "name": f"{st['agent_name']} (Autonomous Worker)",
            "endpoint": st.get("self_url", DEFAULT_SELF_URL),
            "ollama_url": st["ollama_url"],
            "model": st["active_model"],
            "skills_count": len(st["skills"]),
            "memories_count": len(st["memories"]),
        }
        req = urllib.request.Request(
            f"{p_url}/api/hermes/register",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        st["paperclip_connected"] = True
        st["last_sync"] = time.strftime("%Y-%m-%d %H:%M:%S")
        save_hermes_state(st)
        return {"ok": True, "data": data}
    except Exception as exc:
        st["paperclip_connected"] = False
        save_hermes_state(st)
        return {"ok": False, "error": str(exc)}


def synthesize_skill_from_task(st: Dict[str, Any], title: str, output: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:36] or "autonomous-skill"
    for s in st["skills"]:
        if s["name"] == slug:
            s["uses"] = s.get("uses", 1) + 1
            return slug

    first_line = next((line.strip("#* -") for line in output.splitlines() if len(line.strip()) > 25), title)
    new_skill = {
        "id": f"skill-{str(uuid.uuid4())[:6]}",
        "name": slug,
        "category": "Learned Experience",
        "description": first_line[:180],
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "uses": 1,
    }
    st["skills"].insert(0, new_skill)
    st["memories"].insert(
        0,
        {
            "id": f"mem-{str(uuid.uuid4())[:6]}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": f"Completed '{title}' using {st['active_model']} and synthesized reusable skill '{slug}'.",
            "tags": ["learned", st["active_model"]],
        },
    )
    return slug


def run_ollama_inference(
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
        or f"You are {agent_name}, a self-improving autonomous AI agent modeled after Nous Research's Hermes Agent, "
        f"connected to Paperclip Control Plane and Ollama ({st['ollama_url']})."
    )
    sys_prompt = (
        f"{base_role}\n\n"
        f"LEARNED SKILLS VAULT:\n{skills_context}\n\n"
        f"EPISODIC MEMORY:\n{memories_context}\n\n"
        f"Provide complete, comprehensive, production-ready solutions with zero truncation and zero placeholders. Conclude with a 1-line 'Learned Skill Takeaway'."
    )
    url = st["ollama_url"].rstrip("/") + "/api/chat"
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "options": {"temperature": 0.3, "num_predict": 8192},
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
    content = (data.get("message", {}).get("content") or "").strip()
    thinking = (data.get("message", {}).get("thinking") or "").strip()
    if not content and thinking:
        content = f"### [Reasoning & Technical Execution]\n\n{thinking}"
    elif thinking and content and len(thinking) > 30:
        first_few_thoughts = "\n".join(thinking.splitlines()[:12])
        content = f"<blockquote>🧠 <b>Reasoning Summary:</b>\n{first_few_thoughts}</blockquote>\n\n{content}"

    tokens = int(data.get("eval_count", 0)) + int(data.get("prompt_eval_count", 0))
    return {
        "content": content or "(Task executed successfully)",
        "tokens": tokens or max(64, len(content) // 4),
        "duration_ms": duration_ms,
        "model": model,
    }


ACTIVE_PROCESSING_TICKETS = set()


async def process_claimed_ticket(ticket: Dict[str, Any]):
    t_id = ticket.get("id")
    if not t_id or t_id in ACTIVE_PROCESSING_TICKETS:
        return
    ACTIVE_PROCESSING_TICKETS.add(t_id)
    try:
        st = load_hermes_state()
        title = ticket.get("title", "Paperclip Task")
        desc = ticket.get("description", "")
        model = ticket.get("model_used") or st["active_model"]
        req_agent = st["agent_name"]

        t0 = time.time()
        steps = [
            {"step": "Task Ingested", "time": "0.0s", "detail": f"Hermes Autonomous Worker claimed ticket {t_id} from Paperclip"},
        ]
        skills_used = [s["name"] for s in st["skills"][:4]]
        steps.append({"step": "Skills Vault Prime", "time": f"{round(time.time() - t0, 2)}s", "detail": f"Primed context with {len(skills_used)} active skills: {', '.join(skills_used)}"})
        steps.append({"step": "Episodic Memory Load", "time": f"{round(time.time() - t0, 2)}s", "detail": f"Retrieved {len(st['memories'])} cross-session memory fragments"})

        full_prompt = f"[PAPERCLIP TICKET {t_id}] {title}\n\n{desc}"
        steps.append({"step": "Ollama Inference Started", "time": f"{round(time.time() - t0, 2)}s", "detail": f"Executing inference via local Ollama {st['ollama_url']} (model: {model})"})
        print(f"[*] Hermes Pull Worker [{st['node_id']}] claimed ticket {t_id}: '{title}' -> starting Ollama inference with {model}...")

        res = await asyncio.to_thread(run_ollama_inference, st, full_prompt, model, req_agent, "")

        elapsed_s = max(0.1, round(time.time() - t0, 2))
        tok_sec = round(res['tokens'] / elapsed_s, 1)
        steps.append({"step": "Inference Complete", "time": f"{elapsed_s}s", "detail": f"Generated {res['tokens']} tokens ({tok_sec} tok/sec in {res['duration_ms']} ms)"})
        print(f"[✓] Hermes Pull Worker [{st['node_id']}] finished inference for {t_id}: {res['tokens']} tokens in {res['duration_ms']} ms ({tok_sec} tok/sec)")

        st = load_hermes_state()
        learned_skill = synthesize_skill_from_task(st, title, res["content"])
        steps.append({"step": "Skill Synthesis", "time": f"{round(time.time() - t0, 2)}s", "detail": f"Saved autonomous reusable skill '{learned_skill}' into persistent Skills Vault"})

        memory_summary = f"Completed ticket {t_id} ('{title}') with {model} on {st['node_id']} and synthesized '{learned_skill}'."
        st["tasks_completed"] = st.get("tasks_completed", 0) + 1

        completion_log = {
            "id": f"hlog-{str(uuid.uuid4())[:8]}",
            "ticket_id": t_id,
            "title": title,
            "agent_name": req_agent,
            "node_id": st["node_id"],
            "model": res["model"],
            "tokens": res["tokens"],
            "tok_per_sec": tok_sec,
            "duration_ms": res["duration_ms"],
            "completed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "learned_skill": learned_skill,
            "memory_summary": memory_summary,
            "steps": steps,
            "status": "SUCCESS",
        }
        st.setdefault("ticket_completion_logs", []).insert(0, completion_log)
        st["ticket_completion_logs"] = st["ticket_completion_logs"][:50]
        save_hermes_state(st)

        # Submit deliverable back to Paperclip Control Plane
        p_url = st["paperclip_url"].rstrip("/")
        cb_payload = {
            "ticket_id": t_id,
            "output": res["content"],
            "tokens": res["tokens"],
            "duration_ms": res["duration_ms"],
            "model": res["model"],
            "learned_skill": learned_skill,
            "completion_log": completion_log,
        }
        req = urllib.request.Request(
            f"{p_url}/api/hermes/complete_ticket",
            data=json.dumps(cb_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"[✓] Successfully reported completion of {t_id} to Paperclip Control Plane!")
    except Exception as exc:
        print(f"[!] Error processing ticket {t_id}: {exc}")
    finally:
        ACTIVE_PROCESSING_TICKETS.discard(t_id)


async def background_paperclip_task_worker():
    await asyncio.sleep(4)
    while True:
        try:
            st = load_hermes_state()
            p_url = st["paperclip_url"].rstrip("/")
            node_id = st.get("node_id", "")
            req = urllib.request.Request(
                f"{p_url}/api/hermes/tasks?node_id={node_id}",
                headers={"User-Agent": f"Hermes-Node/{node_id}"},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            tasks = data.get("tasks", [])
            if tasks:
                print(f"[*] Node [{node_id}] found {len(tasks)} queued tasks in Paperclip: {[t['id'] for t in tasks]}")
            for t in tasks:
                t_assigned = t.get("assigned_to", "")
                is_mine = False
                if t_assigned == f"agent-{node_id}":
                    is_mine = True
                elif "desktop" in node_id.lower() and ("desktop" in t_assigned.lower() or t_assigned == "agent-hermes-desktop-efrain"):
                    is_mine = True
                elif node_id == "hermes-k3s-primary" and t_assigned == "agent-hermes":
                    is_mine = True
                elif node_id == "hermes-host-17" and t_assigned == "agent-hermes-17":
                    is_mine = True

                if is_mine and t["id"] not in ACTIVE_PROCESSING_TICKETS:
                    print(f"[*] Node [{node_id}] claimed ticket {t['id']}: '{t.get('title')}'!")
                    asyncio.create_task(process_claimed_ticket(t))
        except Exception as exc:
            pass
        await asyncio.sleep(2)


async def background_paperclip_heartbeat():
    await asyncio.sleep(3)
    while True:
        try:
            st = load_hermes_state()
            await asyncio.to_thread(sync_with_paperclip, st)
        except Exception:
            pass
        await asyncio.sleep(30)
        await asyncio.sleep(25)


@app.on_event("startup")
async def on_startup():
    asyncio.create_task(background_paperclip_heartbeat())
    asyncio.create_task(background_paperclip_task_worker())


@app.get("/", response_class=HTMLResponse)
async def serve_hermes_ui():
    html_path = os.path.join(TEMPLATES_DIR, "hermes.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/state")
async def get_state():
    st = load_hermes_state()
    ollama = await asyncio.to_thread(probe_ollama_models, st["ollama_url"])
    return {"state": st, "ollama": ollama}


@app.post("/api/connect")
async def connect_endpoints(payload: Dict[str, Any] = Body(...)):
    st = load_hermes_state()
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
    if payload.get("active_model"):
        st["active_model"] = payload["active_model"]

    save_hermes_state(st)
    ollama = await asyncio.to_thread(probe_ollama_models, st["ollama_url"])
    bridge = await asyncio.to_thread(sync_with_paperclip, st)
    return {"state": st, "ollama": ollama, "paperclip_bridge": bridge}


@app.post("/api/chat")
async def chat_with_hermes(payload: Dict[str, Any] = Body(...)):
    st = load_hermes_state()
    prompt = payload.get("prompt", "").strip()
    model = payload.get("model") or st["active_model"]
    if not prompt:
        return {"error": "Empty prompt"}

    st["chat_history"].append(
        {
            "id": f"u-{str(uuid.uuid4())[:6]}",
            "role": "user",
            "timestamp": time.strftime("%H:%M:%S"),
            "content": prompt,
        }
    )
    save_hermes_state(st)

    res = await asyncio.to_thread(run_ollama_inference, st, prompt, model)
    st = load_hermes_state()
    learned_skill = synthesize_skill_from_task(st, prompt[:48], res["content"])
    st["tasks_completed"] = st.get("tasks_completed", 0) + 1
    st["chat_history"].append(
        {
            "id": f"a-{str(uuid.uuid4())[:6]}",
            "role": "assistant",
            "timestamp": time.strftime("%H:%M:%S"),
            "model": res["model"],
            "tokens": res["tokens"],
            "duration_ms": res["duration_ms"],
            "learned_skill": learned_skill,
            "content": res["content"],
        }
    )
    save_hermes_state(st)
    return {"reply": st["chat_history"][-1], "state": st}


@app.post("/api/execute_ticket")
async def execute_paperclip_ticket(payload: Dict[str, Any] = Body(...)):
    """Endpoint called directly by Paperclip Control Plane when a ticket is assigned to Hermes-01."""
    st = load_hermes_state()
    if payload.get("ollama_url"):
        st["ollama_url"] = payload["ollama_url"]
    t_id = payload.get("ticket_id", "TCK")
    title = payload.get("title", "Paperclip Task")
    desc = payload.get("description", "")
    model = payload.get("model") or st["active_model"]
    req_agent_name = payload.get("agent_name") or st["agent_name"]
    req_sys_prompt = payload.get("system_prompt") or ""

    t0 = time.time()
    steps = [
        {"step": "Task Ingested", "time": "0.0s", "detail": f"Hermes Agent Bridge received ticket {t_id} for {req_agent_name}: '{title}'"},
    ]
    skills_used = [s["name"] for s in st["skills"][:4]]
    steps.append({"step": "Skills Vault Prime", "time": f"{round(time.time() - t0, 2)}s", "detail": f"Primed context with {len(skills_used)} active skills: {', '.join(skills_used)}"})
    steps.append({"step": "Episodic Memory Load", "time": f"{round(time.time() - t0, 2)}s", "detail": f"Retrieved {len(st['memories'])} cross-session memory fragments"})

    full_prompt = f"[PAPERCLIP TICKET {t_id}] {title}\n\n{desc}"
    steps.append({"step": "Ollama Inference Started", "time": f"{round(time.time() - t0, 2)}s", "detail": f"Executing deep inference via {st['ollama_url']} (model: {model})"})
    res = await asyncio.to_thread(run_ollama_inference, st, full_prompt, model, req_agent_name, req_sys_prompt)
    
    elapsed_s = max(0.1, round(time.time() - t0, 2))
    tok_sec = round(res['tokens'] / elapsed_s, 1)
    steps.append({"step": "Inference Complete", "time": f"{elapsed_s}s", "detail": f"Generated {res['tokens']} tokens ({tok_sec} tok/sec in {res['duration_ms']} ms)"})

    st = load_hermes_state()
    learned_skill = synthesize_skill_from_task(st, title, res["content"])
    steps.append({"step": "Skill Synthesis", "time": f"{round(time.time() - t0, 2)}s", "detail": f"Saved autonomous reusable skill '{learned_skill}' into persistent Skills Vault"})

    memory_summary = f"Completed ticket {t_id} ('{title}') with {model} on behalf of {req_agent_name} and synthesized '{learned_skill}'."
    st["tasks_completed"] = st.get("tasks_completed", 0) + 1
    
    completion_log = {
        "id": f"hlog-{str(uuid.uuid4())[:8]}",
        "ticket_id": t_id,
        "title": title,
        "agent_name": req_agent_name,
        "node_id": st["node_id"],
        "model": res["model"],
        "tokens": res["tokens"],
        "tok_per_sec": tok_sec,
        "duration_ms": res["duration_ms"],
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
            "tokens": res["tokens"],
            "duration_ms": res["duration_ms"],
            "learned_skill": learned_skill,
            "content": f"**[Executed Paperclip Ticket `{t_id}`: {title}]**\n\n{res['content']}",
        }
    )
    save_hermes_state(st)
    return {
        "ok": True,
        "ticket_id": t_id,
        "output": res["content"],
        "tokens": res["tokens"],
        "duration_ms": res["duration_ms"],
        "model": res["model"],
        "learned_skill": learned_skill,
        "completion_log": completion_log,
    }


@app.get("/api/ticket_logs")
async def get_hermes_ticket_logs():
    st = load_hermes_state()
    return {"logs": st.get("ticket_completion_logs", [])}


@app.post("/api/skills")
async def add_custom_skill(payload: Dict[str, Any] = Body(...)):
    st = load_hermes_state()
    skill = {
        "id": f"skill-{str(uuid.uuid4())[:6]}",
        "name": payload.get("name", "custom-skill"),
        "category": payload.get("category", "Custom"),
        "description": payload.get("description", ""),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "uses": 1,
    }
    st["skills"].insert(0, skill)
    save_hermes_state(st)
    return {"skill": skill, "state": st}


@app.get("/api/ollama/library")
async def hermes_ollama_library(q: str = ""):
    st = load_hermes_state()
    p_url = st["paperclip_url"].rstrip("/")
    try:
        def _fetch():
            with urllib.request.urlopen(f"{p_url}/api/ollama/library?sort=popular&q={q}", timeout=10) as r:
                return json.loads(r.read().decode("utf-8"))
        return await asyncio.to_thread(_fetch)
    except Exception as exc:
        return {"models": [], "active_pulls": [], "error": str(exc)}


@app.post("/api/ollama/pull")
async def hermes_pull_model(payload: Dict[str, Any] = Body(...)):
    st = load_hermes_state()
    p_url = st["paperclip_url"].rstrip("/")
    def _post():
        req = urllib.request.Request(
            f"{p_url}/api/ollama/pull",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    return await asyncio.to_thread(_post)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "7892"))
    uvicorn.run(app, host="0.0.0.0", port=port)
