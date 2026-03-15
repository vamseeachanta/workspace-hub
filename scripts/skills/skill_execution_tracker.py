"""Parse session logs into structured skill execution records (WRK-5086).

Reads .claude/state/sessions/session_YYYYMMDD.jsonl files and extracts
skill invocations into skill-executions.jsonl for automated improvement.

Usage:
    uv run --no-project python scripts/skills/skill_execution_tracker.py [--sessions-dir DIR] [--output PATH]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SKILL_PATH_RE = re.compile(r"/\.claude/skills/([^/]+/[^/]+)/SKILL\.md$")


def parse_session_log(path: Path) -> list[dict]:
    """Parse a JSONL session log, skipping malformed lines."""
    entries: list[dict] = []
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return entries
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def _extract_skill_name_from_path(file_path: str) -> str | None:
    """Extract skill name from a SKILL.md file path."""
    m = SKILL_PATH_RE.search(file_path)
    if m:
        # e.g. "workspace-hub/work-queue" -> "work-queue"
        return m.group(1).split("/")[-1]
    return None


def extract_skill_invocations(entries: list[dict], session_id: str) -> list[dict]:
    """Extract skill invocations from paired pre/post hook entries."""
    if not entries:
        return []

    invocations: list[dict] = []
    seen_skills: set[tuple[str, int]] = set()  # (skill_name, epoch) dedup

    i = 0
    while i < len(entries) - 1:
        entry = entries[i]
        hook = entry.get("hook", "")
        tool = entry.get("tool", "")

        if hook != "pre":
            i += 1
            continue

        # Look for matching post entry
        post = entries[i + 1] if i + 1 < len(entries) else None
        if not post or post.get("hook") != "post":
            i += 1
            continue

        skill_name: str | None = None

        if tool == "Skill":
            skill_name = "Skill"
        elif tool == "Read":
            file_path = entry.get("file", "")
            skill_name = _extract_skill_name_from_path(file_path)

        if skill_name is not None:
            epoch = entry.get("epoch", 0)
            dedup_key = (skill_name, epoch)
            if dedup_key not in seen_skills:
                seen_skills.add(dedup_key)
                pre_epoch = entry.get("epoch", 0)
                post_epoch = post.get("epoch", 0)
                invocations.append({
                    "skill_name": skill_name,
                    "timestamp": entry.get("ts", ""),
                    "session_id": session_id,
                    "project": entry.get("project", ""),
                    "duration_s": post_epoch - pre_epoch,
                })
            i += 2
            continue

        i += 1

    return invocations


def write_executions_jsonl(invocations: list[dict], output_path: Path) -> None:
    """Append skill execution records to JSONL file."""
    if not invocations:
        return
    with open(output_path, "a", encoding="utf-8") as f:
        for inv in invocations:
            f.write(json.dumps(inv, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract skill invocations from session logs")
    parser.add_argument("--sessions-dir", default=".claude/state/sessions", help="Session logs directory")
    parser.add_argument("--output", default=".claude/state/skill-executions.jsonl", help="Output JSONL path")
    parser.add_argument("--date", help="Process only session_YYYYMMDD.jsonl for this date")
    args = parser.parse_args()

    sessions_dir = Path(args.sessions_dir)
    output_path = Path(args.output)

    if args.date:
        logs = [sessions_dir / f"session_{args.date}.jsonl"]
        logs = [l for l in logs if l.exists()]
    else:
        logs = sorted(sessions_dir.glob("session_*.jsonl"))

    total = 0
    for log_file in logs:
        session_id = log_file.stem.replace("session_", "")
        entries = parse_session_log(log_file)
        invocations = extract_skill_invocations(entries, session_id=session_id)
        if invocations:
            write_executions_jsonl(invocations, output_path)
            total += len(invocations)

    print(f"Extracted {total} skill invocations from {len(logs)} session logs -> {output_path}")


if __name__ == "__main__":
    main()
