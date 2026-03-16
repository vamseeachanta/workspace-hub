---
name: work-queue-queue-directory-structure
description: 'Sub-skill of work-queue: Queue Directory Structure.'
version: 1.8.0
category: coordination
type: reference
scripts_exempt: true
---

# Queue Directory Structure

## Queue Directory Structure


```
.claude/work-queue/
  pending/        # awaiting processing
  working/        # active (max 1-2)
  blocked/        # awaiting dependencies
  archive/YYYY-MM/
  assets/WRK-NNN/ # evidence, checkpoint, HTML
  state.yaml
```

INDEX.md is source of truth for listing. Regenerate after any mutation:
```bash
uv run --no-project python .claude/work-queue/scripts/generate-index.py
```
