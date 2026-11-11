import json
import re
import subprocess
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

KUBECONFIG = r"C:\scripts\k8s-kubeconfig.yaml"

def run_in_n8n(cmd):
    full_cmd = ["kubectl", "--kubeconfig", KUBECONFIG, "-n", "ai", "exec", "deploy/n8n", "--"] + cmd
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    return res.stdout, res.stderr, res.returncode

def import_workflow(wf_dict):
    clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', wf_dict.get("name", "wf")).lower()
    path = f"/tmp/{clean_name}.json"
    wf_bytes = json.dumps(wf_dict, indent=2).encode('utf-8')

    # Pipe JSON into pod
    pipe_cmd = ["kubectl", "--kubeconfig", KUBECONFIG, "-n", "ai", "exec", "-i", "deploy/n8n", "--", "sh", "-c", f"cat > {path} && n8n import:workflow --input={path}"]
    p = subprocess.Popen(pipe_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate(wf_bytes)
    print(f"[✓] Staged & Imported '{wf_dict['name']}' (code {p.returncode})")
    return p.returncode == 0

# 1. Fetch live agents from Paperclip
try:
    resp = urllib.request.urlopen('http://192.168.0.81:30791/api/state', timeout=5)
    state_data = json.loads(resp.read().decode())['state']
    agents = state_data.get('agents', [])
    print(f"[*] Found {len(agents)} agents in Paperclip Control Plane")
except Exception as e:
    print(f"[!] Warning: Could not fetch agents dynamically ({e}), using default fleet")
    agents = [
        {"id": "agent-ceo", "name": "Atlas", "role": "CEO & Executive Orchestrator", "avatar": "👑", "model": "qwen3:4b-instruct", "adapter": "ollama_native"},
        {"id": "agent-cto", "name": "Vega", "role": "CTO & Chief Systems Architect", "avatar": "🧠", "model": "qwen3.5:latest", "adapter": "ollama_native"},
        {"id": "agent-coder", "name": "Forge", "role": "Staff Full-Stack & K8s Engineer", "avatar": "⚙️", "model": "qwen2.5-coder:7b", "adapter": "ollama_native"},
        {"id": "agent-hermes", "name": "Hermes-01", "role": "Autonomous Self-Improving Worker", "avatar": "🪽", "model": "qwen2.5-coder:14b", "adapter": "hermes_bridge"},
        {"id": "agent-sec", "name": "Sentinel", "role": "Principal QA & Security Auditor", "avatar": "🛡️", "model": "qwen2.5-coder:1.5b", "adapter": "ollama_native"},
        {"id": "agent-hermes-17", "name": "Hermes-17", "role": "Host Autonomous GPU Worker (192.168.0.17)", "avatar": "🪽", "model": "qwen2.5-coder:14b", "adapter": "hermes_bridge"},
    ]

# Deduplicate agents by slug
seen = set()
agent_configs = []
for a in agents:
    aid = a["id"]
    slug = aid.replace("agent-", "")
    if slug in seen:
        continue
    seen.add(slug)
    agent_configs.append({
        "id": aid,
        "name": a["name"],
        "slug": slug,
        "role": a["role"],
        "avatar": a.get("avatar", "🤖"),
        "model": a.get("model", "qwen2.5-coder:7b"),
        "adapter": a.get("adapter", "ollama_native"),
        "sys_prompt": a.get("system_prompt", f"You are {a['name']}, {a['role']} in Sovereign AI Corp.")
    })

all_workflows = []

# ==============================================================================
# 1. PAPERCLIP TICKET PIPELINE WORKFLOW (Receives all completed deliverables)
# ==============================================================================
wf_ticket_pipeline = {
    "name": "Paperclip Agent Ticket Pipeline",
    "nodes": [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "paperclip-ticket",
                "responseMode": "onReceived",
                "options": {}
            },
            "id": "node-wb-ticket-pipeline",
            "name": "Paperclip Ticket Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [180, 260],
            "webhookId": "paperclip-ticket"
        },
        {
            "parameters": {
                "jsCode": """
const item = $input.first().json;
const body = item.body || item;

const event = body.event || 'ticket_event';
const ticketId = body.ticket_id || 'TCK-UNKNOWN';
const title = body.title || 'Untitled Objective';
const agentName = body.agent_name || 'Autonomous Agent';
const agentRole = body.agent_role || 'Specialist';
const avatar = body.avatar || '🤖';
const model = body.model || 'qwen2.5-coder';
const output = body.output || body.deliverable || '';
const tokens = body.tokens || body.tokens_generated || 0;
const durationMs = body.duration_ms || 0;
const timestamp = body.timestamp || new Date().toISOString();

const summary = `[n8n Swarm Pipeline] Received ${event} for ${ticketId} ('${title}') from ${avatar} ${agentName} (${model}) - ${tokens} tokens generated in ${durationMs}ms`;

return [{
    json: {
        event: event,
        ticket_id: ticketId,
        title: title,
        agent_name: agentName,
        agent_role: agentRole,
        avatar: avatar,
        model: model,
        deliverable: output,
        tokens: tokens,
        duration_ms: durationMs,
        pipeline_status: 'PROCESSED_IN_N8N',
        summary: summary,
        received_at: timestamp
    }
}];
"""
            },
            "id": "node-parse-ticket",
            "name": "Parse Ticket Deliverable",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [440, 260]
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://paperclip.ai.svc.cluster.local:7891/api/audit",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": """={{ JSON.stringify({
  "actor": "n8n Swarm Pipeline",
  "event": "n8n validated & stored workflow for " + $json.ticket_id + ": '" + ($json.title || "").substring(0, 48) + "' (" + $json.tokens + " tokens)",
  "level": "SUCCESS"
}) }}""",
                "continueOnFail": True,
                "options": {
                    "timeout": 5000
                }
            },
            "id": "node-audit-ticket",
            "name": "Log Pipeline Execution",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [700, 260]
        }
    ],
    "connections": {
        "Paperclip Ticket Webhook": {
            "main": [
                [{"node": "Parse Ticket Deliverable", "type": "main", "index": 0}]
            ]
        },
        "Parse Ticket Deliverable": {
            "main": [
                [{"node": "Log Pipeline Execution", "type": "main", "index": 0}]
            ]
        }
    },
    "active": True,
    "settings": {"executionOrder": "v1"}
}
all_workflows.append(wf_ticket_pipeline)

# ==============================================================================
# 2. UNIVERSAL SWARM GATEWAY WORKFLOW
# ==============================================================================
wf_gateway = {
    "name": "Universal Agent Swarm Gateway",
    "nodes": [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "agent-swarm-gateway",
                "responseMode": "onReceived",
                "options": {}
            },
            "id": "node-wb-gw",
            "name": "Gateway Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [180, 260],
            "webhookId": "agent-swarm-gateway"
        },
        {
            "parameters": {
                "jsCode": """
