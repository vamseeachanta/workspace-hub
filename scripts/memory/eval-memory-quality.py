#!/usr/bin/env python3
"""eval-memory-quality.py — Read-only quality metrics for workspace-hub memory files.

Usage:
    uv run --no-project python scripts/memory/eval-memory-quality.py \\
        --memory-root <path> [--work-queue-root <path>] [--format json|md] [--check-paths]

    uv run --no-project python scripts/memory/eval-memory-quality.py \\
        --compare before.json after.json

Metrics:
    pct_done_wrk        % bullets referencing done/archived WRK items
    pct_stale_paths     % bullets with non-existent filesystem paths (opt-in)
    signal_density      bullets per line (across all memory files)
    memory_md_headroom  lines remaining before MEMORY.md hits 180L limit
    topic_file_headroom per-file dict of lines remaining before 140L limit
    dedup_candidates    count of bullets with >=90% token overlap

This script is read-only — it never writes to or modifies memory files.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# ── Constants (mirrors compact-memory.py) ────────────────────────────────────

MEMORY_MD_LIMIT = 180
TOPIC_FILE_LIMIT = 140
DEDUP_OVERLAP_THRESHOLD = 0.90
DEDUP_MIN_TOKENS = 4


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_wrk_ids(text: str) -> list[str]:
    return re.findall(r"\bWRK-\d+\b", text)


def _find_paths_in_line(line: str) -> list[str]:
    return re.findall(r"(?:^|[\s`'\"])(/(?:[\w./\-_~]+))", line)


def _is_done_wrk(wrk_id: str, work_queue_root: Path) -> bool:
    """Return True if wrk_id has status: done in any archive/working/pending file."""
    for md in work_queue_root.rglob(f"{wrk_id}.md"):
        text = md.read_text(encoding="utf-8", errors="replace")
        if re.search(r"^status:\s*done", text, re.MULTILINE):
            return True
    return False


def _read_all_files(memory_root: Path) -> tuple[list[str], dict[str, list[str]]]:
    """Return (memory_md_lines, {filename: lines}) for topic files."""
    memory_md = memory_root / "MEMORY.md"
    mem_lines = memory_md.read_text(encoding="utf-8").splitlines() if memory_md.exists() else []

    topic_files: dict[str, list[str]] = {}
    for f in sorted(memory_root.glob("*.md")):
        if f.name == "MEMORY.md":
            continue
        topic_files[f.name] = f.read_text(encoding="utf-8").splitlines()

    return mem_lines, topic_files


def _collect_bullets(
    mem_lines: list[str], topic_files: dict[str, list[str]]
) -> list[str]:
    """Collect all bullet lines from MEMORY.md and topic files."""
    bullets: list[str] = []
    for line in mem_lines:
        if line.strip().startswith("-"):
            bullets.append(line.strip())
    for lines in topic_files.values():
        for line in lines:
            if line.strip().startswith("-"):
                bullets.append(line.strip())
    return bullets


# ── Metric computation ────────────────────────────────────────────────────────

def compute_pct_done_wrk(bullets: list[str], work_queue_root: Path | None) -> float:
    """% of bullets that reference a done/archived WRK item."""
    if not bullets or work_queue_root is None or not work_queue_root.exists():
        return 0.0
    done_count = 0
    for bullet in bullets:
        wrk_ids = _parse_wrk_ids(bullet)
        if any(_is_done_wrk(w, work_queue_root) for w in wrk_ids):
            done_count += 1
    return round(done_count / len(bullets) * 100, 2)


def compute_pct_stale_paths(bullets: list[str]) -> float:
    """% of bullets containing non-existent filesystem paths."""
    if not bullets:
        return 0.0
    stale_count = 0
    for bullet in bullets:
        paths = _find_paths_in_line(bullet)
        if any(not Path(os.path.expanduser(p)).exists() for p in paths):
            stale_count += 1
    return round(stale_count / len(bullets) * 100, 2)


def compute_signal_density(
    bullets: list[str], mem_lines: list[str], topic_files: dict[str, list[str]]
) -> float:
    """Bullets per line across all memory files."""
    total_lines = len(mem_lines) + sum(len(v) for v in topic_files.values())
    if total_lines == 0:
        return 0.0
    return round(len(bullets) / total_lines, 4)


def compute_memory_md_headroom(mem_lines: list[str]) -> int:
    """Lines remaining before MEMORY.md hits the 180L limit."""
    return max(0, MEMORY_MD_LIMIT - len(mem_lines))


def compute_topic_file_headroom(topic_files: dict[str, list[str]]) -> dict[str, int]:
    """Per-file dict of lines remaining before 140L limit."""
    return {name: max(0, TOPIC_FILE_LIMIT - len(lines)) for name, lines in topic_files.items()}


def compute_dedup_candidates(
    mem_lines: list[str], topic_files: dict[str, list[str]]
) -> int:
    """Count bullets with >=90% token overlap within the same file."""
    total = 0
    all_groups: list[list[str]] = [
        [l.strip() for l in mem_lines if l.strip().startswith("-")]
    ]
    for lines in topic_files.values():
        all_groups.append([l.strip() for l in lines if l.strip().startswith("-")])

    for group in all_groups:
        evict: set[int] = set()
        for i, bi in enumerate(group):
            if i in evict:
                continue
            ti = set(bi.lower().split())
            if len(ti) < DEDUP_MIN_TOKENS:
                continue
            for j in range(i + 1, len(group)):
                if j in evict:
                    continue
                bj = group[j]
                tj = set(bj.lower().split())
                if len(tj) < DEDUP_MIN_TOKENS:
                    continue
                overlap = len(ti & tj) / max(len(ti), len(tj))
                if overlap >= DEDUP_OVERLAP_THRESHOLD:
                    evict.add(i)
                    break
        total += len(evict)
    return total


# ── Report formatting ─────────────────────────────────────────────────────────

def format_json(metrics: dict) -> str:
    return json.dumps(metrics, indent=2)


def format_md(metrics: dict) -> str:
    rows = [
        "| Metric | Value |",
        "|--------|-------|",
    ]
    for key, val in metrics.items():
        if isinstance(val, dict):
            for sub_key, sub_val in val.items():
                rows.append(f"| topic_file_headroom[{sub_key}] | {sub_val} |")
        else:
            rows.append(f"| {key} | {val} |")
    return "\n".join(rows)


def format_compare(before: dict, after: dict) -> str:
    rows = [
        "| Metric | Before | After | Delta |",
        "|--------|--------|-------|-------|",
    ]
    all_keys = list(before.keys())
    for key in all_keys:
        b_val = before.get(key, "—")
        a_val = after.get(key, "—")
        if isinstance(b_val, (int, float)) and isinstance(a_val, (int, float)):
            delta = round(a_val - b_val, 4)
            delta_str = f"{delta:+g}"
        elif isinstance(b_val, dict) and isinstance(a_val, dict):
            rows.append(f"| {key} | (dict) | (dict) | — |")
            continue
        else:
            delta_str = "—"
        rows.append(f"| {key} | {b_val} | {a_val} | {delta_str} |")
    return "\n".join(rows)


# ── CLI ───────────────────────────────────────────────────────────────────────

def run_eval(args: argparse.Namespace) -> int:
    memory_root = Path(args.memory_root).expanduser()
    if not memory_root.exists():
        print(f"ERROR: memory root does not exist: {memory_root}", file=sys.stderr)
        return 1

    work_queue_root: Path | None = None
    if args.work_queue_root:
        work_queue_root = Path(args.work_queue_root).expanduser()
    else:
        # Auto-discover from parents
        for parent in memory_root.parents:
            candidate = parent / ".claude" / "work-queue"
            if candidate.exists():
                work_queue_root = candidate
                break

    mem_lines, topic_files = _read_all_files(memory_root)
    bullets = _collect_bullets(mem_lines, topic_files)

    metrics: dict = {
        "pct_done_wrk": compute_pct_done_wrk(bullets, work_queue_root),
        "pct_stale_paths": (
            compute_pct_stale_paths(bullets) if args.check_paths else 0.0
        ),
        "signal_density": compute_signal_density(bullets, mem_lines, topic_files),
        "memory_md_headroom": compute_memory_md_headroom(mem_lines),
        "topic_file_headroom": compute_topic_file_headroom(topic_files),
        "dedup_candidates": compute_dedup_candidates(mem_lines, topic_files),
    }

    fmt = getattr(args, "format", "json") or "json"
    if fmt == "md":
        print(format_md(metrics))
    else:
        print(format_json(metrics))
    return 0


def run_compare(args: argparse.Namespace) -> int:
    before_path = Path(args.compare[0])
    after_path = Path(args.compare[1])
    before = json.loads(before_path.read_text(encoding="utf-8"))
    after = json.loads(after_path.read_text(encoding="utf-8"))
    print(format_compare(before, after))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate memory quality metrics (read-only)."
    )
    parser.add_argument("--memory-root", help="Path to memory directory")
    parser.add_argument(
        "--work-queue-root", default=None,
        help="Path to .claude/work-queue (for done-WRK lookup)",
    )
    parser.add_argument(
        "--format", choices=["json", "md"], default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--check-paths", action="store_true",
        help="Flag bullets with non-existent filesystem paths (opt-in)",
    )
    parser.add_argument(
        "--compare", nargs=2, metavar=("BEFORE", "AFTER"),
        help="Compare two JSON reports and print delta per metric",
    )
    args = parser.parse_args()

    if args.compare:
        return run_compare(args)

    if not args.memory_root:
        parser.error("--memory-root is required unless --compare is used")

    return run_eval(args)


if __name__ == "__main__":
    sys.exit(main())
