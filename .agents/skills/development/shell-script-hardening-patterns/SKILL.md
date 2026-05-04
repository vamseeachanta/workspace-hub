---
name: shell-script-hardening-patterns
description: Harden Bash automation scripts with TDD-first static and behavioral checks, safe Python invocation via uv, locking, persistent state, and review-driven correction loops.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Shell Script Hardening Patterns

Use when fixing or extending repo automation scripts (`*.sh`) that:
- call Python from Bash
- run as cron/watcher jobs
- mutate shared state
- interact with git or GitHub CLI
- are prone to silent failures or duplicate processing

## Core lessons

1. Write failing tests first, even for shell scripts.
2. For shell-script refactors, use a mix of:
   - static tests on script text for banned patterns
   - behavioral tests on companion Python logic
   - direct `bash -n` syntax checks
   - direct dry-run/manual command execution
3. After implementation, run an adversarial review. Expect at least one concurrency/state bug to surface.
4. If review finds a shared-state race, patch it immediately and re-run tests.

## Pattern 1: Safe Python invocation from Bash

Avoid:
- `python3 -c "...${user_or_path}..."`
- `uv run ... python -c "...${shell_var}..."`

Prefer:

```bash
uv run --no-project python - "$ARG1" "$ARG2" <<'PY'
import sys
from pathlib import Path

arg1 = sys.argv[1]
arg2 = sys.argv[2]
print(arg1, arg2)
PY
```

Rules:
- Pass dynamic values as CLI args, not embedded into Python source.
- In this workspace, use `uv run` rather than bare `python3`.
- Use heredoc Python for anything more than a trivial constant expression.

## Pattern 2: Schema alignment for shell + Python validator pairs

If a shell script consumes the same manifest/config as a Python validator:
- make the Python validator the pre-flight source of truth
- only keep minimal shell parsing for iteration/execution after validation
- add a bypass flag only when explicitly needed (`--skip-validation`)
- update the example manifest at the same time as the parser/schema

Checklist:
- same field names everywhere
- same required/optional semantics
- example file matches current schema
- tests cover duplicate names, empty lists, and invalid schema

## Pattern 3: Watcher locking for cron/background loops

For scripts like `watch-results.sh`:
- create a dedicated state dir
- use a single lock file with non-blocking `flock`
- exit gracefully if another instance is already running
- acquire the lock before mutating shared state

Template:

```bash
STATE_DIR="${REPO_ROOT}/queue/.watcher-state"
LOCK_FILE="${STATE_DIR}/watch-results.lock"
mkdir -p "${STATE_DIR}"

exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
  echo "another watcher is already running; exiting gracefully"
  exit 0
fi
```

Important pitfall:
- Do not initialize/reset shared counters before lock acquisition.
- A concurrent no-op invocation can otherwise wipe active state.

## Pattern 4: Surface git pull failures instead of masking them

Avoid:

```bash
git pull origin main 2>/dev/null || true
```

Prefer a sync helper that:
- captures stdout/stderr
- logs the failure with timestamp
- increments a persistent failure counter
- resets the counter on success
- exits non-zero after `N` consecutive failures

Recommended state files:
- `git-pull-failures.count`
- `git-pull-failures.log`

Expose the count in the health/reporting script so operators can see drift even if the watcher is not currently running.

## Pattern 5: Health script reporting

If a health script summarizes queue/cron state:
- include operational counters like `git_pull_failures`
- emit JSON mode for machine consumption
- keep human-readable mode for manual debugging
- use `uv run --no-project python -` rather than `python3 -c` for JSON serialization or YAML extraction

## Pattern 6: GitHub issue idempotency in shell scripts

For automation that opens issues:
- check `gh auth status` before mutation
- write auth outcome into the JSON summary/log artifact
- search for an existing open issue with the target label before creating a new one
- reuse/update/comment on the existing issue instead of creating duplicates

Important pitfall:
- If unauthenticated failure is possible, write the JSON summary before exiting non-zero so the failure is still observable in logs.

## Test strategy that worked well

### Static tests
Read script text and assert:
- banned strings are absent (`python3 -c`, `git pull ... || true`)
- required mechanisms are present (`flock`, `gh auth status`, `gh issue list`)
- important ordering constraints hold (`acquire_lock` occurs before state reset)

### Behavioral tests
Use companion Python tests to validate:
- schema behavior
- duplicate detection
- empty-manifest rejection
- queue health aggregation logic

### Direct execution
Always run all of:
- `bash -n path/to/script.sh`
- targeted `uv run pytest ...`
- one real dry-run or `--once` invocation if the script supports it

## Review loop

After the first green pass:
1. Request a focused review on correctness + race conditions.
2. If review finds a race or state-ordering bug, add a new failing test first.
3. Patch immediately.
4. Re-run tests and re-review.

This was especially valuable for catching a subtle bug where a concurrent watcher invocation reset a failure counter before lock acquisition.

## Commit slicing

For multi-issue shell hardening, group commits by closely related fixes:
- schema + validation integration
- shell-injection hardening
- watcher locking + failure surfacing
- GitHub automation idempotency

## Commands to remember

```bash
bash -n scripts/foo.sh
uv run pytest tests/path/test_script_behavior.py -q
bash scripts/foo.sh --dry-run
bash scripts/foo.sh --once
```

## When this skill is a good fit

Use it when you see any of these symptoms:
- shell script embeds user/path values inside Python code strings
- cron/watch scripts silently swallow git failures
- duplicate processing from concurrent script runs
- automation keeps opening duplicate GitHub issues
- schema defined one way in Python and another way in Bash
