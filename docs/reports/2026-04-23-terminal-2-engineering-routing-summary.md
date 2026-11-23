# Terminal 2 summary — engineering routing salvage

Date: 2026-04-23
Scope: #2461, #2462
Mode: direct salvage after unattended overnight no-output runs

## What changed
- confirmed the canonical assetutilities routing/hygiene plan exists:
  - `docs/plans/2026-04-22-issue-2461-assetutilities-routing-and-source-hygiene.md`
- confirmed the canonical digitalmodel repo-wide routing plan exists:
  - `docs/plans/2026-04-22-issue-2462-digitalmodel-repo-wide-routing-surfaces.md`
- added the missing `docs/plans/README.md` index rows for #2461 and #2462 during the salvage pass

## Issue-by-issue readiness

### #2461 — assetutilities routing and source hygiene
Status: draft, weaker review coverage

Evidence:
- plan exists
- plan status explicitly says only Claude review landed cleanly; Codex/Gemini are still effectively pending / blocked in the current artifact trail

Why it matters:
- assetutilities is the highest misplacement-risk tier-1 repo in the scorecard
- fixes routing surfaces, stale structure guidance, and tracked backup-artifact pollution

Immediate blockers:
- hard dependency on #2460 contract lock
- missing non-Claude review completion

### #2462 — digitalmodel repo-wide routing surfaces
Status: best repo-specific execution candidate after #2460

Evidence:
- plan exists
- full three-provider review artifacts exist:
  - `scripts/review/results/2026-04-22-plan-2462-claude.md`
  - `scripts/review/results/2026-04-22-plan-2462-codex.md`
  - `scripts/review/results/2026-04-22-plan-2462-gemini.md`
- plan hardens the gate so work does not start until #2460 is actually textually locked

Why it matters:
- digitalmodel already has the strongest source/test structure
- a repo-wide operator map and canonical registry would unlock the biggest immediate retrieval gain across engineering work

Immediate blockers:
- #2460 contract not yet approved/locked

## Comparative ranking
1. #2462 first among repo-specific remediations
   - strongest review coverage
   - highest leverage on engineering issue routing
   - least ambiguous scope after contract lock
2. #2461 second
   - highest hygiene risk, but weaker current review coverage and more deletion/hygiene edge cases

## Remaining blockers
- both issues depend on #2460
- #2461 still needs broader adversarial review evidence to match #2462 confidence
- unattended overnight Claude runs produced no direct output; this summary is the salvage artifact

## Suggested morning dispatch order
1. finish #2460 contract maturity
2. launch #2462 planning closeout / approval route next
3. follow with #2461 once the contract naming/host rules are fixed and review coverage is improved

## Files materially relevant to this lane
- `docs/plans/2026-04-22-issue-2461-assetutilities-routing-and-source-hygiene.md`
- `docs/plans/2026-04-22-issue-2462-digitalmodel-repo-wide-routing-surfaces.md`
- `docs/plans/README.md`
- `scripts/review/results/2026-04-22-plan-2461-claude.md`
- `scripts/review/results/2026-04-22-plan-2462-claude.md`
- `scripts/review/results/2026-04-22-plan-2462-codex.md`
- `scripts/review/results/2026-04-22-plan-2462-gemini.md`
