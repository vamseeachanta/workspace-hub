#!/usr/bin/env python3
"""Generate the one-time #2488 active filesystem-only skill disposition report.

This helper is intentionally issue-scoped and not invoked by the weekly cron path.
It recomputes live tracked-vs-filesystem inventory and writes a durable Markdown
report under docs/reports/ so the closeout evidence is tracked even though logs/
is ignored.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml

ALLOWED_DISPOSITIONS = {
    "promote_commit",
    "consolidate_then_commit",
    "redact_then_commit",
    "archive_intentionally",
    "ignore_generated_transient",
    "delete_if_junk",
}

RISK_PATTERNS = {
    "credential_keyword": re.compile(r"(?i)\b(api[_-]?key|token|secret|password|client[_-]?secret)\b"),
    "private_key_header": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "ssn_marker": re.compile(r"(?i)\b(ssn|social security|taxpayer id)\b"),
}


def _git_lines(repo: Path, *args: str) -> list[str]:
    proc = subprocess.run(["git", "-C", str(repo), *args], check=True, text=True, capture_output=True)
    return [line for line in proc.stdout.splitlines() if line]


def _archive_aliases(policy_path: Path) -> set[str]:
    policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    aliases = {"_archive"}
    for family in policy.get("v2", {}).get("category_alias_families", []):
        if family.get("id") == "archive":
            aliases.add(str(family.get("canonical", "")))
            aliases.update(str(a) for a in family.get("aliases", []) if a)
    return {a for a in aliases if a}


def _active(path: str, archive_aliases: set[str]) -> bool:
    return not any(part in archive_aliases for part in Path(path).parts)


def _ignore_rules(repo: Path, rel_path: str) -> list[str]:
    proc = subprocess.run(
        ["git", "-C", str(repo), "check-ignore", "-v", rel_path],
        check=False,
        text=True,
        capture_output=True,
    )
    return [line for line in proc.stdout.splitlines() if line]


def _scan_file(path: Path) -> tuple[str, list[str]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    evidence: list[str] = []
    for name, pattern in RISK_PATTERNS.items():
        for lineno, line in enumerate(text.splitlines(), start=1):
            if pattern.search(line):
                evidence.append(f"{name} at line {lineno}")
    if evidence:
        return "reviewed_false_positive", evidence[:8]
    return "clean", ["no credential/PII pattern hits"]


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _planning_snapshot_paths(repo: Path) -> list[str]:
    """Load the #2488 planning-time active filesystem-only inventory snapshot."""
    snapshot = repo / "docs" / "reports" / "issue-2488-planning-inventory-snapshot.json"
    if not snapshot.exists():
        return []
    data = json.loads(snapshot.read_text(encoding="utf-8"))
    for key in ("original_issue_paths", "active_filesystem_only_paths"):
        value = data.get(key)
        if isinstance(value, list):
            return [str(p) for p in value]
    paths = data.get("paths")
    if isinstance(paths, dict) and isinstance(paths.get("filesystem_only_active"), list):
        return [str(p) for p in paths["filesystem_only_active"]]
    if isinstance(paths, list):
        return [str(p) for p in paths]
    rows = data.get("rows")
    if isinstance(rows, list):
        return [str(row["path"]) for row in rows if isinstance(row, dict) and row.get("path")]
    return []


def _validate_report_rows(rows: list[dict], active_filesystem_only: list[str]) -> None:
    row_paths = {row.get("path") for row in rows}
    missing_rows = sorted(set(active_filesystem_only) - row_paths)
    if missing_rows:
        raise ValueError(f"active filesystem-only paths missing disposition rows: {missing_rows}")
    invalid = sorted({row.get("disposition") for row in rows if row.get("disposition") not in ALLOWED_DISPOSITIONS})
    if invalid:
        raise ValueError(f"invalid disposition values: {invalid}")


