#!/usr/bin/env python3
"""staleness-scanner.py — Documentation freshness scanner.

Walks all .md files under docs/, gets last git commit date for each,
classifies into FRESH (<30 days), MODERATE (30-90 days), STALE (>90 days).
Also checks for inline date stamps (e.g., "Updated: YYYY-MM-DD").

Outputs:
  - YAML report to stdout
  - Markdown dashboard to docs/dashboards/doc-freshness-dashboard.md

Usage:
    uv run --no-project python scripts/docs/staleness-scanner.py

Ref: GH #1568
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Optional: yaml for report output
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FRESH_THRESHOLD_DAYS = 30
MODERATE_THRESHOLD_DAYS = 90

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_ROOT / "docs"
DASHBOARD_PATH = REPO_ROOT / "docs" / "dashboards" / "doc-freshness-dashboard.md"

# Regex for inline date stamps in content
DATE_STAMP_PATTERNS = [
    re.compile(r"(?:Updated|Last [Uu]pdated|Date|Modified|Refreshed)\s*[:=]\s*(\d{4}-\d{2}-\d{2})"),
    re.compile(r"\*\*(?:Last Updated|Date|Updated)\*\*\s*[:=]\s*(\d{4}-\d{2}-\d{2})"),
    re.compile(r"(?:Assessment Date|Refreshed)\s*[:=]\s*(\d{4}-\d{2}-\d{2})"),
]


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def get_git_last_modified(filepath: str, repo_root: str | None = None) -> str | None:
    """Get the last git commit date for a file as ISO 8601 string.

    Returns None if the file is untracked or git is unavailable.
    """
    cwd = repo_root or str(Path(filepath).parent)
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", filepath],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10,
        )
        date_str = result.stdout.strip()
        return date_str if date_str else None
    except (subprocess.SubprocessError, FileNotFoundError):
        return None


def extract_content_date(filepath: str) -> str | None:
    """Extract a date stamp from the file content.

    Looks for patterns like:
      - Updated: 2026-03-15
      - **Last Updated**: 2026-03-15
      - Date: 2026-03-15
    """
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            # Read first 2000 chars — dates are usually near the top
            text = f.read(2000)
    except OSError:
        return None

    for pattern in DATE_STAMP_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1) + "T00:00:00+00:00"

    return None


def classify_staleness(modified_date: datetime, now: datetime | None = None) -> str:
    """Classify a file's staleness based on age.

    Returns:
        FRESH:    <30 days old
        MODERATE: 30-89 days old (inclusive of 30)
        STALE:    >=90 days old
    """
    if now is None:
        now = datetime.now(timezone.utc)

    # Ensure timezone-aware
    if modified_date.tzinfo is None:
        modified_date = modified_date.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    age_days = (now - modified_date).days

    if age_days >= MODERATE_THRESHOLD_DAYS:
        return "STALE"
    elif age_days >= FRESH_THRESHOLD_DAYS:
        return "MODERATE"
    else:
        return "FRESH"


def classify_file(filepath: str, now: datetime | None = None) -> dict | None:
    """Analyze a single .md file and return its classification dict.

    Returns None if the file does not exist.
    """
    if now is None:
        now = datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    path = Path(filepath)
    if not path.exists():
        return None

    # Try git date first
    date_source = "git"
    git_date_str = get_git_last_modified(filepath, repo_root=str(REPO_ROOT))

    if git_date_str:
        try:
            modified = datetime.fromisoformat(git_date_str)
            if modified.tzinfo is None:
                modified = modified.replace(tzinfo=timezone.utc)
        except ValueError:
            git_date_str = None

    # Fall back to content date stamp
    if not git_date_str:
        content_date_str = extract_content_date(filepath)
        if content_date_str:
            date_source = "content"
            try:
                modified = datetime.fromisoformat(content_date_str)
                if modified.tzinfo is None:
                    modified = modified.replace(tzinfo=timezone.utc)
            except ValueError:
                content_date_str = None

    # Fall back to filesystem mtime
    if not git_date_str and not (locals().get("content_date_str")):
        date_source = "filesystem"
        mtime = path.stat().st_mtime
        modified = datetime.fromtimestamp(mtime, tz=timezone.utc)

    age_days = (now - modified).days
    status = classify_staleness(modified, now=now)

    # Make path relative to repo root if possible
    try:
        rel_path = str(path.relative_to(REPO_ROOT))
    except ValueError:
        rel_path = str(path)

    return {
        "file": rel_path,
        "status": status,
        "age_days": age_days,
        "last_modified": modified.isoformat(),
        "date_source": date_source,
    }


def scan_directory(directory: str) -> list[str]:
    """Recursively find all .md files in a directory.

    Returns empty list if directory doesn't exist.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return []

    return sorted(str(p) for p in dir_path.rglob("*.md"))


