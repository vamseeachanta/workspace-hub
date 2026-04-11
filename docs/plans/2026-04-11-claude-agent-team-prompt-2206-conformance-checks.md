# Claude agent-team prompt: #2206 single-source-of-truth pyramid conformance checks

Use this prompt as a single self-contained handoff to Claude Code for the next executable issue after #2096.

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. Validation Architect
3. Adversarial Reviewer
4. Integrator

Do not ask the user any questions.

Repo/workflow constraints:
- This repo is plan-gated. Issue `#2206` is currently labeled `status:plan-approved`; verify live before acting.
- Parent operating model from `#2205` is authoritative.
- Child artifacts from `#2207`, `#2209`, and `#2096` now exist locally and should be consumed as inputs, not redefined.
- This run is for `#2206` only.
- Stay within the approved scope for `#2206`: define conformance checks and validation tooling design for the approved single-source-of-truth pyramid so the ecosystem can detect ownership overlap, broken information flow, and drift.
- Do NOT implement production CI hooks, registry schema changes, wiki ingestion changes, or issue-workflow retrieval policy in this run.
- Do NOT redefine the parent pyramid/layer model from `#2205`.
- Do NOT absorb work from `#2104`, `#2136`, `#2208`, or `#2216`.

Primary issue:
- `#2206` https://github.com/vamseeachanta/workspace-hub/issues/2206

Parent / related issues:
- Parent: `#2205`
- Child artifacts already present locally: `#2207`, `#2209`, `#2096`
- Adjacent but out-of-scope: `#2104`, `#2136`, `#2208`, `#2216`
- Downstream consumer: `#2089`

Authoritative artifacts to consume:
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`
- `docs/document-intelligence/intelligence-accessibility-map.md`

Relevant context to inspect:
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`
- `docs/governance/SESSION-GOVERNANCE.md`
- `docs/README.md`
- `docs/standards/CONTROL_PLANE_CONTRACT.md`
- `docs/plans/README.md`
- `scripts/review/results/2026-04-11-plan-2205-*.md`
- `scripts/review/results/2026-04-11-issue-2207-*.md`
- `scripts/review/results/2026-04-11-issue-2209-*.md`
- `scripts/review/results/2026-04-11-issue-2096-*.md`

Allowed write paths for this run:
- `docs/document-intelligence/pyramid-conformance-checks.md`
- `scripts/review/results/2026-04-11-issue-2206-claude-review.md`
- `scripts/review/results/2026-04-11-issue-2206-final-review.md`
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` (cross-links only, if truly needed)

Read-only paths:
- `docs/**`
- `knowledge/**`
- `scripts/review/results/**`
- GitHub issue threads for the related issues above

Forbidden paths:
- `.claude/**`
- `.codex/**`
- `config/**`
- `data/**`
- `scripts/data/**`
- `scripts/knowledge/**`
- `tests/**`
- any unrelated dirty/untracked files already present in the worktree
- issue bodies/comments for issues other than `#2206` unless a minimal backlink/reference is truly necessary

Important git safety rule:
- First inspect `git status --short`.
- The repo currently has unrelated dirty and untracked files.
- Do NOT modify anything outside the allowed write paths above.
- If the worktree is too dirty to proceed safely even within those paths, stop and report that explicitly in the final summary and GitHub comment.

Success condition:
By the end of this run, the repo should contain a finished conformance-check design document for `#2206` that:
- translates the approved #2205 operating model into concrete validation rules
- defines feasible automated vs manual checks
- covers ownership-overlap detection, flow-rule drift, child-issue guardrail drift, and discoverability/conformance drift
- identifies what can be validated now versus what depends on later implementation in sibling issues
- stays fully consistent with `#2205`, `#2207`, `#2209`, and `#2096`
- has been adversarially reviewed within the run
- is summarized back to GitHub issue `#2206`

Required deliverable document structure:
Create or update:
- `docs/document-intelligence/pyramid-conformance-checks.md`

The document must include these sections:
1. Purpose and scope
2. Relationship to parent operating model (`#2205`)
3. Relationship to sibling child artifacts (`#2207`, `#2209`, `#2096`)
4. Conformance target classes
   - layer ownership
   - document identity usage
   - information-flow rules
   - durable/transient boundary
   - accessibility/discoverability linkage
   - issue classification and child guardrails
5. Candidate checks matrix
   - check name
   - purpose
   - manual or automatable
   - inputs/artifacts needed
   - pass/fail signal
6. Priority checks to implement first
7. Feasible automation surfaces
   - docs linters
   - cross-link validators
   - artifact-ownership checks
   - label/doc consistency checks
8. Checks that are intentionally manual for now
9. Anti-patterns and failure modes
10. Recommended implementation sequence
11. Open questions / residual risks

Policy/content requirements:
- Be explicit about what is a design for validation versus an actual implemented validation.
- Separate “can be checked today from existing files” from “requires future tooling or sibling-issue completion.”
- Do not invent new parent rules; validate against existing ones.
- Use concrete examples from the current artifacts where helpful.
- Include at least one check for each of:
  - duplicate ownership
  - path-only identity leakage
  - wiki/provenance boundary violations
  - transient artifact improper promotion
  - missing cross-links from child artifacts to parent model

Execution steps:

STEP 1 — Read and ground
- Read issue `#2206` live from GitHub.
- Read the parent operating model and the completed sibling artifacts.
- Read related review artifacts to understand what types of drift/failures have already been seen.
- Identify what kinds of checks are realistic from the current repo state.

STEP 2 — Draft the conformance-check design
- Write the document as a normative validation-design doc, not a vague recommendation memo.
- Focus on checks, signals, and implementation priority.
- Be careful not to drift into implementing the checks themselves.

STEP 3 — Internal adversarial review
- Create `scripts/review/results/2026-04-11-issue-2206-claude-review.md`.
- Review for:
  - consistency with `#2205`
  - whether checks are concrete and testable
  - whether boundaries with `#2207`, `#2209`, `#2096`, `#2208`, `#2136` are clear
  - whether the doc distinguishes automatable vs manual checks
  - whether it avoids scope creep into actual tooling implementation
- If major issues are found, revise the doc before finalizing.

STEP 4 — Final integrator pass
- Create `scripts/review/results/2026-04-11-issue-2206-final-review.md` with final verdict and residual risks.
- Ensure the design is internally consistent and scoped correctly.
- If useful and minimal, add a cross-link from the parent operating-model doc to the new conformance-checks doc, but only if this stays inside allowed write paths.

STEP 5 — GitHub update
- Post a concise summary comment on `#2206` including:
  - document path
  - major conformance target classes
  - highest-priority checks to implement first
  - automatable vs manual split
  - residual risks/open questions
- Do not change labels unless absolutely required by repo policy and clearly justified.

Output requirements for the Claude run:
1. What changed
2. Final review verdict
3. Exact files changed
4. Exact GitHub comment posted
5. Residual blockers or risks

Quality bar:
- Prefer concrete validation design over aspirational governance language.
- Use existing artifacts and repo realities.
- Be explicit about what is checkable now versus later.
- Do not drift into implementing scripts or CI hooks.
- Produce something a future implementation agent can use directly to build the checks.
