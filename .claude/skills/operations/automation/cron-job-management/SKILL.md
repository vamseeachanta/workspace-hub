---
name: cron-job-management
description: Patterns for creating, testing, debugging, and maintaining cron-driven
  automation in workspace-hub, including log strategy, failure analysis, and safe
  git-aware job design.
version: 1.0.0
category: operations
type: skill
trigger: manual
auto_execute: false
capabilities:
- cron_design
- cron_debugging
- scheduled_automation
- log_analysis
- git_safe_automation
tools:
- Read
- Write
- Bash
- Grep
related_skills:
- github-actions
requires: []
tags:
- cron
- automation
- scheduled-tasks
- operations
- debugging
---

# Cron Job Management

## When to Use

Use this skill when working on:
- `config/scheduled-tasks/schedule-tasks.yaml`
- `scripts/cron/*`
- machine cron drift / missing jobs
- cron debugging and log inspection
- migrating scheduled jobs to git-safe patterns

## Core Workspace-Hub Pattern

Canonical schedule source:
- `config/scheduled-tasks/schedule-tasks.yaml`

Typical workflow:
1. declare or update the task in YAML
2. implement a dedicated script in `scripts/cron/` when logic is non-trivial
3. ensure logs land in a predictable location
4. test script directly before installing to cron
5. use setup tooling to render/install the crontab
6. verify machine state after install

## Creating a Cron Job

### 1. Define the task in YAML

Include:
- id
- label
- schedule or schedule_by_machine
- machines
- requires
- command
- log
- description

### 2. Prefer wrapper scripts over inline complexity

Good:
```bash
bash scripts/cron/my-job.sh
```

Avoid long inline command chains in YAML when the job:
- performs multiple steps
- uses git
- has branching/error handling
- writes multiple artifacts

### 3. Use git-safe patterns for repo-mutating jobs

If a cron task pulls/commits/pushes, use:
- `scripts/cron/lib/git-safe.sh`

Prefer wrappers that call:
- `git_safe_init`
- `git_safe_pull`
- `git_safe_commit`
- `git_safe_push`
- `git_safe_sync`

## Testing a Cron Job

Before cron installation:

```bash
bash scripts/cron/my-job.sh
bash -n scripts/cron/my-job.sh
```

For schedule rendering:

```bash
bash scripts/cron/setup-cron.sh --dry-run
```

For live installation on the current machine:

```bash
bash scripts/cron/setup-cron.sh --replace
crontab -l
```

## Debugging Cron Failures

Check in this order:

1. YAML declaration exists
2. rendered cron entry looks correct
3. script runs manually
4. log path exists and is writable
5. PATH assumptions are explicit inside the cron command/script
6. any required env vars are resolved in cron context
7. machine assignment matches the host actually being configured

Useful checks:

```bash
crontab -l
rg -n "my-job" config/scheduled-tasks/schedule-tasks.yaml scripts/cron/
tail -n 100 logs/path/to/job.log
```

## Common Failure Modes

- works manually but fails in cron due to PATH/env differences
- command too complex inline in YAML
- missing log file path prevents health monitoring
- git operations race or fail under cron
- task declared in YAML but not installed on machine
- cron entry exists but script path changed

## MANDATORY: Cron Script Prologue

Every cron wrapper script MUST start with PATH injection. Cron's environment is minimal and does not include `$HOME/.local/bin` where `uv`, `node`, etc. live. A script that runs fine in your shell but breaks silently in cron is almost always a PATH issue.

```bash
#!/usr/bin/env bash
set -uo pipefail

# ── Ensure PATH for cron environment ────────────────────────────────────────
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"
```

The cron-health-check script had `uv: command not found` for 5 consecutive days because of this exact issue. The schedule-tasks.yaml command lines include PATH overrides, but wrapper scripts called from those commands do not inherit them in subshells.

## Health Monitoring Realities

