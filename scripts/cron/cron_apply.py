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
_render_spec = importlib.util.spec_from_file_location(
    "cron_render", REPO / "scripts" / "cron" / "cron_render.py")
cr = importlib.util.module_from_spec(_render_spec)
sys.modules["cron_render"] = cr
_render_spec.loader.exec_module(cr)

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


def _combine_keys(*groups: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for key in group:
            if key and key not in seen:
                out.append(key)
                seen.add(key)
    return out


def _selection_context(catalog: dict, registry: dict, machine_id: str) -> dict:
    context = cr.build_context(machine_id, registry=registry)
    canonical_id = context["machine_id"]
    roles = machine_roles(registry, canonical_id)
    selected_raw, conflicts = ct.select_tasks(
        catalog.get("tasks", []) or [],
        roles,
        context.get("tokens", {canonical_id}),
    )
    rendered = [cr.render_task(task, context) for task in selected_raw]
    selected_ids = {task.get("id") for task in selected_raw if task.get("id")}
    return {
        "context": context,
        "machine_id": canonical_id,
        "roles": roles,
        "selected_raw": selected_raw,
        "selected": rendered,
        "selected_task_ids": selected_ids,
        "conflicts": conflicts,
    }


def catalog_commands(
    catalog: dict,
    registry: dict | None = None,
    machine_id: str | None = None,
) -> list[str]:
    if registry is None or machine_id is None:
        return ct.catalog_command_keys(
            catalog.get("tasks", []) or [], include_fingerprinted=False
        )
    selection = _selection_context(catalog, registry, machine_id)
    return _combine_keys(
        ct.catalog_command_keys(selection["selected_raw"], include_fingerprinted=False),
        ct.catalog_command_keys(selection["selected"], include_fingerprinted=False),
    )


def catalog_fingerprints(tasks: list[dict]) -> list[dict]:
    return ct.catalog_owned_fingerprints(tasks)


def external_fingerprints(state_classes: dict) -> list[dict]:
    # preserved_external (other-repo-owned, e.g. deckhand) + preserved_local (this host's
    # own non-catalog workspace-hub crons, #2988) — both are the keep-verbatim bucket.
    entries = (state_classes.get("preserved_external") or []) + \
              (state_classes.get("preserved_local") or [])
    return ct.normalize_preserved_entries(entries)


# ── the transaction ──────────────────────────────────────────────────────────
def run_cutover(machine_id: str, apply: bool, ts: str,
                _read=read_crontab, _write=write_crontab,
                _daemons=None, allow_live_reload: bool = False) -> dict:
    catalog = _load(CATALOG)
    classes = _load(STATE_CLASSES)
    registry = _load(REGISTRY)
    selection = _selection_context(catalog, registry, machine_id)
    canonical_id = selection["machine_id"]
    roles = selection["roles"]
    selected = selection["selected"]
    selected_ids = selection["selected_task_ids"]
    conflicts = selection["conflicts"]
    if not roles and not selected:
        return {"status": "skip", "reason": f"{canonical_id} has no harness_profile.roles or machine-pinned cron tasks"}

    cat_cmds = _combine_keys(
        ct.catalog_command_keys(selection["selected_raw"], include_fingerprinted=False),
        ct.catalog_command_keys(selected, include_fingerprinted=False),
    )
    cat_fps = catalog_fingerprints(selection["selected_raw"])
    ext_fps = external_fingerprints(classes)

    A = _read()
    plan = ct.plan_cutover(
        A,
        selected,
        roles,
        cat_cmds,
        ext_fps,
        selected_task_ids=selected_ids,
        catalog_fingerprints=cat_fps,
    )
    if plan.get("abort_reason"):
        return {"status": "abort", "reason": plan["abort_reason"],
                "uncataloged": plan.get("uncataloged", []), "conflicts": conflicts,
                "machine": canonical_id}

    result = {"status": "planned", "preserved": plan.get("preserved", []),
              "conflicts": conflicts, "selected": [t["id"] for t in selected],
              "machine": canonical_id}
    if not apply:
        result["status"] = "dry-run"
        result["new_text"] = plan["new_text"]
        return result

    # live-comms gate: refuse hot change on a host running comms daemons unless allowed
    daemons = ct_detect(_daemons) if _daemons is not None else detect_comms_daemons()
    if daemons and not allow_live_reload:
        return {"status": "abort", "reason": f"live comms daemons {daemons} — pass --allow-live-reload"}

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup = BACKUP_DIR / f"{canonical_id}-{ts}.crontab"

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
                   and ct.classify_line_detail(
                       ln,
                       cat_cmds,
                       ext_fps,
                       selected_task_ids=selected_ids,
                       catalog_fingerprints=cat_fps,
                   )["class"] in ("preserved_external", "ignore"))
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
    mid = cr.build_context(host, registry=registry)["machine_id"]
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