def build_yaml_report(entries: list[dict], now: datetime | None = None) -> dict:
    """Build the YAML report structure from classified entries.

    Returns a dict with keys: generated_at, summary, files.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    fresh_count = sum(1 for e in entries if e["status"] == "FRESH")
    moderate_count = sum(1 for e in entries if e["status"] == "MODERATE")
    stale_count = sum(1 for e in entries if e["status"] == "STALE")

    return {
        "generated_at": now.isoformat(),
        "summary": {
            "total": len(entries),
            "FRESH": fresh_count,
            "MODERATE": moderate_count,
            "STALE": stale_count,
        },
        "files": sorted(entries, key=lambda e: e["age_days"], reverse=True),
    }


def format_summary_line(summary: dict) -> str:
    """Format a one-line summary: 'N FRESH, M MODERATE, P STALE'."""
    return (
        f"{summary['FRESH']} FRESH, "
        f"{summary['MODERATE']} MODERATE, "
        f"{summary['STALE']} STALE"
    )


def generate_markdown_dashboard(report: dict) -> str:
    """Generate a Markdown dashboard from the report."""
    summary = report["summary"]
    summary_line = format_summary_line(summary)

    lines = [
        "# Doc Freshness Dashboard",
        "",
        f"> **Generated:** {report['generated_at'][:10]}",
        f"> **Total docs scanned:** {summary['total']}",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"**{summary_line}**",
        "",
        "| Status | Count | Threshold |",
        "|--------|------:|-----------|",
        f"| FRESH | {summary['FRESH']} | < 30 days |",
        f"| MODERATE | {summary['MODERATE']} | 30-89 days |",
        f"| STALE | {summary['STALE']} | >= 90 days |",
        "",
        "---",
        "",
        "## STALE Documents (>= 90 days)",
        "",
    ]

    stale = [f for f in report["files"] if f["status"] == "STALE"]
    if stale:
        lines.append("| File | Age (days) | Last Modified | Source |")
        lines.append("|------|----------:|--------------|--------|")
        for f in stale:
            lines.append(
                f"| `{f['file']}` | {f['age_days']} | {f['last_modified'][:10]} | {f['date_source']} |"
            )
    else:
        lines.append("_No stale documents found._")

    lines.extend([
        "",
        "---",
        "",
        "## MODERATE Documents (30-89 days)",
        "",
    ])

    moderate = [f for f in report["files"] if f["status"] == "MODERATE"]
    if moderate:
        lines.append("| File | Age (days) | Last Modified | Source |")
        lines.append("|------|----------:|--------------|--------|")
        for f in moderate:
            lines.append(
                f"| `{f['file']}` | {f['age_days']} | {f['last_modified'][:10]} | {f['date_source']} |"
            )
    else:
        lines.append("_No moderate-age documents found._")

    lines.extend([
        "",
        "---",
        "",
        "## FRESH Documents (< 30 days)",
        "",
    ])

    fresh = [f for f in report["files"] if f["status"] == "FRESH"]
    if fresh:
        lines.append("| File | Age (days) | Last Modified | Source |")
        lines.append("|------|----------:|--------------|--------|")
        for f in fresh:
            lines.append(
                f"| `{f['file']}` | {f['age_days']} | {f['last_modified'][:10]} | {f['date_source']} |"
            )
    else:
        lines.append("_No fresh documents found._")

    lines.extend([
        "",
        "---",
        "",
        f"*Scanner: `scripts/docs/staleness-scanner.py` | Thresholds: FRESH < 30d, MODERATE 30-89d, STALE >= 90d*",
        "",
    ])

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    """Run the doc staleness scanner."""
    now = datetime.now(timezone.utc)

    print(f"\n  Doc Staleness Scanner")
    print(f"  {'='*40}")
    print(f"  Scanning docs/ for .md files...")

    # Find all .md files under docs/
    md_files = scan_directory(str(DOCS_DIR))
    print(f"  Found {len(md_files)} markdown files.")

    # Classify each file
    entries = []
    for filepath in md_files:
        result = classify_file(filepath, now=now)
        if result:
            entries.append(result)

    print(f"  Classified {len(entries)} files.")

    # Build report
    report = build_yaml_report(entries, now=now)
    summary_line = format_summary_line(report["summary"])
    print(f"\n  Summary: {summary_line}")

    # Output YAML report to stdout
    if HAS_YAML:
        print("\n--- YAML Report ---")
        import yaml as _yaml
        print(_yaml.dump(report, default_flow_style=False, sort_keys=False))
    else:
        # Fallback: print summary without yaml
        print(f"\n  (PyYAML not available — install with: uv pip install pyyaml)")
        print(f"  Report: {report['summary']}")

    # Generate markdown dashboard
    dashboard_md = generate_markdown_dashboard(report)

    # Write dashboard
    DASHBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_PATH.write_text(dashboard_md)
    print(f"\n  Dashboard written to: {DASHBOARD_PATH.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
