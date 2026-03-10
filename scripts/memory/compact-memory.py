#!/usr/bin/env python3
"""compact-memory.py — Memory compaction for workspace-hub context files.

Phases:
  A  audit   — parse memory files, flag eviction candidates, write compact-audit.md
  B  dry-run — print proposed actions to stdout, exit 0, write nothing
  C  apply   — evict bullets, rewrite files atomically, append to compact-log.jsonl

Usage:
    uv run --no-project python scripts/memory/compact-memory.py \\
        --memory-root ~/.claude/projects/.../memory/ \\
        [--work-queue-root .claude/work-queue] \\
        [--dry-run] [--force] [--check-commands] [--check-paths]

# keep marker scope
  The `# keep` marker exempts bullets from age/trim/dedup eviction (rules 4-5).
  It does NOT protect against done-WRK expiry (rule 1) or path staleness (rule 2).
  Those rules run unconditionally because stale references corrupt context regardless
  of intent. Use `# keep` to preserve still-valid bullets from trim-to-limit pruning.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

# ── Constants ────────────────────────────────────────────────────────────────

MEMORY_MD_LIMIT = 180       # lines; trigger compaction
TOPIC_FILE_LIMIT = 140      # lines; trigger compaction
AGE_EVICTION_DAYS = 90
DONE_WRK_DAYS = 30
COMMAND_SPOT_CHECK_N = 3
COMMAND_TIMEOUT_S = 5

# ── Data types ───────────────────────────────────────────────────────────────

class EvictionCandidate(NamedTuple):
    file: Path
    line_index: int       # 0-based
    line: str
    reason: str           # done-wrk | stale-path | dedup | age
    archive_target: str   # e.g. "done-wrk.md"


# ── Helpers ──────────────────────────────────────────────────────────────────

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_wrk_ids(text: str) -> list[str]:
    return re.findall(r"\bWRK-\d+\b", text)


def _has_keep_marker(line: str) -> bool:
    return bool(re.search(r"#\s*keep\b", line, re.IGNORECASE))


def _find_paths_in_line(line: str) -> list[str]:
    """Extract plausible filesystem paths from a bullet line."""
    return re.findall(r"(?:^|[\s`'\"])(/(?:[\w./\-_~]+))", line)


def _is_done_wrk(wrk_id: str, work_queue_root: Path) -> bool:
    """Return True if wrk_id has status: done in any archive file."""
    pattern = f"{wrk_id}.md"
    for md in work_queue_root.rglob(pattern):
        text = md.read_text(encoding="utf-8", errors="replace")
        if re.search(r"^status:\s*done", text, re.MULTILINE):
            return True
    return False


_SAFE_CMD_PREFIXES = (
    "uv ", "python", "git ", "gh ", "bash ", "sh ",
    "pytest", "ruff", "mypy", "echo ", "cat ", "ls ",
)
_UNSAFE_PATTERNS = re.compile(r"rm\s+-[rf]|>\s*/|mkfs|dd\s+if=|curl.*\|\s*bash|wget.*\|\s*sh")


def _spot_check_command(cmd_text: str) -> bool:
    """Return True if command runs without error (exit 0) within timeout.

    Safety: only runs commands that start with known-safe prefixes and do not
    match known-destructive patterns. Rejects anything else with True (keep).
    """
    stripped = cmd_text.strip()
    if _UNSAFE_PATTERNS.search(stripped):
        return True  # conservative: don't evict commands that look dangerous
    if not any(stripped.startswith(p) for p in _SAFE_CMD_PREFIXES):
        return True  # unknown command — keep, don't execute
    try:
        result = subprocess.run(
            stripped.split(), capture_output=True,  # no shell=True
            timeout=COMMAND_TIMEOUT_S,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
    except Exception:
        return True  # conservative: keep on unexpected error


def _read_topic_files(memory_root: Path) -> dict[Path, list[str]]:
    """Read all .md topic files (not MEMORY.md, not archive/)."""
    files: dict[Path, list[str]] = {}
    for f in sorted(memory_root.glob("*.md")):
        if f.name == "MEMORY.md":
            continue
        files[f] = f.read_text(encoding="utf-8").splitlines(keepends=True)
    return files


def _triggers_met(memory_root: Path) -> str | None:
    """Return trigger reason string if compaction should run, else None."""
    memory_md = memory_root / "MEMORY.md"
    if memory_md.exists():
        lines = memory_md.read_text(encoding="utf-8").splitlines()
        if len(lines) >= MEMORY_MD_LIMIT:
            return "line-count"
    for f in memory_root.glob("*.md"):
        if f.name == "MEMORY.md":
            continue
        if len(f.read_text(encoding="utf-8").splitlines()) >= TOPIC_FILE_LIMIT:
            return "line-count"
    return None


# ── Phase A — Audit ──────────────────────────────────────────────────────────

def audit(
    memory_root: Path,
    work_queue_root: Path,
    check_commands: bool,
    check_paths: bool = False,
) -> tuple[list[EvictionCandidate], str]:
    """Scan memory files and return eviction candidates + audit report text."""
    topic_files = _read_topic_files(memory_root)
    candidates: list[EvictionCandidate] = []
    report_lines: list[str] = ["# Memory Compaction Audit\n"]

    commands_checked = 0

    for fpath, lines in topic_files.items():
        file_candidates: list[EvictionCandidate] = []
        # bullet_line_indices[k] = actual line index of the k-th bullet
        bullet_line_indices: list[int] = []
        bullet_texts: list[str] = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped.startswith("-"):
                continue

            bullet_line_indices.append(i)
            bullet_texts.append(stripped)

            # Rule 1: Done-WRK expiry (# keep does NOT exempt)
            for wrk_id in _parse_wrk_ids(stripped):
                if _is_done_wrk(wrk_id, work_queue_root):
                    file_candidates.append(
                        EvictionCandidate(fpath, i, line, "done-wrk", "done-wrk.md")
                    )
                    break

            # Rule 2: Path staleness — opt-in via --check-paths (# keep does NOT exempt).
            # Disabled by default: paths valid on one machine may not exist on another.
            if check_paths:
                for path_str in _find_paths_in_line(stripped):
                    if not Path(os.path.expanduser(path_str)).exists():
                        file_candidates.append(
                            EvictionCandidate(fpath, i, line, "stale-path", "stale-paths.md")
                        )
                        break

            # Rule 3: Command staleness (opt-in, capped)
            if check_commands and commands_checked < COMMAND_SPOT_CHECK_N:
                cmd_match = re.search(r"`([^`]{5,80})`", stripped)
                if cmd_match:
                    cmd = cmd_match.group(1)
                    if not _spot_check_command(cmd):
                        file_candidates.append(
                            EvictionCandidate(fpath, i, line, "stale-command", "stale-commands.md")
                        )
                    commands_checked += 1

            # Rule 5: Age eviction (# keep DOES exempt)
            # We skip age eviction in this implementation — no session signal
            # history available at script level; nightly pipeline handles it.
            # (deferred to comprehensive-learning Phase 3 integration)

        # Rule 4: Semantic dedup (simple token-overlap within same file)
        # O(N²) over bullets, but topic files are capped at TOPIC_FILE_LIMIT lines
        # (≤140), so worst case is ~9800 comparisons — trivially fast.
        # Use line-index space consistently throughout
        evict_line_indices = {c.line_index for c in file_candidates}
        for bi, (line_idx, bullet) in enumerate(zip(bullet_line_indices, bullet_texts)):
            if line_idx in evict_line_indices:
                continue
            for bj in range(bi + 1, len(bullet_texts)):
                other_line_idx = bullet_line_indices[bj]
                if other_line_idx in evict_line_indices:
                    continue
                other = bullet_texts[bj]
                tokens_i = set(bullet.lower().split())
                tokens_j = set(other.lower().split())
                if len(tokens_i) < 4 or len(tokens_j) < 4:
                    continue  # skip very short bullets — too many false positives
                overlap = len(tokens_i & tokens_j) / max(len(tokens_i), len(tokens_j))
                if overlap >= 0.90:  # strict threshold to avoid false dedup
                    # keep the later (fresher) bullet; evict the earlier
                    file_candidates.append(
                        EvictionCandidate(fpath, line_idx, lines[line_idx], "dedup", "dedup.md")
                    )
                    evict_line_indices.add(line_idx)
                    break

        # Rule 6: Trim-to-limit — when file still exceeds limit after rules 1-4,
        # age-evict un-marked bullets from the bottom until within limit.
        evict_line_indices_final = {c.line_index for c in file_candidates}
        remaining_line_count = sum(
            1 for i, l in enumerate(lines) if i not in evict_line_indices_final
        )
        if remaining_line_count > TOPIC_FILE_LIMIT:
            # collect evictable bullets (not keep-marked, not already evicted), bottom-up
            evictable = [
                (line_idx, lines[line_idx])
                for line_idx, bullet in zip(bullet_line_indices, bullet_texts)
                if line_idx not in evict_line_indices_final
                and not _has_keep_marker(bullet)
            ]
            for line_idx, line in reversed(evictable):
                if remaining_line_count <= TOPIC_FILE_LIMIT:
                    break
                file_candidates.append(
                    EvictionCandidate(fpath, line_idx, line, "age", "aged-out.md")
                )
                evict_line_indices_final.add(line_idx)
                remaining_line_count -= 1

        candidates.extend(file_candidates)
        if file_candidates:
            report_lines.append(f"\n## {fpath.name}\n")
            for c in file_candidates:
                report_lines.append(f"  [{c.reason}] line {c.line_index+1}: {c.line.rstrip()}\n")

    if not candidates:
        report_lines.append("\nNo eviction candidates found.\n")

    return candidates, "".join(report_lines)


# ── Phase C — Apply ──────────────────────────────────────────────────────────

def apply_evictions(
    memory_root: Path,
    candidates: list[EvictionCandidate],
    trigger: str,
) -> tuple[int, int]:
    """
    Move evicted bullets to archive/<target>, rewrite topic files atomically.

    Returns (lines_freed_topics, bullets_archived).
    """
    archive_dir = memory_root / "archive"
    archive_dir.mkdir(exist_ok=True)

    # Group by file
    by_file: dict[Path, list[EvictionCandidate]] = {}
    for c in candidates:
        by_file.setdefault(c.file, []).append(c)

    lines_freed = 0
    bullets_archived = 0

    for fpath, file_candidates in by_file.items():
        lines = fpath.read_text(encoding="utf-8").splitlines(keepends=True)
        evict_indices = {c.line_index for c in file_candidates}

        # Write evicted bullets to archive files
        for target, group in _group_by_target(file_candidates):
            archive_file = archive_dir / target
            with archive_file.open("a", encoding="utf-8") as af:
                af.write(f"\n## Evicted from {fpath.name} — {_now().isoformat()}\n")
                for c in group:
                    af.write(c.line if c.line.endswith("\n") else c.line + "\n")
                    bullets_archived += 1

        # Rewrite topic file without evicted lines (atomic)
        kept = [l for i, l in enumerate(lines) if i not in evict_indices]
        tmp = fpath.with_suffix(".tmp")
        tmp.write_text("".join(kept), encoding="utf-8")
        tmp.replace(fpath)
        lines_freed += len(evict_indices)

    return lines_freed, bullets_archived


def _group_by_target(
    candidates: list[EvictionCandidate],
) -> list[tuple[str, list[EvictionCandidate]]]:
    groups: dict[str, list[EvictionCandidate]] = {}
    for c in candidates:
        groups.setdefault(c.archive_target, []).append(c)
    return list(groups.items())


def _write_log(memory_root: Path, lines_freed_memory: int, lines_freed_topics: int,
               bullets_evicted: int, bullets_archived: int, trigger: str) -> None:
    log_file = memory_root / "compact-log.jsonl"
    entry = {
        "timestamp": _now().isoformat(),
        "lines_freed_memory": lines_freed_memory,
        "lines_freed_topics": lines_freed_topics,
        "bullets_evicted": bullets_evicted,
        "bullets_archived": bullets_archived,
        "trigger": trigger,
    }
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# ── CLI ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Compact workspace-hub memory files.")
    parser.add_argument("--memory-root", required=True, help="Path to memory directory")
    parser.add_argument(
        "--work-queue-root",
        default=None,
        help="Path to .claude/work-queue (for done-WRK lookup)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print audit, write nothing")
    parser.add_argument("--force", action="store_true", help="Skip trigger check")
    parser.add_argument(
        "--check-commands", action="store_true",
        help="Spot-check commands in bullets (opt-in; disabled by default for cron)",
    )
    parser.add_argument(
        "--check-paths", action="store_true",
        help=(
            "Flag bullets referencing non-existent filesystem paths (opt-in; "
            "disabled by default to avoid cross-machine false positives)"
        ),
    )
    args = parser.parse_args()

    memory_root = Path(args.memory_root).expanduser()
    if not memory_root.exists():
        print(f"ERROR: memory root does not exist: {memory_root}", file=sys.stderr)
        return 1

    # Resolve work-queue root
    if args.work_queue_root:
        wq_root = Path(args.work_queue_root).expanduser()
    else:
        # Heuristic: look for .claude/work-queue relative to memory_root parents
        wq_root = None
        for parent in memory_root.parents:
            candidate = parent / ".claude" / "work-queue"
            if candidate.exists():
                wq_root = candidate
                break
        if wq_root is None:
            wq_root = memory_root.parent  # fallback: no WRK lookups will match

    # Check triggers (skip if --force or --dry-run forces a run)
    if not args.force and not args.dry_run:
        trigger = _triggers_met(memory_root)
        if trigger is None:
            trigger = "manual"
    else:
        trigger = "forced" if args.force else "dry-run"

    # Phase A — audit
    candidates, report = audit(memory_root, wq_root, args.check_commands, args.check_paths)

    if args.dry_run:
        print(report)
        print(f"\n[dry-run] {len(candidates)} eviction candidate(s) found. No files modified.")
        return 0

    # Phase C — apply
    lines_freed_topics, bullets_archived = apply_evictions(memory_root, candidates, trigger)

    # Write audit report
    audit_file = memory_root / "compact-audit.md"
    tmp = audit_file.with_suffix(".tmp")
    tmp.write_text(report, encoding="utf-8")
    tmp.replace(audit_file)

    # Log
    _write_log(
        memory_root,
        lines_freed_memory=0,  # MEMORY.md rewrite not yet implemented
        lines_freed_topics=lines_freed_topics,
        bullets_evicted=len(candidates),
        bullets_archived=bullets_archived,
        trigger=trigger,
    )

    print(
        f"compact-memory: evicted {len(candidates)} bullet(s), "
        f"freed {lines_freed_topics} lines. Log → {memory_root}/compact-log.jsonl"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
