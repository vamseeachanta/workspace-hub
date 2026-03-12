# Feature Planning Rules

> When work is too large for one agent context window, use a Feature WRK.

## When to Create a Feature WRK

Read `config/work-queue/chunk-sizing.yaml`. If ANY limit is exceeded, create a
Feature WRK instead of a regular WRK. Never try to fit oversized work into one item.

## Feature WRK Lifecycle

1. Create Feature WRK with `type: feature` in frontmatter
2. Run full Stages 1–7 (planning + Stage 6 cross-review + Stage 7 hard gate)
3. At Stage 7 exit: run `scripts/work-queue/new-feature.sh WRK-NNN` to scaffold children
4. Feature WRK moves to status `coordinating`; children are queued as pending
5. Feature WRK closes automatically when all children reach `archived`

**Hard rule:** No child WRK enters the queue before Stage 7 is complete on the feature.

## Decomposition in the Feature Plan

The feature plan (Stage 4b artifact) MUST include a `## Decomposition` section with:
- Child title and one-sentence scope
- Which files/skills each child needs (entry_reads)
- Explicit dependencies between children (`blocked_by:`)
- Preferred agent per child (`orchestrator:`)
- Optional `wrk_ref` column — set to an existing `WRK-NNN` to adopt it under this feature instead of creating a new item

**Adopting existing WRKs:** `new-feature.sh` adds `parent: WRK-NNN` to the adopted item's frontmatter and includes it in `children:`. The adopted item continues its own lifecycle unchanged — adoption is purely a linking operation.

## Linking and Dependency Fields

| Field | Set on | Meaning |
|-------|--------|---------|
| `type: feature` | Feature WRK | Marks this as an orchestrating item |
| `children: [WRK-A, WRK-B]` | Feature WRK | All child WRKs spawned by this feature |
| `parent: WRK-NNN` | Child WRK | Points to the feature that owns it |
| `blocked_by: [WRK-A]` | Child WRK | Sequential dependency on sibling |
| `entry_reads:` | Child checkpoint | Files/skills loaded at stage start |
| `orchestrator:` | Child WRK | Preferred AI provider for execution |
