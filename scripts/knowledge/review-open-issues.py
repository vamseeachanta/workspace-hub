#!/usr/bin/env python3
"""review-open-issues.py — Fetch open GitHub Issues, group and display.

Usage:
    review-open-issues.py [--format table|yaml|json]
                          [--group-by label|category|priority]
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone


def fetch_issues(repo="vamseeachanta/workspace-hub", limit=500):
    """Fetch open issues via gh CLI, return list of dicts."""
    try:
        r = subprocess.run(
            ["gh", "issue", "list", "--repo", repo, "--state", "open",
             "--limit", str(limit),
             "--json", "number,title,labels"],
            capture_output=True, text=True, timeout=30)
    except FileNotFoundError:
        print("Error: gh CLI not found. Install: "
              "https://cli.github.com/", file=sys.stderr)
        return []
    except subprocess.TimeoutExpired:
        print("Error: gh command timed out", file=sys.stderr)
        return []
    if r.returncode != 0:
        print(f"Error fetching issues: {r.stderr}", file=sys.stderr)
        return []
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        print("Error: invalid JSON from gh", file=sys.stderr)
        return []


def _extract_label(labels, prefix):
    """Extract value from labels matching prefix (e.g. 'cat:')."""
    for lb in labels:
        name = lb.get("name", "") if isinstance(lb, dict) else str(lb)
        if name.startswith(prefix):
            return name[len(prefix):]
    return None


def group_issues(issues, group_by="category"):
    """Group issues by category (cat:*) or priority (priority:*)."""
    prefix_map = {
        "category": "cat:",
        "label": "cat:",
        "priority": "priority:",
    }
    prefix = prefix_map.get(group_by, "cat:")
    fallback = "uncategorized" if group_by != "priority" else "unset"
    groups = {}
    for issue in issues:
        labels = issue.get("labels", [])
        key = _extract_label(labels, prefix) or fallback
        if key not in groups:
            groups[key] = {"count": 0, "issues": []}
        groups[key]["count"] += 1
        label_names = [
            (lb.get("name", "") if isinstance(lb, dict) else str(lb))
            for lb in labels]
        groups[key]["issues"].append({
            "number": issue["number"],
            "title": issue.get("title", ""),
            "labels": label_names,
        })
    return groups


def format_table(groups, total=0):
    """Render groups as human-readable table."""
    lines = []
    for cat in sorted(groups.keys()):
        info = groups[cat]
        lines.append(f"Category: {cat} ({info['count']} issues)")
        for iss in info["issues"]:
            label_str = "  ".join(
                lb for lb in iss["labels"]
                if lb.startswith("priority:"))
            lines.append(
                f"  #{iss['number']:<4} {iss['title']:<55} "
                f"{label_str}")
        lines.append("")
    cat_count = len(groups)
    lines.append(
        f"Summary: {total} open issues across {cat_count} categories")
    lines.append(
        "  Action needed: review each group, decide keep/close/merge")
    return "\n".join(lines)


def format_yaml(groups, total=0):
    """Render groups as YAML string."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        f'generated_at: "{now}"',
        f"total_open: {total}",
        "groups:",
    ]
    for cat in sorted(groups.keys()):
        info = groups[cat]
        lines.append(f"  {cat}:")
        lines.append(f"    count: {info['count']}")
        lines.append("    issues:")
        for iss in info["issues"]:
            lines.append(f"      - number: {iss['number']}")
            lines.append(f'        title: "{iss["title"]}"')
            lb_str = ", ".join(iss["labels"])
            lines.append(f"        labels: [{lb_str}]")
    return "\n".join(lines)


def format_json(groups, total=0):
    """Render groups as JSON string."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data = {
        "generated_at": now,
        "total_open": total,
        "groups": groups,
    }
    return json.dumps(data, indent=2)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--format", choices=["table", "yaml", "json"],
                    default="table")
    ap.add_argument("--group-by",
                    choices=["label", "category", "priority"],
                    default="category")
    args = ap.parse_args(argv)
    issues = fetch_issues()
    groups = group_issues(issues, group_by=args.group_by)
    total = sum(g["count"] for g in groups.values())
    formatters = {
        "table": format_table,
        "yaml": format_yaml,
        "json": format_json,
    }
    print(formatters[args.format](groups, total=total))


if __name__ == "__main__":
    main()
