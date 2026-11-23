# Claude agent-team prompt: #2136 intelligence accessibility registry planning pack

Use this prompt as a single self-contained handoff to Claude Code.

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. Registry / Information Architecture Designer
3. Adversarial Reviewer
4. Integrator

Do not ask the user any questions.

Critical repo/workflow constraints:
- This repo is plan-gated.
- Issue `#2136` is not currently known to be implementation-approved from the live state shown here.
- Treat this run as planning-only unless live checks prove otherwise.
- Do NOT implement the registry schema, generator, query tooling, or tests in this run.
- Your goal is to produce the planning package for `#2136`, grounded in the completed parent/sibling artifacts, and move the issue to `status:plan-review` only if the plan is review-ready.
- If a blocking uncertainty remains after review, post a blocker summary and stop without applying `status:plan-review`.

Primary issue:
- `#2136` https://github.com/vamseeachanta/workspace-hub/issues/2136

Related issues to consume, not redefine:
- `#2205` parent operating model
- `#2207` provenance + reuse contract
- `#2209` durable-vs-transient boundary policy
- `#2096` intelligence accessibility map
- `#2104` canonical entry points plan
- `#2208` workflow retrieval contract
- downstream consumer: `#2089`

Primary repo artifacts to read first:
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`
- `docs/document-intelligence/intelligence-accessibility-map.md`
- `docs/plans/2026-04-11-issue-2104-canonical-entry-points-for-ecosystem-intelligence.md`
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`
- `data/document-index/registry.yaml`
- `data/document-index/standards-transfer-ledger.yaml`
- `data/document-index/mounted-source-registry.yaml`
- `data/design-codes/code-registry.yaml`
- `docs/plans/README.md`
- `docs/plans/_template-issue-plan.md`

Allowed write paths for this run:
- `docs/plans/2026-04-11-issue-2136-intelligence-accessibility-registry-with-machine-reachability.md`
- `scripts/review/results/2026-04-11-plan-2136-claude.md`
- `scripts/review/results/2026-04-11-plan-2136-final.md`
- `docs/plans/README.md`

Read-only paths:
- `docs/**`
- `data/**`
- `knowledge/**`
- `scripts/review/results/**`
- GitHub issue threads listed above

Forbidden paths:
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
By the end of this run, the repo should contain a review-ready plan for `#2136` that:
- defines the registry purpose and role in the architecture without implementing it
- identifies the canonical fields needed for intelligence accessibility, including machine reachability
- stays consistent with the `doc_key` and provenance requirements from `#2207`
- uses the current accessibility map (`#2096`) and entry-point planning (`#2104`) as evidence and upstream inputs
- defines seeding strategy for major intelligence assets
- defines validation expectations for schema completeness and registry health
- clearly separates what belongs in the registry from what stays in docs/wikis/issues
- has been adversarially reviewed in this run
- is posted back to GitHub as a plan-review package if ready

Required outputs:
1. A formal plan file:
   - `docs/plans/2026-04-11-issue-2136-intelligence-accessibility-registry-with-machine-reachability.md`
2. A Claude review artifact:
   - `scripts/review/results/2026-04-11-plan-2136-claude.md`
3. A final synthesis / integrator artifact:
   - `scripts/review/results/2026-04-11-plan-2136-final.md`
4. Update the plan index in `docs/plans/README.md`
5. Post a summary comment on GitHub issue `#2136`
6. Apply `status:plan-review` only if the plan is review-ready and the label exists

The plan must include these core sections:
- Resource Intelligence Summary
- Existing registry/provenance assets consulted
- Parent/sibling artifacts consulted
- Gaps in the current registry landscape
- Proposed registry role and scope boundaries
- Proposed minimum field set and validation expectations
- Seeding strategy for major intelligence assets
- Artifact map
- Deliverable
- Pseudocode / registry-assembly logic sketch
- Files to Change (planning scope only; likely future implementation surfaces may be listed separately)
- TDD / verification list for future implementation
- Acceptance Criteria
- Adversarial Review Summary
- Risks and Open Questions
- Complexity

Specific planning questions to answer from real evidence:
1. What exact problem does the accessibility registry solve that current docs/maps do not?
2. What should be the minimum required fields for each registry row?
3. Which fields come from existing assets today versus needing future implementation?
4. How should machine reachability be represented without conflicting with the parent pyramid or provenance contract?
5. What are the first major assets to seed into the registry?
6. How should the registry relate to:
   - `data/document-index/registry.yaml`
   - `standards-transfer-ledger.yaml`
   - `mounted-source-registry.yaml`
   - `code-registry.yaml`
   - accessibility map docs
7. What should remain out of scope for `#2136` because it belongs to `#2104` or `#2208`?
8. What future implementation surfaces are most likely touched if this issue is later approved?

Execution steps:

STEP 1 — Live intake and resource intelligence
- Read `#2136` live from GitHub.
- Read the completed parent/sibling docs and the new #2104 plan.
- Inspect the current machine-readable registry/provenance surfaces in `data/`.
- Identify what information already exists and what the accessibility registry still needs to add.

STEP 2 — Draft the plan
- Write the plan file in repo style.
- Keep it planning-only.
- Do not implement schemas or tooling.
- Be explicit about scope boundaries and how the registry differs from existing registries/ledgers/maps.

STEP 3 — Adversarial review
- Create `scripts/review/results/2026-04-11-plan-2136-claude.md`.
- Review for:
  - scope discipline
  - consistency with `#2205`, `#2207`, `#2209`, `#2096`, `#2104`
  - whether the registry role is clearly distinct from docs/maps and from workflow retrieval
  - whether the minimum field set is grounded in actual current repo assets
  - whether implementation scope is bounded
- Revise the plan if needed.

STEP 4 — Final synthesis
- Create `scripts/review/results/2026-04-11-plan-2136-final.md`.
- State whether the plan is ready for `status:plan-review`.
- If not ready, explain exactly why.

STEP 5 — GitHub update
If ready:
- Post a concise planning summary comment to `#2136` with:
  - plan path
  - registry purpose summary
  - minimum field-set summary
  - seeding strategy summary
  - boundaries with `#2104` and `#2208`
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
- Ground every major claim in existing repo registry/provenance assets.
- Prefer a clear, minimal registry role over a giant redesign.
- Do not let planning drift into implementation.
- Keep boundaries with entry points and workflow retrieval explicit.
- Produce a plan that can become the next operator-ready implementation dossier.
