#!/usr/bin/env python3
"""Fetch plaintext log for a specific GHA job."""
import sys
import urllib.request

if len(sys.argv) != 2:
    print("usage: wed-2433-fetch-joblog.py <job_id>")
    sys.exit(2)

job_id = sys.argv[1]
URL = f"https://api.github.com/repos/vamseeachanta/worldenergydata/actions/jobs/{job_id}/logs"
req = urllib.request.Request(URL, headers={"Accept": "application/vnd.github+json"})
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", errors="replace"))
