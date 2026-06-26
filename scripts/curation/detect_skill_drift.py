#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""detect_skill_drift.py — cross-provider skill-drift detector + alert (#3250, epic #3248).

Reads the FACTS emitted by ``audit_skill_currency.py`` (``.claude/state/skill-currency-<machine>.json``)
and fires a ``scripts/notify.sh`` alert ONLY when NEW or CHANGED unexpected cross-provider family
drift appears — never re-alerting on an unchanged standing divergence. Mirrors the
``venue_absence_detector.py`` shape: a PURE decide-core (``drift_signature`` / ``evaluate_drift`` —
no IO, no clock, no subprocess) plus a thin CLI that gathers inputs, calls the core, and routes each
alert through an injectable ``notify_fn``.

Design decisions (locked by the #3250 plan + adversarial review):
  * The audit stays the sole fact emitter; this is a separate decide/alert/persist layer that READS
    its state file (the same ``audit → matrix`` split already in place).
  * Spam suppression via a persisted last-seen drift SIGNATURE
    (``.claude/state/skill-drift-<machine>.json``). An alert fires only on a signature transition
    into/within drift (new drift, or the drift SET changed); drift→clean emits one ``pass`` recovery.
  * Index staleness is EXCLUDED from the default signature — ``.claude/skills-index.yaml`` is
    known-rotted and would false-fire the detector's very first run. It folds into the signature
    ONLY under the explicit ``--include-index`` opt-in. Index rot stays surfaced by the matrix
    ``SKILLS-INDEX-STALE`` verdict.
  * Fail-closed: an unreadable/missing audit state yields signature ``UNREADABLE`` and alerts once
    (``audit-unreadable``) — never silently green.
  * The machine label is BORROWED from the audit (``audit_skill_currency.machine_label()`` called at
    runtime, not reimplemented) so the file the detector reads and the files it writes can never key
    off a different label.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

REPO = Path(__file__).resolve().parents[2]
STATE = REPO / ".claude" / "state"
NOTIFY_SH = REPO / "scripts" / "notify.sh"
EQUIVALENCE_CLI = REPO / "scripts" / "monitoring" / "equivalence_state.py"

PUBLISH_TIMEOUT_S = 90
DRIFT_REF = "skill-drift-state"

# Import the audit module (not the function) so its machine_label() is resolved at CALL TIME and
# remains monkeypatchable in tests. Same-dir module; ensure the curation dir is importable.
_CURATION_DIR = str(Path(__file__).resolve().parent)
if _CURATION_DIR not in sys.path:
    sys.path.insert(0, _CURATION_DIR)
import audit_skill_currency  # noqa: E402  (path set up above)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --------------------------------------------------------------------------- #
# PURE CORE — no IO, no clock, no subprocess
# --------------------------------------------------------------------------- #


def _pos_int(v) -> bool:
    """True for a strictly-positive plain int (rejects bool, which is an int subclass)."""
    return isinstance(v, int) and not isinstance(v, bool) and v > 0


def _drift_count(facts: dict) -> int:
    """Unexpected cross-provider family count, gated on gemini being present.

    Returns 0 when gemini is absent (a stale count must not register as drift) or when the count is
    missing/garbled. PURE.
    """
    if not bool(facts.get("gemini_present")):
        return 0
    n = facts.get("gemini_unexpected")
    return n if _pos_int(n) else 0


def _families(facts: dict) -> list[str]:
    """Sorted, stringified list of unexpected family NAMES (optional audit field; [] if absent)."""
    return sorted(str(f) for f in (facts.get("gemini_unexpected_families") or []))


def drift_signature(facts: dict, *, include_index: bool = False) -> str:
    """A stable, order-independent fingerprint of the current drift state. PURE.

    Returns one of:
      * ``"UNREADABLE"`` — the audit could not read the tree (``canonical_count`` not a positive int)
        → fail-closed, alertable.
      * ``"CLEAN"``      — no unexpected cross-provider drift (and, unless ``include_index``, index
        rot is ignored).
      * ``"fam:a,b[|idx:N]"`` — a pipe-joined signature naming the drifted families (and, only under
        ``include_index``, the dangling-index count).

    Index staleness is folded in ONLY when ``include_index=True`` so the standing index rot can never
    trip the family-drift alert on a first run.
    """
    if not isinstance(facts, dict) or not _pos_int(facts.get("canonical_count")):
        return "UNREADABLE"
    parts: list[str] = []
    n = _drift_count(facts)
    if n > 0:
        fams = _families(facts)
        parts.append("fam:" + ",".join(fams) if fams else f"fam-count:{n}")
    if include_index:
        dang = facts.get("index_dangling")
        if _pos_int(dang):
            parts.append(f"idx:{dang}")
    return "CLEAN" if not parts else "|".join(parts)


def _human_summary(facts: dict, sig: str) -> str:
    if sig == "UNREADABLE":
        return "skill-currency audit state missing or unreadable (fail-closed)"
    fams = _families(facts)
    n = _drift_count(facts)
    if fams:
        return f"{n} unexpected gemini family(ies) vs canonical: {', '.join(fams)}"
    if n:
        return f"{n} unexpected gemini family(ies) vs canonical (names unavailable)"
    return f"drift signature {sig}"


def evaluate_drift(facts, last_seen, *, now_iso: str, include_index: bool = False) -> dict:
    """Decide whether to alert, given current facts + the last-seen state. PURE — no IO/clock.

    Spam-suppression contract (alert exactly once per distinct drift state):
      * none → drift        : ``new_drift`` (one ``fail`` alert)
      * drift → same drift  : suppressed (no alert)
      * drift → changed set : ``new_drift`` (one ``fail`` alert)
      * drift → clean        : ``recovered`` (one ``pass`` alert)

    ``UNREADABLE`` counts as a (fail-closed) drift state, so a missing/garbled audit alerts once as
    ``audit-unreadable`` and stays suppressed until it changes or recovers.
    """
    if not isinstance(facts, dict):
        facts = {}
    sig = drift_signature(facts, include_index=include_index)
    drift_present = sig != "CLEAN"
    last = last_seen if isinstance(last_seen, dict) else None
    last_sig = (last or {}).get("signature")

    new_drift = drift_present and sig != last_sig
    recovered = (not drift_present) and last_sig not in (None, "CLEAN")

    alerts: list[dict] = []
    if new_drift:
        kind = "audit-unreadable" if sig == "UNREADABLE" else "skill-drift"
        alerts.append({
            "kind": kind,
            "detail": _human_summary(facts, sig),
            "severity": "critical",
            "status": "fail",
        })
    if recovered:
        alerts.append({
            "kind": "skill-drift-cleared",
            "detail": f"cross-provider skill drift cleared (was {last_sig}, now CLEAN)",
            "severity": "info",
            "status": "pass",
        })

    if sig == last_sig and last and last.get("first_seen"):
        first_seen = last["first_seen"]
    else:
        first_seen = now_iso
    new_state = {
        "signature": sig,
        "drift_present": drift_present,
        "first_seen": first_seen,
        "updated_at": now_iso,
    }

    dang = facts.get("index_dangling")
    report = {
        "machine": facts.get("machine") if isinstance(facts.get("machine"), str) else None,
        "evaluated_at": now_iso,
        "signature": sig,
        "drift_present": drift_present,
        "new_drift": new_drift,
        "recovered": recovered,
        "include_index": bool(include_index),
        "gemini_present": bool(facts.get("gemini_present")),
        "gemini_unexpected": _drift_count(facts),
        "gemini_unexpected_families": _families(facts),
        "index_dangling": (dang if (isinstance(dang, int) and not isinstance(dang, bool)) else None),
        "schema_version": 1,
    }

    return {
        "signature": sig,
        "drift_present": drift_present,
        "new_drift": new_drift,
        "recovered": recovered,
        "alerts": alerts,
        "report": report,
        "new_state": new_state,
    }


# --------------------------------------------------------------------------- #
# THIN CLI — IO, clock, subprocess live here
# --------------------------------------------------------------------------- #


def _read_json(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def _default_notify(alert: dict) -> None:
    """Real notifier: append one JSONL event via scripts/notify.sh (source=cron, job=skill-drift)."""
    status = alert.get("status", "fail")
    detail = f"{alert.get('kind', '?')}: {alert.get('detail', '')}"
    subprocess.run(
        ["bash", str(NOTIFY_SH), "cron", "skill-drift", status, detail],
        check=False,
    )


def publish_drift(machine: str) -> str:
    """Publish this box's drift report to the dedicated git ref via the equivalence-state CLI, in a
    BOUNDED subprocess. The git push can hang (network/auth/lock — a sibling publish was observed
    stuck >1h), so we cap it and fail soft: a hung/failed publish must never stall curation. Mirrors
    curate_session_memory.publish_fingerprint."""
    report_file = STATE / f"skill-drift-report-{machine}.json"
    if not report_file.exists() or not EQUIVALENCE_CLI.exists():
        return "publish-skipped (no state/cli)"
    try:
        r = subprocess.run(
            [sys.executable, str(EQUIVALENCE_CLI), "publish", "--repo", str(REPO),
             "--role", machine, "--file", str(report_file), "--ref", DRIFT_REF],
            capture_output=True, text=True, timeout=PUBLISH_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return f"publish-timeout ({PUBLISH_TIMEOUT_S}s)"
    except Exception as e:  # noqa: BLE001 — best-effort fleet slice; never fail local detection
        return f"publish-error: {str(e)[:80]}"
    return "published" if r.returncode == 0 else f"publish-rc{r.returncode}"


def run_cli(args: argparse.Namespace, notify_fn: Callable[[dict], None] = _default_notify) -> int:
    """Gather audit state, decide, persist, and fire one notify_fn per alert. Returns exit code.

    Returns 1 when a NEW drift fired (so a cron can branch on it), else 0. notify_fn is injectable so
    tests assert call counts without shelling out. The machine label is borrowed from the audit so
    every filename keys off the SAME label that wrote skill-currency-<machine>.json.
    """
    machine = audit_skill_currency.machine_label()
    facts = _read_json(STATE / f"skill-currency-{machine}.json")
    last = _read_json(STATE / f"skill-drift-{machine}.json")
    result = evaluate_drift(facts, last, now_iso=_now(), include_index=getattr(args, "include_index", False))

    # (a) report ALWAYS written, regardless of alert.
    _write_json(STATE / f"skill-drift-report-{machine}.json", result["report"])
    # (b) alerts gated by the dedup decision.
    for alert in result["alerts"]:
        notify_fn(alert)
    # (c) persist the last-seen signature for next-run suppression.
    _write_json(STATE / f"skill-drift-{machine}.json", result["new_state"])
    # (d) optional bounded, fail-soft cross-machine publish.
    if getattr(args, "publish", False):
        print(publish_drift(machine), file=sys.stderr)

    sig = result["signature"]
    if result["alerts"]:
        for alert in result["alerts"]:
            print(f"skill-drift: [{alert['status']}] {alert['kind']}: {alert['detail']}",
                  file=sys.stderr)
    else:
        print(f"skill-drift: no new alert (signature={sig})")
    return 1 if result["new_drift"] else 0


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Cross-provider skill-drift detector — alerts once per distinct drift state."
    )
    p.add_argument("--include-index", action="store_true",
                   help="Fold the dangling-index count into the drift signature (default OFF — index "
                        "rot is surfaced by the matrix SKILLS-INDEX-STALE verdict instead).")
    p.add_argument("--publish", action="store_true",
                   help="Publish the drift report to the skill-drift-state git ref (bounded, fail-soft).")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    return run_cli(args)


if __name__ == "__main__":
    sys.exit(main())
