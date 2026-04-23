# Terminal 1 summary — contract and control plane salvage

Date: 2026-04-23
Scope: #2390, #2460, #2464
Mode: direct salvage after unattended overnight no-output runs

## What changed
- confirmed the llm-wiki umbrella (#2390) already includes Work Stream G linking tier-1 routing/index work into the knowledge roadmap
- confirmed the canonical contract plan for #2460 exists:
  - `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md`
- confirmed the canonical workspace-hub remediation plan for #2464 exists:
  - `docs/plans/2026-04-22-issue-2464-workspace-hub-curated-routing-index.md`
- added the missing `docs/plans/README.md` index row for #2464 during the salvage pass

## Issue-by-issue readiness

### #2390 — epic(knowledge): llm-wiki strengthening roadmap and execution waves
Status: usable umbrella / sequencing surface

Why it matters:
- already connects llm-wiki strengthening to tier-1 repo-routing work via Work Stream G
- should remain the portfolio steering issue rather than absorb implementation details

Immediate blocker:
- none for roadmap usage

### #2460 — tier-1 indexing and code-placement contract
Status: draft, central prerequisite

Evidence:
- plan exists at `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md`
- issue is open and currently `status:plan-review`

Why it gates the rest:
- child plans #2461-#2465 depend on this contract to lock naming, routing-surface requirements, and registry/operator-map conventions

Immediate blocker:
- still draft / not yet user-approved

### #2464 — workspace-hub curated routing index
Status: draft, partial review only

Evidence:
- plan exists at `docs/plans/2026-04-22-issue-2464-workspace-hub-curated-routing-index.md`
- review artifact exists only for Claude:
  - `scripts/review/results/2026-04-23-plan-2464-claude.md`

Immediate blocker:
- Codex/Gemini adversarial review artifacts are still missing
- implementation should not start before #2460 is locked

## Remaining blockers
- #2460 must mature first; it is the contract gate for the repo-routing wave
- #2464 still needs broader adversarial review coverage beyond Claude self-review
- the unattended overnight Claude worktrees produced no durable edits; this summary is a manual salvage artifact

## Recommended morning execution order
1. tighten / review / approve #2460 first
2. once #2460 is locked, route #2462 and #2465 next because they have the strongest downstream leverage
3. then run #2464 as the workspace-hub control-plane cleanup after the contract is stable
4. keep #2390 as the steering umbrella, not a delivery vehicle

## Files materially relevant to this lane
- `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md`
- `docs/plans/2026-04-22-issue-2464-workspace-hub-curated-routing-index.md`
- `docs/plans/README.md`
- `scripts/review/results/2026-04-23-plan-2464-claude.md`
