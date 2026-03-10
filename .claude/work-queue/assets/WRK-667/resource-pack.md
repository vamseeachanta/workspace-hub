# Resource Pack — WRK-667

## Problem Context
Resource Intelligence stage (Stage 2) exists since WRK-655 but has no measurable quality
metrics. WRK-624 gap review flagged `resource_intelligence: revise` — the skill needs to
demonstrably reduce plan rework and missing-artifact rates.

## Relevant Documents/Data
- `coordination/workspace/work-queue` SKILL.md — stage lifecycle, 20-stage contracts
- `workspace-hub/resource-intelligence` SKILL.md v1.1.0 — stage 2/16, templates, scripts
- `workspace-hub/work-queue-workflow` SKILL.md — full lifecycle and gate policy
- `scripts/work-queue/verify-gate-evidence.py` — gate checks including RI gate
- `scripts/work-queue/generate-html-review.py` — lifecycle HTML generator (1968 lines)
- `.claude/skills/workspace-hub/resource-intelligence/scripts/validate-resource-pack.sh`
- `.claude/skills/workspace-hub/resource-intelligence/scripts/init-resource-pack.sh`
- `.claude/work-queue/archive/2026-03/WRK-624.md` — parent WRK + gap review
- `.claude/work-queue/done/WRK-655.md` — RI skill creation WRK

## Constraints
- validate-resource-pack.sh changes must be backward-compatible (warn-only when RI evidence absent)
- generate-html-review.py is 1968 lines — keep Phase 4 change focused; no full refactor
- quality_signals block is not gate-checked today (introduce warn-only first)
- comparison examples must use real WRKs from archive (not synthetic)

## Assumptions
- WRK-655 is archived and the RI skill is stable enough to extend
- WRK-667 target: workspace-hub (single repo, Route B)
- Comparison WRK pairs can be reconstructed from archive evidence (some fields estimated)

## Open Questions
- When should quality_signals become gate-checked? (deferred, see future-work.yaml)
- Should ri-comparison-examples.md be updated automatically? (deferred)

## Domain Notes
Before/after candidate WRKs (same category=harness, same artifact set):
- WRK-655 (RI skill build), WRK-624 (governance review), WRK-1028 (stage-isolation)

## Source Paths
- `.claude/skills/workspace-hub/resource-intelligence/` — skill scripts, templates, tests
- `scripts/work-queue/generate-html-review.py` — Phase 4 target
- `.claude/work-queue/assets/WRK-667/` — evidence directory for this WRK
