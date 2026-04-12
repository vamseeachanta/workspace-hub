# Claude agent-team prompt: #2225 acma-codes source registration and initial indexing planning pack

Use this prompt as a single self-contained handoff to Claude Code.

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. Data-Pipeline / Source-Registration Analyst
3. Adversarial Reviewer
4. Integrator

Do not ask the user any questions.

Critical repo/workflow constraints:
- This repo is plan-gated.
- Issue `#2225` is not implementation-approved yet.
- Treat this run as planning-only.
- Do NOT modify pipeline code, registries, wiki pages, or index outputs in this run.
- Your goal is to produce the planning package for `#2225`, grounded in the real contents of `/mnt/ace/acma-codes` and the approved parent architecture, then move the issue to `status:plan-review` only if the plan is review-ready.
- If a blocking uncertainty remains after review, post a blocker summary and stop without applying `status:plan-review`.

Primary issue:
- `#2225` https://github.com/vamseeachanta/workspace-hub/issues/2225

Parent / related issues to consume, not redefine:
- Parent implementation umbrella: `#2216`
- Parent architecture: `#2205`
- Related contracts: `#2207`, `#2209`
- Related maps/registry design: `#2096`, `#2104`, `#2136`
- Downstream follow-ons from split: `#2226`, `#2227`, `#2228`

Primary repo artifacts to read first:
- `docs/plans/2026-04-11-issue-2216-acma-codes-llm-wiki-repo-intelligence-integration.md`
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`
- `data/document-index/mounted-source-registry.yaml`
- `data/document-index/standards-transfer-ledger.yaml`
- `data/document-index/index.jsonl`
- `scripts/data/document-index/phase-a-index.py`
- `scripts/data/document-index/provenance.py`
- `docs/plans/README.md`
- `docs/plans/_template-issue-plan.md`

Live source to inspect directly:
- `/mnt/ace/acma-codes`

Allowed write paths for this run:
- `docs/plans/2026-04-11-issue-2225-acma-codes-source-registration-and-initial-indexing.md`
- `scripts/review/results/2026-04-11-plan-2225-claude.md`
- `scripts/review/results/2026-04-11-plan-2225-final.md`
- `docs/plans/README.md`

Read-only paths:
- `/mnt/ace/acma-codes/**`
- `data/document-index/**`
- `scripts/data/document-index/**`
- `docs/**`
- GitHub issue threads listed above

Forbidden paths:
- `knowledge/**`
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
By the end of this run, the repo should contain a review-ready plan for `#2225` that:
- defines the exact source-registration change for `/mnt/ace/acma-codes`
- uses real live inventory evidence from the mounted directory
- defines the Phase A indexing scope and junk-file exclusion rules
- defines the initial dedup assessment approach against the current corpus
- identifies expected outputs/artifacts from the first implementation wave
- stays within planning scope and does not execute indexing or modify registries in this run
- has been adversarially reviewed in this run
- is posted back to GitHub as a plan-review package if ready

Required outputs:
1. A formal plan file:
   - `docs/plans/2026-04-11-issue-2225-acma-codes-source-registration-and-initial-indexing.md`
2. A Claude review artifact:
   - `scripts/review/results/2026-04-11-plan-2225-claude.md`
3. A final synthesis / integrator artifact:
   - `scripts/review/results/2026-04-11-plan-2225-final.md`
4. Update the plan index in `docs/plans/README.md`
5. Post a summary comment on GitHub issue `#2225`
6. Apply `status:plan-review` only if the plan is review-ready and the label exists

The plan must include these core sections:
- Resource Intelligence Summary
- Existing registry/index/pipeline surfaces consulted
- Live inventory findings for `/mnt/ace/acma-codes`
- Proposed source-registration model
- Proposed Phase A indexing scope
- Junk/non-document exclusion policy
- Initial dedup assessment design
- Artifact map
- Deliverable
- Pseudocode / indexing-dedup logic sketch
- Files to Change (planning scope only)
- Verification list for future implementation
- Acceptance Criteria
- Adversarial Review Summary
- Risks and Open Questions
- Complexity

Specific planning questions to answer from real evidence:
1. What are the actual top-level source families and representative file types in `/mnt/ace/acma-codes`?
2. What exact mounted-source-registry entry should be added?
3. How should junk artifacts like `Thumbs.db` be excluded or classified?
4. What is the best first-pass dedup method against existing corpus and standards sources?
5. What outputs should implementation produce for downstream issue #2226?
6. What live inventory caveats remain even after direct inspection?

Execution steps:

STEP 1 — Live intake and resource intelligence
- Read `#2225` live from GitHub.
- Inspect `/mnt/ace/acma-codes` directly (top-level families, representative files, junk artifacts).
- Read the relevant registry/pipeline sources and the parent #2216 plan.
- Ground all major claims in current repo files and live directory contents.

STEP 2 — Draft the plan
- Write the plan file in repo style.
- Keep it planning-only.
- Do not run indexing or modify registries.
- Be explicit about the mounted source entry, filtering rules, and dedup strategy.

STEP 3 — Adversarial review
- Create `scripts/review/results/2026-04-11-plan-2225-claude.md`.
- Review for:
  - scope discipline
  - consistency with #2216, #2205, #2207
  - whether the live inventory is sufficiently grounded
  - whether indexing/dedup plan is realistic and bounded
  - whether downstream handoff to #2226 is clear
- Revise the plan if needed.

STEP 4 — Final synthesis
- Create `scripts/review/results/2026-04-11-plan-2225-final.md`.
- State whether the plan is ready for `status:plan-review`.
- If not ready, explain exactly why.

STEP 5 — GitHub update
If ready:
- Post a concise planning summary comment to `#2225` with:
  - plan path
  - live inventory summary
  - source-registration model
  - dedup strategy summary
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
- Ground every major claim in direct inspection or current repo artifacts.
- Keep this tightly scoped to source registration, Phase A indexing, and initial dedup planning.
- Do not let planning drift into ledger, wiki, or accessibility implementation.
- Produce a plan that can become the next operator-ready implementation dossier.
