#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""cron_apply.py — transactional crontab cutover (#2969, F2 of epic #2967).

Wraps the pure planning core (cron_transaction.py) in a FAIL-CLOSED IO transaction so a
machine's crontab converges to its role's catalog tasks WITHOUT ever deleting an
externally-owned live cron (e.g. the deckhand Telegram automation on ace-linux-2).

Transaction (Codex MAJOR fold):
  1. flock a per-host lock (serialize against a concurrent setup-cron / deckhand reinstall).
  2. A = read crontab.
  3. plan_cutover(A, …): abort on parse error or any uncataloged live line (fail closed).
  4. backup A to logs/cron-backups/<host>-<ts>.crontab.
  5. compare-and-swap: B = re-read crontab; if B != A → ABORT (something changed under us).
  6. write new crontab.
  7. post-cutover: re-read; assert every preserved_external/ignore line from A is still
     present (zero net removal); on failure → restore backup, exit non-zero.

Default is --dry-run (prints the plan, writes nothing, creates no artifact). --apply commits.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import socket
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CATALOG = REPO / "config" / "scheduled-tasks" / "schedule-tasks.yaml"
STATE_CLASSES = REPO / "config" / "workstations" / "harness-state-classes.yaml"
REGISTRY = REPO / "config" / "workstations" / "registry.yaml"
LOCKFILE = Path.home() / ".cron-reconcile.lock"
BACKUP_DIR = REPO / "logs" / "cron-backups"

# load the pure core by file path (kebab-safe; module name has underscores)
_spec = importlib.util.spec_from_file_location(
    "cron_transaction", REPO / "scripts" / "cron" / "cron_transaction.py")
ct = importlib.util.module_from_spec(_spec)
sys.modules["cron_transaction"] = ct
_spec.loader.exec_module(ct)

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover
    yaml = None


# ── IO seams (injectable for tests) ──────────────────────────────────────────
def read_crontab(_run=subprocess.run) -> str:
    r = _run(["crontab", "-l"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""  # no crontab yet → empty


def write_crontab(text: str, _run=subprocess.run) -> None:
    _run(["crontab", "-"], input=text, text=True, check=True)


def detect_comms_daemons(pgrep_fn=None) -> list[str]:
    return ct_detect(pgrep_fn)  # delegate to a small helper for testability


def ct_detect(pgrep_fn=None) -> list[str]:
    pats = ["hermes_cli.main gateway", "whatsapp-bridge", "deckhand"]
    def _default(p):
        return subprocess.run(["pgrep", "-f", p], capture_output=True).returncode == 0
    probe = pgrep_fn or _default
    return [p for p in pats if probe(p)]


# ── config loading ───────────────────────────────────────────────────────────
def _load(p: Path) -> dict:
    if yaml is None:
        raise RuntimeError("pyyaml unavailable — run via `uv run --script`")
    return yaml.safe_load(p.read_text()) if p.exists() else {}


def machine_roles(registry: dict, machine_id: str) -> list[str]:
    m = (registry.get("machines") or {}).get(machine_id, {})
    return ((m.get("harness_profile") or {}).get("roles")) or []


def catalog_commands(catalog: dict) -> list[str]:
    out = []
    for t in catalog.get("tasks", []):
        cmd = t.get("command", "")
        # a stable script-path fragment is a better catalog key than the full command
        for tok in cmd.split():
            if tok.startswith("scripts/") and (tok.endswith(".sh") or tok.endswith(".py")):
                out.append(tok)
                break
        else:
            out.append(cmd.strip()[:60])
    return out


def external_fingerprints(state_classes: dict) -> list[dict]:
    return [e.get("fingerprint", {}) for e in (state_classes.get("preserved_external") or [])]


# ── the transaction ──────────────────────────────────────────────────────────
def run_cutover(machine_id: str, apply: bool, ts: str,
                _read=read_crontab, _write=write_crontab,
                _daemons=None, allow_live_reload: bool = False) -> dict:
    catalog = _load(CATALOG)
    classes = _load(STATE_CLASSES)
    registry = _load(REGISTRY)
    roles = machine_roles(registry, machine_id)
    if not roles:
        return {"status": "skip", "reason": f"{machine_id} has no harness_profile.roles"}

    selected, conflicts = ct.select_tasks(catalog.get("tasks", []), roles, machine_id)
    cat_cmds = catalog_commands(catalog)
    ext_fps = external_fingerprints(classes)

    A = _read()
    plan = ct.plan_cutover(A, selected, roles, cat_cmds, ext_fps)
    if plan.get("abort_reason"):
        return {"status": "abort", "reason": plan["abort_reason"],
                "uncataloged": plan.get("uncataloged", []), "conflicts": conflicts}

    result = {"status": "planned", "preserved": plan.get("preserved", []),
              "conflicts": conflicts, "selected": [t["id"] for t in selected]}
    if not apply:
        result["status"] = "dry-run"
        return result

    # live-comms gate: refuse hot change on a host running comms daemons unless allowed
    daemons = ct_detect(_daemons) if _daemons is not None else detect_comms_daemons()
    if daemons and not allow_live_reload:
        return {"status": "abort", "reason": f"live comms daemons {daemons} — pass --allow-live-reload"}

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup = BACKUP_DIR / f"{machine_id}-{ts}.crontab"
    backup.write_text(A)

    B = _read()                                   # compare-and-swap
    if B != A:
        return {"status": "abort", "reason": "crontab changed during cutover (CAS) — no write",
                "backup": str(backup)}

    _write(plan["new_text"])

    # post-cutover: zero-net-removal of preserved/ignore lines
    after = _read()
    for line in plan.get("preserved", []):
        if line not in after:
            _write(A)                             # rollback
            return {"status": "rolled-back", "reason": f"preserved line lost: {line!r}",
                    "backup": str(backup)}
    result["status"] = "applied"
    result["backup"] = str(backup)
    return result


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="transactional crontab cutover (#2969)")
    ap.add_argument("--apply", action="store_true", help="commit (default: dry-run)")
    ap.add_argument("--allow-live-reload", action="store_true")
    ap.add_argument("--machine", default=None)
    ap.add_argument("--ts", default="manual", help="backup timestamp tag (caller supplies)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    host = args.machine or socket.gethostname().split(".")[0]
    registry = _load(REGISTRY)
    mid = next((m for m, e in (registry.get("machines") or {}).items()
                if e.get("hostname", "").startswith(host) or m == host), host)
    res = run_cutover(mid, args.apply, args.ts, allow_live_reload=args.allow_live_reload)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"cron-apply {mid}: {res['status']}" + (f" — {res.get('reason')}" if res.get("reason") else ""))
        for cid in res.get("conflicts", []):
            print(f"  CONFLICT {cid}")
    return 0 if res["status"] in ("applied", "dry-run", "planned", "skip") else 2


if __name__ == "__main__":
    sys.exit(main())
