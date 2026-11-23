#!/usr/bin/env python3
"""Poll GitHub Actions runs for a given SHA until all complete. Emits one line per state change."""
import json
import sys
import time
import urllib.request

SHA = "0f8ac02680d756e526be1a412e808efd238b0a7b"
URL = f"https://api.github.com/repos/vamseeachanta/worldenergydata/actions/runs?head_sha={SHA}&per_page=20"

def fetch():
    req = urllib.request.Request(URL, headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

prev = None
for _ in range(80):  # ~40 minutes max
    try:
        data = fetch()
    except Exception as e:
        print(f"poll-error: {e}", flush=True)
        time.sleep(30)
        continue
    runs = data.get("workflow_runs", [])
    snap = "|".join(
        f"{r['id']}|{r['name']}|{r['status']}|{r['conclusion']}" for r in runs
    )
    if snap != prev:
        for r in runs:
            print(
                f"run={r['id']} name={r['name']} status={r['status']} conclusion={r['conclusion']} url={r['html_url']}",
                flush=True,
            )
        print("---", flush=True)
        prev = snap
    if runs and all(r["status"] == "completed" for r in runs):
        print("ALL-DONE", flush=True)
        sys.exit(0)
    time.sleep(30)
print("POLL-TIMEOUT", flush=True)
sys.exit(1)
