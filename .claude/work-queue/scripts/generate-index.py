#!/usr/bin/env python3
"""Generate INDEX.md for the work queue.

Scans pending/, working/, blocked/, and archive/*/ directories for WRK-*.md
files, parses YAML frontmatter, and generates a structured index with multiple
lookup views.

Usage:
    python .claude/work-queue/scripts/generate-index.py
"""

from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

QUEUE_ROOT = Path(__file__).resolve().parent.parent
STATUS_DIRS = {
    "pending": QUEUE_ROOT / "pending",
    "working": QUEUE_ROOT / "working",
    "blocked": QUEUE_ROOT / "blocked",
}
ARCHIVE_DIR = QUEUE_ROOT / "archive"
INDEX_PATH = QUEUE_ROOT / "INDEX.md"

FRONTMATTER_FIELDS = [
    "id", "title", "status", "priority", "complexity", "target_repos",
    "blocked_by", "related", "children", "parent", "compound", "route",
    "created_at", "completed_at",
    "plan_reviewed", "plan_approved", "percent_complete", "brochure_status",
]


def parse_frontmatter(path: Path) -> dict | None:
    """Extract YAML frontmatter from a markdown file.

    Also auto-detects plan existence from spec_ref or ``## Plan`` section.
    """
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return None
    raw = match.group(1)

    if yaml is not None:
        try:
            data = yaml.safe_load(raw)
            if not isinstance(data, dict):
                data = _regex_parse(raw)
        except yaml.YAMLError:
            data = _regex_parse(raw)
    else:
        data = _regex_parse(raw)

    # Auto-detect plan existence from spec_ref or body ## Plan section
    body = text[match.end():]
    has_spec_ref = bool(data.get("spec_ref"))
    has_plan_section = bool(re.search(r"^## Plan\b", body, re.MULTILINE))
    data["_plan_exists"] = has_spec_ref or has_plan_section

    return data


def _regex_parse(raw: str) -> dict:
    """Minimal YAML-like parser using regex (no dependency)."""
    data: dict = {}
    current_key = None
    list_buffer: list[str] = []

    for line in raw.splitlines():
        # List continuation
        list_match = re.match(r"^\s+-\s+(.*)", line)
        if list_match and current_key:
            list_buffer.append(list_match.group(1).strip().strip("'\""))
            continue

        # Flush previous list
        if current_key and list_buffer:
            data[current_key] = list_buffer
            list_buffer = []
            current_key = None

        kv = re.match(r"^(\w[\w_]*):\s*(.*)", line)
        if not kv:
            continue

        key = kv.group(1)
        val = kv.group(2).strip()

        # Inline list: [a, b, c]
        inline = re.match(r"^\[(.*)\]$", val)
        if inline:
            items = [v.strip().strip("'\"") for v in inline.group(1).split(",") if v.strip()]
            data[key] = items
            current_key = None
            continue

        # Scalar value
        if val == "" or val == "[]":
            current_key = key
            list_buffer = []
            if val == "[]":
                data[key] = []
                current_key = None
            continue

        # Boolean / null
        if val.lower() in ("true", "false"):
            data[key] = val.lower() == "true"
        elif val.lower() in ("null", "~", ""):
            data[key] = None
        else:
            data[key] = val.strip("'\"")

        current_key = None

    if current_key and list_buffer:
        data[current_key] = list_buffer

    return data


