#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import claude_session_ecosystem_audit as audit


ALLOWED_INDEX_PATHS = {
    "docs/reports/claude-session-ecosystem-audit-2026-04-09.md",
    "docs/reports/claude-session-ecosystem-audit-2026-04-09.json",
}
WORK_QUEUE_DIRS = ("blocked", "pending", "working", "done")
EVIDENCE_STUB_BASENAME = "stage-prompt-drift-summary.stub.md"


def summarize_package(package: dict) -> dict:
    prompt_files = package.get("prompt_files", [])
    missing_prompts = [item for item in prompt_files if not item.get("exists")]
    evidence_files = package.get("evidence_files", [])
    index_replacements = [path for path in evidence_files if path in ALLOWED_INDEX_PATHS]
    return {
        "work_item": package.get("work_item"),
        "stages": package.get("stages", []),
        "missing_prompt_files": missing_prompts,
        "evidence_files": evidence_files,
        "index_replacements": index_replacements,
        "has_replacement": bool(evidence_files or index_replacements),
    }


def find_drift_issues(stage_prompt_packages: list[dict]) -> list[dict]:
    issues = []
    for package in stage_prompt_packages:
        summary = summarize_package(package)
        if summary["missing_prompt_files"] and not summary["has_replacement"]:
            issues.append(summary)
    return sorted(issues, key=lambda item: (item["work_item"] or "", item["stages"]))


