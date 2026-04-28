#!/usr/bin/env python3
"""review-open-issues.py — Fetch open GitHub Issues, group and display.

Usage:
    review-open-issues.py [--format table|yaml|json]
                          [--group-by label|category|priority]
"""
import argparse
import glob
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


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


def fetch_issue_snapshot(repo="vamseeachanta/workspace-hub", limit=500,
                         state="all"):
    """Fetch issue metadata needed by the hygiene audit."""
    fields = "number,title,labels,state,body,updatedAt,closedAt"
    try:
        r = subprocess.run(
            ["gh", "issue", "list", "--repo", repo, "--state", state,
             "--limit", str(limit), "--json", fields],
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


ISSUE_REF_RE = re.compile(r"#(\d+)")
PATH_RE = re.compile(r"`([^`\n]+)`")
ACTION_RE = re.compile(r"\b(close|merge|refine|refresh|verify|implement)\b",
                       re.IGNORECASE)


def _issue_state_index(issues):
    return {
        int(issue["number"]): str(issue.get("state", "OPEN")).upper()
        for issue in issues
        if "number" in issue
    }


def _issue_refs(text):
    return sorted({int(match) for match in ISSUE_REF_RE.findall(text)})


def _artifact_record(path):
    artifact_path = Path(path)
    text = artifact_path.read_text(encoding="utf-8", errors="replace")
    return {
        "path": artifact_path,
        "text": text,
        "issue_refs": _issue_refs(text),
        "actions": {m.lower() for m in ACTION_RE.findall(text)},
    }


def _snippet(text, max_len=180):
    clean = " ".join(text.split())
    if len(clean) <= max_len:
        return clean
    return clean[:max_len - 3] + "..."


def _finding(category, recommendation, issues, evidence,
             confidence="medium", artifact=None):
    return {
        "category": category,
        "recommendation": recommendation,
        "confidence": confidence,
        "issues": sorted(int(issue) for issue in issues),
        "artifact": str(artifact) if artifact is not None else None,
        "evidence": _snippet(evidence),
    }


def _line_findings_from_overlap_audit(issues, overlap_audit_text):
    state_by_issue = _issue_state_index(issues)
    findings = []
    if not overlap_audit_text:
        return findings
    for raw_line in overlap_audit_text.splitlines():
        line = raw_line.strip()
        refs = [ref for ref in _issue_refs(line) if ref in state_by_issue]
        lower = line.lower()
        if not refs:
            continue
        if (
            len(refs) >= 2
            and ("duplicate" in lower or "overlap" in lower)
            and any(state_by_issue[ref] == "OPEN" for ref in refs)
        ):
            findings.append(_finding(
                "duplicate", "merge", refs, line, confidence="medium"))
        if (
            len(refs) == 1
            and state_by_issue[refs[0]] == "OPEN"
            and ("no longer matches" in lower
                 or "stale premise" in lower
                 or "re-evaluat" in lower
                 or "reevaluat" in lower)
        ):
            findings.append(_finding(
                "stale-premise", "verify", refs, line, confidence="medium"))
    return findings


def _artifact_findings(issues, artifact_paths, repo_root):
    state_by_issue = _issue_state_index(issues)
    findings = []
    root = Path(repo_root) if repo_root else Path.cwd()
    for path in artifact_paths or []:
        record = _artifact_record(path)
        refs = [ref for ref in record["issue_refs"] if ref in state_by_issue]
        closed_refs = [ref for ref in refs if state_by_issue[ref] == "CLOSED"]
        if closed_refs and record["actions"]:
            findings.append(_finding(
                "stale-artifact", "refresh", closed_refs,
                f"Artifact action {sorted(record['actions'])} references "
                f"closed issue(s) {closed_refs}.",
                confidence="high", artifact=record["path"]))

        lower = record["text"].lower()
        if len(refs) >= 2 and closed_refs and (
            "child" in lower or "parent" in lower or "route" in lower
            or "depends" in lower or "dependency" in lower
        ):
            findings.append(_finding(
                "parent-child-drift", "verify", refs,
                "Artifact still describes parent/child routing while at "
                f"least one referenced issue is closed: {closed_refs}.",
                confidence="medium", artifact=record["path"]))

        for line in record["text"].splitlines():
            line_lower = line.lower()
            if not any(
                word in line_lower
                for word in ("missing", "exists", "present")
            ):
                continue
            for cited in PATH_RE.findall(line):
                if cited.startswith(("http://", "https://", "#")):
                    continue
                if "/" not in cited and not cited.startswith("."):
                    continue
                path_exists = (root / cited).exists()
                cited_lower = cited.lower()
                if "missing" in line_lower and path_exists:
                    findings.append(_finding(
                        "repo-reality-contradiction", "verify",
                        refs or _issue_refs(record["path"].stem),
                        "Artifact says a path is missing, but it exists: "
                        f"{cited}",
                        confidence="medium", artifact=record["path"]))
                elif (
                    ("exists" in line_lower or "present" in line_lower)
                    and not path_exists
                    and "missing" not in cited_lower
                ):
                    findings.append(_finding(
                        "repo-reality-contradiction", "verify",
                        refs or _issue_refs(record["path"].stem),
                        "Artifact says a path exists, but it is absent: "
                        f"{cited}",
                        confidence="medium", artifact=record["path"]))
    return findings


def _dedupe_findings(findings):
    seen = set()
    unique = []
    for finding in findings:
        key = (
            finding["category"],
            finding["recommendation"],
            tuple(finding["issues"]),
            finding["artifact"],
            finding["evidence"],
        )
        if key not in seen:
            seen.add(key)
            unique.append(finding)
    return sorted(
        unique,
        key=lambda f: (
            f["recommendation"], f["category"], f["issues"],
            f["artifact"] or "", f["evidence"],
        ),
    )


def audit_issue_hygiene(issues, artifact_paths=None, repo_root=None,
                        overlap_audit_text=""):
    """Return deterministic issue-hygiene findings.

    Duplicate findings intentionally require structural overlap-audit evidence;
    title similarity alone is not enough for v1.
    """
    findings = []
    findings.extend(_artifact_findings(issues, artifact_paths or [], repo_root))
    findings.extend(_line_findings_from_overlap_audit(
        issues, overlap_audit_text or ""))
    return _dedupe_findings(findings)


def _stable_finding(finding):
    item = dict(finding)
    item["issues"] = sorted(item.get("issues", []))
    return item


def format_hygiene_json(findings, generated_at=None):
    """Render hygiene findings as a stable JSON document."""
    now = generated_at or datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    stable_findings = sorted(
        (_stable_finding(f) for f in findings),
        key=lambda f: (
            f["recommendation"], f["category"], f["issues"],
            f.get("artifact") or "", f.get("evidence") or "",
        ),
    )
    data = {
        "generated_at": now,
        "schema_version": 1,
        "finding_count": len(stable_findings),
        "findings": stable_findings,
    }
    return json.dumps(data, indent=2, sort_keys=False)


def _format_issue_list(issue_numbers):
    return ", ".join(f"#{num}" for num in sorted(issue_numbers))


def format_hygiene_markdown(findings, generated_at=None):
    """Render hygiene findings as an operator report grouped by action."""
    now = generated_at or datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# Issue Hygiene Audit",
        "",
        f"Generated: {now}",
        f"Findings: {len(findings)}",
        "",
    ]
    for action in ("refresh", "merge", "close", "verify"):
        action_findings = [
            f for f in findings if f.get("recommendation") == action
        ]
        lines.append(f"## {action.title()}")
        if not action_findings:
            lines.append("- None")
        for finding in sorted(
            action_findings,
            key=lambda f: (f["category"], f["issues"], f.get("artifact") or ""),
        ):
            artifact = f" ({finding['artifact']})" if finding["artifact"] else ""
            lines.append(
                f"- {_format_issue_list(finding['issues'])}: "
                f"{finding['category']} [{finding['confidence']}]{artifact} "
                f"- {finding['evidence']}"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _read_text_file(path):
    if not path:
        return ""
    text_path = Path(path)
    if not text_path.exists():
        return ""
    return text_path.read_text(encoding="utf-8", errors="replace")


def _load_issues_file(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _artifact_paths_from_glob(pattern):
    if not pattern:
        return []
    return [Path(path) for path in sorted(glob.glob(pattern, recursive=True))]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--audit", action="store_true",
                    help="run issue hygiene audit mode")
    ap.add_argument("--repo", default="vamseeachanta/workspace-hub")
    ap.add_argument("--limit", type=int, default=500)
    ap.add_argument("--format", choices=["table", "yaml", "json"],
                    default="table")
    ap.add_argument("--audit-format", choices=["json", "markdown"],
                    default="markdown")
    ap.add_argument("--group-by",
                    choices=["label", "category", "priority"],
                    default="category")
    ap.add_argument("--issues-json",
                    help="fixture JSON issue snapshot for audit mode")
    ap.add_argument("--artifact-glob",
                    default="docs/plans/**/results/*.md",
                    help="artifact glob for audit mode")
    ap.add_argument("--overlap-audit",
                    default="docs/reports/issue-overlap-audit-2026-03-31.md",
                    help="overlap audit markdown file for structural signals")
    ap.add_argument("--repo-root", default=".",
                    help="repo root for repo-reality checks")
    args = ap.parse_args(argv)
    if args.audit:
        issues = (_load_issues_file(args.issues_json)
                  if args.issues_json
                  else fetch_issue_snapshot(args.repo, limit=args.limit))
        findings = audit_issue_hygiene(
            issues,
            artifact_paths=_artifact_paths_from_glob(args.artifact_glob),
            repo_root=args.repo_root,
            overlap_audit_text=_read_text_file(args.overlap_audit),
        )
        if args.audit_format == "json":
            print(format_hygiene_json(findings))
        else:
            print(format_hygiene_markdown(findings), end="")
        return

    issues = fetch_issues(args.repo, limit=args.limit)
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
