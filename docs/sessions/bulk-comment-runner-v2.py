#!/usr/bin/env python3
"""Retry bulk-comment with fixed throttle detection and conservative pacing.

Diffs vs v1 (lessons from 2026-05-18 first run):
  - Throttle regex now matches "submitted too quickly" (GraphQL addComment error)
  - Pacing 8s/comment (was 2s) — well under the per-token cumulative ceiling
  - Escalating backoff on throttle: 60s, 5min, 30min, then hard exit
  - Hard exit on 3 consecutive throttles regardless of backoff success
  - --sleep-first <seconds> for delayed launch (GitHub cooldown window)
  - Reads target-list path from argv (parameterizable, not hardcoded to /tmp)

Run:  python3 bulk-comment-runner-v2.py <targets.json> [--sleep-first SECONDS]
"""
import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = "vamseeachanta/workspace-hub"
REPO_ROOT = Path(subprocess.check_output(
    ["git", "-C", "/mnt/local-analysis/workspace-hub", "rev-parse", "--show-toplevel"],
    text=True,
).strip())
LOG_DIR = REPO_ROOT / "docs" / "sessions"
LOG_DIR.mkdir(parents=True, exist_ok=True)
BODY_FILE = Path("/tmp/bulk-comment-retry-body.md")

TEMPLATE = """okay this is going kinda viral and tbh my original text was kind of messy, so here's a second pass with the help of Claude:

--
Implement {title}. As you work maintain a running implementation-notes.html file that captures anything I should know about how the implementation diverges from or interprets the spec, including:

- Design decisions: choices you made where the spec was ambiguous
- Deviations: places where you intentionally departed from the spec, and why
- Tradeoffs:  alternatives you considered and why you picked what you did
- Open questions: anything you'd want me to confirm or revise
"""

THROTTLE_PATTERN = re.compile(
    r"(rate limit|abuse|secondary rate|wait a few minutes|submitted too quickly)",
    re.IGNORECASE,
)
BACKOFF_SCHEDULE = [60, 300, 1800]
PACE_SECONDS = 8


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("targets", type=Path, help="JSON file with [{number, title}, ...]")
    p.add_argument("--sleep-first", type=int, default=0, help="Initial sleep in seconds before first request")
    args = p.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    log_path = LOG_DIR / f"bulk-comment-retry-{stamp}.log"

    def log(msg: str) -> None:
        line = f"{now()} {msg}"
        print(line, flush=True)
        with log_path.open("a") as f:
            f.write(line + "\n")

    with args.targets.open() as f:
        targets = json.load(f)
    total = len(targets)

    log(f"# Bulk-comment retry started, repo={REPO}, targets={total}")
    log(f"# Targets file: {args.targets}")
    log(f"# Log: {log_path}")
    log(f"# Pacing: {PACE_SECONDS}s/comment, escalating backoff {BACKOFF_SCHEDULE}, hard-exit on 3 consecutive throttles")

    if args.sleep_first > 0:
        wake_at = datetime.now(timezone.utc).timestamp() + args.sleep_first
        wake_iso = datetime.fromtimestamp(wake_at, timezone.utc).isoformat()
        log(f"# Initial sleep {args.sleep_first}s — will start posting at {wake_iso}")
        time.sleep(args.sleep_first)
        log(f"# Initial sleep complete, beginning posts")

    success = 0
    failed = 0
    consecutive_throttles = 0

    for i, issue in enumerate(targets, 1):
        num = issue["number"]
        title = issue["title"]
        body = TEMPLATE.format(title=title)
        BODY_FILE.write_text(body)

        result = subprocess.run(
            ["gh", "issue", "comment", str(num), "--repo", REPO, "--body-file", str(BODY_FILE)],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            url = result.stdout.strip()
            log(f"OK  [{i}/{total}] #{num} {url}")
            success += 1
            consecutive_throttles = 0
            time.sleep(PACE_SECONDS)
            continue

        err = (result.stderr + result.stdout).strip()
        log(f"ERR [{i}/{total}] #{num} rc={result.returncode} {err[:300]}")
        failed += 1

        if THROTTLE_PATTERN.search(err):
            consecutive_throttles += 1
            log(f"THROTTLE detected (consecutive={consecutive_throttles})")
            if consecutive_throttles > len(BACKOFF_SCHEDULE):
                log(f"HARD-EXIT after {consecutive_throttles} consecutive throttles — cooldown insufficient")
                log(f"# Done (aborted). success={success} failed={failed} processed={i}/{total}")
                return 2
            backoff = BACKOFF_SCHEDULE[consecutive_throttles - 1]
            log(f"Sleeping {backoff}s before retrying #{num}")
            time.sleep(backoff)
            result = subprocess.run(
                ["gh", "issue", "comment", str(num), "--repo", REPO, "--body-file", str(BODY_FILE)],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                url = result.stdout.strip()
                log(f"OK  [{i}/{total}] #{num} (after backoff) {url}")
                success += 1
                failed -= 1
                consecutive_throttles = 0
            else:
                err2 = (result.stderr + result.stdout).strip()
                log(f"ERR [{i}/{total}] #{num} retry-after-backoff rc={result.returncode} {err2[:300]}")
        else:
            consecutive_throttles = 0

        time.sleep(PACE_SECONDS)

    log(f"# Done. success={success} failed={failed} total={total}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