### False-Positive Awareness
The cron-health-check reports STALE for weekly jobs (Sunday/Monday) when viewed on Tuesday. Day-of-week schedules (`0 3 * * 0`, `0 4 * * 1`) naturally exceed the 25h default staleness threshold. When doing a health review:
- Weekly jobs scheduled for yesterday or today = EXPECTED, not stale
- Weekly jobs scheduled for 3+ days ago = ACTUALLY stale and needs attention
- Daily jobs > 25h old = genuinely stale

### Log Path Gotchas
- `log: null` in YAML means the health checker cannot monitor the task -- this produces a MISS on glob matching. Every task should have a `log:` field with a valid glob pattern.
- The glob pattern is expanded relative to `$WORKSPACE_HUB`, so `logs/quality/thing-*.log` resolves to `/mnt/local-analysis/workspace-hub/logs/quality/thing-*.log`.

### Pre-Create GitHub Labels
Any script that creates issues with `gh issue create --label "X"` must pre-create the label:
```bash
gh label create "X" --description "..." --color "..." 2>/dev/null || true
```
Without this, `gh issue create` fails with `could not add label: 'X' not found` and the issue is silently not created.

### Legal Scan vs Learning Pipeline
The comprehensive-learning pipeline can be blocked by legal-sanity-scan when session JSONL logs contain client names that match deny-list patterns. Session logs are append-only operational data, not source code. Watch for this pattern:
- `RESULT: FAIL — N block violation(s) found` in learning logs
- `WARNING: learning artifact commit failed — changes remain local`
- Changes accumulate uncommitted across multiple runs

Either exclude the log directory from the legal scan, or use `--diff-only` for the learning pipeline's commit path.

## Health Review Workflow

To perform a comprehensive cron health review:
1. Run `cron-health-check.sh` manually -- this is your first pass
2. Check the cron log directory: `tail -10 logs/research/2026-04-*.log` for research, etc.
3. Cross-reference with `crontab -l` vs `config/scheduled-tasks/schedule-tasks.yaml`
4. Verify the `/today` daily report at `logs/daily/YYYY-MM-DD.md` is fresh
5. If reports exist but health-check is broken, fix the script first, then rerun

## Troubleshooting Guidance

### Missing job on machine
- compare `crontab -l` with `setup-cron.sh --dry-run`
- reinstall with `--replace` if YAML is canonical

### Silent failure
- add or inspect log redirection
- run the exact cron command manually
- check for non-interactive shell assumptions

### Git contention
- replace raw git pipelines with `git-safe` wrappers

### Health monitoring blind spots
- make sure the task has a stable `log:` glob in YAML
- verify monitoring scripts can parse YAML and locate latest log files

## Key Workspace-Hub References

- `config/scheduled-tasks/schedule-tasks.yaml`
- `scripts/cron/setup-cron.sh`
- `scripts/cron/lib/git-safe.sh`
- `scripts/cron/comprehensive-learning-nightly.sh`
- `scripts/monitoring/cron-health-check.sh`

## YAML Date Escaping Gotcha

The `%` character in crontab date format strings must be escaped as `\%`. In `schedule-tasks.yaml`, the YAML `>-` block scalar strips trailing newlines but also adds an extra layer of backslash handling through the `setup-cron.sh` Python rendering pipeline. This creates a quadruple-escape trap:

- Correct in schedule-tasks.yaml: `$(date +\\\\%Y\\\\%m\\\\%d)` (4 backslashes in YAML → `\%Y\%m\%d` in crontab → `%Y%m%d` for date)
- Broken: `$(date +\\\\\\\\%Y\\\\\\\\%m\\\\\\\\%d)` (too many escapes)
- Also broken: `$(date +\\\\%Y\\\\%m\\\\%d)` with only 2 (becomes `%Y%m%d` with single backslash which also fails)

If a cron log shows date format errors or the log file has literal backslash names, check the YAML escaping level. Use `sed -n '/id: my-job/,/^[^ ]/p' config/scheduled-tasks/schedule-tasks.yaml` to inspect.

## Mandatory: schedule Field

