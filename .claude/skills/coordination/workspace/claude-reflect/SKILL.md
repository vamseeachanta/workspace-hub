---
name: claude-reflect
description: Periodic cross-repo reflection analyzing 30 days of git history, extracting
  patterns via RAGS loop, and auto-creating skills
version: 2.0.0
category: coordination
type: skill
trigger: scheduled
auto_execute: true
cron: 0 5 * * *
capabilities:
- multi_repo_git_analysis
- pattern_extraction
- pattern_scoring
- trend_analysis
- skill_auto_creation
- skill_enhancement
- weekly_reports
- cross_repo_sync
- progress_tracking
tools:
- Read
- Write
- Edit
- Bash
- Grep
- Glob
- Task
related_skills:
- skill-learner
- repo-sync
- skill-creator
- knowledge-manager
- improve
scripts:
- analyze-history.sh
- extract-patterns.sh
- analyze-trends.sh
- generate-report.sh
- create-skills.sh
- daily-reflect.sh
requires: []
see_also:
- claude-reflect-automated-execution
- claude-reflect-distinction-from-similar-skills
- claude-reflect-1-reflect-collect-git-history
- claude-reflect-state-management
- claude-reflect-pattern-output-format
- claude-reflect-with-skill-learner
- claude-reflect-weekly-reflection
- claude-reflect-metrics-success-criteria
- claude-reflect-script-details
tags: []
---

# Claude Reflect

## Quick Start

```bash
# Run full RAGS loop manually
/reflect

# Quick 7-day reflection
/reflect --days 7

# Preview patterns without creating skills
DRY_RUN=true /reflect

# Force weekly report generation
WEEKLY_REPORT=true /reflect
```

## When to Use

- **Automated**: Runs daily via cron - no manual intervention needed
- **Manual**: Run `/reflect` to trigger immediate analysis
- Before planning new features to identify reusable patterns
- After major releases to capture learnings

## Prerequisites

- Git access to all workspace-hub submodules
- `~/.claude/state/` directory for state persistence
- `~/.claude/memory/` directory for global patterns

## Overview

This skill analyzes git history across all 26+ workspace-hub submodules to extract development patterns and automatically enhance or create skills based on findings.

## References

- [Skill Learner](../skill-learner/SKILL.md) - Post-commit pattern extraction
- [Repo Sync](../repo-sync/SKILL.md) - Multi-repo operations
- [Skill Creator](../../builders/skill-creator/SKILL.md) - Skill generation

---

## Version History

- **2.0.0** (2026-01-21): Full RAGS loop implementation
  - Added pattern extraction engine (`extract-patterns.sh`)
  - Added cross-daily trend analysis (`analyze-trends.sh`)
  - Added actionable reports generator (`generate-report.sh`)
  - Added auto-skill creation module (`create-skills.sh`)
  - Updated `daily-reflect.sh` to orchestrate all phases
  - Weekly reports auto-generated on Sundays
- **1.0.0** (2026-01-21): Initial release with basic RAGS spec

## Sub-Skills

- [Quick Reference](quick-reference/SKILL.md)
- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Automated Execution](automated-execution/SKILL.md)
- [Distinction from Similar Skills](distinction-from-similar-skills/SKILL.md)
- [1. REFLECT - Collect Git History (+3)](1-reflect-collect-git-history/SKILL.md)
- [State Management](state-management/SKILL.md)
- [Pattern Output Format](pattern-output-format/SKILL.md)
- [With skill-learner (+3)](with-skill-learner/SKILL.md)
- [Weekly Reflection (+2)](weekly-reflection/SKILL.md)
- [Metrics & Success Criteria](metrics-success-criteria/SKILL.md)
- [Script Details (+1)](script-details/SKILL.md)
