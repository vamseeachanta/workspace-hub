# Claude agent-team prompt: #2104 canonical entry points planning pack

Use this prompt as a single self-contained handoff to Claude Code.

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. Navigation / Information Architecture Designer
3. Adversarial Reviewer
4. Integrator

Do not ask the user any questions.

Critical repo/workflow constraints:
- This repo is plan-gated.
- Issue `#2104` is not currently known to be implementation-approved from the live state shown here.
- Treat this run as planning-only unless live checks prove otherwise.
- Do NOT implement the entry-point pages, docs rewrites, or registry code in this run.
- Your goal is to produce the planning package for `#2104`, grounded in the completed parent/sibling artifacts, and move the issue to `status:plan-review` only if the plan is review-ready.
- If a blocking uncertainty remains after review, post a blocker summary and stop without applying `status:plan-review`.

Primary issue:
- `#2104` https://github.com/vamseeachanta/workspace-hub/issues/2104

Related issues to consume, not redefine:
- `#2205` parent operating model
- `#2207` provenance + reuse contract
- `#2209` durable-vs-transient boundary policy
- `#2096` intelligence accessibility map
- `#2136` accessibility registry
- `#2208` workflow retrieval contract
- downstream consumer: `#2089`

Primary repo artifacts to read first:
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`
- `docs/document-intelligence/intelligence-accessibility-map.md`
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`
- `docs/README.md`
- `docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md`
- `docs/standards/CONTROL_PLANE_CONTRACT.md`
- `docs/modules/ai-native/workspace-hub-structure.md`
- `docs/document-intelligence/data-intelligence-map.md`
- `docs/document-intelligence/engineering-documentation-map.md`
- `docs/plans/README.md`
- `docs/plans/_template-issue-plan.md`

Allowed write paths for this run:
- `docs/plans/2026-04-11-issue-2104-canonical-entry-points-for-ecosystem-intelligence.md`
- `scripts/review/results/2026-04-11-plan-2104-claude.md`
- `scripts/review/results/2026-04-11-plan-2104-final.md`
- `docs/plans/README.md`

Read-only paths:
- `docs/**`
- `knowledge/**`
- `scripts/review/results/**`
- GitHub issue threads listed above

Forbidden paths:
- `data/**`
- `scripts/data/**`
- `scripts/knowledge/**`
- `tests/**`
- `.claude/**`
- `.codex/**`
- `config/**`
- any unrelated dirty/untracked files currently in the worktree

Git safety rule:
- First inspect `git status --short`.
- The repo is already dirty with many unrelated files.
- Do NOT modify anything outside the allowed write paths.
- If the worktree is too dirty to safely write only the allowed files, stop and report that explicitly in the final summary and issue comment.

Success condition:
By the end of this run, the repo should contain a review-ready plan for `#2104` that:
- defines the canonical entry-point strategy for ecosystem intelligence
- uses the completed accessibility map (`#2096`) as evidence rather than re-inventorying blindly
- identifies the minimum navigation surface needed for humans and agents
- defines recommended linking/navigation standards
- identifies dead-end, redundant, or conflicting entry points to retire or demote
- defines weekly validation checks for entry-point health
- stays within planning scope and does not build the pages yet
- has been adversarially reviewed in this run
- is posted back to GitHub as a plan-review package if ready

Required outputs:
1. A formal plan file:
   - `docs/plans/2026-04-11-issue-2104-canonical-entry-points-for-ecosystem-intelligence.md`
2. A Claude review artifact:
   - `scripts/review/results/2026-04-11-plan-2104-claude.md`
3. A final synthesis / integrator artifact:
   - `scripts/review/results/2026-04-11-plan-2104-final.md`
4. Update the plan index in `docs/plans/README.md`
5. Post a summary comment on GitHub issue `#2104`
6. Apply `status:plan-review` only if the plan is review-ready and the label exists

The plan must include these core sections:
- Resource Intelligence Summary
- Existing repo docs and entry points consulted
- Parent/sibling artifacts consulted
- Current entry points and their strengths/weaknesses
- Redundant/conflicting/dead-end entry points identified
- Proposed canonical entry-point model
- Recommended linking/navigation standards
- Artifact map
- Deliverable
- Pseudocode / navigation logic sketch
- Files to Change (planning scope only; likely future implementation surfaces may be listed separately)
- TDD / verification list for future implementation
- Acceptance Criteria
- Adversarial Review Summary
- Risks and Open Questions
- Complexity

Specific planning questions to answer from real evidence:
1. What should be the canonical top-level human entry point(s) for ecosystem intelligence?
2. What should be the canonical agent entry point(s)?
3. Which current assets should be linked directly from `docs/README.md` and which should remain one level deeper?
4. Should `docs/document-intelligence/README.md` or similar become the intelligence landing page? If so, what must it contain?
5. How should wiki domains surface upward into the main docs navigation?
6. Which current entry points are obsolete, conflicting, or dead-end and should be retired/demoted?
7. What validation checks should `#2089` use weekly to confirm entry-point health?
8. What implementation should remain deferred to `#2136` (registry) and `#2208` (workflow retrieval)?

Execution steps:

STEP 1 — Live intake and resource intelligence
- Read `#2104` live from GitHub.
- Read the completed parent/sibling architecture docs.
- Use `#2096` as the factual baseline for current discoverability gaps.
- Inspect current entry-point surfaces such as `docs/README.md`, control-plane docs, capability summaries, wiki indexes, and document-intelligence maps.

STEP 2 — Draft the plan
- Write the plan file in repo style.
- Keep it planning-only.
- Do not implement docs or code changes.
- Be explicit about canonical entry-point recommendations and what should remain deferred.

STEP 3 — Adversarial review
- Create `scripts/review/results/2026-04-11-plan-2104-claude.md`.
- Review for:
  - scope discipline
  - consistency with `#2205`, `#2207`, `#2209`, `#2096`
  - whether recommendations are grounded in actual current entry points
  - whether boundaries with `#2136` and `#2208` are clear
  - whether the proposed navigation surface is minimal and practical
- Revise the plan if needed.

STEP 4 — Final synthesis
- Create `scripts/review/results/2026-04-11-plan-2104-final.md`.
- State whether the plan is ready for `status:plan-review`.
- If not ready, explain exactly why.

STEP 5 — GitHub update
If ready:
- Post a concise planning summary comment to `#2104` with:
  - plan path
  - top-level canonical entry-point recommendations
  - dead-end/conflicting entry points found
  - recommended minimum navigation surface
  - review verdict summary
- Apply `status:plan-review` if the label exists.

If not ready:
- Post a blocker summary comment and do NOT apply `status:plan-review`.

Final return format in the Claude session:
1. What changed
2. Final review verdict
3. Whether `status:plan-review` was applied
4. Exact files changed
5. Exact GitHub comment/labels added
6. Residual blockers or risks

Quality bar:
- Ground every major claim in existing repo navigation surfaces.
- Prefer a minimal stable navigation design over an exhaustive portal redesign.
- Do not let planning drift into implementation.
- Keep boundaries with registry and workflow issues explicit.
- Produce a plan that can become the next operator-ready implementation dossier.