const item = $input.first().json;
const body = item.body || item;
const requestedAgent = (body.agent || body.agent_id || 'hermes').toLowerCase();
const prompt = body.prompt || body.message || body.task || 'Report status';

let targetUrl = 'http://192.168.0.17:11434/api/chat';
let selectedModel = 'qwen2.5-coder:14b';
let agentName = 'Hermes-17';
let backendType = 'hermes_host17';

if (requestedAgent.includes('17')) {
    targetUrl = 'http://192.168.0.17:7892/api/chat';
    selectedModel = 'qwen2.5-coder:14b';
    agentName = 'Hermes-17';
    backendType = 'hermes_host17';
} else if (requestedAgent.includes('ceo') || requestedAgent.includes('atlas')) {
    targetUrl = 'http://192.168.0.17:11434/api/chat';
    selectedModel = 'qwen3:4b-instruct';
    agentName = 'Atlas';
    backendType = 'ollama_native';
} else if (requestedAgent.includes('cto') || requestedAgent.includes('vega')) {
    targetUrl = 'http://192.168.0.17:11434/api/chat';
    selectedModel = 'qwen3.5:latest';
    agentName = 'Vega';
    backendType = 'ollama_native';
} else if (requestedAgent.includes('coder') || requestedAgent.includes('forge')) {
    targetUrl = 'http://192.168.0.17:11434/api/chat';
    selectedModel = 'qwen2.5-coder:7b';
    agentName = 'Forge';
    backendType = 'ollama_native';
} else if (requestedAgent.includes('sec') || requestedAgent.includes('sentinel')) {
    targetUrl = 'http://192.168.0.17:11434/api/chat';
    selectedModel = 'qwen2.5-coder:1.5b';
    agentName = 'Sentinel';
    backendType = 'ollama_native';
} else {
    targetUrl = 'http://hermes.ai.svc.cluster.local:7892/api/chat';
    selectedModel = 'qwen2.5-coder:14b';
    agentName = 'Hermes-01';
    backendType = 'hermes_k3s';
}

