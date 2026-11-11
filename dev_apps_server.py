#!/usr/bin/env python3
"""
K3s 'dev' Namespace Autonomous Website & App Hosting Gateway (Port 8080 / NodePort 30795)
Serves all websites and web applications built autonomously by Claude, Hermes, and Paperclip agents.
Includes mandatory Google AdSense (ca-pub-1596056523034714) and /ads.txt on all public pages.
"""

import json
import os
import time
from typing import Any, Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse

APP_PORT = int(os.environ.get("PORT", "8080"))
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))
DEV_APPS_DIR = os.path.join(DATA_DIR, "dev_apps")
STATE_FILE = os.path.join(DATA_DIR, "paperclip_state.json")
ADS_TXT_CONTENT = "google.com, pub-1596056523034714, DIRECT, f08c47fec0942fa0\n"

os.makedirs(DEV_APPS_DIR, exist_ok=True)

app = FastAPI(title="K3s Dev Namespace Autonomous App Gateway", version="2.4.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_dev_apps() -> List[Dict[str, Any]]:
    apps: List[Dict[str, Any]] = []
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                st = json.load(f)
                apps = st.get("dev_apps", [])
        except Exception:
            pass
    # Also scan DEV_APPS_DIR for any directories with meta.json
    known_slugs = {a.get("slug") for a in apps if a.get("slug")}
    if os.path.exists(DEV_APPS_DIR):
        for entry in sorted(os.listdir(DEV_APPS_DIR), reverse=True):
            meta_p = os.path.join(DEV_APPS_DIR, entry, "meta.json")
            if entry not in known_slugs and os.path.exists(meta_p):
                try:
                    with open(meta_p, "r", encoding="utf-8") as mf:
                        apps.append(json.load(mf))
                except Exception:
                    pass
    return apps


@app.get("/ads.txt", response_class=PlainTextResponse)
async def serve_root_ads_txt():
    return PlainTextResponse(content=ADS_TXT_CONTENT, media_type="text/plain")


@app.get("/healthz")
async def healthz():
    return {"ok": True, "namespace": "dev", "service": "dev-apps-gateway", "apps_count": len(load_dev_apps())}


@app.get("/api/apps")
async def api_list_apps():
    apps = load_dev_apps()
    return {"ok": True, "namespace": "dev", "count": len(apps), "apps": apps}


@app.get("/{slug}/ads.txt", response_class=PlainTextResponse)
async def serve_app_ads_txt(slug: str):
    return PlainTextResponse(content=ADS_TXT_CONTENT, media_type="text/plain")


@app.get("/{slug}", response_class=HTMLResponse)
@app.get("/{slug}/", response_class=HTMLResponse)
async def serve_deployed_app(slug: str):
    safe_slug = "".join(c for c in slug if c.isalnum() or c in "-_").strip("-_")
    idx_path = os.path.join(DEV_APPS_DIR, safe_slug, "index.html")
    if not os.path.exists(idx_path):
        return HTMLResponse(
            content=f"<html><body style='background:#060913;color:#f8fafc;font-family:sans-serif;padding:40px;'><h2>404 — K3s Dev App '{safe_slug}' not found</h2><p><a href='/' style='color:#38bdf8;'>← Back to K3s Dev Namespace Portal</a></p></body></html>",
            status_code=404,
        )
    with open(idx_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/", response_class=HTMLResponse)
async def serve_portal():
    apps = load_dev_apps()
    cards_html = ""
    for a in apps:
        slug = a.get("slug", "")
        title = a.get("title", slug)
        agent = a.get("agent_name", "Claude-01 + Hermes-01")
        avatar = a.get("agent_avatar", "✴️")
        model = a.get("model", "qwen2.5-coder:14b")
        created = a.get("created_at", "")
        tck_id = a.get("ticket_id", "AUTO")
        desc = a.get("description", "Autonomous web application deployed to K3s dev namespace.")
        cards_html += f"""
        <div class="card">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span class="badge">{tck_id} • k3s namespace: dev</span>
            <span style="font-size:12px;color:#94a3b8;">{created}</span>
          </div>
          <h3 style="margin:0 0 6px 0;font-size:17px;color:#f8fafc;">{title}</h3>
          <p style="font-size:12.5px;color:#94a3b8;line-height:1.45;margin:0 0 12px 0;">{desc[:180]}</p>
          <div style="font-size:12px;color:#cbd5e1;margin-bottom:14px;">
            Built by: <strong>{avatar} {agent}</strong> • Model: <code>{model}</code>
          </div>
          <div style="display:flex;gap:8px;">
            <a href="/{slug}/" target="_blank" class="btn">🚀 Open Live Website (/{slug}/) ↗</a>
          </div>
        </div>
        """
    if not cards_html:
        cards_html = "<div class='card'><h3>⏳ Autonomous Agents are building the first K3s dev website...</h3><p>Refresh in a few seconds.</p></div>"

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>K3s Dev Namespace — Autonomous Agent App Portal (30795)</title>
  <!-- Google AdSense with Page-Level Auto-Ads -->
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1596056523034714"
     crossorigin="anonymous"></script>
  <script>
    (adsbygoogle = window.adsbygoogle || []).push({{
      google_ad_client: "ca-pub-1596056523034714",
      enable_page_level_ads: true
    }});
  </script>
  <style>
    body {{ margin:0; background:#050811; color:#f8fafc; font-family:'Inter',system-ui,sans-serif; padding:28px; }}
    .wrap {{ max-width:1360px; margin:0 auto; }}
    .hdr {{ display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px; padding:20px 24px; background:rgba(15,23,42,0.85); border:1px solid rgba(56,189,248,0.3); border-radius:14px; margin-bottom:24px; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(340px, 1fr)); gap:16px; }}
    .card {{ background:rgba(15,23,42,0.9); border:1px solid rgba(255,255,255,0.1); border-radius:12px; padding:18px; display:flex; flex-direction:column; justify-content:space-between; }}
    .badge {{ background:rgba(16,185,129,0.15); color:#34d399; border:1px solid rgba(16,185,129,0.4); border-radius:6px; padding:3px 8px; font-size:11px; font-family:monospace; }}
    .btn {{ display:inline-flex; align-items:center; justify-content:center; width:100%; padding:10px 14px; background:linear-gradient(135deg,#0284c7,#7e22ce); color:#fff; text-decoration:none; border-radius:8px; font-weight:700; font-size:13px; }}
    code {{ color:#38bdf8; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hdr">
      <div>
        <div style="font-size:12px;color:#38bdf8;font-weight:700;letter-spacing:0.08em;">KUBERNETES NAMESPACE: DEV • NODEPORT 30795</div>
        <h1 style="margin:4px 0 0 0;font-size:24px;">🚀 K3s Dev Autonomous Website &amp; App Hosting Gateway</h1>
        <div style="font-size:13px;color:#94a3b8;margin-top:4px;">Continuously built and deployed by <strong>Claude-01 (✴️)</strong>, <strong>Hermes-01 (🪽)</strong>, and the <strong>Paperclip AI Swarm</strong>.</div>
      </div>
      <div style="display:flex;gap:10px;">
        <a href="http://192.168.0.81:30791" class="btn" style="width:auto;padding:10px 18px;">📎 Back to Paperclip Control Plane (30791)</a>
      </div>
    </div>
    <div class="grid">{cards_html}</div>
    <div style="margin:24px 0;text-align:center;">
      <ins class="adsbygoogle"
           style="display:block"
           data-ad-client="ca-pub-1596056523034714"
           data-ad-slot="auto"
           data-ad-format="auto"
           data-full-width-responsive="true"></ins>
      <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
    </div>
  </div>
  <script>setTimeout(() => location.reload(), 15000);</script>
</body>
</html>"""
    return HTMLResponse(content=html_doc)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=APP_PORT)
