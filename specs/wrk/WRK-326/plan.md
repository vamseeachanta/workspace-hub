# WRK-326 Plan: OrcaFlex Skill Reconciliation and Enrichment

> Route C spec for `.claude/work-queue/pending/WRK-326.md`

## Problem
Skill metadata diverged between canonical and local pointers, and some skills lacked examples-derived capability declarations.

## Implementation Plan
1. Audit four target skills and compare local pointers vs canonical source paths.
2. Reconcile diverged skill pointers to canonical `engineering/marine-offshore` locations.
3. Add examples-derived capability/requires/see-also metadata where missing.
4. Add `EXAMPLES.md` model map for rapid model-to-skill routing.
5. Confirm skill files remain within style constraints.

## Deliverables
- Canonicalized skill pointer files in `digitalmodel/.claude/skills/`
- Updated canonical skill markdowns in `.claude/skills/engineering/marine-offshore/`
- `EXAMPLES.md` for `orcaflex-modeling`

## Validation
- Pointer files resolve to canonical paths.
- Capability arrays populated as required.

## Cross-Review Log
| Iter | Date | Reviewer | Verdict | Findings | Fixed |
|------|------|----------|---------|----------|-------|
| P1 | 2026-02-24 | Claude | MINOR | Diverged modeling/generator pointers required explicit canonical reconciliation. | yes |
| P2 | 2026-02-26 | Codex | APPROVE | Pointer reconciliation and examples map completed. | n/a |
| P3 | 2026-02-26 | Gemini | MINOR | Independent CLI review deferred (local CLI timeout); updated pointers and docs are coherent. | deferred |
