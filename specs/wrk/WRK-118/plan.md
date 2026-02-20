---
title: "WRK-118 AI Agent Utilization Strategy — Plan"
wrk_id: WRK-118
status: approved
plan_approved: true
plan_reviewed: false
created: "2026-02-18"
---

# WRK-118 Plan: AI Agent Utilization Strategy

## Phase 1 — Audit & Role Matrix *(Gemini)*
- Scan `.claude/work-queue/archive/` for actual provider usage patterns by task type
- Derive empirical role matrix from real outcomes, not assumptions
- Extend `behavior-contract.yaml` strengths block with task-type granularity
  (feature | bugfix | refactor | test-writing | research | docs → primary + rationale)

## Phase 2 — task_agents Delegation Templates *(Claude)*
- Author `docs/modules/ai/agent-delegation-templates.md`
- Standard `task_agents:` maps for each task type × route (A/B/C):
  - feature/A → codex
  - feature/B → claude plan + codex impl
  - feature/C → claude arch + codex impl + gemini docs
  - bugfix → codex diagnose+fix + claude review
  - refactor → codex + gemini summary
  - test-writing → codex primary + claude review
  - research/docs → gemini primary + claude synthesize
- Referenced by WRK-199 as the decision table it automates

## Phase 3 — Wire task_classifier into /work run *(Codex)*
- Add routing recommendation step to `work.sh` pre-plan gate
- Call `scripts/coordination/routing/lib/task_classifier.sh` → `provider_recommender.sh`
- Auto-populate `task_agents:` in WRK frontmatter from recommendation
- Display rationale with quota context

## Phase 4 — Provider Assessment Scaffolding *(Claude)*
- Create `.claude/state/provider-assessments/` + YAML template
- Wire post-cross-review step: write assessment entry per verdict
- Add quarterly report trigger to `work.sh`

## Phase 5 — Validate on 3 Items *(Claude)*
- Apply routing to WRK-199, WRK-184, WRK-186
- Confirm task_agents populated correctly, rationale sensible
- Adjust templates if recommendations drift

## Review Log

| Iter | Date | Reviewer | Verdict | Findings | Fixed |
|------|------|----------|---------|----------|-------|
| Plan | pending | Codex | — | — | — |
| Plan | pending | Gemini | — | — | — |
