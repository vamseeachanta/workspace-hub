"""TDD tests for scripts/skills/backfill_skill_invocations.py (#3138).

Reconstructs historical {skill_name (rel-path), ts, session_id} skill-invocation
events from Claude transcripts (~/.claude/projects/**/*.jsonl) and existing
session logs, writing them into the scanner-consumable session_*.jsonl envelope
so the #3112 scanner -> report -> demotion chain can act on a >=14d window now.

Key contracts under test:
  - FULL rel-path extraction under .claude/skills/ (matches session-logger.sh's
    `${FILE##*/.claude/skills/}` minus /SKILL.md), NOT the 2-segment
    SKILL_PATH_RE capture nor _extract_skill_name_from_path's basename. Includes
    a DEEP nested-skill case (4 path segments).
  - Skill-tool events are SKIPPED (deferred to #3137); only Read-of-SKILL.md.
  - Idempotency: re-running over the same input adds zero rows.
  - Malformed lines are skipped without aborting the file.
  - Date-windowing (--since / --until).
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(
    subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=Path(__file__).parent,
        text=True,
    ).strip()
)
BACKFILL_PATH = REPO_ROOT / "scripts" / "skills" / "backfill_skill_invocations.py"
SCANNER_PATH = REPO_ROOT / "scripts" / "skills" / "skill-invocation-scanner.py"


def _load_module(path: Path, modname: str):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def bf():
    assert BACKFILL_PATH.exists(), f"backfill not yet written: {BACKFILL_PATH}"
    return _load_module(BACKFILL_PATH, "backfill_skill_invocations")


# ---------------------------------------------------------------------------
# rel-path extraction (the CRITICAL TRAP: full depth, not 2-segment capture)
# ---------------------------------------------------------------------------


def test_rel_path_from_main_checkout(bf):
    fp = "/x/.claude/skills/coordination/issue-planning-mode/SKILL.md"
    assert bf.rel_path_from(fp) == "coordination/issue-planning-mode"


def test_rel_path_from_worktree(bf):
    # Matches under a worktree root too — regex anchors on /.claude/skills/.
    fp = "/mnt/local-analysis/reconcile-main-20260427/.claude/skills/development/x/SKILL.md"
    assert bf.rel_path_from(fp) == "development/x"


def test_rel_path_deep_nested_skill(bf):
    """CRITICAL: deep (4-segment) skills must yield the FULL rel-path.

    SKILL_PATH_RE captures only two segments; the scanner's discover_skills join
    key is the full rel-path. A 2-segment extraction would silently fail the
    demotion join for every deep-nested skill.
    """
    fp = "/repo/.claude/skills/engineering/marine-offshore/aqwa/input/SKILL.md"
    assert bf.rel_path_from(fp) == "engineering/marine-offshore/aqwa/input"


def test_rel_path_three_segment_skill(bf):
    fp = "/repo/.claude/skills/research/llm-wiki/public-private-routing/SKILL.md"
    assert bf.rel_path_from(fp) == "research/llm-wiki/public-private-routing"


def test_rel_path_none_for_non_skill(bf):
    assert bf.rel_path_from("/x/src/foo.py") is None
    assert bf.rel_path_from("/x/.claude/skills/a/README.md") is None
    assert bf.rel_path_from("") is None
    assert bf.rel_path_from(None) is None


# ---------------------------------------------------------------------------
# transcript parsing
# ---------------------------------------------------------------------------


def _transcript_record(name, file_path, ts="2026-05-01T10:00:00.000Z", sid="sess-1"):
    return {
        "type": "assistant",
        "timestamp": ts,
        "sessionId": sid,
        "message": {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "thinking"},
                {
                    "type": "tool_use",
                    "name": name,
                    "input": {"file_path": file_path},
                },
            ],
        },
    }


def _write_jsonl(path: Path, records):
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            if isinstance(r, str):
                f.write(r + "\n")
            else:
                f.write(json.dumps(r) + "\n")


def test_transcript_parse_tool_use(bf, tmp_path):
    proj = tmp_path / "projects" / "-some-proj"
    proj.mkdir(parents=True)
    _write_jsonl(
        proj / "t.jsonl",
        [_transcript_record("Read", "/r/.claude/skills/email/gmail-triage/SKILL.md")],
    )
    events = list(bf.iter_transcript_events(tmp_path / "projects"))
    assert len(events) == 1
    ev = events[0]
    assert ev["skill_name"] == "email/gmail-triage"
    assert ev["ts"] == "2026-05-01T10:00:00.000Z"
    assert ev["session_id"] == "sess-1"
    assert ev["tool"] == "Read"


def test_transcript_skips_skill_tool(bf, tmp_path):
    """Skill-tool tool_use events are NOT emitted (deferred to #3137)."""
    proj = tmp_path / "projects" / "-p"
    proj.mkdir(parents=True)
    _write_jsonl(
        proj / "t.jsonl",
        [
            _transcript_record("Skill", "/r/.claude/skills/email/gmail-triage/SKILL.md"),
            {
                "type": "assistant",
                "timestamp": "2026-05-01T10:00:00Z",
                "sessionId": "s",
                "message": {
                    "role": "assistant",
                    "content": [
                        {"type": "tool_use", "name": "Skill",
                         "input": {"command": "superpowers:test-driven-development"}}
                    ],
                },
            },
        ],
    )
    events = list(bf.iter_transcript_events(tmp_path / "projects"))
    assert events == [], "Skill-tool events must be skipped (deferred #3137)"


def test_transcript_skips_non_read_tools(bf, tmp_path):
    """Grep/other tool_use on a SKILL.md path is not a skill invocation."""
    proj = tmp_path / "projects" / "-p"
    proj.mkdir(parents=True)
    _write_jsonl(
        proj / "t.jsonl",
        [_transcript_record("Grep", "/r/.claude/skills/email/gmail-triage/SKILL.md")],
    )
    assert list(bf.iter_transcript_events(tmp_path / "projects")) == []


def test_transcript_malformed_line_skipped(bf, tmp_path):
    proj = tmp_path / "projects" / "-p"
    proj.mkdir(parents=True)
    _write_jsonl(
        proj / "t.jsonl",
        [
            "{ this is not json",
            _transcript_record("Read", "/r/.claude/skills/a/b/SKILL.md"),
            "",
        ],
    )
    events = list(bf.iter_transcript_events(tmp_path / "projects"))
    assert len(events) == 1
    assert events[0]["skill_name"] == "a/b"


# ---------------------------------------------------------------------------
# session-log parsing (existing logs carry `file` but no skill_name)
# ---------------------------------------------------------------------------


def test_sessionlog_parse_file_field(bf, tmp_path):
    sdir = tmp_path / "sessions"
    sdir.mkdir()
    _write_jsonl(
        sdir / "session_20260501.jsonl",
        [
            {"ts": "2026-05-01T09:00:00+00:00", "tool": "Read",
             "file": "/r/.claude/skills/a/b/SKILL.md", "session_id": "sl-1"},
            {"ts": "2026-05-01T09:01:00+00:00", "tool": "Read",
             "file": "/r/src/main.py", "session_id": "sl-1"},  # not a skill
        ],
    )
    events = list(bf.iter_sessionlog_events(sdir))
    assert len(events) == 1
    assert events[0]["skill_name"] == "a/b"
    assert events[0]["session_id"] == "sl-1"


# ---------------------------------------------------------------------------
# backfill: idempotency, dedup, windowing
# ---------------------------------------------------------------------------


def _setup_transcripts(tmp_path, records):
    proj = tmp_path / "projects" / "-p"
    proj.mkdir(parents=True)
    _write_jsonl(proj / "t.jsonl", records)
    return tmp_path / "projects"


def test_backfill_emit_format_and_writes(bf, tmp_path):
    pdir = _setup_transcripts(
        tmp_path,
        [_transcript_record("Read", "/r/.claude/skills/a/b/SKILL.md",
                            ts="2026-05-01T10:00:00.000Z", sid="s1")],
    )
    out = tmp_path / "out"
    stats = bf.backfill(transcripts_root=pdir, sessions_dirs=[], out_dir=out)
    f = out / "session_20260501.backfill.jsonl"
    assert f.exists()
    rows = [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
    assert len(rows) == 1
    r = rows[0]
    # Must be consumable by scan_sessions: skill_name + ts + session_id present.
    assert r["skill_name"] == "a/b"
    assert r["ts"] == "2026-05-01T10:00:00.000Z"
    assert r["session_id"] == "s1"
    assert stats["events_written"] == 1


def test_idempotent_rerun(bf, tmp_path):
    pdir = _setup_transcripts(
        tmp_path,
        [_transcript_record("Read", "/r/.claude/skills/a/b/SKILL.md",
                            ts="2026-05-01T10:00:00.000Z", sid="s1")],
    )
    out = tmp_path / "out"
    bf.backfill(transcripts_root=pdir, sessions_dirs=[], out_dir=out)
    f = out / "session_20260501.backfill.jsonl"
    first = f.read_text()
    stats2 = bf.backfill(transcripts_root=pdir, sessions_dirs=[], out_dir=out)
    assert f.read_text() == first, "second run must be byte-identical (idempotent)"
    assert stats2["events_written"] == 0


def test_dedup_key_across_sources(bf, tmp_path):
    """Same (session_id, ts, skill_name) from transcript + sessionlog -> one row."""
    ts = "2026-05-01T10:00:00.000Z"
    pdir = _setup_transcripts(
        tmp_path,
        [_transcript_record("Read", "/r/.claude/skills/a/b/SKILL.md", ts=ts, sid="dup")],
    )
    sdir = tmp_path / "sessions"
    sdir.mkdir()
    _write_jsonl(
        sdir / "session_20260501.jsonl",
        [{"ts": ts, "tool": "Read", "file": "/r/.claude/skills/a/b/SKILL.md",
          "session_id": "dup"}],
    )
    out = tmp_path / "out"
    stats = bf.backfill(transcripts_root=pdir, sessions_dirs=[sdir], out_dir=out)
    rows = [json.loads(l) for l in (out / "session_20260501.backfill.jsonl").read_text().splitlines() if l.strip()]
    assert len(rows) == 1
    assert stats["events_written"] == 1


def test_date_window_since_until(bf, tmp_path):
    pdir = _setup_transcripts(
        tmp_path,
        [
            _transcript_record("Read", "/r/.claude/skills/a/b/SKILL.md",
                               ts="2026-04-30T10:00:00.000Z", sid="s"),
            _transcript_record("Read", "/r/.claude/skills/a/b/SKILL.md",
                               ts="2026-05-01T10:00:00.000Z", sid="s"),
            _transcript_record("Read", "/r/.claude/skills/a/b/SKILL.md",
                               ts="2026-05-02T10:00:00.000Z", sid="s"),
        ],
    )
    out = tmp_path / "out"
    bf.backfill(transcripts_root=pdir, sessions_dirs=[], out_dir=out,
                since="2026-05-01", until="2026-05-01")
    files = sorted(p.name for p in out.glob("*.backfill.jsonl"))
    assert files == ["session_20260501.backfill.jsonl"]


# ---------------------------------------------------------------------------
# end-to-end: scanner consumes backfill output and the coverage gate flips
# ---------------------------------------------------------------------------


def test_scanner_reads_backfill_output_coverage_gate(bf, tmp_path):
    """20-day backfill for a real skill -> scanner reports coverage_days>=14
    and nonzero session_count for that skill; should_demote flips for the
    zero-session universe."""
    scanner = _load_module(SCANNER_PATH, "skill_invocation_scanner")

    # Build a tiny skills root with one deep-nested skill so the join is exercised.
    skills_root = tmp_path / "skills"
    skill_dir = skills_root / "engineering" / "marine-offshore" / "aqwa"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: aqwa\n---\nbody\n")

    # 20 days of Read events for that skill (full rel-path key).
    recs = []
    for day in range(1, 21):
        recs.append(
            _transcript_record(
                "Read",
                f"/r/.claude/skills/engineering/marine-offshore/aqwa/SKILL.md",
                ts=f"2026-05-{day:02d}T10:00:00.000Z",
                sid=f"s{day}",
            )
        )
    pdir = _setup_transcripts(tmp_path, recs)
    out = tmp_path / "out"
    bf.backfill(transcripts_root=pdir, sessions_dirs=[], out_dir=out)

    event_ts, session_ts, coverage = scanner.scan_sessions(out)
    assert coverage >= 14, f"expected >=14d coverage, got {coverage}"
    # scanner keys events on the FULL rel-path produced by discover_skills.
    assert "engineering/marine-offshore/aqwa" in event_ts
    assert len(session_ts["engineering/marine-offshore/aqwa"]) == 20

    rows = scanner.classify(event_ts, session_ts, coverage, skills_root)
    aqwa = [r for r in rows if r["skill"] == "aqwa"]
    assert aqwa and aqwa[0]["session_count_available_days"] == 20

    # Coverage gate: a zero-session skill is now demotable (>=14d observed).
    assert scanner.should_demote(session_count=0, coverage_days=coverage) is True
