#!/usr/bin/env python3
"""doc-staleness-scanner.py — Documentation freshness scanner (#1568).

Scans docs/ and subdirectories for .md files, classifies each by age:
  - current:  <90 days old
  - stale:    90-180 days old
  - critical: >180 days old

Outputs a JSON report and an ASCII dashboard.

Usage:
    uv run --no-project python scripts/quality/doc-staleness-scanner.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCAN_DIRS = [
    "docs/",
    "docs/assessments/",
    "docs/modules/",
    "docs/research/",
    "docs/standards/",
    "docs/vision/",
]

STALE_THRESHOLD_DAYS = 90
CRITICAL_THRESHOLD_DAYS = 180

# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def extract_git_date(filepath: Path, repo_root: Path | None = None) -> datetime | None:
    """Extract last-modified date from git log for a file.

    Returns a timezone-aware datetime, or None if the file is untracked.
    """
    cwd = repo_root or filepath.parent
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", str(filepath)],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=10,
        )
        date_str = result.stdout.strip()
        if not date_str:
            return None
        return datetime.fromisoformat(date_str)
    except (subprocess.SubprocessError, ValueError):
        return None


def extract_frontmatter_date(filepath: Path) -> datetime | None:
    """Extract date from YAML frontmatter (date or version_date field).

    Looks for:
      - date: YYYY-MM-DD
      - version_date: YYYY-MM-DD
      - last_updated: YYYY-MM-DD
    """
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    # Check for YAML frontmatter delimited by ---
    fm_match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not fm_match:
        return None

    frontmatter = fm_match.group(1)

    # Look for date fields
    for field in ("date", "version_date", "last_updated"):
        pattern = rf"^{field}:\s*['\"]?(\d{{4}}-\d{{2}}-\d{{2}})['\"]?"
        m = re.search(pattern, frontmatter, re.MULTILINE)
        if m:
            try:
                dt = datetime.strptime(m.group(1), "%Y-%m-%d")
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue

    return None


def classify_staleness(modified_date: datetime, now: datetime | None = None) -> str:
    """Classify a file as current, stale, or critical based on age.

    - current:  <90 days old
    - stale:    90-180 days old (inclusive of 90)
    - critical: >=180 days old
    """
    if now is None:
        now = datetime.now(timezone.utc)

    # Ensure both are timezone-aware for comparison
    if modified_date.tzinfo is None:
        modified_date = modified_date.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    age = (now - modified_date).days

    if age >= CRITICAL_THRESHOLD_DAYS:
        return "critical"
    elif age >= STALE_THRESHOLD_DAYS:
        return "stale"
    else:
        return "current"


def find_md_files(directories: list[Path]) -> list[Path]:
    """Find all .md files in the given directories (recursive)."""
    seen: set[Path] = set()
    result: list[Path] = []

    for d in directories:
        if not d.exists():
            continue
        for md in sorted(d.rglob("*.md")):
            resolved = md.resolve()
            if resolved not in seen:
                seen.add(resolved)
                result.append(md)

    return result


def analyze_file(filepath: Path, repo_root: Path, now: datetime) -> dict:
    """Analyze a single .md file and return its entry dict."""
    # Primary: git date
    git_date = extract_git_date(filepath, repo_root=repo_root)
    # Secondary: frontmatter
    fm_date = extract_frontmatter_date(filepath)

    if git_date is not None:
        last_modified = git_date
        source = "git"
    elif fm_date is not None:
        last_modified = fm_date
        source = "frontmatter"
    else:
        # Fall back to file mtime
        mtime = filepath.stat().st_mtime
        last_modified = datetime.fromtimestamp(mtime, tz=timezone.utc)
        source = "filesystem"

    # Ensure timezone-aware
    if last_modified.tzinfo is None:
        last_modified = last_modified.replace(tzinfo=timezone.utc)

    age_days = (now - last_modified).days
    classification = classify_staleness(last_modified, now)

    # Make path relative to repo root
    try:
        rel_path = str(filepath.relative_to(repo_root))
    except ValueError:
        rel_path = str(filepath)

    return {
        "path": rel_path,
        "last_modified": last_modified.isoformat(),
        "classification": classification,
        "age_days": age_days,
        "source": source,
    }


def build_report(entries: list[dict], now: datetime) -> dict:
    """Build the full JSON report structure."""
    summary = {
        "total": len(entries),
        "current": sum(1 for e in entries if e["classification"] == "current"),
        "stale": sum(1 for e in entries if e["classification"] == "stale"),
        "critical": sum(1 for e in entries if e["classification"] == "critical"),
    }

    return {
        "generated_at": now.isoformat(),
        "summary": summary,
        "files": sorted(entries, key=lambda e: e["age_days"], reverse=True),
    }


def format_dashboard(entries: list[dict]) -> str:
    """Format an ASCII table dashboard sorted by staleness (most stale first)."""
    # Sort by age descending
    sorted_entries = sorted(entries, key=lambda e: e["age_days"], reverse=True)

    # Column widths
    path_w = max((len(e["path"]) for e in sorted_entries), default=10)
    path_w = max(path_w, 4)  # minimum "Path"
    path_w = min(path_w, 70)  # cap

    lines = []
    header = f"{'Path':<{path_w}}  {'Age':>6}  {'Status':<10}  {'Source':<12}  {'Last Modified':<25}"
    sep = "-" * len(header)

    lines.append("")
    lines.append("  DOC STALENESS DASHBOARD")
    lines.append(f"  Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("")
    lines.append(header)
    lines.append(sep)

    status_icons = {
        "current": "  CURRENT",
        "stale": "  STALE",
        "critical": "  CRITICAL",
    }

    for e in sorted_entries:
        path_display = e["path"]
        if len(path_display) > path_w:
            path_display = "..." + path_display[-(path_w - 3):]
        status = status_icons.get(e["classification"], e["classification"])
        lines.append(
            f"{path_display:<{path_w}}  {e['age_days']:>4}d  {status:<10}  {e['source']:<12}  {e['last_modified'][:25]}"
        )

    lines.append(sep)
    lines.append("")

    return "\n".join(lines)


def format_summary(report: dict) -> str:
    """Format a summary stats line."""
    s = report["summary"]
    return (
        f"\n  SUMMARY: {s['total']} docs total — "
        f"{s['current']} current, {s['stale']} stale, {s['critical']} critical\n"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    """Run the doc staleness scanner."""
    repo_root = Path(__file__).resolve().parents[2]
    now = datetime.now(timezone.utc)

    # Resolve scan directories
    scan_dirs = [repo_root / d for d in SCAN_DIRS]

    print(f"\n  Scanning for .md files in {len(SCAN_DIRS)} directories...")

    # Find all .md files
    md_files = find_md_files(scan_dirs)
    print(f"  Found {len(md_files)} markdown files.")

    # Analyze each file
    entries = []
    for f in md_files:
        entry = analyze_file(f, repo_root, now)
        entries.append(entry)

    # Build report
    report = build_report(entries, now)

    # Write JSON report
    state_dir = repo_root / ".claude" / "state" / "doc-staleness"
    state_dir.mkdir(parents=True, exist_ok=True)
    date_str = now.strftime("%Y-%m-%d")
    json_path = state_dir / f"{date_str}.json"
    json_path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"  JSON report written to: {json_path.relative_to(repo_root)}")

    # Print dashboard
    dashboard = format_dashboard(entries)
    print(dashboard)

    # Print summary
    summary = format_summary(report)
    print(summary)

    return 0


if __name__ == "__main__":
    sys.exit(main())
