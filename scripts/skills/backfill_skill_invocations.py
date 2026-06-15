#!/usr/bin/env python3
"""backfill_skill_invocations.py — #3138 (follow-on to #3112)

Reconstruct historical skill-invocation events from logs that predate the
forward-looking emit signal shipped in #3112, so the
skill-invocation-scanner.py -> skill-usage-report.py demotion chain can act on a
>=14-day coverage window NOW instead of waiting ~2 weeks for the live emit to
accrue.

What it recovers
----------------
Every Read-of-SKILL.md tool call recorded in:
  1. Claude transcripts: ``~/.claude/projects/**/*.jsonl`` (the widest span;
     ~358 events / ~90d as of 2026-06-15). Records carry top-level ``timestamp``
     + ``sessionId`` and a ``message.content[]`` block with
     ``type=="tool_use"``, ``name=="Read"``, ``input.file_path`` = the SKILL.md.
  2. Existing session logs (``.claude/state/sessions/session_*.jsonl`` and/or
     ``logs/orchestrator/claude/...``) — these already have a ``file`` field but
     ``skill_name`` was never derived for pre-#3112 records.

It writes them in the scanner-consumable envelope
``{skill_name, ts, session_id, ...}``, one file per source-day, named
``session_<YYYYMMDD>.backfill.jsonl`` so it never clobbers or races the live
logger that is appending to ``session_<today>.jsonl``.

The CRITICAL key contract (#3138 trap)
--------------------------------------
session-logger.sh emits the **FULL rel-path** under ``.claude/skills/``
(``${FILE##*/.claude/skills/}`` minus ``/SKILL.md``), and the scanner joins
events on that full rel-path (``discover_skills`` yields
``skill_md.parent.relative_to(root).as_posix()``, which is full-depth). But
``skill_execution_tracker.SKILL_PATH_RE`` captures only TWO path segments and
``_extract_skill_name_from_path`` reduces even that to a basename — BOTH are the
wrong key for the scanner join. Skills nest deeper than two segments (e.g.
``engineering/marine-offshore/aqwa/input``), so this tool emits the FULL
rel-path. We import ``SKILL_PATH_RE`` only to assert intent-compatibility (the
2-segment capture is a strict prefix of our full-depth extraction); we do NOT
use it for the emitted key.

Limitation (documented per #3112 task)
--------------------------------------
Pre-instrumentation usage is fundamentally **unknowable** for any skill never
Read in a surviving transcript/session log. This backfill recovers what is
recoverable from the logs; absence of an event does NOT prove a skill was
unused before the retained window. Skill-tool (``/skill``) invocations are
recoverable but use plugin-namespaced ids needing id->short_name resolution and
are explicitly DEFERRED to #3137 — this tool emits only Read-of-SKILL.md events.

Usage
-----
  uv run --no-project python scripts/skills/backfill_skill_invocations.py \\
      [--transcripts-root ~/.claude/projects] \\
      [--sessions-dir .claude/state/sessions ...] \\
      [--out-dir .claude/state/sessions] \\
      [--since YYYY-MM-DD] [--until YYYY-MM-DD]

PII note: only ``skill_name`` (rel-path), ``session_id``, ``ts`` and a couple of
provenance tags are emitted — never prompts, file contents, or tool args.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Reuse the tracker's regex for *intent* compatibility only (NOT as the key).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill_execution_tracker import SKILL_PATH_RE  # noqa: E402,F401

# Full-depth rel-path extraction: capture everything between `/.claude/skills/`
# and the trailing `/SKILL.md`. This mirrors session-logger.sh
# (`${FILE##*/.claude/skills/}` minus `/SKILL.md`) and the scanner's
# discover_skills() full-depth join key — unlike SKILL_PATH_RE's 2-segment
# capture. `.+?` (one-or-more, non-greedy) requires at least one segment.
_FULL_SKILL_PATH_RE = re.compile(r"/\.claude/skills/(.+?)/SKILL\.md$")


def rel_path_from(file_path: str | None) -> str | None:
    """Return the FULL rel-path under .claude/skills/ for a SKILL.md path.

    e.g. '/x/.claude/skills/engineering/marine-offshore/aqwa/input/SKILL.md'
         -> 'engineering/marine-offshore/aqwa/input'
    Returns None for non-SKILL.md paths or falsy input. Matches under worktree
    roots too (the regex anchors on '/.claude/skills/.../SKILL.md').
    """
    if not file_path:
        return None
    m = _FULL_SKILL_PATH_RE.search(file_path)
    return m.group(1) if m else None


def _safe_json(line: str):
    try:
        return json.loads(line)
    except (json.JSONDecodeError, ValueError):
        return None


def iter_transcript_events(transcripts_root):
    """Stream Read-of-SKILL.md events from Claude transcripts.

    Reads each .jsonl line-by-line (never read_text() of whole files) so
    thousands of multi-MB transcripts never all sit in memory. Yields dicts:
      {skill_name (rel-path), ts, session_id, tool, hook, source}.
    Skips: malformed lines, non-Read tool_use (Grep/Edit/...), and the Skill
    tool (deferred #3137).
    """
    root = Path(transcripts_root)
    if not root.exists():
        return
    for jsonl in sorted(root.rglob("*.jsonl")):
        try:
            fh = jsonl.open(encoding="utf-8")
        except OSError:
            continue
        with fh:
            for line in fh:
                if "SKILL.md" not in line:  # cheap pre-filter
                    continue
                rec = _safe_json(line)
                if rec is None:
                    continue
                msg = rec.get("message")
                content = msg.get("content") if isinstance(msg, dict) else None
                if not isinstance(content, list):
                    continue
                ts = rec.get("timestamp")
                sid = rec.get("sessionId")
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") != "tool_use":
                        continue
                    # Only the Read tool counts. 'Skill' deferred to #3137;
                    # 'Grep'/'Edit'/etc. of a SKILL.md are not invocations.
                    if block.get("name") != "Read":
                        continue
                    inp = block.get("input")
                    fp = inp.get("file_path") if isinstance(inp, dict) else None
                    rel = rel_path_from(fp)
                    if not rel or not ts:
                        continue
                    yield {
                        "skill_name": rel,
                        "ts": ts,
                        "session_id": sid or "",
                        "tool": "Read",
                        "hook": "backfill",
                        "source": "transcript",
                    }


def iter_sessionlog_events(sessions_dir):
    """Stream Read-of-SKILL.md events from existing session_*.jsonl logs.

    These already carry a `file` field + `session_id`, but no derived
    `skill_name` (it shipped after they were written). Yields the same envelope.
    """
    sdir = Path(sessions_dir)
    if not sdir.exists():
        return
    for path in sorted(sdir.glob("session_*.jsonl")):
        # Skip our own output so re-runs over the same dir don't double-count.
        if path.name.endswith(".backfill.jsonl"):
            continue
        try:
            fh = path.open(encoding="utf-8")
        except OSError:
            continue
        with fh:
            for line in fh:
                line = line.strip()
                if not line or "SKILL.md" not in line:
                    continue
                ev = _safe_json(line)
                if not isinstance(ev, dict):
                    continue
                if ev.get("tool") != "Read":
                    continue
                rel = rel_path_from(ev.get("file"))
                ts = ev.get("ts")
                if not rel or not ts:
                    continue
                yield {
                    "skill_name": rel,
                    "ts": ts,
                    "session_id": ev.get("session_id", "") or "",
                    "tool": "Read",
                    "hook": "backfill",
                    "source": "sessionlog",
                }


def _day_from_ts(ts: str) -> str | None:
    """YYYYMMDD from an ISO ts ('2026-05-01T...' -> '20260501'). None if bad."""
    if not ts or len(ts) < 10 or ts[4] != "-" or ts[7] != "-":
        return None
    return ts[:4] + ts[5:7] + ts[8:10]


def _load_existing_dedup(out_dir: Path) -> set:
    """Seed the dedup index from previously-written *.backfill.jsonl rows so a
    re-run is a no-op (idempotency contract)."""
    seen = set()
    if not out_dir.exists():
        return seen
    for path in sorted(out_dir.glob("session_*.backfill.jsonl")):
        try:
            fh = path.open(encoding="utf-8")
        except OSError:
            continue
        with fh:
            for line in fh:
                ev = _safe_json(line)
                if isinstance(ev, dict):
                    seen.add((ev.get("session_id", ""), ev.get("ts", ""), ev.get("skill_name", "")))
    return seen


def backfill(transcripts_root=None, sessions_dirs=None, out_dir=".claude/state/sessions",
             since=None, until=None):
    """Reconstruct events from all sources into per-day *.backfill.jsonl files.

    Idempotent (dedup key = (session_id, ts, skill_name); seeded from prior
    output). Streams per-line. Date-windowed by --since/--until (inclusive,
    YYYY-MM-DD, compared on the event's calendar day). Returns a stats dict.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    seen = _load_existing_dedup(out)

    sources = []
    if transcripts_root is not None:
        sources.append(iter_transcript_events(transcripts_root))
    for sd in (sessions_dirs or []):
        sources.append(iter_sessionlog_events(sd))

    since_c = since.replace("-", "") if since else None
    until_c = until.replace("-", "") if until else None

    handles: dict[str, "object"] = {}
    written = 0
    skills: set[str] = set()
    days: set[str] = set()
    try:
        for src in sources:
            for ev in src:
                day = _day_from_ts(ev["ts"])
                if day is None:
                    continue
                if since_c and day < since_c:
                    continue
                if until_c and day > until_c:
                    continue
                key = (ev["session_id"], ev["ts"], ev["skill_name"])
                if key in seen:
                    continue
                seen.add(key)
                fh = handles.get(day)
                if fh is None:
                    fh = (out / f"session_{day}.backfill.jsonl").open("a", encoding="utf-8")
                    handles[day] = fh
                fh.write(json.dumps(ev, ensure_ascii=False) + "\n")
                written += 1
                skills.add(ev["skill_name"])
                days.add(day)
    finally:
        for fh in handles.values():
            fh.close()

    return {
        "events_written": written,
        "distinct_skills": len(skills),
        "distinct_days": len(days),
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Backfill historical skill-invocation events from transcripts/logs (#3138)"
    )
    default_transcripts = Path(os.path.expanduser("~/.claude/projects"))
    p.add_argument("--transcripts-root", type=Path, default=default_transcripts,
                   help="Root of Claude transcripts (~/.claude/projects)")
    p.add_argument("--sessions-dir", action="append", default=None, dest="sessions_dirs",
                   help="Existing session-log dir(s); repeatable. "
                        "(e.g. .claude/state/sessions, logs/orchestrator/claude)")
    p.add_argument("--out-dir", type=Path, default=Path(".claude/state/sessions"),
                   help="Where to write session_<day>.backfill.jsonl files")
    p.add_argument("--since", default=None, help="Inclusive lower bound, YYYY-MM-DD")
    p.add_argument("--until", default=None, help="Inclusive upper bound, YYYY-MM-DD")
    p.add_argument("--no-transcripts", action="store_true",
                   help="Skip the transcripts source (session logs only)")
    args = p.parse_args(argv)

    stats = backfill(
        transcripts_root=None if args.no_transcripts else args.transcripts_root,
        sessions_dirs=args.sessions_dirs,
        out_dir=args.out_dir,
        since=args.since,
        until=args.until,
    )
    print(
        f"backfill: wrote {stats['events_written']} new events "
        f"({stats['distinct_skills']} skills, {stats['distinct_days']} days) "
        f"to {args.out_dir}/session_*.backfill.jsonl"
    )
    print("NOTE: pre-instrumentation usage is unknowable — absence of an event "
          "does NOT prove a skill was unused before the retained log window "
          "(#3112). Skill-tool events are deferred to #3137.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
