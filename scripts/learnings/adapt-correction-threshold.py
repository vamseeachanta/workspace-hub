#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""adapt-correction-threshold.py — adaptive correction-confidence threshold (#3256, epic #3248).

Supplies the **read-only** adaptation machinery for gap #6 ("hard-coded confidence threshold —
never adapts to whether promoted learnings actually survive"). It reads the git-tracked promotion
ledger (`.claude/state/candidates/correction-promotions.yaml`), counts ONLY terminal outcomes that
carry a *human-provenance* `reviewed_by` marker, and writes a bounded new threshold for the
`session_corrections` signal to `.claude/state/correction-confidence-threshold.json`.
`extract-learnings.sh` reads `.threshold` from that JSON and applies it ONLY to `session_corrections`
signals (the other four signal types keep the static `AUTO_ISSUE_THRESHOLD=70`).

DORMANT BY DESIGN (round-2 major #3 — read before grading gap #6 closure):
  gap #6 is NOT closed by this module. No ledger entry carries `reviewed_by` today, and this module
  introduces NO writer for it. The human-terminal count is therefore 0, so the loop holds at 80
  forever (`dormant: true`) until a human-provenance writer lands. Shipping inert machinery is the
  correct fail-SAFE posture for Hard Rule 1 — the bar never moves without human provenance, and an
  auto-promote → auto-lower-threshold → more-auto-issues loop is structurally impossible.

`reviewed_by` CONTRACT (the human-provenance marker — defined here, owned by a FUTURE writer):
  * WHAT  : a top-level string field on a `promotions:` list entry in correction-promotions.yaml,
            e.g. `reviewed_by: "vamsee"`. Non-empty (after strip) ⇒ a human reviewed this promotion.
  * WHO   : written ONLY by a human-review entry point — a follow-on child of epic #3248 that owns
            the review UI/CLI. This module (and sibling #3252) MUST NOT write it (advisory; this
            module cannot mechanically prevent another process from writing it, but it never does).
  * WHEN COUNTED : an entry counts toward adaptation iff it has BOTH a TERMINAL `status:`
            (SURVIVED vocab `{accepted,merged,verified,promoted}` or REJECTED vocab
            `{rejected,reverted,abandoned}`) AND a non-empty `reviewed_by`. `status:` alone is
            machine-writable (sibling #3252) ⇒ insufficient; bare-status entries are IGNORED so a
            machine can never close the auto-promote loop.

Design (mirrors detect_skill_drift.py): a PURE decide-core (`adapt_threshold` / `_is_human_terminal`
— no IO, no clock, no subprocess) plus a thin CLI that reads the ledger + current state, calls the
core, and persists the state JSON. The CLI ALWAYS exits 0 (Hard Rule 4 — signal via JSON, never the
exit code); it performs NO `gh`/`git`/status-label writes (Hard Rule 1) and NO state-ref push
(Hard Rule 5 — the state is machine-invariant; fleet distribution is the ordinary nightly commit).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
STATE = REPO / ".claude" / "state"
DEFAULT_LEDGER = STATE / "candidates" / "correction-promotions.yaml"
DEFAULT_STATE = STATE / "correction-confidence-threshold.json"

# The session_corrections score lattice is exactly {80, 90} (extract-learnings.sh:188-204):
# 80 = single occurrence, 90 = count>10 corroborated. One STEP crosses the one real boundary.
DEFAULT, FLOOR, CEIL, STEP = 80, 80, 90, 10
MIN_SAMPLE = 8                        # fail-safe: no adaptation without enough human-terminal evidence
TARGET_HIGH, TARGET_LOW = 0.80, 0.50  # success-rate bands (inclusive boundaries)
SCHEMA_VERSION = 1

SURVIVED = {"accepted", "merged", "verified", "promoted"}   # terminal "survived"
REJECTED = {"rejected", "reverted", "abandoned"}            # terminal "failed"
# everything else (identified, proposed, pending, …) is NON-terminal ⇒ ignored


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --------------------------------------------------------------------------- #
# PURE CORE — no IO, no clock, no subprocess
# --------------------------------------------------------------------------- #
def _is_human_terminal(entry) -> str | None:
    """Classify a ledger entry as a human-reviewed terminal outcome. PURE.

    Returns ``"survived"`` / ``"rejected"`` / ``None``. Rule-1 gate: a terminal outcome counts ONLY
    if a human stamped a non-empty ``reviewed_by`` marker. ``status`` alone is machine-writable
    (sibling #3252) ⇒ insufficient. No entry carries ``reviewed_by`` today ⇒ this returns ``None``
    for EVERY current entry ⇒ the loop is DORMANT by design (major #3). That is correct, not a bug.
    """
    if not isinstance(entry, dict):
        return None
    reviewer = entry.get("reviewed_by")
    if not (isinstance(reviewer, str) and reviewer.strip()):
        return None
    s = entry.get("status")
    if s in SURVIVED:
        return "survived"
    if s in REJECTED:
        return "rejected"
    return None


def _clamp(x: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, x))


def _coerce_current(current, default: int, floor: int, ceiling: int) -> int:
    """Clamp a possibly-garbled current value into the band; fall back to default. PURE."""
    if isinstance(current, (int, float)) and not isinstance(current, bool):
        return _clamp(int(current), floor, ceiling)
    return _clamp(default, floor, ceiling)


def _result(cur: int, new: int, terminal: int, accepted: int, rejected: int, reason: str) -> dict:
    rate = (accepted / terminal) if terminal else None
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": "session_corrections",
        "updated_at": _now(),
        "threshold": new,
        "previous": cur,
        "default": DEFAULT,
        "floor": FLOOR,
        "ceiling": CEIL,
        "step": STEP,
        "changed": new != cur,
        "dormant": terminal == 0,
        "inputs": {
            "terminal": terminal,
            "accepted": accepted,
            "rejected": rejected,
            "success_rate": rate,
            "sample_sufficient": terminal >= MIN_SAMPLE,
        },
        "reason": reason,
    }


