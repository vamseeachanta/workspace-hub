---
name: work-queue-feature-layer-epic-level-work
description: 'Sub-skill of work-queue: Feature Layer (Epic-level work).'
version: 1.8.0
category: coordination
type: reference
scripts_exempt: true
---

# Feature Layer (Epic-level work)

## Feature Layer (Epic-level work)


When a work item exceeds chunk-sizing limits (`config/work-queue/chunk-sizing.yaml`),
create a **Feature WRK** instead of a regular WRK:

```bash
# manually: copy config/work-queue/feature-template.md
```

Feature WRK lifecycle:
- Full Stage 1–7 planning (Stage 6 cross-review + Stage 7 hard gate mandatory)
- At Stage 7 exit → `new-feature.sh WRK-NNN` spawns child WRKs
- Feature WRK status becomes `coordinating`; children queue as `pending`
- Feature closes when all children are `archived`

Key frontmatter fields:
- `type: feature` — marks this as an orchestrating item
- `children: [WRK-A, WRK-B]` — populated by new-feature.sh
- Child WRKs carry `parent: WRK-NNN` and optional `blocked_by: [sibling]`

Feature status: `scripts/work-queue/feature-status.sh WRK-NNN`
