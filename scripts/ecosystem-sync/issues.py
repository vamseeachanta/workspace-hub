"""GitHub issue filing with dedupe + retry. Never closes or edits."""
from __future__ import annotations
import json
import subprocess
import time
from dataclasses import dataclass
from typing import Literal
from scripts.ecosystem_sync.models import Signal


@dataclass(frozen=True)
class IssueResult:
    status: Literal["created", "skipped-duplicate", "failed", "dedupe-check-failed"]
    url: str | None = None
    error: str | None = None


def open_issue_if_new(signal: Signal, issue_repo: str) -> IssueResult:
    # Dedupe check
    try:
        listing = subprocess.run(
            ["gh", "issue", "list",
             "--repo", issue_repo,
             "--search", signal.title,
             "--state", "open",
             "--json", "number,title", "--limit", "20"],
            capture_output=True, text=True, check=True, timeout=30,
        )
        existing = json.loads(listing.stdout or "[]")
    except (subprocess.CalledProcessError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
        return IssueResult(status="dedupe-check-failed", error=str(e))

    if any(issue.get("title") == signal.title for issue in existing):
        return IssueResult(status="skipped-duplicate")

    # Create with one retry
    labels = [f"sync:{signal.kind}"]
    for attempt in (1, 2):
        try:
            result = subprocess.run(
                ["gh", "issue", "create",
                 "--repo", issue_repo,
                 "--title", signal.title,
                 "--body", signal.body,
                 *sum([["--label", l] for l in labels], [])],
                capture_output=True, text=True, check=True, timeout=30,
            )
            url = result.stdout.strip().splitlines()[-1] if result.stdout else None
            return IssueResult(status="created", url=url)
        except subprocess.CalledProcessError as e:
            if attempt == 2:
                return IssueResult(status="failed", error=e.stderr or str(e))
            time.sleep(10)
        except subprocess.TimeoutExpired as e:
            if attempt == 2:
                return IssueResult(status="failed", error=str(e))
            time.sleep(10)
    return IssueResult(status="failed", error="unreachable")