Every task in schedule-tasks.yaml MUST have either a `schedule:` field or a `schedule_by_machine:` field. The `cron-health` entry (#1512) was declared in YAML without either, so `setup-cron.sh` silently skipped it -- the Python parser got an empty schedule string and `continue`d. The cron-health-check.py could not find the crontab entry because it was never installed.

After adding or editing a task, always verify:
```bash
bash scripts/cron/setup-cron.sh --dry-run | grep task_id
bash scripts/cron/setup-cron.sh --replace
crontab -l | grep task_id
```

## requires: Capability Validation Gotcha

The `requires:` list in schedule-tasks.yaml is validated against the flattened capabilities in `config/workstations/registry.yaml`. The validator (`scripts/cron/validate-schedule.py`) merges all values from `agent_clis`, `languages`, and `tools` lists for the host machine.

**Rule**: Any tool name in `requires:` must appear in the machine's capabilities. Adding `requires: [gh]` or `requires: [npm]` will FAIL validation unless `gh` / `npm` are also added to the `tools:` list in registry.yaml for the target machine.

```yaml
# WRONG — validation fails with "unknown capability 'gh'":
- id: my-new-job
  requires: [python3, uv, gh]

# CORRECT — first add gh to registry.yaml:
#   dev-primary capabilities:
#     tools: [uv, git, gh]  # ← add here
# Then in schedule-tasks.yaml:
- id: my-new-job
  requires: [python3, uv, gh]
```

After adding new capabilities to registry.yaml, verify:
```bash
uv run --no-project python scripts/cron/validate-schedule.py
```

## Hermes Gateway Cron Scheduler

Hermes has its OWN cron scheduler inside the Gateway process (separate from system crontab). Jobs managed via the `hermes cron` CLI (gmail-daily-digest, memory-bridge-daily, etc.) require the Gateway to be running.

**Starting the Gateway:**
```bash
# Use the systemd service directly — the hermes CLI wrapper
# requires sudo which may not resolve hermes in root PATH
systemctl --hermes-gateway
# Equivalent: sudo systemctl start hermes-gateway
```

**Diagnosing a dead Hermes cron job:**
```bash
sudo systemctl status hermes-gateway   # if not active, no Hermes cron fires
hermes cron list                        # check job next_run_at dates — stale dates mean gateway has been dead
```

**Warning "No messaging platforms enabled"** is non-fatal — the cron ticker still runs. 'local' delivery works fine. Only 'origin'/platform deliveries may be affected.

## uv PEP 723 Inline Metadata in Cron

Scripts with `# /// script\n# dependencies = ["pyyaml"]\n# ///` blocks are PEP 723 inline-metadata scripts. uv treats them as self-contained scripts and auto-installs dependencies.

**CRITICAL**: Do NOT use `python` between `uv run` and the script path:
```bash
# WRONG — bypasses PEP 723 metadata, dependencies NOT installed:
uv run --no-project python scripts/ai/my-script.py
# RIGHT — uv recognizes the script's inline metadata block:
uv run --no-project scripts/ai/my-script.py
```
This bug caused agent-radar to fail for days with "Install PyYAML: uv add pyyaml" even though the script's metadata block declares pyyaml as a dependency.

## False-Positive Counting in Daily Reports

When investigating alerts like "13 CVE references", "42 ERROR/FAIL", etc., always verify the raw count against unique root causes. Common traps:
- `grep -ci "CVE"` counts "0 blocking CVEs" in daily summary lines — false alarm
- Error counts across rolling windows of multi-day logs inflate perceived severity
- Benchmark regressions on sub-millisecond tests are often run-to-run noise, not code issues

## Absolute Paths in Cron Shell Context

Cron's minimal environment may not have `$HOME` set when PATH is expanded at parse time. Use hardcoded absolute paths rather than `$HOME` expansions in shell scripts:
```bash
# UNRELIABLE in cron:
export PATH="$HOME/.local/bin:$PATH"
# RELIABLE:
export PATH="/home/vamsee/.local/bin:$PATH"
# BEST: use absolute path for specific commands:
/home/vamsee/.local/bin/uv run --no-project ...
```

## Rule of Thumb

If a cron task is important enough to debug twice, it is important enough to have:
- a dedicated wrapper script
- a clear log path
- a dry-run/install verification path
- a git-safe strategy if it mutates the repo
