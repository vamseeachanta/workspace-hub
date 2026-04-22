# Approval-stage adversarial cross-review summary — 2026-04-22

Reviewed issue plans:
- #2311 — `docs/plans/2026-04-17-issue-2311-stage-transition-stale-reference-cleanup.md`
- #2312 — `docs/plans/2026-04-17-issue-2312-lifecycle-script-authority-cleanup.md`
- #2332 — `docs/plans/2026-04-22-issue-2332-provider-audit-python3-runtime-cleanup.md`
- #2333 — `docs/plans/2026-04-22-issue-2333-provider-audit-drift-classification-expansion.md`

Providers used for cross-review:
- Codex
- Gemini

## Verdict table

| Issue | Codex | Gemini | Overall |
|---|---|---|---|
| #2311 | MAJOR | MAJOR | NOT approval-ready |
| #2312 | MAJOR | MAJOR | NOT approval-ready |
| #2332 | MAJOR | MAJOR | NOT approval-ready |
| #2333 | MAJOR | MAJOR | NOT approval-ready |

Rule applied: a single MAJOR blocks approval-stage readiness. All four plans remain blocked.

## Shared blocker themes

### #2311
- classifier / scan-universe for “current instructional surfaces” is still undefined
- plan still defers key decisions to implementation time
- file-change set includes speculative or scope-creep items
- existing plan text already admits prior review failure without incorporating the required rewrite

### #2312
- canonical replacement contract for close/archive evidence is still unresolved
- current/historical/fixture boundary is underspecified
- some proposed file edits are speculative and not tied to verified stale hits
- tests rely on undefined curated lists rather than fixed protected surfaces

### #2332
- plan still lacks named hotspot files and a concrete allowlist/exception policy
- provider-audit evidence cited in the draft needs tightening against committed/attested repo state before approval
- Hermes-first prioritization was challenged as insufficiently grounded in the attested artifact set
- scope boundary against #48 is not yet explicit enough

### #2333
- bucket taxonomy is still partly open, especially generated-site vs broader non-repo class
- anomaly/event-time separation logic is not defined concretely enough for TDD
- some file targets are speculative (`if needed` / index-only maintenance)
- acceptance criteria promise deterministic rules that the plan has not fully specified yet

## Review artifacts
- `scripts/review/results/2026-04-22-plan-2311-codex.md`
- `scripts/review/results/2026-04-22-plan-2311-gemini.md`
- `scripts/review/results/2026-04-22-plan-2312-codex.md`
- `scripts/review/results/2026-04-22-plan-2312-gemini.md`
- `scripts/review/results/2026-04-22-plan-2332-codex.md`
- `scripts/review/results/2026-04-22-plan-2332-gemini.md`
- `scripts/review/results/2026-04-22-plan-2333-codex.md`
- `scripts/review/results/2026-04-22-plan-2333-gemini.md`

## Next recommended action
Do not move any of these plans to approval.
Instead:
1. redraft each blocked plan against the concrete MAJOR findings,
2. refresh prompt files from the latest plan text,
3. rerun adversarial cross-review,
4. only then consider `status:plan-review` / approval-stage surfacing.
