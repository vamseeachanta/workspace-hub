#!/usr/bin/env python3
"""Automated download-and-catalog pipeline for online resources.

Reads data/document-index/online-resource-registry.yaml, filters entries
that need downloading, executes or plans downloads, and updates the registry.

Supports:
  --dry-run     Show what would be downloaded without doing it
  --domain NAME Filter by domain
  --limit N     Cap downloads per run

GH issue: #1578
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
WORKSPACE = Path(__file__).resolve().parents[3]  # workspace-hub root
REGISTRY_PATH = WORKSPACE / "data/document-index/online-resource-registry.yaml"
REPORT_DIR = WORKSPACE / "docs/reports"
ACE_ROOT = "/mnt/ace"

# Types eligible for automatic download
DOWNLOADABLE_TYPES = {"github_repo", "paper", "standard_portal"}


# ===========================================================================
# Registry loading
# ===========================================================================

def load_registry(path: str) -> dict:
    """Load the online-resource-registry YAML."""
    with open(path) as f:
        data = yaml.safe_load(f) or {}
    return data


def save_registry(path: str, data: dict) -> None:
    """Write updated registry back to YAML."""
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, width=120, sort_keys=False)


# ===========================================================================
# Filtering
# ===========================================================================

def filter_downloadable(
    entries: list[dict],
    domain: str | None = None,
    limit: int | None = None,
) -> list[dict]:
    """Filter registry entries to those eligible for download.

    Criteria:
      - download_status == "not_started"
      - type in DOWNLOADABLE_TYPES
      - Optionally filtered by domain
      - Optionally capped by limit
    """
    results = []
    for e in entries:
        if e.get("download_status") != "not_started":
            continue
        if e.get("type") not in DOWNLOADABLE_TYPES:
            continue
        if domain and e.get("domain") != domain:
            continue
        results.append(e)

    # Sort by relevance_score descending for priority
    results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

    if limit is not None:
        results = results[:limit]
    return results


# ===========================================================================
# Target path determination
# ===========================================================================

def determine_target_path(entry: dict, ace_root: str = ACE_ROOT) -> str:
    """Determine the local target path for a download.

    Pattern: /mnt/ace/downloads/<type_bucket>/<domain>/<repo_or_filename>
    """
    etype = entry.get("type", "unknown")
    domain = entry.get("domain", "general")
    url = entry.get("url", "")

    if etype == "github_repo":
        # Extract repo name from URL
        parsed = urlparse(url)
        repo_name = parsed.path.rstrip("/").split("/")[-1]
        return f"{ace_root}/downloads/github_repos/{domain}/{repo_name}"

    elif etype == "paper":
        return f"{ace_root}/downloads/papers/{domain}"

    elif etype == "standard_portal":
        return f"{ace_root}/downloads/standards/{domain}"

    else:
        return f"{ace_root}/downloads/other/{domain}"


# ===========================================================================
# Download planning and execution
# ===========================================================================

def plan_downloads(
    entries: list[dict],
    ace_root: str = ACE_ROOT,
    dry_run: bool = False,
) -> list[dict]:
    """Plan (and optionally execute) downloads for filtered entries.

    Returns list of action dicts describing what was done or would be done.
    """
    actions = []

    for entry in entries:
        etype = entry.get("type", "unknown")
        url = entry.get("url", "")
        target = determine_target_path(entry, ace_root)
        entry_id = entry.get("id", "unknown")

        if etype == "github_repo":
            action = _handle_github_repo(entry, target, dry_run)
        elif etype == "paper":
            action = _handle_paper(entry, target, dry_run)
        elif etype == "standard_portal":
            action = {
                "id": entry_id,
                "action": "manual_download_required",
                "target": target,
                "url": url,
                "dry_run": dry_run,
                "message": f"Standard portal requires manual access: {url}",
            }
        else:
            action = {
                "id": entry_id,
                "action": "skipped",
                "target": "",
                "url": url,
                "dry_run": dry_run,
                "message": f"Unsupported type: {etype}",
            }

        actions.append(action)

    return actions


def _handle_github_repo(entry: dict, target: str, dry_run: bool) -> dict:
    """Handle a GitHub repo download (clone or pull)."""
    url = entry.get("url", "")
    entry_id = entry.get("id", "unknown")

    if dry_run:
        if Path(target).exists():
            return {
                "id": entry_id,
                "action": "would_pull",
                "target": target,
                "url": url,
                "dry_run": True,
                "message": f"Would git pull in {target}",
            }
        return {
            "id": entry_id,
            "action": "would_clone",
            "target": target,
            "url": url,
            "dry_run": True,
            "message": f"Would git clone --depth 1 {url} -> {target}",
        }

    # Actual execution
    target_path = Path(target)
    if target_path.exists() and (target_path / ".git").exists():
        # git pull
        try:
            result = subprocess.run(
                ["git", "-C", target, "pull"],
                capture_output=True, text=True, timeout=120,
            )
            return {
                "id": entry_id,
                "action": "git_pull",
                "target": target,
                "url": url,
                "dry_run": False,
                "success": result.returncode == 0,
                "message": result.stdout.strip() or result.stderr.strip(),
            }
        except subprocess.TimeoutExpired:
            return {
                "id": entry_id,
                "action": "git_pull",
                "target": target,
                "url": url,
                "dry_run": False,
                "success": False,
                "message": "Timeout during git pull",
            }
    else:
        # git clone --depth 1
        target_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            result = subprocess.run(
                ["git", "clone", "--depth", "1", url, target],
                capture_output=True, text=True, timeout=300,
            )
            return {
                "id": entry_id,
                "action": "git_clone",
                "target": target,
                "url": url,
                "dry_run": False,
                "success": result.returncode == 0,
                "message": result.stdout.strip() or result.stderr.strip(),
            }
        except subprocess.TimeoutExpired:
            return {
                "id": entry_id,
                "action": "git_clone",
                "target": target,
                "url": url,
                "dry_run": False,
                "success": False,
                "message": "Timeout during git clone",
            }


def _handle_paper(entry: dict, target: str, dry_run: bool) -> dict:
    """Handle a paper/PDF download using wget."""
    url = entry.get("url", "")
    entry_id = entry.get("id", "unknown")
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path) or f"{entry_id}.pdf"
    dest = f"{target}/{filename}"

    if dry_run:
        return {
            "id": entry_id,
            "action": "would_download",
            "target": target,
            "url": url,
            "dry_run": True,
            "message": f"Would wget {url} -> {dest}",
        }

    # Actual download
    target_path = Path(target)
    target_path.mkdir(parents=True, exist_ok=True)

    if Path(dest).exists():
        return {
            "id": entry_id,
            "action": "skip_exists",
            "target": dest,
            "url": url,
            "dry_run": False,
            "success": True,
            "message": f"Already exists: {dest}",
        }

    try:
        result = subprocess.run(
            ["wget", "-q", "--timeout=60", "--tries=3", "-O", dest, url],
            capture_output=True, text=True, timeout=120,
        )
        return {
            "id": entry_id,
            "action": "wget_download",
            "target": dest,
            "url": url,
            "dry_run": False,
            "success": result.returncode == 0,
            "message": "Downloaded" if result.returncode == 0 else result.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        return {
            "id": entry_id,
            "action": "wget_download",
            "target": dest,
            "url": url,
            "dry_run": False,
            "success": False,
            "message": "Timeout during wget",
        }


# ===========================================================================
# Status update
# ===========================================================================

def update_entry_status(
    entry: dict,
    new_status: str,
    local_path: str,
) -> dict:
    """Update a registry entry's download status."""
    entry = entry.copy()
    entry["download_status"] = new_status
    entry["local_backup_path"] = local_path
    entry["last_checked"] = datetime.now().strftime("%Y-%m-%d")
    return entry


