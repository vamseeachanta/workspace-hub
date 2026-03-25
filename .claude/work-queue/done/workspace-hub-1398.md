---
id: workspace-hub#1398
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1398
title: "Review scheduled tasks & fix daily summaries not surfacing across all workstations"
type: bug
status: done
priority: high
complexity: medium
route: B
created_at: "2026-03-25"
closed_at: "2026-03-25"
target_repos: [workspace-hub]
computer: ace-linux-1
execution_machine: ace-linux-1
plan_workstations: [ace-linux-1]
execution_workstations: [ace-linux-1]
category: ops
subcategory: scheduling
tags: [scheduled-tasks, daily-summaries, cross-machine, cron, triggers]
plan_reviewed: true
plan_approved: true
percent_complete: 100
audit_completed: "2026-03-25"
spec_file: specs/modules/jaunty-sparking-hollerith.md
spinoffs: [workspace-hub#1409, workspace-hub#1410, workspace-hub#1411]
resume_notes: |
  Complete. Crontab installed (14 entries from YAML). /today smoke tested.
  session-analysis added to YAML. claude-memory-backup fixed to use ace-linux-2.
  setup-cron.sh append-only bug noted — used crontab replacement workaround.
---

# Review Scheduled Tasks & Fix Daily Summary Delivery

## Problem
Daily summaries are **not being brought to attention** across all workstations.
Scheduled tasks need a full audit to determine what's running, what's broken,
and what's missing.

## Scope

### 1. Audit All Scheduled Tasks
- List all cron jobs, scheduled triggers, and recurring agents across all machines
- Verify each is actually firing (check logs, last-run timestamps)
- Identify orphaned, stale, or duplicate schedules
- Document what each schedule does and which workstation owns it

### 2. Diagnose Daily Summary Gaps
- Determine how daily summaries are currently generated and delivered
- Identify why they're not reaching all workstations
- Check: is it a generation failure, a delivery/notification failure, or both?
- Review cross-machine sync paths (repo-sync, push/pull, shared filesystem)

### 3. Fix & Verify
- Ensure daily summaries are generated reliably
- Ensure they surface on all active workstations (ace-linux-1, dev-primary, etc.)
- Add monitoring/alerting so missed summaries are caught
- Document the schedule inventory in `docs/ops/scheduled-tasks.md`

## Output
- Schedule audit report
- Fix for daily summary cross-workstation delivery
- `docs/ops/scheduled-tasks.md` — living inventory of all scheduled work