def discover_items() -> list[dict]:
    """Find all WRK-*.md files across queue directories."""
    items = []

    # Status directories
    for status_name, dir_path in STATUS_DIRS.items():
        if not dir_path.is_dir():
            continue
        for f in sorted(dir_path.glob("WRK-*.md")):
            fm = parse_frontmatter(f)
            if fm:
                fm["_file"] = str(f.relative_to(QUEUE_ROOT))
                fm.setdefault("status", status_name)
                items.append(fm)

    # Archive: files directly in archive/ and in archive/YYYY-MM/ subdirs
    if ARCHIVE_DIR.is_dir():
        # Files directly in archive/
        for f in sorted(ARCHIVE_DIR.glob("WRK-*.md")):
            fm = parse_frontmatter(f)
            if fm:
                fm["_file"] = str(f.relative_to(QUEUE_ROOT))
                fm.setdefault("status", "archived")
                items.append(fm)
        # Subdirectories (archive/2026-01/, archive/2026-02/, etc.)
        for sub in sorted(ARCHIVE_DIR.iterdir()):
            if sub.is_dir():
                for f in sorted(sub.glob("WRK-*.md")):
                    fm = parse_frontmatter(f)
                    if fm:
                        fm["_file"] = str(f.relative_to(QUEUE_ROOT))
                        fm.setdefault("status", "archived")
                        items.append(fm)

    return items


def sort_key(item: dict) -> int:
    """Extract numeric ID for sorting."""
    id_str = item.get("id", "WRK-999")
    match = re.search(r"(\d+)", str(id_str))
    return int(match.group(1)) if match else 999


def normalize(item: dict) -> dict:
    """Ensure consistent field types."""
    item.setdefault("title", "Untitled")
    item.setdefault("priority", "medium")
    item.setdefault("complexity", "medium")
    item.setdefault("target_repos", [])
    item.setdefault("blocked_by", [])
    item.setdefault("related", [])
    item.setdefault("children", [])
    item.setdefault("parent", None)
    item.setdefault("compound", False)
    item.setdefault("route", "")

    # Plan tracking fields
    item.setdefault("plan_reviewed", False)
    item.setdefault("plan_approved", False)
    item.setdefault("percent_complete", 0)
    item.setdefault("brochure_status", "")

    # Ensure lists are lists
    for field in ("target_repos", "blocked_by", "related", "children"):
        val = item[field]
        if val is None:
            item[field] = []
        elif isinstance(val, str):
            item[field] = [v.strip() for v in val.split(",") if v.strip()]

    # Normalize status
    status = str(item.get("status", "pending")).lower()
    if status == "archived":
        pass  # keep as-is from discovery
    elif "archive" in item.get("_file", ""):
        item["status"] = "archived"
    else:
        item["status"] = status

    # Normalize percent_complete to int
    try:
        item["percent_complete"] = int(item["percent_complete"])
    except (ValueError, TypeError):
        item["percent_complete"] = 0

    # Normalize booleans
    for field in ("plan_reviewed", "plan_approved"):
        val = item[field]
        if isinstance(val, str):
            item[field] = val.lower() in ("true", "yes", "1")
        elif not isinstance(val, bool):
            item[field] = bool(val)

    # Determine effective plan status (auto-detect or explicit)
    if not item.get("_plan_exists"):
        item["_plan_exists"] = bool(item.get("spec_ref"))

    # Archived items are 100% complete
    if item["status"] == "archived" and item["percent_complete"] == 0:
        item["percent_complete"] = 100

    return item


def repos_str(repos: list) -> str:
    return ", ".join(str(r) for r in repos) if repos else "-"


def list_str(items: list) -> str:
    return ", ".join(str(i) for i in items) if items else "-"


def bool_icon(val: bool) -> str:
    """Render boolean as check/cross icon."""
    return "\u2705" if val else "\u274c"


def pct_str(val: int) -> str:
    """Render percent complete as bar + number."""
    if val >= 100:
        return "\u2588\u2588\u2588 100%"
    if val >= 75:
        return "\u2588\u2588\u2591 %d%%" % val
    if val >= 50:
        return "\u2588\u2591\u2591 %d%%" % val
    if val >= 25:
        return "\u2591\u2591\u2591 %d%%" % val
    return "- %d%%" % val if val > 0 else "-"


def brochure_str(val: str) -> str:
    """Render brochure status."""
    if not val:
        return "-"
    status_map = {
        "pending": "\u23f3 pending",
        "updated": "\u2705 updated",
        "synced": "\u2705 synced",
        "n/a": "n/a",
    }
    return status_map.get(str(val).lower(), str(val))