def apply_actions_to_registry(
    registry: dict,
    actions: list[dict],
) -> dict:
    """Apply download action results back to the registry."""
    entries_by_id = {e["id"]: e for e in registry.get("entries", [])}

    for action in actions:
        entry_id = action.get("id")
        if entry_id not in entries_by_id:
            continue

        entry = entries_by_id[entry_id]
        act = action.get("action", "")

        if action.get("dry_run"):
            continue  # Don't update in dry-run

        if act == "manual_download_required":
            entries_by_id[entry_id] = update_entry_status(
                entry, "manual_download_required", "",
            )
        elif action.get("success"):
            entries_by_id[entry_id] = update_entry_status(
                entry, "downloaded", action.get("target", ""),
            )
        elif not action.get("success") and act not in ("skipped",):
            entries_by_id[entry_id] = update_entry_status(
                entry, "failed", "",
            )

    registry = registry.copy()
    registry["entries"] = list(entries_by_id.values())
    return registry


# ===========================================================================
# Report generation
# ===========================================================================

def generate_download_report(
    actions: list[dict],
    dry_run: bool = False,
) -> str:
    """Generate a markdown download report."""
    today = datetime.now().strftime("%Y-%m-%d")
    lines: list[str] = []

    mode = "DRY RUN" if dry_run else "LIVE"
    lines.append(f"# Download & Catalog Report — {today}")
    lines.append(f"\nMode: **{mode}**")
    lines.append(f"Actions: {len(actions)}")
    lines.append("")

    if not actions:
        lines.append("No actions to report.")
        return "\n".join(lines)

    # Summary counts
    action_types: dict[str, int] = {}
    for a in actions:
        act = a.get("action", "unknown")
        action_types[act] = action_types.get(act, 0) + 1

    lines.append("## Summary")
    lines.append("")
    lines.append("| Action | Count |")
    lines.append("|---|---|")
    for act, count in sorted(action_types.items()):
        lines.append(f"| {act} | {count} |")
    lines.append("")

    # Detail table
    lines.append("## Actions Detail")
    lines.append("")
    lines.append("| ID | Action | URL | Target | Message |")
    lines.append("|---|---|---|---|---|")
    for a in actions:
        aid = a.get("id", "—")
        act = a.get("action", "—")
        url = a.get("url", "—")
        # Truncate long URLs
        if len(url) > 50:
            url = url[:47] + "..."
        target = a.get("target", "—")
        if len(target) > 50:
            target = target[:47] + "..."
        msg = a.get("message", "—")
        if len(msg) > 60:
            msg = msg[:57] + "..."
        lines.append(f"| {aid} | {act} | {url} | {target} | {msg} |")
    lines.append("")

    return "\n".join(lines)