def adapt_threshold(*, current, accepted: int, rejected: int,
                    default: int = DEFAULT, floor: int = FLOOR, ceiling: int = CEIL,
                    step: int = STEP, min_sample: int = MIN_SAMPLE,
                    target_high: float = TARGET_HIGH, target_low: float = TARGET_LOW) -> dict:
    """Compute a bounded new session_corrections threshold from human-terminal outcomes. PURE.

    ``current`` may be None/garbled ⇒ falls back to ``default``, clamped into ``[floor, ceiling]``.
    Adaptation is held (no change) below ``min_sample`` terminal outcomes. High success ⇒ LOWER the
    bar (admit single-occurrence signals, +recall); low success ⇒ RAISE the bar (demand
    corroboration, +precision); otherwise hold.
    """
    cur = _coerce_current(current, default, floor, ceiling)
    terminal = accepted + rejected
    if terminal < min_sample:
        return _result(cur, cur, terminal, accepted, rejected,
                       f"insufficient sample ({terminal}/{min_sample}) — hold")
    rate = accepted / terminal
    if rate >= target_high:
        new = _clamp(cur - step, floor, ceiling)
        why = f"success {rate:.2f}>={target_high} ⇒ lower→{new} (+recall)"
    elif rate <= target_low:
        new = _clamp(cur + step, floor, ceiling)
        why = f"success {rate:.2f}<={target_low} ⇒ raise→{new} (+precision)"
    else:
        new = cur
        why = f"success {rate:.2f} in dead-band ⇒ hold"
    return _result(cur, new, terminal, accepted, rejected, why)


# --------------------------------------------------------------------------- #
# THIN CLI — IO lives here; ALWAYS exits 0
# --------------------------------------------------------------------------- #
def _load_ledger(path: Path) -> list:
    """Return the `promotions:` list, or [] on any read/parse failure (fail-safe)."""
    try:
        data = yaml.safe_load(path.read_text())
    except (OSError, yaml.YAMLError):
        return []
    if not isinstance(data, dict):
        return []
    promos = data.get("promotions")
    return promos if isinstance(promos, list) else []


def _read_current(path: Path):
    """Return the stored `.threshold` int, or None if absent/garbled (fail-safe)."""
    try:
        doc = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    t = doc.get("threshold") if isinstance(doc, dict) else None
    if isinstance(t, (int, float)) and not isinstance(t, bool):
        return int(t)
    return None


def run_cli(args: argparse.Namespace) -> int:
    """Read ledger + current state, compute, persist (unless --stdout). ALWAYS returns 0.

    The adapter performs NO `gh`/`git`/status-label write and NO state-ref push — it only reads the
    git-tracked ledger and writes a single machine-invariant JSON the consumer reads.
    """
    ledger_path = Path(args.ledger)
    state_path = Path(args.state)

    ledger = _load_ledger(ledger_path)
    outcomes = [o for e in ledger if (o := _is_human_terminal(e)) is not None]
    accepted = outcomes.count("survived")
    rejected = outcomes.count("rejected")
    current = _read_current(state_path)

    result = adapt_threshold(current=current, accepted=accepted, rejected=rejected)

    if getattr(args, "stdout", False):
        print(json.dumps(result, indent=2))
        return 0

    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(result, indent=2) + "\n")
    print(f"adapt-correction-threshold: scope=session_corrections threshold={result['threshold']} "
          f"(prev={result['previous']}, terminal={result['inputs']['terminal']}, "
          f"dormant={result['dormant']}) — {result['reason']}", file=sys.stderr)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Adaptive correction-confidence threshold for the session_corrections signal "
                    "(#3256). DORMANT until a human-provenance reviewed_by marker lands.")
    p.add_argument("--ledger", default=str(DEFAULT_LEDGER),
                   help="promotion ledger YAML (default: the git-tracked correction-promotions.yaml)")
    p.add_argument("--state", default=str(DEFAULT_STATE),
                   help="threshold state JSON to read current value from and write the result to")
    p.add_argument("--stdout", action="store_true",
                   help="print the computed state JSON to stdout and do NOT write the state file")
    return p


def main(argv: list[str] | None = None) -> int:
    return run_cli(_build_parser().parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
