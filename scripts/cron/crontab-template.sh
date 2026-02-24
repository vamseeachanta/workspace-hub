#!/usr/bin/env bash
# crontab-template.sh — Reference crontab entries per machine role.
#
# PURPOSE: This file is the canonical record of all standard cron jobs.
#          Do NOT run it directly.  To install, use:
#
#   bash scripts/cron/setup-cron.sh               # auto-detects machine role
#   bash scripts/cron/setup-cron.sh --dry-run     # preview without changes
#
# MACHINE ROLES:
#   full              ace-linux-1  — nightly pipeline + all maintenance
#   contribute        ace-linux-2  — repo sync only
#   contribute-minimal ACMA-ANSYS05 / acma-ws014  — Windows Task Scheduler
#
# FORMAT:  # ROLE: <role>
#          <cron-schedule>  <command>
# ─────────────────────────────────────────────────────────────────────────────

# ── ROLE: full (ace-linux-1) ──────────────────────────────────────────────────

# Nightly comprehensive learning pipeline (10 phases); runs at 02:00 to avoid
# overlap with session work.  Log rotated by logrotate (see /etc/logrotate.d/).
# CRON: 0  2  * * *  cd $WORKSPACE_HUB && bash scripts/cron/comprehensive-learning-nightly.sh >> $WORKSPACE_HUB/.claude/state/learning-reports/cron.log 2>&1

# Nightly session analysis; runs at 03:00 after learning pipeline completes.
# CRON: 0  3  * * *  cd $WORKSPACE_HUB && bash scripts/cron/session-analysis-nightly.sh >> $WORKSPACE_HUB/.claude/state/learning-reports/cron.log 2>&1

# Weekly model-ID refresh (Sunday 03:30); updates config/agents/model-registry.yaml.
# CRON: 30 3  * * 0  cd $WORKSPACE_HUB && bash scripts/cron/update-model-ids.sh >> $WORKSPACE_HUB/.claude/state/learning-reports/cron.log 2>&1

# Weekly skills curation (Monday 04:00); archives stale skills, validates frontmatter.
# CRON: 0  4  * * 1  cd $WORKSPACE_HUB && bash scripts/cron/skills-curation.sh >> $WORKSPACE_HUB/.claude/state/learning-reports/cron.log 2>&1

# Repository sync every 4 hours; pulls from remotes, pushes derived state.
# CRON: 0  */4 * * * cd $WORKSPACE_HUB && bash scripts/repository-sync-auto >> $WORKSPACE_HUB/.claude/state/learning-reports/cron.log 2>&1

# ── ROLE: contribute (ace-linux-2) ───────────────────────────────────────────

# Repository sync every 4 hours; log to /tmp (no persistent .claude/state here).
# CRON: 0  */4 * * * cd $WORKSPACE_HUB && bash scripts/repository-sync-auto >> /tmp/workspace-hub-cron.log 2>&1

# ── ROLE: contribute-minimal (Windows / ACMA-ANSYS05, acma-ws014) ────────────
# Windows does not support cron.  Use Task Scheduler instead:
#
#   Task 1 — Repository Sync (every 4 hours)
#     Program:   bash.exe  (Git Bash — C:\Program Files\Git\bin\bash.exe)
#     Arguments: -c "cd /path/to/workspace-hub && bash scripts/repository-sync-auto"
#     Trigger:   Every 4 hours
#
#   Task 2 — Session-end state commit (daily 03:00)
#     Program:   bash.exe
#     Arguments: -c "cd /path/to/workspace-hub && git add .claude/state/candidates/ .claude/state/corrections/ && git diff --staged --quiet || git commit -m 'chore: session learnings from %COMPUTERNAME%' && git push"
#     Trigger:   Daily 03:00
#
# For WSL, replace paths with WSL mount points (/mnt/d/...).
# For cross-network sync, ensure Tailscale is running and SSH key is authorised
# on ace-linux-1 (see .claude/docs/new-machine-setup.md § SSH Setup).
