# Claude agent-team prompt: #2226 ledger/provenance backfill planning pack

Use this prompt as a single self-contained handoff to Claude Code.

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. Provenance / Ledger Analyst
3. Adversarial Reviewer
4. Integrator

Do not ask the user any questions.

Critical repo/workflow constraints:
- This repo is plan-gated.
- Issue `#2226` is not implementation-approved yet.
- Treat this run as planning-only.
- Do NOT modify the ledger, code registry, wiki pages, or pipeline code in this run.
- Your goal is to produce the planning package for `#2226`, grounded in the real indexed results now available from `acma_codes`, and move the issue to `status:plan-review` only if the plan is review-ready.
- If a blocking uncertainty remains after review, post a blocker summary and stop without applying `status:plan-review`.

Primary issue:
- `#2226` https://github.com/vamseeachanta/workspace-hub/issues/2226

Parent / related issues to consume, not redefine:
- Parent implementation umbrella: `#2216`
- Upstream completed implementation: `#2225`
- Parent architecture: `#2205`
- Related contracts: `#2207`, `#2209`
- Downstream follow-ons from split: `#2227`, `#2228`

Primary repo artifacts to read first:
- `docs/plans/2026-04-11-issue-2216-acma-codes-llm-wiki-repo-intelligence-integration.md`
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- `data/document-index/standards-transfer-ledger.yaml`
- `data/design-codes/code-registry.yaml`
- `data/document-index/index.jsonl`
- `scripts/data/document-index/provenance.py`
- `docs/plans/README.md`
- `docs/plans/_template-issue-plan.md`

Use live indexed evidence from the completed #2225 work:
- `acma_codes` source is now registered and indexed
- `index.jsonl` contains `acma_codes` records
- use real indexed results to reason about API overlap, OCIMF net-new content, CSA additions, and duplicate/alias behavior

Allowed write paths for this run:
- `docs/plans/2026-04-11-issue-2226-ocimf-csa-ledger-provenance-backfill.md`
- `scripts/review/results/2026-04-11-plan-2226-claude.md`
- `scripts/review/results/2026-04-11-plan-2226-final.md`
- `docs/plans/README.md`

Read-only paths:
- `data/document-index/**`
- `data/design-codes/**`
- `docs/**`
- GitHub issue threads listed above

Forbidden paths:
- `knowledge/**`
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
By the end of this run, the repo should contain a review-ready plan for `#2226` that:
- identifies exactly which OCIMF and CSA standards should be added to the transfer ledger
- uses real indexed `acma_codes` evidence and real existing ledger state
- defines provenance/doc-key linkage expectations consistent with `#2207`
- defines how overlapping API records should be treated as aliases or distinct editions
- defines whether `data/design-codes/code-registry.yaml` should change and why
- stays within planning scope and does not edit the ledger yet
- has been adversarially reviewed in this run
- is posted back to GitHub as a plan-review package if ready

Required outputs:
1. A formal plan file:
   - `docs/plans/2026-04-11-issue-2226-ocimf-csa-ledger-provenance-backfill.md`
2. A Claude review artifact:
   - `scripts/review/results/2026-04-11-plan-2226-claude.md`
3. A final synthesis / integrator artifact:
   - `scripts/review/results/2026-04-11-plan-2226-final.md`
4. Update the plan index in `docs/plans/README.md`
5. Post a summary comment on GitHub issue `#2226`
6. Apply `status:plan-review` only if the plan is review-ready and the label exists

The plan must include these core sections:
- Resource Intelligence Summary
- Existing ledger/code-registry/index artifacts consulted
- Real indexed findings from `acma_codes`
- Candidate ledger entries / updates
- Proposed alias vs new-entry treatment for API overlaps
- Proposed provenance/doc-key linkage rules for this issue’s implementation
- Whether design-code registry updates are in scope or deferred
- Artifact map
- Deliverable
- Pseudocode / ledger-backfill logic sketch
- Files to Change (planning scope only)
- Verification list for future implementation
- Acceptance Criteria
- Adversarial Review Summary
- Risks and Open Questions
- Complexity

Specific planning questions to answer from real evidence:
1. Which exact OCIMF and CSA documents now visible in `index.jsonl` deserve ledger entries?
2. Which API records should be treated as alias paths to existing entries versus distinct editions/new entries?
3. How should `doc_key` / content hash be threaded into the ledger or related provenance surfaces?
4. What evidence exists that OCIMF MEG 2008 is duplicate vs historical predecessor vs different scan?
5. Does `code-registry.yaml` need any updates in this issue, or should that be deferred?
6. What outputs should this issue produce to make `#2227` wiki promotion straightforward?

Execution steps:

STEP 1 — Live intake and resource intelligence
- Read `#2226` live from GitHub.
- Read the parent #2216 plan and the completed #2225 implementation evidence.
- Inspect current ledger entries, code-registry entries, and real `acma_codes` records in `index.jsonl`.
- Ground all major claims in current data.

STEP 2 — Draft the plan
- Write the plan file in repo style.
- Keep it planning-only.
- Do not edit the ledger or code registry.
- Be explicit about alias handling, edition handling, and provenance linkage.

STEP 3 — Adversarial review
- Create `scripts/review/results/2026-04-11-plan-2226-claude.md`.
- Review for:
  - scope discipline
  - consistency with #2216, #2205, #2207
  - whether ledger-entry recommendations are grounded in real indexed evidence
  - whether alias vs distinct-edition handling is clearly defined
  - whether downstream handoff to #2227 is clear
- Revise the plan if needed.

STEP 4 — Final synthesis
- Create `scripts/review/results/2026-04-11-plan-2226-final.md`.
- State whether the plan is ready for `status:plan-review`.
- If not ready, explain exactly why.

STEP 5 — GitHub update
If ready:
- Post a concise planning summary comment to `#2226` with:
  - plan path
  - real indexed findings summary
  - ledger update model
  - alias/edition handling summary
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
- Ground every major claim in indexed records or current ledger/code-registry state.
- Keep this tightly scoped to ledger/provenance planning.
- Do not let planning drift into wiki promotion or accessibility updates.
- Produce a plan that can become the next operator-ready implementation dossier.
