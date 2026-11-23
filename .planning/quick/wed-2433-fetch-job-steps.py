#!/usr/bin/env python3
"""Fetch step-level details for one GHA job."""
import json
import sys
import urllib.request

if len(sys.argv) != 2:
    print("usage: wed-2433-fetch-job-steps.py <job_id>")
    sys.exit(2)

job_id = sys.argv[1]
URL = f"https://api.github.com/repos/vamseeachanta/worldenergydata/actions/jobs/{job_id}"
req = urllib.request.Request(URL, headers={"Accept": "application/vnd.github+json"})
with urllib.request.urlopen(req, timeout=30) as r:
    data = json.load(r)

print(f"Job: {data['name']} | status={data['status']} conclusion={data['conclusion']}")
print(f"URL: {data['html_url']}")
print("Steps:")
for s in data.get("steps", []):
    print(
        f"  [{s.get('number'):>2}] {s.get('name'):<55} status={s.get('status'):<10} conclusion={s.get('conclusion')}"
    )
