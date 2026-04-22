#!/usr/bin/env python3
"""Dump job outcomes for a GHA run."""
import json
import sys
import urllib.request

RUN_ID = "24757842396"
URL = f"https://api.github.com/repos/vamseeachanta/worldenergydata/actions/runs/{RUN_ID}/jobs?per_page=30"

req = urllib.request.Request(URL, headers={"Accept": "application/vnd.github+json"})
with urllib.request.urlopen(req, timeout=30) as r:
    data = json.load(r)

for j in data.get("jobs", []):
    print(
        f"{j['name']:<32} status={j['status']:<10} conclusion={j['conclusion']} id={j['id']} url={j['html_url']}"
    )
