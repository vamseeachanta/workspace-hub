#!/usr/bin/env python3
"""aggregate_drift_candidates.py — recurring drift classes → parked skill-update candidates (#3254, epic #3248).

Closes gap #5: `detect-drift.sh` appends per-session rule-violation counts to
`.claude/state/drift-summary.yaml`, but repeats never become skill-update candidates. This script
windows that corpus, finds drift CLASSES that recur on N distinct calendar days, and emits a PARKED
candidate file (`.claude/state/candidates/drift-skill-candidates.yaml`) for human triage. It NEVER
opens issues, applies labels, or edits skills/rules — it is an actuator for humans, not the agent
(Hard Rule 1). The candidates/ dir is auto-committed by the nightly committer.

Design (locked by the #3254 adversarial plan review, rounds r1–r3):
  * "Recurring" = nonzero count for a class on >= DRIFT_RECUR_DAYS DISTINCT UTC calendar days within
    a [now - DRIFT_WINDOW_DAYS, now] window. Day-grained, NOT distinct-log-grained: a single nightly
    run stamps every record (20–150 Codex logs + 1 Claude + 1 Hermes) with that night's `scanned_at`
    date, so one noisy night collapses to ONE day and cannot trip a candidate. This makes recurrence
    mean "drifted on N separate nights" = persistence over TIME, and is provider-commensurate.
  * Pure core (`evaluate_recurring`, `merge_candidates`) — no IO, no clock, no subprocess; `now` is
    injected as a naive-UTC datetime. Mirrors `scripts/operations/venue_absence_detector.py`.
  * Thresholds are env-overridable named constants (`DRIFT_WINDOW_DAYS` / `DRIFT_RECUR_DAYS`).
  * Only the four LEAF violation classes are considered. `git_workflow` (a rollup of its two git
    leaves) and `git_exempt_type` (counts NON-violations) are deliberately excluded.
  * The writer is a MERGE: it preserves any human-edited status, refreshes evidence on still-recurring
    rows, and ages decayed candidates to `active: false` (never silently deletes).
  * Exit 0 on success even when candidates are found — "found candidates" is signaled by file content,
    never by exit code (Hard Rule 4). The nightly invocation is additionally `|| echo WARNING`-guarded.
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml  # NOT PEP-723; the nightly hard-preflights `import yaml` (comprehensive-learning-nightly.sh:14-19)

# --- IMPORT WIRING (round-2 MINOR fix) -------------------------------------------------------------
# scripts/ is not a package and scripts/curation is not on sys.path under the bare
#   `${PYTHON} scripts/session/aggregate_drift_candidates.py`
# nightly invocation. Insert it BEFORE importing machine_label, or the import would ModuleNotFoundError
# and the nightly's `|| echo WARNING` guard would silently no-op the aggregator every night.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "curation"))  # -> repo/scripts/curation
from audit_skill_currency import machine_label  # noqa: E402  canonical host->label (audit_skill_currency.py:53)

# ─── Paths (env-overridable for testability; default to the repo state files) ──────────────────────
REPO = Path(__file__).resolve().parents[2]
STATE = REPO / ".claude" / "state"
DEFAULT_SUMMARY_FILE = STATE / "drift-summary.yaml"
DEFAULT_CANDIDATES_FILE = STATE / "candidates" / "drift-skill-candidates.yaml"

# ─── Thresholds (named constants; env-overridable in the CLI, not in the pure core) ────────────────
DEFAULT_WINDOW_DAYS = 14
DEFAULT_RECUR_DAYS = 3  # distinct CALENDAR DAYS, not distinct logs (round-2 MAJOR)

# The four LEAF violation classes. git_workflow (rollup) + git_exempt_type (non-violation) excluded.
LEAF_VIOLATION_CLASSES = (
    "python_runtime",
    "file_placement",
    "git_non_conventional",
    "git_missing_wrk_ref",
)

# class -> (target, default_kind, action, rationale_template{d,w})
_CODING_STYLE = ".claude/rules/coding-style.md"
CLASS_TARGETS = {
    "python_runtime": (
        f"{_CODING_STYLE} (Python runtime: `uv run` vs bare python3)",
        "skill-guide",
        "Propose a skill-guide note or a documented skill-exception for bare python3 usage",
        "python_runtime drifted on {d} distinct days over {w}d — repeated rule miss; capture as guidance or sanctioned exception.",
    ),
    "file_placement": (
        f"{_CODING_STYLE} (test/src file placement)",
        "skill-guide",
        "Propose a skill-guide note or a documented skill-exception for test/src file placement",
        "file_placement drifted on {d} distinct days over {w}d — repeated rule miss; capture as guidance or sanctioned exception.",
    ),
    "git_non_conventional": (
        "git-workflow rule / conventional-commit guide",
        "skill-guide",
        "Propose a skill-guide note or a documented skill-exception for conventional commit subjects",
        "git_non_conventional drifted on {d} distinct days over {w}d — repeated rule miss; capture as guidance or sanctioned exception.",
    ),
    "git_missing_wrk_ref": (
        "git-workflow rule (WRK/issue ref in commit)",
        "skill-guide",
        "Propose a skill-guide note or a documented skill-exception for missing issue refs in commits",
        "git_missing_wrk_ref drifted on {d} distinct days over {w}d — repeated rule miss; capture as guidance or sanctioned exception.",
    ),
}

# Evidence fields refreshed on every recurring row (status never refreshed — park-for-review gate).
_EVIDENCE_FIELDS = (
    "distinct_days", "distinct_sessions", "total_violations",
    "providers", "last_seen", "window_days",
)


# ─── Canonical time helpers (round-trip with producer's `date -u +%Y-%m-%dT%H:%M:%SZ`) ─────────────
PRODUCER_FMT = "%Y-%m-%dT%H:%M:%S"  # producer appends a literal "Z" after this


def parse_iso(s):
    """Producer emits naive-UTC seconds + literal 'Z'. Strip 'Z', parse to NAIVE datetime, or None."""
    try:
        return datetime.strptime(str(s).strip().rstrip("Z"), PRODUCER_FMT)
    except (ValueError, AttributeError, TypeError):
        return None  # malformed/absent -> caller skips (fail-closed)


def iso_z(dt):
    """NAIVE utc datetime -> '....T..:..:..Z'; round-trips with parse_iso and matches the producer."""
    return dt.replace(microsecond=0).isoformat() + "Z"


def _as_nonneg_int(v):
    try:
        n = int(v)
    except (TypeError, ValueError):
        return 0
    return n if n > 0 else 0


def _count_by_provider(sessions):
    out = defaultdict(int)
    for s in sessions.values():
        out[s["provider"]] += 1
    return dict(out)


# ─── PURE CORE (no IO, no clock, no subprocess; `now` injected as a NAIVE-UTC datetime) ─────────────
def evaluate_recurring(entries, *, now, window_days, recur_days):
    """Return a list of fresh recurring-drift candidate dicts. PURE: no IO, no clock.

    entries: parsed drift-summary records [{scanned_at, log, provider, violations:{...}}].
    A class is recurring iff it has a nonzero count on >= recur_days distinct UTC calendar dates
    within [now - window_days, now]. Evidence fields dedup by distinct `log` (max count per log).
    """
    cutoff = now - timedelta(days=window_days)
    per_class_days = defaultdict(set)       # class -> {date}  (THE recurrence metric)
    per_class_sessions = defaultdict(dict)  # class -> {log: {count, provider, scanned_at}}  (evidence)

    for rec in entries:
        if not isinstance(rec, dict):
            continue
        ts = parse_iso(rec.get("scanned_at"))
        if ts is None or ts < cutoff or ts > now:  # malformed/out-of-window/future -> skip (fail-closed)
            continue
        day = ts.date()
        log = rec.get("log") or ""
        prov = rec.get("provider") or "unknown"
        viol = rec.get("violations") or {}
        if not isinstance(viol, dict):
            continue
        for cls in LEAF_VIOLATION_CLASSES:
            c = _as_nonneg_int(viol.get(cls))
            if c <= 0:
                continue
            per_class_days[cls].add(day)
            cur = per_class_sessions[cls].get(log)
            if cur is None or c > cur["count"]:  # dedup: max count per distinct session (evidence)
                per_class_sessions[cls][log] = {"count": c, "provider": prov, "scanned_at": ts}

    out = []
    for cls in LEAF_VIOLATION_CLASSES:
        days = per_class_days[cls]
        if len(days) < recur_days:  # THE recurrence threshold (distinct days)
            continue
        sessions = per_class_sessions[cls]
        target, kind, action, rtmpl = CLASS_TARGETS[cls]
        stamps = [s["scanned_at"] for s in sessions.values()]
        out.append({
            "drift_class": cls,
            "kind": kind,
            "target": target,
            "action": action,
            "distinct_days": len(days),
            "distinct_sessions": len(sessions),
            "total_violations": sum(s["count"] for s in sessions.values()),
            "providers": _count_by_provider(sessions),
            "first_seen": iso_z(min(stamps)),
            "last_seen": iso_z(max(stamps)),
            "window_days": window_days,
            "rationale": rtmpl.format(d=len(days), w=window_days),
        })
    return out


# ─── MERGE (preserve human statuses; age out decayed candidates) ──────────────────────────────────
def merge_candidates(existing_doc, fresh, *, now_iso, machine, window_days, recur_days):
    """Merge fresh recurring candidates into the existing parked doc. Never clobbers human status."""
    by_class = {c["drift_class"]: dict(c) for c in (existing_doc or {}).get("candidates", [])}
    fresh_classes = {f["drift_class"] for f in fresh}

    for f in fresh:
        prev = by_class.get(f["drift_class"])
        if prev and prev.get("status") not in (None, "candidate"):
            # human-triaged row, still recurring -> refresh EVIDENCE ONLY; never touch status.
            for k in _EVIDENCE_FIELDS:
                prev[k] = f[k]
            prev["active"] = True
        else:
            row = {**(prev or {}), **f}
            row["status"] = "candidate"
            row["active"] = True
            row["first_seen"] = (prev or {}).get("first_seen", f["first_seen"])  # sticky first_seen
            by_class[f["drift_class"]] = row

    # classes NOT recurring this cycle
    for cls, row in by_class.items():
        if cls in fresh_classes:
            continue
        if row.get("status") in (None, "candidate"):
            row["active"] = False  # decayed below threshold -> mark inactive (last_seen left as-is)
        # human-set non-candidate rows: left fully intact (status + active untouched)

    return {
        "generated_at": now_iso,
        "machine": machine,
        "window_days": window_days,
        "recur_days": recur_days,
        "schema_version": 1,
        "candidates": [by_class[k] for k in sorted(by_class)],
    }


# ─── Thin CLI ─────────────────────────────────────────────────────────────────────────────────────
def _summary_file():
    return Path(os.environ.get("DRIFT_SUMMARY_FILE", str(DEFAULT_SUMMARY_FILE)))


def _candidates_file():
    return Path(os.environ.get("DRIFT_CANDIDATES_FILE", str(DEFAULT_CANDIDATES_FILE)))


def _load_yaml(path):
    """Load a YAML file. Missing/empty/garbled -> None (fail-closed; never raise)."""
    try:
        text = path.read_text()
    except (FileNotFoundError, OSError):
        return None
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError:
        return None


def _atomic_write_yaml(path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(yaml.safe_dump(doc, sort_keys=False))
    tmp.replace(path)


def _env_int(name, default):
    raw = os.environ.get(name)
    if raw is None or str(raw).strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def main(argv=None):
    parser = argparse.ArgumentParser(description="Aggregate recurring drift classes into parked skill-update candidates.")
    parser.add_argument("--window-days", type=int, default=None)
    parser.add_argument("--recur-days", type=int, default=None)
    parser.add_argument("--stdout", action="store_true", help="dry-run: print the merged doc, write nothing")
    args = parser.parse_args(argv)

    window = _env_int("DRIFT_WINDOW_DAYS", args.window_days if args.window_days is not None else DEFAULT_WINDOW_DAYS)
    recur = _env_int("DRIFT_RECUR_DAYS", args.recur_days if args.recur_days is not None else DEFAULT_RECUR_DAYS)
    now = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)  # NAIVE UTC -> matches parse_iso output

    raw = _load_yaml(_summary_file())
    entries = raw if isinstance(raw, list) else []
    fresh = evaluate_recurring(entries, now=now, window_days=window, recur_days=recur)
    existing = _load_yaml(_candidates_file())
    existing = existing if isinstance(existing, dict) else None
    doc = merge_candidates(existing, fresh, now_iso=iso_z(now), machine=machine_label(),
                           window_days=window, recur_days=recur)

    if args.stdout:
        print(yaml.safe_dump(doc, sort_keys=False))
        return 0
    _atomic_write_yaml(_candidates_file(), doc)
    return 0  # ALWAYS 0 on success (Hard Rule 4) — "found candidates" is signaled by file content


if __name__ == "__main__":
    raise SystemExit(main())
