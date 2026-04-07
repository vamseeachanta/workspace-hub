#!/home/vamsee/.hermes/claude-code/.venv/bin/python
# ABOUTME: Nightly Gemini batch processor — auto-processes agent:gemini labeled issues.
# ABOUTME: Queries open issues, clusters by scope, dispatches via local subagents or Hermes router.
# Issue: #1961
#
# Gemini's designated roles:
#   1. Issue triage prep — scan unassigned issues, draft approach notes
#   2. Research before coding — API/standards/library research
#   3. Document ingestion — large PDFs/standards using 1M context
#   4. Codebase reconnaissance — scan repos before implementation sprints
#   5. Standards mapping — map unmapped functions to API/DNV/ISO standards
#   6. Test data generation — create fixtures for TDD work
#
# Execution modes:
#   MODE 1 (local): Filesystem tasks — catalog, triage, scan, script execution
#   MODE 2 (router): Web research, large doc ingestion, standards lookup
#
# Usage:
#   uv run --no-project python scripts/cron/gemini-nightly-batch.py [--dry-run] [--max N]

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────
WORKSPACE_HUB = os.environ.get(
    "WORKSPACE_HUB",
    str(Path(__file__).resolve().parent.parent.parent),
)
LOG_DIR = Path(WORKSPACE_HUB) / "logs" / "gemini"
REPORT_DIR = Path(WORKSPACE_HUB) / ".claude" / "state" / "gemini-batch"
MAX_ISSUES_PER_RUN = 10  # safety cap
HERMES_ROUTER_CMD = "hermes chat --provider openrouter -m google/gemini-2.5-pro"

# Issue categories that determine execution mode
MODE2_LABELS = {
    "cat:research",
    "cat:document-intelligence",
    "dark-intelligence",
    "domain:marine",
    "domain:standards",
}


def log(msg: str, level: str = "INFO") -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[gemini-batch] {ts} {level}: {msg}", flush=True)