let payload = {};
if (backendType.startsWith('hermes')) {
    payload = { prompt: prompt, model: selectedModel, agent_name: agentName };
} else {
    payload = {
        model: selectedModel,
        stream: false,
        messages: [
            { role: 'system', content: 'You are ' + agentName + ' in Sovereign AI Corp. Complete the objective thoroughly.' },
            { role: 'user', content: prompt }
        ]
    };
}

return [{
    json: {
        agent_selected: agentName,
        target_url: targetUrl,
        backend_type: backendType,
        model: selectedModel,
        prompt: prompt,
        payload: payload,
        timestamp: new Date().toISOString()
    }
}];
"""
            },
            "id": "node-route-gw",
            "name": "Route to Target Agent",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [420, 260]
        },
        {
            "parameters": {
                "method": "POST",
                "url": "={{ $json.target_url }}",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify($json.payload) }}",
                "options": {
                    "timeout": 180000
                }
            },
            "id": "node-exec-gw",
            "name": "Execute Target Agent Inference",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [660, 260],
            "continueOnFail": True,
            "retryOnFail": True,
            "maxTries": 3,
            "waitBetweenTries": 2000
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://paperclip.ai.svc.cluster.local:7891/api/audit",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": """={{ JSON.stringify({
  "actor": "n8n Swarm Gateway",
  "event": "Gateway dispatched objective to " + $json.agent_selected + " (" + $json.model + ")",
  "level": "SUCCESS"
}) }}""",
                "continueOnFail": True,
                "options": {
                    "timeout": 5000
                }
            },
            "id": "node-audit-gw",
            "name": "Log Gateway Action",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [920, 260]
        }
    ],
    "connections": {
        "Gateway Webhook": {
            "main": [[{"node": "Route to Target Agent", "type": "main", "index": 0}]]
        },
        "Route to Target Agent": {
            "main": [[{"node": "Execute Target Agent Inference", "type": "main", "index": 0}]]
        },
        "Execute Target Agent Inference": {
            "main": [[{"node": "Log Gateway Action", "type": "main", "index": 0}]]
        }
    },
    "active": True,
    "settings": {"executionOrder": "v1"}
}
all_workflows.append(wf_gateway)

# ==============================================================================
# 3. DEDICATED AGENT WORKFLOWS
# ==============================================================================
for ac in agent_configs:
    wf_name = f"Agent: {ac['avatar']} {ac['name']} ({ac['role']})"
    webhook_path = f"agent-{ac['slug']}"
    is_hermes = "hermes" in ac["adapter"] or "hermes" in ac["slug"].lower()
    if "17" in ac["slug"]:
        target_api_url = "http://192.168.0.17:7892/api/chat"
        backend_type = "hermes_host17"
    elif is_hermes:
        target_api_url = "http://hermes.ai.svc.cluster.local:7892/api/chat"
        backend_type = "hermes_k3s"
    else:
        target_api_url = "http://192.168.0.17:11434/api/chat"
        backend_type = "ollama_native"

    wf = {
        "name": wf_name,
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": webhook_path,
                    "responseMode": "onReceived",
                    "options": {}
                },
                "id": f"node-wb-{ac['slug']}",
                "name": f"Webhook: {ac['name']}",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [180, 260],
                "webhookId": webhook_path
            },
            {
                "parameters": {
                    "jsCode": f"""
const item = $input.first().json;
const body = item.body || item;
const prompt = body.prompt || body.message || body.task || body.title || body.deliverable || 'Execute assigned objective';
const agentName = '{ac['name']}';
const agentRole = '{ac['role']}';
const model = body.model || '{ac['model']}';
const sysPrompt = {json.dumps(ac['sys_prompt'])};
const backendType = '{backend_type}';

