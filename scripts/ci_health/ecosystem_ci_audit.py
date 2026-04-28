#!/usr/bin/env python
"""Generate a bounded cross-repo CI health audit for workspace-hub issue #2424."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RELEVANT_EVENTS = {"push", "schedule", "workflow_dispatch", "dynamic"}
RED_CONCLUSIONS = {
    "action_required",
    "cancelled",
    "failure",
    "startup_failure",
    "timed_out",
}
GREEN_CONCLUSIONS = {"success", "neutral", "skipped"}


@dataclass(frozen=True)
class EcosystemRepo:
    full_name: str
    tracker: str
    note: str


EXPECTED_REPOS = [
    EcosystemRepo(
        "vamseeachanta/workspace-hub",
        "#2437",
        "workspace-hub child closed; parent remains rollup",
    ),
    EcosystemRepo(
        "vamseeachanta/worldenergydata", "#2433", "main CI and Dependabot blocker lane"
    ),
    EcosystemRepo(
        "vamseeachanta/digitalmodel",
        "#2441 / #2490",
        "pylife child closed; coverage-gate follow-up open",
    ),
    EcosystemRepo(
        "vamseeachanta/assethold",
        "#2442 / #2448 / #2459",
        "startup/smoke children closed; hardening plan remains",
    ),
    EcosystemRepo(
        "vamseeachanta/achantas-data",
        "#2443",
        "CI restored; scheduled link-check must stay observable",
    ),
    EcosystemRepo(
        "vamseeachanta/aceengineer-admin", "#2444", "minimal CI bootstrap child closed"
    ),
    EcosystemRepo(
        "vamseeachanta/assetutilities", "reference", "known green reference repo"
    ),
]

TRACKED_ISSUES = [2424, 2433, 2437, 2441, 2442, 2443, 2444, 2448, 2459, 2490]


def _run_json(command: list[str]) -> Any:
    completed = subprocess.run(
        command, check=True, capture_output=True, text=True, timeout=60
    )
    return json.loads(completed.stdout)


def latest_relevant_runs_by_workflow(
    runs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return the newest main-branch CI-like run for each workflow."""

    latest: dict[str, dict[str, Any]] = {}
    for run in sorted(runs, key=lambda item: item.get("createdAt") or "", reverse=True):
        if run.get("headBranch") != "main":
            continue
        if run.get("event") not in RELEVANT_EVENTS:
            continue
        workflow_name = run.get("workflowName") or "<unnamed>"
        latest.setdefault(workflow_name, run)
    return list(latest.values())


def classify_repo(latest_runs: list[dict[str, Any]]) -> dict[str, Any]:
    if not latest_runs:
        return {"state": "no-signal", "red_workflows": []}

    red_workflows = [
        run.get("workflowName") or "<unnamed>"
        for run in latest_runs
        if run.get("status") != "completed" or run.get("conclusion") in RED_CONCLUSIONS
    ]
    unknown_workflows = [
        run.get("workflowName") or "<unnamed>"
        for run in latest_runs
        if run.get("status") == "completed"
        and run.get("conclusion") not in RED_CONCLUSIONS
        and run.get("conclusion") not in GREEN_CONCLUSIONS
    ]

    if red_workflows:
        return {"state": "red", "red_workflows": red_workflows}
    if unknown_workflows:
        return {"state": "unknown", "red_workflows": []}
    return {"state": "green", "red_workflows": []}


def fetch_repo_runs(repo: str, limit: int) -> list[dict[str, Any]]:
    return _run_json(
        [
            "gh",
            "run",
            "list",
            "--repo",
            repo,
            "--branch",
            "main",
            "--limit",
            str(limit),
            "--json",
            "databaseId,workflowName,displayTitle,headBranch,conclusion,status,createdAt,url,event",
        ]
    )


def fetch_issue_rows() -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    for issue_number in TRACKED_ISSUES:
        try:
            raw = _run_json(
                [
                    "gh",
                    "issue",
                    "view",
                    str(issue_number),
                    "--repo",
                    "vamseeachanta/workspace-hub",
                    "--json",
                    "number,state,labels,title,url",
                ]
            )
        except subprocess.CalledProcessError:
            rows[issue_number] = {
                "state": "MISSING",
                "labels": [],
                "title": "",
                "url": "",
            }
            continue
        rows[issue_number] = {
            "state": raw["state"],
            "labels": [label["name"] for label in raw.get("labels", [])],
            "title": raw.get("title", ""),
            "url": raw.get("url", ""),
        }
    return rows


