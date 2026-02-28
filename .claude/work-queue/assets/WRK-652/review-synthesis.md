# WRK-624 Review Synthesis

## Review set

- Claude final artifact: `.claude/work-queue/assets/WRK-651/claude-review-final.md`
- Codex plan review: `scripts/review/results/20260227T133331Z-plan.md-plan-codex.md`
- Gemini review: `specs/wrk/WRK-624/review/review-gemini.md`

## Historical review verdict

`REQUEST_CHANGES`

This was the correct synthesis verdict for the earlier revision reviewed by Claude/Codex/Gemini.

## Latest formal rerun verdict

`REQUEST_CHANGES`

Formal rerun executed on `2026-02-28` against the remediated draft:
- Claude: `REQUEST_CHANGES`
- Codex: `NO_OUTPUT`
- Gemini: `APPROVE`

Fallback consensus did not pass because Claude still returned blocking findings and Gemini approval alone was insufficient to override Codex `NO_OUTPUT`.
This rerun was one seed per provider and therefore does not satisfy the newer Route C review depth standard of 3 seeds per provider that was added afterward.

## Seed-compliant Route C review verdict

`REQUEST_CHANGES`

Strict Route C review completed with `3 seeds per provider` on the current draft:
- Claude seeds 1-3: `REQUEST_CHANGES`, `REQUEST_CHANGES`, `REQUEST_CHANGES`
- Codex seeds 1-3: `REQUEST_CHANGES`, `REQUEST_CHANGES`, `REQUEST_CHANGES`
- Gemini seeds 1-3: `APPROVE`, `APPROVE`, `APPROVE`

The pattern was fully stable across all nine runs: Claude and Codex consistently found blocking issues; Gemini consistently approved with operational-overhead cautions.

## Synthesis summary

The review set agreed that the workflow-hardening direction was strong and worth keeping, but the earlier draft had correctness and enforceability gaps. Those gaps have since been remediated in place. Gemini remained broadly supportive throughout, while Claude and Codex supplied the stricter critiques that drove the corrections.

## Cross-agent themes

### Strong agreement
- The 8-stage lifecycle and phased rollout are directionally sound.
- Review gates, closure evidence, and queue validation are the right hardening mechanisms.
- The workflow should standardize review artifact structure and enforce gate discipline.

### Previously blocking issues now addressed
- Metadata and state contradictions in the spec/work-item state were aligned.
- Previously underspecified terms were defined or tightened, including:
  - `computer`
  - Route A `risk signals`
  - acceptable short-defer threshold for claim/quota waits
- Mermaid failure/retry flow now routes through a revise/fix step instead of looping directly back to execute.
- Rollback coverage was added for later rollout phases.
- `INVALID_OUTPUT` is now explicitly treated as a blocking review/validator state in the policy surface.

### Rerun blocker groups now addressed in the current draft
- Phase 2 and Phase 3 now include explicit success metrics.
- User HTML review gates now define a 48-hour SLA with defer/delegate/rollback handling.
- The dependency contract now includes additional load-bearing systems referenced in the plan:
  - workstation registry
  - document-intelligence indexing
  - comprehensive-learning handoff
- The comprehensive-learning requirement now has an explicit contract covering owner, trigger, artifact set, metadata, and verification.

### Remaining non-blocking follow-up
- Rollback paths should be covered explicitly in the testing strategy.
- Route A scaling floor for resource packs/examples can still be tightened if you want less ambiguity for trivial items.
- Route A scaling and script-path consolidation remain worthwhile follow-up candidates but are no longer the primary blockers.

### Current blocking themes from the seed-compliant review
- Acceptance criteria remained too document-centric and did not define enough observable end-state behavior for WRK-624 delivery.
- User-review and deferral flow remained the primary blocker surface even with the 48-hour SLA.
- Scope boundary for WRK-624 versus follow-on automation/integration work was not explicit enough.

### Current draft direction after author decisions
- Full Route C seed depth is intentionally retained and is not being reduced as a workaround.
- User HTML review flow is treated as the primary blocking concern.
- Core WRK-624 scope is being tightened around lifecycle enforcement and HTML/user-review gating.
- Deeper legal-scan, document-intelligence, and comprehensive-learning automation are treated as follow-on integration work unless explicitly pulled back into core scope.

## Reviewer-specific emphasis

### Claude
- Drove the key blocking fixes: internal contradictions, execute-loop weakness, undefined terms, and missing rollback detail.
- In the latest rerun, shifted to a narrower set of enforceability gaps that have now been addressed in the current draft revision.

### Codex
- Earlier concerns about migration specificity, dependency authority, testing depth, and machine-checkable criteria materially improved the draft.
- The current draft retains those improvements.
- In the strict seeded review, Codex consistently continued to object to acceptance-criteria quality, scope boundary clarity, and operational feasibility.

### Gemini
- Broadly approved the direction.
- In the latest rerun, approved the draft while still noting Route A proportionality and timeout-override concerns.
- In the strict seeded review, Gemini consistently approved while continuing to note overhead and bottleneck risks rather than structural blockers.

## Resolution status

- Transport problem for Claude review: resolved enough for operational use via patched wrapper.
- Final Claude review mode: full bundle.
- Default Claude bounded wait: `300s`.
- Historical synthesis verdict remains `REQUEST_CHANGES` for the earlier reviewed revision.
- Latest formal rerun also remains `REQUEST_CHANGES`, but it should be interpreted as a single-seed-per-provider rerun rather than a fully seed-compliant Route C review.
- Seed-compliant Route C review now also remains `REQUEST_CHANGES`.
- Current document state has resolved the earlier structural blockers and rerun blocker groups; the remaining work is to align acceptance criteria and scope boundary with the chosen focus on user HTML review gating.