def get_changed_paths(repo_root: Path, base_ref: str, head_ref: str = "HEAD") -> dict[str, set[str]]:
    result = subprocess.run(
        ["git", "diff", "--name-status", f"{base_ref}...{head_ref}"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git diff failed for {base_ref}...{head_ref}")

    deleted: set[str] = set()
    added: set[str] = set()
    modified: set[str] = set()
    for raw_line in result.stdout.splitlines():
        if not raw_line.strip():
            continue
        status, path = raw_line.split("\t", 1)
        if status.startswith("D"):
            deleted.add(path)
        elif status.startswith("A"):
            added.add(path)
        else:
            modified.add(path)
    return {"deleted": deleted, "added": added, "modified": modified}


def filter_newly_introduced_drift(issues: list[dict], changed_paths: dict[str, set[str]]) -> list[dict]:
    deleted = changed_paths.get("deleted", set())
    added = changed_paths.get("added", set())
    filtered = []
    for issue in issues:
        work_item = issue.get("work_item", "")
        missing_prompt_files = issue.get("missing_prompt_files", [])
        deleted_prompts = [item for item in missing_prompt_files if item.get("path") in deleted]
        if not deleted_prompts:
            continue
        has_added_replacement = any(
            path.startswith(f".claude/work-queue/assets/{work_item}/evidence/") or path in ALLOWED_INDEX_PATHS
            for path in added
        )
        if has_added_replacement:
            continue
        updated_issue = dict(issue)
        updated_issue["missing_prompt_files"] = deleted_prompts
        filtered.append(updated_issue)
    return sorted(filtered, key=lambda item: (item["work_item"] or "", item["stages"]))


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    _, sep, remainder = text[4:].partition("\n---\n")
    if not sep:
        return {}
    frontmatter = text[4 : 4 + len(text[4:]) - len(remainder) - len(sep)]
    metadata: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return metadata


def locate_work_item_record(repo_root: Path, work_item: str) -> Path | None:
    queue_root = repo_root / ".claude" / "work-queue"
    for queue_dir in WORK_QUEUE_DIRS:
        directory = queue_root / queue_dir
        if not directory.exists():
            continue
        direct_match = directory / f"{work_item}.md"
        if direct_match.exists():
            return direct_match
        for candidate in sorted(directory.glob("*.md")):
            try:
                text = candidate.read_text(encoding="utf-8")
            except OSError:
                continue
            metadata = parse_frontmatter(text)
            if metadata.get("id") == work_item or f"# {work_item}" in text:
                return candidate
    return None


def detect_blocked_work_item(repo_root: Path, work_item: str) -> dict[str, Any] | None:
    record_path = locate_work_item_record(repo_root, work_item)
    if record_path is None:
        return None
    text = record_path.read_text(encoding="utf-8")
    metadata = parse_frontmatter(text)
    blocked_reasons: list[str] = []
    status = metadata.get("status", "").strip().lower()
    if status == "blocked":
        blocked_reasons.append("frontmatter status=blocked")
    for line in text.splitlines():
        if "blocked" in line.lower():
            blocked_reasons.append(line.strip())
    if not blocked_reasons:
        return None
    return {
        "record_path": str(record_path.relative_to(repo_root)),
        "blocked_reasons": blocked_reasons[:5],
    }


def existing_evidence_stub(evidence_dir: Path) -> Path | None:
    matches = sorted(evidence_dir.glob("stage-prompt-drift-summary.stub*.md"))
    return matches[0] if matches else None


def create_evidence_stub_for_issue(issue: dict, repo_root: Path, generated_at: str) -> dict[str, Any] | None:
    work_item = issue.get("work_item")
    if not work_item:
        return None
    blocked_context = detect_blocked_work_item(repo_root, work_item)
    if blocked_context is None:
        return None

    evidence_dir = repo_root / ".claude" / "work-queue" / "assets" / work_item / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stub_path = existing_evidence_stub(evidence_dir)
    created = False
    if stub_path is None:
        stub_path = evidence_dir / EVIDENCE_STUB_BASENAME
        stages = ", ".join(str(stage) for stage in issue.get("stages", [])) or "none"
        missing_prompts = issue.get("missing_prompt_files", [])
        missing_prompt_lines = [
            f"- `{prompt['path']}` (reads={prompt.get('reads', 0)})" for prompt in missing_prompts
        ] or ["- none recorded"]
        blocked_reason_lines = [f"- {reason}" for reason in blocked_context["blocked_reasons"]]
        stub_text = "\n".join(
            [
                f"# Stage Prompt Drift Evidence Stub ({work_item})",
                "",
                f"Generated automatically at `{generated_at}` because stage-prompt drift was detected for a blocked work item.",
                "",
                "## Drift Summary",
                f"- work_item: `{work_item}`",
                f"- stages: {stages}",
                f"- work_item_record: `{blocked_context['record_path']}`",
                "- reason: prompt artifact was removed without a replacement evidence summary",
                "",
                "## Missing Prompts",
                *missing_prompt_lines,
                "",
                "## Blocked Context",
                *blocked_reason_lines,
                "",
                "## Next Actions",
                "1. Replace this stub with a human-authored evidence summary before deleting prompt history permanently.",
                "2. Document the blocker, current state, and what information from the deleted prompt still matters.",
                "3. Link any supporting logs, issue comments, or review artifacts that justify the deletion.",
                "",
            ]
        )
        stub_path.write_text(stub_text, encoding="utf-8")
        created = True

    return {
        "path": str(stub_path.relative_to(repo_root)),
        "created": created,
        "blocked_context": blocked_context,
    }


def maybe_create_evidence_stubs(issues: list[dict], repo_root: Path, generated_at: str) -> list[dict]:
    updated_issues: list[dict] = []
    for issue in issues:
        updated_issue = dict(issue)
        stub_info = create_evidence_stub_for_issue(updated_issue, repo_root, generated_at)
        if stub_info:
            updated_issue["evidence_stub"] = stub_info
        updated_issues.append(updated_issue)
    return updated_issues


def build_report(
    logs_dir: Path,
    repo_root: Path,
    base_ref: str | None = None,
    head_ref: str = "HEAD",
    write_evidence_stubs: bool = False,
) -> dict:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    audit_summary = audit.build_summary(logs_dir, repo_root)
    stage_prompt_packages = audit_summary.get("stage_prompt_packages", [])
    issues = find_drift_issues(stage_prompt_packages)
    changed_paths = None
    if base_ref:
        changed_paths = get_changed_paths(repo_root, base_ref=base_ref, head_ref=head_ref)
        issues = filter_newly_introduced_drift(issues, changed_paths)
    if write_evidence_stubs:
        issues = maybe_create_evidence_stubs(issues, repo_root, generated_at)
    return {
        "generated_at": generated_at,
        "repo_root": str(repo_root),
        "logs_dir": str(logs_dir),
        "base_ref": base_ref,
        "head_ref": head_ref,
        "write_evidence_stubs": write_evidence_stubs,
        "packages_scanned": len(stage_prompt_packages),
        "issues_found": len(issues),
        "issues": issues,
        "changed_paths": {
            key: sorted(value) for key, value in (changed_paths or {}).items()
        },
    }


def render_markdown(report: dict) -> str:
    lines = [
        f"# Stage prompt drift check — {report['generated_at'][:10]}",
        "",
        "Flags work-queue stage prompt artifacts that were referenced by Claude logs but no longer exist and have no evidence/index replacement.",
        "",
        "## Summary",
        f"- packages_scanned: {report['packages_scanned']}",
        f"- issues_found: {report['issues_found']}",
    ]
    if report.get("base_ref"):
        lines.append(f"- base_ref: {report['base_ref']}")
        lines.append(f"- head_ref: {report.get('head_ref', 'HEAD')}")
    if report.get("write_evidence_stubs"):
        lines.append("- write_evidence_stubs: true")
    lines += [
        "",
        "## Drift issues",
    ]
    issues = report.get("issues", [])
    if not issues:
        lines += ["- none", ""]
        return "\n".join(lines)

    for issue in issues:
        stages = ", ".join(str(stage) for stage in issue.get("stages", [])) or "none"
        work_item = issue["work_item"]
        evidence_dir = f".claude/work-queue/assets/{work_item}/evidence/"
        lines.append(f"- `{work_item}` — stages: {stages} | missing prompts: {len(issue['missing_prompt_files'])}")
        for prompt in issue.get("missing_prompt_files", []):
            lines.append(f"  - missing prompt: `{prompt['path']}` (reads={prompt.get('reads', 0)})")
        lines.append("  - replacement evidence: none")
        evidence_stub = issue.get("evidence_stub")
        if evidence_stub:
            action = "created" if evidence_stub.get("created") else "reused"
            lines.append(f"  - evidence stub: {action} `{evidence_stub['path']}`")
        lines.append(
            f"  - remediation: add a summary artifact under `{evidence_dir}` (for example `gate-evidence-summary.md`) before deleting the prompt artifact"
        )
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Check for stale stage prompt references lacking evidence replacements.")
    parser.add_argument("--repo-root", default=str(repo_root))
    parser.add_argument("--logs-dir", default=str(repo_root / "logs" / "orchestrator" / "claude"))
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    parser.add_argument("--base-ref", help="Only fail for drift newly introduced relative to this git ref")
    parser.add_argument("--head-ref", default="HEAD", help="Comparison head ref when --base-ref is set")
    parser.add_argument(
        "--write-evidence-stubs",
        action="store_true",
        help="Create non-destructive evidence stub summaries for blocked work items",
    )
    parser.add_argument("--fail-on-issues", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    logs_dir = Path(args.logs_dir).resolve()
    report = build_report(
        logs_dir,
        repo_root,
        base_ref=args.base_ref,
        head_ref=args.head_ref,
        write_evidence_stubs=args.write_evidence_stubs,
    )
    markdown = render_markdown(report)

    if args.output_json:
        output_json = Path(args.output_json)
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.output_md:
        output_md = Path(args.output_md)
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(markdown + "\n", encoding="utf-8")
    else:
        print(markdown)

    if args.fail_on_issues and report["issues_found"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
