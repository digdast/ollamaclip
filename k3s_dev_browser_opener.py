#!/usr/bin/env python3
"""
Local Windows Desktop Auto-Opener for K3s 'dev' Websites & Apps
Polls Paperclip Control Plane (http://192.168.0.81:30791/api/dev/apps) and automatically
opens newly finished websites in the user's desktop browser when agents complete them.
"""

import json
import os
import sys
import time
import urllib.request
import webbrowser

PAPERCLIP_API = os.environ.get("PAPERCLIP_API", "http://192.168.0.81:30791/api/dev/apps")
POLL_SECONDS = int(os.environ.get("POLL_SECONDS", "5"))


def fetch_dev_apps():
    req = urllib.request.Request(PAPERCLIP_API, headers={"User-Agent": "K3s-Dev-Desktop-Opener/1.0"})
    with urllib.request.urlopen(req, timeout=8) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    seen_slugs = set()
    first_run = True
    print(f"[*] Watching K3s 'dev' Website Factory at {PAPERCLIP_API} ...")

    while True:
        try:
            data = fetch_dev_apps()
            apps = data.get("apps", [])
            if first_run:
                for a in apps:
                    if a.get("slug"):
                        seen_slugs.add(a["slug"])
                first_run = False
                # Open the latest deployed site on initial launch if requested via --open-latest
                if "--open-latest" in sys.argv and apps:
                    latest_url = apps[0].get("k3s_dev_url") or apps[0].get("paperclip_dev_url")
                    if latest_url:
                        print(f"[+] Opening latest K3s dev website: {apps[0].get('title')} -> {latest_url}")
                        webbrowser.open(latest_url)
            else:
                for a in reversed(apps):
                    slug = a.get("slug")
                    if slug and slug not in seen_slugs:
                        seen_slugs.add(slug)
                        url = a.get("k3s_dev_url") or a.get("paperclip_dev_url")
                        if url:
                            print(f"[+] New K3s dev website finished by {a.get('agent_name')}: {a.get('title')} -> {url}")
                            webbrowser.open(url)
        except Exception as exc:
            print(f"[!] Poll warning: {exc}")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
