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
  7. re-read and require byte-for-byte equality with the planned crontab.
  8. on mismatch, restore A only after a rollback CAS and verify the restoration.

Default is --dry-run (prints the plan, writes nothing, creates no artifact). --apply commits.
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import importlib.util
import json
import os
import re
import secrets
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CATALOG = REPO / "config" / "scheduled-tasks" / "schedule-tasks.yaml"
STATE_CLASSES = REPO / "config" / "workstations" / "harness-state-classes.yaml"
REGISTRY = REPO / "config" / "workstations" / "registry.yaml"
LOCKFILE = Path.home() / ".cron-reconcile.lock"
BACKUP_DIR = Path(os.environ.get("CRON_BACKUP_DIR", REPO / "logs" / "cron-backups"))

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
build_ownership_context = ct.build_ownership_context

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


def create_backup(machine_id: str, tag: str | None, text: str) -> Path:
    """Atomically create backup content without overwriting recovery evidence."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if tag is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        tag = f"{stamp}-{os.getpid()}-{secrets.token_hex(3)}"
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", tag):
        raise ValueError("backup tag contains unsafe characters")
    path = BACKUP_DIR / f"{machine_id}-{tag}.crontab"
    with path.open("x", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    return path


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


def _state_diagnostics(text: str) -> dict:
    encoded = text.encode("utf-8")
    return {
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "bytes": len(encoded),
        "lines": len(text.splitlines()),
    }


def _transaction_result(status: str, backup: Path, **states: str) -> dict:
    result = {"status": status, "backup": str(backup)}
    result.update({name: _state_diagnostics(text) for name, text in states.items()})
    return result


def _observe_rollback_error(A, C, backup, _read) -> dict:
    try:
        observed = _read()
    except Exception:
        return _transaction_result("rollback-indeterminate", backup, expected=A)
    if observed == A:
        return _transaction_result(
            "rolled-back-with-write-error", backup, expected=A, observed=observed
        )
    status = "rollback-failed" if observed == C else "rollback-aborted"
    return _transaction_result(status, backup, expected=A, observed=observed)


def _rollback(A, C, backup, _read, _write) -> dict:
    with _flock(LOCKFILE):
        try:
            current = _read()
        except Exception:
            return _transaction_result("rollback-indeterminate", backup, expected=A)
        if current != C:
            result = _transaction_result(
                "rollback-aborted", backup, expected=A, observed=current
            )
            result["reason"] = "concurrent crontab change; rollback not attempted"
            return result
        try:
            _write(A)
        except Exception:
            return _observe_rollback_error(A, C, backup, _read)
        try:
            restored = _read()
        except Exception:
            return _transaction_result("rollback-indeterminate", backup, expected=A)
    status = "rolled-back" if restored == A else "rollback-failed"
    return _transaction_result(status, backup, expected=A, observed=restored)


def _write_observation(B, _read, _write) -> tuple[bool, bool, str | None]:
    write_failed = False
    try:
        _write(B)
    except Exception:
        write_failed = True
    try:
        observed = _read()
    except Exception:
        return write_failed, True, None
    return write_failed, False, observed


def _finish_exact(A, B, backup, observation, _read, _write) -> dict:
    write_failed, read_failed, observed = observation
    if read_failed:
        return _transaction_result("verification-indeterminate", backup, expected=B)
    if not write_failed and observed == B:
        return _transaction_result("applied", backup, expected=B, observed=observed)
    if write_failed and observed in (A, B):
        status = "write-failed-no-change" if observed == A else "write-error-state-exact"
        return _transaction_result(status, backup, expected=B, observed=observed)
    result = _rollback(A, observed, backup, _read, _write)
    result["planned"] = _state_diagnostics(B)
    return result


# ── the transaction ──────────────────────────────────────────────────────────
def _load_cutover_context(machine_id):
    catalog = _load(CATALOG)
    classes = _load(STATE_CLASSES)
    registry = _load(REGISTRY)
    selection = _selection_context(catalog, registry, machine_id)
    ownership = build_ownership_context(catalog, registry, classes, machine_id)
    return selection, classes, ownership


def _build_cutover(selection, classes, ownership, _read):
    selected = selection["selected"]
    cat_cmds = _combine_keys(
        ct.catalog_command_keys(selection["selected_raw"], include_fingerprinted=False),
        ct.catalog_command_keys(selected, include_fingerprinted=False),
    )
    baseline = _read()
    plan = ct.plan_cutover(
        baseline,
        selected,
        selection["roles"],
        cat_cmds,
        external_fingerprints(classes),
        selected_task_ids=selection["selected_task_ids"],
        catalog_fingerprints=catalog_fingerprints(selection["selected_raw"]),
        ownership_context=ownership,
    )
    return baseline, plan


def run_cutover(machine_id: str, apply: bool, ts: str | None,
                _read=read_crontab, _write=write_crontab,
                _daemons=None, allow_live_reload: bool = False) -> dict:
    selection, classes, ownership = _load_cutover_context(machine_id)
    canonical_id = selection["machine_id"]
    roles = selection["roles"]
    selected = selection["selected"]
    conflicts = selection["conflicts"]
    if not roles and not selected:
        return {"status": "skip", "reason": f"{canonical_id} has no harness_profile.roles or machine-pinned cron tasks"}
    A, plan = _build_cutover(selection, classes, ownership, _read)
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

    # Hold an exclusive process lock across the read→write critical section so a concurrent
    # cron-apply / setup-cron cannot interleave (#2969 code-review MAJOR #2). A writer that
    # does NOT honor the lock (e.g. deckhand) is still caught by the compare-and-swap below.
    with _flock(LOCKFILE):
        current = _read()                         # re-read UNDER the lock (CAS baseline)
        if current != A:                          # changed since we planned → plan is stale
            return {"status": "abort",
                    "reason": "crontab changed during cutover (CAS) — re-run", "backup": None}
        backup = create_backup(canonical_id, ts, A)
        observation = _write_observation(plan["new_text"], _read, _write)
    transaction = _finish_exact(
        A, plan["new_text"], backup, observation, _read, _write
    )
    result.update(transaction)
    return result


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="transactional crontab cutover (#2969)")
    ap.add_argument("--apply", action="store_true", help="commit (default: dry-run)")
    ap.add_argument("--allow-live-reload", action="store_true")
    ap.add_argument("--machine", default=None)
    ap.add_argument("--ts", default=None, help="optional unique backup tag")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    host = args.machine or socket.gethostname().split(".")[0]
    registry = _load(REGISTRY)
    mid = cr.build_context(host, registry=registry)["machine_id"]
    physical_host = socket.gethostname().split(".")[0]
    physical_mid = cr.build_context(physical_host, registry=registry)["machine_id"]
    if mid != physical_mid:
        res = {
            "status": "abort",
            "reason": f"refusing local crontab reconciliation for remote machine {mid}",
            "machine": mid,
        }
        print(json.dumps(res, indent=2) if args.json else f"cron-apply {mid}: abort — {res['reason']}")
        return 2
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
