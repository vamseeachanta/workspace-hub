# Weekly-cadence plan-review hardening pattern

Use after creating or drafting an LLM-wiki weekly-cadence / code-utility issue wave and before asking the user to approve implementation.

## Trigger

The issue wave contains multiple related plan artifacts for freshness, manifests, graph/retrieval, benchmarks, watchlists, or query surfaces. Adversarial review returns `MINOR` or `MAJOR` findings that are fixable by narrowing scope and freezing contracts.

## Pattern

1. Patch each plan with a dedicated section named `Adversarial review synthesis and accepted hardening`.
2. For each issue, normalize reviewer output into:
   - original review verdict
   - accepted changes
   - revised v1 boundary
   - residual risk
   - approval posture
3. Create one cross-issue synthesis report under `docs/reports/` that lists:
   - all issues in scope
   - verdict before hardening
   - patched status
   - residual risk
   - recommended execution order
   - cross-issue binding constraints
4. Commit and push the patched plans plus synthesis report before posting issue comments. Use the pushed commit hash in every GitHub comment.
5. Post a compact comment to each issue, then move labels from `status:pending` to `status:plan-review`.
6. Verify live issue labels and latest comment URLs before surfacing approvals to the user.

## Durable hardening themes from the 2026-05-15 wave

- Prefer checked-in JSON contracts and fixture-backed tests for v1.
- Keep default validation offline/no-network.
- Separate live update scanning from deterministic report rendering.
- Use schema versions and stable artifact paths for machine-readable outputs.
- Make gated/downstream behavior explicit instead of partially implementing hidden dependencies.
- Keep public-safe summaries and path-bounded evidence; do not expose private/client/vendor raw content.

## Recommended wave sequencing

For a weekly cadence / code-utility roadmap, recommend approval in two waves:

1. First wave: freshness control loop, agent entrypoints/manifests, and external concept/tool watchlist.
2. Second wave: knowledge graph, retrieval benchmark, and query surface after first-wave artifact contracts exist.

## GitHub comment shape

Each issue comment should include:

- topic
- patched plan path
- cross-issue synthesis report path
- commit hash
- residual risk
- approval posture
- short bullet list of binding hardening accepted into the plan
- explicit gate state: `status:plan-review`; implementation blocked until explicit user approval moves it to `status:plan-approved`

## Pitfalls

- Do not mark MAJOR-reviewed plans as approval-ready without naming the narrowed scope and residual risk.
- Do not post comments before pushing the plan patches; otherwise GitHub points to uncommitted local state.
- Do not ask the user to approve all issues as one undifferentiated batch when some are substrate work and others depend on the substrate.
