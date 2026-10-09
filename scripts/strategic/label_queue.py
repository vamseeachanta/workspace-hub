"""GitHub label queue normalization for strategic scoring."""

from __future__ import annotations

import json
import subprocess

REPO_SLUG = "vamseeachanta/workspace-hub"


def label_names(issue: dict) -> list[str]:
    labels = issue.get("labels") or []
    names: list[str] = []
    for label in labels:
        if isinstance(label, dict):
            name = label.get("name")
        else:
            name = str(label)
        if name:
            names.append(name)
    return names


def axis_value(labels: list[str], prefix: str) -> str | None:
    for label in labels:
        if label.startswith(prefix):
            return label.split(":", 1)[1]
    return None


def issue_to_work_item(issue: dict) -> dict:
    labels = label_names(issue)
    priority = axis_value(labels, "priority:") or "medium"
    lane = axis_value(labels, "lane:")
    ai_provider = axis_value(labels, "ai:")
    status = axis_value(labels, "dispatch:") or str(issue.get("state", "open")).lower()
    category = (
        axis_value(labels, "cat:")
        or axis_value(labels, "domain:")
        or axis_value(labels, "decision:")
        or "uncategorised"
    )
    return {
        "id": f"#{issue['number']}",
        "title": issue.get("title", ""),
        "priority": priority,
        "complexity": "medium",
        "status": status,
        "category": category,
        "track": ai_provider or lane,
        "blocked_by": [],
        "source": "github-labels",
    }


def gh_query_label_queue(repo: str = REPO_SLUG) -> list[dict]:
    result = subprocess.run(
        [
            "gh", "-R", repo, "issue", "list",
            "-L", "200",
            "--state", "open",
            "--label", "dispatch:ready",
            "--json", "number,title,labels,state",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "gh issue list failed")
    return json.loads(result.stdout or "[]")
