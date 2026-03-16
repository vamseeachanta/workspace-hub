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
| `/work run` | Process — run next stage (auto-loads checkpoint.yaml) |
| `/work list` | Status — read INDEX.md |
| `/work list --by-category` | Category-grouped view (HIGH first) |
| `/work list --category <name> [--subcategory <sub>]` | Narrow by category |
| `/work status WRK-NNN` | Detail for one item |
| `/work archive WRK-NNN` | Manually archive |
| `/work report` | Queue health summary |

Smart routing: action verbs (run/go/start) → Process; descriptive content → Capture.
