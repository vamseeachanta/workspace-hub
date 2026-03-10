# Resource Pack — WRK-667

## Core Skills
- `coordination/workspace/work-queue` — SKILL.md: stage lifecycle, 20-stage contracts
- `workspace-hub/resource-intelligence` — SKILL.md v1.1.0: stage 2/16, templates, scripts
- `workspace-hub/work-queue-workflow` — full lifecycle and gate policy

## Key Scripts
- `scripts/work-queue/verify-gate-evidence.py` — gate checks including RI gate
- `scripts/work-queue/generate-html-review.py` — lifecycle HTML generator
- `.claude/skills/workspace-hub/resource-intelligence/scripts/validate-resource-pack.sh`
- `.claude/skills/workspace-hub/resource-intelligence/scripts/init-resource-pack.sh`

## Reference Artifacts
- `.claude/work-queue/archive/2026-03/WRK-624.md` — parent WRK + gap review
- `.claude/work-queue/archive/2026-03/WRK-624/gap-review-user.json` — user decisions
- `.claude/work-queue/done/WRK-655.md` — RI skill creation WRK

## Before/After Candidate WRKs
For 3 comparison examples, select from:
- Pre-RI WRKs: WRK-617, WRK-610, WRK-600 (no RI evidence)
- Post-RI WRKs: WRK-690, WRK-1003, WRK-1028 (have RI evidence)
