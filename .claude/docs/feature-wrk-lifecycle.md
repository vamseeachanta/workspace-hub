# Feature WRK Lifecycle

> Referenced from: `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md`

## Overview

A Feature WRK (`type: feature`) orchestrates multiple child WRKs that together deliver
a large piece of work too big for a single agent context window.

## Lifecycle Steps

1. **Create** — capture WRK with `type: feature` in frontmatter
2. **Stages 1–7** — standard planning cycle including cross-review and user approval
3. **Stage 7 exit** — produce `evidence/feature-decomposition.yaml` with Decomposition table
4. **Stage 9b** — run `bash scripts/work-queue/new-feature.sh WRK-NNN`:
   - Allocates child WRK IDs, writes child files to pending/
   - Writes `children: [WRK-A, WRK-B, ...]` inside feature WRK frontmatter
   - Sets `status: coordinating` on the feature WRK
5. **Coordinating** — feature WRK stays `status: coordinating` in `working/` while children execute
6. **Children complete** — each child runs its own 20-stage lifecycle and reaches `archived`
7. **All children archived** — `feature-close-check.sh WRK-NNN` exits 0
8. **Close** — `close-item.sh WRK-NNN` enforces feature-close-check.sh gate before proceeding
9. **Archive** — feature WRK archived like any other WRK

## Key Rule

`archived` is the required terminal state for all children before the feature WRK can close.
`done` is not sufficient — children must reach `archived`.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/work-queue/new-feature.sh WRK-NNN` | Scaffold children; set status:coordinating |
| `scripts/work-queue/feature-status.sh WRK-NNN` | Print "N/M archived (X%)" |
| `scripts/work-queue/feature-close-check.sh WRK-NNN` | Exit 0 iff all children archived |
| `scripts/work-queue/dep_graph.py --feature WRK-NNN` | Print ASCII dependency tree |

## Status Values

| Status | Meaning |
|--------|---------|
| `working` | Active execution (pre-scaffolding) |
| `coordinating` | Children scaffolded; waiting for all to archive |
| `done` / `archived` | Feature complete |

## Dependency Fields

| Field | Set on | Meaning |
|-------|--------|---------|
| `type: feature` | Feature WRK | Marks orchestrating item |
| `children: [WRK-A, WRK-B]` | Feature WRK | All child WRKs |
| `parent: WRK-NNN` | Child WRK | Points to owning feature |
| `blocked_by: [WRK-A]` | Child WRK | Sequential dependency |
