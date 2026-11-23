You are working in `/mnt/local-analysis/workspace-hub`.

Overnight planning-only run. Do NOT implement source code. Your job is to strengthen the llm-wiki / repo-ecosystem control-plane packet so tomorrow's execution can proceed with less ambiguity and less rediscovery.

Owned issues
- #2390 — `epic(knowledge): llm-wiki strengthening roadmap and execution waves`
- #2460 — `feat(repo-organization): tier-1 indexing and code-placement contract`
- #2464 — `chore(workspace-hub): split curated tier-1 routing index from raw inventory and clean routing noise`

Mission
1. Reconcile the llm-wiki umbrella (#2390) with the tier-1 routing/index wave as an explicit execution dependency.
2. Tighten the canonical plan for #2460 so it is more approval-ready and more testable.
3. Draft or tighten the canonical plan for #2464 so workspace-hub becomes a cleaner curated routing/control-plane surface.
4. Leave behind one summary artifact that tells tomorrow's operator exactly what is ready vs still blocked.

Mandatory stance
- Planning and adversarial review only.
- No implementation in `src/`, `tests/`, nested repos, or runtime scripts.
- Do not ask the user questions.
- Do not create approval markers.
- Do not add `status:plan-approved`.
- You may update issue comments and `status:plan-review` only if the local plan + review evidence actually support it.

Owned write paths
- `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md`
- `docs/plans/2026-04-22-issue-2464-*.md` (create if missing)
- `docs/plans/README.md` (ONLY rows for #2460 and #2464)
- `docs/reports/2026-04-23-terminal-1-tier1-contract-summary.md`
- `scripts/review/results/*2460*`
- `scripts/review/results/*2464*`

Forbidden write paths
- any plan/review artifact for #2461, #2462, #2463, #2465
- `.planning/plan-approved/**`
- `src/**`
- `tests/**`
- any nested repo under `digitalmodel/`, `assetutilities/`, `aceengineer-website/`

Read-first sources
- `AGENTS.md`
- `docs/plans/2026-04-22-overnight-tier1-knowledge-beef-up-pack.md`
- `docs/reports/2026-04-16-llm-wiki-resource-intelligence-unified-review.md`
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `docs/reports/2026-04-22-tier-1-indexing-scorecard.md`
- live GitHub issue bodies/comments for #2390, #2460, #2464

Internal workflow
1. Planner
   - Verify live issue state for #2390, #2460, #2464.
   - Confirm whether #2464 already has a canonical `docs/plans/` artifact.
2. Reviewer
   - Look for scope drift, stale assumptions, missing acceptance criteria, and any contradiction between llm-wiki architecture and the tier-1 routing contract.
3. Implementer
   - Patch #2460 plan.
   - Create or patch #2464 plan.
   - If useful, add a concise GitHub comment to #2390 or #2460 clarifying the dependency chain.
4. Tester
   - Verify `docs/plans/README.md` rows are truthful and only the owned rows changed.
   - Verify review artifacts exist for the issues you revised.
5. Synthesizer
   - Write `docs/reports/2026-04-23-terminal-1-tier1-contract-summary.md` with sections:
     - What changed
     - Issue-by-issue readiness
     - Remaining blockers
     - Recommended next execution order

Validation expectations
- If `#2464` lacks a plan, create the canonical plan from template.
- If `#2460` already has a plan, improve specificity rather than rewriting aimlessly.
- Keep status conservative unless real review artifacts justify stronger language.
- Ensure the llm-wiki roadmap dependency on tier-1 routing surfaces remains explicit.

Output requirements
- Do not commit.
- Do not push.
- Print a concise completion summary listing exact files changed, exact issue comments posted, and exact blockers still open.