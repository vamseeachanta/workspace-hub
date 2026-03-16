---
name: work-queue-key-scripts
description: 'Sub-skill of work-queue: Key Scripts.'
version: 1.8.0
category: coordination
type: reference
scripts_exempt: true
---

# Key Scripts

## Key Scripts


| Script | Purpose |
|--------|---------|
| `next-id.sh` | Return next WRK-NNN id |
| `queue-status.sh` | Report counts per state |
| `archive-item.sh WRK-NNN` | Move to archive/, run completion hook |
| `close-item.sh WRK-NNN <hash>` | Close with gate verification |
| `verify-gate-evidence.py WRK-NNN` | Validate all gate evidence |
| `generate-html-review.py WRK-NNN --lifecycle` | Regenerate lifecycle HTML |
| `checkpoint.sh [WRK-NNN]` | Write checkpoint.yaml |
| `start_stage.py WRK-NNN N` | Stage entry (auto-prints resume block) |
| `exit_stage.py WRK-NNN N` | Stage exit validation |