def _state_label(state: str) -> str:
    return {
        "green": "Green",
        "red": "Red",
        "no-signal": "No signal",
        "unknown": "Unknown",
    }.get(state, state.title())


def _repo_url(repo: str) -> str:
    return f"https://github.com/{repo}"


def _format_run(run: dict[str, Any]) -> str:
    workflow = run.get("workflowName") or "<unnamed>"
    conclusion = run.get("conclusion") or run.get("status") or "unknown"
    created_at = run.get("createdAt") or "unknown-time"
    url = run.get("url") or ""
    if url:
        return f"[{workflow}]({url}) `{conclusion}` at `{created_at}`"
    return f"{workflow} `{conclusion}` at `{created_at}`"


def _open_issue_summary(issue_rows: dict[int, dict[str, Any]]) -> str:
    open_items = [
        f"`#{issue_number}` OPEN `{','.join(row.get('labels', [])) or 'no-labels'}`"
        for issue_number, row in sorted(issue_rows.items())
        if row.get("state") == "OPEN"
    ]
    return "; ".join(open_items) if open_items else "None"


def render_markdown_report(
    repo_runs: dict[str, list[dict[str, Any]]],
    issue_rows: dict[int, dict[str, Any]],
    generated_at: str,
) -> str:
    repo_names = {repo.full_name for repo in EXPECTED_REPOS}
    missing = sorted(repo_names.difference(repo_runs))
    if missing:
        raise ValueError(f"Missing repo run evidence for: {', '.join(missing)}")

    rows: list[tuple[EcosystemRepo, dict[str, Any], list[dict[str, Any]]]] = []
    counts = {"green": 0, "red": 0, "no-signal": 0, "unknown": 0}
    for repo in EXPECTED_REPOS:
        latest_runs = latest_relevant_runs_by_workflow(repo_runs[repo.full_name])
        classification = classify_repo(latest_runs)
        counts[classification["state"]] = counts.get(classification["state"], 0) + 1
        rows.append((repo, classification, latest_runs))

    lines = [
        "# Issue #2424 ecosystem CI health audit",
        "",
        f"Generated: `{generated_at}`",
        "",
        "## Summary",
        "",
        "| State | Count |",
        "|---|---:|",
        f"| Green | {counts.get('green', 0)} |",
        f"| Red | {counts.get('red', 0)} |",
        f"| No signal | {counts.get('no-signal', 0)} |",
        f"| Unknown | {counts.get('unknown', 0)} |",
        "",
        f"Open tracked issue evidence: {_open_issue_summary(issue_rows)}",
        "",
        "## Repo Evidence",
        "",
        "| Repo | State | Tracker | Latest main-branch workflow evidence | Note |",
        "|---|---|---|---|---|",
    ]

    for repo, classification, latest_runs in rows:
        if latest_runs:
            evidence = "<br>".join(_format_run(run) for run in latest_runs)
        else:
            evidence = "No relevant `main` push/schedule/workflow_dispatch/dynamic runs returned by `gh run list`."
        lines.append(
            "| "
            f"[`{repo.full_name}`]({_repo_url(repo.full_name)}) | "
            f"{_state_label(classification['state'])} | "
            f"{repo.tracker} | "
            f"{evidence} | "
            f"{repo.note} |"
        )

    lines.extend(
        [
            "",
            "## Guard Contract",
            "",
            "- The audit filters to `main` branch runs and CI-like events so Dependabot PR noise cannot mask red main evidence.",
            "- One latest run per workflow is shown to avoid stale older failures overriding newer green runs.",
            "- The seven-repo scoreboard is hard-coded because #2424 is a fixed ecosystem rollup, not a broad repo rewrite lane.",
            "- This report is evidence only; child issue implementation and closure still follow their individual approved plans.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "uv run python scripts/ci_health/ecosystem_ci_audit.py "
            "--output docs/reports/2026-04-27-issue-2424-ecosystem-ci-health-audit.md "
            "--limit 30",
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def collect_live_repo_runs(limit: int) -> dict[str, list[dict[str, Any]]]:
    return {
        repo.full_name: fetch_repo_runs(repo.full_name, limit)
        for repo in EXPECTED_REPOS
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, help="Write the Markdown report to this path."
    )
    parser.add_argument(
        "--limit", type=int, default=20, help="Run rows to fetch per repository."
    )
    parser.add_argument(
        "--generated-at",
        default=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    )
    args = parser.parse_args()

    report = render_markdown_report(
        collect_live_repo_runs(args.limit),
        fetch_issue_rows(),
        generated_at=args.generated_at,
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
