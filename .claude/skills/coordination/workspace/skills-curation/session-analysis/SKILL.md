---
name: skills-curation-session-analysis
description: 'Sub-skill of skills-curation: session-analysis (+3).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# session-analysis (+3)

## session-analysis


`session-analysis.sh` populates `skill-candidates.md` at 3AM. The curation skill reads this file in Phase 1. The two skills share state through the candidates file — no direct coupling.


## skill-learner


`skill-learner` fires post-commit and may also create/enhance skills. The health check in Phase 5 verifies skill-learner is active. The curation skill does not duplicate skill-learner's commit-analysis logic — they operate at different granularities (per-commit vs periodic batch).


## agentic-horizon


`agentic-horizon` reassesses WRK item dispositions weekly. The curation skill reads WRK items to compute graph demand scores but does not modify them. Deep gap WRK items created by the curation skill will be picked up by agentic-horizon on its next run.


## work-queue


WRK items spun off for deep gaps follow the standard work-queue format. The curation skill assigns `blocked_by: []` and `plan_approved: false` to ensure they surface for user review before execution.

---
