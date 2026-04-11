# Claude agent-team prompt: #2208 intelligence retrieval contract planning pack

Use this prompt as a single self-contained handoff to Claude Code.

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. Workflow / Retrieval Architect
3. Adversarial Reviewer
4. Integrator

Do not ask the user any questions.

Critical repo/workflow constraints:
- This repo is plan-gated.
- Issue `#2208` is not currently known to be implementation-approved from the live state shown here.
- Treat this run as planning-only unless live checks prove otherwise.
- Do NOT implement template changes, hooks, gate scripts, or workflow enforcement code in this run.
- Your goal is to produce the planning package for `#2208`, grounded in the completed parent/sibling artifacts, and move the issue to `status:plan-review` only if the plan is review-ready.
- If a blocking uncertainty remains after review, post a blocker summary and stop without applying `status:plan-review`.

Primary issue:
- `#2208` https://github.com/vamseeachanta/workspace-hub/issues/2208

Related issues to consume, not redefine:
- `#2205` parent operating model
- `#2207` provenance + reuse contract
- `#2209` durable-vs-transient boundary policy
- `#2096` intelligence accessibility map
- `#2104` canonical entry points plan
- `#2136` accessibility registry plan
- downstream consumer: `#2089`

Primary repo artifacts to read first:
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`
- `docs/document-intelligence/intelligence-accessibility-map.md`
- `docs/plans/2026-04-11-issue-2104-canonical-entry-points-for-ecosystem-intelligence.md`
- `docs/plans/2026-04-11-issue-2136-intelligence-accessibility-registry-with-machine-reachability.md`
- `docs/plans/README.md`
- `docs/plans/_template-issue-plan.md`
- `docs/standards/engineering-issue-workflow-skill.md`
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`
- any workflow/planning docs that currently define resource-intelligence or plan-review expectations

Allowed write paths for this run:
- `docs/plans/2026-04-11-issue-2208-intelligence-retrieval-contract-for-github-issue-workflows.md`
- `scripts/review/results/2026-04-11-plan-2208-claude.md`
- `scripts/review/results/2026-04-11-plan-2208-final.md`
- `docs/plans/README.md`

Read-only paths:
- `docs/**`
- `knowledge/**`
- `data/**`
- `scripts/review/results/**`
- GitHub issue threads listed above

Forbidden paths:
- `scripts/**` except read-only inspection
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
By the end of this run, the repo should contain a review-ready plan for `#2208` that:
- defines the retrieval contract by workflow stage (intake, planning, execution, review, closeout)
- specifies the minimum retrieval bundle for relevant issue classes
- defines where retrieval evidence must appear in plan artifacts and GitHub comments
- defines measurable checks for retrieval compliance and success
- clearly separates discovery registries from synthesis wikis and execution state
- stays consistent with `#2205`, `#2207`, `#2209`, `#2096`, `#2104`, and `#2136`
- has been adversarially reviewed in this run
- is posted back to GitHub as a plan-review package if ready

Required outputs:
1. A formal plan file:
   - `docs/plans/2026-04-11-issue-2208-intelligence-retrieval-contract-for-github-issue-workflows.md`
2. A Claude review artifact:
   - `scripts/review/results/2026-04-11-plan-2208-claude.md`
3. A final synthesis / integrator artifact:
   - `scripts/review/results/2026-04-11-plan-2208-final.md`
4. Update the plan index in `docs/plans/README.md`
5. Post a summary comment on GitHub issue `#2208`
6. Apply `status:plan-review` only if the plan is review-ready and the label exists

The plan must include these core sections:
- Resource Intelligence Summary
- Existing workflow/governance artifacts consulted
- Parent/sibling artifacts consulted
- Current retrieval expectations and gaps
- Proposed retrieval contract by workflow stage
- Proposed minimum retrieval bundles by issue class
- Required evidence placement in plan/review/GitHub artifacts
- Measurable checks / scorecard ideas
- Artifact map
- Deliverable
- Pseudocode / workflow logic sketch
- Files to Change (planning scope only; likely future implementation surfaces may be listed separately)
- TDD / verification list for future implementation
- Acceptance Criteria
- Adversarial Review Summary
- Risks and Open Questions
- Complexity

Specific planning questions to answer from real evidence:
1. What should every issue always retrieve before planning begins?
2. Which issue classes require additional retrieval (standards/doc-intel/wiki/registry) beyond general code/docs/issue history?
3. Where exactly should retrieval evidence appear in:
   - issue plans
   - review artifacts
   - GitHub comments
4. What should count as sufficient evidence that intelligence was actually used?
5. Which parts of the contract can be enforced by templates/docs alone, and which need later tooling/hooks?
6. How should the retrieval contract depend on the canonical entry points (`#2104`) and accessibility registry (`#2136`) without blocking on them completely?
7. What should remain out of scope because it belongs to implementation/enforcement follow-ons rather than this contract issue?

Execution steps:

STEP 1 — Live intake and resource intelligence
- Read `#2208` live from GitHub.
- Read the completed parent/sibling docs and the new #2104/#2136 plans.
- Inspect current planning/workflow/governance docs for how resource intelligence and evidence are already required or implied.
- Identify the gap between current expectations and a formal retrieval contract.

STEP 2 — Draft the plan
- Write the plan file in repo style.
- Keep it planning-only.
- Do not implement hooks, templates, or scripts.
- Be explicit about workflow stages, evidence locations, and measurable checks.

STEP 3 — Adversarial review
- Create `scripts/review/results/2026-04-11-plan-2208-claude.md`.
- Review for:
  - scope discipline
  - consistency with `#2205`, `#2207`, `#2209`, `#2096`, `#2104`, `#2136`
  - whether the contract is practical and auditable
  - whether evidence placement and checks are specific enough
  - whether boundaries with tooling/enforcement work are clear
- Revise the plan if needed.

STEP 4 — Final synthesis
- Create `scripts/review/results/2026-04-11-plan-2208-final.md`.
- State whether the plan is ready for `status:plan-review`.
- If not ready, explain exactly why.

STEP 5 — GitHub update
If ready:
- Post a concise planning summary comment to `#2208` with:
  - plan path
  - retrieval contract purpose summary
  - minimum retrieval bundle summary
  - evidence placement summary
  - measurable checks summary
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
- Ground every major claim in existing workflow docs and completed sibling artifacts.
- Prefer a practical auditable contract over an abstract governance essay.
- Do not let planning drift into implementation.
- Keep boundaries with entry points, registry, and enforcement tooling explicit.
- Produce a plan that can become the next operator-ready implementation dossier.