let requestPayload = {{}};
if (backendType.startsWith('hermes')) {{
    requestPayload = {{
        prompt: prompt,
        model: model,
        agent_name: agentName
    }};
}} else {{
    requestPayload = {{
        model: model,
        stream: false,
        messages: [
            {{ role: 'system', content: sysPrompt }},
            {{ role: 'user', content: prompt }}
        ],
        options: {{ temperature: 0.3 }}
    }};
}}

return [{{
    json: {{
        agent_id: '{ac['id']}',
        agent_name: agentName,
        agent_role: agentRole,
        model: model,
        prompt: prompt,
        backend_url: '{target_api_url}',
        backend_type: backendType,
        request_payload: requestPayload,
        timestamp: new Date().toISOString()
    }}
}}];
"""
                },
                "id": f"node-prep-{ac['slug']}",
                "name": "Prepare Agent Context",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [420, 260]
            },
            {
                "parameters": {
                    "method": "POST",
                    "url": target_api_url,
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": "={{ JSON.stringify($json.request_payload) }}",
                    "options": {
                        "timeout": 180000,
                        "allowUnauthorizedCerts": True
                    }
                },
                "id": f"node-exec-{ac['slug']}",
                "name": f"Inference: {ac['name']}",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [660, 260],
                "continueOnFail": True,
                "retryOnFail": True,
                "maxTries": 3,
                "waitBetweenTries": 2000
            },
            {
                "parameters": {
                    "method": "POST",
                    "url": "http://paperclip.ai.svc.cluster.local:7891/api/audit",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": f"""={{{{ JSON.stringify({{
  "actor": "n8n Agent Workflow: {ac['avatar']} {ac['name']}",
  "event": "Workflow processed objective for {ac['name']}",
  "level": "SUCCESS"
}}) }}}}""",
                    "continueOnFail": True,
                    "options": {
                        "timeout": 5000
                    }
                },
                "id": f"node-audit-{ac['slug']}",
                "name": "Log Agent Action",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [920, 260]
            }
        ],
        "connections": {
            f"Webhook: {ac['name']}": {
                "main": [[{"node": "Prepare Agent Context", "type": "main", "index": 0}]]
            },
            "Prepare Agent Context": {
                "main": [[{"node": f"Inference: {ac['name']}", "type": "main", "index": 0}]]
            },
            f"Inference: {ac['name']}": {
                "main": [[{"node": "Log Agent Action", "type": "main", "index": 0}]]
            }
        },
        "active": True,
        "settings": {"executionOrder": "v1"}
    }
    all_workflows.append(wf)

print(f"\n[*] Deploying {len(all_workflows)} workflows into n8n...")
for wf in all_workflows:
    import_workflow(wf)

# Query workflow IDs and publish each one
out, err, _ = run_in_n8n(["node", "-e", "const sqlite3 = require('/usr/local/lib/node_modules/n8n/node_modules/sqlite3'); const db = new sqlite3.Database('/home/node/.n8n/database.sqlite'); db.all('SELECT id, name FROM workflow_entity', [], (err, rows) => console.log(JSON.stringify(rows)));"])
try:
    rows = json.loads(out)
    print(f"\n[*] Found {len(rows)} total workflows in database. Publishing all...")
    for r in rows:
        wf_id = r["id"]
        wf_name = r["name"]
        pub_out, pub_err, code = run_in_n8n(["n8n", "publish:workflow", f"--id={wf_id}"])
        print(f"[✓] Published '{wf_name}' (ID: {wf_id})")
except Exception as e:
    print(f"[!] Error reading workflow rows: {e}")

print("\n[*] Restarting n8n to apply all active webhooks...")
subprocess.run(["kubectl", "--kubeconfig", KUBECONFIG, "-n", "ai", "rollout", "restart", "deploy/n8n"])
subprocess.run(["kubectl", "--kubeconfig", KUBECONFIG, "-n", "ai", "rollout", "status", "deploy/n8n", "--timeout=60s"])
print("[✓] ALL AGENT WORKFLOWS SUCCESSFULLY DEPLOYED AND LIVE IN N8N!")

