# Session Handoff — Machine-Equality Family (#2801 + children)

**Date:** 2026-05-28  •  **Origin:** "add a gh issue to assess machine equality" → grew into a family.

## TL;DR state
| Issue | What | State | Branch |
|-------|------|-------|--------|
| [#2801](https://github.com/vamseeachanta/workspace-hub/issues/2801) | Machine-equality matrix (parent) | **merged** (PR #2810, `7cc51cc2f`); OPEN pending owner verify-label + close | feat/2801-equality (merged, deleted) |
| [#2851](https://github.com/vamseeachanta/workspace-hub/issues/2851) | Freshness guard (stale-checkout defense) | **plan-approved + T2-reviewed; impl NOT started** (marker was never created) | feat/2851-freshness-guard (plan+reviews pushed) |
| [#2814](https://github.com/vamseeachanta/workspace-hub/issues/2814) | Fix stale context.md (siblings vs nested) | open, needs-plan | — |
| [#2815](https://github.com/vamseeachanta/workspace-hub/issues/2815) | Win Task Scheduler single-source + live-validate (ties #2229) | open, needs-plan | — |
| [#2816](https://github.com/vamseeachanta/workspace-hub/issues/2816) | collect-equality.ps1 Windows compute + restore RAM floor | open, needs-plan | — |
| [#2817](https://github.com/vamseeachanta/workspace-hub/issues/2817) | **RE-SCOPED**: plan-approval gate → label-actor authority, retire forgeable marker | plan-review; **5 MAJOR open** (Codex); Gemini pending | feat/2817-label-authority (authoritative); feat/2817-approve-helper (SUPERSEDED) |

## What was accomplished
- **#2801 built end-to-end**: collector + matrix verdict engine, declared-baseline conformance (cold dims) + equality (uniform dims), sandboxed behavior probes, commit-on-change. 39 TDD tests. Two-stage T3 review (plan + code; Claude/Codex/Gemini). Merged.
- **Cross-machine population: 2/4** (dev-primary + dev-secondary). Matrix regenerated.
- **Investigation win**: the b3/skills "divergences" were proven FALSE — dev-primary report came from a tree 85 commits behind main (stale-checkout contamination). Corrected on #2801; root-caused into #2851.
- **#2817 re-scope**: Codex found the marker-helper premise was itself a self-approval primitive. User chose to re-scope to **server-authoritative + local-advisory label-actor authority** (mirrors #2798 completeness gate). Plan drafted + Claude r1 (fixed) + Codex delta (5 MAJOR = revision agenda). Premature plan-approved label rolled back to plan-review.

## Blockers (all need the USER)
1. **#2851 marker** — `mkdir -p .planning/plan-approved && echo "Approved by: vamsee 2026-05-28 (#2851)" > .planning/plan-approved/2851.md` → then I implement the approved freshness guard.
2. **#2801 close** — owner applies `status:completeness-verified` (record already stamped, pct 95) then `gh issue close 2801`. Plus Windows machines self-report (`collect-equality.sh` + push on licensed-win-1/2) → regen matrix at 4/4.
3. **#2817** — resume as dedicated security work; revision agenda = the 5 Codex MAJORs (fail-closed, anti-substitution linkage, approval-freshness binding, PAT/owner hardening, migration) + Gemini review.

## Recommended resume order
1. **#2851** (cheapest concrete win; already approved+reviewed) — unblocks trustworthy cross-machine comparison.
2. **#2814** (T1 doc fix) + Windows self-report + close #2801 (the 2/4→4/4 + verify).
3. **#2817** security redesign (dedicated; agenda written).

## Review artifacts (on feat branches)
scripts/review/results/2026-05-28-plan-2851-{claude,codex}.md ; 2026-05-28-plan-2817-{claude,codex}.md (superseded helper) ; 2026-05-28-plan-2817v2-{claude,codex}.md (re-scope) ; 2026-05-26-{plan,code}-2801-*.md (#2801, on main).

## Recurring hazard noted
The 2-step approval (label + marker) dropped the marker 3× (#2801 ×2, #2851). #2817 (re-scoped) fixes the root cause. Until then: apply label AND create marker together, or just commit the marker.