def generate_index(items: list[dict]) -> str:
    """Build the full INDEX.md content."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    items = [normalize(i) for i in items]
    items.sort(key=sort_key)

    lines: list[str] = []
    w = lines.append

    w("<!-- AUTO-GENERATED — do not edit by hand -->")
    w(f"<!-- Generated: {now} by generate-index.py -->")
    w("")
    w("# Work Queue Index")
    w("")
    w(f"> Auto-generated on {now}. Do not edit manually — run "
      "`python .claude/work-queue/scripts/generate-index.py` to regenerate.")
    w("")

    # ── Summary ──────────────────────────────────────────────
    w("## Summary")
    w("")
    w(f"**Total items:** {len(items)}")
    w("")

    # By status
    status_counts: dict[str, int] = {}
    for it in items:
        s = it["status"]
        status_counts[s] = status_counts.get(s, 0) + 1

    w("### By Status")
    w("")
    w("| Status | Count |")
    w("|--------|-------|")
    for s in ("pending", "working", "blocked", "done", "archived", "failed"):
        c = status_counts.get(s, 0)
        if c > 0:
            w(f"| {s} | {c} |")
    w("")

    # By priority
    prio_counts: dict[str, int] = {}
    for it in items:
        p = it["priority"]
        prio_counts[p] = prio_counts.get(p, 0) + 1

    w("### By Priority")
    w("")
    w("| Priority | Count |")
    w("|----------|-------|")
    for p in ("high", "medium", "low"):
        c = prio_counts.get(p, 0)
        if c > 0:
            w(f"| {p} | {c} |")
    w("")

    # By complexity
    comp_counts: dict[str, int] = {}
    for it in items:
        cx = it["complexity"]
        comp_counts[cx] = comp_counts.get(cx, 0) + 1

    w("### By Complexity")
    w("")
    w("| Complexity | Count |")
    w("|------------|-------|")
    for cx in ("simple", "medium", "complex"):
        c = comp_counts.get(cx, 0)
        if c > 0:
            w(f"| {cx} | {c} |")
    w("")

    # By repo
    repo_counts: dict[str, int] = {}
    for it in items:
        for r in it["target_repos"]:
            repo_counts[r] = repo_counts.get(r, 0) + 1

    w("### By Repository")
    w("")
    w("| Repository | Count |")
    w("|------------|-------|")
    for r in sorted(repo_counts.keys()):
        w(f"| {r} | {repo_counts[r]} |")
    w("")

    # ── Plan & Brochure Summary ─────────────────────────────
    plan_count = sum(1 for it in items if it["_plan_exists"])
    reviewed_count = sum(1 for it in items if it["plan_reviewed"])
    approved_count = sum(1 for it in items if it["plan_approved"])
    brochure_pending = sum(1 for it in items
                          if str(it.get("brochure_status", "")).lower() == "pending")
    brochure_updated = sum(1 for it in items
                          if str(it.get("brochure_status", "")).lower()
                          in ("updated", "synced"))

    w("### Plan Tracking")
    w("")
    w(f"| Metric | Count |")
    w(f"|--------|-------|")
    w(f"| Plans exist | {plan_count} / {len(items)} |")
    w(f"| Plans cross-reviewed | {reviewed_count} |")
    w(f"| Plans approved | {approved_count} |")
    w(f"| Brochure pending | {brochure_pending} |")
    w(f"| Brochure updated/synced | {brochure_updated} |")
    w("")

    # ── Master Table ─────────────────────────────────────────
    w("## Master Table")
    w("")
    w("| ID | Title | Status | Priority | Complexity | Repos | "
      "Plan? | Reviewed? | Approved? | % Done | Brochure | Blocked By |")
    w("|-----|-------|--------|----------|------------|-------|"
      "-------|-----------|-----------|--------|----------|------------|")
    for it in items:
        bid = it.get("id", "?")
        title = it["title"]
        status = it["status"]
        prio = it["priority"]
        comp = it["complexity"]
        repos = repos_str(it["target_repos"])
        plan = bool_icon(it["_plan_exists"])
        reviewed = bool_icon(it["plan_reviewed"])
        approved = bool_icon(it["plan_approved"])
        pct = pct_str(it["percent_complete"])
        brochure = brochure_str(it.get("brochure_status", ""))
        blocked = list_str(it["blocked_by"])
        w(f"| {bid} | {title} | {status} | {prio} | {comp} | {repos} | "
          f"{plan} | {reviewed} | {approved} | {pct} | {brochure} | {blocked} |")
    w("")

    # ── By Status ────────────────────────────────────────────
    w("## By Status")
    w("")

    status_order = [
        ("done", "Done (unarchived)"),
        ("pending", "Pending"),
        ("working", "Working"),
        ("blocked", "Blocked"),
        ("failed", "Failed"),
        ("archived", "Archived"),
    ]

    for status_key, heading in status_order:
        group = [it for it in items if it["status"] == status_key]
        if not group:
            continue
        w(f"### {heading}")
        w("")
        w("| ID | Title | Priority | Complexity | Repos |")
        w("|-----|-------|----------|------------|-------|")
        for it in group:
            w(f"| {it.get('id', '?')} | {it['title']} | {it['priority']} "
              f"| {it['complexity']} | {repos_str(it['target_repos'])} |")
        w("")

    # ── By Repository ────────────────────────────────────────
    w("## By Repository")
    w("")

    repo_items: dict[str, list[dict]] = {}
    for it in items:
        for r in it["target_repos"]:
            repo_items.setdefault(r, []).append(it)

    for repo in sorted(repo_items.keys()):
        group = repo_items[repo]
        w(f"### {repo}")
        w("")
        w("| ID | Title | Status | Priority | Complexity |")
        w("|-----|-------|--------|----------|------------|")
        for it in group:
            w(f"| {it.get('id', '?')} | {it['title']} | {it['status']} "
              f"| {it['priority']} | {it['complexity']} |")
        w("")

    # ── By Priority ──────────────────────────────────────────
    w("## By Priority")
    w("")

    for prio in ("high", "medium", "low"):
        group = [it for it in items if it["priority"] == prio]
        if not group:
            continue
        w(f"### {prio.capitalize()}")
        w("")
        w("| ID | Title | Status | Complexity | Repos |")
        w("|-----|-------|--------|------------|-------|")
        for it in group:
            w(f"| {it.get('id', '?')} | {it['title']} | {it['status']} "
              f"| {it['complexity']} | {repos_str(it['target_repos'])} |")
        w("")

    # ── By Complexity ────────────────────────────────────────
    w("## By Complexity")
    w("")

    for comp in ("simple", "medium", "complex"):
        group = [it for it in items if it["complexity"] == comp]
        if not group:
            continue
        w(f"### {comp.capitalize()}")
        w("")
        w("| ID | Title | Status | Priority | Repos |")
        w("|-----|-------|--------|----------|-------|")
        for it in group:
            w(f"| {it.get('id', '?')} | {it['title']} | {it['status']} "
              f"| {it['priority']} | {repos_str(it['target_repos'])} |")
        w("")

    # ── Dependencies ─────────────────────────────────────────
    w("## Dependencies")
    w("")

    dep_items = [
        it for it in items
        if it["blocked_by"] or it["children"] or it.get("parent")
    ]

    if dep_items:
        w("| ID | Title | Blocked By | Children | Parent |")
        w("|-----|-------|------------|----------|--------|")
        for it in dep_items:
            blocked = list_str(it["blocked_by"])
            children = list_str(it["children"])
            parent = it.get("parent") or "-"
            w(f"| {it.get('id', '?')} | {it['title']} "
              f"| {blocked} | {children} | {parent} |")
        w("")
    else:
        w("No items with dependencies found.")
        w("")

    return "\n".join(lines) + "\n"


def main() -> None:
    items = discover_items()
    if not items:
        print("No WRK-*.md items found.", file=sys.stderr)
        sys.exit(1)

    content = generate_index(items)
    INDEX_PATH.write_text(content, encoding="utf-8")
    print(f"Generated {INDEX_PATH} with {len(items)} items.")


if __name__ == "__main__":
    main()
