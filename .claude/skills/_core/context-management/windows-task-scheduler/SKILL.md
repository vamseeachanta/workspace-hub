---
name: core-context-management-windows-task-scheduler
description: 'Sub-skill of core-context-management: Windows Task Scheduler (+2).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# Windows Task Scheduler (+2)

## Windows Task Scheduler


Task: `ContextManagementDaily`
Schedule: Daily at 6:00 AM
Action: `scripts/context/daily_context_check.sh`
Output: `.claude/reports/context-health-YYYY-MM-DD.md`

## Daily Check Includes


The `daily_context_check.sh` script runs:
1. `validate_context.sh` - Size validation
2. `analyze_patterns.sh` - Pattern analysis (7 days)
3. `improve_context.sh --dry-run` - Improvement suggestions
4. `optimize-mcp-context.sh --dry-run` - MCP optimization check
5. Repository status table generation

## Setup Command


```powershell
# Run as Administrator
schtasks /create /tn "ContextManagementDaily" /tr "D:\workspace-hub\scripts\context\daily_context_check.sh" /sc daily /st 06:00
```

---
