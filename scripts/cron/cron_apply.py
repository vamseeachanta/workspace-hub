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
import contextlib
import fcntl
import importlib.util
import json
import socket
import subprocess
import sys
from collections import Counter
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


# ── process lock (real flock — #2969 code-review MAJOR #2) ───────────────────
@contextlib.contextmanager
def _flock(path: Path):
    """Exclusive advisory lock held for the read→write critical section."""
    path.parent.mkdir(parents=True, exist_ok=True)
    f = open(path, "w")
    try:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        f.close()


# ── IO seams (injectable for tests) ──────────────────────────────────────────
class CronReadError(RuntimeError):
    """crontab -l failed for a reason OTHER than 'no crontab' — fail closed."""


def read_crontab(_run=subprocess.run) -> str:
    r = _run(["crontab", "-l"], capture_output=True, text=True)
    if r.returncode == 0:
        return r.stdout
    # `crontab -l` exits non-zero in TWO very different cases:
    #   (a) the user has no crontab yet  → legitimately empty, safe to proceed
    #   (b) a real error (permissions, crond down, command missing) → MUST NOT be
    #       treated as empty, or backup/rollback would write an empty crontab (#2969
    #       code-review MAJOR #2). Distinguish by stderr and FAIL CLOSED on (b).
    err = (r.stderr or "").lower()
    if "no crontab" in err:
        return ""
    raise CronReadError(f"crontab -l failed (rc={r.returncode}): {r.stderr.strip()!r}")


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

    # Hold an exclusive process lock across the read→write critical section so a concurrent
    # cron-apply / setup-cron cannot interleave (#2969 code-review MAJOR #2). A writer that
    # does NOT honor the lock (e.g. deckhand) is still caught by the compare-and-swap below.
    with _flock(LOCKFILE):
        current = _read()                         # re-read UNDER the lock (CAS baseline)
        if current != A:                          # changed since we planned → plan is stale
            return {"status": "abort",
                    "reason": "crontab changed during cutover (CAS) — re-run", "backup": None}
        backup.write_text(A)                       # A is verified-intact (read succeeded)
        _write(plan["new_text"])
        after = _read()

    # post-cutover: every preserved/ignore line present BEFORE must still be present, by
    # LINE IDENTITY + multiplicity, not substring (#2969 code-review MAJOR #4).
    after_counts = Counter(after.splitlines())
    need = Counter(ln for ln in A.splitlines()
                   if ln.strip()
                   and ct.classify_line(ln, cat_cmds, ext_fps) in ("preserved_external", "ignore"))
    for line, n in need.items():
        if after_counts[line] < n:
            with _flock(LOCKFILE):
                _write(A)                          # rollback to verified-intact A
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
