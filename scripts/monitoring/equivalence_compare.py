#!/usr/bin/env python3
"""equivalence_compare.py — compare per-machine equivalence fingerprints, emit divergences.

Pure logic (no git, no network) so it is unit-testable; the CLI reads a directory
of ``<role>.json`` fingerprints produced by ``equivalence-fingerprint.sh`` and
collected via the ``equivalence-state`` git ref.

Part of the machine-equivalence drift sentinel (#3059, harden-ecosystem epic #3058).
Codifies the manual cross-machine audit performed 2026-06-13.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from datetime import datetime

CRITICAL, WARNING, INFO = "CRITICAL", "WARNING", "INFO"
_SEV_RANK = {CRITICAL: 0, WARNING: 1, INFO: 2}

# Learning-loop crons expected to stay fresh on the orchestration hub (role "full").
# Staleness here means ecosystem learning is silently degrading — the SPOF risk
# surfaced on 2026-06-13 when ace-linux-1 was 14 commits behind unnoticed.
HUB_LEARNING_CRONS = ("comprehensive-learning-nightly", "session-analysis")


def _div(severity: str, code: str, detail: str, boxes: dict) -> dict:
    return {"severity": severity, "code": code, "detail": detail, "boxes": boxes}


def _parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None


def compare(fps, *, behind_warn=10, stale_h=6.0, learning_max_h=48.0):
    """Compare fingerprint dicts; return divergences sorted worst-first.

    A divergence is ``{severity, code, detail, boxes}``. Empty list == equivalent.
    Role-aware: cron *set* differences between roles are expected and NOT flagged;
    only registry/harness equivalence, clone lag, hub-cron freshness, and
    reporting staleness are checked.
    """
    out: list[dict] = []
    if not fps:
        return out
    roles = [f.get("role") or f.get("hostname") or "?" for f in fps]

    # 1. model-registry divergence across boxes -> CRITICAL (config not equivalent)
    reg = {f.get("registry_sha256") for f in fps if f.get("registry_sha256")}
    if len(reg) > 1:
        out.append(_div(CRITICAL, "registry-divergence",
                        "config/agents/model-registry.yaml differs across boxes — model config not equivalent",
                        {r: (f.get("registry_sha256") or "?")[:12] for r, f in zip(roles, fps)}))

    # 2. harness version mismatch -> WARNING
    hv = {f.get("harness_version") for f in fps if f.get("harness_version")}
    if len(hv) > 1:
        out.append(_div(WARNING, "harness-version-mismatch",
                        "claude harness version differs across boxes",
                        {r: f.get("harness_version") for r, f in zip(roles, fps)}))

    # 3. harness install method mismatch -> INFO
    hi = {f.get("harness_install") for f in fps if f.get("harness_install")}
    if len(hi) > 1:
        out.append(_div(INFO, "harness-install-mismatch",
                        "claude install method differs across boxes",
                        {r: f.get("harness_install") for r, f in zip(roles, fps)}))

    # 4. clone behind origin/main -> WARNING (>= behind_warn) or INFO (1..behind_warn-1)
    for r, f in zip(roles, fps):
        b = f.get("behind_origin")
        if isinstance(b, int) and b > 0:
            out.append(_div(WARNING if b >= behind_warn else INFO, "clone-behind-origin",
                            f"{r} clone is {b} commit(s) behind origin/main", {r: b}))

    # 5. hub learning-cron staleness (orchestration SPOF) -> WARNING
    for r, f in zip(roles, fps):
        if f.get("role") != "full":
            continue
        ages = f.get("learning_cron_ages_h") or {}
        for cron in HUB_LEARNING_CRONS:
            age = ages.get(cron)
            if age is None:
                out.append(_div(WARNING, "hub-cron-unknown",
                                f"{r}: learning cron '{cron}' last-run age unknown", {r: cron}))
            elif age > learning_max_h:
                out.append(_div(WARNING, "hub-cron-stale",
                                f"{r}: learning cron '{cron}' last ran {age:.0f}h ago (> {learning_max_h:.0f}h)",
                                {r: round(age, 1)}))

    # 5b. per-provider SOUL.runtime divergence across machines -> WARNING (#3074).
    # Equivalent provider behavior across all machines means each provider's
    # built runtime hash matches box-to-box. Only providers reported by >1 box
    # are checked (a provider absent on a box is handled by hub/role config, not here).
    prov_seen = {}  # provider -> {box: hash}
    for r, f in zip(roles, fps):
        for prov, h in (f.get("provider_soul_hashes") or {}).items():
            if h:
                prov_seen.setdefault(prov, {})[r] = h
    for prov, by_box in sorted(prov_seen.items()):
        if len(by_box) > 1 and len(set(by_box.values())) > 1:
            out.append(_div(WARNING, "provider-soul-divergence",
                            f"provider '{prov}' SOUL.runtime differs across boxes — behavior not equivalent",
                            {b: h[:8] for b, h in by_box.items()}))

    # 6. stale fingerprint (a box stopped reporting) -> WARNING, vs newest ts
    valid = [(r, _parse_ts(f.get("ts"))) for r, f in zip(roles, fps)]
    valid = [(r, t) for r, t in valid if t]
    if len(valid) > 1:
        newest = max(t for _, t in valid)
        for r, t in valid:
            age_h = (newest - t).total_seconds() / 3600.0
            if age_h > stale_h:
                out.append(_div(WARNING, "stale-fingerprint",
                                f"{r} fingerprint is {age_h:.1f}h older than the newest box — may not be reporting",
                                {r: round(age_h, 1)}))

    # 7. primary (role=full) parked off `main` -> WARNING (#3187). Cron scripts run
    # against whatever branch is checked out, so an off-main primary silently serves
    # stale scripts. Off-main is only flagged for role=full (the cron/orchestration
    # hub); secondary boxes legitimately sit on feature branches.
    for r, f in zip(roles, fps):
        if f.get("role") != "full":
            continue
        if f.get("on_main") is False:
            out.append(_div(WARNING, "primary-off-main",
                            f"{r} (orchestration hub) is parked off main — crons run against the wrong tree",
                            {r: "off-main"}))

    # 8. stale .git/index.lock reported -> WARNING (#3187). A zero-byte orphan lock
    # with no holder silently freezes git automation (froze the primary ~5h on
    # 2026-06-17). The fingerprint only sets this when no live git process holds it.
    for r, f in zip(roles, fps):
        age = f.get("index_lock_stale_min")
        if isinstance(age, (int, float)) and not isinstance(age, bool):
            out.append(_div(WARNING, "stale-index-lock",
                            f"{r}: orphan .git/index.lock ~{age:.0f} min old with no holder — git automation may be frozen",
                            {r: round(float(age), 1)}))

    out.sort(key=lambda d: _SEV_RANK[d["severity"]])
    return out


def worst_severity(divs):
    """Return the worst severity present, or None."""
    if not divs:
        return None
    return min((d["severity"] for d in divs), key=lambda s: _SEV_RANK[s])


def load_dir(d):
    fps = []
    for p in sorted(glob.glob(os.path.join(d, "*.json"))):
        try:
            with open(p) as fh:
                fps.append(json.load(fh))
        except (OSError, ValueError) as e:
            print(f"WARN: skip {p}: {e}", file=sys.stderr)
    return fps


def main(argv=None):
    ap = argparse.ArgumentParser(description="Compare machine-equivalence fingerprints")
    ap.add_argument("dir", help="directory of <role>.json fingerprints")
    ap.add_argument("--behind-warn", type=int, default=10)
    ap.add_argument("--stale-h", type=float, default=6.0)
    ap.add_argument("--learning-max-h", type=float, default=48.0)
    ap.add_argument("--json", action="store_true", help="emit JSON")
    a = ap.parse_args(argv)
    fps = load_dir(a.dir)
    divs = compare(fps, behind_warn=a.behind_warn, stale_h=a.stale_h,
                   learning_max_h=a.learning_max_h)
    if a.json:
        print(json.dumps({"boxes": len(fps), "divergences": divs}, indent=2))
    else:
        print(f"equivalence: {len(fps)} box(es), {len(divs)} divergence(s)")
        for d in divs:
            print(f"  [{d['severity']}] {d['code']}: {d['detail']}")
    worst = worst_severity(divs)
    return 2 if worst == CRITICAL else (1 if worst == WARNING else 0)


if __name__ == "__main__":
    sys.exit(main())
