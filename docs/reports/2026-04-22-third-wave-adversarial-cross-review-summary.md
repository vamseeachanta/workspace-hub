# Third-wave adversarial cross-review summary — 2026-04-22

## Reviewed plans
- #2311 — `docs/plans/2026-04-17-issue-2311-stage-transition-stale-reference-cleanup.md`
- #2312 — `docs/plans/2026-04-17-issue-2312-lifecycle-script-authority-cleanup.md`
- #2332 — `docs/plans/2026-04-22-issue-2332-provider-audit-python3-runtime-cleanup.md`
- #2333 — `docs/plans/2026-04-22-issue-2333-provider-audit-drift-classification-expansion.md`

## Verdict matrix

| Issue | Codex | Gemini | Status |
|---|---|---|---|
| #2311 | MAJOR | MAJOR | blocked |
| #2312 | MAJOR | MAJOR | blocked |
| #2332 | MAJOR | APPROVE | blocked |
| #2333 | MAJOR | MAJOR | blocked |

Single-MAJOR rule still applies, so none are approval-ready.

## Main blocker classes after the third wave

### #2311
- review-evidence governance drift remains in the plan text: one cited review artifact is treated as substantive evidence even though the reviewer called it empty/insufficient
- taxonomy still appears inconsistent across sections to Codex
- scope-expansion wording still looks partly implementation-time rather than fully locked at plan time

### #2312
- still carries unsupported evidence/content claims according to Codex
- Gemini flagged governance drift from citing empty/hallucinatory review evidence
- acceptance criteria/test command surface still needs tightening and mapping to real targets only

### #2332
- strongest progress of the four: Gemini APPROVE
- remaining blocker is Codex only
- Codex still sees unresolved mechanics around:
  - exact prior-audit delta computation behavior
  - exact launcher runtime choice
  - stale/misleading review-state evidence in the plan text

### #2333
- still blocked from both providers
- Codex says unsupported evidence claims, gating/status contradiction, and weak test contract remain
- Gemini says the plan still over-rotates toward generated-site filtering instead of staying centered on the issue’s transient/scratch-path mandate

## Net conclusion
The extra tightening wave improved #2332 the most, but did not get any plan across the approval threshold.

## Best next move
If continuing efficiently, prioritize:
1. `#2332` first — it is one-provider-away from approval readiness.
2. Then `#2311` / `#2312` governance-evidence cleanup.
3. Re-scope `#2333` more aggressively around transient/worktree/scratch-path handling before trying again.
