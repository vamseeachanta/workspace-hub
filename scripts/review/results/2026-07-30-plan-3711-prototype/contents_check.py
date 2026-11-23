#!/usr/bin/env python3
"""PROPOSED enforcement contents check, prototyped against a repo's git INDEX.

Regenerates the identity rows from index bytes with the lexical (host-independent)
render and compares them to the inventory blob in the same index.
Exit 0 = accept, 1 = reject.  Read-only.
"""
import importlib.util, json, os, subprocess, sys
from pathlib import Path, PurePosixPath

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / "scripts/cron"))
spec = importlib.util.spec_from_file_location("bcii", root / "scripts/cron/build-cron-identity-inventory.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
import cron_render, yaml

cron_render.workspace_hub_path = lambda wh=None: (
    PurePosixPath(os.path.normpath(str(wh or os.environ.get("WORKSPACE_HUB"))))
    if (wh or os.environ.get("WORKSPACE_HUB")) else cron_render.REPO_ROOT)

def blob(rel):
    return subprocess.run(["git", "cat-file", "blob", f":{rel}"], cwd=root,
                          check=True, capture_output=True).stdout

catalog = yaml.safe_load(blob("config/scheduled-tasks/schedule-tasks.yaml"))
registry = yaml.safe_load(blob("config/workstations/registry.yaml"))
classes = yaml.safe_load(blob("config/workstations/harness-state-classes.yaml"))
committed = json.loads(blob("docs/reports/issue-3475-command-identity-inventory.json"))

machines = sorted(m for m, r in (registry.get("machines") or {}).items() if r.get("os") == "linux")
rows, unsupported, collisions, bound = [], [], [], set()
for mid in machines:
    mod._build_machine(catalog, registry, classes, mid, rows, unsupported, collisions, bound)

ok = rows == committed["identities"] and machines == committed["machines"]
bad = [(r["machine_id"], r["task_id"]) for r in committed["identities"] if r not in rows]
print(f"regenerated={len(rows)} committed={len(committed['identities'])} contents_match={ok}")
if bad:
    print(f"REJECT: identity inventory rows do not match a host-independent regeneration: {sorted(bad)}")
sys.exit(0 if ok else 1)
