# Paperclip-Ollama (`ClipOS`) & Hermes-Ollama (`Hermes-01`)

An end-to-end **Zero-Human AI Company Control Plane** (inspired by [paperclip.ing](https://paperclip.ing/)) paired with a **Self-Improving Autonomous Agent** (inspired by Hermes Agent), purpose-built for **1-click connection to Ollama** (`http://192.168.0.17:11434`) and deployed natively on **K3s**.

## Components

1. **Paperclip-Ollama (`paperclip_server.py`, Port `7891` / NodePort `30791`)**
   - **Product Website & Software Host**: Hosts the interactive landing page and downloadable `paperclip-hermes-suite.zip` software bundle (`/download/paperclip-hermes-suite.zip`).
   - **1-Click Ollama Connector**: Connects directly to `http://192.168.0.17:11434`, discovers all installed GGUF models via `/api/tags`, and binds models to roles in your AI company.
   - **AI Org Chart & Ticket Dispatch**: Hire AI agents (CEO, CTO, Hermes Worker, QA Auditor, DevOps), dispatch goals/tickets, and execute them live against Ollama or delegate them over the bridge to Hermes.
   - **Governance & Audit Log**: Built-in human approval gates and full token/latency telemetry.

2. **Hermes-Ollama (`hermes_agent.py`, Port `7892` / NodePort `30792`)**
   - **1-Click Dual Bridge**: Connects simultaneously to Ollama (`http://192.168.0.17:11434`) and Paperclip (`http://paperclip.ai.svc.cluster.local:7891`).
   - **Autonomous Heartbeat & Task Execution**: Auto-registers with Paperclip's Org Chart (`agent-hermes`) and executes delegated tickets via `/api/execute_ticket`.
   - **Self-Improving Skills Vault & Episodic Memory**: Synthesizes reusable procedural skills after every task and persists cross-session memories.

## Quick Start (Local)

```bash
pip install -r requirements.txt
python paperclip_server.py   # Runs on http://localhost:7891
python hermes_agent.py       # Runs on http://localhost:7892
```

## K3s Deployment

```bash
kubectl apply -f k8s-paperclip-hermes.yaml
```
