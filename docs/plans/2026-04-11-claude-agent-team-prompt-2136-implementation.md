# Claude agent-team prompt: #2136 implementation

Use this prompt as a single self-contained handoff to Claude Code for implementation.

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. Data/Docs Implementer
3. Adversarial Reviewer
4. Integrator

Do not ask the user any questions.

Execution authorization:
- Issue `#2136` has been explicitly user-approved for execution.
- GitHub label `status:plan-approved` is present.
- Local marker exists: `.planning/plan-approved/2136.md`

Primary issue:
- `#2136` https://github.com/vamseeachanta/workspace-hub/issues/2136

Approved plan:
- `docs/plans/2026-04-11-issue-2136-intelligence-accessibility-registry-with-machine-reachability.md`

Review artifacts:
- `scripts/review/results/2026-04-11-plan-2136-claude.md`
- `scripts/review/results/2026-04-11-plan-2136-final.md`

Authoritative supporting docs to follow, not redefine:
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md`
- `docs/document-intelligence/intelligence-accessibility-map.md`
- `docs/plans/2026-04-11-issue-2104-canonical-entry-points-for-ecosystem-intelligence.md`
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`

Critical safety constraints:
- The repo has many unrelated dirty/untracked files.
- Do NOT touch unrelated files.
- Stage and commit ONLY the files explicitly owned by this issue.
- Never use `git add .` or broad globs.
- If you detect unavoidable conflict with unrelated dirty files, stop and report clearly.

Owned implementation paths for #2136 only:
- `data/document-index/intelligence-accessibility-registry.yaml`
- `scripts/data/document-index/validate-accessibility-registry.py`
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`

Read-only context paths:
- `docs/plans/2026-04-11-issue-2136-intelligence-accessibility-registry-with-machine-reachability.md`
- `docs/document-intelligence/intelligence-accessibility-map.md`
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- `data/document-index/registry.yaml`
- `data/document-index/standards-transfer-ledger.yaml`
- `data/document-index/mounted-source-registry.yaml`
- `data/design-codes/code-registry.yaml`
- `scripts/review/results/2026-04-11-plan-2136-*.md`

Forbidden paths:
- `docs/README.md`
- `docs/document-intelligence/**`
- `knowledge/**`
- `.claude/**`
- `.codex/**`
- `config/**`
- any unrelated dirty/untracked file outside the owned paths above

Success condition:
Implement the approved #2136 plan fully and safely.

Required implementation outcomes:
1. Create `data/document-index/intelligence-accessibility-registry.yaml`
   - include schema header / version metadata
   - include initial seeded entries grounded in #2096 accessibility map and plan #2136
   - use the required minimum field set and sensible extended fields where available
2. Seed the major intelligence assets described in the plan
   - wiki domains
   - key registries/ledgers
   - architecture docs
   - maps / inventories
   - weekly review template
3. Create `scripts/data/document-index/validate-accessibility-registry.py`
   - validate schema completeness for required fields
   - validate `asset_key` uniqueness
   - validate `canonical_path` existence
   - validate enum values for fields like `asset_type`, `layer`, `source_of_truth_tier`, `durability`
   - print actionable errors and non-zero exit on failure
4. Update `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`
   - add registry-based checks to Section D only if this can be done minimally and cleanly
   - do not rewrite the whole document
5. Verify the registry and validator against the seeded file
6. Commit only the owned files for this issue
7. Post a GitHub implementation summary comment on #2136
8. Close the issue if fully complete and verified

Implementation guidance:
- Keep v1 simple and explicit.
- Prefer YAML that humans can inspect and scripts can validate.
- Use stable `asset_key` slugs.
- For `machine_scope`, use conservative values grounded in current evidence.
- Do not over-engineer a query API in this issue.
- `query_command` strings may be simple shell commands for now.

Required verification before commit:
- registry file exists and is non-empty
- validator passes on the new registry file
- seeded entries cover the main asset classes identified in the plan
- all `canonical_path` values in seeded entries exist
- no duplicate `asset_key` values
- weekly review changes (if any) remain minimal and only within owned scope

Git discipline:
- Stage only the owned paths explicitly by path.
- Commit message:
  - `feat(intelligence): add accessibility registry with machine reachability metadata (#2136)`
- After commit, push to `origin main`.

GitHub closeout:
- Post a concise comment on #2136 summarizing:
  - files changed
  - validation performed
  - seeded asset coverage
  - any minor deviations from the plan
- If everything is complete and verified, close the issue.

Final return format in the Claude session:
1. What changed
2. Verification performed
3. Exact files committed
4. GitHub comment URL
5. Whether issue was closed
6. Residual risks or follow-ups
