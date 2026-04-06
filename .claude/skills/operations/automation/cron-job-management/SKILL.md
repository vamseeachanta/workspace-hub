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

## Rule of Thumb

If a cron task is important enough to debug twice, it is important enough to have:
- a dedicated wrapper script
- a clear log path
- a dry-run/install verification path
- a git-safe strategy if it mutates the repo
