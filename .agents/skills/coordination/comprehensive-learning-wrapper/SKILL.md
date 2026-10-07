---
name: comprehensive-learning-wrapper
description: Discoverable skill wrapper for the comprehensive-learning nightly pipeline. Provides session-invocable commands to trigger learning extraction, check pipeline status, and review recent learning reports. Bridges the cron-based pipeline to the skills tree.
version: 1.0.0
category: coordination
type: skill
trigger: manual
invoke: learn-extended
auto_execute: false
tools:
  - Bash
  - Read
  - Grep
  - Glob
tags:
  - learning
  - pipeline
  - cron
  - skill-discovery
  - session-learning
related_skills:
  - comprehensive-learning
  - session-corpus-audit
  - extract-learnings-to-issues
issue_ref: "#2057"
---

# Comprehensive Learning — Skill Wrapper

Discoverable entry point for the comprehensive-learning nightly pipeline. The pipeline
itself runs via cron (`scripts/cron/comprehensive-learning-nightly.sh`) and is invisible
to skill discovery without this wrapper.

## Why This Exists

The learning extraction pipeline is the largest automated process in the ecosystem:
- 10+ phases running nightly at 22:00 on dev-primary
- Processes session signals, drift detection, knowledge harvesting
- Produces learning reports, WRK items, memory updates

But it was invisible to `/skills` discovery and could not be invoked on-demand. This
wrapper makes it accessible via `/learn-extended` or similar commands.

## Canonical Pipeline

The full pipeline lives at:
- **Skill definition**: `.claude/skills/workspace-hub/comprehensive-learning/`
- **Cron wrapper**: `scripts/cron/comprehensive-learning-nightly.sh`
- **Pipeline script**: `scripts/learning/comprehensive-learning.sh`
- **Phase specs**: `.claude/skills/workspace-hub/comprehensive-learning/references/pipeline-detail.md`

## On-Demand Commands

### Check Pipeline Health

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
REPORT_DIR="$REPO_ROOT/.claude/state/learning-reports"
CRON_LOG="$REPORT_DIR/cron.log"

echo "=== Pipeline health ==="
# Last run time
if [[ -f "$CRON_LOG" ]]; then
  LAST_RUN=$(tail -1 "$CRON_LOG" 2>/dev/null)
  echo "  Last cron log entry: $LAST_RUN"
else
  echo "  WARNING: No cron log found at $CRON_LOG"
fi

# Most recent report
LATEST_REPORT=$(ls -t "$REPORT_DIR"/*.md 2>/dev/null | head -1)
if [[ -n "$LATEST_REPORT" ]]; then
  echo "  Latest report: $(basename "$LATEST_REPORT")"
  echo "  Report age: $(( ($(date +%s) - $(stat -c %Y "$LATEST_REPORT" 2>/dev/null || echo 0)) / 3600 )) hours"
else
  echo "  WARNING: No learning reports found"
fi
```

### Review Latest Report

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
REPORT_DIR="$REPO_ROOT/.claude/state/learning-reports"
LATEST=$(ls -t "$REPORT_DIR"/*.md 2>/dev/null | head -1)
if [[ -n "$LATEST" ]]; then
  head -80 "$LATEST"
else
  echo "No learning reports available"
fi
```

### List Recent Learning Candidates

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
CANDIDATES_DIR="$REPO_ROOT/.claude/state/candidates"

echo "=== Recent learning candidates ==="
if [[ -d "$CANDIDATES_DIR" ]]; then
  ls -lt "$CANDIDATES_DIR"/*.md 2>/dev/null | head -10
else
  echo "  No candidates directory found"
fi
```

### Manual Pipeline Trigger (use sparingly)

The pipeline is designed for nightly cron execution. Running it during an active
session violates the Iron Law documented in the comprehensive-learning skill.
Only trigger manually in exceptional cases:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
# DRY RUN: list what phases would execute
echo "Pipeline phases:"
head -30 "$REPO_ROOT/scripts/learning/comprehensive-learning.sh" 2>/dev/null || echo "Script not found"
echo ""
echo "WARNING: Running the pipeline mid-session violates the Iron Law."
echo "Use nightly cron instead. See: .claude/skills/workspace-hub/comprehensive-learning/"
```

## Scheduling Reference

The cron entry on dev-primary:
```
0 22 * * * cd /path/to/workspace-hub && bash scripts/cron/comprehensive-learning-nightly.sh >> .claude/state/learning-reports/cron.log 2>&1
```

## Iron Law Reminder

> No learning pipeline phase shall run standalone during an active work session.
> Learning is deferred to the nightly pipeline, always.

This wrapper provides read-only inspection commands that are session-safe. The
actual pipeline execution is reserved for cron.

## Related

- Primary skill: `.claude/skills/workspace-hub/comprehensive-learning/`
- Extract to issues: `.claude/skills/extract-learnings-to-issues/`
- Session corpus audit: `.claude/skills/coordination/session-corpus-audit/`
- Cron scripts: `scripts/cron/comprehensive-learning-nightly.sh`
