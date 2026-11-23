#!/usr/bin/env python3
"""Find the ci.yml run on main *immediately before* 0f8ac026 and report its jobs."""
import json
import urllib.request

SHA_NEW = "0f8ac02680d756e526be1a412e808efd238b0a7b"

# Find ci.yml workflow id
wf_url = "https://api.github.com/repos/vamseeachanta/worldenergydata/actions/workflows"
req = urllib.request.Request(wf_url, headers={"Accept": "application/vnd.github+json"})
with urllib.request.urlopen(req, timeout=30) as r:
    wfs = json.load(r).get("workflows", [])
ci_wf = next(w for w in wfs if w["path"].endswith("/ci.yml"))
print(f"ci.yml workflow id = {ci_wf['id']}")

# List last 10 ci.yml runs on main
runs_url = f"https://api.github.com/repos/vamseeachanta/worldenergydata/actions/workflows/{ci_wf['id']}/runs?branch=main&per_page=10"
req = urllib.request.Request(runs_url, headers={"Accept": "application/vnd.github+json"})
with urllib.request.urlopen(req, timeout=30) as r:
    runs = json.load(r).get("workflow_runs", [])

print("\nRecent ci.yml runs on main:")
for r_ in runs:
    print(
        f"  id={r_['id']} sha={r_['head_sha'][:8]} status={r_['status']} conclusion={r_['conclusion']} title={r_['display_title'][:60]}"
    )

# Get the one immediately before my commit (i.e., excluding SHA_NEW)
prior = next((r_ for r_ in runs if r_["head_sha"] != SHA_NEW), None)
if prior is None:
    print("No prior run found")
    raise SystemExit(0)

print(
    f"\nPrior run on main: id={prior['id']} sha={prior['head_sha'][:8]} conclusion={prior['conclusion']}"
)
print(f"URL: {prior['html_url']}")
jobs_url = f"https://api.github.com/repos/vamseeachanta/worldenergydata/actions/runs/{prior['id']}/jobs?per_page=30"
req = urllib.request.Request(jobs_url, headers={"Accept": "application/vnd.github+json"})
with urllib.request.urlopen(req, timeout=30) as r:
    jobs = json.load(r).get("jobs", [])
print("Jobs:")
for j in jobs:
    print(
        f"  {j['name']:<32} conclusion={j['conclusion']:<10} id={j['id']}"
    )
