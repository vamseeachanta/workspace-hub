# Claude agent-team prompt: #2216 /mnt/ace/acma-codes integration planning pack

Use this prompt as a single self-contained handoff to Claude Code.

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. Resource-Intelligence Analyst
3. Adversarial Reviewer
4. Integrator

Do not ask the user any questions.

Critical repo/workflow constraints:
- This repo is plan-gated.
- Issue `#2216` is NOT implementation-ready unless live checks prove otherwise.
- This run is planning-only unless the issue is already fully approved for execution, which is unlikely. Verify live.
- Do NOT implement ingestion code, registry changes, wiki changes, or pipeline code for `#2216` in this run.
- Your goal is to produce the planning package for `#2216`, grounded in the real contents of `/mnt/ace/acma-codes`, and move the issue to `status:plan-review` only if the planning package is review-ready.
- If a blocking uncertainty remains after review, post a blocker summary and stop without applying `status:plan-review`.

Primary issue:
- `#2216` https://github.com/vamseeachanta/workspace-hub/issues/2216

Related architecture/issues to consume, not redefine:
- `#2205` parent operating model
- `#2207` provenance + reuse contract
- `#2209` durable-vs-transient boundary policy
- `#2096` intelligence accessibility map
- `#2104` canonical entry points
- `#2136` accessibility registry
- `#2208` workflow retrieval contract
- upstream context: `#1575`, `#1563`, `#2034`

Key real-world source location:
- `/mnt/ace/acma-codes`

Observed sample contents already known from live inspection:
- `OCIMF/OCIMF - 2008 - Mooring Equipment Guidelines.pdf`
- `OCIMF/OCIMF-Tandem Mooring and Offloading Guidelines for Conventional Tankers at FPSO Facilities.pdf`
- `API/1996 Dec RP 2SK Stationkeeping Systems for Floating Structures 2nd ed.pdf`
- `API/1999 July RP 1111 Offshore Hydrocarbon Pipelines 3rd ed.pdf`
- `CSA/276.1-20 marine structures associated with LNG facilities.pdf`
- `CSA/Z276.18 LNG Production, storage, and handling.pdf`
- mixed file types also exist (`.pdf`, `.xlsx`, `.txt`, `Thumbs.db`)

Primary repo artifacts to read first:
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`
- `docs/document-intelligence/intelligence-accessibility-map.md`
- `docs/assessments/document-intelligence-audit.md`
- `docs/document-intelligence/holistic-resource-intelligence.md`
- `data/document-index/standards-transfer-ledger.yaml`
- `data/document-index/mounted-source-registry.yaml`
- `data/design-codes/code-registry.yaml`
- `docs/plans/README.md`
- `docs/plans/_template-issue-plan.md`

Allowed write paths for this run:
- `docs/plans/2026-04-11-issue-2216-acma-codes-llm-wiki-repo-intelligence-integration.md`
- `scripts/review/results/2026-04-11-plan-2216-claude.md`
- `scripts/review/results/2026-04-11-plan-2216-final.md`
- `docs/plans/README.md`

Read-only paths:
- `/mnt/ace/acma-codes/**`
- `docs/document-intelligence/**`
- `data/document-index/**`
- `data/design-codes/**`
- `docs/**`
- GitHub issue threads listed above

Forbidden paths:
- `knowledge/wikis/**`
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
By the end of this run, the repo should contain a review-ready plan for `#2216` that:
- inventories and classifies the real contents of `/mnt/ace/acma-codes`
- states whether the collection is raw-source, derived, mixed, or duplicated corpus material
- defines how it should enter the intelligence ecosystem without violating #2205/#2207/#2209
- identifies dedup/provenance requirements against existing registries and corpora
- identifies likely promotion candidates into llm-wikis versus assets that should remain registry/provenance-only
- identifies likely follow-on implementation work if the task must split further
- has been adversarially reviewed in this run
- is posted back to GitHub as a plan-review package if ready

Required outputs:
1. A formal plan file using the repo plan template semantics:
   - `docs/plans/2026-04-11-issue-2216-acma-codes-llm-wiki-repo-intelligence-integration.md`
2. A Claude review artifact:
   - `scripts/review/results/2026-04-11-plan-2216-claude.md`
3. A final synthesis / integrator artifact:
   - `scripts/review/results/2026-04-11-plan-2216-final.md`
4. Update the plan index in `docs/plans/README.md`
5. Post a summary comment on GitHub issue `#2216`
6. Apply `status:plan-review` only if the plan is review-ready and the label exists

The plan must include these core sections:
- Resource Intelligence Summary
- Existing repo code / artifacts relevant to this source collection
- Standards / registries consulted
- LLM wiki pages or intelligence docs consulted
- Documents consulted
- Real inventory/classification of `/mnt/ace/acma-codes`
- Gaps identified
- Artifact map
- Deliverable
- Pseudocode / integration logic sketch
- Files to Change (planning scope only; likely future implementation surfaces may be listed separately)
- TDD / verification list for future implementation
- Acceptance Criteria
- Adversarial Review Summary
- Risks and Open Questions
- Complexity

Specific planning questions to answer from real evidence:
1. Which standards/code families are present under `/mnt/ace/acma-codes`?
2. What duplicate or overlap risk likely exists with existing corpora and registries?
3. Should `/mnt/ace/acma-codes` become:
   - a new mounted source,
   - a subset mapped into existing mounted sources,
   - a staging area that must be normalized first,
   - or a mixed source requiring separation?
4. What should be promoted into llm-wikis versus kept in L2 provenance/registry layers only?
5. Which future implementation surfaces are likely touched (registry, source mapping, promotion, wiki backlinks, discoverability docs)?
6. Should this issue remain one implementation issue after planning, or be split into follow-on issues such as:
   - source registration/dedup
   - provenance backfill
   - wiki promotion
   - accessibility/entry-point updates

Execution steps:

STEP 1 — Live intake and resource intelligence
- Read `#2216` live from GitHub.
- Inspect `/mnt/ace/acma-codes` directly.
- Build a concise but real inventory by top-level family, file types, and obvious standards domains.
- Check current repo registries/docs for overlap and likely duplication.
- Use the parent/sibling architecture docs to constrain the design.

STEP 2 — Draft the plan
- Write the plan file in repo style.
- Keep it planning-only.
- Do not write implementation code.
- Be explicit about whether the collection is source-of-truth material, mixed staging material, or partially duplicated material.

STEP 3 — Adversarial review
- Create `scripts/review/results/2026-04-11-plan-2216-claude.md`.
- Review for:
  - scope discipline
  - consistency with `#2205`, `#2207`, `#2209`, `#2096`
  - realistic handling of dedup/provenance risk
  - whether the inventory is grounded in real files
  - whether the issue should split further
- Revise the plan if needed.

STEP 4 — Final synthesis
- Create `scripts/review/results/2026-04-11-plan-2216-final.md`.
- State whether the plan is ready for `status:plan-review`.
- If not ready, explain exactly why.

STEP 5 — GitHub update
If ready:
- Post a concise planning summary comment to `#2216` with:
  - plan path
  - top-level inventory findings
  - recommended integration model
  - dedup/provenance risks
  - whether follow-on issue split is recommended
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
- Ground every major claim in the real `/mnt/ace/acma-codes` contents or current repo artifacts.
- Prefer explicit split recommendations over vague “future work.”
- Do not let planning drift into implementation.
- Keep the result usable as the next operator-ready implementation dossier.
