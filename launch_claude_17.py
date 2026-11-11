import os
import subprocess
import time

subprocess.run(["pkill", "-f", "7893"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
subprocess.run(["pkill", "-f", "claude_agent"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
time.sleep(1)

env = os.environ.copy()
env.update({
    "OLLAMA_URL": "http://127.0.0.1:11434",
    "PAPERCLIP_URL": "http://192.168.0.81:30791",
    "HERMES_URL": "http://127.0.0.1:7892",
    "CLAUDE_SELF_URL": "http://192.168.0.17:7893",
    "CLAUDE_NODE_ID": "claude-host-17",
    "PORT": "7893",
    "DATA_DIR": "/opt/hermes/data",
})

log_f = open("/opt/hermes/claude.log", "ab")
p = subprocess.Popen(
    ["/opt/hermes/venv/bin/python3", "/opt/hermes/claude_agent.py"],
    cwd="/opt/hermes",
    env=env,
    stdin=subprocess.DEVNULL,
    stdout=log_f,
    stderr=log_f,
    start_new_session=True,
    close_fds=True,
)
print(f"Started claude_agent (dual HTTP+HTTPS) on port 7893 with PID {p.pid}")
