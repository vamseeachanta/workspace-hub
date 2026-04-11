# Claude agent-team prompt: #2207 standards/codes provenance + reuse contract

Use this prompt as a single self-contained handoff to Claude Code for the next execution step after #2205.

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. Architect
3. Adversarial Reviewer
4. Integrator

Do not ask the user any questions.

Repo/workflow constraints:
- This repo is plan-gated, but issue `#2207` is already labeled `status:plan-approved`.
- Parent operating model from `#2205` is now available locally and must be treated as authoritative.
- This run is for `#2207` only.
- Stay within the approved scope for `#2207`: define the provenance + reuse contract for standards/codes so document-intelligence outputs can feed llm-wikis and issue workflows without unnecessary reparsing.
- Do NOT absorb unrelated child work from `#2206`, `#2208`, `#2209`, or `#2216`.
- Do NOT redefine the parent pyramid/layer model from `#2205`.

Primary issue:
- `#2207` https://github.com/vamseeachanta/workspace-hub/issues/2207

Parent / related issues:
- Parent: `#2205` https://github.com/vamseeachanta/workspace-hub/issues/2205
- Related: `#2136`, `#2034`, `#1563`, `#1575`
- Do not implement: `#2206`, `#2208`, `#2209`, `#2216`

Authoritative parent artifact to consume:
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`

Likely source surfaces to inspect:
- `data/document-index/standards-transfer-ledger.yaml`
- `scripts/data/document-index/provenance.py`
- `scripts/data/document-index/phase-e-registry.py`
- `scripts/data/document-index/query-ledger.py`
- `scripts/data/doc_intelligence/query.py`
- `scripts/knowledge/llm_wiki.py`
- `scripts/knowledge/tests/test_llm_wiki.py`
- `docs/assessments/document-intelligence-audit.md`
- `docs/document-intelligence/holistic-resource-intelligence.md`

Allowed write paths for this run:
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- `scripts/review/results/2026-04-11-issue-2207-claude-review.md`
- `scripts/review/results/2026-04-11-issue-2207-final-review.md`
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` (cross-links only, if truly needed)

Read-only paths:
- `data/document-index/**`
- `scripts/data/document-index/**`
- `scripts/data/doc_intelligence/**`
- `scripts/knowledge/**`
- `docs/assessments/**`
- `docs/plans/**`

Forbidden paths:
- `knowledge/wikis/**`
- `.claude/**`
- `.codex/**`
- `config/**`
- `tests/**` outside `scripts/knowledge/tests/test_llm_wiki.py` read-only inspection
- any file owned by `#2206`, `#2208`, `#2209`, `#2216`
- any unrelated dirty files already present in the worktree

Important git safety rule:
- First inspect `git status --short`.
- If the worktree contains unrelated dirty changes outside your allowed write paths, do NOT modify them.
- Prefer to work only in the allowed write paths above.
- If the repo is too dirty to proceed safely, stop and report that in the final summary and GitHub comment.

Success condition:
By the end of this run, the repo should contain a finished contract document for `#2207` that:
- defines canonical provenance fields for standards/codes artifacts
- defines a canonical `doc_key` / content-identity reuse policy consistent with `#2205`
- defines reuse-vs-reparse decision rules
- defines the llm-wiki promotion path using existing document-intelligence outputs when sufficient evidence exists
- defines fallback rules for OCR/reparse when evidence is insufficient
- defines likely implementation surfaces and follow-on work without implementing them
- includes anti-patterns and conflict-resolution guidance
- has been adversarially reviewed within the run
- is summarized back to GitHub issue `#2207`

Required deliverable document structure:
Create or update:
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`

The document must include these sections:
1. Purpose and scope
2. Relationship to parent operating model (`#2205`)
3. Canonical identity model
   - `doc_key` / content hash
   - alias paths and machine-specific paths
   - revision/new-doc-key rule
4. Required provenance fields
   - minimum required fields
   - recommended extended fields
   - field ownership by layer
5. Reuse-vs-reparse decision rules
   - when registry/promoted evidence is sufficient
   - when raw doc access is required
   - when OCR is required
6. llm-wiki promotion path
   - from document-intelligence outputs into wiki-ready records
   - without reparsing when sufficient evidence exists
7. Unified artifact-registry implications
   - architecture-level compatibility with `#2205`
   - what this issue recommends without fixing exact schema for all children
8. Anti-patterns
   - duplicate parsing
   - path-only identity
   - broken lineage
   - wiki entries outranking provenance
9. Likely implementation surfaces
   - specific files/modules likely to change in future implementation issues
10. Open questions / residual risks
11. Recommended follow-on implementation sequence

Execution steps:

STEP 1 — Read and ground
- Read issue `#2207` live from GitHub.
- Read the parent operating model doc from `#2205`.
- Read the listed registry/provenance/query/wiki files and relevant docs.
- Extract the actual current identity/provenance terms already present (`sha256`, `checksum`, `content_hash`, etc.).
- Identify inconsistencies in naming or ownership.

STEP 2 — Draft the contract document
- Write the contract as a normative doc, not a vague note.
- Keep it implementation-guiding but not implementation-heavy.
- It must clearly state what future implementation work should converge on.
- It must not redefine `#2205`; instead it should inherit parent rules and specialize them for provenance/reuse.

STEP 3 — Internal adversarial review
- Create `scripts/review/results/2026-04-11-issue-2207-claude-review.md`.
- Review for:
  - consistency with `#2205`
  - avoidance of schema creep beyond issue scope
  - clarity of reuse-vs-reparse decision rules
  - whether future implementation teams could use this without guessing
- If you find major issues, revise the doc before finalizing.

STEP 4 — Final integrator pass
- Create `scripts/review/results/2026-04-11-issue-2207-final-review.md` with final verdict and residual risks.
- Ensure the contract doc is internally consistent and scoped correctly.
- If useful and minimal, add a cross-link from the parent operating-model doc to the new contract doc, but only if this stays inside allowed write paths.

STEP 5 — GitHub update
- Post a concise summary comment on `#2207` including:
  - document path
  - main identity decision
  - main reuse-vs-reparse rule
  - main llm-wiki promotion rule
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
- Be explicit over elegant.
- Prefer concrete contract language over broad aspirations.
- Do not let path identity outrank content identity.
- Do not let this document drift into #2208 workflow policy or #2206 conformance tooling.
- Produce something a future implementation agent can follow directly.