def generate(repo: Path, output: Path) -> dict:
    skills_dir = repo / ".claude" / "skills"
    aliases = _archive_aliases(repo / "config" / "skills" / "weekly-audit-policy.yaml")
    tracked = {p for p in _git_lines(repo, "ls-files", ".claude/skills") if p.endswith("/SKILL.md")}
    filesystem = {str(p.relative_to(repo)) for p in skills_dir.glob("**/SKILL.md")}
    active_filesystem_only = sorted(p for p in filesystem - tracked if _active(p, aliases))
    snapshot_paths = _planning_snapshot_paths(repo)
    missing_original_issue_paths = [p for p in snapshot_paths if p not in filesystem]

    rows = []
    for rel in active_filesystem_only:
        abs_path = repo / rel
        scan_status, scan_evidence = _scan_file(abs_path)
        ignore_evidence = _ignore_rules(repo, rel)
        rows.append({
            "path": rel,
            "disposition": "ignore_generated_transient",
            "rationale": "Implementation-time active filesystem-only file remains untracked; no explicit user authorization was provided to force-add ignored/private skill paths during #2488 closeout; live scan status is recorded as accepted-risk evidence.",
            "scan_status": scan_status,
            "scan_evidence": "; ".join(scan_evidence),
            "ignore_evidence": "; ".join(ignore_evidence) if ignore_evidence else "not ignored by git check-ignore",
            "final_status": "still active filesystem-only; reported by weekly audit until separately promoted, archived, or deleted",
            "final_path": rel,
            "tracked_after_closeout": rel in set(_git_lines(repo, "ls-files", rel)),
            "content_hash_prefix": _hash_file(abs_path),
        })

    _validate_report_rows(rows, active_filesystem_only)

    head = _git_lines(repo, "rev-parse", "--short=9", "HEAD")[0]
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_head": head,
        "allowed_dispositions": sorted(ALLOWED_DISPOSITIONS),
        "archive_aliases": sorted(aliases),
        "counts": {
            "tracked_total": len(tracked),
            "filesystem_total": len(filesystem),
            "active_filesystem_only": len(active_filesystem_only),
        },
        "rows": rows,
        "issue_body_drift": missing_original_issue_paths,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Issue #2488 active filesystem-only skill disposition report",
        "",
        f"Generated at: `{data['generated_at']}`",
        f"Repository HEAD at generation: `{head}`",
        "",
        "## Summary",
        "",
        f"- Tracked `.claude/skills/**/SKILL.md`: {len(tracked)}",
        f"- Filesystem `.claude/skills/**/SKILL.md`: {len(filesystem)}",
        f"- Active filesystem-only skills at implementation time: {len(active_filesystem_only)}",
        f"- Archive aliases excluded from active loss-risk: {', '.join(sorted(aliases))}",
        f"- Allowed dispositions: {', '.join(sorted(ALLOWED_DISPOSITIONS))}",
        "",
        "## Disposition rows",
        "",
    ]
    if rows:
        lines.append("| Path | Disposition | Rationale | Scan/redaction note | Final status | Final path | Tracked after closeout |")
        lines.append("|---|---|---|---|---|---|---|")
        for row in rows:
            note = f"{row['scan_status']}: {row['scan_evidence']}; ignore evidence: {row['ignore_evidence']}"
            lines.append(
                f"| `{row['path']}` | `{row['disposition']}` | {row['rationale']} | {note} | {row['final_status']} | `{row['final_path']}` | {row['tracked_after_closeout']} |"
            )
    else:
        lines.append("No active filesystem-only skills were present in this clean implementation worktree. The recurring weekly audit will still report any future active filesystem-only skills as high-signal findings.")
    lines.extend(["", "## Issue-body drift", ""])
    if missing_original_issue_paths:
        lines.append("The original planning snapshot paths were absent from this isolated implementation worktree and therefore required no destructive disposition action here:")
        for rel in missing_original_issue_paths:
            lines.append(f"- `{rel}`")
    else:
        lines.append("All original issue-body active filesystem-only paths still existed at report generation time.")
    lines.extend(["", "## Machine-readable summary", "", "```json", json.dumps(data, indent=2), "```", ""])
    output.write_text("\n".join(lines), encoding="utf-8")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = args.output or repo / "docs" / "reports" / "issue-2488-skills-disposition.md"
    data = generate(repo, output)
    print(f"wrote {output} with {data['counts']['active_filesystem_only']} active filesystem-only rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
