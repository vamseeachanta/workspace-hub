# WRK-667 Plan — Claude Synthesis (Post Cross-Review)

## Overall Verdict: APPROVE (Codex=MINOR, Gemini=APPROVE)

Hard gate passed. Codex MINOR findings absorbed below.

## Refinements Absorbed

### C1 — quality_signals field semantics
Add explicit counting rules in template YAML comments:
- `plan_changes_after_ri`: count substantive plan edits after Stage 2 (exclude formatting)
- `artifacts_gaps_prevented`: list specific artifacts that RI surfaced before they were missed
- `cross_review_blockers_prevented`: list blocker labels resolved early via RI finding
- `confidence`: `high` iff required artifacts present + ≥1 P1 resolved + provenance complete

### C3 + G3 — Comparison example rubric (Phase 5)
Predefined rubric for pre/post WRK pairs:
- Same WRK category (harness/skills or engineering)
- Same artifact set (both have plan + execute + close evidence)
- Measure: missing-artifact rate at close, cross-review blocker count, plan edit count post-Stage-2

### C4 — resource_pack_ref normalization
`resource_pack_ref` must be a relative path under `.claude/work-queue/assets/<wrk-id>/`.
Gate checks: field exists in frontmatter AND path resolves.

### C5 + G2 — HTML confidence + placement
- confidence derived automatically (not self-reported)
- RI summary placed as prominent callout near top of lifecycle HTML (above stage chips)
- Degrades gracefully when evidence absent (shows "RI evidence: absent — legacy WRK")

## Deferred (C2, G1)
- C2: skills.core_used ≥3 gate rule — pre-existing from WRK-655, out of scope
- G1: review_cycles_saved field — captured as P3 enhancement
