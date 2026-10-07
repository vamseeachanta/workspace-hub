#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""harness_reconcile.py — role-overlay harness reconciler (#2968, F1 of epic #2967).

Converges a *managed* machine's role-managed harness surface (user-settings policy
keys, hooks, skill families) to `git base + (_base ∪ its role overlays)`.

Design (per approved plan + Codex MAJOR fold):
- COMPOSABLE roles: a machine declares `harness_profile.roles: [...]`; applied
  overlay = `_base ∪ role₁ ∪ role₂ …` (Q1).
- `managed: false` hosts (e.g. licensed-win, declared for F3 routing) are SKIPPED —
  the reconciler never writes to them (Q2).
- PURELY ADDITIVE, identity-keyed merges — never removes a local entry:
    * `permissions.deny` (list[str])  → sorted(set(local) ∪ set(required))
    * `hooks` (event → [groups])      → union by (event, type, command) identity;
      a same-identity hook with a different non-identity field FAILS CLOSED.
    * scalar keys                     → set to required unless in intentionally-divergent.
- Idempotent: a second `--apply` yields a byte-identical settings.json.
- Fail-closed on overlay key-conflict and on `uncataloged-live` items.
- Live-session gating: `--apply` refuses on a comms host with active daemons when the
  hook surface would change, unless `--allow-live-reload`.