# ===========================================================================
# Main CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Download and catalog online resources from registry",
    )
    parser.add_argument(
        "--registry",
        default=str(REGISTRY_PATH),
        help="Path to online-resource-registry.yaml",
    )
    parser.add_argument(
        "--ace-root",
        default=ACE_ROOT,
        help="Root of /mnt/ace mount for downloads",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be downloaded without doing it",
    )
    parser.add_argument(
        "--domain",
        type=str,
        default=None,
        help="Filter by domain name",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Cap number of downloads per run",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output report path (default: docs/reports/download-report-YYYY-MM-DD.md)",
    )
    args = parser.parse_args()

    # Load registry
    print(f"Loading registry: {args.registry}")
    registry = load_registry(args.registry)
    entries = registry.get("entries", [])
    print(f"Total entries: {len(entries)}")

    # Filter
    filtered = filter_downloadable(
        entries,
        domain=args.domain,
        limit=args.limit,
    )
    print(f"Downloadable entries: {len(filtered)}")

    if not filtered:
        print("Nothing to download.")
        return

    # Plan/execute
    mode = "DRY RUN" if args.dry_run else "LIVE"
    print(f"\nMode: {mode}")
    print("=" * 60)

    actions = plan_downloads(
        filtered,
        ace_root=args.ace_root,
        dry_run=args.dry_run,
    )

    # Print actions
    for a in actions:
        status = "[DRY]" if a.get("dry_run") else "[LIVE]"
        print(f"  {status} {a['action']:25s} {a.get('id', '?'):30s} -> {a.get('target', '?')}")

    # Update registry (only in live mode)
    if not args.dry_run:
        registry = apply_actions_to_registry(registry, actions)
        save_registry(args.registry, registry)
        print(f"\nRegistry updated: {args.registry}")

    # Generate report
    report = generate_download_report(actions, dry_run=args.dry_run)
    today = datetime.now().strftime("%Y-%m-%d")
    report_path = args.output or str(REPORT_DIR / f"download-report-{today}.md")
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    Path(report_path).write_text(report)
    print(f"Report: {report_path}")

    # Summary
    print(f"\n{'=' * 60}")
    by_action: dict[str, int] = {}
    for a in actions:
        act = a.get("action", "unknown")
        by_action[act] = by_action.get(act, 0) + 1
    for act, count in sorted(by_action.items()):
        print(f"  {act}: {count}")


if __name__ == "__main__":
    main()
