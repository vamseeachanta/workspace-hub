---
name: work-queue-command-interface
description: 'Sub-skill of work-queue: Command Interface.'
version: 1.8.0
category: coordination
type: reference
scripts_exempt: true
---

# Command Interface

## Command Interface


| Command | Action |
|---------|--------|
| `/work add <desc>` | Capture — log work items |
| `/work run [WRK-NNN]` | Process — run `bash scripts/work-queue/dispatch-run.sh [WRK-NNN]` and follow its output |
| `/work list` | Status — read INDEX.md |
| `/work list --by-category` | Category-grouped view (HIGH first) |
| `/work list --category <name> [--subcategory <sub>]` | Narrow by category |
| `/work find <keyword> [--archived] [--gh]` | Search items by keyword (local; `--gh` adds GitHub Issues) |
| `/work status WRK-NNN` | Detail for one item |
| `/work archive WRK-NNN` | Manually archive |
| `/work report` | Queue health summary |

Smart routing: action verbs (run/go/start) → Process; descriptive content → Capture.

## `/work run` Dispatch

When processing `/work run [WRK-NNN]`, the agent MUST:
1. Run `bash scripts/work-queue/dispatch-run.sh [WRK-NNN]`
2. Follow the dispatch output exactly (run the printed command)
3. Do NOT browse sub-skills to determine the next stage — dispatch-run.sh handles routing