The core functions are PURE (dict in / dict out) so they are unit-testable with
fixtures; the CLI (`main`) does the file IO and daemon probe.
"""
from __future__ import annotations

import argparse
import copy
import json
import socket
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - declared in PEP-723 block above
    yaml = None

REPO = Path(__file__).resolve().parents[2]
ROLES_CFG = REPO / "config" / "workstations" / "harness-roles.yaml"
REGISTRY = REPO / "config" / "workstations" / "registry.yaml"
STATE_CLASSES = REPO / "config" / "workstations" / "harness-state-classes.yaml"
SETTINGS = Path.home() / ".claude" / "settings.json"

# daemons whose presence makes a host "live" for hook-surface changes
LIVE_DAEMON_PATTERNS = ["hermes_cli.main gateway", "whatsapp-bridge", "deckhand"]


class ReconcileError(Exception):
    """Fail-closed reconciler error."""


# ── role composition (Q1) ────────────────────────────────────────────────────
def hook_identity(event: str, hook: dict) -> tuple:
    return (event, hook.get("type"), hook.get("command"))


def merge_deny(local: list[str], required: list[str]) -> list[str]:
    """Set-union + dedup + lexical sort. Never drops a local rule (additive)."""
    return sorted(set(local or []) | set(required or []))


def merge_hooks(local: dict, required: dict) -> dict:
    """Union hook groups by (event, type, command). Same identity with a divergent
    non-identity field fails closed. Stable order: required-canonical, then local."""
    out: dict[str, list] = {}
    for event in list(required or {}) + [e for e in (local or {}) if e not in (required or {})]:
        seen: dict[tuple, dict] = {}
        order: list[tuple] = []
        for src in (required.get(event, []), (local or {}).get(event, [])):
            for group in src:
                for hook in group.get("hooks", [group]):
                    ident = hook_identity(event, hook)
                    if ident in seen:
                        if seen[ident] != hook:
                            raise ReconcileError(
                                f"hook conflict for {ident}: {seen[ident]} != {hook} (fail-closed)")
                        continue
                    seen[ident] = hook
                    order.append(ident)
        out[event] = [{"hooks": [seen[i]]} for i in order]
    return out


def compose_overlay(roles_cfg: dict, role_names: list[str], machine_os: str | None = None) -> dict:
    """_base ∪ role₁ ∪ role₂…  Scalar key present in 2 overlays with different values
    fails closed (no last-writer-wins). Lists (skill_families, schedule_jobs, deny)
    are set-unioned.

    WF1 #2999: `_base.deny_required_os` is an {os: [deny…]} map. The subset matching
    `machine_os` is set-unioned into `deny_required`, then the map is popped (config-only —
    apply_overlay/compute_drift never read it). `machine_os=None` adds no OS subset.
    """
    roles = roles_cfg.get("roles", {})
    chain = ["_base"] + [r for r in role_names if r != "_base"]
    merged: dict = {}
    for name in chain:
        ov = roles.get(name)
        if ov is None:
            raise ReconcileError(f"unknown role: {name}")
        for k, v in ov.items():
            if k not in merged:
                merged[k] = copy.deepcopy(v)
            elif isinstance(v, list) and isinstance(merged[k], list):
                merged[k] = sorted(set(merged[k]) | set(v))
            elif isinstance(v, dict) and isinstance(merged[k], dict):
                # merge key-by-key; a shared inner key with a different value fails
                # closed (no silent last-writer-wins — the Codex MAJOR class).
                for ik, iv in v.items():
                    if ik in merged[k] and merged[k][ik] != iv:
                        raise ReconcileError(
                            f"overlay key conflict '{k}.{ik}': "
                            f"{merged[k][ik]!r} vs {name}:{iv!r} (fail-closed)")
                    merged[k][ik] = iv
            elif merged[k] != v:
                raise ReconcileError(
                    f"overlay key conflict '{k}': {merged[k]!r} vs {name}:{v!r} (fail-closed)")
    # WF1: resolve the per-OS deny subset, then drop the config-only map.
    os_map = merged.pop("deny_required_os", None)
    if os_map and machine_os:
        subset = os_map.get(machine_os, [])
        merged["deny_required"] = sorted(set(merged.get("deny_required", [])) | set(subset))
    return merged


# ── drift + apply ─────────────────────────────────────────────────────────────
def is_managed(profile: dict | None) -> bool:
    return bool(profile and profile.get("managed") is True)


def resolve_machine_id(machines: dict, host: str) -> str | None:
    """Resolve a hostname to its registry key via the canonical idiom: match the key,
    hostname, OR hostname_aliases (case-insensitive — Windows hostnames are often
    reported upper-case, e.g. an ACE-WIN-1 alias must still resolve to ace-win-1).
    WF1 #2999: without alias resolution the reconciler can't identify a Windows host
    whose real OS hostname is declared only as a hostname_aliases entry."""
    h = host.lower()
    for mid, e in machines.items():
        cands = [mid, e.get("hostname", "")] + list(e.get("hostname_aliases") or [])
        cands = [str(c).lower() for c in cands if c]
        if h in cands or any(c and c.startswith(h) for c in [str(e.get("hostname", "")).lower()]):
            return mid
    return None


def compute_drift(current: dict, overlay: dict) -> list[dict]:
    """Return list of {key, current, expected} the overlay would change. Additive:
    only reports keys the overlay requires; never proposes removals."""
    drift = []
    # deny
    req_deny = overlay.get("deny_required", [])
    if req_deny:
        merged = merge_deny(((current.get("permissions") or {}).get("deny")), req_deny)
        cur = sorted(set(((current.get("permissions") or {}).get("deny")) or []))
        if merged != cur:
            drift.append({"key": "permissions.deny", "current": cur, "expected": merged})
    # hooks
    req_hooks = overlay.get("hooks_required", {})
    if req_hooks:
        merged = merge_hooks(current.get("hooks", {}), req_hooks)
        if merged != current.get("hooks", {}):
            drift.append({"key": "hooks", "current": current.get("hooks", {}), "expected": merged})
    # scalar required keys
    for key in overlay.get("scalar_required", {}):
        want = overlay["scalar_required"][key]
        have = current.get(key)
        if have != want:
            drift.append({"key": key, "current": have, "expected": want})
    return drift


def apply_overlay(current: dict, overlay: dict) -> dict:
    """Return a NEW settings dict with the overlay merged in (additive, deterministic).
    Unknown local keys preserved."""
    out = copy.deepcopy(current)
    req_deny = overlay.get("deny_required", [])
    if req_deny:
        perms = out.setdefault("permissions", {})
        perms["deny"] = merge_deny(perms.get("deny"), req_deny)
    req_hooks = overlay.get("hooks_required", {})
    if req_hooks:
        out["hooks"] = merge_hooks(out.get("hooks", {}), req_hooks)
    for key, want in overlay.get("scalar_required", {}).items():
        out[key] = want
    return out


def find_uncataloged_live(current: dict, state_classes: dict) -> list[str]:
    """A hook present locally whose identity is in no class is 'uncataloged-live' and
    BLOCKS --apply until classified."""
    known = state_classes.get("hooks_known") or []

    def _is_known(event: str, hook: dict) -> bool:
        # A catalog entry matches on event + (exact command OR any command_contains
        # substring). The substring form keeps the catalog portable across machines
        # whose hook commands carry absolute paths (epic #2967 path-portability hazard).
        cmd = hook.get("command") or ""
        for e in known:
            if e.get("event") not in (None, event):
                continue
            if e.get("command") is not None and e["command"] == cmd:
                return True
            subs = e.get("command_contains")
            if subs and any(s in cmd for s in (subs if isinstance(subs, list) else [subs])):
                return True
        return False

    flagged = []
    for event, groups in (current.get("hooks") or {}).items():
        for group in groups:
            for hook in group.get("hooks", [group]):
                if not _is_known(event, hook):
                    flagged.append(f"{hook_identity(event, hook)}")
    return flagged


def overlay_changes_hooks(current: dict, overlay: dict) -> bool:
    return any(d["key"] == "hooks" for d in compute_drift(current, overlay))


# ── live-session gating (Codex MAJOR #1) ─────────────────────────────────────
def detect_live_daemons(pgrep_fn=None) -> list[str]:
    def _default(pat):
        try:
            return subprocess.run(["pgrep", "-f", pat], capture_output=True).returncode == 0
        except (FileNotFoundError, OSError):
            return False  # WF1: no pgrep (Windows/Git-Bash) → treat as no live daemon
    probe = pgrep_fn or _default
    out = []
    for p in LIVE_DAEMON_PATTERNS:
        try:
            if probe(p):
                out.append(p)
        except (FileNotFoundError, OSError):
            continue  # a probe that cannot run is not evidence of a live daemon
    return out


def should_block_apply(daemons_active: bool, changes_hooks: bool, allow_live_reload: bool) -> bool:
    """Refuse a hot hook-surface change on a live comms host unless explicitly allowed."""
    return daemons_active and changes_hooks and not allow_live_reload


# ── canonical serialization (idempotency) ────────────────────────────────────
def serialize(settings: dict) -> str:
    """Byte-stable: sorted keys, sorted deny array. Second apply == first."""
    s = copy.deepcopy(settings)
    if "permissions" in s and "deny" in (s["permissions"] or {}):
        s["permissions"]["deny"] = sorted(set(s["permissions"]["deny"]))
    return json.dumps(s, indent=2, sort_keys=True) + "\n"


# ── CLI ──────────────────────────────────────────────────────────────────────
def _load_yaml(p: Path) -> dict:
    if yaml is None:
        raise ReconcileError(
            "pyyaml unavailable — run via `uv run --script`, or on Windows/Git-Bash "
            "(no uv) `python -m pip install pyyaml` then `python harness_reconcile.py`")
    return yaml.safe_load(p.read_text()) if p.exists() else {}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="role-overlay harness reconciler (#2968)")
    ap.add_argument("--apply", action="store_true", help="converge (default: dry-run)")
    ap.add_argument("--allow-live-reload", action="store_true",
                    help="permit hook-surface change on a live comms host")
    ap.add_argument("--machine", default=None, help="override machine id (default: hostname)")
    args = ap.parse_args(argv)

    roles_cfg = _load_yaml(ROLES_CFG)
    registry = _load_yaml(REGISTRY)
    state_classes = _load_yaml(STATE_CLASSES)
    machines = registry.get("machines", {})
    host = args.machine or socket.gethostname().split(".")[0]
    mid = resolve_machine_id(machines, host)
    if mid is None:
        print(f"harness-reconcile: machine '{host}' not in registry — skipping", file=sys.stderr)
        return 0
    profile = machines[mid].get("harness_profile")
    if not is_managed(profile):
        print(f"harness-reconcile: {mid} is declare-only (managed!=true) — routing only, no write")
        return 0

    overlay = compose_overlay(roles_cfg, profile.get("roles", []),
                              machine_os=machines[mid].get("os"))
    current = json.loads(SETTINGS.read_text()) if SETTINGS.exists() else {}
    drift = compute_drift(current, overlay)
    uncat = find_uncataloged_live(current, state_classes)

    print(f"--- harness-reconcile {mid} roles={profile.get('roles')} ---")
    for d in drift:
        print(f"  DRIFT {d['key']}")
    if uncat:
        print(f"  UNCATALOGED-LIVE (blocks --apply): {uncat}")
    if not args.apply:
        print(f"  [dry-run] {len(drift)} drift item(s); writes nothing")
        return 0

    if uncat:
        print("  REFUSED: uncataloged-live items must be classified first", file=sys.stderr)
        return 2
    if should_block_apply(bool(detect_live_daemons()), overlay_changes_hooks(current, overlay),
                          args.allow_live_reload):
        print("  REFUSED: live comms daemons active + hook change; pass --allow-live-reload",
              file=sys.stderr)
        return 2

    new = apply_overlay(current, overlay)
    SETTINGS.with_suffix(".json.bak").write_text(serialize(current))
    SETTINGS.write_text(serialize(new))
    # idempotency self-check
    if compute_drift(json.loads(SETTINGS.read_text()), overlay):
        raise ReconcileError("post-apply drift non-empty — not idempotent (fail-closed)")
    print(f"  applied; backup at {SETTINGS.with_suffix('.json.bak')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
