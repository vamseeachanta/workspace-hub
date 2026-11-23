#!/usr/bin/env python3
"""Issue #3711 prototype, sections E and F (headline test + declared-root guard).

E. Inject a FAKE macOS /home-firmlink resolver on ANY host, regenerate the whole
   identity inventory, and compare with the committed Linux-rendered baseline.
   This is the headline regression test in a CI-runnable form: no Mac required.
F. Show that a '~'-declared workspace_root is silently host-expanded today
   (exit 0, wrong rows) and would be a loud refusal under the proposed guard.
Read-only.  Usage: python proto_ef.py <repo-root>
"""
from __future__ import annotations
import importlib.util, json, os, platform, sys
from pathlib import Path, PurePosixPath

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / "scripts/cron"))
spec = importlib.util.spec_from_file_location("bcii", root / "scripts/cron/build-cron-identity-inventory.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
import cron_render, yaml

committed = (root / "docs/reports/issue-3475-command-identity-inventory.json").read_bytes()
print(f"=== host={platform.system()} node={platform.node()} ===")

# ---- E: fake macOS firmlink resolver -------------------------------------
_MAC_FIRMLINK = "/System/Volumes/Data"

def fake_darwin_resolve(self):
    """Reproduce the measured macOS behaviour: /home/X -> /System/Volumes/Data/home/X."""
    text = str(self)
    if text == "/home" or text.startswith("/home/"):
        return Path(_MAC_FIRMLINK + text)
    return Path(os.path.normpath(text))

def generate():
    return mod.render(mod.build(mod.DEFAULT_CATALOG, mod.DEFAULT_REGISTRY, mod.DEFAULT_CLASSES))

saved_resolve = Path.resolve
Path.resolve = fake_darwin_resolve
try:
    today_faked = generate()
finally:
    Path.resolve = saved_resolve
print(f"[E] today, fake-Darwin resolver: generated == committed baseline -> {today_faked == committed}")
tj, cj = json.loads(today_faked), json.loads(committed)
print(f"[E] today, fake-Darwin resolver: rows differing -> "
      f"{sorted((r['machine_id'], r['task_id']) for r in tj['identities'] if r not in cj['identities'])}")
print(f"[E] today, fake-Darwin resolver: input_digest still matches -> "
      f"{tj['input_digest'] == cj['input_digest']}")

lexical = lambda wh=None: (PurePosixPath(os.path.normpath(str(wh))) if wh else cron_render.REPO_ROOT)
saved_whp, cron_render.workspace_hub_path = cron_render.workspace_hub_path, lexical
Path.resolve = fake_darwin_resolve
try:
    fixed_faked = generate()
finally:
    Path.resolve = saved_resolve
    cron_render.workspace_hub_path = saved_whp
print(f"[E] PROPOSED, fake-Darwin resolver: generated == committed baseline -> {fixed_faked == committed}")

# ---- F: a '~'-declared workspace_root ------------------------------------
registry = yaml.safe_load((root / "config/workstations/registry.yaml").read_text())
tilde = json.loads(json.dumps(registry))
tilde["machines"]["gpu-claw"]["workspace_root"] = "~/ws/workspace-hub"
declared = tilde["machines"]["gpu-claw"]["workspace_root"]
try:
    today_val = str(cron_render.workspace_hub_path(declared))
except Exception as exc:
    today_val = f"<{type(exc).__name__}: {exc}>"
print(f"[F] declared={declared}")
print(f"[F] today workspace_hub_path -> {today_val}   faithful={today_val == declared}")
print(f"[F] today: silently host-expanded, no error raised -> {today_val != declared}")

def unfaithful_declared_roots(reg):
    bad = []
    for mid, row in sorted((reg.get("machines") or {}).items()):
        if (row or {}).get("os") != "linux":
            continue
        d = (row or {}).get("workspace_root")
        if d is None:
            continue
        t = str(d)
        if not t.startswith("/"):
            bad.append((mid, t, "workspace_root is not an absolute POSIX path"))
        elif str(PurePosixPath(os.path.normpath(t))) != t:
            bad.append((mid, t, "workspace_root is not in normal form"))
    return bad

print(f"[F] PROPOSED guard -> {unfaithful_declared_roots(tilde)}")
print(f"[F] PROPOSED guard on the real registry -> {unfaithful_declared_roots(registry)}")
tu = json.loads(json.dumps(registry))
tu["machines"]["gpu-claw"]["workspace_root"] = "~undi/ws/workspace-hub"
try:
    v = str(cron_render.workspace_hub_path("~undi/ws/workspace-hub"))
except Exception as exc:
    v = f"<{type(exc).__name__}: {exc}>"
print(f"[F] today, ~user-declared root -> {v}")
print(f"[F] PROPOSED guard, ~user-declared root -> {unfaithful_declared_roots(tu)}")
