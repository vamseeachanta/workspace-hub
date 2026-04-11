# Claude agent-team prompt: #2209 durable-vs-transient knowledge boundary

Use this prompt as a single self-contained handoff to Claude Code for the next execution step after #2207.

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. Policy Architect
3. Adversarial Reviewer
4. Integrator

Do not ask the user any questions.

Repo/workflow constraints:
- This repo is plan-gated, but issue `#2209` is already labeled `status:plan-approved`.
- Parent operating model from `#2205` is authoritative.
- `#2207` contract work now exists locally and should be treated as a sibling child contract, not something to redefine.
- This run is for `#2209` only.
- Stay within the approved scope for `#2209`: define the durable-vs-transient knowledge boundary across llm-wikis, GitHub issues, registries, weekly reviews, and session/handoff artifacts.
- Do NOT implement downstream enforcement hooks, registry schemas, or wiki/code changes in this run.
- Do NOT redefine the parent pyramid/layer model from `#2205`.
- Do NOT absorb retrieval-policy work from `#2208`, provenance/schema work from `#2207`, conformance tooling from `#2206`, or `/mnt/ace/acma-codes` integration work from `#2216`.

Primary issue:
- `#2209` https://github.com/vamseeachanta/workspace-hub/issues/2209

Parent / related issues:
- Parent: `#2205` https://github.com/vamseeachanta/workspace-hub/issues/2205
- Sibling child contract already present: `#2207`
- Related: `#2089`, `#2096`, `#2104`, `#2136`
- Do not implement: `#2206`, `#2208`, `#2216`

Authoritative artifacts to consume:
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`

Relevant context to inspect:
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`
- `docs/governance/SESSION-GOVERNANCE.md`
- `docs/plans/README.md`
- `docs/handoffs/` (sample handoff artifacts for transient layer examples)
- `knowledge/wikis/engineering/wiki/index.md`
- `knowledge/wikis/engineering/wiki/sources/closed-engineering-issues.md`
- any docs under `docs/document-intelligence/` and `docs/reports/` that help distinguish durable vs transient artifacts

Allowed write paths for this run:
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`
- `scripts/review/results/2026-04-11-issue-2209-claude-review.md`
- `scripts/review/results/2026-04-11-issue-2209-final-review.md`
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` (cross-links only, if truly needed)

Read-only paths:
- `knowledge/wikis/**`
- `docs/handoffs/**`
- `docs/plans/**`
- `docs/modules/**`
- `docs/governance/**`
- `docs/document-intelligence/**`
- `scripts/review/results/**`

Forbidden paths:
- `.claude/**`
- `.codex/**`
- `config/**`
- `data/**`
- `scripts/data/**`
- `scripts/knowledge/**`
- `tests/**`
- any unrelated dirty/untracked files already present in the worktree

Important git safety rule:
- First inspect `git status --short`.
- The repo currently has unrelated dirty and untracked files.
- Do NOT modify anything outside the allowed write paths above.
- If the worktree is too dirty to proceed safely even within those paths, stop and report that explicitly in the final summary and GitHub comment.

Success condition:
By the end of this run, the repo should contain a finished policy document for `#2209` that:
- clearly distinguishes durable vs transient artifacts across all major intelligence/tracking layers
- defines allowed bridge/sync directions
- defines promotion rules from transient to durable knowledge
- defines anti-patterns and guardrails
- recommends policy/template/skill follow-on implementation work
- stays fully consistent with `#2205` and does not collide with `#2207`
- has been adversarially reviewed within the run
- is summarized back to GitHub issue `#2209`

Required deliverable document structure:
Create or update:
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`

The document must include these sections:
1. Purpose and scope
2. Relationship to parent operating model (`#2205`)
3. Relationship to sibling provenance/reuse contract (`#2207`)
4. Artifact classes and ownership statements
   - llm-wikis
   - GitHub issues / plans / review artifacts
   - registries / ledgers / manifests
   - weekly review artifacts
   - session / handoff / scratchpad artifacts
5. Durable vs transient classification rules
6. Allowed bridge / sync directions
7. Promotion rules from transient to durable
8. Retention / expiration guidance for transient artifacts
9. Anti-patterns and guardrails
10. Likely implementation surfaces (docs/templates/skills/workflows only)
11. Open questions / residual risks
12. Recommended follow-on implementation sequence

Policy content requirements:
- Make explicit that GitHub issues own execution state, not durable knowledge.
- Make explicit that registries own provenance/inventory, not narrative synthesis.
- Make explicit that llm-wikis own durable conceptual/technical knowledge, not live task tracking.
- Make explicit that session/handoff artifacts are transient by default unless promoted.
- Clarify how weekly-review artifacts fit: recurring operational evidence, not the durable source of truth for domain knowledge.
- Include criteria for when a transient artifact deserves promotion into durable knowledge.
- Include criteria for when an artifact should be archived, allowed to decay, or replaced by a promoted durable artifact.

Execution steps:

STEP 1 — Read and ground
- Read issue `#2209` live from GitHub.
- Read the parent operating model (`#2205`) and the sibling provenance/reuse contract (`#2207`).
- Read the listed governance, review, handoff, and wiki context.
- Extract real examples of:
  - durable artifacts
  - transient artifacts
  - boundary-blurring artifacts
- Identify existing repo guidance that already implies a boundary.

STEP 2 — Draft the boundary policy
- Write the policy as a normative doc, not a loose discussion.
- Keep it implementation-guiding but not implementation-heavy.
- Use concrete examples from the repo where helpful.
- Ensure the document says what each artifact class is for, what it is not for, and how it may legitimately connect to other layers.

STEP 3 — Internal adversarial review
- Create `scripts/review/results/2026-04-11-issue-2209-claude-review.md`.
- Review for:
  - consistency with `#2205`
  - non-overlap with `#2207`
  - clarity of promotion/retention rules
  - whether future implementation teams could use this without guessing
  - whether anti-patterns are concrete and enforceable
- If major issues are found, revise the doc before finalizing.

STEP 4 — Final integrator pass
- Create `scripts/review/results/2026-04-11-issue-2209-final-review.md` with final verdict and residual risks.
- Ensure the contract is internally consistent and scoped correctly.
- If useful and minimal, add a cross-link from the parent operating-model doc to the new boundary-policy doc, but only if this stays inside allowed write paths.

STEP 5 — GitHub update
- Post a concise summary comment on `#2209` including:
  - document path
  - main boundary decisions
  - allowed bridge directions
  - promotion rule summary
  - implementation surfaces identified
  - residual risks/open questions
- Do not change labels unless absolutely required by repo policy and clearly justified.

Output requirements for the Claude run:
1. What changed
2. Final review verdict
3. Exact files changed
4. Exact GitHub comment posted
5. Residual blockers or risks

Quality bar:
- Be explicit and policy-oriented.
- Prefer hard boundaries over vague "it depends" wording.
- Use real repo artifact classes/examples.
- Do not let the document drift into workflow retrieval policy (`#2208`) or conformance tooling (`#2206`).
- Produce something a future implementation agent can follow directly.