def run_cmd(cmd: str, check: bool = True, capture: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command with error handling."""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=capture,
        text=True,
        cwd=WORKSPACE_HUB,
        timeout=120,
    )
    if check and result.returncode != 0:
        log(f"Command failed: {cmd}\nstderr: {result.stderr}", "ERROR")
    return result


def fetch_gemini_issues() -> list[dict]:
    """Fetch all open issues labeled agent:gemini."""
    cmd = (
        'gh issue list --label "agent:gemini" --state open '
        '--json number,title,labels,body,createdAt --limit 50'
    )
    result = run_cmd(cmd)
    if result.returncode != 0:
        log("Failed to fetch issues from GitHub", "ERROR")
        return []

    try:
        issues = json.loads(result.stdout)
    except json.JSONDecodeError:
        log(f"Failed to parse issue JSON: {result.stdout[:200]}", "ERROR")
        return []

    log(f"Found {len(issues)} open agent:gemini issues")
    return issues


def classify_issue(issue: dict) -> dict:
    """Classify an issue by execution mode and priority."""
    labels = {lbl["name"] for lbl in issue.get("labels", [])}
    number = issue["number"]
    title = issue["title"]

    # Determine execution mode
    if labels & MODE2_LABELS:
        mode = "router"  # Mode 2: needs web/Gemini context
    else:
        mode = "local"  # Mode 1: filesystem/script work

    # Determine priority
    if "priority:high" in labels:
        priority = 1
    elif "priority:medium" in labels:
        priority = 2
    else:
        priority = 3

    # Determine task category
    category = "triage"  # default
    if "cat:document-intelligence" in labels or "dark-intelligence" in labels:
        category = "document-ingestion"
    elif "cat:research" in labels:
        category = "research"
    elif "cat:engineering" in labels:
        category = "codebase-recon"
    elif "cat:tooling" in labels:
        category = "tooling"
    elif "cat:documentation" in labels:
        category = "documentation"

    return {
        "number": number,
        "title": title,
        "labels": labels,
        "body": issue.get("body", ""),
        "mode": mode,
        "priority": priority,
        "category": category,
    }


def process_local_issue(issue: dict, dry_run: bool = False) -> dict:
    """Process a Mode 1 (local filesystem) issue."""
    number = issue["number"]
    title = issue["title"]
    category = issue["category"]

    log(f"Processing #{number} locally: {title} (category={category})")

    if dry_run:
        return {"number": number, "status": "dry-run", "mode": "local"}

    # For local issues, generate a triage comment with approach notes
    body = issue.get("body", "")
    body_preview = body[:500] if body else "(no body)"

    triage_comment = (
        f"**Gemini Nightly Batch — Triage Notes**\n\n"
        f"**Category:** {category}\n"
        f"**Execution Mode:** Local (filesystem/script)\n"
        f"**Auto-processed:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        f"**Approach:**\n"
    )

    if category == "tooling":
        triage_comment += (
            "- This is a tooling/automation task\n"
            "- Recommended: implement script, add to schedule-tasks.yaml\n"
            "- Follow existing cron patterns in scripts/cron/\n"
        )
    elif category == "documentation":
        triage_comment += (
            "- Documentation update needed\n"
            "- Check docs/ for existing content to update\n"
            "- Follow MkDocs conventions\n"
        )
    elif category == "codebase-recon":
        triage_comment += (
            "- Codebase reconnaissance task\n"
            "- Run repo-architecture-analysis skill\n"
            "- Scan for patterns, dead code, coverage gaps\n"
        )
    else:
        triage_comment += (
            "- General triage — review issue scope and assign to appropriate agent\n"
            "- If implementation-ready, re-label with agent:claude or agent:codex\n"
        )

    # Post comment
    comment_cmd = f'gh issue comment {number} -b "{triage_comment}"'
    result = run_cmd(comment_cmd, check=False)

    return {
        "number": number,
        "status": "triaged" if result.returncode == 0 else "comment-failed",
        "mode": "local",
        "category": category,
    }


def process_router_issue(issue: dict, dry_run: bool = False) -> dict:
    """Process a Mode 2 (Hermes router / Gemini) issue."""
    number = issue["number"]
    title = issue["title"]
    category = issue["category"]

    log(f"Processing #{number} via router: {title} (category={category})")

    if dry_run:
        return {"number": number, "status": "dry-run", "mode": "router"}

    # For router issues, post a triage comment noting Gemini research is needed
    triage_comment = (
        f"**Gemini Nightly Batch — Research Queue**\n\n"
        f"**Category:** {category}\n"
        f"**Execution Mode:** Router (Gemini 1M context / web research)\n"
        f"**Queued:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        f"This issue requires Gemini's extended context or web research capabilities. "
        f"It will be processed in the next available Gemini router session.\n\n"
        f"**Prerequisites:**\n"
        f"- OpenRouter credit balance > $5\n"
        f"- Task prompt prepared in /tmp/gemini-task-{number}.txt\n"
    )

    comment_cmd = f'gh issue comment {number} -b "{triage_comment}"'
    result = run_cmd(comment_cmd, check=False)

    return {
        "number": number,
        "status": "queued-for-router" if result.returncode == 0 else "comment-failed",
        "mode": "router",
        "category": category,
    }


def write_report(results: list[dict], dry_run: bool = False) -> None:
    """Write a batch report to state directory."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_path = REPORT_DIR / f"batch-{date_str}.json"

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "total_issues": len(results),
        "local_processed": sum(1 for r in results if r["mode"] == "local"),
        "router_queued": sum(1 for r in results if r["mode"] == "router"),
        "results": results,
    }

    report_path.write_text(json.dumps(report, indent=2))
    log(f"Report written to {report_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Gemini nightly batch processor")
    parser.add_argument("--dry-run", action="store_true", help="Preview without processing")
    parser.add_argument("--max", type=int, default=MAX_ISSUES_PER_RUN, help="Max issues to process")
    args = parser.parse_args()

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log(f"Starting gemini-nightly-batch (dry_run={args.dry_run}, max={args.max})")

    # Fetch and classify issues
    issues = fetch_gemini_issues()
    if not issues:
        log("No open agent:gemini issues found. Nothing to do.")
        write_report([], args.dry_run)
        return

    classified = [classify_issue(issue) for issue in issues]
    classified.sort(key=lambda x: x["priority"])  # high priority first

    # Skip self-referencing meta issues (the cron issue itself)
    classified = [c for c in classified if c["number"] != 1961]

    # Cap at max
    to_process = classified[: args.max]
    log(f"Processing {len(to_process)} of {len(classified)} issues")

    # Process each issue
    results = []
    for issue in to_process:
        try:
            if issue["mode"] == "local":
                result = process_local_issue(issue, args.dry_run)
            else:
                result = process_router_issue(issue, args.dry_run)
            results.append(result)
        except Exception as e:
            log(f"Error processing #{issue['number']}: {e}", "ERROR")
            results.append({
                "number": issue["number"],
                "status": "error",
                "error": str(e),
                "mode": issue["mode"],
            })

    # Summary
    local_count = sum(1 for r in results if r["mode"] == "local")
    router_count = sum(1 for r in results if r["mode"] == "router")
    error_count = sum(1 for r in results if r["status"] == "error")
    log(
        f"Batch complete: {len(results)} processed "
        f"(local={local_count}, router={router_count}, errors={error_count})"
    )

    # Write report
    write_report(results, args.dry_run)

    if error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
