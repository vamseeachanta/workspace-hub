---
name: today
description: Interactive daily productivity review with guided priority setting. Supports
  morning planning, midday check-ins, and end-of-day wrap-ups. Use for daily ritual
  or cron automation.
version: 1.1.0
category: business
last_updated: 2026-01-21
related_skills:
- context-management
capabilities: []
requires: []
see_also:
- today-morning-flow
- today-daily-review-process
- today-completed-yesterday
- today-summary
- today-priorities
- today-notes
- today-data-sources-configuration
- today-installation
- today-morning-ritual
- today-output-locations
tags: []
scripts_exempt: true
---

# Today

## Overview

A daily ritual skill that reviews your workspace activity, summarizes progress, identifies blockers, and suggests focus items for sustained productivity. Features **interactive review mode** that guides you through priority setting and progress tracking.

## Quick Start

```bash
# Interactive review (auto-detects morning/midday/evening)
/today

# Specific modes
/today morning    # Full review + set priorities
/today midday     # Quick progress check
/today --eod      # End-of-day wrap-up

# Weekly review
/today --week

# Cron automation (runs at 6 AM)
0 6 * * * /path/to/workspace-hub/scripts/productivity/daily_today.sh
```

## When to Use

- Start of workday ritual
- After returning from break/vacation
- Weekly planning sessions
- Automated daily reports via cron
- Before standup meetings

## Related Skills

- [context-management](../../context-management/SKILL.md) - Manage context efficiently
- [planning](../../development/planning/SKILL.md) - Detailed planning methodology

---

## Version History

- **1.1.0** (2026-01-21): Add interactive review mode with morning/midday/evening flows
- **1.0.0** (2026-01-21): Initial release with daily review, cron support, long-term suggestions

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
- [Metrics](metrics/SKILL.md)

## Sub-Skills

- [Morning Flow (+2)](morning-flow/SKILL.md)
- [Daily Review Process](daily-review-process/SKILL.md)
- [Completed Yesterday (+3)](completed-yesterday/SKILL.md)
- [Summary](summary/SKILL.md)
- [Priorities](priorities/SKILL.md)
- [Notes](notes/SKILL.md)
- [Data Sources Configuration](data-sources-configuration/SKILL.md)
- [Installation (+1)](installation/SKILL.md)
- [Morning Ritual (+9)](morning-ritual/SKILL.md)
- [Output Locations](output-locations/SKILL.md)
