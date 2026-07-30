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


def _parse_registry_minimal(text):
    """No-pyyaml fallback for the registry: extracts only what the roster needs
    (machines/<name>/{hostname, hostname_aliases, schedule_variant}). The sentinel
    runs under ``uv run --no-project`` where pyyaml is not guaranteed."""
    machines, cur, in_machines = {}, None, False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        key, _, val = line.strip().partition(":")
        val = val.strip()
        if indent == 0:
            in_machines, cur = (key == "machines"), None
            continue
        if not in_machines:
            continue
        if indent == 2 and not val:
            cur = key
            machines[cur] = {}
        elif indent == 4 and cur and val:
            if val.startswith("[") and val.endswith("]"):
                machines[cur][key] = [v.strip().strip("'\"")
                                      for v in val[1:-1].split(",") if v.strip()]
            else:
                machines[cur][key] = val.strip("'\"")
    return {"machines": machines}


def load_expected_machines(registry_path):
    """Roster of machines expected to publish: ``config/workstations/registry.yaml``
    entries whose ``schedule_variant`` is set and not ``none`` (i.e. they run the
    daily cron). Degrades open (empty roster → check skipped) on any failure so a
    missing/unparseable registry never turns the sentinel into a false alarm."""
    try:
        with open(registry_path) as fh:
            text = fh.read()
        try:
            import yaml
            data = yaml.safe_load(text) or {}
        except ImportError:
            data = _parse_registry_minimal(text)
        roster = []
        for name, m in sorted((data.get("machines") or {}).items()):
            m = m or {}
            if str(m.get("schedule_variant") or "none").lower() == "none":
                continue
            roster.append({"machine": name, "hostname": m.get("hostname"),
                           "aliases": list(m.get("hostname_aliases") or [])})
        return roster
    except Exception as e:  # noqa: BLE001 — degrade open by design
        print(f"WARN: expected-machines roster unavailable ({e}); "
              f"absent-fingerprint check skipped", file=sys.stderr)
        return []


def compare(fps, *, behind_warn=10, stale_h=6.0, learning_max_h=48.0,
            expected_machines=None, publish_slow_s=60.0):
    """Compare fingerprint dicts; return divergences sorted worst-first.

    A divergence is ``{severity, code, detail, boxes}``. Empty list == equivalent.
    Role-aware: cron *set* differences between roles are expected and NOT flagged;
    only registry/harness equivalence, clone lag, hub-cron freshness, and
    reporting staleness are checked.

    ``expected_machines`` (#3502): roster from ``load_expected_machines`` — any
    roster machine with no fingerprint in the store is flagged; a box whose
    publish is gate-blocked (#3500) can never land its fingerprint, so absence
    IS the deadlock symptom. ``publish_slow_s`` flags publishes that landed but
    took gate-length time (re-emergent hook gating).
    """
    out: list[dict] = []
    if not fps:
        return out
    # #3516: label boxes by machine_id first — two same-role boxes (ace-win-1/2)
    # must not merge into one key in divergence "boxes" dicts.
    roles = [f.get("machine_id") or f.get("role") or f.get("hostname") or "?" for f in fps]

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

    # 9. roster machine absent from the store -> WARNING (#3502). A gate-blocked
    # publish (#3500) can never land its fingerprint — absence IS the symptom;
    # the other possibility (sentinel not installed) equally needs surfacing.
    if expected_machines:
        seen = {str(f.get("hostname") or "").lower() for f in fps}
        seen |= {str(r).lower() for r in roles}
        seen.discard("")
        for m in expected_machines:
            names = {str(m.get("hostname") or "").lower(),
                     str(m.get("machine") or "").lower()}
            names |= {str(a).lower() for a in (m.get("aliases") or [])}
            names.discard("")
            if names and not (names & seen):
                label = m.get("machine") or m.get("hostname") or "?"
                out.append(_div(WARNING, "absent-fingerprint",
                                f"{label}: no fingerprint in equivalence-state — publish may be "
                                f"gate-blocked (#3500) or the sentinel is not running there",
                                {label: "absent"}))

    # 10. publish landed but took gate-length time -> WARNING (#3502). Detects a
    # re-emergent pre-push gate even when the push eventually succeeds.
    for r, f in zip(roles, fps):
        dur = f.get("last_publish_duration_s")
        if isinstance(dur, (int, float)) and not isinstance(dur, bool) and dur > publish_slow_s:
            out.append(_div(WARNING, "publish-slow",
                            f"{r}: last equivalence publish took {dur:.0f}s "
                            f"(> {publish_slow_s:.0f}s) — pre-push gate suspected (#3500)",
                            {r: round(float(dur), 1)}))

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
    ap.add_argument("--publish-slow-s", type=float, default=60.0)
    ap.add_argument("--registry", default=None,
                    help="config/workstations/registry.yaml — enables absent-fingerprint check")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    a = ap.parse_args(argv)
    fps = load_dir(a.dir)
    expected = load_expected_machines(a.registry) if a.registry else None
    divs = compare(fps, behind_warn=a.behind_warn, stale_h=a.stale_h,
                   learning_max_h=a.learning_max_h,
                   expected_machines=expected, publish_slow_s=a.publish_slow_s)
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
