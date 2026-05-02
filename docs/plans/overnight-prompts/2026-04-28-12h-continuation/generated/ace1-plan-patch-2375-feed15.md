# ace1-plan-patch-2375-feed15 — bounded plan patch for #2375

You are running unattended as a safe follow-up lane in the 2026-04-28 12h continuation window.

## Scope

Patch only the draft plan for #2375 to address the prior feed14 adversarial review findings.

- Plan to patch: `docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md`
- Prior draft result: `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-draft-2375-feed13.md`
- Prior review result: `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-review-2375-feed14.md`
- Full review artifact: `scripts/review/results/2026-04-29-plan-2375-claude-feed14.md`

## Required patch items

Address only the three MINOR findings from feed14:

1. F1: Fix the inaccurate claim that the #2375 0..3 scoring rubric mirrors #2370. Clarify the relationship accurately: #2375 may share qualitative classification goals with #2370 but uses a different numeric architecture from #2370's 4-dimension × 0-5 weighted composite. Add a coordination note for future merge/cross-ledger work.
2. F2: Add or correct the sibling-plan coordination note for #2374's stale wiki-candidate path reference (`knowledge-base/wiki-candidates.yaml` → current `data/document-index/wrk-wiki-candidates.yaml`). Do not patch the #2374 plan in this lane; only document the coordination hazard in #2375.
3. F3: Define the previously undefined pseudocode helpers or replace them with plan-local contracts: `existing_wiki_page_for`, `DURABLE_CATEGORIES`, and `route_engineering_subdomain`. Keep `existing_wiki_page_for` read-only; do not imply this issue mutates existing wiki pages.

You may also fix the LOW wording nits only if adjacent to the required edits (e.g. RULES count wording, `classify()` vs `apply_rules()` naming, `completed_at: None` documentation, route_domain catch-all tests). Do not broaden scope.

## Allowed actions

- Read repository files and the prior review artifacts needed to make the patch accurate.
- Edit exactly this plan file: `docs/plans/2026-04-29-issue-2375-wrk-completions-normalize.md`.
- Write exactly this lane result file: `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-patch-2375-feed15.md`.
- Optionally run read-only validation commands or focused docs checks that do not mutate repo state.

## Hard boundaries

- Do not implement code.
- Do not create approval markers.
- Do not add or remove GitHub labels.
- Do not post issue comments, create PRs, merge, close, push, force-push, hard reset, or mutate GitHub.
- Do not launch additional agents.
- Do not route to cross-provider review in this lane; the next lane/control surface may do that after inspecting your patch.
- If blocked by permissions, write the blocker and complete; do not spin.

## Output requirements

The lane result must include:

- `Classification: COMPLETED_WITH_RESULT` unless blocked before useful work.
- Summary of exact plan sections changed.
- Mapping from feed14 findings F1-F3 to patch status.
- Any residual risks / next safe action (expected: second-provider reviews via `plan-review-fanout.sh`, then status:plan-review only after reviews pass and operator approves).
- Explicit boundary compliance statement.
