# Claude agent-team prompt: #2226 implementation

Use this prompt as a single self-contained handoff to Claude Code for implementation.

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. Ledger/Provenance Implementer
3. Adversarial Reviewer
4. Integrator

Do not ask the user any questions.

Execution authorization:
- Issue `#2226` has been explicitly user-approved for execution.
- GitHub label `status:plan-approved` is present.
- Local marker exists: `.planning/plan-approved/2226.md`

Primary issue:
- `#2226` https://github.com/vamseeachanta/workspace-hub/issues/2226

Approved plan:
- `docs/plans/2026-04-11-issue-2226-ocimf-csa-ledger-provenance-backfill.md`

Review artifacts:
- `scripts/review/results/2026-04-11-plan-2226-claude.md`
- `scripts/review/results/2026-04-11-plan-2226-final.md`

Authoritative supporting docs to follow, not redefine:
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `docs/plans/2026-04-11-issue-2216-acma-codes-llm-wiki-repo-intelligence-integration.md`
- `docs/plans/2026-04-11-issue-2225-acma-codes-source-registration-and-initial-indexing.md`
- `data/document-index/index.jsonl`
- `data/document-index/standards-transfer-ledger.yaml`
- `data/design-codes/code-registry.yaml`

Critical safety constraints:
- The repo has many unrelated dirty/untracked files.
- Do NOT touch unrelated files.
- Stage and commit ONLY the files explicitly owned by this issue.
- Never use `git add .` or broad globs.
- If you detect unavoidable conflict with unrelated dirty files, stop and report clearly.

Owned implementation paths for #2226 only:
- `data/document-index/standards-transfer-ledger.yaml`

Optional owned path only if clearly warranted and minimal:
- `data/design-codes/code-registry.yaml` (ONLY if you conclude a code-registry update is clearly warranted by the plan and evidence; otherwise do not touch it)

Read-only context paths:
- `docs/plans/2026-04-11-issue-2226-ocimf-csa-ledger-provenance-backfill.md`
- `data/document-index/index.jsonl`
- `data/design-codes/code-registry.yaml`
- `scripts/review/results/2026-04-11-plan-2226-*.md`
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`

Forbidden paths:
- `knowledge/**`
- `scripts/**`
- `docs/**`
- `tests/**`
- `.claude/**`
- `.codex/**`
- `config/**`
- any unrelated dirty/untracked file outside the owned paths above

Success condition:
Implement the approved #2226 plan fully and safely.

Required implementation outcomes:
1. Update `data/document-index/standards-transfer-ledger.yaml`
   - add the approved OCIMF entries
   - add the approved CSA entries
   - update the existing API RP 1111 and API RP 2SK entries with acma-codes alias/doc_paths where approved by the plan
   - add the approved API RP 2SK 3rd edition / addendum entries if supported by the plan and indexed evidence
2. Use real indexed evidence from `index.jsonl` for every new or updated ledger entry
3. Preserve ledger consistency and avoid duplicate/conflicting truth
4. If and only if clearly warranted by the plan/evidence, update `data/design-codes/code-registry.yaml`; otherwise leave it untouched and say so
5. Post a GitHub implementation summary comment on #2226
6. Close #2226 only if the approved acceptance criteria are genuinely met

Implementation guidance:
- Ground every ledger edit in actual indexed records.
- Prefer conservative ledger updates over speculative ones.
- Be explicit in notes/fields where records are alias paths versus new editions versus addenda.
- Do not attempt to solve the broader hash-format inconsistency in this issue.
- Do not add a new `doc_key` field to the ledger schema unless the existing structure already clearly supports it and the plan explicitly allows it. Otherwise keep to the current schema and use path/provenance notes as planned.

Required verification before commit:
- confirm all new/updated ledger entries map to real indexed `acma_codes` records
- confirm no duplicate/conflicting IDs are introduced
- confirm API alias vs new-edition handling matches the approved plan
- confirm any optional `code-registry.yaml` change is justified; otherwise leave it untouched
- confirm no forbidden paths were modified

Git discipline:
- Stage only the owned paths explicitly by path.
- Commit message:
  - `feat(acma-codes): backfill ledger provenance and aliases for OCIMF/CSA (#2226)`
- After commit, push to `origin main`.

GitHub closeout:
- Post a concise comment on #2226 summarizing:
  - files changed
  - which ledger entries were added/updated
  - how API overlaps were treated
  - whether the code-registry was changed or intentionally left unchanged
- Close the issue only if it is fully complete and verified.

Final return format in the Claude session:
1. What changed
2. Verification performed
3. Exact files committed
4. GitHub comment URL
5. Whether issue was closed
6. Residual risks or follow-ups
