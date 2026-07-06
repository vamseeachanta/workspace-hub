#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""audit_memory_freshness.py — cross-provider memory-freshness audit (#3255, epic #3248).

Emits the FACTS for the machine-equality `memory_freshness` line item: how long ago was each
memory surface last refreshed, and is any of them stale? The matrix
(build-equality-matrix.py::memory_freshness_verdict) maps these facts → verdict. This module also
carries a self-contained pure verdict (`categorize`) so the staleness tier is unit-testable here.

Memory surfaces graded:
  * .claude/memory/context.md          (git-bridged — written by bridge-hermes-claude.sh)
  * .claude/memory/agents.md           (git-bridged)
  * config/agents/codex/MEMORY.runtime.md   (git-bridged provider runtime slice)
  * config/agents/gemini/MEMORY.runtime.md  (git-bridged provider runtime slice)
  * ~/.hermes/memories/                (machine-LOCAL, NOT git-tracked)

Design decision (locked by the #3255 adversarial review — same git-over-mtime posture as
audit_skill_currency.py #3249):
  * The four git-bridged surfaces take their last-refresh clock from `git log -1 --format=%cI`
    (the path's last-COMMIT time), NOT from `st_mtime`. The bridge writes these files on the owner
    box, commits, and every other box receives them by `git pull` — so on a fresh clone `st_mtime`
    equals checkout time, not refresh time, and would false-red a perfectly healthy box. The commit
    time, by contrast, travels with the repo (machine-invariant) and survives `git checkout`/`pull`.
    (audit_skill_currency.py:24 — "mtime is non-deterministic on fresh checkouts".)
  * Only `~/.hermes/memories/` (local, never checked out) uses real `st_mtime` — correct there.
  * git unavailable / not-a-repo / hung ⇒ the runner returns None ⇒ those surfaces are absent
    (fail-closed), never silently fresh.

Leak posture: state carries surface KEYS (short role names) + ISO timestamps + ages + bools only —
never absolute paths, file contents, prompt text, tokens, or client identifiers.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STATE = REPO / ".claude" / "state"

# Make the sibling audit module importable so machine_label() can be REUSED (not re-implemented),
# regardless of whether this file is run as a script or loaded by importlib from the test suite.
sys.path.insert(0, str(Path(__file__).resolve().parent))

# ── Freshness thresholds ──────────────────────────────────────────────────────────────────────
# The git-bridged memory surfaces are refreshed on a DAILY bridge cadence (provider-dream-bridge /
# hermes-claude-bridge @ ~04:0x), not the 6-hourly curation cadence — so these tiers are looser than
# session-curation's 12h/24h. 36h = one missed daily run (still amber-tolerant); 72h = three missed
# daily runs ⇒ the bridge is effectively dead and the cell should go red. Tunable in one place.
MEMORY_STALE_H = 36
MEMORY_EXPIRED_H = 72

MEMORY_FRESH = "MEMORY-FRESH"
MEMORY_STALE = "MEMORY-STALE"
MEMORY_EXPIRED = "MEMORY-EXPIRED"
MISSING_EVIDENCE = "MISSING-EVIDENCE"

# #3384: freshness is clocked by the daily BRIDGE HEARTBEAT (a committed liveness marker), NOT by the
# deterministic/byte-invariant content surfaces. context.md is a static heredoc and the read-back
# slices are deterministic (no timestamp) — on a quiet day they never diff, so their git-commit clock
# cannot advance and would false-trip EXPIRED even on a healthy daily bridge. The heartbeat changes
# once/day → guarantees one commit/day → its commit time is the honest "bridge ran" signal.
RECENCY_GIT_SURFACES = {
    "bridge_heartbeat": ".claude/state/memory-bridge-heartbeat.json",  # clock = git last-commit time
}
# Content surfaces graded by FILESYSTEM PRESENCE (exists + non-empty), NOT recency. A git-log clock
# reports a DELETED path as still-present via its last commit (#3384 r2 Finding 2), so presence must
# be a real filesystem check.
PRESENCE_SURFACES = {
    "context_md": ".claude/memory/context.md",
    "agents_md": ".claude/memory/agents.md",
    "codex_runtime": "config/agents/codex/MEMORY.runtime.md",
    "gemini_runtime": "config/agents/gemini/MEMORY.runtime.md",
}
# Machine-LOCAL surface (not git-tracked) → freshness clock = newest file mtime. Co-liveness signal:
# a genuinely-dead Hermes still legitimately trips the cell (max over recency surfaces).
HERMES_DIR = Path.home() / ".hermes" / "memories"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def _parse_iso(s) -> datetime | None:
    if not isinstance(s, str):
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def _git_commit_iso(rel_path: str) -> str | None:
    """Last-commit ISO time of a tracked path (survives checkout). None on git failure/untracked.

    This is THE runner the tests monkeypatch — it is the only place a `git log` subprocess is run,
    bounded and fail-soft so a hung/locked/missing git never stalls or false-greens the audit.
    """
    try:
        r = subprocess.run(
            ["git", "-C", str(REPO), "log", "-1", "--format=%cI", "--", rel_path],
            capture_output=True, text=True, timeout=30,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None                       # hung/locked/absent git ⇒ no evidence (fail-closed)
    if r.returncode != 0:
        return None
    out = r.stdout.strip()
    return out or None                    # empty ⇒ untracked / never committed ⇒ surface absent


def _hermes_mtime_iso() -> str | None:
    """Newest st_mtime among ~/.hermes/memories/*.md as ISO. None if the surface is absent/empty.

    mtime is the CORRECT clock here: this tree is machine-local and never git-checked-out, so its
    mtime reflects the actual last Hermes write on this box.
    """
    if not HERMES_DIR.exists():
        return None
    mtimes: list[float] = []
    for p in HERMES_DIR.glob("*.md"):
        try:
            mtimes.append(p.stat().st_mtime)
        except OSError:
            continue
    if not mtimes:
        return None
    return _iso(datetime.fromtimestamp(max(mtimes), timezone.utc))


def _surface_record(refreshed_at: str | None, signal: str, now: datetime) -> dict:
    """One surface's facts: present/refreshed_at/age_hours/signal. Unparseable stamp ⇒ absent."""
    dt = _parse_iso(refreshed_at)
    if dt is None:
        return {"present": False, "refreshed_at": None, "age_hours": None, "signal": signal}
    age = round((now - dt).total_seconds() / 3600.0, 3)
    return {"present": True, "refreshed_at": refreshed_at, "age_hours": age, "signal": signal}


def _presence_record(rel: str, now: datetime) -> dict:
    """Content surface graded by filesystem presence (exists + non-empty), not recency. Filesystem —
    NOT git history — so a committed-then-deleted/emptied path reads absent (#3384 r2 Finding 2)."""
    try:
        p = REPO / rel
        present = p.is_file() and p.stat().st_size > 0
    except OSError:
        present = False
    return {"present": present, "refreshed_at": None, "age_hours": None, "signal": "presence"}


# ── Pure verdict ────────────────────────────────────────────────────────────────────────────────
def freshness_category(worst_age_hours, stale_h: float = MEMORY_STALE_H,
                       expired_h: float = MEMORY_EXPIRED_H) -> str:
    """Pure tier map for a single worst (oldest) age. None ⇒ MISSING-EVIDENCE; a negative age
    (future stamp ⇒ clock skew) ⇒ MISSING-EVIDENCE (fail-closed). Boundaries inclusive."""
    if isinstance(worst_age_hours, bool) or not isinstance(worst_age_hours, (int, float)):
        return MISSING_EVIDENCE          # bool is an int subclass — exclude it (matrix-parity)
    if worst_age_hours < 0:
        return MISSING_EVIDENCE
    if worst_age_hours <= stale_h:
        return MEMORY_FRESH
    if worst_age_hours <= expired_h:
        return MEMORY_STALE
    return MEMORY_EXPIRED


def categorize(ages, stale_h: float = MEMORY_STALE_H, expired_h: float = MEMORY_EXPIRED_H) -> str:
    """Pure facts→verdict: `ages` = the per-surface age_hours of the PRESENT surfaces. The OLDEST
    present surface dominates. Empty (no present surface proved a timestamp) ⇒ MISSING-EVIDENCE.
    Any negative age (clock skew) ⇒ MISSING-EVIDENCE (fail-closed)."""
    valid = [a for a in ages if isinstance(a, (int, float)) and not isinstance(a, bool)]
    if not valid:
        return MISSING_EVIDENCE
    if any(a < 0 for a in valid):
        return MISSING_EVIDENCE
    return freshness_category(max(valid), stale_h, expired_h)


def audit(machine: str | None = None, now: datetime | None = None) -> dict:
    if now is None:
        now = _now()
    if machine is None:
        import audit_skill_currency            # REUSE machine_label at call time (monkeypatchable)
        machine = audit_skill_currency.machine_label()

    surfaces: dict[str, dict] = {}
    for key, rel in RECENCY_GIT_SURFACES.items():                # liveness clock = git commit time
        surfaces[key] = _surface_record(_git_commit_iso(rel), "git-commit", now)
    surfaces["hermes_memories"] = _surface_record(_hermes_mtime_iso(), "file-mtime", now)
    for key, rel in PRESENCE_SURFACES.items():                   # content = filesystem presence only
        surfaces[key] = _presence_record(rel, now)

    # Freshness tier comes ONLY from the recency surfaces (heartbeat liveness + hermes local liveness);
    # the byte-invariant content surfaces never advance a commit clock, so they must not be graded here.
    recency = [surfaces[k] for k in RECENCY_GIT_SURFACES] + [surfaces["hermes_memories"]]
    present = [s for s in recency if s["present"] and s["age_hours"] is not None]
    worst_age = max((s["age_hours"] for s in present), default=None)        # oldest present recency surface
    newest = min(present, key=lambda s: s["age_hours"], default=None)       # most-recently refreshed
    newest_refresh = newest["refreshed_at"] if newest else None

    # Presence gate (fail-closed): a content surface that should exist but is absent/empty ⇒ the whole
    # audit is MISSING-EVIDENCE regardless of heartbeat freshness (catches a deleted/clobbered surface).
    content_absent = any(not surfaces[k]["present"] for k in PRESENCE_SURFACES)
    freshness = MISSING_EVIDENCE if content_absent else categorize([s["age_hours"] for s in present])

    return {
        "machine": machine,
        "audited_at": _iso(now),
        "surfaces": surfaces,
        "newest_refresh": newest_refresh,
        "worst_age_hours": worst_age,
        "freshness": freshness,
        "schema_version": 2,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Cross-provider memory-freshness audit (#3255)")
    ap.add_argument("--machine", default=None)
    ap.add_argument("--stdout", action="store_true", help="print state JSON, do not write")
    a = ap.parse_args(argv)
    state = audit(a.machine)
    machine = state["machine"]
    if a.stdout:
        print(json.dumps(state, indent=2))
        return 0
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / f"memory-freshness-{machine}.json").write_text(json.dumps(state, indent=2) + "\n")
    present = sum(1 for s in state["surfaces"].values() if s["present"])
    print(f"audited {machine}: {present}/{len(state['surfaces'])} surfaces present, "
          f"worst_age={state['worst_age_hours']}h, freshness={state['freshness']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
